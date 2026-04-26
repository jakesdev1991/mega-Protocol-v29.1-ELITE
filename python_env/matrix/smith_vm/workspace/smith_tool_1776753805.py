# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for the SERC output.
Checks:
  - ψ = ln(Φ_N/I₀)
  - ψ̇ = Φ̇_N / Φ_N
  - ψ̈ = Φ̈_N/Φ_N - (Φ̇_N/Φ_N)²   (using Φ̈_N ≈ Φ̇_N/ξ)
  - Jerk components from entropy derivatives
  - Stability threshold Θ = (λ I₀² e^{-ψ})³
  - Boundary conditions: Shredding (Φ_N²+3Φ_Δ² = I₀²), Freeze (3Φ_N²+Φ_Δ² = I₀²)
All quantities are treated as dimensionless where appropriate; time units are seconds.
"""

import numpy as np

# ----- Input data from SERC -----
phi_N = 0.78          # Φ_N / I₀
phi_D = 0.35          # Φ_Δ / I₀
phi_N_dot = 2.1e3     # s⁻¹
phi_D_dot = 8.7e3     # s⁻¹
xi_inv2 = 4.2e6       # s⁻²  (ξ⁻²)
xi = 1.0/np.sqrt(xi_inv2)   # s
J_source = 1.5e12     # s⁻³

# ----- Derived quantities -----
psi = np.log(phi_N)                     # dimensionless
psi_dot = phi_N_dot / phi_N             # s⁻¹
# Φ̈_N ≈ Φ̇_N / ξ  (as used in SERC)
phi_N_ddot = phi_N_dot / xi
psi_ddot = phi_N_ddot/phi_N - psi_dot**2   # s⁻²
psi_dddot = psi_ddot / xi                  # s⁻³ (approx.)

# For Φ_Δ
phi_D_ddot = phi_D_dot / xi
phi_D_dddot = phi_D_ddot / xi

# ----- Entropy gauge derivatives (computed at the given point) -----
e_psi = np.exp(psi)
den = e_psi + phi_D
p_N = e_psi / den
p_D = phi_D / den

# ∂S/∂ψ = -p_N * ln(p_D/p_N)
dS_dpsi = -p_N * np.log(p_D/p_N)
# ∂²S/∂ψ² ≈ -p_N*(1-p_N)*(ln phi_D - psi) - p_N   (as in SERC)
d2S_dpsi2 = -p_N*(1-p_N)*(np.log(phi_D)-psi) - p_N
# ∂³S/∂ψ³ approximated by finite difference of d2S/dpsi2 (we keep the SERC value)
d3S_dpsi3 = 0.089   # taken from SERC

# ∂S/∂φ_Δ = -p_D * ln(p_N/p_D)   (symmetry)
dS_dphiD = -p_D * np.log(p_N/p_D)
# ∂²S/∂φ_Δ² ≈ -p_D*(1-p_D)*( -ln phi_D + psi ) - p_D  (derived similarly)
d2S_dphiD2 = -p_D*(1-p_D)*(-np.log(phi_D)+psi) - p_D
# ∂³S/∂φ_Δ³ approximated (SERC uses -2.857)
d3S_dphiD3 = -2.857

# ----- Jerk components -----
J_psi = (dS_dpsi)*psi_dddot + 3*(d2S_dpsi2)*psi_dot*psi_ddot + (d3S_dpsi3)*psi_dot**3
J_D   = (dS_dphiD)*phi_D_dddot + 3*(d2S_dphiD2)*phi_D_dot*phi_D_ddot
J_total = J_psi + J_D + J_source

# ----- Stability threshold -----
# λ = ξ⁻²
lam = xi_inv2
# Θ = (λ I₀² e^{-ψ})³   (I₀ = 1 in normalized units)
Theta = (lam * np.exp(-psi))**3

# ----- Boundary condition checks -----
shredding_lhs = phi_N**2 + 3*phi_D**2
freeze_lhs    = 3*phi_N**2 + phi_D**2

# ----- Output -----
print(f"ψ = {psi:.6f}")
print(f"ψ̇ = {psi_dot:.3e} s⁻¹")
print(f"ψ̈ = {psi_ddot:.3e} s⁻²")
print(f"ψ̇̈ = {psi_dddot:.3e} s⁻³")
print(f"J_ψ = {J_psi:.3e} s⁻³")
print(f"J_Δ = {J_D:.3e} s⁻³")
print(f"J_total (incl. source) = {J_total:.3e} s⁻³")
print(f"Stability threshold Θ = {Theta:.3e} s⁻⁶")
print(f"Shredding LHS = {shredding_lhs:.6f}  (≟ 1)")
print(f"Freeze    LHS = {freeze_lhs:.6f}   (≟ 1)")
print(f"Threshold comparison: σ_J² (approx J_total²) = {J_total**2:.3e} s⁻⁶")
print(f"  → Unstable if σ_J² > Θ ? {J_total**2 > Theta}")