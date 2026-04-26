# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 Compliance Validator for CTMS‑Ω (or similar) proposals.

Checks:
  1. Invariant definition: ψ = ln(Φ_N/Φ_N0)
  2. Fokker‑Planck equation: ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ²[D P] + S
  3. Action contains explicit entropy gauge term A_μ J^μ
  4. Boundary requirement: presence of "Shredding Event" or "Informational Freeze"
  5. No boilerplate (simple heuristic: >30% of lines are not generic lists)

Usage:
    python3 omega_validator.py --invariant "<sympy expr>" \
                               --fp_eq "<sympy expr>" \
                               --action "<sympy expr>" \
                               --text "<proposal text>"
"""

import sys
import argparse
import re
from sympy import symbols, Eq, ln, Function, diff, simplify, Eq as SymEq

def parse_args():
    p = argparse.ArgumentParser(description="Omega Protocol v26.0 validator")
    p.add_argument("--invariant", required=True,
                   help="Sympy expression for ψ_cog (e.g., ln(Phi_N/Phi_N0))")
    p.add_argument("--fp_eq", required=True,
                   help="Sympy expression for Fokker-Planck RHS (without ∂_t P)")
    p.add_argument("--action", required=True,
                   help="Sympy expression for the integrand of S[Λ]")
    p.add_argument("--text", required=True,
                   help="Full proposal text as a single string")
    return p.parse_args()

def check_invariant(expr_str):
    """Verify ψ = ln(Φ_N/Φ_N0) up to symbolic equivalence."""
    Phi_N, Phi_N0 = symbols('Phi_N Phi_N0')
    target = ln(Phi_N/Phi_N0)
    try:
        expr = eval(expr_str, {"ln": ln, "Phi_N": Phi_N, "Phi_N0": Phi_N0})
    except Exception as e:
        return False, f"Invariant parsing error: {e}"
    return simplify(expr - target) == 0, "Invariant matches ln(Φ_N/Φ_N0)"

def check_fokker_planck(rhs_str):
    """Check that diffusion term carries factor 1/2."""
    # Expected form: -∂_Λ[μ P] + 1/2 ∂_Λ²[D P] + S
    Lambda, t = symbols('Lambda t')
    P = Function('P')(Lambda, t)
    mu, D, S = symbols('mu D S')
    # Build target RHS
    target = -diff(mu*P, Lambda) + Rational(1,2)*diff(diff(D*P, Lambda), Lambda) + S
    try:
        rhs = eval(rhs_str, {"diff": diff, "Lambda": Lambda, "t": t,
                             "P": P, "mu": mu, "D": D, "S": S,
                             "Rational": lambda a,b: a/b})
    except Exception as e:
        return False, f"FP RHS parsing error: {e}"
    return simplify(rhs - target) == 0, "Fokker-Planck includes ½ diffusion factor"

def check_action_gauge(action_str):
    """Action integrand must contain A_mu J^mu term."""
    # We look for a product of two symbols named A and J contracted.
    # Simple heuristic: presence of both A_ and J_ (or A and J) multiplied.
    try:
        expr = eval(action_str, {"A": symbols('A'), "J": symbols('J'),
                                 "mu": symbols('mu'), "nu": symbols('nu')})
    except Exception as e:
        return False, f"Action parsing error: {e}"
    # Check if expression contains a term like A*J or A_mu*J^mu
    # Using string search as a fallback
    action_low = action_str.lower()
    if ("a_" in action_low and "j_" in action_low) or ("a*" in action_low and "j*" in action_low):
        return True, "Entropy gauge term A_μ J^μ detected"
    return False, "Entropy gauge term A_μ J^μ missing"

def check_boundary(text):
    pattern = r"(shredding\s+event|informational\s+freeze)"
    return bool(re.search(pattern, text, re.IGNORECASE)), \
           "Boundary keyword ('Shredding Event' or 'Informational Freeze') found"

def check_boilerplate(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False, "Empty proposal"
    # Heuristic: count lines that look like bullet points or generic lists
    bullet_pattern = r"^[\-\*\•]\s+|^\d+\.\s+"
    bullet_lines = sum(1 for ln in lines if re.match(bullet_pattern, ln))
    ratio = bullet_lines / len(lines)
    # Allow at most 30% boilerplate
    if ratio > 0.3:
        return False, f"Boilerplate ratio too high ({ratio:.0%})"
    return True, "Boilerplate within acceptable limits"

def main():
    args = parse_args()
    ok = True
    msgs = []

    # 1. Invariant
    inv_ok, inv_msg = check_invariant(args.invariant)
    ok &= inv_ok
    msgs.append(("Invariant", inv_ok, inv_msg))

    # 2. Fokker-Planck
    fp_ok, fp_msg = check_fokker_planck(args.fp_eq)
    ok &= fp_ok
    msgs.append(("Fokker-Planck", fp_ok, fp_msg))

    # 3. Action gauge
    gauge_ok, gauge_msg = check_action_gauge(args.action)
    ok &= gauge_ok
    msgs.append(("Entropy gauge", gauge_ok, gauge_msg))

    # 4. Boundary
    bound_ok, bound_msg = check_boundary(args.text)
    ok &= bound_ok
    msgs.append(("Boundary", bound_ok, bound_msg))

    # 5. Boilerplate
    boiler_ok, boiler_msg = check_boilerplate(args.text)
    ok &= boiler_ok
    msgs.append(("Boilerplate", boiler_ok, boiler_msg))

    # Output
    for name, passed, msg in msgs:
        status = "PASS" if passed else "FAIL"
        print(f"{name:15}: {status} - {msg}")

    if not ok:
        print("\nΩ‑Protocol validation FAILED. Please fix the issues above.")
        sys.exit(1)
    else:
        print("\nΩ‑Protocol validation PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()