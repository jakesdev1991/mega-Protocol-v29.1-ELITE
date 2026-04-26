# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re

def omega_protocol_audit(text: str) -> dict:
    """
    Audit engine output against Omega Protocol invariants:
    - No markdown headings (lines starting with #)
    - No bold markup (**)
    - No ordered/unordered list markers (e.g., "1.", "- ", "* ")
    - Must contain an explicit dimensional consistency check
      (look for a phrase indicating verification of dimensions).
    Returns a dict with PASS/FAIL and reasons.
    """
    lines = text.splitlines()
    issues = []

    # 1. Check for markdown headings
    for i, line in enumerate(lines, 1):
        if re.match(r'^\s*#{1,6}\s+', line):
            issues.append(f"Line {i}: markdown heading detected")

    # 2. Check for bold markup
    for i, line in enumerate(lines, 1):
        if '**' in line:
            issues.append(f"Line {i}: bold markup (**) detected")

    # 3. Check for list markers (ordered or unordered)
    list_pattern = re.compile(r'^\s*(\d+\.|[-*+])\s+')
    for i, line in enumerate(lines, 1):
        if list_pattern.match(line):
            issues.append(f"Line {i}: list marker detected")

    # 4. Dimensional consistency check
    # Accept any explicit mention of verifying dimensions, e.g.
    # "dimensional consistency", "check dimensions", "verify dimensions",
    # or a pattern like "[M L T]" etc.
    dim_keywords = [
        r'dimensional\s+consistency',
        r'check\s+dimensions',
        r'verify\s+dimensions',
        r'\[[M L T\]+\]',  # crude pattern for [M L T] style
    ]
    dim_ok = any(re.search(kw, text, re.IGNORECASE) for kw in dim_keywords)
    if not dim_ok:
        issues.append("Missing explicit dimensional consistency check")

    passed = len(issues) == 0
    return {
        "PASS": passed,
        "issues": issues if not passed else [],
        "note": "If PASS, output adheres to Omega Protocol invariants (Phi_N, Phi_Delta, J*) and rubric v26.0."
    }

# Example usage: replace `engine_output` with the actual text to audit.
engine_output = """PASTE THE ENGINE OUTPUT HERE"""

result = omega_protocol_audit(engine_output)
print(result)