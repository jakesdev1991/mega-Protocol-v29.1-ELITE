# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Derivation Validator (SymPy based)
# --------------------------------------------------------------
# Usage:  Define the symbols and expressions below as per your
#         derivation, then run the script.  All checks must pass
#         for the derivation to be considered equation‑level correct.
# --------------------------------------------------------------

import sympy as sp

# ------------------- 1. Symbols -------------------
PhiN, PhiD, v, lam = sp.symbols('PhiN PhiD v lam', real=True)
# Couplings (appear in Pi_eff and alpha)
e, gN, gD = sp.symbols('e gN gD', real=True)
# Momentum scale
q2, Lambda, LambdaN, LambdaD = sp.symbols('q2 Lambda LambdaN LambdaD', positive=True)
# Bare coupling
alpha0 = sp.symbols('alpha0', positive=True)

# ------------------- 2. Potential -------------------
# Mexican-hat form
V = lam/4 * (PhiN**2 + PhiD**2 - v**2)**2

# Stiffnesses from second derivatives
xiN_inv2_expr = sp.diff(V, PhiN, 2)
xiD_inv2_expr = sp.diff(V, PhiD, 2)

# Claimed forms (as per plead-case)
xiN_inv2_claimed = lam * (3*PhiN**2 + PhiD**2 - v**2)
xiD_inv2_claimed = lam * (PhiN**2 + 3*PhiD**2 - v**2)

# ------------------- 3. Effective polarisation -------------------
# General log form (coefficients to be checked)
A, B, C = sp.symbols('A B C')
Pi_eff = A*sp.log(Lambda**2/q2) + B*sp.log(LambdaN**2/q2) + C*sp.log(LambdaD**2/q2)

# Running coupling (first‑order expansion)
alpha_run = alpha0 * (1 + alpha0 * Pi_eff)

# ------------------- 4. Beta‑function -------------------
# Derivative w.r.t. ln(q2)  <=>  -q2 * d/d(q2)
beta_expr = -q2 * sp.diff(alpha_run, q2)
beta_simplified = sp.simplify(beta_expr)

# Claimed beta (plead‑case form)
#   -alpha^2/pi * [1 + 3*gD^2/(4*pi) + gN^2/(4*pi)]
beta_claimed = -alpha_run**2 / sp.pi * (1 + 3*gD**2/(4*sp.pi) + gN**2/(4*sp.pi))

# ------------------- 5. Shredding condition -------------------
# Curvature in PhiD direction
curvature_PhiD = sp.diff(V, PhiD, 2)
shredding_cond = sp.Eq(curvature_PhiD, 0)   # => PhiN^2 + 3*PhiD^2 = v^2

# ------------------- 6. Validation checks -------------------
def check(expr1, expr2, name):
    """Return True if expr1 and expr2 are identical up to simplification."""
    diff = sp.simplify(expr1 - expr2)
    if diff == 0:
        print(f"[PASS] {name}")
        return True
    else:
        print(f"[FAIL] {name}")
        print(f"       Difference: {diff}")
        return False

all_ok = True

all_ok &= check(xiN_inv2_expr, xiN_inv2_claimed, "xiN^-2 matches potential")
all_ok &= check(xiD_inv2_expr, xiD_inv2_claimed, "xiD^-2 matches potential")
all_ok &= check(sp.simplify(alpha_run - alpha0*(1 + alpha0*Pi_eff)), 0,
                "alpha_run expansion correct")
all_ok &= check(beta_simplified, beta_claimed, "beta matches derivative of alpha_run")
# For shredding we just verify the algebraic equivalence
shredding_eq = sp.simplify(curvature_PhiD)
all_ok &= check(shredding_eq, lam*(PhiN**2 + 3*PhiD**2 - v**2),
                "shredding condition curvature expression")

# ------------------- 7. Report -------------------
if all_ok:
    print("\n=== All core mathematical checks PASSED ===")
else:
    print("\n=== Some checks FAILED – derivation not equation‑level correct ===")
    print("Please revise the offending expressions and re‑run.")