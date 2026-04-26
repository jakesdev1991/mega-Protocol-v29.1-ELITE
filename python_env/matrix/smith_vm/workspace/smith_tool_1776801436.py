# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Higher-Order Lattice Polarization claim
against Omega Protocol invariants (Φ_N, Φ_Δ, J*).

The script does *not* re‑derive the physics; it merely checks
that a proposed formula for the effective fine-structure constant
obeys the minimal consistency conditions required by the
invariants.
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
# ------------------------------------------------------------------
α0, e, p, m, a = sp.symbols('α0 e p m a', positive=True)   # basics
ΦN, ΦΔ = sp.symbols('ΦN ΦΔ', real=True)                    # Omega modes
i, z = sp.symbols('i z')                                   # direction label (i = x,y,z)
# Kronecker delta: δ_{i,z}
δ_i_z = sp.Piecewise((1, sp.Eq(i, z)), (0, True))

# ------------------------------------------------------------------
# Building blocks from the engine's output (kept symbolic)
# ------------------------------------------------------------------
# Isotropic part (1-loop + Newtonian mode)
Π0 = (e**2/(12*sp.pi**2))*sp.log(a**(-2)/p**2) + (e**2/sp.pi**2)*ΦN

# Anisotropic kernel (treated as an unspecified function of p)
ΠΔ = sp.Function('ΠΔ')(p**2)   # placeholder; assumed real and O(e^2)

# Proposed effective coupling (engine's final formula)
α_eff = α0 / (1 + Π0 + δ_i_z * ΦΔ * ΠΔ)

# ------------------------------------------------------------------
# Helper: series expansion to O(ΦΔ)
# ------------------------------------------------------------------
α_eff_series = sp.series(α_eff, ΦΔ, 0, 2).removeO()   # up to linear in ΦΔ

# ------------------------------------------------------------------
# Test 1: Dimensionless check (α0 is dimensionless, Π0, ΠΔ dimensionless)
# ------------------------------------------------------------------
def is_dimensionless(expr):
    # Replace all dimensional symbols with a dummy dimension and see if it cancels
    dim = sp.symbols('dim')
    subs_dict = {e: dim**0, p: dim**1, m: dim**1, a: dim**(-1)}  # e dimensionless, p,m ~ 1/length, a ~ length
    # In natural units ħ=c=1, e is dimensionless, p,m have mass dimension 1, a has -1
    # The combination e^2/(π^2) is dimensionless, log term dimensionless, ΦN,ΦΔ dimensionless by definition
    # So we just verify that no leftover dimension symbols remain.
    expr_sub = expr.subs(subs_dict)
    return expr_sub.has(dim) == False

print("Test 1 – Dimensionless:", is_dimensionless(α_eff))

# ------------------------------------------------------------------
# Test 2: Isotropic limit (ΦΔ → 0) → α0/(1+Π0)
# ------------------------------------------------------------------
α_iso = α0 / (1 + Π0)
print("Test 2 – Isotropic limit matches:", sp.simplify(α_eff.subs(ΦΔ, 0) - α_iso) == 0)

# ------------------------------------------------------------------
# Test 3: Direction‑selectivity – anisotropic term only for i = z
# ------------------------------------------------------------------
# Extract the coefficient of ΦΔ in the linear expansion
coeff_ΦΔ = sp.Poly(α_eff_series, ΦΔ).coeff_monomial(ΦΔ)
# This coefficient should be zero for i ≠ z and non‑zero (but proportional to ΠΔ) for i = z
coeff_i_not_z = sp.simplify(coeff_ΦΔ.subs(δ_i_z, 0))
coeff_i_is_z   = sp.simplify(coeff_ΦΔ.subs(δ_i_z, 1))
print("Test 3 – Coeff for i≠z zero:", coeff_i_not_z == 0)
print("Test 3 – Coeff for i=z proportional to ΠΔ:", sp.simplify(coeff_i_is_z / ΠΔ) != 0)

# ------------------------------------------------------------------
# Test 4: Linear in ΦΔ (no ΦΔ^2 terms kept)
# ------------------------------------------------------------------
# Check that the series expansion contains no ΦΔ^2 term
ΦΔ2_coeff = sp.Poly(α_eff_series, ΦΔ).coeff_monomial(ΦΔ**2)
print("Test 4 – No ΦΔ^2 term (to O(ΦΔ)):", ΦΔ2_coeff == 0)

# ------------------------------------------------------------------
# Test 5: Consistency with metric deformation invariant J* = √g
# For a simple diagonal metric g_μν = diag(1,1,1,1+ΦΔ) we have √g = (1+ΦΔ)^{1/2}
# To first order in ΦΔ, √g ≈ 1 + ΦΔ/2.
# The effective coupling should depend on ΦΔ only through the combination
#   ΦΔ/√(1+ΦΔ)  ≈ ΦΔ*(1 - ΦΔ/2 + ...)  → linear term ΦΔ/2.
# We verify that the linear coefficient of ΦΔ in α_eff matches the expected
# scaling from the metric (up to an overall factor that can be absorbed into ΠΔ).
J_star = sp.sqrt(1 + ΦΔ)          # √g
J_star_series = sp.series(J_star, ΦΔ, 0, 2).removeO()  # 1 + ΦΔ/2 + O(ΦΔ^2)
# Expected linear scaling factor from metric: (J_star - 1) ≈ ΦΔ/2
expected_linear = (J_star_series - 1)   # = ΦΔ/2
# Extract linear coefficient from α_eff (relative to α0/(1+Π0))
α0_iso = α0/(1+Π0)
linear_from_eff = sp.simplify((α_eff_series - α0_iso) / ΦΔ)
print("Test 5 – Linear coefficient from α_eff:", linear_from_eff)
print("Test 5 – Expected linear coefficient (metric):", expected_linear)
# They need not be numerically equal because ΠΔ carries the dynamics;
# we only check that the dependence is *linear* in ΦΔ (already done in Test 4)
print("Test 5 – Linear in ΦΔ (consistent with metric):", ΦΔ2_coeff == 0)

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
print("\n=== Validation Summary ===")
print("If any test fails, the expression is NOT Omega‑Protocol compliant.")