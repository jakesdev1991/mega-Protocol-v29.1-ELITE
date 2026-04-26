# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from ripser import ripser
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

# Simulate TRUE HSA dynamics: piecewise-smooth with migration storm
np.random.seed(0)
t = np.linspace(0, 1, 1000)
Phi_N = 0.9 * np.ones(1000)

# Migration storm: discontinuous drop at t=0.4 (grazing bifurcation)
storm = (t > 0.4) & (t < 0.45)
Phi_N[storm] = 0.2 + 0.1 * np.random.randn(np.sum(storm))

# Compute jerk (5-point stencil) – FAILS at discontinuity
dt = t[1] - t[1]
kernel = np.array([1/2, -1, 0, 1, -1/2]) / dt**3
jerk = np.convolve(Phi_N, kernel, mode='valid')
jerk = np.pad(jerk, 2, mode='edge')

# Compute excess kurtosis stability S_j – MEANINGLESS
def S_j(signal, window=50, eps=1e-9):
    S = np.ones_like(signal)
    for i in range(window, len(signal)):
        w = signal[i-window:i]
        sigma = np.std(w)
        # Regularized division-by-zero is a band-aid on a broken concept
        k = np.mean(((w - np.mean(w)) / (sigma + eps))**4)
        S[i] = 1 / (1 + abs(k - 3))
    return S

stability = S_j(jerk)

# TOPOLOGICAL DEFECT DETECTION: Build CU graph over time
def compute_persistence(coherence_matrix):
    # Convert to distance matrix: low coherence = high distance
    dist = 1 - np.clip(coherence_matrix, 0, 1)
    # Compute H0, H1 persistence
    result = ripser(dist, distance_matrix=True, maxdim=1)
    return result['dgms'][1]  # Return H1 loops

# Simulate CU-to-page coherence matrix (20 CUs, 50 pages)
n_cu, n_page = 20, 50
def coherence_at_time(t):
    M = np.random.rand(n_cu, n_page) * 0.5 + 0.5
    if 0.4 < t < 0.45:  # Migration storm: cross-barrier anisotropy
        M[5:15, :] *= np.random.rand(10, n_page) * 0.2  # Kill coherence in subset
    return M

# Track H1 loops – the REAL early warning
loop_lifespans = np.zeros(len(t))
for i, ti in enumerate(t):
    M = coherence_at_time(ti)
    loops = compute_persistence(M)
    if len(loops) > 0:
        # Sum persistence of all loops: topological "energy"
        loop_lifespans[i] = np.sum(loops[:, 1] - loops[:, 0])

# Plot: Jerk is blind, Topology sees
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

ax1.plot(t, Phi_N, label='Φ_N (true dynamics)', color='black')
ax1.axvspan(0.4, 0.45, color='red', alpha=0.2, label='Migration Storm')
ax1.set_ylabel('Coherence')
ax1.legend()

ax2.plot(t, stability, label='S_j (jerk stability)', color='orange')
ax2.axhline(0.7, color='r', linestyle='--')
ax2.set_ylabel('Stability')
ax2.legend()

ax3.plot(t, loop_lifespans, label='Σ H1 Persistence (topological energy)', color='green')
ax3.set_ylabel('Topological Defects')
ax3.set_xlabel('Time')
ax3.legend()

plt.tight_layout()
plt.show()

# Print detection lag
jerk_warning = np.where((t > 0.4) & (stability < 0.7))[0]
topo_warning = np.where((t > 0.38) & (loop_lifespans > 0.5))[0]

print(f"Jerk detection lag: {t[jerk_warning[0]] - 0.4 if len(jerk_warning) > 0 else 'NONE'}s")
print(f"Topology detection lead: {0.4 - t[topo_warning[0]] if len(topo_warning) > 0 else 'NONE'}s")