# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- simulation parameters ---
dt = 1e-4
T = 8.0
t = np.arange(0, T, dt)
N = len(t)
sigma = 0.15          # noise amplitude
phi = np.zeros(N)
phi[0] = 1.0          # initial order parameter

# control parameter a(t) ramps from stable (a>phi^2) to critical (a~phi^2)
a = np.linspace(2.0, 0.5, N)

# --- Langevin integration (Euler-Maruyama) ---
for i in range(1, N):
    dV_dphi = 4.0 * phi[i-1] * (phi[i-1]**2 - a[i-1])
    phi[i] = phi[i-1] - dV_dphi * dt + sigma * np.sqrt(dt) * np.random.randn()

# --- observables ---
# treat "current" as proportional to phi
I = phi

# jerk via central differences (noise amplified)
jerk = np.gradient(np.gradient(np.gradient(I, dt), dt), dt)

# correlation lengths from potential curvature
second_N = 12.0 * phi**2 - 4.0 * a   # ∂²V/∂Φ_N² (approx as ∂²V/∂Φ_Δ² for symmetric case)
xi = 1.0 / np.sqrt(np.maximum(np.abs(second_N), 1e-12))

# stiffness ratio (here xi_N ≈ xi, so ratio ~1 far from threshold, →0 near threshold)
R = xi / (xi + 1e-6)   # avoid division by zero

# --- plotting ---
fig, ax = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
ax[0].plot(t, phi, label='Φ (order parameter)')
ax[0].legend()
ax[0].set_ylabel('Φ')
ax[0].axvline(x=t[np.argmin(np.abs(second_N))], color='k', ls='--', lw=1)

ax[1].plot(t, jerk, label='jerk d³I/dt³', alpha=0.7)
ax[1].legend()
ax[1].set_ylabel('jerk')
ax[1].set_yscale('symlog')

ax[2].plot(t, R, label='stiffness ratio R=ξ_N/ξ_Δ')
ax[2].legend()
ax[2].set_ylabel('R')
ax[2].set_xlabel('time')
ax[2].set_yscale('log')
plt.tight_layout()
plt.show()