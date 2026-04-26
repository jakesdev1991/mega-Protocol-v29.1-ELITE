# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# Agent Smith's Omega‑Protocol Validation Script
# -------------------------------------------------
# Usage: Provide the vacuum polarization expression as a string
#        using sympy syntax. Example:
#        expr = "alpha0/(3*pi)*log(-q**2/m**2) + gDelta**2*alpha0/(32*pi**4)*log(-q**2/m**2)**2"
#        validate_vacuum_polarization(expr)
#
# The script will print PASS/FAIL for each invariant test.

import sympy as sp
import sys

def validate_vacuum_polarization(expr_str):
    # -----------------------------------------------------------------
    # 1. Symbols
    # -----------------------------------------------------------------
    q, m, alpha0, gDelta, pi = sp.symbols('q m alpha0 gDelta pi', positive=True)
    # Lorentz structure: we assume the transverse form (q^2*g^{mu\nu} - q^mu q^nu)
    # For the scalar check we only need the coefficient function Pi(q^2)
    # so we treat expr as the coefficient multiplying (q^2*g^{mu\nu} - q^mu q^nu)
    Pi = sp.sympify(expr_str)

    # -----------------------------------------------------------------
    # 2. Gauge invariance: q_mu Pi^{mu nu} = 0  <=> Pi depends only on q^2
    # -----------------------------------------------------------------
    # Check that Pi has no explicit q (only q^2)
    if Pi.has(q) and not Pi.has(q**2):
        print("[FAIL] Pi depends linearly on q (violates transverse structure).")
        return False
    # Replace q^2 -> s to simplify further checks
    s = sp.symbols('s')
    Pi_s = Pi.subs(q**2, s)

    # -----------------------------------------------------------------
    # 3. Dimensionless check: Pi must be dimensionless
    # -----------------------------------------------------------------
    # Dimensions: [alpha0] = 0, [gDelta] = 0, [m] = 1, [q] = 1
    # We assign dimension 1 to m and q, 0 to couplings.
    def dim(expr):
        # Replace each symbol with its dimension exponent
        d = 0
        d += expr.has(alpha0) * 0   # dimensionless
        d += expr.has(gDelta) * 0   # dimensionless
        d += expr.has(m) * 1        # mass dimension 1
        d += expr.has(q) * 1        # mass dimension 1
        # logs are dimensionless if argument dimensionless
        # we will check argument separately
        return d
    # Simple check: any leftover m or q inside a log must be ratio
    log_args = [arg for arg in Pi_s.atoms(sp.log) if arg.is_Mul or arg.is_Pow]
    bad = False
    for arg in log_args:
        # argument should be dimensionless -> ratio of two masses or q^2/m^2 etc.
        # We'll accept forms like -q**2/m**2, m**2/q**2, etc.
        if not (arg.has(q**2) and arg.has(m**2)):
            print(f"[FAIL] Log argument {arg} not dimensionless.")
            bad = True
    if bad:
        return False

    # -----------------------------------------------------------------
    # 4. One-loop QED limit: set gDelta -> 0, expand to O(alpha0)
    # -----------------------------------------------------------------
    Pi_QED = sp.simplify(Pi_s.subs(gDelta, 0))
    # Expected: + alpha0/(3*pi) * log(-s/m**2)  (note minus inside log)
    expected_QED = alpha0/(3*pi) * sp.log(-s/m**2)
    if not sp.simplify(Pi_QED - expected_QED):
        print("[PASS] One-loop QED term matches.")
    else:
        print("[FAIL] One-loop QED term mismatch.")
        print(f"  Got:      {Pi_QED}")
        print(f"  Expected: {expected_QED}")
        return False

    # -----------------------------------------------------------------
    # 5. Phi_Delta scaling: check mass dimension of gDelta^2 term
    # -----------------------------------------------------------------
    # Extract term proportional to gDelta**2
    coeff_g2 = sp.Poly(Pi_s, gDelta).coeff_monomial(gDelta**2) if Pi_s.has(gDelta**2) else 0
    if coeff_g2:
        # coeff_g2 should be dimensionless * log^2(...) (or log * const)
        # Check that coeff_g2 has no leftover m or q dimensions
        if coeff_g2.has(m) or coeff_g2.has(q):
            print("[FAIL] gDelta^2 term carries incorrect mass dimension.")
            return False
        # Optionally, check that the log power is at most 2 (as expected from two-loop)
        log_pow = sp.Poly(coeff_g2, sp.log(-s/m**2)).degree()
        if log_pow > 2:
            print(f"[FAIL] Unexpected log power {log_pow} in gDelta^2 term.")
            return False
        print("[PASS] Phi_Delta term respects dimensional analysis.")
    else:
        print("[INFO] No gDelta^2 term present.")

    # -----------------------------------------------------------------
    # 6. Beta-function consistency (optional)
    # -----------------------------------------------------------------
    # Beta(alpha) = mu * d alpha / d mu = - alpha^2 * d Pi / d log(mu)
    # In MS-bar, d/d log(mu) acts on log(-q^2/m^2) -> -1
    # So beta_QED = 2*alpha0**2/(3*pi)
    # We compute beta from Pi and compare.
    mu = sp.symbols('mu')
    # Replace m -> mu (renormalization scale)
    Pi_mu = Pi_s.subs(m, mu)
    dPi_dlogmu = - sp.diff(Pi_mu, sp.log(mu))  # derivative w.r.t. log(mu)
    beta = - alpha0**2 * dPi_dlogmu
    beta_simplified = sp.simplify(beta)
    expected_beta = 2*alpha0**2/(3*pi)  # pure QED part
    # subtract expected and see if remainder is O(alpha0*gDelta^2)
    remainder = sp.simplify(beta_simplified - expected_beta)
    if remainder.has(gDelta):
        # check that remainder is at most O(alpha0 * gDelta**2)
        if not remainder.has(alpha0*gDelta**2):
            print("[FAIL] Beta-function contains unexpected gDelta dependence.")
            return False
        else:
            print("[PASS] Beta-function includes correct scalar contribution.")
    else:
        print("[INFO] Beta-function reduces to pure QED (no scalar term detected).")

    # -----------------------------------------------------------------
    # 7. Summary
    # -----------------------------------------------------------------
    print("\n=== All core invariant checks passed ===")
    return True

# -----------------------------------------------------------------
# Example usage (uncomment to test)
# -----------------------------------------------------------------
if __name__ == "__main__":
    # Example expression from the Engine (note the sign error)
    expr_engine = (
        "alpha0/(3*pi)*log(-q**2/m**2)"   # one-loop QED (correct sign)
        "+ gDelta**2*alpha0/(32*pi**4)*log(-q**2/m**2)**2"  # suspect two-loop term
    )
    print("Validating Engine's expression:")
    validate_vacuum_polarization(expr_engine)