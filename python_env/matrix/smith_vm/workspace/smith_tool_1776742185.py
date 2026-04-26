# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Rubric v26.0 compliance checker.
- Enforces NO BOILERPLATE (no markdown headings, no explicit lists).
- Verifies presence of required technical tokens.
- Performs a lightweight dimensional‑consistency sanity check.
"""

import re
import sys

def load_proposal(source: str) -> str:
    """Read proposal text from a file or treat the argument as raw text."""
    try:
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    except OSError:
        # Assume the argument is already the raw text
        return source

def check_no_boilerplate(text: str) -> tuple[bool, list[str]]:
    """Return (pass, violations) where violations are offending lines."""
    lines = text.splitlines()
    violations = []
    for i, line in enumerate(lines, start=1):
        # Markdown headings (###, ##, #) – adjust pattern if other forms are forbidden
        if re.match(r'^\s*#{1,6}\s+', line):
            violations.append(f"Line {i}: markdown heading detected → '{line.rstrip()}'")
        # Optional: forbid explicit bullet/numbered lists at start of line
        if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            violations.append(f"Line {i}: list-like bullet/number detected → '{line.rstrip()}'")
    return (len(violations) == 0, violations)

def check_required_tokens(text: str) -> tuple[bool, list[str]]:
    """Ensure key Rubric elements appear somewhere in the text."""
    required = [
        r'Φ_N', r'Φ_Δ',                # covariant modes
        r'ψ', r'ξ_N', r'ξ_Δ',          # invariants
        r'Shannon\s+entropy',          # entropy‑based observable
        r'S\[I\]', r'action',          # Omega Action reference
        r'V\(I\)', r'potential',       # potential term
        r'⟨coh⟩', r'coherence',        # coherence observable
        r'PHI', r'Pipeline\s+Health\s+Index',  # PHI definition
        r'Shredding\s+Event', r'Informational\s+Freeze',  # boundaries
        r'Φ‑density', r'Φ\s+density', # impact assessment
    ]
    missing = []
    for pat in required:
        if not re.search(pat, text, flags=re.IGNORECASE):
            missing.append(pat)
    return (len(missing) == 0, missing)

def dimensional_sanity(text: str) -> tuple[bool, list[str]]:
    """
    Very light check: look for the defining equations of the stiffness invariants.
    We expect something like:
        ξ_N⁻² = λ * (3⟨coh⟩⁻¹ + ⟨coh⟩⁻²)
        ξ_Δ⁻² = λ * (⟨coh⟩⁻¹ + 3⟨coh⟩⁻²)
    The regex tolerates spaces and alternative unicode for minus/superscript.
    """
    # Normalise common variants
    norm = text.replace('⁻²', '^-2').replace('⁻¹', '^-1')
    # Patterns allowing optional * or spaces
    patterns = [
        r'ξ_N\s*^-2\s*=\s*λ\s*\*\s*\(\s*3\s*⟨coh⟩\s*^-1\s*\+\s*⟨coh⟩\s*^-2\s*\)',
        r'ξ_Δ\s*^-2\s*=\s*λ\s*\*\s*\(\s*⟨coh⟩\s*^-1\s*\+\s*3\s*⟨coh⟩\s*^-2\s*\)',
    ]
    fails = []
    for i, pat in enumerate(patterns, start=1):
        if not re.search(pat, norm, flags=re.IGNORECASE):
            fails.append(f"Stiffness invariant {i} pattern not found: '{pat}'")
    return (len(fails) == 0, fails)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 omega_check.py <proposal_file_or_text>")
        sys.exit(1)

    source = sys.argv[1]
    proposal = load_proposal(source)

    # 1. BOILERPLATE check
    boilerplate_ok, boilerplate_errs = check_no_boilerplate(proposal)
    # 2. REQUIRED TOKENS check
    tokens_ok, missing = check_required_tokens(proposal)
    # 3. DIMENSIONAL SANITY check
    dim_ok, dim_errs = dimensional_sanity(proposal)

    all_ok = boilerplate_ok and tokens_ok and dim_ok

    print("=== Omega Protocol Rubric v26.0 Compliance Report ===")
    print(f"No boilerplate (headings/lists)          : {'PASS' if boilerplate_ok else 'FAIL'}")
    if not boilerplate_ok:
        print("  Violations:")
        for v in boilerplate_errs:
            print(f"   - {v}")
    print(f"Required technical tokens present          : {'PASS' if tokens_ok else 'FAIL'}")
    if not tokens_ok:
        print("  Missing tokens:")
        for m in missing:
            print(f"   - {m}")
    print(f"Dimensional sanity (stiffness invariants) : {'PASS' if dim_ok else 'FAIL'}")
    if not dim_ok:
        print("  Issues:")
        for e in dim_errs:
            print(f"   - {e}")
    print(f"Overall verdict                            : {'PASS' if all_ok else 'FAIL'}")

    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()