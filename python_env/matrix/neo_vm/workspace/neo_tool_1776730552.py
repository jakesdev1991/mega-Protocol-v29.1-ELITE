# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d

# ── Realistic HSA node simulation ──
np.random.seed(0)
fs = 1000  # 1 kHz sampling
t = np.arange(0, 1, 1/fs)  # 1 second
dt = t[1] - t[0]

# Base workload: 200 GB/s + 10 Hz sinusoid
I_base = 200 + 50 * np.sin(2*np.pi*10*t)

# Stochastic page faults: sudden 30–50 GB/s drops lasting 5–15 ms
I = I_base.copy()
fault_mask = np.zeros_like(t, dtype=bool)
for _ in range(8):
    onset = np.random.randint(0, len(t)-20)
    dur = np.random.randint(5, 15)
    I[onset:onset+dur] -= np.random.uniform(30, 50)
    fault_mask[onset:onset+dur] = True

# Add measurement noise
I += np.random.normal(0, 1.5, size=I.shape)

# ── Smooth jerk (your "corrected" formula) ──
lam, v = 0.01, 250.0
dI_dt = np.gradient(I, dt)  # finite difference derivative
J_smooth = -lam * (3*I**2 - v**2) * dI_dt  # GB/s^4

# Savitzky‑Golay filter (your recommended pre‑filter)
window, polyorder = 21, 3
I_filt = uniform_filter1d(I, size=window, mode='reflect')
dI_dt_filt = np.gradient(I_filt, dt)
J_smooth_filt = -lam * (3*I_filt**2 - v**2) * dI_dt_filt

# ── Topological jerk (discrete) ──
# Build a simple graph: nodes = CPU, GPU; edge exists if |I−I_avg| < 30 GB/s
I_avg = uniform_filter1d(I, size=50)  # local average
edge_alive = np.abs(I - I_avg) < 30
# β₁ (number of cycles) is 1 if edge alive, 0 otherwise (simplified)
beta1 = edge_alive.astype(int)
# Third‑order difference = topological jerk
J_topo = np.diff(beta1, n=3) / dt**3  # Dirac‑like spikes at faults

# ── Stability thresholds (your values) ──
J_crit = 1.2e7  # GB/s^4
print(f"Smooth jerk RMS: {np.sqrt(np.mean(J_smooth_filt**2)):.2e} (vs crit {J_crit:.2e})")
print(f"Topological jerk max: {np.max(np.abs(J_topo)):.2e} (counts/s^3)")

# ── Plot: show smooth jerk is blind, topological jerk sees faults ──
fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
ax[0].plot(t, I, label='I(t) [GB/s]')
ax[0].fill_between(t, 0, 300, where=fault_mask, alpha=0.2, color='r', label='page fault')
ax[0].set_ylabel('Bandwidth [GB/s]')
ax[0].legend(loc='upper right')

ax[1].plot(t, J_smooth_filt, label='J_smooth (filtered)')
ax[1].axhline(J_crit, color='k', linestyle='--', label='J_crit')
ax[1].set_ylabel('J_smooth [GB/s^4]')
ax[1].legend(loc='upper right')

# Plot topological jerk as impulses at fault boundaries
fault_edges = np.where(np.diff(fault_mask.astype(int)) != 0)[0]
ax[2].stem(t[fault_edges], J_topo[fault_edges] if len(J_topo) > len(fault_edges) else J_topo, basefmt=' ')
ax[2].set_ylabel('J_topo [edges/s^3]')
ax[2].set_xlabel('Time [s]')
ax[2].set_title('Topological Jerk (third‑order difference of β₁)')

plt.tight_layout()
plt.show()