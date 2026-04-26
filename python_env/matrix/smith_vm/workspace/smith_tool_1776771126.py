# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith – Omega Protocol Validation Script
----------------------------------------------
This script checks the mathematical consistency of the invariant ψ
and the stability of the proposed shear‑flow control law
within the Omega Physics Rubric (v26.0 Strictor Gate).

Assumptions (consistent with the proposal):
    ξ = ξ0 * |S - S_crit|**(-nu)          (correlation length scaling)
    m_eff ∝ 1/ξ                           (mass–length duality near criticality)
    ψ_rubric = ln(m_eff / m0)            (Omega‑Rubric invariant)
    ψ_wrong  = ln(ξ / ξ0)                (as mistakenly used in the proposal)
    Control law:  dS/dt = -γ * sign(S-S_crit) * exp(-ψ/nu)
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
# ------------------------------------------------------------------
S, S_crit, nu, gamma, xi0, m0 = sp.symbols('S S_crit nu gamma xi0 m0', real=True, positive=True)
# distance from criticality
DeltaS = S - S_crit
sign_DS = sp.sign(DeltaS)          # +1 if S>S_crit, -1 if S<S_crit, 0 at criticality

# ------------------------------------------------------------------
# Scaling ansatz (universal critical scaling)
# ------------------------------------------------------------------
xi = xi0 * (sp.Abs(DeltaS))**(-nu)          # correlation length
# Effective mass inversely proportional to correlation length (up to const)
m_eff = 1 / xi                               # we absorb proportionality constants into m0 later

# ------------------------------------------------------------------
# Invariants
# ------------------------------------------------------------------
# Rubric‑required invariant: ψ = ln(m_eff / m0)
psi_rubric = sp.log(m_eff / m0)

# The mistaken invariant used in the proposal: ψ_wrong = ln(ξ / ξ0)
psi_wrong = sp.log(xi / xi0)

# ------------------------------------------------------------------
# Control law (as written in the proposal)
# ------------------------------------------------------------------
control_wrong = -gamma * sign_DS * sp.exp(-psi_wrong / nu)
control_rubric = -gamma * sign_DS * sp.exp(-psi_rubric / nu)

# ------------------------------------------------------------------
# Simplify using the scaling relations
# ------------------------------------------------------------------
# Since xi = xi0 * |ΔS|^{-nu}, we have log(xi/xi0) = -nu * log(|ΔS|)
log_abs_DS = sp.log(sp.Abs(DeltaS))
psi_wrong_simp = -nu * log_abs_DS
psi_rubric_simp = nu * log_abs_DS   # because m_eff ∝ 1/xi → ln(m_eff) = -ln(xi) + const

# Substitute simplified forms
control_wrong_simp = -gamma * sign_DS * sp.exp(-psi_wrong_simp / nu)
control_rubric_simp = -gamma * sign_DS * sp.exp(-psi_rubric_simp / nu)

# ------------------------------------------------------------------
# Analyze effect on |ΔS|
# ------------------------------------------------------------------
# d|ΔS|/dt = sign(ΔS) * dS/dt   (because d|x|/dt = sign(x) * dx/dt)
d_abs_DT_wrong = sign_DS * control_wrong_simp
d_abs_DT_rubric = sign_DS * control_rubric_simp

# Simplify further
d_abs_DT_wrong_simp = sp.simplify(d_abs_DT_wrong)
d_abs_DT_rubric_simp = sp.simplify(d_abs_DT_rubric)

# ------------------------------------------------------------------
# Output results
# ------------------------------------------------------------------
print("=== Invariant Check ===")
print("ψ_rubric (simplified) :", psi_rubric_simp)
print("ψ_wrong  (simplified) :", psi_wrong_simp)
print()
print("Are they opposite up to an additive constant?")
print("ψ_rubric + ψ_wrong =", sp.simplify(psi_rubric_simp + psi_wrong_simp))
print()
print("=== Control‑Law Effect on |S - S_crit| ===")
print("d|ΔS|/dt (using ψ_wrong) :", d_abs_DT_wrong_simp)
print("d|ΔS|/dt (using ψ_rubric):", d_abs_DT_rubric_simp)
print()
print("Interpretation:")
print("  * If d|ΔS|/dt > 0  →  distance to criticality INCREASES (stabilising).")
print("  * If d|ΔS|/dt < 0  →  distance DECREASES (destabilising).")
print()
# Sign analysis (assuming DeltaS ≠ 0)
print("Sign of d|ΔS|/dt for ψ_wrong :", sp.sign(d_abs_DT_wrong_simp).subs({DeltaS: 1}))  # S>S_crit case
print("Sign of d|ΔS|/dt for ψ_rubric:", sp.sign(d_abs_DT_rubric_simp).subs({DeltaS: 1}))
print()
print("=== Suggested Fix ===")
print("Replace the control law with:")
print("    dS/dt = +γ * sign(S - S_crit) * exp(-ψ/nu)   (using ψ = ψ_rubric)")
print("which yields d|ΔS|/dt = +γ/|S - S_crit| > 0  → stabilising.")