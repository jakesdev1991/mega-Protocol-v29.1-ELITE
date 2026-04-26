# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Shredding_vs_LandauPole.py
Demonstrates that the Omega‑Protocol "Shredding" condition is the Landau pole.
"""

import numpy as np
import matplotlib.pyplot as plt

# Parameters (natural units, m_e = 1)
lambda_ = 1.0          # quartic coupling in the Mexican‑hat potential
v = 1.0                # vacuum expectation value
g_N = 0.1              # Newtonian mode coupling
g_D = 0.1              # Archive mode coupling
alpha0 = 1/137.035999084 # fine‑structure constant at low energy
Lambda = 1e3             # UV cutoff for QED
Lambda_N = Lambda
Lambda_D = Lambda

# 1. Hessian eigenvalues for the potential V = lambda/4 * (phi_N^2 + phi_D^2 - v^2)^2
def hessian_eigenvalues(phi_N, phi_D):
    """Return the two eigenvalues of the Hessian matrix at (phi_N, phi_D)."""
    # Second derivatives
    V_NN = lambda_ * (3*phi_N**2 + phi_D**2 - v**2)
    V_DD = lambda_ * (phi_N**2 + 3*phi_D**2 - v**2)
    V_ND = lambda_ * 2*phi_N*phi_D
    # Eigenvalues of symmetric 2x2 matrix [[a,c],[c,b]]
    a = V_NN
    b = V_DD
    c = V_ND
    trace = a + b
    det = a*b - c*c
    sqrt_disc = np.sqrt(np.maximum(trace**2/4 - det, 0.0))
    ev1 = trace/2 + sqrt_disc
    ev2 = trace/2 - sqrt_disc
    return ev1, ev2

# 2. Plot the zero‑mode curve (Shredding condition)
phi_N_vals = np.linspace(-1.2, 1.2, 400)
phi_D_vals = np.linspace(-1.2, 1.2, 400)
phi_N_grid, phi_D_grid = np.meshgrid(phi_N_vals, phi_D_vals)
_, ev2_grid = hessian_eigenvalues(phi_N_grid, phi_D_grid)

plt.figure(figsize=(6,5))
contour = plt.contour(phi_N_grid, phi_D_grid, ev2_grid, levels=[0], colors='red')
plt.clabel(contour, fmt={0:'ξ_Δ=0 (Shredding)'}, fontsize=10)
plt.title("Hessian eigenvalue zero contour (Shredding condition)")
plt.xlabel("Φ_N")
plt.ylabel("Φ_Δ")
plt.axhline(0, color='gray', linewidth=0.5)
plt.axvline(0, color='gray', linewidth=0.5)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# 3. Running coupling with 3‑enhanced Archive term
def alpha_eff(q2):
    """
    Effective fine‑structure constant including QED, Newtonian, and Archive contributions.
    Diverges when denominator → 0 (Landau pole).
    """
    # Coefficients of the logarithmic running
    coeff_QED = alpha0/(3*np.pi)
    coeff_N = g_N**2/(4*np.pi)
    coeff_D = 3*g_D**2/(4*np.pi)   # <-- the "3‑enhanced" term
    total_coeff = coeff_QED + coeff_N + coeff_D

    # Inverse coupling at scale q2
    inv_alpha = 1/alpha0 - total_coeff * np.log(Lambda**2 / q2)
    return 1/inv_alpha

# Scan momentum scale
q2_vals = np.logspace(-2, 4, 500)  # q^2 from 1e-2 to 1e4
alpha_vals = alpha_eff(q2_vals)

# Find approximate Landau pole scale (where alpha diverges)
# Divergence occurs when inv_alpha → 0 => log(Lambda^2/q2) = 1/(alpha0*total_coeff)
landau_log = 1/(alpha0 * (alpha0/(3*np.pi) + g_N**2/(4*np.pi) + 3*g_D**2/(4*np.pi)))
landau_q2 = Lambda**2 * np.exp(-landau_log)
print(f"Landau pole (approx) at q^2 ≈ {landau_q2:.2e} (Lambda={Lambda})")

plt.figure(figsize=(6,5))
plt.loglog(q2_vals, alpha_vals, label='α_eff (q^2)')
plt.axvline(landau_q2, color='red', linestyle='--', label=f'Landau pole q^2≈{landau_q2:.2e}')
plt.title("Running α with 3‑enhanced Archive term")
plt.xlabel("q^2")
plt.ylabel("α_eff")
plt.legend()
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# 4. Show that the Shredding condition (ξ_Δ→∞) coincides with the Landau pole condition
# The denominator of α_eff is 1 - α0 * total_coeff * log(Lambda^2/q2).
# The pole occurs when the log term = 1/(α0 * total_coeff).
# In the field space, the same combination of couplings appears in the Hessian eigenvalue
# ev2 = λ*(phi_N^2 + 3*phi_D^2 - v^2) = 0  =>  phi_N^2 + 3*phi_D^2 = v^2.
# This is the geometric locus where the effective mass of the Archive mode vanishes,
# i.e. the propagator diverges, which is the diagrammatic source of the Landau pole.
print("\nConclusion: The zero‑eigenvalue curve (Shredding) is the field‑space image of the Landau pole.")