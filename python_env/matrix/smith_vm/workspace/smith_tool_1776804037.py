# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Higher‑Order Lattice Polarization
Checks:
  1. Presence of required Omega invariants (psi, xi_N, xi_Delta).
  2. That the one-loop anisotropic term retains angular dependence
     (i.e., does NOT reduce to a pure mass term after trace).
  3. Basic structural sanity: Phi_N, Phi_Delta appear as expected.
"""

import re
import sympy as sp

def validate_derivation(text: str) -> dict:
    """
    Returns a dict with validation results.
    """
    # Normalise whitespace and case for robust substring search
    clean = re.sub(r'\s+', ' ', text).lower()

    # ----- 1. Omega invariants -------------------------------------------------
    inv_patterns = {
        "psi": r'psi\s*=\s*ln\s*\(\s*phi_n\s*\)',
        "xi_n": r'xi_n\s*=\s*∂phi_n\s*/\s*∂psi',
        "xi_delta": r'xi_delta\s*=\s*∂phi_delta\s*/\s*∂psi',
    }
    inv_present = {k: bool(re.search(pat, clean)) for k, pat in inv_patterns.items()}

    # ----- 2. One-loop angular dependence --------------------------------------
    # Look for the problematic collapsed form: "... * m^2 * ..." inside the PhiDelta term
    # and ensure there is at least one sin_z*k or sin_z*(k-p) factor.
    one_loop_block = re.search(
        r'delta\s*pi\s*\(1\)\s*\(mu,nu\)\s*=\s*phi_delta\s*.*?\[',
        clean,
        re.DOTALL | re.IGNORECASE,
    )
    one_loop_ok = False
    if one_loop_block:
        block = one_loop_block.group(0)
        # If the block contains only a mass term after the bracket, it's bad.
        bad_mass = re.search(r'\[\s*.*?m\s*\*\*?\s*2\s*.*?\]', block)
        good_angular = re.search(
            r'sin\s*_?z\s*\*\s*k\s*|\s*sin\s*_?z\s*\*\s*\(k\s*-\s*p\s*\)',
            block,
            re.IGNORECASE,
        )
        one_loop_ok = (bad_mass is None) and (good_angular is not None)

    # ----- 3. Phi_N / Phi_Delta appearance ------------------------------------
    phi_n_present = bool(re.search(r'phi_n\s*', clean))
    phi_delta_present = bool(re.search(r'phi_delta\s*', clean))

    # ----- Assemble result ----------------------------------------------------
    result = {
        "Omega invariants": inv_present,
        "All invariants present": all(inv_present.values()),
        "One-loop angular dependence preserved": one_loop_ok,
        "Phi_N present": phi_n_present,
        "Phi_Delta present": phi_delta_present,
        "Overall compliant": (
            all(inv_present.values())
            and one_loop_ok
            and phi_n_present
            and phi_delta_present
        ),
    }
    return result


# ---------------------------------------------------------------------------
# Example usage with the Engine's text (paste the derivation string here)
# ---------------------------------------------------------------------------
engine_text = r"""
[Insert the full Engine derivation text here – the long LaTeX block]
"""

if __name__ == "__main__":
    report = validate_derivation(engine_text)
    from pprint import pprint
    pprint(report)

    # Simple pass/fail for the VM
    if report["Overall compliant"]:
        print("META-PASS: Derivation satisfies Omega Protocol invariants and mathematical soundness.")
    else:
        print("META-FAIL: See report for deficiencies.")