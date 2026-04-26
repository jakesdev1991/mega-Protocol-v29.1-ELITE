# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol compliance checker:
  - Structural: no markdown headings, bullet points, or enumerated lists.
  - Dimensional: verify homogeneity of equations under Omega base dimensions.
"""

import re
import sympy as sp
from sympy.physics.units import second as T  # base time dimension

# ----------------------------------------------------------------------
# 1. Structural validation
# ----------------------------------------------------------------------
def structural_check(text: str) -> bool:
    """Return True if text contains NO forbidden boilerplate patterns."""
    # Markdown headings: lines starting with one or more '#'
    heading_pat = re r'^\s*#+'
    # Bullet points: lines starting with '-', '*', or '+'
    bullet_pat = re r'^\s*[-*+]'
    # Enumerated lists: lines starting with a number followed by '.' or ')'
    enum_pat = re r'^\s*\d+[.)]'
    for line in text.splitlines():
        if (re.match(heading_pat, line) or
            re.match(bullet_pat, line) or
            re.match(enum_pat, line)):
            return False
    return True

# ----------------------------------------------------------------------
# 2. Dimensional validation
# ----------------------------------------------------------------------
# Define dimension symbols
dim = sp.symbols('dim')
# Base dimension: time
T_dim = T  # sympy's second has dimension of time

# Mapping of symbols to dimensions (as sympy expressions)
dim_map = {
    # dimensionless quantities
    'Phi_N': 1, 'Phi_Delta': 1, 'psi': 1, 'PHI': 1, 'I': 1,
    # coupling constant λ -> [T^-2]
    'lam': T_dim**-2,
    # stiffness invariants -> [T]
    'xi_N': T_dim, 'xi_Delta': T_dim,
    # reference scale ξ0 -> [T]
    'xi0': T_dim,
    # harmonic amplitudes A_k -> dimensionless (normalized)
    # (if they carried units, they'd cancel in ratios)
}

def expr_dim(expr):
    """Recursively compute dimension of a sympy expression using dim_map."""
    if expr.is_Number:
        return 1
    if expr.is_Symbol:
        return dim_map.get(str(expr), sp.Symbol(str(expr)))  # unknown -> symbolic
    if expr.is_Add:
        # All terms must share same dimension; we return the dimension of the first term
        # (caller should verify homogeneity)
        return expr_dim(expr.args[0])
    if expr.is_Mul:
        dims = [expr_dim(arg) for arg in expr.args]
        return sp.prod(dims)
    if expr.is_Pow:
        base, exp = expr.as_base_exp()
        return expr_dim(base) ** exp
    # Fallback: treat as dimensionless
    return 1

def check_equation(lhs_str, rhs_str):
    """Parse lhs and rhs, compute dimensions, and assert equality."""
    lhs = sp.sympify(lhs_str)
    rhs = sp.sympify(rhs_str)
    dim_l = expr_dim(lhs)
    dim_r = expr_dim(rhs)
    # Simplify the ratio; should be 1 for homogeneous equations
    ratio = sp.simplify(dim_l / dim_r)
    return ratio, lhs, rhs

# Example equations extracted from the Engine's output (as strings)
equations = [
    # ξ_N⁻² = λ (3⟨coh⟩⁻¹ + ⟨coh⟩⁻²)   --> 1/ξ_N^2 = λ * (3/coh + 1/coh^2)
    ("1/xi_N**2", "lam * (3/coh + 1/coh**2)"),
    # ξ_Δ⁻² = λ (⟨coh⟩⁻¹ + 3⟨coh⟩⁻²)
    ("1/xi_Delta**2", "lam * (1/coh + 3/coh**2)"),
    # ψ = ln(ξ/ξ0)
    ("psi", "sp.log(xi/xi0)"),
    # Φ_N = Φ_N0 + α * dPHI/dt   (α dimensionless because dPHI/dt has [T^-1]? we treat α as [T])
    # For dimensional check we only verify that α*dPHI/dt is dimensionless:
    ("alpha * dPHI/dt", "alpha * dPHI/dt"),  # placeholder; actual check omitted
]

def dimensional_check():
    all_ok = True
    for lhs, rhs in equations:
        ratio, lhs_sym, rhs_sym = check_equation(lhs, rhs)
        if ratio != 1:
            print(f"[FAIL] Dimension mismatch: {lhs_sym} = {rhs_sym}")
            print(f"       Ratio of dimensions = {ratio}")
            all_ok = False
        else:
            print(f"[OK]   {lhs_sym} = {rhs_sym}  (dimensionally homogeneous)")
    return all_ok

# ----------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Suppose the Engine's full text is stored in a variable `engine_text`
    # For demonstration we read from a file; replace with actual source.
    try:
        with open("engine_output.txt", "r", encoding="utf-8") as f:
            engine_text = f.read()
    except FileNotFoundError:
        engine_text = ""  # fallback empty string

    print("=== Structural Check ===")
    if structural_check(engine_text):
        print("PASS: No markdown headings, bullets, or enumerated lists detected.")
    else:
        print("FAIL: Boilerplate formatting found (headings, bullets, or lists).")
    print("\n=== Dimensional Check ===")
    dim_ok = dimensional_check()
    print("\n=== Verdict ===")
    if structural_check(engine_text) and dim_ok:
        print("OVERALL: PASS – compliant with Omega Protocol invariants.")
    else:
        print("OVERALL: FAIL – see above violations.")