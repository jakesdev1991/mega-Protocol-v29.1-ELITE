# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation of the informational jerk stability for a Linux HSA node.
Computes J_stab from the corrected formula and compares it to the empirical
threshold J_thresh = 5.0e12 s^-3.
"""

import math

# ----------------------------------------------------------------------
# Input data (already normalised where required)
# ----------------------------------------------------------------------
# Dimensionless field magnitudes
phi_N   = 0.78          # Φ_N / v
phi_D   = 0.35          # Φ_Δ / v

# Time derivatives of the dimensionless fields (s^-1)
phi_dot_N   = 2.1e3     # dφ_N/dt
phi_dot_D   = 8.7e3     # dφ_Δ/dt

# Stiffness: ξ^{-2} = λ v^2 = 4.2e6 s^-2  → ξ^4 = (ξ^{-2})^2
xi_inv_sq = 4.2e6       # s^-2
xi_sq     = 1.0 / xi_inv_sq   # s^2
xi_pow4   = xi_sq * xi_sq     # s^4

# Source jerk term (s^-3)
J_source = 1.5e12

# ----------------------------------------------------------------------
# Jerk calculation (dimensionless formula)
#   J_stab = (3*phi_D/ξ^4)*(phi_dot_D)^3 - (phi_N/ξ^4)*(phi_dot_N)^3 + J_source
# ----------------------------------------------------------------------
term_archive = (3.0 * phi_D) / xi_pow4 * (phi_dot_D ** 3)
term_newton  =        phi_N  / xi_pow4 * (phi_dot_N ** 3)

J_stab = term_archive - term_newton + J_source

# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------
print("=== Informational Jerk Stability Validation ===")
print(f"Dimensionless Newtonian field      φ_N   = {phi_N}")
print(f"Dimensionless Archive field        φ_Δ   = {phi_D}")
print(f"Newtonian velocity                 φ̇_N  = {phi_dot_N:.3e} s⁻¹")
print(f"Archive velocity                   φ̇_Δ  = {phi_dot_D:.3e} s⁻¹")
print(f"Stiffness ξ⁻²                      = {xi_inv_sq:.3e} s⁻²")
print(f"ξ⁴                                 = {xi_pow4:.3e} s⁴")
print(f"Source jerk J_source               = {J_source:.3e} s⁻³")
print()
print(f"Archive term   (3φ_Δ/ξ⁴)φ̇_Δ³      = {term_archive:.3e} s⁻³")
print(f"Newtonian term ( φ_N/ξ⁴)φ̇_N³      = {term_newton:.3e} s⁻³")
print(f"Computed J_stab                     = {J_stab:.3e} s⁻³")
print()
print(f"Empirical stability threshold J_thr = 5.0e12 s⁻³")
print(f"Is J_stab < J_thr ?  {J_stab < 5.0e12}")

# ----------------------------------------------------------------------
# Simple assertion for automated checking (will raise AssertionError if fails)
# ----------------------------------------------------------------------
assert J_stab < 5.0e12, "Jerk stability threshold exceeded!"
print("\n✅  Validation passed: node is stable (J_stab below threshold).")