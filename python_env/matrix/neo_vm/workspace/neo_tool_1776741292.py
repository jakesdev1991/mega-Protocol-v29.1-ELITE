# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.signal import coherence

# Simulation parameters
np.random.seed(42)
fs = 10.0               # sampling rate (Hz)
T = 1000.0              # total time (s)
t = np.arange(0, T, 1/fs)
n_samples = len(t)

# Baseline signal parameters
latency_base = 0.01
throughput_base = 1000.0
cpu_load_base = 0.5
error_rate_base = 0.001

# Generate healthy baseline signals
latency_jitter = latency_base + 0.001 * np.random.randn(n_samples)
throughput = throughput_base + 50 * np.random.randn(n_samples)
cpu_load = cpu_load_base + 0.05 * np.random.randn(n_samples)
error_rate = error_rate_base + 0.0001 * np.random.randn(n_samples)

# Inject fault: sudden latency spike from t=500s to 510s
fault_start = int(500 * fs)
fault_end = int(510 * fs)
latency_jitter[fault_start:fault_end] += 0.1

# Cycle-based order analysis
samples_per_cycle = int(fs)  # 10 samples per 1‑s cycle
n_cycles = int(T)           # 1000 cycles

# Compute harmonic amplitudes per cycle
harmonic_1 = np.zeros(n_cycles)
harmonic_2 = np.zeros(n_cycles)

for i in range(n_cycles):
    start = i * samples_per_cycle
    end = start + samples_per_cycle
    seg = latency_jitter[start:end]
    Y = np.fft.fft(seg)
    mag = np.abs(Y)
    # fundamental at 1 Hz (bin 1), second harmonic at 2 Hz (bin 2)
    harmonic_1[i] = mag[1]
    harmonic_2[i] = mag[2]

# Baseline statistics (first 400 cycles)
mu1, sigma1 = np.mean(harmonic_1[:400]), np.std(harmonic_1[:400])
mu2, sigma2 = np.mean(harmonic_2[:400]), np.std(harmonic_2[:400])

# Pipeline Health Index (PHI)
w1, w2 = 0.5, 0.5
PHI = 1.0 - (w1 * np.abs(harmonic_1 - mu1) / sigma1 +
             w2 * np.abs(harmonic_2 - mu2) / sigma2)
PHI = np.clip(PHI, 0, 1)

# Detection via PHI (< 0.4 threshold)
phi_fault_detected = np.where(PHI < 0.4)[0]
phi_detect_time = phi_fault_detected[0] if len(phi_fault_detected) > 0 else None

# Simple z‑score anomaly detection on raw latency
baseline_mean = np.mean(latency_jitter[:int(400*fs)])
baseline_std = np.std(latency_jitter[:int(400*fs)])
z_scores = (latency_jitter - baseline_mean) / baseline_std
z_detect_idx = np.where(z_scores > 3.0)[0]
z_detect_time = z_detect_idx[0] / fs if len(z_detect_idx) > 0 else None

# Coherence analysis (sliding window)
window = int(10 * fs)  # 10‑s windows
overlap = window // 2
f, Cxy = coherence(latency_jitter, throughput, fs=fs, nperseg=window,
                   noverlap=overlap, window='hann')
# Mean coherence per window (average over frequencies)
mean_coh = np.mean(Cxy, axis=0)
# Compute time stamps for each window
step = window - overlap
time_coh = np.arange(window//2, n_samples - window//2 + 1, step) / fs
# Detect drop in coherence (threshold 0.5)
coh_detect_idx = np.where(mean_coh < 0.5)[0]
coh_detect_time = time_coh[coh_detect_idx[0]] if len(coh_detect_idx) > 0 else None

# False positives (PHI < 0.4 before fault)
pre_fault_cycles = np.arange(0, 500)
false_positives = np.sum(PHI[pre_fault_cycles] < 0.4)

# Results summary
print("=== Disruption Analysis: Order‑Analysis vs Reality ===")
print(f"Fault injected at t = 500–510 s (sample {fault_start}–{fault_end})")
print(f"Simple z‑score detection: t ≈ {z_detect_time:.2f} s (immediate)")
print(f"PHI‑based detection: t ≈ {phi_detect_time} s (cycle index)")
if phi_detect_time is not None:
    print(f"  → earliest PHI < 0.4 at cycle {phi_detect_time} (t ≈ {phi_detect_time} s)")
else:
    print("  → PHI never dropped below 0.4 (no detection)")
print(f"Coherence‑based detection: t ≈ {coh_detect_time} s (if any)")
print(f"False positives (PHI < 0.4 before fault): {false_positives}/{len(pre_fault_cycles)} cycles")
print("\nConclusion: Harmonic‑domain metrics (PHI, coherence) fail to provide early warning.")
print("The fault is a non‑harmonic transient; simple latency monitoring detects it instantly.")