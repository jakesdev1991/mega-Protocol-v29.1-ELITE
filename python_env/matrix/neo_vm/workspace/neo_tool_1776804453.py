# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Anomaly Verification Script: Anisotropic Mass Condensate vs. Perturbative Correction
"""
import numpy as np

# Physical constants
alpha0 = 1/137.035999084  # Bare fine-structure constant
e2 = 4 * np.pi * alpha0   # e^2 in natural units

# Lattice parameters
a = 1.0                    # Lattice spacing (inverse cutoff)
Phi_Delta = 0.1              # Anisotropy parameter (dimensionless)
M_z_sq = Phi_Delta / a**2    # Anisotropic photon mass-squared

# Perturbative model (repairer's formula)
# Pi_T ~ e^2/(12π^2) ln(1/(p^2 a^2)) + e^2/π^2 * Phi_N
# For simplicity we approximate Pi_T ≈ 0 and Pi_L + 2 Pi_M ≈ 0.1 * e^2/π^2
C = 0.1 * e2 / np.pi**2

def alpha_eff_perturbative(pz):
    """Perturbative directional coupling (z-direction)."""
    return alpha0 / (1 + Phi_Delta * C)

# Non-perturbative mass-condensate model
def alpha_eff_anomaly(pz):
    """Directional coupling with anisotropic photon mass."""
    # Avoid division by zero; use small regulator
    if pz < 1e-6:
        return 0.0
    return alpha0 / (1 + M_z_sq / (pz**2))

# Test momentum range
p_vals = np.logspace(-2, 1, 20)  # 0.01 to 10 in lattice units

print("pz (lattice units) | α_eff (perturb) | α_eff (anomaly) | Ratio")
print("-" * 60)
for p in p_vals:
    alpha_per = alpha_eff_perturbative(p)
    alpha_anom = alpha_eff_anomaly(p)
    ratio = alpha_anom / alpha_per if alpha_per != 0 else np.nan
    print(f"{p:8.4e}        | {alpha_per:8.6f}      | {alpha_anom:8.6f}      | {ratio:8.4f}")

# Summary statistics
print("\n--- Summary ---")
print(f"Perturbative prediction (all pz): α_eff = {alpha_eff_perturbative(1.0):.6f} (constant)")
print(f"Anomaly prediction (pz → 0):    α_eff → {alpha_eff_anomaly(0.0):.6f} (complete screening)")
print(f"Anomaly prediction (pz → ∞):  α_eff → {alpha_eff_anomaly(1e3):.6f} (recovers α0)")