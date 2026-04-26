# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator
----------------------------------
Checks a text block for:
  - NO BOILERPLATE: no lines that look like numbered steps.
  - INVARIANTS: presence of ψ = ln(φₙ) (or common ASCII equivalents).
  - (Stiffness invariants ξ_N, ξ_Δ are optional but recommended).

Usage:
    echo "<text to validate>" | python3 validate_omega.py
    # or pipe a file: cat file.txt | python3 validate_omega.py
"""

import sys
import re

def has_boilerplate(text: str) -> bool:
    """
    Returns True if any line matches the pattern:
        optional whitespace, digits, a period, optional whitespace, then a capital letter.
    This catches "1. ...", "2. ...", etc.
    """
    pattern = re.compile(r'^\s*\d+\.\s*[A-Z]')
    return any(pattern.match(line) for line in text.splitlines())

def has_psi_invariant(text: str) -> bool:
    """
    Looks for the invariant ψ = ln(φₙ) in various plausible spellings:
        - ψ (Unicode U+03C8) or the literal "psi"
        - ln(φₙ) where φₙ may be Unicode φ (U+03C6) + subscript n (U+2082) or
          the ASCII "phi_n".
    Allows optional spaces and an equals sign.
    """
    # Unicode phi + subscript n
    phi_n_unicode = r'φ\s*₍?n₍?\)'  # φₙ (subscript 2)
    # ASCII fallback
    phi_n_ascii = r'phi\s*_?\s*n'
    # ln(...) wrapper
    ln_pattern = rf'ln\s*\(\s*(?:{phi_n_unicode}|{phi_n_ascii})\s*\)'
    # ψ or psi, optional spacing, equals, then the ln(...)
    pattern = re.compile(
        rf'(?:ψ|psi)\s*=\s*{ln_pattern}',
        re.IGNORECASE
    )
    return bool(pattern.search(text))

def has_stiffness_invariants(text: str) -> bool:
    """
    Optional check for the stiffness invariants ξ_N and ξ_Δ.
    Accepts Unicode ξ (U+03BE) with subscripts N and Δ, or ASCII xi_N / xi_Delta.
    """
    xi_N = r'(?:ξ|xi)\s*[Nn]'
    xi_Delta = r'(?:ξ|xi)\s*[Δδ]\s*(?:eta)?'  # allow Δ or delta
    pattern = re.compile(
        rf'{xi_N}.*{xi_Delta}|{xi_Delta}.*{xi_N}',
        re.IGNORECASE
    )
    return bool(pattern.search(text))

def main() -> None:
    text = sys.stdin.read()
    if not text.strip():
        print("ERROR: Empty input.", file=sys.stderr)
        sys.exit(1)

    violations = []

    if has_boilerplate(text):
        violations.append("BOILERPLATE: Detected numbered‑list style (e.g., '1. ...').")
    if not has_psi_invariant(text):
        violations.append("INVARIANT: Missing ψ = ln(φₙ) (or equivalent).")
    # Stiffness invariants are recommended but not absolute; warn if missing.
    if not has_stiffness_invariants(text):
        violations.append("WARNING: Stiffness invariants ξ_N / ξ_Δ not found.")

    if violations:
        print("Omega Protocol Validation FAILED:", file=sys.stderr)
        for v in violations:
            print(f" - {v}", file=sys.stderr)
        sys.exit(1)   # non‑zero -> block output in the VM
    else:
        print("Omega Protocol Validation PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()