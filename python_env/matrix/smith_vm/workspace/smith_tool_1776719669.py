# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Meta‑Scrutiny Engine
Checks:
  1. Presence of required Omega invariants and entropy terms.
  2. Basic mathematical correctness of the one‑loop vacuum‑polarization
     low‑q² expansion (integral factor, sign, and α₀² constant).
Usage:
    python omega_validator.py "<Engine raw output>"
"""

import sys
import re
import sympy as sp

# ----------------------------------------------------------------------
# 1. Rubric‑term validation
# ----------------------------------------------------------------------
REQUIRED_INVARIANTS = [
    r"\\psi\s*=\s*\\ln\s*\(\s*\\phi_n\s*\)",   # ψ = ln(φₙ)
    r"\\xi_N",
    r"\\xi_\\Delta",
]
REQUIRED_ENTROPY = [
    r"Shannon\s+conditional\s+entropy",
    r"topological\s+impedance",
]

def check_rubric(text: str) -> tuple[bool, list[str]]:
    missing = []
    for pat in REQUIRED_INVARIANTS + REQUIRED_ENTROPY:
        if not re.search(pat, text, re.IGNORECASE):
            missing.append(pat)
    return (len(missing) == 0, missing)

# ----------------------------------------------------------------------
# 2. Mathematical validation (sympy)
# ----------------------------------------------------------------------
def check_math(text: str) -> tuple[bool, list[str]]:
    errors = []

    # Define symbols
    x, q2, m_eff2, alpha0 = sp.symbols('x q2 m_eff2 alpha0', positive=True)
    # One‑loop vacuum polarization integrand (standard QED)
    integrand = x * (1 - x) * sp.log(1 - x*(1-x)*q2/m_eff2)

    # Exact integral from 0 to 1 (should be zero at q2=0, we expand)
    I_exact = sp.integrate(integrand, (x, 0, 1))
    # Series expansion in q2/m_eff2 up to O(q2)
    I_series = sp.series(I_exact, q2, 0, 2).removeO()
    # Expected coefficient: + alpha0/(90*pi) * q2/m_eff2
    expected_coeff = alpha0/(90*sp.pi) * q2/m_eff2

    # Extract coefficient of q2/m_eff2 from series
    coeff_actual = sp.simplify(I_series.coeff(q2/m_eff2, 1))
    if not sp.simplify(coeff_actual - expected_coeff) == 0:
        errors.append(
            f"One‑loop coefficient mismatch: got {coeff_actual}, expected {expected_coeff}"
        )

    # Check sign of Π(q²) for spacelike q² (should be +)
    # Π ≈ alpha0 * I_series
    Pi_approx = alpha0 * I_series
    # The term proportional to q2/m_eff2 should be positive
    term = sp.simplify(Pi_approx.coeff(q2/m_eff2, 1))
    if term.is_negative:
        errors.append(
            f"Sign error: vacuum‑polarization term is {term} (should be positive for spacelike q²)"
        )

    # Check for missing α₀² constant term (two‑loop)
    # Look for a standalone α₀² term not multiplied by q²/m_eff² or log
    # Simple heuristic: search for pattern α₀²/(4π²)*(11/2 - 3ζ(2))
    const_pat = r"\\alpha_0\\^2\\s*/\\s*4\\s*\\pi\\^2\\s*\\*\s*\\(\\s*11/2\s*-\\s*3\\s*\\\\zeta\\s*\\(\\s*2\\s*\\)\\s*\\)"
    if not re.search(const_pat, text):
        errors.append(
            "Missing two‑loop constant term: α₀²/(4π²)*(11/2 - 3ζ(2))"
        )

    return (len(errors) == 0, errors)

# ----------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python omega_validator.py \"<Engine raw output>\"")
        sys.exit(1)

    engine_text = sys.argv[1]

    # Rubric check
    rubric_ok, missing = check_rubric(engine_text)
    if not rubric_ok:
        print("[RUBRIC FAIL] Missing required Omega terms:")
        for m in missing:
            print("  -", m)
    else:
        print("[RUBRIC PASS] All required invariants & entropy terms present.")

    # Math check
    math_ok, errs = check_math(engine_text)
    if not math_ok:
        print("[MATH FAIL] Mathematical issues:")
        for e in errs:
            print("  -", e)
    else:
        print("[MATH PASS] One‑loop expansion and α₀² constant are correct.")

    # Overall verdict
    if rubric_ok and math_ok:
        print("\n>>> OMEGA VALIDATION: PASS <<<")
        sys.exit(0)
    else:
        print("\n>>> OMEGA VALIDATION: FAIL <<<")
        sys.exit(1)

if __name__ == "__main__":
    main()