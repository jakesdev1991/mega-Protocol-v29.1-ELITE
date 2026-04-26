# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol compliance checker for the agent's final output.
Run: python3 check_compliance.py <input_text_file>
"""

import re
import sys

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def check_numbered_sections(text):
    """Return False if any line looks like a numbered list item."""
    pattern = re.compile(r'^\s*\d+\.\s')   # line starts with optional whitespace, digits, dot, space
    for i, line in enumerate(text.splitlines(), 1):
        if pattern.match(line):
            return False, f"Line {i} appears to be a numbered list item: '{line.strip()}'"
    return True, ""

def check_psi_in_eom(text):
    """Check that ψ appears in a line that looks like an equation of motion."""
    # Very loose heuristic: line contains a derivative symbol (∂_μ) or the word "EOM"
    eom_pattern = re.compile(r'(∂_μ|EOM|equation of motion)', re.IGNORECASE)
    psi_pattern = re.compile(r'[ψΨ]')   # Greek psi or capital Psi (sometimes used)
    for i, line in enumerate(text.splitlines(), 1):
        if eom_pattern.search(line) and psi_pattern.search(line):
            return True, ""
    return False, "No line containing both a derivative/EOM marker and the invariant ψ was found."

def check_cod_defined_via_integral(text):
    """Check that COD is defined using an integral overlap."""
    # Look for \int ... |Ψ_S† Ψ_C|^2 ... \int ... |Ψ_S|^2 ... \int ... |Ψ_C|^2
    int_pattern = re.compile(r'\\int')
    # We simply require at least three integral symbols and the overlap pattern.
    if len(int_pattern.findall(text)) < 3:
        return False, "Fewer than three integral symbols found; COD likely not expressed as overlap ratio."
    overlap_pattern = re.compile(r'\\|\s*\\Psi_S^\dagger\s*\\Psi_C\s*\\|')  # |Ψ_S† Ψ_C|
    if not overlap_pattern.search(text):
        return False, "Overlap integral |Ψ_S† Ψ_C| not detected."
    return True, ""

def check_forbidden_boilerplate(text):
    """Disallow typical non‑compliant filler phrases."""
    forbidden = [
        r'Nominal invariant usage',
        r'Heuristic derivations',
        r'boilerplate sections',
        r'Numbered sections',
    ]
    for pat in forbidden:
        if re.search(pat, text, re.IGNORECASE):
            return False, f"Forbidden phrase detected: '{pat}'"
    return True, ""

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 check_compliance.py <path_to_final_output.txt>")
        sys.exit(1)

    text = load_text(sys.argv[1])

    checks = [
        ("Numbered sections", check_numbered_sections),
        ("ψ in EOM", check_psi_in_eom),
        ("COD via integral overlap", check_cod_defined_via_integral),
        ("Forbidden boilerplate", check_forbidden_boilerplate),
    ]

    all_ok = True
    for name, func in checks:
        ok, msg = func(text)
        if not ok:
            print(f"[FAIL] {name}: {msg}")
            all_ok = False
        else:
            print(f"[PASS] {name}")

    if all_ok:
        print("\nOverall: The text passes the objectively verifiable Omega Protocol checks.")
    else:
        print("\nOverall: The text fails one or more compliance checks.")
        sys.exit(1)

if __name__ == "__main__":
    main()