# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 Compliance Validator
-----------------------------------------
Checks an agent's output for:
  * Absence of boilerplate (numbered steps, bold/italic, bullet/list, markdown headings)
  * Presence of required Omega‑Physics elements:
        - Covariant modes: Φ_N, Φ_Δ
        - Invariants: ψ, ξ_N, ξ_Δ
        - Boundaries: Shredding Event, Informational Freeze
        - Entropy observable: Shannon conditional entropy OR topological impedance
        - Equation‑level detection (a line containing '=' outside of code blocks)
        - Explicit dimensional consistency check phrase
        - Φ‑density impact assessment phrase
Returns a compliance report and a boolean PASS/FAIL.
"""

import re
from typing import Tuple, List

# ----------------------------------------------------------------------
# Patterns that indicate boilerplate (strictly forbidden)
# ----------------------------------------------------------------------
NUMBERED_STEP   = re.compile(r'^\s*\d+\.\s')          # "1. ", "2. " etc.
BOLD_ITALIC     = re.compile(r'(\*\*|__)[^*_]+(\*\*|__)')  # **text** or __text__
BULLET_LIST     = re.compile(r'^\s*[-*+]\s')          # "- ", "* ", "+ "
MARKDOWN_HEAD   = re.compile(r'^\s*#{1,6}\s')         # "# ", "## ", etc.
# Any line that looks like a list item via alphabetic enumeration (a). etc.
ALPHA_ENUM      = re.compile(r'^\s*[a-zA-Z]\.\s')

BOILERPLATE_PATTERNS = [
    NUMBERED_STEP, BOLD_ITALIC, BULLET_LIST,
    MARKDOWN_HEAD, ALPHA_ENUM
]

# ----------------------------------------------------------------------
# Required semantic tokens (case‑insensitive)
# ----------------------------------------------------------------------
REQUIRED_TOKENS = {
    "covariant_modes":   [r'\bΦ_N\b', r'\bΦ_Δ\b'],
    "invariants":        [r'\bψ\b', r'\bξ_N\b', r'\bξ_Δ\b'],
    "boundaries":        [r'Shredding\s+Event', r'Informational\s+Freeze'],
    "entropy":           [r'Shannon\s+conditional\s+entropy', r'topological\s+impedance'],
    "equation":          r'=',  # at least one equals sign not inside a code block
    "dimensional_check": [r'dimensional\s+consistency\s+check',
                          r'unit\s+analysis',
                          r'\[.*\]\s*=\s*\[.*\]'],
    "phi_density":       [r'Φ[-_]density\s+impact',
                          r'Phi\s+density\s+impact',
                          r'phi\s+density\s+impact']
}

def _has_equation_outside_code(text: str) -> bool:
    """
    Very naive check: split by triple backticks and inspect only non‑code chunks.
    Returns True if any '=' appears outside a code block.
    """
    parts = re.split(r'```.*?```', text, flags=re.DOTALL)
    # parts[0], parts[2], ... are non‑code; parts[1], parts[3], ... are code
    for i, chunk in enumerate(parts):
        if i % 2 == 0:  # non‑code
            if '=' in chunk:
                return True
    return False

def _contains_any(patterns: List[str], text: str) -> bool:
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def validate_omega_compliance(output: str) -> Tuple[bool, List[str]]:
    """
    Returns (is_compliant, list_of_violations)
    """
    violations = []

    # 1. Boilerplate check (entire output)
    lines = output.splitlines()
    for idx, line in enumerate(lines, start=1):
        for pattern in BOILERPLATE_PATTERNS:
            if pattern.search(line):
                violations.append(
                    f"Line {idx}: boilerplate detected – '{line.strip()}'"
                )
                break  # avoid multiple messages per line

    # 2. Required semantic tokens
    for category, patterns in REQUIRED_TOKENS.items():
        if category == "equation":
            if not _has_equation_outside_code(output):
                violations.append("Missing equation‑level derivation (no '=' outside code blocks).")
        else:
            if not _contains_any(patterns, output):
                violations.append(
                    f"Missing required {category.replace('_', ' ')} token(s)."
                )

    is_compliant = len(violations) == 0
    return is_compliant, violations

# ----------------------------------------------------------------------
# Example usage (replace with actual agent output)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example: the meta‑scrutiny text from the prompt
    sample_output = r"""
    ### Internal Thought Process for Meta-Scrutiny

    I am performing a meta-scrutiny of the Scrutiny auditor's analysis of the Engine output...
    ... (truncated for brevity) ...

    **Verdict:** NOT META-PASS

    **Detailed Critique:**

    1. **Scrutiny Missed a Subtle Rule Violation:** ...
    2. **No Evidence of Reasoning Poisoning:** ...
    3. **Absolute Rules Not Fully Upheld:** ...

    **Required Actions:**
    - Scrutiny should be refined ...
    - The Engine output must be revised ...

    **Φ-Density Impact Reflection:**
    - Short-term: ...
    - Long-term: ...
    """

    compliant, errs = validate_omega_compliance(sample_output)
    print("Compliant?" , compliant)
    if errs:
        print("Violations:")
        for e in errs:
            print(" -", e)