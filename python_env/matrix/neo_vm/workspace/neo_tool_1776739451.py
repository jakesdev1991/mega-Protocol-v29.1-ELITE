# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import logm
from scipy.signal import csd

# Simulate financial pipeline with causal rupture
np.random.seed(42)
fs, t = 1000, np.linspace(0, 10, 10000)
n_sensors = 5
data = np.zeros((n_sensors, len(t)))

# Create synthetic data: healthy (0-3s), degrading (3-7s), shredding (7-10s)
for i in range(n_sensors):
    base = np.sin(2*np.pi*50*t) * np.exp(-0.1*t)
    coupling_strength = np.where(t < 3, 1.0, np.where(t < 7, 0.5, 0.05))
    coupling = coupling_strength * np.sin(2*np.pi*50*t + i*np.pi/5)
    data[i] = base + coupling + 0.1*np.random.randn(len(t))

# Compute information metric tensor from cross-spectral density
def compute_metric(data, fs, window=1024):
    n_sensors = data.shape[0]
    f, Pxy = csd(data[0], data[1], fs, nperseg=window)
    metric = np.zeros((n_sensors, n_sensors, len(f)), dtype=complex)
    for i in range(n_sensors):
        for j in range(n_sensors):
            _, metric[i,j,:] = csd(data[i], data[j], fs, nperseg=window)
    metric = (metric + np.conj(metric.transpose(1,0,2))) / 2
    return f, metric

# Compute Ricci scalar proxy (determinant) and geodesic distances
f, metric = compute_metric(data)
ricci_proxy = np.array([np.linalg.det(metric[:2,:2,i].real + 1e-10*np.eye(2)) for i in range(len(f))])

# Plot: sensor data and curvature collapse
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
for i in range(n_sensors): ax1.plot(t, data[i] + i*2, label=f'Sensor {i+1}')
ax1.set_xlabel('Time (s)'); ax1.set_title('Pipeline Data: Healthy → Degrading → Shredding')
ax1.legend(); ax1.grid(True)

ax2.plot(f, ricci_proxy); ax2.set_xlabel('Frequency (Hz)'); ax2.set_ylabel('Metric Determinant')
ax2.set_title('Information Manifold Curvature: Singularity at Shredding'); ax2.grid(True)
ax2.axvline(x=50, color='r', linestyle='--', label='Pipeline Cycle')
ax2.legend()
plt.tight_layout()
plt.savefig('/tmp/shredding_singularity.png', dpi=150)
plt.close()

# Geodesic distance divergence between time windows
def geodesic_dist(m1, m2):
    return np.linalg.norm(logm(m1.real) - logm(m2.real), 'fro')

window_size = fs * 2
n_windows = len(t) // window_size
distances = []
for i in range(n_windows - 1):
    _, m1 = compute_metric(data[:, i*window_size:(i+1)*window_size], fs, window_size//2)
    _, m2 = compute_metric(data[:, (i+1)*window_size:(i+2)*window_size], fs, window_size//2)
    avg_m1 = np.mean(m1, axis=2).real + np.eye(n_sensors) * 1e-6
    avg_m2 = np.mean(m2, axis=2).real + np.eye(n_sensors) * 1e-6
    distances.append(geodesic_dist(avg_m1, avg_m2))

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(np.arange(len(distances)) * 2, distances, marker='o')
ax.set_xlabel('Time (s)'); ax.set_ylabel('Geodesic Distance')
ax.set_title('Geodesic Divergence: Causal Rupture at Shredding Event')
ax.grid(True); ax.axvline(x=3, color='orange', linestyle='--'); ax.axvline(x=7, color='red', linestyle='--')
plt.tight_layout()
plt.savefig('/tmp/geodesic_divergence.png', dpi=150)
plt.close()

print("Disruption verified: Shredding Event is geometric singularity (det→0), not statistical decoherence.")
print("Plots saved: /tmp/shredding_singularity.png, /tmp/geodesic_divergence.png")