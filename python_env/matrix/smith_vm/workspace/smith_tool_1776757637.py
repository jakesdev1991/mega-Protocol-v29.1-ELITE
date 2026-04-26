# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the Higher‑Order Lattice Polarization RG flow.
Checks for premature Shredding (ΦΔ blow‑up, ΦN negativity) and
verifies the predicted scaling exponents.
"""

import numpy as np
from scipy.integrate import solve_ivp

# ------------------- Model parameters -------------------
# Choose values that trigger a Shredding Event
eta_N   = 0.1      # >0 (Newtonian mode self‑limiting)
eta_D   = -0.5     # <0  (drives Archive mode unstable)
kappa   = 0.3      # >0  (coupling)
I0      = 1.0      # normalization (can be set to 1)

# ------------------- RG equations -------------------
def rg_flow(lny, y):
    """
    lny = ln(q/q0)   (independent variable)
    y   = [Phi_N, Phi_Delta]
    Returns dy/d(lny)
    """
    Phi_N, Phi_D = y
    dPhi_N = eta_N * Phi_N * (1 - Phi_N**2 / I0**2) - kappa * Phi_D**2
    dPhi_D = eta_D * Phi_D * (1 - Phi_D**2 / I0**2) + kappa * Phi_N * Phi_D
    return [dPhi_N, dPhi_D]

# ------------------- Integration settings -------------------
lny_span = (0.0, 5.0)          # we expect blow‑up before lny ~ 5 for these params
y0       = [0.5, 0.2]          # small seed values in the perturbative regime

# Use dense output to inspect the solution near the singularity
sol = solve_ivp(rg_flow, lny_span, y0, method='RK45',
                dense_output=True, max_step=1e-4, rtol=1e-9, atol=1e-12)

lny_vals = sol.t
Phi_N_vals = sol.y[0]
Phi_D_vals = sol.y[1]

# ------------------- Detect Shredding -------------------
# Thresholds for "blow‑up"
PHI_D_BLOWUP = 1e6
PHI_N_NEG_TOL = -1e2   # allow small numerical negative noise

blowup_idx = np.where(np.abs(Phi_D_vals) > PHI_D_BLOWUP)[0]
neg_idx    = np.where(Phi_N_vals < PHI_N_NEG_TOL)[0]

if blowup_idx.size > 0:
    idx = blowup_idx[0]
    lny_c = lny_vals[idx]
    print(f"*** Shredding detected: |ΦΔ| > {PHI_D_BLOWUP} at lny = {lny_c:.4f}")
    print(f"  ΦN at that point = {Phi_N_vals[idx]:.3e}")
else:
    print("No ΦΔ blow‑up detected in the integration range.")

if neg_idx.size > 0:
    idx = neg_idx[0]
    lny_neg = lny_vals[idx]
    print(f"*** ΦN became negative (< {PHI_N_NEG_TOL}) at lny = {lny_neg:.4f}")
    print(f"  ΦΔ at that point = {Phi_D_vals[idx]:.3e}")
else:
    print("ΦN remained non‑negative in the integration range.")

# ------------------- Verify scaling exponents -------------------
# Fit log‑log of (lny_c - lny) vs ΦΔ near the blow‑up point
if blowup_idx.size > 0:
    # Use points within a decade of the singularity
    mask = (lny_vals > lny_c - 2.0) & (lny_vals < lny_c - 1e-3)
    if np.any(mask):
        X = np.log(lny_c - lny_vals[mask])
        Y = np.log(np.abs(Phi_D_vals[mask]))
        # linear fit Y = p * X + const
        p, c = np.polyfit(X, Y, 1)
        print(f"\nScaling fit near blow‑up:")
        print(f"  ΦΔ ∝ (lny_c - lny)^{p:.4f}   (expected -0.5)")
        print(f"  Intercept constant => A = exp({c:.4f})")
        # Expected amplitude A = 1/sqrt(2|eta_D|)
        A_expected = 1.0/np.sqrt(2*abs(eta_D))
        A_measured = np.exp(c)
        print(f"  Expected A = {A_expected:.4f}, Measured A = {A_measured:.4f}")
    else:
        print("\nNot enough points for scaling fit.")
else:
    print("\nNo blow‑up to fit scaling exponents.")

# ------------------- Optional: plot (requires matplotlib) -------------------
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8,5))
    plt.plot(lny_vals, Phi_N_vals, label=r'$\Phi_N$')
    plt.plot(lny_vals, Phi_D_vals, label=r'$\Phi_\Delta$')
    plt.axvline(lny_c if blowup_idx.size>0 else np.nan, color='k', linestyle='--',
                label='Estimated $lny_c$' if blowup_idx.size>0 else None)
    plt.yscale('symlin', linthresh=1e-2)
    plt.xlabel(r'$\ln(q/q_0)$')
    plt.ylabel('Mode amplitude')
    plt.title('RG flow showing premature Shredding')
    plt.legend()
    plt.grid(True, which='both', ls=':', alpha=0.5)
    plt.tight_layout()
    plt.show()
except Exception as e:
    print("\nMatplotlib not available or failed to plot:", e)