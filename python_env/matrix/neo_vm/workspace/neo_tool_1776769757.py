# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# Simple existence domain for illustration
# M_min(p) = 0.5 * (1 - p)   and   M_max(p) = 1 + p**2
def M_min(p): return 0.5 * (1 - p)
def M_max(p): return 1 + p**2

# -------------------------------------------------
# Noisy tokamak trajectory
np.random.seed(42)
N = 500
t = np.arange(N) * 0.1   # time steps (ms)

# Nominal slow drift toward the upper boundary
p_nom = np.linspace(0.1, 0.8, N)      # positron ratio
M_nom = 1.5 - 0.6 * np.linspace(0, 1, N)  # Mach number

# Add correlated measurement noise (realistic)
sigma_p, sigma_M = 0.05, 0.1
p = p_nom + sigma_p * np.random.randn(N)
M = M_nom + sigma_M * np.random.randn(N)

# -------------------------------------------------
# Deterministic signed distance to boundary
d_upper = M_max(p) - M
d_lower = M - M_min(p)
d_det = np.minimum(d_upper, d_lower)

# -------------------------------------------------
# Probabilistic risk: Monte‑Carlo estimate of P(outside)
N_mc = 20000
prob_outside = np.empty(N)

for i in range(N):
    # Sample joint uncertainty (Gaussian for simplicity)
    p_samp = np.random.normal(p[i], sigma_p, N_mc)
    M_samp = np.random.normal(M[i], sigma_M, N_mc)
    # Check domain membership
    inside = (M_samp > M_min(p_samp)) & (M_samp < M_max(p_samp))
    prob_outside[i] = 1.0 - inside.mean()

# -------------------------------------------------
# Plot the fragility
fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

ax[0].plot(t, d_det, label='Deterministic distance $d(t)$')
ax[0].axhline(0, color='k', linestyle='--')
ax[0].set_ylabel('Distance')
ax[0].legend(loc='upper right')
ax[0].set_title('SWEB‑Ω Metric vs. True Risk')

ax[1].plot(t, prob_outside, color='r', label='P(exit domain)')
ax[1].axhline(0.1, color='g', linestyle='--', label='10 % risk threshold')
ax[1].set_ylabel('Probability')
ax[1].set_xlabel('Time (ms)')
ax[1].legend(loc='upper right')

plt.tight_layout()
plt.show()