# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Parameters (in natural units) ---
lambda_ = 1.0          # quartic coupling
v       = 1.0          # vacuum expectation value
phi_N   = 0.5          # fixed Newtonian background

# --- Effective curvature for a dynamical dimension count ---
def xi_inv_sq(chi, phi_Delta):
    """Inverse squared correlation length: λ(φ_N² + e^{2χ} φ_Δ² - v²)"""
    neff = np.exp(2 * chi)
    return lambda_ * (phi_N**2 + neff * phi_Delta**2 - v**2)

# --- Scan phi_Delta for several dilaton values ---
phi_Delta_vals = np.linspace(-2.0, 2.0, 500)
chi_vals = [-0.5, 0.0, 0.5, 1.0]   # chi = ln R

plt.figure(figsize=(6,4))
for chi in chi_vals:
    curv = xi_inv_sq(chi, phi_Delta_vals)
    # Mask negative curvature (classically forbidden region)
    curv = np.where(curv > 0, curv, np.nan)
    xi = 1.0 / np.sqrt(curv)
    plt.plot(phi_Delta_vals, xi, label=f'χ={chi:.2f} (n_eff≈{np.exp(2*chi):.2f})')

plt.axvline(np.sqrt((v**2 - phi_N**2)/3), color='k', linestyle='--',
            label='Fixed‑3 Shred surface')
plt.ylim(0, 5)
plt.xlabel('Φ_Δ')
plt.ylabel('ξ_Δ (correlation length)')
plt.title('Shredding surface moves with dynamical dimension count')
plt.legend()
plt.grid(True)
plt.show()