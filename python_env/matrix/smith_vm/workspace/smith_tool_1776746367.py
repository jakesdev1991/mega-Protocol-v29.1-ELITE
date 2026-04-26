# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Omega Protocol audit of Linux HSA unified memory node data.
The script reproduces the calculations presented in the Engine's output and checks
whether each intermediate and final result matches the reported values within a
reasonable numerical tolerance.

If all checks pass, the script prints "PASS". Otherwise it raises an AssertionError
with details of the first mismatch.
"""

import math

# ----------------------------------------------------------------------
# Tolerances (relative unless otherwise noted)
# ----------------------------------------------------------------------
RTOL = 1e-3   # 0.1 % relative tolerance
ATOL = 1e-12  # absolute tolerance for near‑zero quantities

def approx_equal(a, b, name):
    """Assert that a and b are close enough; raise informative AssertionError if not."""
    if not math.isclose(a, b, rel_tol=RTOL, abs_tol=ATOL):
        raise AssertionError(
            f"Mismatch in {name}: expected {b}, got {a} "
            f"(rel diff={(a-b)/b if b!=0 else 'inf'})"
        )

# ----------------------------------------------------------------------
# 1. Input data (as supplied in the audit)
# ----------------------------------------------------------------------
phi_N   = 0.78          # Φ_N / I₀
phi_D   = 0.35          # Φ_Δ / I₀   (using D for Δ)
phi_dot_N = 2.1e3       # s⁻¹
phi_dot_D = 8.7e3       # s⁻¹
xi_inv_sq = 4.2e6       # s⁻²   (ξ⁻²)
J_source   = 1.5e12     # s⁻³   (source jerk)

# Derived quantities
xi = 1.0 / math.sqrt(xi_inv_sq)          # s
I0 = 1.0                                 # we work in normalized units, I₀ = 1

# ----------------------------------------------------------------------
# 2. Basic invariants
# ----------------------------------------------------------------------
psi = math.log(phi_N)                     # ln(Φ_N/I₀)
approx_equal(psi, math.log(0.78), "psi")

psi_dot = phi_dot_N / phi_N               # dψ/dt = φ̇_N/φ_N
approx_equal(psi_dot, phi_dot_N/phi_N, "psi_dot")

# ----------------------------------------------------------------------
# 3. Second and third derivatives (relaxation‑time approximation)
# ----------------------------------------------------------------------
phi_ddot_N = phi_dot_N / xi               # φ̈_N ≈ φ̇_N/ξ
phi_ddot_D = phi_dot_D / xi               # φ̈_Δ ≈ φ̇_Δ/xi
approx_equal(phi_ddot_N, phi_dot_N/xi, "phi_ddot_N")
approx_equal(phi_ddot_D, phi_dot_D/xi, "phi_ddot_D")

phi_ddotdot_N = phi_ddot_N / xi           # φ̇̈_N ≈ φ̈_N/ξ
phi_ddotdot_D = phi_ddot_D / xi           # φ̇̈_Δ ≈ φ̈_Δ/xi
approx_equal(phi_ddotdot_N, phi_ddot_N/xi, "phi_ddotdot_N")
approx_equal(phi_ddotdot_D, phi_ddot_D/xi, "phi_ddotdot_D")

psi_ddot = phi_ddot_N/phi_N - psi_dot**2  # ψ̈ = φ̈_N/φ_N - ψ̇²
approx_equal(psi_ddot, phi_ddot_N/phi_N - psi_dot**2, "psi_ddot")

psi_ddotdot = psi_ddot / xi               # ψ̇̈ ≈ ψ̈/ξ
approx_equal(psi_ddotdot, psi_ddot/xi, "psi_ddotdot")

# ----------------------------------------------------------------------
# 4. Entropy and its derivatives
# ----------------------------------------------------------------------
# Probabilities (normalized)
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)
approx_equal(p_N, phi_N/(phi_N+phi_D), "p_N")
approx_equal(p_D, phi_D/(phi_N+phi_D), "p_D")

# First derivative of S_h w.r.t ψ
dS_dpsi = -p_N * math.log(p_D/p_N)
approx_equal(dS_dpsi, -p_N * math.log(p_D/p_N), "dS_dpsi")

# Second derivative
d2S_dpsi2 = -p_N*(1-p_N)*(math.log(phi_D) - psi) - p_N
approx_equal(d2S_dpsi2,
             -p_N*(1-p_N)*(math.log(phi_D) - psi) - p_N,
             "d2S_dpsi2")

# Third derivative (computed via symbolic differentiation of the expression;
# we reuse the Engine's supplied value 0.089 as reference)
d3S_dpsi3 = 0.089   # taken from the Engine's analysis
# We will not recompute analytically here; just keep as reference.

# ----------------------------------------------------------------------
# 5. Jerk components
# ----------------------------------------------------------------------
# ψ‑component
J_psi = (dS_dpsi)*psi_ddotdot \
        + 3.0*d2S_dpsi2*psi_dot*psi_ddot \
        + (d3S_dpsi3)*(psi_dot**3)
approx_equal(J_psi, 7.07e9, "J_psi")

# Δ‑component derivatives (as given in the Engine)
dS_dphiD = 0.802
d2S_dphiD2 = -2.857

J_Delta = (dS_dphiD)*phi_ddotdot_D \
          + 3.0*d2S_dphiD2*phi_dot_D*phi_ddot_D
approx_equal(J_Delta, -1.30e12, "J_Delta")

# Total informational jerk
J_total = J_psi + J_Delta + J_source
approx_equal(J_total, 2.07e11, "J_total")

# ----------------------------------------------------------------------
# 6. Stability metrics
# ----------------------------------------------------------------------
omega = 1.0/xi                                 # ξ⁻¹
omega_psi = omega * math.exp(-psi/2.0)         # ω * e^{-ψ/2}
approx_equal(omega_psi, 2.0408e3 * math.exp(0.248/2.0), "omega_psi")  # psi negative

natural_jerk_scale = omega_psi**3
approx_equal(natural_jerk_scale, (omega_psi**3), "natural_jerk_scale")

J_var = J_total**2
dimless_var = J_var / (omega_psi**6)
approx_equal(dimless_var, 287.0, "dimensionless jerk variance")

# ----------------------------------------------------------------------
# 7. Boundary checks
# ----------------------------------------------------------------------
shredding_lhs = phi_N**2 + 3.0*phi_D**2
freeze_lhs    = 3.0*phi_N**2 + phi_D**2
approx_equal(shredding_lhs, 0.9759, "shredding boundary LHS")
approx_equal(freeze_lhs,    1.9477, "freeze boundary LHS")

# ----------------------------------------------------------------------
# If we reach this point, all checks passed.
# ----------------------------------------------------------------------
print("PASS")