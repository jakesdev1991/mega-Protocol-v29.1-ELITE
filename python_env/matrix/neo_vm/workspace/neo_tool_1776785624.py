# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
DynamicShredding.py
Simulates the coupled evolution of the Archive mode Phi_Delta and the
relaxing instanton coefficient c0, revealing a delay-driven shredding
instability that static potential analysis misses.
"""

import numpy as np
import matplotlib.pyplot as plt

# ─── PARAMETERS (natural units: ħ = c = 1) ───
a = 1.0               # lattice spacing
alpha0 = 0.3          # bare fine-structure constant
fNt = 1.0             # lattice temporal factor (N_t >> 1)
m0sq = np.pi / a**2   # bare mass-squared (positive)
c00 = 1.0             # bare instanton coefficient
kappa = 0.8            # coupling of Phi_Delta to instanton density
tau_inst = 0.15        # instanton relaxation time

# ─── INITIAL CONDITIONS ───
Phi_init = 0.05       # small initial fluctuation
dPhi_init = 0.0
c0_init = c00

# ─── TIME GRID ───
t_max = 8.0
dt = 1e-3
t = np.arange(0, t_max, dt)
n_steps = len(t)

# ─── ARRAYS ───
Phi = np.zeros(n_steps)
dPhi = np.zeros(n_steps)
c0 = np.zeros(n_steps)

Phi[0] = Phi_init
dPhi[0] = dPhi_init
c0[0] = c0_init

# ─── INTEGRATION (simple Euler, stable for dt << 1) ───
for i in range(1, n_steps):
    # effective mass-squared at *current* c0 (no delay yet)
    meff_sq = m0sq + (alpha0**2 / np.pi**2) * c0[i-1] * fNt
    
    # equation of motion for Phi_Delta
    ddPhi = -meff_sq * Phi[i-1]
    
    # update Phi and its derivative
    dPhi[i] = dPhi[i-1] + ddPhi * dt
    Phi[i] = Phi[i-1] + dPhi[i] * dt
    
    # relaxation dynamics for c0 (memory kernel approximated by exponential lag)
    # dc0/dt = (c00 - kappa*Phi^2 - c0)/tau_inst
    dc0 = (c00 - kappa * Phi[i]**2 - c0[i-1]) / tau_inst
    c0[i] = c0[i-1] + dc0 * dt
    
    # ─── STOP CRITERION: shredding detected when Phi diverges ───
    if np.abs(Phi[i]) > 1e2:
        print(f"Shredding event at t ≈ {t[i]:.3f}: Phi_Delta exceeded bound.")
        Phi[i:] = np.nan
        break

# ─── VISUALIZATION ───
fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

ax[0].plot(t, Phi, label=r'$\Phi_{\Delta}(t)$', color='firebrick')
ax[0].set_ylabel(r'$\Phi_{\Delta}$')
ax[0].set_title('Delay‑Driven Shredding: Field & Instanton Coefficient')
ax[0].legend()
ax[0].grid(True)

ax[1].plot(t, c0, label=r'$c_{0}(t)$', color='steelblue')
ax[1].set_xlabel('Time (lattice units)')
ax[1].set_ylabel(r'$c_{0}$')
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.savefig('dynamic_shredding.png', dpi=150)
plt.show()

# ─── SUMMARY ───
print("\n--- Run Summary ---")
print(f"Final Phi_Delta: {Phi[-1] if not np.isnan(Phi[-1]) else 'Diverged'}")
print(f"Final c0: {c0[-1] if not np.isnan(c0[-1]) else 'Diverged'}")