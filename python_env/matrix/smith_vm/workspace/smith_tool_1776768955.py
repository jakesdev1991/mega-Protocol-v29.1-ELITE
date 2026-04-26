# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Rubric v26.0 Compliance Checker for NCSM-Ω Proposals
"""

import re
import sys

def load_proposal(text: str) -> str:
    """Return the proposal text (could be read from a file)."""
    return text

def has_boilerplate(text: str) -> bool:
    """Detect markdown headings (###, ##, #) as boilerplate."""
    # Match lines that start with optional whitespace followed by one or more '#'
    pattern = re r'^\s*#+.*$'
    return bool(re.search(pattern, text, flags=re.MULTILINE))

def extract_symbols(text: str):
    """Return a set of required symbols found in the text."""
    required = {
        r'Φ_N', r'Φ_Δ', r'ψ', r'ξ_N', r'ξ_Δ',
        r'S', r'NCI', r'R'   # entropy S, narrative coherence index, scalar curvature
    }
    found = set()
    for sym in required:
        if re.search(sym, text):
            found.add(sym)
    return found, required - found

def dimension_comment_check(text: str) -> bool:
    """
    Very lightweight check: whenever we see a second‑derivative of V_eff
    w.r.t. a field, we expect a nearby comment containing '[dim]' or similar.
    This is optional but helps catch missing dimensional annotations.
    """
    # Pattern for second derivative terms
    deriv_pat = re.compile(r'∂^2\s*V_eff\s*/\s*∂[ΦΦ_]_?[NΔ]?\s*^2')
    # Look for a comment after the term on the same line or next line
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if deriv_pat.search(line):
            # Check this line and the next for a dimension hint
            window = ' '.join(lines[i:i+2])
            if not re.search(r'\[dim\]|\(dim\)|dimension', window, flags=re.I):
                return False
    return True

def main():
    # In practice, read from stdin or a file; here we expect the proposal as argv[1]
    if len(sys.argv) < 2:
        print("Usage: python3 omega_check.py <proposal_text_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        proposal = f.read()

    failures = []

    if has_boilerplate(proposal):
        failures.append("Boilerplate detected: markdown headings present (violates NO BOILERPLATE).")

    found, missing = extract_symbols(proposal)
    if missing:
        failures.append(f"Missing required symbols: {', '.join(sorted(missing))}")

    if not dimension_comment_check(proposal):
        failures.append("Potential dimensional annotation missing for V_eff second derivatives.")

    if failures:
        print("FAIL – Omega Protocol Rubric v26.0 compliance issues:")
        for f in failures:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("PASS – Proposal satisfies all checked rubric pillars.")
        sys.exit(0)

if __name__ == "__main__":
    main()