# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 compliance checker.
Checks a given text for:
  * NO BOILERPLATE (no markdown headings, no bold, no numbered/bullet lists)
  * Presence of required technical terms and symbols
  * Explicit equation-level derivation (look for action integral and potential)
  * Both boundary conditions (Shredding Event & Informational Freeze)
  * Dimensional consistency check (mention of units for key quantities)
  * Quantified Φ-density impact (short‑term % cost and long‑term % gain)
Returns a compliance report and a boolean PASS/FAIL.
"""

import re
import sys

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def check_boilerplate(text):
    """Return list of boilerplate violations."""
    violations = []
    # Markdown headings
    if re.search(r'^#{1,6}\s+.+', text, flags=re.MULTILINE):
        violations.append("Markdown heading detected")
    # Bold markup
    if re.search(r'\*\*.*?\*\*', text):
        violations.append("Bold markup (**) detected")
    # Numbered list (e.g., "1. ")
    if re.search(r'(^|\n)\s*\d+\.\s+', text):
        violations.append("Numbered list detected")
    # Bullet list (e.g., "- " or "* ")
    if re.search(r'(^|\n)\s*[-*]\s+', text):
        violations.append("Bullet list detected")
    return violations

def check_required_terms(text):
    terms = [
        r'\\?Phi_N', r'\\?Phi_\\Delta',   # covariant modes
        r'\\?psi', r'\\?xi_N', r'\\?xi_\\Delta',  # invariants
        r'S_h', r'\\mathcal{S}', r'\\mathcal{J}_I',  # observables
        r'V\\(I\\)', r'\\lambda', r'I_0',  # action/potential
        r'Shredding', r'Informational Freeze',  # boundaries
        r'dimensional', r'unit', r'[\\[][^]]*[\\]]',  # placeholder for unit check
        r'Phi density', r'\\%'
    ]
    missing = []
    for pat in terms:
        if not re.search(pat, text, flags=re.IGNORECASE):
            missing.append(pat)
    return missing

def check_derivation(text):
    """Look for an action integral and potential definition."""
    has_action = re.search(r'\\mathcal\\s*\\[\\s*I\\s*\\]', text) or \
                 re.search(r'\\\\mathcal\s*\\\\S\s*=\\\\s*\\\\int', text, re.IGNORECASE)
    has_potential = re.search(r'V\s*\(\s*I\s*\)', text, re.IGNORECASE) or \
                    re.search(r'\\\\lambda/4\\s*\(I\^2-I_0\^2\)\^2', text)
    return bool(has_action and has_potential)

def check_boundaries(text):
    shred = re.search(r'xi_\\Delta\s*->\s*\\\\?infty|Phi_N\^2\s*\+\s*3*Phi_\\Delta\^2\s*=\s*I_0\^2', text, re.IGNORECASE)
    freeze = re.search(r'xi_N\s*->\s*\\\\?infty|3*Phi_N\^2\s*\+\s*Phi_\\Delta\^2\s*=\s*I_0\^2', text, re.IGNORECASE)
    return bool(shred and freeze)

def check_dimensions(text):
    # Very loose check: look for any mention of seconds, s^-1, s^-2, s^-3, s^-6 etc.
    dim_patterns = [r'\[?s\]?\^-?[0-9]', r'second', r'sec', r'[Tt]ime']
    return any(re.search(p, text, flags=re.IGNORECASE) for p in dim_patterns)

def check_phi_density_impact(text):
    # Look for a number followed by % or a phrase like "X-%" or "X percent"
    short = re.search(r'(\d+\.?\d*)\s*%\s*(cost|dip|reduction|loss)', text, re.IGNORECASE)
    long  = re.search(r'(\d+\.?\d*)\s*%\s*(gain|increase|benefit|improvement)', text, re.IGNORECASE)
    return bool(short and long)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 omega_check.py <path-to-text>")
        sys.exit(1)
    text = load_text(sys.argv[1])
    report = []

    # Boilerplate
    bp = check_boilerplate(text)
    if bp:
        report.append("FAIL - Boilerplate violations: " + "; ".join(bp))
    else:
        report.append("PASS - No boilerplate detected")

    # Required terms
    missing = check_required_terms(text)
    if missing:
        report.append("FAIL - Missing required terms/symbols: " + ", ".join(missing[:10]))
    else:
        report.append("PASS - All required terms present")

    # Derivation
    if check_derivation(text):
        report.append("PASS - Equation-level derivation (action + potential) found")
    else:
        report.append("FAIL - No explicit action integral / potential definition found")

    # Boundaries
    if check_boundaries(text):
        report.append("PASS - Both Shredding Event and Informational Freeze conditions present")
    else:
        report.append("FAIL - Missing one or both boundary conditions")

    # Dimensional consistency
    if check_dimensions(text):
        report.append("PASS - Dimensional consistency check detected")
    else:
        report.append("FAIL - No dimensional analysis found")

    # Φ-density impact
    if check_phi_density_impact(text):
        report.append("PASS - Quantified short‑term and long‑term Φ‑density impact present")
    else:
        report.append("FAIL - Missing quantified Φ‑density impact")

    overall = "PASS" if all(r.startswith("PASS") for r in report) else "FAIL"
    print("\n".join(report))
    print(f"\nOVERALL VERDICT: {overall}")

if __name__ == "__main__":
    main()