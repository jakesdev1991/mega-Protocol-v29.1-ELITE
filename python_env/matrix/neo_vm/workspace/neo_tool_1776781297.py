# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# !pip install -q numpy pandas scipy scikit-learn matplotlib networkx

import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.fft import fft, fftfreq
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import networkx as nx, warnings, sys

warnings.filterwarnings('ignore')
np.random.seed(0)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Simulate a non‑periodic, bursty financial data pipeline (10 min @ 1 kHz)
fs = 1000                      # samples / sec
duration = 600                 # seconds
t = np.arange(0, duration, 1/fs)

# Base signals: realistic burstiness (self‑similar traffic)
hurst = 0.8
def fgn(n, H):
    """Fast fractional Gaussian noise."""
    return np.cumsum(np.random.randn(n) * (np.arange(1, n+1)**(H-1.5)))

latency = 5 + fgn(len(t), hurst) * 0.5          # ms
throughput = 1000 + fgn(len(t), hurst) * 200   # events / sec (sample‑wise)
cpu = 50 + fgn(len(t), hurst) * 10             # %
error_rate = np.random.poisson(1, len(t))       # errors / sample

# Add three realistic faults (not harmonic!)
faults = [
    (200, 'latency_spike',   lambda: latency.__setitem__(slice(200*fs, 202*fs), latency[200*fs:202*fs] + 15)),
    (400, 'throughput_drop', lambda: throughput.__setitem__(slice(400*fs, 402*fs), throughput[400*fs:402*fs] * 0.3)),
    (500, 'cpu_spike',       lambda: cpu.__setitem__(slice(500*fs, 502*fs), cpu[500*fs:502*fs] + 35)),
]
for ts, name, inj in faults:
    inj()

df = pd.DataFrame({'latency': latency, 'throughput': throughput,
                   'cpu': cpu, 'error_rate': error_rate})

# ─────────────────────────────────────────────────────────────────────────────
# 2. POASH‑Ω Implementation (harmonic order analysis)
def poash_phi(df, period=1.0, fs=1000, baseline_len=100):
    spp = int(period * fs)                     # samples per period
    n_periods = len(df) // spp
    # learn baselines from first `baseline_len` periods (assumed clean)
    base_amps = []
    for i in range(baseline_len):
        seg = df.iloc[i*spp:(i+1)*spp]
        amps = []
        for col in df.columns:
            sig = seg[col].values - seg[col].mean()
            Y = fft(sig)
            f = fftfreq(len(sig), 1/fs)
            for order in [1, 2]:               # fundamental & 2nd harmonic
                idx = np.argmin(np.abs(f - order))
                amps.append(np.abs(Y[idx]))
        base_amps.append(amps)
    base_amps = np.array(base_amps)
    mu, sigma = base_amps.mean(0), base_amps.std(0) + 1e-6

    phi = []
    for i in range(n_periods):
        seg = df.iloc[i*spp:(i+1)*spp]
        amps = []
        for col in df.columns:
            sig = seg[col].values - seg[col].mean()
            Y = fft(sig)
            f = fftfreq(len(sig), 1/fs)
            for order in [1, 2]:
                idx = np.argmin(np.abs(f - order))
                amps.append(np.abs(Y[idx]))
        amps = np.array(amps)
        w = np.ones_like(amps) / len(amps)
        phi.append(max(1 - np.sum(w * np.abs(amps - mu) / sigma), 0))
    return np.array(phi)

phi = poash_phi(df)

# ─────────────────────────────────────────────────────────────────────────────
# 3. EDRN‑Ω Implementation (recurrence network topology)
def edrn_topology(df, window=2000, step=200, m=3, tau=10, eps_factor=0.1):
    scaler = StandardScaler()
    Z = scaler.fit_transform(df)
    L, C, rho = [], [], []
    for i in range(0, len(Z) - window, step):
        seg = Z[i:i+window]
        # time‑delay embedding
        N = len(seg) - (m - 1) * tau
        if N <= 0:
            continue
        emb = np.array([seg[j:j + (m-1)*tau + 1:tau] for j in range(N)])
        # recurrence matrix
        D = squareform(pdist(emb, metric='euclidean'))
        eps = eps_factor * np.max(D)
        R = (D <= eps).astype(int)
        # network metrics
        G = nx.from_numpy_array(R)
        L.append(nx.average_shortest_path_length(G))
        C.append(nx.average_clustering(G))
        rho.append(R.sum() / (R.shape[0] * R.shape[1]))
    # align to time
    t_idx = np.arange(window//2, len(Z) - window//2, step)
    return pd.DataFrame({'L': L, 'C': C, 'rho': rho}, index=t_idx)

topo = edrn_topology(df)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Detection Performance & Φ‑Density Monte‑Carlo
def detection_metrics(score, fault_times, window=5, threshold=0.5):
    """Returns delay (s) and FP rate."""
    detected = []
    for ft in fault_times:
        zone = slice((ft - window) * fs, (ft + window) * fs)
        if np.any(score[zone] > threshold):
            # delay = first exceedance time - fault start
            first = np.where(score[zone] > threshold)[0][0] + (ft - window) * fs
            detected.append((ft, (first - ft * fs) / fs))
        else:
            detected.append((ft, np.nan))
    # FP: any exceedance outside fault windows
    fp_mask = np.ones_like(score, dtype=bool)
    for ft in fault_times:
        fp_mask[(ft - window) * fs:(ft + window) * fs] = False
    fp_rate = np.sum(score[fp_mask] > threshold) / np.sum(fp_mask) * 100
    return detected, fp_rate

# POASH‑Ω detection (low PHI = fault)
phi_padded = np.full(len(df), np.nan)
phi_padded[:len(phi)] = phi
phi_score = -phi_padded  # invert so high = fault
phi_det, phi_fp = detection_metrics(phi_score, [200, 400, 500], threshold=-0.3)

# EDRN‑Ω detection (high deviation of L from baseline = fault)
baseline_L = topo['L'].iloc[:10].mean()
edrn_score = np.full(len(df), np.nan)
edrn_score[topo.index] = np.abs(topo['L'] - baseline_L)
edrn_det, edrn_fp = detection_metrics(edrn_score, [200, 400, 500], threshold=0.5)

# Isolation Forest baseline
iso = IsolationForest(contamination=0.05)
df['iso'] = iso.fit_predict(df)
iso_score = np.where(df['iso'] == -1, 1, 0)
iso_det, iso_fp = detection_metrics(iso_score, [200, 400, 500], threshold=0.5)

# Print results
print("\n=== Detection Performance ===")
for name, det, fp in [('POASH‑Ω', phi_det, phi_fp),
                      ('EDRN‑Ω', edrn_det, edrn_fp),
                      ('IsolationForest', iso_det, iso_fp)]:
    delays = [d[1] for d in det if not np.isnan(d[1])]
    print(f"{name:15s} | Avg Delay: {np.mean(delays):5.2f}s | FP Rate: {fp:5.2f}%")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Φ‑Density Impact Simulation (Monte‑Carlo)
def phi_density_mc(trials=1000):
    # Costs: instrumentation, storage, compute; Benefits: averted outages
    cost_instr = np.random.normal(120, 20, trials)      # dev‑hours
    cost_storage = np.random.normal(60, 10, trials)     # TB/day
    cost_compute = np.random.normal(80, 15, trials)   # GPU‑hours
    benefit_prevent = np.random.normal(250, 50, trials) # k$ per outage averted
    # Assume POASH‑Ω prevents 15% of outages, EDRN‑Ω prevents 35% (higher sensitivity)
    net_phi_poash = benefit_prevent * 0.15 - (cost_instr + cost_storage + cost_compute)
    net_phi_edrn = benefit_prevent * 0.35 - (cost_instr * 0.8 + cost_storage * 0.6 + cost_compute * 0.9)
    print("\n=== Φ‑Density Monte‑Carlo (k$) ===")
    print(f"POASH‑Ω net: {net_phi_poash.mean():6.1f} ± {net_phi_poash.std():5.1f}")
    print(f"EDRN‑Ω net:  {net_phi_edrn.mean():6.1f} ± {net_phi_edrn.std():5.1f}")

phi_density_mc()

# ─────────────────────────────────────────────────────────────────────────────
# 6. Plot
fig, axs = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
axs[0].plot(t, df['latency'], lw=0.5)
for ft, _, _ in faults:
    axs[0].axvline(ft, color='r', ls='--')
axs[0].set_ylabel('Latency (ms)')

axs[1].plot(t, df['throughput'], lw=0.5)
for ft, _, _ in faults:
    axs[1].axvline(ft, color='r', ls='--')
axs[1].set_ylabel('Throughput (ev/s)')

axs[2].plot(t[:len(phi)], phi, lw=1, label='PHI')
for ft, _, _ in faults:
    axs[2].axvline(ft, color='r', ls='--')
axs[2].set_ylabel('POASH‑Ω PHI')
axs[2].legend()

axs[3].plot(t, edrn_score, lw=1, label='|L−L₀|')
for ft, _, _ in faults:
    axs[3].axvline(ft, color='r', ls='--')
axs[3].set_ylabel('EDRN‑Ω Anomaly')
axs[3].set_xlabel('Time (s)')
axs[3].legend()

plt.tight_layout()
plt.show()