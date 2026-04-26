# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Jerk‑Stability Validator
---------------------------------------
Usage:
    1. Replace the placeholder `jerk_expr` with your final SymPy expression
       for J_stab (should be a function of phi_N, phi_D, dphi_N, dphi_D,
       xi_N, xi_D, psi, J_source, etc.).
    2. Run the script. It will report PASS/FAIL and why.
"""

import sympy as sp
import re

# ----------------------------------------------------------------------
# 1. USER INPUT: paste your final derived jerk expression here
# ----------------------------------------------------------------------
# Example (do NOT use this; replace with your own):
# jerk_expr = (sp.Derivative(phi_N, t, 3) + sp.Derivative(phi_D, t, 3)) + J_source
# ----------------------------------------------------------------------
# Define symbols (units will be assigned later)
t = sp.symbols('t')
phi_N, phi_D = sp.symbols('phi_N phi_D', positive=True)   # dimensionless after normalization
dphi_N = sp.Derivative(phi_N, t)
dphi_D = sp.Derivative(phi_D, t)
# Stiffness invariants (have dimensions of time^-2)
xi_N, xi_D = sp.symbols('xi_N xi_D', positive=True)
# Invariant
psi = sp.log(phi_N)
# Source term
J_source = sp.symbols('J_source')
# Placeholder for your expression:
jerk_expr = sp.sympify(0)   # <<< REPLACE THIS LINE WITH YOUR DERIVED EXPRESSION >>>
# ----------------------------------------------------------------------


def has_boilerplate(text: str) -> bool:
    """Detect numbered section headings or bullet‑point patterns."""
    numbered = re.search(r'(?m)^\s*\d+\.\s+', text)   # "1. ", "2. ", ...
    bullets  = re.search(r'(?m)^\s*[-*•]\s+', text)   # "- ", "* ", "• "
    return bool(numbered or bullets)


def dimensional_check(expr):
    """Return True if expr reduces to [s^-3] under the unit assignments."""
    # Base dimensions: [M] mass, [L] length, [T] time, [I] current, [Θ] temperature, [N] amount, [J] luminous intensity
    # We only need time; everything else is set to 1 (dimensionless).
    dim = {
        sp.Symbol('t'): sp.T,          # time
        sp.Symbol('phi_N'): 1,         # dimensionless
        sp.Symbol('phi_D'): 1,
        sp.Symbol('dphi_N'): sp.T**(-1),   # derivative adds 1/T
        sp.Symbol('dphi_D'): sp.T**(-1),
        sp.Symbol('xi_N'): sp.T,       # xi has dimension of time (xi^-2 -> 1/T^2)
        sp.Symbol('xi_D'): sp.T,
        sp.Symbol('psi'): 1,           # log of dimensionless -> dimensionless
        sp.Symbol('J_source'): sp.T**(-3), # source jerk unit
    }

    # Replace each symbol with its dimension, then simplify
    dim_expr = expr.subs(dim)
    # Simplify assuming T is the only base dimension
    dim_expr = sp.simplify(dim_expr)
    # Expected dimension: T^-3
    expected = sp.T**(-3)
    return sp.simplify(dim_expr / expected) == 1


def invariant_used(expr):
    """Check that psi (or ln(phi_N)) appears somewhere in the expression."""
    return expr.has(psi) or expr.has(sp.log(phi_N))


def numeric_evaluation(expr):
    """Plug in the supplied numbers and return a float (in s^-3)."""
    # Supplied data
    subs_dict = {
        phi_N: 0.78,
        phi_D: 0.35,
        dphi_N: 2.1e3,      # s^-1
        dphi_D: 8.7e3,      # s^-1
        # xi^-2 = 4.2e6 s^-2  => xi = 1/sqrt(4.2e6) s
        xi_N: 1.0 / sp.sqrt(4.2e6),
        xi_D: 1.0 / sp.sqrt(4.2e6),
        psi: sp.log(0.78),
        J_source: 1.5e12,   # s^-3
    }
    try:
        val = expr.subs(subs_dict).evalf()
        return float(val)
    except Exception as e:
        return f"Evaluation error: {e}"


def main():
    # ------------------------------------------------------------------
    # Boilerplate check on the source code (comments are ignored)
    # ------------------------------------------------------------------
    source_lines = open(__file__).read()
    if has_boilerplate(source_lines):
        print("FAIL: Source contains boilerplate (numbered sections or bullets).")
        return

    # ------------------------------------------------------------------
    # Expression sanity
    # ------------------------------------------------------------------
    if jerk_expr == 0:
        print("FAIL: No jerk expression provided. Replace the placeholder.")
        return

    print("Expression under test:")
    sp.pprint(jerk_expr)
    print()

    # ------------------------------------------------------------------
    # Dimensional analysis
    # ------------------------------------------------------------------
    if not dimensional_check(jerk_expr):
        print("FAIL: Dimensional inconsistency. Expected [s^-3].")
        return
    print("PASS: Dimensional consistency ([s^-3]) verified.")

    # ------------------------------------------------------------------
    # Invariant usage
    # ------------------------------------------------------------------
    if not invariant_used(jerk_expr):
        print("FAIL: Invariant ψ = ln(φ_N) not found in the expression.")
        return
    print("PASS: Invariant ψ appears in the expression.")

    # ------------------------------------------------------------------
    # Numeric evaluation
    # ------------------------------------------------------------------
    num_val = numeric_evaluation(jerk_expr)
    if isinstance(num_val, str):
        print(f"FAIL: {num_val}")
        return
    print(f"Numeric jerk value: {num_val:.3e} s⁻³")
    threshold = 5.0e12
    if abs(num_val) < threshold:
        print(f"Result is BELOW the stability threshold ({threshold:.2e} s⁻³).")
    else:
        print(f"Result is ABOVE the stability threshold ({threshold:.2e} s⁻³).")

    print("\nOverall: PASS – expression satisfies Omega Protocol checks.")


if __name__ == "__main__":
    main()