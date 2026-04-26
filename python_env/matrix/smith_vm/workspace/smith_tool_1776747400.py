# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Rubric Validator for the ETO‑Ω proposal.
Run: python3 validate_eto.py <proposal_file>
"""

import sys
import re
from pathlib import Path

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def check_boilerplate(text: str) -> list:
    """Return list of violations (line numbers, snippet)."""
    violations = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        # numbered headings like "1. ", "2. "
        if re.match(r'^\d+\.\s+', stripped):
            violations.append((i, line))
        # markdown bold headings ** ... **
        if re.match(r'^\*\*.*\*\*$', stripped):
            violations.append((i, line))
        # also catch headings that start with a number and a dot after bold
        if re.match(r'^\*\*\d+\.\s+', stripped):
            violations.append((i, line))
    return violations

def extract_equations(text: str) -> list:
    """Return a list of LaTeX/math snippets found in $...$ or \\(...\\)."""
    pattern = r'(?:\$\$?|\\\().*?(?:\$\$?|\\\))'
    return re.findall(pattern, text, flags=re.DOTALL)

def invariants_in_equations(equations: list) -> dict:
    """Check which invariants appear inside any equation snippet."""
    invars = [r'\\Phi_N', r'\\Phi_\Delta', r'\\psi', r'\\xi_N', r'\\xi_\Delta']
    found = {ivar: False for ivar in invars}
    for eq in equations:
        for ivar in invars:
            if re.search(ivar, eq):
                found[ivar] = True
    return found

def check_required_phrases(text: str) -> dict:
    """Look for key conceptual markers."""
    markers = {
        "Shredding Event": r'Shredding\s+Event',
        "Informational Freeze": r'Informational\s+Freeze',
        "topological entanglement entropy": r'topological\s+entanglement\s+entropy',
        "effective Hamiltonian": r'effective\s+Hamiltonian',
        "gap.*function": r'\\Delta\s*=\s*.*\\xi_N.*\\xi_\Delta',
        "logical operators": r'\\bar[XZ]\\s*\\equiv\s*\\Phi_[NΔ]',
    }
    result = {}
    for name, pat in markers.items():
        result[name] = bool(re.search(pat, text, flags=re.IGNORECASE))
    return result

def dimensional_check_present(text: str) -> bool:
    """Very loose check for an explicit dimensional‑consistency statement."""
    return bool(re.search(r'dimensional\s+check|dimensionally\s+consistent',
                          text, flags=re.IGNORECASE))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_eto.py <proposal_file>")
        sys.exit(1)

    proposal_path = Path(sys.argv[1])
    text = load_text(proposal_path)

    # 1. Boilerplate check
    boilerplate_violations = check_boilerplate(text)
    # 2. Equations and invariants
    equations = extract_equations(text)
    invars_found = invariants_in_equations(equations)
    # 3. Required phrases
    phrases = check_required_phrases(text)
    # 4. Dimensional check
    dim_ok = dimensional_check_present(text)

    # Reporting
    print("=== Omega Protocol Rubric Validation ===\n")
    if boilerplate_violations:
        print("❌ BOILERPLATE VIOLATIONS (lines):")
        for ln, snippet in boilerplate_violations:
            print(f"   {ln:4}: {snippet}")
    else:
        print("✅ No boilerplate (numbered headings / bold section titles) detected.")

    print("\n--- Invariant Presence in Equations ---")
    for invar, present in invars_found.items():
        status = "✅" if present else "❌"
        print(f"   {status} {invar.lstrip('\\\\')}")

    print("\n--- Required Conceptual Markers ---")
    for name, present in phrases.items():
        status = "✅" if present else "❌"
        print(f"   {status} {name}")

    print("\n--- Dimensional Consistency Check ---")
    if dim_ok:
        print("✅ Explicit dimensional‑consistency statement found.")
    else:
        print("❌ No explicit dimensional‑consistency check detected.")
        print("    Suggestion: add a short paragraph verifying that [H_eff]=energy,")
        print("    [Δ]=energy, [Φ_N,Φ_Δ]=dimensionless, [ξ_N,ξ_Δ]=length, etc.")

    print("\n=== Summary ===")
    all_good = (not boilerplate_violations and
                all(invars_found.values()) and
                all(phrases.values()) and
                dim_ok)
    if all_good:
        print("🟢 Proposal passes the Omega Protocol Rubric (v26.0).")
        sys.exit(0)
    else:
        print("🔴 Proposal fails one or more rubric requirements.")
        sys.exit(1)

if __name__ == "__main__":
    main()