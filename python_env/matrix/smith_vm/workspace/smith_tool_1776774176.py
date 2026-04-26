# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Compliance Validator
-----------------------------------
Checks a submitted text (internal thought process + final output) against the
mandatory pillars of the Omega Physics Rubric v26.0:

1. NO BOILERPLATE – no numbered steps, no bold headings.
2. Covariant modes Φ_N and Φ_Δ must be present.
3. Invariants ψ, ξ_N, ξ_Δ must be present.
4. Boundary conditions: Shredding Event (PHI → 0) and Informational Freeze (PHI → 1).
5. Equation‑level rigor – discourage heuristic/empirical language when defining Φ_N/Φ_Δ.

Usage:
    python3 omega_validator.py <input_file>
"""

import sys
import re

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def boilerplate_check(text):
    """Return list of violations."""
    violations = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        # Numbered step like "1 –" or "Step 1"
        if re.match(r'^\s*\d+\s[–-]', line) or re.match(r'^\s*Step\s+\d+', line, re.I):
            violations.append(f"Line {i}: numbered step or explicit sequencing detected.")
        # Bold markdown headings (e.g., **Title:**)
        if re.search(r'\*\*.*?\*\*', line):
            violations.append(f"Line {i}: bold heading/boilerplate markup detected.")
    return violations

def token_present(text, pattern, name):
    """Check if a LaTeX‑style token or plain text appears."""
    # Accept both \Phi_N and Phi_N
    regex = re.compile(r'\\?' + re.escape(pattern), re.I)
    return bool(regex.search(text))

def invariant_check(text):
    missing = []
    for tok, name in [ (r'\\Phi_N', r'\Phi_N'), (r'\\Phi_\Delta', r'\Phi_\Delta') ]:
        if not token_present(text, tok, name):
            missing.append(name)
    for tok, name in [ (r'\\psi', r'\psi'), (r'\\xi_N', r'\xi_N'), (r'\\xi_\Delta', r'\xi_\Delta') ]:
        if not token_present(text, tok, name):
            missing.append(name)
    return missing

def boundary_check(text):
    """Look for explicit shredding/freeze statements."""
    shred = re.search(r'PHI\s*[→->]\s*0|Shredding\s+Event', text, re.I)
    freeze = re.search(r'PHI\s*[→->]\s*1|Informational\s+Freeze', text, re.I)
    missing = []
    if not shred:
        missing.append("Shredding Event (PHI → 0)")
    if not freeze:
        missing.append("Informational Freeze (PHI → 1)")
    return missing

def rigor_check(text):
    """Flag heuristic/empirical language when defining Φ_N or Φ_Δ."""
    warnings = []
    # Look for sentences that contain Phi_N/Phi_Delta and heuristic words
    sentences = re.split(r'[.!?]', text)
    heuristic_words = r'heuristic|empirical|sigmoid|linear terms|ad[- ]hoc'
    for i, sent in enumerate(sentences):
        if re.search(r'\\?Phi[N_]?', sent, re.I) and re.search(heuristic_words, sent, re.I):
            warnings.append(f"Sentence {i+1}: heuristic/empirical language used in Φ_N/Φ_Δ definition.")
    return warnings

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 omega_validator.py <input_file>", file=sys.stderr)
        sys.exit(1)

    text = load_text(sys.argv[1])

    report = []

    # 1. Boilerplate
    boiler = boilerplate_check(text)
    if boiler:
        report.append("Boilerplate violations:")
        report.extend(boiler)

    # 2. Covariant modes
    cov_missing = []
    if not token_present(text, r'\\Phi_N', r'\Phi_N'):
        cov_missing.append(r'\Phi_N')
    if not token_present(text, r'\\Phi_\Delta', r'\Phi_\Delta'):
        cov_missing.append(r'\Phi_\Delta')
    if cov_missing:
        report.append("Missing covariant mode(s): " + ", ".join(cov_missing))

    # 3. Invariants
    inv_missing = invariant_check(text)
    if inv_missing:
        report.append("Missing invariant(s): " + ", ".join(inv_missing))

    # 4. Boundaries
    bound_missing = boundary_check(text)
    if bound_missing:
        report.append("Missing boundary condition(s): " + ", ".join(bound_missing))

    # 5. Equation‑level rigor
    rigor_warn = rigor_check(text)
    if rigor_warn:
        report.append("Rigour warnings (possible heuristic mapping):")
        report.extend(rigor_warn)

    if report:
        print("NON‑COMPLIANT – Omega Protocol violations detected:\n")
        print("\n".join(report))
        sys.exit(1)   # block integration
    else:
        print("COMPLIANT – All Omega Rubric v26.0 checks passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()