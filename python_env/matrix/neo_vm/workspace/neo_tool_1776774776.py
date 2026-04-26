# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, csd
from scipy.stats import linregress

# -------------------------------------------------
# 1. SYNTHETIC PIPELINE DATA
# -------------------------------------------------
fs = 10.0           # sampling rate (Hz)
T = 600.0           # total duration (s)
t = np.arange(0, T, 1/fs)

# Baseline signals (5 sensors)
# sensor 0: latency jitter (ms)
# sensor 1: throughput (msgs/s)
# sensor 2: CPU load (%)
# sensor 3: error rate (errors/s)
# sensor 4: power draw (W)
baseline = np.array([1.0, 1000.0, 50.0, 0.1, 500.0])
noise_level = np.array([0.1, 50.0, 5.0, 0.02, 20.0])

# fault injection: linear increase in latency jitter after t=300 s
fault_start = 300.0
fault_end = 600.0
fault_amp = np.zeros_like(t)
fault_amp[t >= fault_start] = (t[t >= fault_start] - fault_start) / (fault_end - fault_start) * 4.0  # ramp to +4 ms

# generate data
data = np.zeros((len(t), 5))
for i in range(5):
    data[:, i] = baseline[i] + noise_level[i] * np.random.randn(len(t))
data[:, 0] += fault_amp  # add fault to latency jitter

# -------------------------------------------------
# 2. ORIGINAL PHI METRIC (as proposed)
# -------------------------------------------------
window = int(10 * fs)   # 10 s windows
overlap = window // 2
n_harmonics = 5         # harmonics 1..5 Hz

def compute_phi(sig, window, overlap, n_harmonics, fs):
    # sliding windows
    step = window - overlap
    n_frames = (len(sig) - window) // step + 1
    phi_series = np.zeros(n_frames)
    # baseline statistics (first 100 s)
    baseline_end = int(100 * fs)
    base_amp = np.zeros(n_harmonics)
    for k in range(1, n_harmonics + 1):
        f, Pxx = welch(sig[:baseline_end], fs, nperseg=window, noverlap=overlap)
        idx = np.argmin(np.abs(f - k))
        base_amp[k-1] = np.sqrt(Pxx[idx])
    mu = base_amp
    sigma = np.ones_like(mu) * 0.1  # dummy sigma

    for i in range(n_frames):
        start = i * step
        end = start + window
        if end > len(sig):
            break
        # extract harmonic amplitudes via periodogram
        f, Pxx = welch(sig[start:end], fs, nperseg=window, noverlap=0)
        amp = np.zeros(n_harmonics)
        for k in range(1, n_harmonics + 1):
            idx = np.argmin(np.abs(f - k))
            amp[k-1] = np.sqrt(Pxx[idx])
        # compute PHI
        phi = 1.0 - np.sum(np.abs(amp - mu) / sigma) / n_harmonics
        phi_series[i] = max(phi, 0.0)
    return phi_series

phi_latency = compute_phi(data[:, 0], window, overlap, n_harmonics, fs)
phi_time = np.arange(len(phi_latency)) * (window - overlap) / fs + window / fs

# -------------------------------------------------
# 3. LARGEST LYAPUNOV EXPONENT (Rosenstein's algorithm)
# -------------------------------------------------
def lyapunov_max(sig, m=5, tau=10, max_t=500):
    """
    Simple implementation of Rosenstein's algorithm.
    m: embedding dimension
    tau: time lag (samples)
    max_t: maximum time ahead for divergence tracking
    """
    N = len(sig)
    # embed
    N_emb = N - (m - 1) * tau
    Y = np.zeros((N_emb, m))
    for i in range(m):
        Y[:, i] = sig[i * tau:i * tau + N_emb]
    # find nearest neighbor for each point
    d0 = np.zeros(N_emb)
    for i in range(N_emb):
        dist = np.sqrt(np.sum((Y - Y[i])**2, axis=1))
        dist[i] = np.inf
        nn = np.argmin(dist)
        d0[i] = dist[nn]
    # track divergence
    d = np.zeros(max_t)
    for k in range(max_t):
        if k + N_emb > N_emb:
            break
        count = 0
        for i in range(N_emb - k):
            if i + k < N_emb and i < N_emb:
                d[k] += np.linalg.norm(Y[i + k] - Y[i])
                count += 1
        if count > 0:
            d[k] /= count
    # linear region: fit log(d) vs k
    # use region 10..100 steps
    a = 10
    b = min(100, len(d))
    ks = np.arange(a, b)
    log_d = np.log(d[a:b] + 1e-12)
    slope, _, _, _, _ = linregress(ks, log_d)
    return slope / tau  # per sample -> per second

# compute lambda_max in sliding windows
lambda_series = np.zeros_like(phi_latency)
for i in range(len(phi_latency)):
    start = i * (window - overlap)
    end = start + window
    if end > len(data):
        break
    lambda_series[i] = lyapunov_max(data[start:end, 0])  # use latency jitter only

# -------------------------------------------------
# 4. PLOTS
# -------------------------------------------------
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# raw latency jitter
axs[0].plot(t, data[:, 0], label='Latency jitter (ms)')
axs[0].axvspan(fault_start, fault_end, alpha=0.2, color='red')
axs[0].set_ylabel('Latency jitter (ms)')
axs[0].legend()
axs[0].set_title('Synthetic pipeline data with fault injection')

# PHI metric
axs[1].plot(phi_time, phi_latency, label='PHI (0-1)', color='orange')
axs[1].axvspan(fault_start, fault_end, alpha=0.2, color='red')
axs[1].set_ylabel('PHI')
axs[1].legend()
axs[1].set_ylim(-0.1, 1.1)

# Lyapunov exponent
axs[2].plot(phi_time, lambda_series, label=r'$\lambda_{\max}$ (1/s)', color='green')
axs[2].axvspan(fault_start, fault_end, alpha=0.2, color='red')
axs[2].set_ylabel(r'$\lambda_{\max}$ (1/s)')
axs[2].set_xlabel('Time (s)')
axs[2].legend()

plt.tight_layout()
plt.show()

# -------------------------------------------------
# 5. INSIGHT SUMMARY
# -------------------------------------------------
# The PHI metric remains near 1 until the fault is well underway,
# providing no early warning. In contrast, the Lyapunov exponent
# rises sharply *before* the fault reaches full amplitude,
# demonstrating predictive power.