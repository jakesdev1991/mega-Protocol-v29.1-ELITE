# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Compliance Checker for Agent Smith's audit.
- Detects numbered sections (e.g., "1.", "2)").
- Warns if core invariants Φ_N, Φ_Delta, J* are not mentioned.
- Performs a simple dimensional‑consistency heuristic on LaTeX‑style equations.
"""

import re
import sys

def load_text() -> str:
    """Read the entire stdin as the agent's submitted thought."""
    return sys.stdin.read()

def check_numbered_sections(text: str):
    """Return list of lines that look like numbered sections."""
    lines = text.splitlines()
    pattern = re.compile(r'^\s*\d+[\).]')  # e.g., "1.", "2)"
    violations = [(i+1, line.rstrip()) for i, line in enumerate(lines) if pattern.match(line)]
    return violations

def check_invariants(text: str):
    """Check for explicit mention of the three Omega Protocol invariants."""
    required = [r'Φ_N', r'Φ_Delta', r'J\*']
    missing = [sym for sym in required if not re.search(sym, text)]
    return missing

def extract_latex_equations(text: str):
    """Very naive extraction of $...$ and $$...$$ blocks."""
    # Inline math
    inline = re.findall(r'\$(.*?)\$', text, flags=re.DOTALL)
    # Display math
    display = re.findall(r'\$\$(.*?)\$\$', text, flags=re.DOTALL)
    return inline + display

def dimensional_heuristic(eq: str):
    """
    Simple heuristic: flag if an equation contains both a probability‑density-like
    symbol (e.g., Ψ, ρ, |Ψ|^2) and an energy-like symbol (e.g., E, ΔE, ħω) without
    an explicit constant (ħ, k_B, etc.) that could bridge the dimensions.
    Returns True if likely consistent, False if suspect.
    """
    prob_pattern = re.compile(r'\\Psi|\rho|\\|\\Psi\\|^2|P\\(sub\\)', re.IGNORECASE)
    energy_pattern = re.compile(r'E|\\ΔE|ħ\\s*ω|\\\\hbar\\s*ω|k_B\\s*T', re.IGNORECASE)
    const_pattern = re.compile(r'ħ|\\\\hbar|k_B|\\\\frac', re.IGNORECASE)

    has_prob = bool(prob_pattern.search(eq))
    has_energy = bool(energy_pattern.search(eq))
    has_const = bool(const_pattern.search(eq))

    # If both prob and energy appear, we expect a constant to mediate dimensions.
    if has_prob and has_energy and not has_const:
        return False
    return True

def check_dimensions(text: str):
    """Run dimensional heuristic on all LaTeX equations found."""
    eqs = extract_latex_equations(text)
    bad = []
    for idx, eq in enumerate(eqs, 1):
        if not dimensional_heuristic(eq):
            bad.append((idx, eq.strip()))
    return bad

def main():
    text = load_text()
    violations = []

    # 1. Numbered sections
    numbered = check_numbered_sections(text)
    if numbered:
        violations.append("Numbered sections detected:")
        for lineno, line in numbered:
            violations.append(f"  Line {lineno}: {line}")

    # 2. Missing invariants
    missing = check_invariants(text)
    if missing:
        violations.append(f"Missing Omega Protocol invariants: {', '.join(missing)}")

    # 3. Dimensional sanity
    dim_issues = check_dimensions(text)
    if dim_issues:
        violations.append("Potential dimensional inconsistencies in equations:")
        for idx, eq in dim_issues:
            violations.append(f"  Equation {idx}: {eq}")

    if violations:
        print("Ω PROTOCOL VIOLATION DETECTED:", file=sys.stderr)
        for v in violations:
            print(v, file=sys.stderr)
        sys.exit(1)
    else:
        print("Ω PROTOCOL CHECK PASSED – no obvious violations detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()