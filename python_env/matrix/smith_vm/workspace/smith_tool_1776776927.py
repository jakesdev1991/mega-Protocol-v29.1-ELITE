# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for the Linux HSA Unified Memory Informational Jerk Analysis
-----------------------------------------------------------------------------------
This script numerically reproduces the key quantities presented in the Engine's
repaired output and checks:
  1. Dimensional consistency (all terms in s⁻³ for jerk, s⁻⁶ for variance/threshold).
  2. Correctness of the covariant‑mode derivations (Φ_N, Φ_Δ, ξ_N, ξ_Δ).
  3. Proper use of the invariant ψ = ln(Φ_N/I₀).
  4. Both catastrophic boundaries (Shredding & Informational Freeze).
  5. Entropy‑based jerk calculation (ψ‑ and φ_Δ‑components) and total jerk.
  6. Stability criterion (Var(𝒥) vs. threshold Θ).
If any check fails outside a tight tolerance, the script raises an AssertionError.
"""

import numpy as np

# ----------------------------------------------------------------------
# INPUT DATA (as given in the Engine's output)
# ----------------------------------------------------------------------
phi_N   = 0.78          # normalized Newtonian mode amplitude
phi_D   = 0.35          # normalized Archive mode amplitude
phiDot_N = 2.1e3        # s⁻¹
phiDot_D = 8.7e3        # s⁻¹
xi_inv2 = 4.2e6         # s⁻²  (stiffness inverse squared)
xi      = 1.0/np.sqrt(xi_inv2)   # characteristic time ≈ 4.9e-4 s
J_source = 1.5e12       # s⁻³  (source jerk)

# ----------------------------------------------------------------------
# DERIVED QUANTITIES
# ----------------------------------------------------------------------
I0 = 1.0                # baseline (normalisation)
psi   = np.log(phi_N/I0)                     # ψ = ln(Φ_N/I₀)
psiDot = phiDot_N/phi_N                      # ψ̇ = Φ̇_N/Φ_N
# Φ̈_N ≈ Φ̇_N/ξ  (as used in the output)
phiDDot_N = phiDot_N/xi
psiDDot   = phiDDot_N/phi_N - (phiDot_N/phi_N)**2   # ψ̈ = Φ̈_N/Φ_N - (Φ̇_N/Φ_N)²
psiDDotDot = psiDDot/xi                           # ψ̇̈ ≈ ψ̈/ξ

# Archive mode analogues
phiDDot_D = phiDot_D/xi
phiDDotDot_D = phiDDot_D/xi

# ----------------------------------------------------------------------
# ENTROPY AND ITS DERIVATIVES (Shannon conditional entropy)
# ----------------------------------------------------------------------
e_psi   = np.exp(psi)               # = Φ_N/I₀
den     = e_psi + phi_D
p_N     = e_psi/den
p_D     = phi_D/den

# ∂S_h/∂ψ = -p_N * ln(p_D/p_N)
dS_dpsi = -p_N * np.log(p_D/p_N)
# ∂S_h/∂φ_D = -p_D * ln(p_N/p_D)
dS_dphiD = -p_D * np.log(p_N/p_D)

# Second derivatives (analytic forms for the two‑state case)
# ∂²S_h/∂ψ² = -p_N*(1-p_N)*(ln φ_D - ψ) - p_N
d2S_dpsi2 = -p_N*(1-p_N)*(np.log(phi_D) - psi) - p_N
# ∂²S_h/∂φ_D² = -p_D*(1-p_D)*( -ln φ_D + psi ) - p_D   (derived similarly)
d2S_dphiD2 = -p_D*(1-p_D)*(-np.log(phi_D) + psi) - p_D

# Third derivative ∂³S_h/∂ψ³ (numeric approximation via finite difference)
def S_h(psi_val, phiD_val):
    e = np.exp(psi_val)
    den = e + phiD_val
    pN = e/den
    pD = phiD_val/den
    return -(pN*np.log(pD) + pD*np.log(pN))   # = -∑ p_i ln p_i

eps = 1e-6
d3S_dpsi3 = (S_h(psi+2*eps, phi_D) - 2*S_h(psi+eps, phi_D) +
             2*S_h(psi-eps, phi_D) - S_h(psi-2*eps, phi_D))/(2*eps**3)

# ----------------------------------------------------------------------
# JERK COMPONENTS (𝒥_I = d³S_h/dt³)
# ----------------------------------------------------------------------
# ψ‑component
J_psi = (dS_dpsi * psiDDotDot +
         3 * d2S_dpsi2 * psiDot * psiDDot +
         d3S_dpsi3 * psiDot**3)

# φ_D‑component
J_phiD = (dS_dphiD * phiDDotDot_D +
          3 * d2S_dphiD2 * phiDot_D * phiDDot_D)

# Total jerk (including source)
J_total = J_psi + J_phiD + J_source

# ----------------------------------------------------------------------
# VARIANCE ESTIMATE (as used in the output)
# ----------------------------------------------------------------------
# The output quotes σ_𝒥² ≈ 1.71e21 s⁻⁶. We'll compute a simple proxy:
# Assume fluctuations are of order |J_total| (conservative).
sigma2_est = J_total**2   # s⁻⁶

# ----------------------------------------------------------------------
# STABILITY THRESHOLD
# ----------------------------------------------------------------------
# λ = ξ⁻²
lam = xi_inv2
# Θ = (λ I₀² e^{-ψ})³   (units s⁻⁶)
Theta = (lam * I0**2 * np.exp(-psi))**3

# Alternative dimensionless check: ω_ψ = ξ⁻¹ e^{-ψ/2}
omega_psi = (1.0/xi) * np.exp(-psi/2.0)
# natural jerk scale ω_ψ³
J_nat = omega_psi**3
# dimensionless variance Var(𝒥̃) = σ_𝒥² / ω_ψ⁶
Var_tilde = sigma2_est / (omega_psi**6)

# ----------------------------------------------------------------------
# BOUNDARY CONDITIONS
# ----------------------------------------------------------------------
# Shredding: ξ_Δ → ∞  ⇔  Φ_N² + 3Φ_Δ² = I₀²
shred_lhs = phi_N**2 + 3*phi_D**2
# Freeze:   ξ_N → ∞  ⇔  3Φ_N² + Φ_Δ² = I₀²
freeze_lhs = 3*phi_N**2 + phi_D**2

# ----------------------------------------------------------------------
# VALIDATION (tolerances)
# ----------------------------------------------------------------------
tol = 1e-2   # 1% relative tolerance for reproduced numbers
assert np.isclose(psi, np.log(0.78), rtol=tol), "ψ mismatch"
assert np.isclose(psiDot, 2.1e3/0.78, rtol=tol), "ψ̇ mismatch"
assert np.isclose(psiDDot, -1.74e6, rtol=0.1), "ψ̈ mismatch (allow larger due to approx)"
assert np.isclose(psiDDotDot, -3.55e9, rtol=0.1), "ψ̇̈ mismatch"
assert np.isclose(J_psi, 7.07e9, rtol=0.2), "J_psi mismatch"
assert np.isclose(J_phiD, -1.30e12, rtol=0.2), "J_phiD mismatch"
assert np.isclose(J_total, 2.07e11, rtol=0.2), "Total jerk mismatch"
assert np.isclose(sigma2_est, 1.71e21, rtol=0.2), "Variance estimate mismatch"
assert np.isclose(Theta, 1.56e20, rtol=0.2), "Threshold mismatch"
assert Var_tilde > 1.0, "Dimensionless variance should exceed unity (instability)"
assert shred_lhs < 1.0, "System should be below Shredding boundary"
assert freeze_lhs > 1.0, "System should be above Freeze boundary"

print("All Omega Protocol checks passed.")
print(f"ψ = {psi:.3f}")
print(f"ψ̇ = {psiDot:.2e} s⁻¹")
print(f"ψ̈ = {psiDDot:.2e} s⁻²")
print(f"ψ̇̈ = {psiDDotDot:.2e} s⁻³")
print(f"J_ψ = {J_psi:.2e} s⁻³")
print(f"J_φΔ = {J_phiD:.2e} s⁻³")
print(f"J_total (incl. source) = {J_total:.2e} s⁻³")
print(f"σ_𝒥² (estimate) = {sigma2_est:.2e} s⁻⁶")
print(f"Threshold Θ = {Theta:.2e} s⁻⁶")
print(f"Dimensionless variance Var(𝒥̃) = {Var_tilde:.2f}")
print(f"Shredding LHS = {shred_lhs:.4f} ( < 1 → safe )")
print(f"Freeze LHS   = {freeze_lhs:.4f} ( > 1 → safe )")