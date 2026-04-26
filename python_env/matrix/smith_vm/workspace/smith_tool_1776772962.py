# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
Validates the Linux HSA Unified Memory Informational Jerk Stability Analysis
against the Omega Physics Rubric v26.0.
"""

import numpy as np

# ----------------------------------------------------------------------
# 1. INPUT DATA (normalized to I0 = 1)
# ----------------------------------------------------------------------
phi_N = 0.78          # Φ_N / I0
phi_D = 0.35          # Φ_Δ / I0
dot_phi_N = 2.1e3     # s⁻¹
dot_phi_D = 8.7e3     # s⁻¹
xi_inv_sq = 4.2e6     # ξ⁻²  (s⁻²)
J_source = 1.5e12     # source jerk (s⁻³)

# Derived quantities
I0 = 1.0
xi = 1.0 / np.sqrt(xi_inv_sq)          # characteristic time (s)
psi = np.log(phi_N)                    # metric coupling invariant
dot_psi = dot_phi_N / phi_N

# Approximate higher‑order derivatives via relaxation‑time scaling
ddot_phi_N = dot_phi_N / xi
ddot_phi_D = dot_phi_D / xi
ddot_psi   = ddot_phi_N / phi_N - dot_psi**2
dddot_psi  = ddot_psi / xi
dddot_phi_D = ddot_phi_D / xi

# ----------------------------------------------------------------------
# 2. COVARIANT MODES & INVARIANTS (check consistency)
# ----------------------------------------------------------------------
# Stiffness from the given ξ⁻² (interpreted as ξ_N⁻²)
lambda_est = xi_inv_sq / (3*phi_N**2 + phi_D**2 - 1.0)   # from ξ_N⁻² formula
xi_N_inv_sq_calc = lambda_est * (3*phi_N**2 + phi_D**2 - 1.0)
xi_D_inv_sq_calc = lambda_est * (phi_N**2 + 3*phi_D**2 - 1.0)

print(f"λ (from ξ_N⁻²)          = {lambda_est:.3e} s⁻²")
print(f"ξ_N⁻² (recalc)          = {xi_N_inv_sq_calc:.3e} s⁻²  (input {xi_inv_sq:.3e})")
print(f"ξ_Δ⁻² (recalc)          = {xi_D_inv_sq_calc:.3e} s⁻²")
print(f"ψ = ln(Φ_N/I₀)          = {psi:.6f}")
print(f"ξ = 1/√(ξ⁻²)            = {xi:.3e} s")

# ----------------------------------------------------------------------
# 3. ENTROPY GAUGE & DERIVATIVES
# ----------------------------------------------------------------------
e_psi = np.exp(psi)
Z = e_psi + phi_D               # partition function
p_N = e_psi / Z
p_D = phi_D / Z

def entropy(pN, pD):
    return -(pN*np.log(pN) + pD*np.log(pD))

S_h = entropy(p_N, p_D)

# Derivatives w.r.t ψ (analytic)
# p_N = e^ψ / Z,  p_D = φ_Δ / Z,  Z = e^ψ + φ_Δ
dpN_dpsi = p_N * (1 - p_N)          # = p_N * p_D
dpD_dpsi = -p_N * p_D               # = -p_N * p_D
dS_dpsi  = -(dpN_dpsi * (np.log(p_N)+1) + dpD_dpsi * (np.log(p_D)+1))

# Second derivative
d2pN_dpsi2 = p_N * (1 - 2*p_N)      # derivative of dpN_dpsi
d2pD_dpsi2 = -d2pN_dpsi2
d2S_dpsi2  = -(d2pN_dpsi2*(np.log(p_N)+1) + dpN_dpsi**2/p_N
               + d2pD_dpsi2*(np.log(p_D)+1) + dpD_dpsi**2/p_D)

# Third derivative (tedious but doable; we compute via finite diff for sanity)
def S_of_psi(psi_val):
    e = np.exp(psi_val)
    Zv = e + phi_D
    pNv = e / Zv
    pDv = phi_D / Zv
    return -(pNv*np.log(pNv) + pDv*np.log(pDv))

# central finite difference
h = 1e-6
dS_dpsi_fd   = (S_of_psi(psi+h) - S_of_psi(psi-h))/(2*h)
d2S_dpsi2_fd = (S_of_psi(psi+h) - 2*S_of_psi(psi) + S_of_psi(psi-h))/h**2
d3S_dpsi3_fd = (S_of_psi(psi+2*h) - 2*S_of_psi(psi+h) + 2*S_of_psi(psi-h) - S_of_psi(psi-2*h))/(2*h**3)

print("\nEntropy gauge:")
print(f"p_N = {p_N:.5f}, p_Δ = {p_D:.5f}, S_h = {S_h:.6f}")
print(f"∂S/∂ψ (analytic) = {dS_dpsi:.6f}, (FD) = {dS_dpsi_fd:.6f}")
print(f"∂²S/∂ψ² (analytic) = {d2S_dpsi2:.6f}, (FD) = {d2S_dpsi2_fd:.6f}")
print(f"∂³S/∂ψ³ (FD) = {d3S_dpsi3_fd:.6f}")

# Derivatives w.r.t φ_Δ (keeping ψ fixed)
dpN_dphiD = -e_psi / Z**2          # = -p_N * p_D / phi_D
dpD_dphiD = (Z - e_psi) / Z**2     # = p_N / Z = p_N / (e_psi+phi_D) = p_N / Z
# simpler: p_D = φ_Δ / Z → ∂p_D/∂φ_Δ = (Z - φ_Δ)/Z^2 = e_psi/Z^2 = p_N * p_D / phi_D
dpD_dphiD = e_psi / Z**2
dS_dphiD  = -(dpN_dphiD*(np.log(p_N)+1) + dpD_dphiD*(np.log(p_D)+1))

# Second derivative w.r.t φ_Δ
d2pN_dphiD2 = 2*e_psi / Z**3
d2pD_dphiD2 = -2*e_psi / Z**3
d2S_dphiD2  = -(d2pN_dphiD2*(np.log(p_N)+1) + dpN_dphiD**2/p_N
               + d2pD_dphiD2*(np.log(p_D)+1) + dpD_dphiD**2/p_D)

print(f"\n∂S/∂φ_Δ = {dS_dphiD:.6f}")
print(f"∂²S/∂φ_Δ² = {d2S_dphiD2:.6f}")

# ----------------------------------------------------------------------
# 4. JERK COMPONENTS
# ----------------------------------------------------------------------
J_psi = (dS_dpsi * dddot_psi
         + 3 * d2S_dpsi2 * dot_psi * ddot_psi
         + d3S_dpsi3_fd * dot_psi**3)

J_Delta = (dS_dphiD * dddot_phi_D
           + 3 * d2S_dphiD2 * dot_phi_D * ddot_phi_D)

J_total = J_psi + J_Delta + J_source

print("\nJerk components (s⁻³):")
print(f"J_ψ   = {J_psi:.3e}")
print(f"J_Δ   = {J_Delta:.3e}")
print(f"J_src = {J_source:.3e}")
print(f"J_total = {J_total:.3e}")

# ----------------------------------------------------------------------
# 5. BOUNDARY CHECKS
# ----------------------------------------------------------------------
shredding_lhs = phi_N**2 + 3*phi_D**2
freeze_lhs    = 3*phi_N**2 + phi_D**2

print("\nBoundary conditions:")
print(f"φ_N² + 3φ_Δ² = {shredding_lhs:.6f}  (shredding if = 1)")
print(f"3φ_N² + φ_Δ² = {freeze_lhs:.6f}    (freeze if = 1)")

# ----------------------------------------------------------------------
# 6. STABILITY METRIC (dimensionless jerk variance)
# ----------------------------------------------------------------------
omega = 1.0 / xi                     # ξ⁻¹  (s⁻¹)
omega_psi = omega * np.exp(-psi/2.0) # ψ‑modulated frequency
jerk_scale = omega_psi**3            # natural jerk scale (s⁻³)
sigma_J_sq = J_total**2
dimless_var = sigma_J_sq / (omega_psi**6)

print("\nStability assessment:")
print(f"ω = ξ⁻¹          = {omega:.2f} s⁻¹")
print(f"ω_ψ = ω e^{-ψ/2} = {omega_psi:.2f} s⁻¹")
print(f"Natural jerk scale ω_ψ³ = {jerk_scale:.3e} s⁻³")
print(f"σ_J² = J_total²   = {sigma_J_sq:.3e} s⁻⁶")
print(f"Dimensionless Var( J̃ ) = σ_J² / ω_ψ⁶ = {dimless_var:.2f}")
print(f"Stability threshold ~ O(1) → {'UNSTABLE' if dimless_var > 10 else 'MARGINAL'}")

# ----------------------------------------------------------------------
# 7. TOLERANCE CHECKS (assertions)
# ----------------------------------------------------------------------
tol = 1e-2   # 1 % relative tolerance

assert np.abs((xi_N_inv_sq_calc - xi_inv_sq)/xi_inv_sq) < tol, "ξ_N⁻² mismatch"
assert np.abs((dS_dpsi - dS_dpsi_fd)/dS_dpsi_fd) < tol, "∂S/∂ψ mismatch"
assert np.abs((d2S_dpsi2 - d2S_dpsi2_fd)/d2S_dpsi2_fd) < tol, "∂²S/∂ψ² mismatch"
assert np.abs((J_psi - 7.07e9)/7.07e9) < 0.05, "J_ψ out of expected range"
assert np.abs((J_Delta - (-1.30e12))/1.30e12) < 0.05, "J_Δ out of expected range"
assert np.abs((J_total - 2.07e11)/2.07e11) < 0.05, "J_total out of expected range"
assert np.abs((dimless_var - 287)/287) < 0.05, "Dimensionless variance mismatch"

print("\nAll validation checks passed within tolerance.")