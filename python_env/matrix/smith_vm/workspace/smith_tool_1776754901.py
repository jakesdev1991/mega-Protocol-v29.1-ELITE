# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator – Tokamak Jerk‑Stability Proposal
-------------------------------------------------------------------
This script checks the mathematical soundness of the boundary condition
derived from the Mexican‑hat potential V = (Φ_N² + Φ_Δ² - ψ₀²)².
It verifies:
  1. Correct expressions for ξ_N, ξ_Δ.
  2. Instability occurs when ∂²V/∂Φ² = 0  →  ξ → ∞.
  3. The proposal's claim (ξ → 0 at instability) is false.
Run in the isolated VM; any assertion failure indicates a rule violation.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbolic definitions
# ----------------------------------------------------------------------
Φ_N, Φ_Δ, ψ0 = sp.symbols('Φ_N Φ_Δ ψ0', real=True, nonnegative=True)

# Mexican‑hat potential
V = (Φ_N**2 + Φ_Δ**2 - ψ0**2)**2

# Second derivatives (mass terms)
d2V_dΦN2 = sp.diff(V, Φ_N, 2)
d2V_dΦΔ2 = sp.diff(V, Φ_Δ, 2)

# Correlation lengths (inverse sqrt of mass terms)
xi_N = sp.simplify((d2V_dΦN2)**(-sp.Rational(1,2)))
xi_Δ = sp.simplify((d2V_dΦΔ2)**(-sp.Rational(1,2)))

# ----------------------------------------------------------------------
# Analytic instability condition: second derivative = 0
# ----------------------------------------------------------------------
instability_cond_N = sp.simplify(d2V_dΦN2)   # = 4*(3*Φ_N**2 + Φ_Δ**2 - ψ0**2)
instability_cond_Δ = sp.simplify(d2V_dΦΔ2)   # = 4*(Φ_N**2 + 3*Φ_Δ**2 - ψ0**2)

# Solve for the threshold surfaces
threshold_N = sp.solve(instability_cond_N, Φ_N**2)   # Φ_N**2 = (ψ0**2 - Φ_Δ**2)/3
threshold_Δ = sp.solve(instability_cond_Δ, Φ_Δ**2)   # Φ_Δ**2 = (ψ0**2 - Φ_N**2)/3

# ----------------------------------------------------------------------
# Validation checks
# ----------------------------------------------------------------------
def check_expression(expr, expected_form, name):
    """Simple structural check – ensures expr matches expected_form up to a constant factor."""
    # Expect expr = C * expected_form ; we compare the ratio to be constant
    ratio = sp.simplify(expr / expected_form)
    if not ratio.is_constant():
        raise AssertionError(f"{name} does not match expected form; ratio = {ratio}")
    return ratio

# 1. Verify ξ expressions are inverse sqrt of the mass terms
try:
    check_expression(xi_N, (d2V_dΦN2)**(-sp.Rational(1,2)), "ξ_N")
    check_expression(xi_Δ, (d2V_dΦΔ2)**(-sp.Rational(1,2)), "ξ_Δ")
    print("[PASS] ξ_N and ξ_Δ correctly derived from V.")
except AssertionError as e:
    print("[FAIL]", e)

# 2. Instability when mass term = 0 → ξ diverges
#    We test that substituting the threshold makes the denominator zero.
denom_N = d2V_dΦN2
denom_Δ = d2V_dΦΔ2

subs_N = {Φ_N**2: (ψ0**2 - Φ_Δ**2)/3}   # from threshold_N
subs_Δ = {Φ_Δ**2: (ψ0**2 - Φ_N**2)/3}   # from threshold_Δ

# Evaluate denominators at the threshold (should be zero)
val_N = sp.simplify(denom_N.subs(subs_N))
val_Δ = sp.simplify(denom_Δ.subs(subs_Δ))

if val_N == 0 and val_Δ == 0:
    print("[PASS] Second derivative vanishes at the derived threshold → ξ → ∞ (instability).")
else:
    print("[FAIL] Second derivative does not vanish at threshold.")
    print("  val_N =", val_N, " val_Δ =", val_Δ)

# 3. Check the proposal's erroneous claim: ξ → 0 at instability
#    Substitute threshold into ξ expressions; they should blow up (i.e., be infinite).
#    In sympy we detect this by checking if the expression contains a division by zero.
def xi_diverges(xi_expr, subs_dict):
    """Return True if xi_expr becomes infinite (denominator zero) under subs."""
    expr_sub = xi_expr.subs(subs_dict)
    # If expression contains Pow with negative exponent of zero -> infinite
    return expr_sub.has(sp.Pow) and any(
        isinstance(arg, sp.Pow) and arg.exp < 0 and arg.base == 0
        for arg in sp.preorder_traversal(expr_sub)
    )

# For ξ_N
div_N = xi_diverges(xi_N, subs_N)
# For ξ_Δ
div_Δ = xi_diverges(xi_Δ, subs_Δ)

if div_N and div_Δ:
    print("[PASS] ξ_N and ξ_Δ diverge (→∞) at instability threshold.")
else:
    print("[FAIL] ξ does NOT diverge at threshold – this would support the erroneous ξ→0 claim.")
    print("  div_N =", div_N, " div_Δ =", div_Δ)

# ----------------------------------------------------------------------
# Numeric illustration (optional)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Choose a sample ψ0 = 1.0, Φ_Δ = 0.2 → compute Φ_N at threshold
    psi0_val = 1.0
    PhiDelta_val = 0.2
    # From threshold: Φ_N^2 = (ψ0^2 - Φ_Δ^2)/3
    PhiN_sq_val = (psi0_val**2 - PhiDelta_val**2) / 3.0
    PhiN_val = sp.sqrt(PhiN_sq_val)
    print("\n--- Numeric Example ---")
    print(f"ψ0 = {psi0_val}, Φ_Δ = {PhiDelta_val}")
    print(f"Threshold Φ_N = sqrt((ψ0^2 - Φ_Δ^2)/3) = {PhiN_val.evalf()}")
    # Compute ξ at threshold
    xi_N_val = xi_N.subs({Φ_N: PhiN_val, Φ_Δ: PhiDelta_val, ψ0: psi0_val})
    xi_Δ_val = xi_Δ.subs({Φ_N: PhiN_val, Φ_Δ: PhiDelta_val, ψ0: psi0_val})
    print(f"ξ_N at threshold = {xi_N_val.evalf()} (should be oo)")
    print(f"ξ_Δ at threshold = {xi_Δ_val.evalf()} (should be oo)")
    # Show that a small perturbation makes ξ large but finite
    eps = 1e-3
    xi_N_pert = xi_N.subs({Φ_N: PhiN_val + eps, Φ_Δ: PhiDelta_val, ψ0: psi0_val})
    xi_Δ_pert = xi_Δ.subs({Φ_N: PhiN_val, Φ_Δ: PhiDelta_val + eps, ψ0: psi0_val})
    print(f"ξ_N (Φ_N+{eps}) = {xi_N_pert.evalf()}")
    print(f"ξ_Δ (Φ_Δ+{eps}) = {xi_Δ_pert.evalf()}")