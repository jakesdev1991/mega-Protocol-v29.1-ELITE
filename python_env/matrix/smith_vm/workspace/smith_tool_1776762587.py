# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Rubric v26.0 Validator
-------------------------------------
Validates that a given text output satisfies the *structural* requirements
of the rubric (NO BOILERPLATE, presence of required conceptual pillars,
and, if equations are present, dimensional consistency).

Usage:
    python3 omega_validator.py "<text to validate>"
"""

import re
import sys
from typing import List, Tuple

# ----------------------------------------------------------------------
# 1. Conceptual pillars that must be mentioned (case‑insensitive)
# ----------------------------------------------------------------------
REQUIRED_PILLARS: List[str] = [
    r"covariant\s+modes",          # Φ_N and Φ_Δ
    r"invariants",                 # ψ, ξ_N, ξ_Δ
    r"boundaries",                 # Shredding & Informational Freeze
    r"entropy",                    # S_h(t)
    r"equation\s*[- ]level\s+derivation",
    r"dimensional\s+consistency",
    r"\bΦ\s*[- ]density\s+impact\b",
    r"no\s+boilerplate",          # the pillar itself (free‑form narrative)
]

# ----------------------------------------------------------------------
# 2. Patterns that indicate prohibited formatting (boilerplate)
# ----------------------------------------------------------------------
PROHIBITED_PATTERNS: List[Tuple[str, str]] = [
    (r"^\s*#{1,6}\s", "markdown heading"),          # # Heading
    (r"^\s*\d+\.\s", "ordered list"),              # 1. Item
    (r"^\s*[-*]\s", "unordered list"),             # - Item or * Item
    (r"\*\*.*?\*\*", "bold markdown"),             # **bold**
    (r"`{3}.*?`{3}", "code block"),                # ``` ... ```
]

# ----------------------------------------------------------------------
# 3. Helper: simple dimensional analysis (placeholder)
# ----------------------------------------------------------------------
def check_dimensional_consistency(equation_str: str) -> bool:
    """
    Very lightweight dimensional check.
    In a real implementation we would parse symbols with sympy and
    verify that each term shares the same dimensions.
    For this demo we assume the equation is well‑formed if it contains
    an equals sign and at least one alphabetic symbol.
    """
    if "=" not in equation_str:
        return False
    # Ensure there is at least one letter (variable) on each side
    lhs, rhs = equation_str.split("=", 1)
    return bool(re.search(r"[A-Za-z]", lhs)) and bool(re.search(r"[A-Za-z]", rhs))

# ----------------------------------------------------------------------
# 4. Main validation routine
# ----------------------------------------------------------------------
def validate_omega_output(text: str) -> Tuple[bool, List[str]]:
    """
    Returns (is_valid, list_of_issues)
    """
    issues: List[str] = []

    # ---- 4.1 Prohibited formatting (boilerplate) ----
    for pattern, desc in PROHIBITED_PATTERNS:
        if re.search(pattern, text, flags=re.MULTILINE):
            issues.append(f"Prohibited formatting detected: {desc}")

    # ---- 4.2 Required conceptual pillars ----
    lowered = text.lower()
    for pillar in REQUIRED_PILLARS:
        if not re.search(pillar, lowered, flags=re.IGNORECASE):
            issues.append(f"Missing required pillar: '{pillar}'")

    # ---- 4.3 Optional: if equations appear, check dimensions ----
    # Detect potential LaTeX‑like or plain‑text equations.
    eq_candidates = re.findall(r"[^.\n]*=[^.\n]*", text)
    for eq in eq_candidates:
        eq = eq.strip()
        if eq and not check_dimensional_consistency(eq):
            issues.append(f"Dimensional consistency check failed for: '{eq}'")

    return len(issues) == 0, issues

# ----------------------------------------------------------------------
# 5. Command‑line interface
# ----------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 omega_validator.py '<text to validate>'")
        sys.exit(1)

    input_text = sys.argv[1]
    ok, problems = validate_omega_output(input_text)

    if ok:
        print("✅  PASS – Output complies with Omega Protocol rubric (structural checks).")
    else:
        print("❌  FAIL – Structural violations found:")
        for p in problems:
            print(f"   - {p}")
        sys.exit(1)

if __name__ == "__main__":
    main()