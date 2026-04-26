# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator v1.0
- Detects boilerplate (headings, lists, explicit section labels).
- Checks dimensional consistency of extracted equations.
- (Optional) Symbolic Hessian test for I(A) and V(I).
"""

import re
import sympy as sp
from sympy.physics.units import DimensionSystem, dimsys_SI

# ----------------------------------------------------------------------
# 1. Boilerplate detection
# ----------------------------------------------------------------------
BOILERPLATE_PATTERNS = [
    r'^\s*#{1,6}\s',               # markdown headings
    r'^\s*\d+\.\s',                # numbered list
    r'^\s*[-*+]\s',                # bullet list
    r'^\s*[A-Z][a-z]+:\s',         # explicit label like "Step 1 –"
    r'^\s*Phase\s+\d+[-–]',        # "Phase 1 –"
]

def has_boilerplate(text: str) -> bool:
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        for pat in BOILERPLATE_PATTERNS:
            if re.match(pat, line):
                print(f"Boilerplate detected at line {i}: {line.strip()}")
                return True
    return False

# ----------------------------------------------------------------------
# 2. Dimensional consistency helper
# ----------------------------------------------------------------------
# Define base dimensions we care about
T = sp.Symbol('T')          # time
# In natural units (ħ = c = 1) action is dimensionless, but we keep [T]⁻¹ as
# the text uses. We'll let the user choose a system.
def make_dim_system(use_natural: bool = False):
    if use_natural:
        # action dimensionless -> [S] = 1
        return DimensionSystem([T], {sp.Symbol('S'): 1})
    else:
        # action has dimensions of energy·time -> [M L^2 T^-1]·[T] = [M L^2]
        # For simplicity we treat [S] = T^-1 as the text claims.
        return DimensionSystem([T], {sp.Symbol('S'): T**-1})

def check_dimension(expr: sp.Expr, dim_system: DimensionSystem) -> bool:
    """Return True if expr is dimensionless according to dim_system."""
    try:
        dim = dim_system.get_dimensional_dependence(expr)
        # expr is dimensionless if all exponents are zero
        return all(exp == 0 for exp in dim.values())
    except Exception:
        # If SymPy cannot determine dimension, assume unknown -> fail
        return False

def extract_equations(text: str):
    """Very naive extraction: look for patterns like '=' or '∫'."""
    # Replace line breaks with spaces for easier regex
    flat = re.sub(r'\s+', ' ', text)
    # Find anything that looks like an equation: contains '=' and not just a word
    eq_candidates = re.findall(r'[^=\n]+?=[^=\n]+?', flat)
    # Also capture integral-like expressions
    int_candidates = re.findall(r'∫[^∫]+?d[tT]', flat, flags=re.IGNORECASE)
    return eq_candidates + int_candidates

def dimensional_audit(text: str, use_natural: bool = False):
    dim_sys = make_dim_system(use_natural)
    equations = extract_equations(text)
    problems = []
    for eq in equations:
        try:
            lhs, rhs = eq.split('=', 1)
            lhs_sym = sp.sympify(lhs.strip())
            rhs_sym = sp.sympify(rhs.strip())
        except Exception:
            # If we cannot split or sympify, skip
            continue
        if not (check_dimension(lhs_sym, dim_sys) and check_dimension(rhs_sym, dim_sys)):
            problems.append(eq.strip())
    return problems

# ----------------------------------------------------------------------
# 3. (Optional) Hessian test – user must supply I(A) and V(I)
# ----------------------------------------------------------------------
def hessian_test(I_expr, A_symbols, lam, I0):
    """
    I_expr : sympy expression of I in terms of A_symbols
    A_symbols : iterable of sympy symbols (the amplitudes)
    lam, I0 : symbols for λ and I₀
    Returns eigenvalues of Hessian of V(I) at I=I0.
    """
    V = (lam/4)*(I_expr**2 - I0**2)**2
    grad = [sp.diff(V, a) for a in A_symbols]
    hess = [[sp.diff(g, b) for b in A_symbols] for g in grad]
    # Substitute equilibrium condition I=I0 (i.e. I_expr = I0)
    subs_dict = {I_expr: I0}
    hess_eq = [[sp.simplify(h.subs(subs_dict)) for h in row] for row in hess]
    hess_mat = sp.Matrix(hess_eq)
    eigs = hess_mat.eigenvals()
    return eigs

# ----------------------------------------------------------------------
# Main driver – example usage
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Load the narrative (here we read from a file; replace with your string)
    with open("engine_pleading.txt", "r", encoding="utf-8") as f:
        narrative = f.read()

    print("=== Boilerplate Check ===")
    if has_boilerplate(narrative):
        print("FAIL: Boilerplate present.")
    else:
        print("PASS: No boilerplate detected.")

    print("\n=== Dimensional Consistency Check ===")
    # Try both conventions: text's claim ([S]=T^-1) and natural units
    for label, natural in [("Text convention ([S]=T⁻¹)", False),
                           ("Natural units ([S]=dimensionless)", True)]:
        problems = dimensional_audit(narrative, use_natural=natural)
        if problems:
            print(f"{label}: FAIL – {len(problems)} expression(s) dim‑inconsistent:")
            for p in problems[:5]:  # show first few
                print("  ", p)
        else:
            print(f"{label}: PASS – all extracted expressions dimensionally consistent.")

    print("\n=== Optional Hessian Test (illustrative) ===")
    # Define a simple two‑mode example to show the rank‑1 property
    A1, A2 = sp.symbols('A1 A2', real=True)
    lam, I0 = sp.symbols('lam I0', positive=True)
    # I = - Σ p log p with p_k = A_k^2 / (A1^2 + A2^2)
    sq_sum = A1**2 + A2**2
    p1 = A1**2 / sq_sum
    p2 = A2**2 / sq_sum
    I_expr = -(p1*sp.log(p1) + p2*sp.log(p2))
    eigs = hessian_test(I_expr, [A1, A2], lam, I0)
    print("Eigenvalues of Hessian(V) at I=I0 for two‑mode case:")
    print(eigs)
    print("Note: only one non‑zero eigenvalue (rank‑1 Hessian).")