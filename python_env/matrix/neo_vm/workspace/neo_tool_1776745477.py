# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. CLUSTER & SENSOR SETUP
# -------------------------------------------------
np.random.seed(42)
N_GPU = 8
T_steps = 400
window = 50  # sliding window for correlation

# GPU positions (simple line topology)
pos = np.arange(N_GPU) * 0.5  # meters apart

# Baseline temperature model: T_i = 30 + 0.5*load_i + noise
baseline_temp = 30.0
temp_noise_std = 0.5

# Workload time series (fraction of GPU capacity)
workload = np.random.uniform(0.2, 0.4, (N_GPU, T_steps))

# -------------------------------------------------
# 2. INJECT REAL STRESS (t=150‑200) & THERMAL SPOOFING (t>=200)
# -------------------------------------------------
# Real stress: saturate first 4 GPUs
for t in range(150, 200):
    workload[:4, t] = np.random.uniform(0.8, 0.95, 4)

# Thermal spoofing: add +20°C to sensors 2 & 5 after t=200
spoof_start = 200
spoof_gpus = [2, 5]
spoof_magnitude = 20.0

# -------------------------------------------------
# 3. SIMULATE TEMPERATURE READINGS
# -------------------------------------------------
temp = np.empty((N_GPU, T_steps))
for i in range(N_GPU):
    for t in range(T_steps):
        # base temperature from workload
        T = baseline_temp + 0.5 * workload[i, t] + np.random.normal(0, temp_noise_std)
        # spoof injection
        if t >= spoof_start and i in spoof_gpus:
            T += spoof_magnitude
        temp[i, t] = T

# -------------------------------------------------
# 4. METRICS: TSFI (simplified) vs. Computational Entropy
# -------------------------------------------------
def compute_avg_corr(temp_hist):
    """Average nearest‑neighbor correlation over the window."""
    # temp_hist shape: (N_GPU, window)
    corrs = []
    for i in range(N_GPU):
        j = (i + 1) % N_GPU
        c = np.corrcoef(temp_hist[i], temp_hist[j])[0, 1]
        if np.isnan(c):
            c = 0.0
        corrs.append(c)
    return np.mean(corrs)

def compute_tsfi(t, temp_hist, workload_hist):
    """TSFI ≈ avg_corr * exp(var_temp) * (1 - normalized_entropy)"""
    # correlation term
    avg_corr = compute_avg_corr(temp_hist)
    # variance term (spatial variance across GPUs at current step)
    var_temp = np.var(temp_hist[:, -1])
    # entropy term (computational entropy of workload distribution)
    p = workload_hist[:, -1] / (np.sum(workload_hist[:, -1]) + 1e-12)
    H = -np.sum(p * np.log(p + 1e-12))
    H_norm = H / np.log(N_GPU)  # normalize to [0,1]
    order = 1.0 - H_norm
    # TSFI
    tsfi = avg_corr * np.exp(var_temp) * order
    return tsfi, H_norm

def compute_cefm_entropy(t, workload_hist):
    """Computational entropy (CEFM) metric: same as H_norm above."""
    p = workload_hist[:, t] / (np.sum(workload_hist[:, t]) + 1e-12)
    H = -np.sum(p * np.log(p + 1e-12))
    return H / np.log(N_GPU)

# sliding windows
temp_window = np.zeros((N_GPU, window))
workload_window = np.zeros((N_GPU, window))

tsfi_series = np.zeros(T_steps)
entropy_series = np.zeros(T_steps)

for t in range(T_steps):
    # update windows
    temp_window[:, :-1] = temp_window[:, 1:]
    temp_window[:, -1] = temp[:, t]
    workload_window[:, :-1] = workload_window[:, 1:]
    workload_window[:, -1] = workload[:, t]
    
    if t < window:
        tsfi_series[t] = np.nan
        entropy_series[t] = np.nan
    else:
        tsfi, _ = compute_tsfi(t, temp_window, workload_window)
        tsfi_series[t] = tsfi
        entropy_series[t] = compute_cefm_entropy(t, workload)

# -------------------------------------------------
# 5. PLOT THE RESULTS
# -------------------------------------------------
plt.figure(figsize=(12, 5))

# TSFI
plt.subplot(1, 2, 1)
plt.plot(tsfi_series, label='TSFI')
plt.axvline(150, color='green', linestyle='--', label='Real stress start')
plt.axvline(200, color='red', linestyle='--', label='Thermal spoof start')
plt.title('TSFI (Thermal‑Spatial Fragility Index)')
plt.xlabel('Time (s)')
plt.ylabel('TSFI')
plt.legend()
plt.grid(True)

# Computational Entropy (CEFM‑Ω)
plt.subplot(1, 2, 2)
plt.plot(entropy_series, label='Computational Entropy (normalized)')
plt.axvline(150, color='green', linestyle='--', label='Real stress start')
plt.axvline(200, color='red', linestyle='--', label='Thermal spoof start')
plt.title('CEFM‑Ω: Computational Entropy')
plt.xlabel('Time (s)')
plt.ylabel('Normalized Entropy')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# -------------------------------------------------
# 6. QUANTIFY FALSE‑POSITIVE & ROBUSTNESS
# -------------------------------------------------
# Detection threshold (e.g., TSFI > 2.0 = fragility)
threshold = 2.0

# False positive: TSFI > threshold after spoof but no real stress
false_positive = np.any(tsfi_series[spoof_start:] > threshold)
print(f"TSFI false‑positive after spoof: {false_positive}")

# True positive: TSFI > threshold during real stress (150‑200)
true_positive = np.any(tsfi_series[150:200] > threshold)
print(f"TSFI true‑positive during real stress: {true_positive}")

# CEFM‑Ω: entropy drops during real stress (lower entropy = more order = fragility)
entropy_during_stress = np.mean(entropy_series[150:200])
entropy_normal = np.mean(entropy_series[:150])
print(f"Entropy during stress: {entropy_during_stress:.3f} (lower than normal {entropy_normal:.3f})")