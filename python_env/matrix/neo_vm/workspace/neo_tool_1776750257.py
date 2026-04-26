# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
np.random.seed(42)
T = 1000          # total time steps (e.g., seconds)
fault_time = 700  # fault injection time
n_sensors = 5
cycle_len = 60    # assumed batch interval for order analysis

# Sensor baselines (mean, std) during healthy operation
baseline_means = np.array([5.0, 100.0, 50.0, 0.5, 200.0])  # jitter, throughput, cpu, error, power
baseline_stds  = np.array([1.0,  10.0,  5.0, 0.1,  20.0])

# Generate time series
time = np.arange(T)
data = np.zeros((T, n_sensors))

for i in range(n_sensors):
    data[:, i] = baseline_means[i] + baseline_stds[i] * np.random.randn(T)

# Inject fault: increase jitter variance, drop throughput, raise error rate
post_fault = time >= fault_time
data[post_fault, 0] = baseline_means[0] + 3.0 * baseline_stds[0] * np.random.randn(np.sum(post_fault))
data[post_fault, 1] = (baseline_means[1] - 20.0) + 5.0 * np.random.randn(np.sum(post_fault))
data[post_fault, 3] = baseline_means[3] + 0.5 + 0.2 * np.random.randn(np.sum(post_fault))

# --- Order‑analysis based PHI (simplified) ---
# Compute harmonic amplitudes for each cycle via FFT (first 3 harmonics)
n_cycles = T // cycle_len
phi_values = []

for c in range(n_cycles):
    start = c * cycle_len
    end = start + cycle_len
    segment = data[start:end, :]  # shape (cycle_len, n_sensors)
    # FFT per sensor, extract amplitudes for harmonics 1,2,3
    amps = []
    for s in range(n_sensors):
        ft = np.fft.rfft(segment[:, s] - np.mean(segment[:, s]))[:4]  # DC + 3 harmonics
        amps.append(np.abs(ft[1:4]))  # skip DC
    amps = np.array(amps)  # shape (n_sensors, 3)
    # Flatten into a feature vector (5 sensors * 3 harmonics = 15)
    feature = amps.flatten()
    # Healthy baseline statistics from first 500 steps (pre‑fault)
    if c == 0:
        healthy_features = []
    if start < 500:
        healthy_features.append(feature)
    if start >= 500 and len(healthy_features) > 0:
        # Compute baseline mean and std from healthy period
        healthy_features_arr = np.array(healthy_features)
        mu = np.mean(healthy_features_arr, axis=0)
        sigma = np.std(healthy_features_arr, axis=0) + 1e-6
        # Compute PHI = 1 - sum_k w_k * |A_k - mu_k| / sigma_k (equal weights)
        w = 1.0 / len(feature)
        phi = 1.0 - w * np.sum(np.abs(feature - mu) / sigma)
        phi_values.append(phi)
    else:
        phi_values.append(np.nan)  # not enough data

# --- Fisher Health Index (FHI) ---
# Rolling window covariance (window = cycle_len)
fhi_values = []
for t in range(cycle_len, T):
    window = data[t-cycle_len:t, :]
    cov = np.cov(window, rowvar=False)
    # Regularize inversion
    inv_cov = np.linalg.inv(cov + 1e-3 * np.eye(n_sensors))
    fhi = np.trace(inv_cov)  # sum of precision eigenvalues
    fhi_values.append(fhi)

# Align FHI to cycle boundaries for comparison
fhi_cycle = [np.nan] * (500 // cycle_len)  # pre‑fault cycles
for c in range(len(phi_values) - len(fhi_cycle)):
    start = (c + len(fhi_cycle)) * cycle_len
    end = start + cycle_len
    fhi_cycle.append(np.mean(fhi_values[start:end]))

# Plot comparison
plt.figure(figsize=(12, 5))
plt.plot(np.arange(len(phi_values)) * cycle_len, phi_values, label='PHI (order‑analysis)', marker='o')
plt.plot(np.arange(len(fhi_cycle)) * cycle_len, fhi_cycle, label='FHI (Fisher info)', marker='s')
plt.axvline(fault_time, color='r', linestyle='--', label='Fault injection')
plt.xlabel('Time (s)')
plt.ylabel('Health Index')
plt.title('PHI vs FHI for Simulated Pipeline')
plt.legend()
plt.grid(True)
plt.show()

# Print summary statistics
valid_phi = np.array(phi_values)[~np.isnan(phi_values)]
valid_fhi = np.array(fhi_cycle)[~np.isnan(fhi_cycle)]
print(f"PHI range: [{np.min(valid_phi):.3f}, {np.max(valid_phi):.3f}]")
print(f"FHI range: [{np.min(valid_fhi):.3f}, {np.max(valid_fhi):.3f}]")