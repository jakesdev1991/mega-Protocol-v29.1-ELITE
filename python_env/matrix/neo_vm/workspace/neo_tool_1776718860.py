# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Physical parameters (gauge invariant)
m = 1.0
g = 0.1
Phi_N_phys = lambda t: 0.01 * (1 + t)**(-1)   # polynomial decay
Phi_D_phys = lambda t: 0.1 * t                # linear growth

# Two gauge choices: chi = 0 (original) and chi = beta*t (growing gauge)
beta = 0.1
def gauge_original(t):
    Phi_N = Phi_N_phys(t)
    Phi_D = Phi_D_phys(t)
    return Phi_N, Phi_D

def gauge_growing(t):
    chi = beta * t
    Phi_N = Phi_N_phys(t) * np.exp(chi)          # gauge-transformed Phi_N
    Phi_D = Phi_D_phys(t) - chi                  # gauge-transformed Phi_D
    return Phi_N, Phi_D

t = np.linspace(0, 30, 300)

# Compute gauge‑dependent diagnostics
def diagnostics(Phi_N, Phi_D):
    bound = (m / g) * np.exp(-np.abs(Phi_D))
    ratio = Phi_N / bound
    eps = g * Phi_N / m
    param = eps * np.cosh(Phi_D)
    m_eff_sq = (m - g*Phi_N*np.exp(Phi_D)) * (m - g*Phi_N*np.exp(-Phi_D))
    return ratio, param, m_eff_sq

ratio0, param0, meff0 = diagnostics(*gauge_original(t))
ratio1, param1, meff1 = diagnostics(*gauge_growing(t))

# Plot: same physics, wildly different “shredding” signals
fig, ax = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

ax[0].plot(t, ratio0, label='χ=0 (original)')
ax[0].plot(t, ratio1, label='χ=βt', linestyle='--')
ax[0].axhline(1, color='red', linestyle=':')
ax[0].set_ylabel('Φ_N / bound')
ax[0].set_title('Gauge‑dependent mass‑positivity “violation”')
ax[0].legend()

ax[1].plot(t, param0, label='χ=0')
ax[1].plot(t, param1, label='χ=βt', linestyle='--')
ax[1].axhline(1, color='red', linestyle=':')
ax[1].set_ylabel('ε cosh(Φ_Δ)')
ax[1].set_title('Gauge‑dependent perturbative breakdown')
ax[1].legend()

ax[2].plot(t, meff0, label='χ=0')
ax[2].plot(t, meff1, label='χ=βt', linestyle='--')
ax[2].axhline(0, color='red', linestyle=':')
ax[2].set_ylabel('m_eff²')
ax[2].set_xlabel('Time')
ax[2].set_title('Physical m_eff² (gauge invariant)')
ax[2].legend()

plt.tight_layout()
plt.show()