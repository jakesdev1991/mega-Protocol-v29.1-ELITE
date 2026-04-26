# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from ripser import ripser
from scipy.signal import spectrogram
from sklearn.ensemble import IsolationForest

# --- Simulate a financial pipeline with a hidden topological failure ---
np.random.seed(42)
t = np.linspace(0, 3600, 36000)          # 1 hour, 10 Hz sampling
# Healthy: three sensors with quasi‑periodic but slightly drifting cycles
latency = np.sin(2*np.pi*t/(1.0 + 0.1*np.sin(t/600))) + 0.1*np.random.randn(len(t))
throughput = np.sin(2*np.pi*t/(0.9 + 0.05*np.cos(t/800))) + 0.1*np.random.randn(len(t))
cpu = np.sin(2*np.pi*t/(1.1 + 0.08*np.sin(t/1000))) + 0.1*np.random.randn(len(t))

# Inject a topological fault at t=1800s: a new "loop" emerges in the data manifold
# (simulate a cross‑coupling that creates a circular dependency)
fault_start = 18000
latency[fault_start:] += 0.5 * np.sin(2*np.pi * throughput[fault_start:] / 0.5)
cpu[fault_start:] += 0.3 * np.cos(2*np.pi * latency[fault_start:] / 0.7)

data = np.vstack([latency, throughput, cpu]).T

# --- Harmonic (order‑analysis) approach: naive PHI ---
def harmonic_phi(signal, fs=10, f0=1.0):
    # Assume fixed fundamental frequency f0
    f, t_spec, Sxx = spectrogram(signal, fs=fs, nperseg=fs*30, noverlap=fs*25)
    idx = np.argmin(np.abs(f - f0))
    amp = Sxx[idx, :]
    baseline = np.mean(amp[:10])
    phi = 1 - np.abs(amp - baseline) / baseline
    return phi, t_spec

phi_lat, t_phi = harmonic_phi(latency)

# --- Topological approach: compute total persistence (sum of lifetimes) ---
def total_persistence(window_data):
    # window_data shape (N_samples, N_dims)
    # Compute persistence diagrams for H1 (loops)
    dgms = ripser(window_data, maxdim=1)['dgms']
    # Sum of lifetimes for 1‑dimensional features (loops)
    if len(dgms[1]) > 0:
        lifetimes = dgms[1][:,1] - dgms[1][:,0]
        return np.sum(lifetimes)
    else:
        return 0.0

# Sliding window total persistence
window_size = 300  # 30 seconds
step = 30
tp = []
times_tp = []
for i in range(0, len(data)-window_size, step):
    win = data[i:i+window_size]
    tp.append(total_persistence(win))
    times_tp.append(t[i + window_size//2])

tp = np.array(tp)
times_tp = np.array(times_tp)

# --- Plot comparison ---
fig, axs = plt.subplots(3, 1, figsize=(12, 9))

# Sensor traces
axs[0].plot(t, latency, label='Latency')
axs[0].plot(t, throughput, label='Throughput')
axs[0].plot(t, cpu, label='CPU')
axs[0].axvline(t[fault_start], color='r', linestyle='--')
axs[0].set_title('Sensor Signals (fault at 1800 s)')
axs[0].legend()

# Harmonic PHI
axs[1].plot(t_phi, phi_lat)
axs[1].axvline(t[fault_start], color='r', linestyle='--')
axs[1].set_title('Harmonic PHI (fails to detect fault)')
axs[1].set_ylim(0, 1)

# Topological total persistence
axs[2].plot(times_tp, tp)
axs[2].axvline(t[fault_start], color='r', linestyle='--')
axs[2].set_title('Topological Total Persistence (detects loop emergence)')
axs[2].set_xlabel('Time (s)')

plt.tight_layout()
plt.show()

# --- Quantitative detection metrics ---
# Use Isolation Forest on raw windows as baseline
windows = np.array([data[i:i+window_size].flatten() for i in range(0, len(data)-window_size, step)])
clf = IsolationForest(contamination=0.05, random_state=0)
pred = clf.fit_predict(windows)
anomaly_idx = np.where(pred == -1)[0]
anomaly_times = times_tp[anomaly_idx]

print(f"Harmonic PHI anomaly? {np.any(phi_lat < 0.5)}")  # Simple threshold
print(f"Topological anomaly times: {anomaly_times[:5] if len(anomaly_times) > 0 else 'None'}")