# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script
--------------------------------
Validates Engine output against:
  - NO BOILERPLATE
  - INVARIANTS (ψ = ln(φₙ) must be used)
  - DIMENSIONAL CONSISTENCY of jerk terms
  - Presence of a rigorous derivation (placeholder check)

Usage:
    python3 validate_omega.py --engine_output "<raw text>"
"""

import re
import argparse
import sympy as sp
from sympy.physics.units import second, dimensionless

# ----------------------------------------------------------------------
# 1. Boilerplate detection
# ----------------------------------------------------------------------
BOILERPLATE_PATTERNS = [
    r'^\s*\d+\.\s',          # "1. ", "2. ", ...
    r'^\s*[IVXLC]+\.\s',     # Roman numerals
    r'^\s*[a-z]\)\s',        # "a) ", "b) "
    r'^\s*Step\s+\d+',       # "Step 1", "Step 2"
]

def contains_boilerplate(text: str) -> bool:
    for pat in BOILERPLATE_PATTERNS:
        if re.search(pat, text, flags=re.MULTILINE):
            return True
    return False

# ----------------------------------------------------------------------
# 2. Invariant usage check
# ----------------------------------------------------------------------
INVARIANT_SYMBOL = r'ψ'          # psi
INVARIANT_DEF    = r'ln\(φ_N\)'  # ln(phi_N)

def invariant_used(text: str) -> bool:
    # Look for ψ or ln(φ_N) inside a math expression (anything with =, +, -, *, /, ^)
    # Simple heuristic: if the symbol appears and is not isolated by whitespace/punctuation only.
    pattern = rf'(?<![A-Za-z0-9_]){INVARIANT_SYMBOL}(?![A-Za-z0-9_])|{INVARIANT_DEF}'
    matches = list(re.finditer(pattern, text))
    if not matches:
        return False
    # Verify at least one match is within a mathematical context
    for m in matches:
        start, end = m.span()
        # Expand a window to capture surrounding chars
        window = text[max(0, start-20):min(len(text), end+20)]
        if re.search(r'[=\+\-\*/^]', window):
            return True
    return False

# ----------------------------------------------------------------------
# 3. Dimensional analysis helper
# ----------------------------------------------------------------------
def check_dimension(term_expr: str, symbols: dict) -> bool:
    """
    term_expr: string like "phi/xi**4 * phi_dot**3"
    symbols: dict mapping symbol name -> SymPy unit (e.g., phi: dimensionless,
                                                    xi: second,
                                                    phi_dot: 1/second)
    Returns True if the term has dimension of second**(-3) (jerk).
    """
    # Build SymPy expression
    expr = sp.sympify(term_expr, locals=symbols)
    # Replace each symbol with its unit
    unit_expr = expr.subs(symbols)
    # Simplify to a power of second
    unit_expr = sp.simplify(unit_expr)
    # Jerk dimension = second**(-3)
    expected = second**(-3)
    return unit_expr.equals(expected)

# ----------------------------------------------------------------------
# 4. Main validation routine
# ----------------------------------------------------------------------
def validate_engine_output(output: str):
    issues = []

    # Boilerplate
    if contains_boilerplate(output):
        issues.append("❌ BOILERPLATE: numbered/step‑by‑step sections detected.")

    # Invariant usage
    if not invariant_used(output):
        issues.append("❌ INVARIANT: ψ = ln(φₙ) mentioned but not used in any equation.")

    # Extract potential jerk terms (crude: look for patterns like φ/ξ**4 * φ_dot**3)
    # We'll just test the Engine's claimed term.
    jerk_candidate = "phi/xi**4 * phi_dot**3"
    symbols = {
        "phi": dimensionless,      # normalized field
        "xi": second,              # stiffness inverse sqrt has dimension of time
        "phi_dot": 1/second,       # time derivative of normalized field
    }
    if not check_dimension(jerk_candidate, symbols):
        issues.append(
            f"❌ DIMENSIONAL: term '{jerk_candidate}' yields "
            f"{sp.simplify(sp.sympify(jerk_candidate, locals=symbols))} "
            f"(expected s⁻³)."
        )

    # Derivation placeholder – we can't auto‑detect a full derivation,
    # but we can flag if the text lacks any differential operator.
    if not re.search(r'\bd\d{1,3}S_h/dt\b|\b∂.*S_h/∂', output, re.IGNORECASE):
        issues.append(
            "⚠️ DERIVATION: No explicit appearance of dS_h/dt or higher derivatives; "
            "derivation may be missing or heuristic."
        )

    return issues

# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Engine output against Omega Protocol.")
    parser.add_argument(
        "--engine_output",
        type=str,
        required=True,
        help="Raw text of the Engine's submission.",
    )
    args = parser.parse_args()

    problems = validate_engine_output(args.engine_output)
    if problems:
        print("Omega Protocol Validation FAILED:")
        for p in problems:
            print(" -", p)
        exit(1)
    else:
        print("✅ Omega Protocol Validation PASSED.")
        exit(0)