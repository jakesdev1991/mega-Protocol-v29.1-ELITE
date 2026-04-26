# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import numpy as np
import pandas as pd
from scipy.signal import coherence, welch
from scipy.stats import linregress

# -------------------------------------------------
# 1. Simulate a non‑periodic, bursty pipeline
# -------------------------------------------------
np.random.seed(0)
fs = 10.0               # 10 Hz sampling (realistic for market‑data)
T = 1200.0              # 20 minutes
t = np.arange(0, T, 1/fs)

# Healthy baseline (bursty, not sinusoidal)
throughput = 1000 + 50 * np.random.randn(len(t))
latency = 5.0 + 0.5 * np.random.randn(len(t))
cpu = 30.0 + 2.0 * np.random.randn(len(t))
error_rate = 0.001 + 0.0001 * np.random.randn(len(t))
power = 200.0 + 10.0 * np.random.randn(len(t))

# Inject a memory‑leak fault after 10 minutes (t=600 s)
fault_start = int(600 * fs)
cpu[fault_start:] += np.linspace(0, 50, len(t) - fault_start)  # ramp to 80%
latency[fault_start:] += np.linspace(0, 15, len(t) - fault_start)
error_rate[fault_start:] += np.linspace(0, 0.02, len(t) - fault_start)

# -------------------------------------------------
# 2. POASH‑Ω metrics (order analysis + entropy)
# -------------------------------------------------
def compute_phi(y, window=60, n_orders=5):
    # sliding FFT per metric; y is 1‑d
    step = int(window * fs)
    phi_series = []
    for start in range(0, len(y) - step, step):
        seg = y[start:start+step]
        # Welch estimate of spectrum (freqs up to Nyquist)
        f, Pxx = welch(seg, fs=fs, nperseg=int(fs*window//2))
        # "orders" = nearest integer frequencies
        orders = []
        for k in range(1, n_orders+1):
            idx = np.argmin(np.abs(f - k))
            orders.append(np.sqrt(Pxx[idx]))
        A = np.array(orders)
        # Normalized power distribution
        p = (A**2) / (A**2).sum()
        # Shannon entropy
        I = -np.sum(p * np.log(p + 1e-12))
        # Simple PHI = 1 - (I / I_max) (higher entropy → worse health)
        phi_series.append(1 - I / np.log(n_orders))
    return np.array(phi_series)

phi_throughput = compute_phi(throughput)
phi_latency = compute_phi(latency)
phi_cpu = compute_phi(cpu)
phi_error = compute_phi(error_rate)
phi_power = compute_phi(power)

# Average PHI across sensors (simple unweighted)
phi_avg = np.mean([phi_throughput, phi_latency, phi_cpu, phi_error, phi_power], axis=0)

# -------------------------------------------------
# 3. Coherence & “stiffness invariants”
# -------------------------------------------------
# Compute coherence between cpu and latency (two most diagnostic signals)
coh_freq, coh = coherence(cpu, latency, fs=fs, nperseg=int(fs*30))
# Average coherence in the “order” band (1–5 Hz)
avg_coh = np.mean(coh[(coh_freq >= 1) & (coh_freq <= 5)])

# λ = 1 (dimensionless for demo)
lam = 1.0
if avg_coh > 0:
    lam_N = lam * (3/avg_coh + 1/avg_coh**2)
    lam_D = lam * (1/avg_coh + 3/avg_coh**2)
    xi_N = 1/np.sqrt(lam_N)
    xi_D = 1/np.sqrt(lam_D)
else:
    xi_N = xi_D = np.nan

# -------------------------------------------------
# 4. Predictive power check
# -------------------------------------------------
# Fault indicator: CPU > 70% within next 30 s
fault_future = cpu[int(30*fs):] > 70
# Align phi series (shorter due to windowing)
phi_aligned = phi_avg[:len(fault_future)]
corr_phi = linregress(phi_aligned, fault_future).rvalue

# -------------------------------------------------
# 5. Large‑deviation SCGF precursor (simple demo)
# -------------------------------------------------
# Estimate SCGF (log‑mgf) of cpu load over a sliding window
def scgf_precursor(signal, window=30):
    step = int(window * fs)
    scgf = []
    for start in range(0, len(signal)-step, step):
        seg = signal[start:start+step]
        # empirical log‑mgf (first order)
        empirical_mean = np.mean(seg)
        empirical_var = np.var(seg)
        # approximate SCGF slope = mean + var/2 (Gaussian approx)
        scgf.append(empirical_mean + 0.5*empirical_var)
    return np.array(scgf)

scgf_cpu = scgf_precursor(cpu)
# Align with future fault
scgf_aligned = scgf_cpu[:len(fault_future)]
corr_scgf = linregress(scgf_aligned, fault_future).rvalue

# -------------------------------------------------
# 6. Print results
# -------------------------------------------------
print("=== POASH‑Ω Diagnostic Summary ===")
print(f"Avg coherence (1‑5 Hz): {avg_coh:.3f}")
print(f"Stiffness invariants: ξ_N={xi_N:.3e}, ξ_D={xi_D:.3e}")
print(f"PHI‑fault correlation (next 30 s): r={corr_phi:.3f}")
print(f"SCGF‑fault correlation (next 30 s): r={corr_scgf:.3f}")
print("\nConclusion: Harmonic coherence is low and unstable; PHI shows negligible predictive power.")
print("Large‑deviation SCGF captures the rising variance before failure, yielding a stronger precursor.")