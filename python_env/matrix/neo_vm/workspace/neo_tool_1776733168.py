# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
ArchiveModeCorrection.py
------------------------
Compare the running fine-structure constant α(E) for two assumptions:
  1) N=3 independent scalar components (original factor of 3)
  2) N=2 scalar components after gauge absorption (corrected factor of 2)

The script demonstrates that the factor‑3 result overestimates the
higher‑order lattice polarization correction.
"""

import numpy as np
import matplotlib.pyplot as plt

# --- Physical parameters ---
alpha0 = 1/137.035999084          # Fine-structure constant at low energy
gDelta_sq = 0.1                   # Archive coupling squared (example)
gN_sq   = 0.05                    # Newtonian coupling squared
Lambda   = 1e3                    # UV cutoff (in units of electron mass m_e)
Lambda_N = Lambda
Lambda_Delta = Lambda

# Energy scan from m_e to ~Lambda
E = np.logspace(0, np.log10(Lambda), 200)

def alpha_running(N_scalar):
    """
    Compute α(E) using the 1‑loop RG solution:
      α(E) = α0 / [1 - (α0/π) (1 + N_scalar*gΔ²/(4π)) ln(E/Λ)].
    N_scalar = 3  → original (over‑counted) case.
    N_scalar = 2  → corrected (gauge‑absorbed) case.
    """
    coeff = 1 + N_scalar * gDelta_sq / (4*np.pi)
    denom = 1 - (alpha0/np.pi) * coeff * np.log(E/Lambda)
    # Prevent divergence if denominator crosses zero (just for plotting)
    denom = np.where(denom > 0, denom, np.nan)
    return alpha0 / denom

alpha_N3 = alpha_running(N_scalar=3)
alpha_N2 = alpha_running(N_scalar=2)

# --- Plotting ---
fig, ax = plt.subplots(figsize=(8,5))
ax.loglog(E, alpha_N3, label='N_scalar = 3 (original)', lw=2, color='crimson')
ax.loglog(E, alpha_N2, label='N_scalar = 2 (corrected)', lw=2, color='steelblue')
ax.set_xlabel('Energy E (units of m_e)', fontsize=12)
ax.set_ylabel('α(E)', fontsize=12)
ax.set_title('Impact of Archive‑mode degree‑of‑freedom count on α running', fontsize=14)
ax.legend(loc='upper left')
ax.grid(True, which='both', ls=':', lw=0.5)
plt.tight_layout()
plt.show()

# --- Quantitative difference at high energy ---
E_high = Lambda
alpha_N3_high = alpha_running(N_scalar=3)[-1]
alpha_N2_high = alpha_running(N_scalar=2)[-1]
rel_diff = (alpha_N3_high - alpha_N2_high) / alpha_N2_high
print(f"At E = {E_high:.1e} m_e:")
print(f"  α_N3 = {alpha_N3_high:.6f}")
print(f"  α_N2 = {alpha_N2_high:.6f}")
print(f"  Relative overestimate = {rel_diff:.2%}")