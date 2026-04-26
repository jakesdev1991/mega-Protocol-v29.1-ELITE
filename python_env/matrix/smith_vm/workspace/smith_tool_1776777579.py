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
Checks the agent's final output for:
 1. Absence of numbered/boiler‑plate sections (no leading numbers or markdown headings).
 2. Presence of required dimensional annotations:
      - COD described as dimensionless.
      - Impedance Z carrying units [I]·[T]⁻¹.
 3. Basic LaTeX‑like math sanity (balanced $, \(, \[, \) and \]).
Usage: pipe the agent's response into stdin or pass as first argument.
"""

import sys
import re

def read_input():
    if len(sys.argv) > 1:
        with open(sys.argv[0], 'r', encoding='utf-8') as f:
            return f.read()
    return sys.stdin.read()

def has_numbered_section(text: str) -> bool:
    """
    Detects lines that start with a number followed by a period, parenthesis,
    or a markdown heading (###, ##, #). Any of these are treated as boilerplate.
    """
    lines = text.splitlines()
    for ln in lines:
        stripped = ln.lstrip()
        # markdown heading
        if re.match(r'^#{1,6}\s', stripped):
            return True
        # numbered list like "1.", "2)", "3. ", etc.
        if re.match(r'^\d+[.)]\s', stripped):
            return True
    return False

def check_dimension_annotations(text: str) -> tuple[bool, list]:
    """
    Returns (ok, messages). Checks for required unit phrases.
    """
    msgs = []
    # COD dimensionless
    if not re.search(r'\bCOD\b.*\bdimensional\w*\s*less\b', text, re.I):
        msgs.append("Missing explicit statement that COD is dimensionless.")
    # Impedance units [I]·[T]⁻¹ (allow variations)
    impedance_pattern = r'\[I\]\s*[\·\*]?\s*\[T\]\s*\^\s*-\s*1'
    if not re.search(impedance_pattern, text, re.I):
        msgs.append("Impedance Z not annotated with units [I]·[T]⁻¹.")
    return (len(msgs) == 0, msgs)

def latex_balanced(text: str) -> bool:
    """
    Very light check: ensures $, \(, \[ are closed.
    Does not validate full LaTeX, just catches obvious mismatches.
    """
    stack = []
    pairs = {'$': '$', r'\(': r'\)', r'\[': r'\]'}
    opening = set(pairs.keys())
    closing = set(pairs.values())
    i = 0
    while i < len(text):
        ch = text[i]
        # handle multi‑char opening tokens
        if text[i:i+2] in opening:
            stack.append(pairs[text[i:i+2]])
            i += 2
            continue
        if ch in opening:
            stack.append(pairs[ch])
            i += 1
            continue
        if ch in closing:
            if not stack or stack.pop() != ch:
                return False
            i += 1
            continue
        i += 1
    return not stack

def main():
    txt = read_input()
    if not txt.strip():
        print("ERROR: Empty input.", file=sys.stderr)
        sys.exit(1)

    failures = []

    if has_numbered_section(txt):
        failures.append("Boilerplate/numbered section detected.")

    dim_ok, dim_msgs = check_dimension_annotations(txt)
    if not dim_ok:
        failures.extend(dim_msgs)

    if not latex_balanced(txt):
        failures.append("Unbalanced LaTeX‑like delimiters found.")

    if failures:
        print("VALIDATION FAILED:", file=sys.stderr)
        for f in failures:
            print(f" - {f}", file=sys.stderr)
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()