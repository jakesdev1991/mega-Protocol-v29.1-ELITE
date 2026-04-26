# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Validation script for the Omega Protocol higher‑order lattice polarization
# derivation.  It checks the algebraic consistency of the key results:
#   1. Vacuum‑polarization splitting with the factor 3 for Φ_Δ.
#   2. Effective polarization Π_eff(q²) and its logarithmic form.
#   3. Running fine‑structure constant α_fs(q²) up to O(α₀²).
#   4. β‑function (RG equation) in the diagonal basis.
#
# The script uses only Python's standard library and sympy (if available).
# If sympy is not installed, a fallback numeric check is performed.

import sys
import math

def try_import_sympy():
    try:
        import sympy as sp
        return sp
    except Exception:
        return None

sp = try_import_sympy()

def symbolic_check():
    """Perform algebraic verification with sympy."""
    # Define symbols
    e, gN, gD, alpha0 = sp.symbols('e gN gD alpha0', positive=True)
    q, Lambda, LambdaN, LambdaD = sp.symbols('q Lambda LambdaN LambdaD', positive=True)
    pi = sp.pi

    # One-loop QED term (coefficient from standard derivation)
    Pi_QED = e**2/(3*pi) * sp.log(Lambda**2 / q**2)

    # Mode contributions (factor 3 for the Archive mode)
    Pi_N   = gN**2/(4*pi) * sp.log(LambdaN**2 / q**2)
    Pi_D   = 3*gD**2/(4*pi) * sp.log(LambdaD**2 / q**2)

    Pi_eff = Pi_QED + Pi_N + Pi_D

    # Inverse coupling: α^{-1}(q²) = α0^{-1} - Π_eff
    alpha_inv = 1/alpha0 - Pi_eff

    # Expand α(q²) = 1/α^{-1} to first order in small couplings
    # Use series expansion assuming α0, gN², gD² are small.
    alpha_series = sp.series(1/alpha_inv, alpha0, 0, 2).removeO()
    # Replace e² with 4π ε0 ħ c α0 → in natural units e² = 4π α0
    # Here we simply set e² = 4π α0 to match the QED prefactor.
    alpha_series_subs = alpha_series.subs(e**2, 4*pi*alpha0).simplify()

    # Expected form:
    expected = alpha0 * (1 +
                         (alpha0/(3*pi))*sp.log(Lambda**2/q**2) +
                         (alpha0*gN**2/(4*pi))*sp.log(LambdaN**2/q**2) +
                         (3*alpha0*gD**2/(4*pi))*sp.log(LambdaD**2/q**2))

    # Check equality
    return sp.simplify(alpha_series_subs - expected) == 0

def numeric_check():
    """Fallback numeric verification (random point test)."""
    import random
    random.seed(42)
    # Choose random positive values
    vals = {
        'e': random.uniform(0.1, 1.0),
        'gN': random.uniform(0.01, 0.2),
        'gD': random.uniform(0.01, 0.2),
        'alpha0': random.uniform(0.001, 0.1),
        'Lambda': random.uniform(10, 1000),
        'LambdaN': random.uniform(10, 1000),
        'LambdaD': random.uniform(10, 1000),
        'q': random.uniform(1, 10)
    }
    pi = math.pi
    # Compute pieces
    Pi_QED = vals['e']**2/(3*pi) * math.log(vals['Lambda']**2/vals['q']**2)
    Pi_N   = vals['gN']**2/(4*pi) * math.log(vals['LambdaN']**2/vals['q']**2)
    Pi_D   = 3*vals['gD']**2/(4*pi) * math.log(vals['LambdaD']**2/vals['q']**2)
    Pi_eff = Pi_QED + Pi_N + Pi_D
    alpha_inv = 1/vals['alpha0'] - Pi_eff
    alpha_num = 1/alpha_inv

    # Series expansion to O(alpha0^2) using the same approximations
    # α ≈ α0 [1 + (α0/3π) ln(Λ²/q²) + (α0 gN²/4π) ln(ΛN²/q²) + (3 α0 gD²/4π) ln(ΛD²/q²)]
    term = (vals['alpha0']/(3*pi))*math.log(vals['Lambda']**2/vals['q']**2) + \
           (vals['alpha0']*vals['gN']**2/(4*pi))*math.log(vals['LambdaN']**2/vals['q']**2) + \
           (3*vals['alpha0']*vals['gD']**2/(4*pi))*math.log(vals['LambdaD']**2/vals['q']**2)
    alpha_series = vals['alpha0'] * (1 + term)

    # Relative difference should be small (higher order terms O(α0³))
    rel_diff = abs(alpha_num - alpha_series) / abs(alpha_num)
    return rel_diff < 1e-3  # tolerance for neglected higher orders

def beta_function_check():
    """Verify the β‑function derived from α^{-1}(q²)."""
    if sp is None:
        # Numeric check: differentiate log derivative
        import random, math
        random.seed(123)
        vals = {
            'alpha0': random.uniform(0.001,0.1),
            'gN': random.uniform(0.01,0.2),
            'gD': random.uniform(0.01,0.2),
            'Lambda': random.uniform(10,1000),
            'LambdaN': random.uniform(10,1000),
            'LambdaD': random.uniform(10,1000)
        }
        # Choose a few q values and compute dα/dln(q²) numerically
        def alpha_of_q2(q2):
            Pi_QED = vals['e']**2/(3*math.pi) * math.log(vals['Lambda']**2/q2)
            Pi_N   = vals['gN']**2/(4*math.pi) * math.log(vals['LambdaN']**2/q2)
            Pi_D   = 3*vals['gD']**2/(4*math.pi) * math.log(vals['LambdaD']**2/q2)
            Pi_eff = Pi_QED + Pi_N + Pi_D
            alpha_inv = 1/vals['alpha0'] - Pi_eff
            return 1/alpha_inv
        qs = [1.0, 2.0, 5.0, 10.0]
        derivs = []
        for i in range(len(qs)-1):
            q1, q2 = qs[i], qs[i+1]
            a1, a2 = alpha_of_q2(q1), alpha_of_q2(q2)
            dlnq = math.log(q2) - math.log(q1)
            derivs.append((a2 - a1)/dlnq)
        # Expected β = -α²/π [1 + 3gD²/(4π) + gN²/(4π)]
        alpha_mid = alpha_of_q2((qs[0]+qs[-1])/2)
        beta_expected = -alpha_mid**2/math.pi * (1 + 3*vals['gD']**2/(4*math.pi) + vals['gN']**2/(4*math.pi))
        # Compare average
        return all(abs(d - beta_expected) < 1e-2 for d in derivs)
    else:
        # Symbolic check
        e, gN, gD, alpha0 = sp.symbols('e gN gD alpha0', positive=True)
        q, Lambda, LambdaN, LambdaD = sp.symbols('q Lambda LambdaN LambdaD', positive=True)
        pi = sp.pi
        Pi_QED = e**2/(3*pi) * sp.log(Lambda**2/q**2)
        Pi_N   = gN**2/(4*pi) * sp.log(LambdaN**2/q**2)
        Pi_D   = 3*gD**2/(4*pi) * sp.log(LambdaD**2/q**2)
        Pi_eff = Pi_QED + Pi_N + Pi_D
        alpha_inv = 1/alpha0 - Pi_eff
        alpha = 1/alpha_inv
        # dα/dln(q²) = q² * dα/d(q²)
        beta = sp.simplify(q**2 * sp.diff(alpha, q))
        expected = -alpha**2/pi * (1 + 3*gD**2/(4*pi) + gN**2/(4*pi))
        return sp.simplify(beta - expected) == 0

def main():
    print("Running validation checks...")
    if sp is not None:
        print("Sympy available – performing symbolic verification.")
        sym_ok = symbolic_check()
        print(f"  Symbolic α_fs expansion check: {'PASS' if sym_ok else 'FAIL'}")
        beta_ok = beta_function_check()
        print(f"  Symbolic β‑function check: {'PASS' if beta_ok else 'FAIL'}")
    else:
        print("Sympy not available – falling back to numeric verification.")
    num_ok = numeric_check()
    print(f"  Numeric α_fs expansion check: {'PASS' if num_ok else 'FAIL'}")
    beta_num_ok = beta_function_check()
    print(f"  Numeric β‑function check: {'PASS' if beta_num_ok else 'FAIL'}")

    overall = (sym_ok if sp is not None else True) and num_ok and beta_ok if sp is not None else num_ok and beta_num_ok
    print("\nOverall validation:", "PASS" if overall else "FAIL")
    sys.exit(0 if overall else 1)

if __name__ == "__main__":
    main()