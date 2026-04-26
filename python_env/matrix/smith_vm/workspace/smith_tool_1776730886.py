# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol compliance checker for Informational Jerk stability analyses.
Usage: python3 omega_check.py <solution_text_file>
"""

import sys
import re
import sympy as sp

# ----------------------------------------------------------------------
# 1. Boilerplate detection (numbered sections)
# ----------------------------------------------------------------------
BOILERPLATE_PATTERN = re.compile(r'^\s*\d+\.\s+', re.MULTILINE)

def has_boilerplate(text: str) -> bool:
    return bool(BOILERPLATE_PATTERN.search(text))

# ----------------------------------------------------------------------
# 2. Invariant ψ = ln(phi_N) detection
# ----------------------------------------------------------------------
INVARIANT_PATTERNS = [
    r'\\psi\s*=',          # LaTeX \psi =
    r'psi\s*=',            # plain text psi =
    r'ln\s*\(\s*phi_N\s*\)', # ln(phi_N)
    r'log\s*\(\s*phi_N\s*\)' # log(phi_N) (natural log assumed)
]

def has_invariant(text: str) -> bool:
    lower = text.lower()
    for pat in INVARIANT_PATTERNS:
        if re.search(pat, lower):
            return True
    return False

# ----------------------------------------------------------------------
# 3. Dimensional consistency check
# ----------------------------------------------------------------------
def extract_jexpr(text: str):
    """
    Very naive extraction: look for 'J_stab =' and take everything up to
    the next period or newline that is not part of a fraction.
    """
    m = re.search(r'J_stab\s*=\s*([^.]+)', text, re.IGNORECASE)
    if not m:
        return None
    expr = m.group(1).strip()
    # Remove trailing spaces and possible trailing comment
    expr = expr.split('\n')[0].strip()
    return expr

def check_dimensions(text: str) -> bool:
    expr_str = extract_jexpr(text)
    if expr_str is None:
        print("[DIM] No J_stab expression found.")
        return False

    # Define symbols
    phiN, phiD = sp.symbols('phiN phiD', positive=True)   # dimensionless
    xiN, xiD = sp.symbols('xiN xiD')                       # [T]
    dphiN, dphiD = sp.symbols('dphiN dphiD')               # [T]^{-1}
    Jsrc = sp.symbols('Jsrc')                              # [T]^{-3}

    # Substitution rules for dimensions
    dim_subs = {
        phiN: 1, phiD: 1,
        xiN: sp.Symbol('T'), xiD: sp.Symbol('T'),
        dphiN: sp.Symbol('T')**-1, dphiD: sp.Symbol('T')**-1,
        Jsrc: sp.Symbol('T')**-3
    }

    try:
        expr = sp.sympify(expr_str)
    except sp.SympifyError:
        print(f"[DIM] Could not parse expression: {expr_str}")
        return False

    dim_expr = expr.subs(dim_subs)
    # Simplify to see if we get T^{-3}
    dim_simplified = sp.simplify(dim_expr)
    # Expected dimension: T^{-3}
    expected = sp.Symbol('T')**-3

    if sp.simplify(dim_simplified / expected) == 1:
        return True
    else:
        print(f"[DIM] Dimension check failed.")
        print(f"  Expression: {expr}")
        print(f"  Dimensions after substitution: {dim_simplified}")
        print(f"  Expected: {expected}")
        return False

# ----------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 omega_check.py <solution_text_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()

    violations = []

    if has_boilerplate(text):
        violations.append("BOILERPLATE: numbered sections detected.")
    if not has_invariant(text):
        violations.append("INVARIANT: missing ψ = ln(φ_N).")
    if not check_dimensions(text):
        violations.append("DIMENSIONAL: J_stab expression not [T]^{-3}.")

    if violations:
        print("Omega Protocol compliance FAILED:")
        for v in violations:
            print(f" - {v}")
        sys.exit(1)
    else:
        print("Omega Protocol compliance PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()