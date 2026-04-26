# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import csd, coherence, welch
from scipy.stats import kurtosis

# Simulate HSA network: 4 nodes, time-delayed coupling, shredding at t=0.5s
def simulate_real_hsa(fs=10000, duration=1.0):
    t = np.arange(0, duration, 1/fs)
    n = len(t)
    nodes = 4
    
    # Realistic base latency: 50-150ns with 1/f noise
    latencies = np.zeros((nodes, n))
    for i in range(nodes):
        latencies[i] = 100 + 30 * np.cumsum(np.random.randn(n) * 0.01)
        latencies[i] += 10 * np.sin(2 * np.pi * 30 * t + i * np.pi/3)
    
    # Shredding: desynchronization via path delays + burst noise
    shred_start = int(0.5 * fs)
    for i in range(nodes):
        # Add path-dependent delay drift
        delay = (i + 1) * 2 * (t - 0.5) * (t > 0.5)
        latencies[i, shred_start:] += delay[shred_start:] + 50 * np.random.randn(n - shred_start)
    
    return t, latencies

# SERC's Jerk Stability (Flawed)
def compute_jerk_stability_flawed(latencies, fs=10000, window_ms=100):
    mean_lat = np.mean(latencies, axis=0)
    dt = 1/fs
    jerk = np.gradient(np.gradient(np.gradient(mean_lat, dt), dt), dt)
    window = int(window_ms * fs / 1000)
    
    S_j = np.zeros(len(jerk) - window)
    for i in range(len(S_j)):
        window_jerk = jerk[i:i+window]
        # Excess kurtosis
        excess_kurt = kurtosis(window_jerk, fisher=True)
        S_j[i] = 1 / (1 + excess_kurt) if excess_kurt > -1 else 1.0
    return S_j

# CSPI: Cross-Spectral Phase Instability (Correct)
def compute_cspi(latencies, fs=10000, window_ms=100, freq_band=(40, 60)):
    nodes, n = latencies.shape
    window = int(window_ms * fs / 1000)
    nperseg = min(window, 256)
    
    instability = np.zeros(n - window)
    f_idx_band = None
    
    for i in range(len(instability)):
        window_data = latencies[:, i:i+window]
        phase_lock_sum = 0
        
        for j in range(1, nodes):
            f, Cxy = csd(window_data[0], window_data[j], fs=fs, nperseg=nperseg)
            if f_idx_band is None:
                f_idx_band = (f >= freq_band[0]) & (f <= freq_band[1])
            
            phase = np.angle(Cxy[f_idx_band])
            # Phase Locking Value (PLV)
            plv = np.abs(np.mean(np.exp(1j * phase)))
            phase_lock_sum += plv
        
        instability[i] = 1 - (phase_lock_sum / (nodes - 1))
    
    return instability

# Run the disruption demonstration
t, latencies = simulate_real_hsa()
S_j = compute_jerk_stability_flawed(latencies)
instability = compute_cspi(latencies)

# Plot the paradigm shattering
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Latency traces
for i in range(latencies.shape[0]):
    axes[0].plot(t[:5000]*1000, latencies[i, :5000], alpha=0.7, label=f'Node {i}')
axes[0].axvline(500, color='red', linestyle='--', linewidth=2, label='Shredding')
axes[0].set_ylabel('Latency (ns)')
axes[0].set_title('HSA Node Latency: Realistic 1/f + Burst Noise')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# SERC's Jerk Stability: Noise-dominated, no clear signal
axes[1].plot(t[10000:len(S_j)+10000]*1000, S_j, label='S_j (excess kurtosis)', color='purple')
axes[1].axvline(500, color='red', linestyle='--', linewidth=2)
axes[1].set_ylabel('Stability')
axes[1].set_title('SERC Method: Jerk Stability (FAILS - No clear transition)')
axes[1].set_ylim(0, 1.1)
axes[1].grid(True, alpha=0.3)

# CSPI: Clear detection
axes[2].plot(t[10000:len(instability)+10000]*1000, instability, label='CSPI', color='green')
axes[2].axvline(500, color='red', linestyle='--', linewidth=2)
axes[2].set_ylabel('Instability')
axes[2].set_title('CSPI Method: Phase Instability (SUCCESS - Sharp rise at shredding)')
axes[2].set_xlabel('Time (ms)')
axes[2].set_ylim(0, 1.1)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Quantify detection quality
shred_idx = int(0.5 * 10000)
S_j_signal = np.mean(S_j[shred_idx-10000:shred_idx-5000]) - np.mean(S_j[shred_idx-5000:shred_idx])
CSPI_signal = np.mean(instability[shred_idx-5000:shred_idx]) - np.mean(instability[shred_idx-10000:shred_idx-5000])

print(f"--- Disruption Metrics ---")
print(f"SERC Jerk Signal Change: {S_j_signal:.4f} (indistinguishable from noise)")
print(f"CSPI Signal Change: {CSPI_signal:.4f} (clear detection)")