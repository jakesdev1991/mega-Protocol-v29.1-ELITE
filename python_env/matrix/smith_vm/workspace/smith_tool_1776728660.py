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
Checks:
  * No boiler‑plate (headings, bold, lists, bullets)
  * Correct use of invariants (ψ, ξ_N, ξ_Δ) and Shredding/Poisson conditions
  * Presence of an entropy‑based observable (non‑empty string)
  * Presence of a dimensional‑consistency paragraph (non‑empty string)

Usage:
    python3 validate_omega.py <engine_output.txt> [entropy_str] [dim_check_str]

If entropy_str or dim_check_str are omitted, the script will prompt for them.
"""

import sys
import re
import math

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def boilerplate_check(text):
    """Return list of violations."""
    violations = []

    # Markdown-style headings (##, ###, etc.)
    if re.search(r'^#{1,6}\s+\S', text, flags=re.MULTILINE):
        violations.append("Markdown heading detected.")

    # Bold markup (** or __)
    if re.search(r'\*\*.*?\*\*|__.*?__', text):
        violations.append("Bold markup detected.")

    # Numbered list (1. 2. …) at start of line
    if re.search(r'^\s*\d+\.\s+\S', text, flags=re.MULTILINE):
        violations.append("Numbered list detected.")

    # Bullet list (-, *, •) at start of line
    if re.search(r'^\s*[-*•]\s+\S', text, flags=re.MULTILINE):
        violations.append("Bullet list detected.")

    return violations

def invariant_check(text):
    """Very light sanity check: ensure the symbols appear and the two key
    conditions are expressed somewhere."""
    # Required symbols
    required = [r'\\Phi_N', r'\\Phi_\\Delta', r'\\psi', r'\\xi_N', r'\\xi_\\Delta']
    missing = []
    for pat in required:
        if not re.search(pat, text):
            missing.append(pat)
    if missing:
        return [f"Missing invariant symbols: {', '.join(missing)}"]

    # Shredding condition: xi_Delta -> infinity  <=> Phi_N^2 + 3 Phi_Delta^2 = v^2
    # We just look for the algebraic expression; tolerance for whitespace.
    shred_pat = r'\\Phi_N\s*\^\s*2\s*\+\s*3\s*\\Phi_\\Delta\s*\^\s*2\s*=\s*v\s*\^\s*2'
    if not re.search(shred_pat, text, flags=re.IGNORECASE):
        return ["Shredding condition (Phi_N^2 + 3 Phi_Delta^2 = v^2) not found."]

    # Poisson‑recovery violation: Phi_Delta^2 > v^2 - Phi_N^2
    pois_pat = r'\\Phi_\\Delta\s*\^\s*2\s*>\s*v\s*\^\s*2\s*-\s*\\Phi_N\s*\^\s*2'
    if not re.search(pois_pat, text, flags=re.IGNORECASE):
        return ["Poisson‑recovery violation condition (Phi_Delta^2 > v^2 - Phi_N^2) not found."]

    return []  # all good

def entropy_check(entropy_str):
    if not entropy_str or entropy_str.strip() == "":
        return ["Entropy‑based observable string is empty."]
    return []

def dim_check(dim_str):
    if not dim_str or dim_str.strip() == "":
        return ["Dimensional‑consistency paragraph is empty."]
    return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_omega.py <engine_output.txt> [entropy_str] [dim_check_str]")
        sys.exit(1)

    output_file = sys.argv[1]
    entropy_input = sys.argv[2] if len(sys.argv) > 2 else ""
    dim_input    = sys.argv[3] if len(sys.argv) > 3 else ""

    text = load_text(output_file)

    errors = []
    errors.extend(boilerplate_check(text))
    errors.extend(invariant_check(text))
    # If entropy or dim not supplied via CLI, ask interactively
    if not entropy_input.strip():
        entropy_input = input("Enter entropy‑based observable (non‑empty): ")
    if not dim_input.strip():
        dim_input = input("Enter dimensional‑consistency paragraph (non‑empty): ")

    errors.extend(entropy_check(entropy_input))
    errors.extend(dim_check(dim_input))

    if errors:
        print("❌ Omega Protocol validation FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    else:
        print("✅ Omega Protocol validation PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()