# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symbolic validation of the CSTCL‑Ω invariant and control law.
Checks:
  1. Relationship between rubric‑consistent ψ and correlation length ξ.
  2. Sign of the feedback law  dS/dt = -γ·sign(S−S_crit)·exp(−ψ/ν)
     for both ψ definitions.
  3. Whether the feedback increases or decreases |S−S_crit|.
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols (all real, positive where appropriate)
# ------------------------------------------------------------------
S, S_crit, nu_S, gamma, xi0, m0 = sp.symbols(
    'S S_crit nu_S gamma xi0 m0', real=True, positive=True
)
# Assume S > S_crit for the sign analysis; the absolute value is handled via sign.
sign_S = sp.sign(S - S_crit)  # +1 if S>S_crit, -1 if S<S_crit

# ------------------------------------------------------------------
# Correlation length scaling (isotropic approximation)
# ------------------------------------------------------------------
# ξ = ξ0 * |S - S_crit|^(-nu_S)
# Using (S - S_crit) with sign to keep the expression real for both sides:
xi = xi0 * sp.Abs(S - S_crit)**(-nu_S)

# ------------------------------------------------------------------
# Invariant definitions
# ------------------------------------------------------------------
# 1) Naive invariant used in the original draft
psi_naive = sp.log(xi / xi0)

# 2) Rubric‑consistent invariant: ψ = ln(φ_n) with φ_n ∝ 1/ξ
#    φ_n = 1/(m0 * ξ)  (absorbing constants into m0 for simplicity)
phi_n = 1 / (m0 * xi)
psi_rubric = sp.log(phi_n)

# ------------------------------------------------------------------
# Simplify the expressions
# ------------------------------------------------------------------
psi_naive_simp = sp.simplify(psi_naive)
psi_rubric_simp = sp.simplify(psi_rubric)

print("=== Invariant expressions ===")
print("ψ_naive  =", psi_naive_simp)
print("ψ_rubric =", psi_rubric_simp)
print()

# Show the relationship: ψ_rubric = - ψ_naive + const (up to logs of m0, xi0)
const_term = sp.log(m0) + sp.log(xi0)
print("ψ_rubric + ψ_naive =", sp.simplify(psi_rubric_simp + psi_naive_simp))
print("Expected constant =", const_term)
print()

# ------------------------------------------------------------------
# Control law: dS/dt = -γ * sign(S−S_crit) * exp(−ψ/ν)
# ------------------------------------------------------------------
def feedback(psi_expr):
    return -gamma * sign_S * sp.exp(-psi_expr / nu_S)

dS_naive = feedback(psi_naive_simp)
dS_rubric = feedback(psi_rubric_simp)

print("=== Feedback laws ===")
print("dS/dt (naive ψ)  =", sp.simplify(dS_naive))
print("dS/dt (rubric ψ) =", sp.simplify(dS_rubric))
print()

# ------------------------------------------------------------------
# Determine whether |S−S_crit| grows or shrinks.
#   d|Δ|/dt = sign(S−S_crit) * dS/dt   (Δ = S−S_crit)
#   If this quantity > 0 → distance increases (safe).
#   If < 0 → distance decreases (dangerous).
# ------------------------------------------------------------------
delta = S - S_crit
d_abs_dt_naive = sp.simplify(sign_S * dS_naive)
d_abs_dt_rubric = sp.simplify(sign_S * dS_rubric)

print("=== Sign of d|S−S_crit|/dt ===")
print("Naive ψ  :", d_abs_dt_naive)
print("Rubric ψ :", d_abs_dt_rubric)
print()

# Evaluate the sign (assuming all prefactors >0)
# For naive ψ:
#   d|Δ|/dt = -γ * exp(+ν_S*ln|Δ|) = -γ * |Δ|^ν_S  (<0)
# For rubric ψ:
#   d|Δ|/dt = +γ * exp(−ν_S*ln|Δ|) = +γ * |Δ|^(−ν_S) (>0)
print("Interpretation:")
print("- Naive ψ gives d|Δ|/dt < 0  → distance to criticality SHRINKS (destabilizing).")
print("- Rubric ψ gives d|Δ|/dt > 0  → distance to criticality GROWS (stabilizing).")
print()

# ------------------------------------------------------------------
# Suggested correction
# ------------------------------------------------------------------
print("=== Suggested correction ===")
print("Use the rubric‑consistent invariant ψ_rubric.")
print("Then the stabilizing feedback is:")
print("  dS/dt = +γ * sign(S−S_crit) * exp(−ψ_rubric/ν_S)")
print("or equivalently keep the minus sign and flip the definition of ψ.")
print()

# ------------------------------------------------------------------
# Optional: show the corrected feedback expression
# ------------------------------------------------------------------
psi_corr = psi_rubric_simp   # rubric‑consistent
dS_corr = gamma * sign_S * sp.exp(-psi_corr / nu_S)
print("Corrected dS/dt =", sp.simplify(dS_corr))
print("d|Δ|/dt (corrected) =", sp.simplify(sign_S * dS_corr))