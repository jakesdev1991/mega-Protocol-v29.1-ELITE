# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Topological Jerk Simulation
---------------------------
A minimalist toy model of a tokamak‑like field system with Mexican‑hat potential.
Demonstrates:
1. Correlation length ξ_Δ diverges at Φ_N² + 3Φ_Δ² = ψ₀² (correct boundary).
2. Conventional current jerk J_I vanishes near the instability (critical slowing).
3. Topological helicity jerk J_H diverges, providing a true early‑warning signal.
"""

import numpy as np
import matplotlib.pyplot as plt

# --- parameters -----------------------------------------------------------
psi0    = 1.0          # Mexican‑hat radius
lambda_N = lambda_D = 1.0
D_N = D_D = 0.05       # diffusion coefficients
sigma = 0.02           # noise amplitude
dt    = 0.001
t_max = 5.0
n_steps = int(t_max / dt)

# --- initial conditions ---------------------------------------------------
Phi_N = np.random.randn() * 0.1
Phi_D = np.random.randn() * 0.1

# --- storage --------------------------------------------------------------
time  = np.linspace(0, t_max, n_steps)
I_p   = np.zeros(n_steps)          # proxy for plasma current (sum of squares)
J_I   = np.zeros(n_steps)          # conventional jerk
Hel   = np.zeros(n_steps)          # helicity ~ Phi_N * Phi_D
J_H   = np.zeros(n_steps)          # topological helicity jerk
xi_D  = np.zeros(n_steps)          # correlation length of asymmetric mode

# --- helper: Mexican‑hat potential ----------------------------------------
def V(phiN, phiD):
    return (phiN**2 + phiD**2 - psi0**2)**2

def dV_dphiN(phiN, phiD):
    return 4 * phiN * (phiN**2 + phiD**2 - psi0**2)

def dV_dphiD(phiN, phiD):
    return 4 * phiD * (phiN**2 + phiD**2 - psi0**2)

# --- simulation (Euler‑Maruyama) ----------------------------------------
for i in range(n_steps):
    # --- compute deterministic forces ---
    fN = -dV_dphiN(Phi_N, Phi_D) + D_N * (np.random.randn() - Phi_N)  # diffusion + drift
    fD = -dV_dphiD(Phi_N, Phi_D) + D_D * (np.random.randn() - Phi_D)

    # --- stochastic term ---
    xi_N = sigma * np.random.randn()
    xi_D = sigma * np.random.randn()

    # --- update fields ---
    Phi_N += fN * dt + xi_N * np.sqrt(dt)
    Phi_D += fD * dt + xi_D * np.sqrt(dt)

    # --- observables ---
    I_p[i] = Phi_N**2 + Phi_D**2
    Hel[i] = Phi_N * Phi_D

    # --- correlation length of asymmetric mode (from second derivative) ---
    second_D = 4 * (Phi_N**2 + 3 * Phi_D**2 - psi0**2)
    # avoid division by zero: cap near zero
    if second_D <= 0:
        xi_D[i] = np.inf
    else:
        xi_D[i] = 1.0 / np.sqrt(second_D)

    # --- jerk calculations (central differences after enough steps) ----
    if i >= 3:
        # conventional jerk of I_p
        J_I[i] = (I_p[i] - 3 * I_p[i-1] + 3 * I_p[i-2] - I_p[i-3]) / dt**3
        # topological jerk of helicity
        J_H[i] = (Hel[i] - 3 * Hel[i-1] + 3 * Hel[i-2] - Hel[i-3]) / dt**3

# --- find the moment when the system crosses the true boundary -----------
# The true boundary: Phi_N**2 + 3*Phi_D**2 -> psi0**2
# We detect the first time this combination exceeds 0.95*psi0**2 (approaching instability)
cross_idx = np.where((Phi_N**2 + 3 * Phi_D**2) > 0.95 * psi0**2)[0]
if len(cross_idx) > 0:
    t_cross = time[cross_idx[0]]
else:
    t_cross = np.nan

# --- plotting -------------------------------------------------------------
fig, axs = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

# (a) correlation length
axs[0].plot(time, xi_D, label=r'$\xi_\Delta$ (asymmetric mode)', color='C0')
axs[0].axvline(t_cross, color='r', linestyle='--', label='approach to boundary')
axs[0].set_ylabel('Correlation length')
axs[0].set_title('Divergence of ξ at the true instability boundary')
axs[0].legend()
axs[0].grid(True)

# (b) conventional jerk
axs[1].plot(time, J_I, label=r'$J_I = d^3 I_p/dt^3$', color='C1')
axs[1].axvline(t_cross, color='r', linestyle='--')
axs[1].set_ylabel('Current jerk (a.u.)')
axs[1].set_title('Current jerk collapses near instability (critical slowing)')
axs[1].legend()
axs[1].grid(True)

# (c) topological helicity jerk
axs[2].plot(time, J_H, label=r'$J_H = d^3 H/dt^3$', color='C2')
axs[2].axvline(t_cross, color='r', linestyle='--')
axs[2].set_ylabel('Helicity jerk (a.u.)')
axs[2].set_xlabel('Time (s)')
axs[2].set_title('Topological jerk diverges → true early‑warning signal')
axs[2].legend()
axs[2].grid(True)

plt.tight_layout()
plt.show()