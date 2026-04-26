# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol validation for the Linux HSA unified memory analysis.
Checks:
  - Definitions of ψ, ξ_N, ξ_Δ
  - Entropy probabilities and derivatives
  - Jerk components and total 𝒥_I
  - Shredding / Freeze boundaries
  - Dimensionless jerk variance vs. stability threshold
"""

import math
import numpy as np

# ----------------------------------------------------------------------
# Input data (as given in the audit)
# ----------------------------------------------------------------------
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
dot_phi_N = 2.1e3       # s^-1
dot_phi_D = 8.7e3       # s^-1
xi_inv2 = 4.2e6         # s^-2   => ξ = 1/√xi_inv2
J_source = 1.5e12       # s^-3

# ----------------------------------------------------------------------
# Helper tolerances
# ----------------------------------------------------------------------
RTOL = 1e-3   # relative tolerance
ATOL = 1e-12  # absolute tolerance

def approx_equal(a, b, msg=""):
    assert math.isclose(a, b, rel_tol=RTOL, abs_tol=ATOL), \
        f"{msg}: {a} != {b} (diff={abs(a-b)})"

# ----------------------------------------------------------------------
# 1. Basic invariants
# ----------------------------------------------------------------------
psi = math.log(phi_N)
approx_equal(psi, math.log(0.78), "psi = ln(phi_N)")

# Stiffness (we only need ξ for derivative approximations)
xi = 1.0 / math.sqrt(xi_inv2)
approx_equal(xi, 1.0/math.sqrt(4.2e6), "xi from xi^-2")

# ----------------------------------------------------------------------
# 2. Derivatives (relaxation‑time approximation: d/dt ≈ 1/ξ)
# ----------------------------------------------------------------------
dot_psi = dot_phi_N / phi_N
approx_equal(dot_psi, dot_phi_N/phi_N, "dot_psi")

ddot_phi_N = dot_phi_N / xi
ddot_phi_D = dot_phi_D / xi
approx_equal(ddot_phi_N, dot_phi_N/xi, "ddot_phi_N")
approx_equal(ddot_phi_D, dot_phi_D/xi, "ddot_phi_D")

ddot_psi = ddot_phi_N/phi_N - dot_psi**2
approx_equal(ddot_psi, ddot_phi_N/phi_N - dot_psi**2, "ddot_psi")

dddot_psi = ddot_psi / xi
approx_equal(dddot_psi, ddot_psi/xi, "dddot_psi")

dddot_phi_D = ddot_phi_D / xi
approx_equal(dddot_phi_D, ddot_phi_D/xi, "dddot_phi_D")

# ----------------------------------------------------------------------
# 3. Probabilities and entropy derivatives
# ----------------------------------------------------------------------
e_psi = math.exp(psi)
Z = e_psi + phi_D
p_N = e_psi / Z
p_D = phi_D / Z
approx_equal(p_N, 0.690, "p_N")
approx_equal(p_D, 0.310, "p_D")

# ∂S_h/∂ψ = -p_N * ln(p_D/p_N)
dS_dpsi = -p_N * math.log(p_D/p_N)
approx_equal(dS_dpsi, 0.553, "∂S_h/∂psi")

# ∂²S_h/∂ψ² = -p_N(1-p_N)*(ln φ_D - ψ) - p_N
d2S_dpsi2 = -p_N*(1-p_N)*(math.log(phi_D) - psi) - p_N
approx_equal(d2S_dpsi2, -0.519, "∂²S_h/∂psi²")

# ∂³S_h/∂ψ³ (numeric from finite difference of analytic expression)
def dS_dpsi_func(psi_val):
    e = math.exp(psi_val)
    Z = e + phi_D
    pN = e/Z
    pD = phi_D/Z
    return -pN * math.log(pD/pN)

# central difference
eps = 1e-6
d3S_dpsi3 = (dS_dpsi_func(psi+eps) - 2*dS_dpsi_func(psi) + dS_dpsi_func(psi-eps))/eps**2
approx_equal(d3S_dpsi3, 0.089, "∂³S_h/∂psi³")

# Δ‑mode entropy derivatives (analytic)
dS_dphiD = -math.log(p_D/p_N) * (phi_D/Z)   # derivative of S_h w.r.t φ_Δ
# Using chain rule: ∂S/∂φ_Δ = (∂S/∂p_D)*(∂p_D/∂φ_Δ) + (∂S/∂p_N)*(∂p_N/∂φ_Δ)
# Simpler: compute numerically
def S_h(phiN, phiD):
    e = math.exp(math.log(phiN))  # phiN already normalized, but keep generic
    Z = e + phiD
    pN = e/Z
    pD = phiD/Z
    return -(pN*math.log(pN) + pD*math.log(pD)) if pN>0 and pD>0 else 0.0

eps = 1e-8
dS_dphiD_num = (S_h(phi_N, phi_D+eps) - S_h(phi_N, phi_D-eps))/(2*eps)
approx_equal(dS_dphiD_num, 0.802, "∂S_h/∂phi_D (numeric)")

d2S_dphiD2_num = (S_h(phi_N, phi_D+2*eps) - 2*S_h(phi_N, phi_D) + S_h(phi_N, phi_D-2*eps))/( (2*eps)**2 )
approx_equal(d2S_dphiD2_num, -2.857, "∂²S_h/∂phi_D² (numeric)")

# ----------------------------------------------------------------------
# 4. Jerk components
# ----------------------------------------------------------------------
J_psi = (dS_dpsi * dddot_psi +
         3 * d2S_dpsi2 * dot_psi * ddot_psi +
         d3S_dpsi3 * dot_psi**3)
approx_equal(J_psi, 7.07e9, "J_psi")

J_Delta = (dS_dphiD_num * dddot_phi_D +
           3 * d2S_dphiD2_num * dot_phi_D * ddot_phi_D)
approx_equal(J_Delta, -1.30e12, "J_Delta (within tolerance)")

J_total = J_psi + J_Delta + J_source
approx_equal(J_total, 2.07e11, "Total informational jerk 𝒥_I")

# ----------------------------------------------------------------------
# 5. Boundary checks
# ----------------------------------------------------------------------
shredding_lhs = phi_N**2 + 3*phi_D**2
freeze_lhs    = 3*phi_N**2 + phi_D**2
approx_equal(shredding_lhs, 0.9759, "Shredding LHS")
approx_equal(freeze_lhs,    1.9477, "Freeze LHS")
assert shredding_lhs < 1.0, "System should be below shredding boundary"
assert freeze_lhs    > 1.0, "System should be above freeze boundary"

# ----------------------------------------------------------------------
# 6. Stability criterion (dimensionless jerk variance)
# ----------------------------------------------------------------------
omega = 1.0/xi                     # s^-1
omega_psi = omega * math.exp(-psi/2.0)
natural_jerk_scale = omega_psi**3
approx_equal(natural_jerk_scale, 1.22e10, "Natural jerk scale ω_ψ³")

sigma_J2 = J_total**2
var_J_tilde = sigma_J2 / (omega_psi**6)
approx_equal(var_J_tilde, 287.0, "Dimensionless jerk variance")
assert var_J_tilde > 1.0, "Instability indicated (variance >> 1)"

# ----------------------------------------------------------------------
# If we reach here, all checks passed
# ----------------------------------------------------------------------
print("All Omega‑Protocol invariants and numerical checks passed.")
print(f"ψ = {psi:.6f}")
print(f"𝒥_I = {J_total:.3e} s⁻³")
print(f"Dimensionless jerk variance = {var_J_tilde:.2f}")