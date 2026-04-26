# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Compliance Checker (v26.0)
----------------------------------------
Given a proposal text, returns COMPLIANT only if:
  * No markdown headings, bold markup, or list syntax (NO BOILERPLATE).
  * Required symbols ψ, Φ_N, Φ_Δ, J* appear.
  * An explicit definition of ψ = ln(φₙ) is present.
  * An entropy-based observable and its gauge coupling are mentioned.
  * Boundary conditions (Shredding Event / Informational Freeze) are expressed via ψ limits.
  * A dimensional consistency check is referenced.
All checks are case‑insensitive and tolerate minor whitespace variations.
"""

import re
import sys

def load_proposal(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def boilerplate_check(text: str) -> bool:
    """Return True if any boilerplate pattern is found."""
    patterns = [
        r'^\s*#{1,6}\s',          # markdown headings
        r'\*\*.*?\*\*',           # bold markup
        r'^\s*\d+\.\s',           # ordered list (1. , 2. , …)
        r'^\s*[-*+]\s',           # unordered list (-, *, +)
        r'^\s*[a-zA-Z]\)\s',      # lettered list (a) , b) , …
    ]
    for pat in patterns:
        if re.search(pat, text, flags=re.MULTILINE):
            return True
    return False

def symbol_present(text: str, symbol: str) -> bool:
    """Check for symbol (allowing subscripts/superscripts in plain text)."""
    # Normalise common Unicode subscripts/superscripts to plain names for simplicity
    norm = text.replace('Φ_N', 'Phi_N').replace('Φ_Δ', 'Phi_Delta').replace('ψ', 'psi')
    return re.search(rf'\b{re.escape(symbol)}\b', norm, re.IGNORECASE) is not None

def psi_definition_check(text: str) -> bool:
    """Look for an explicit definition ψ = ln(φₙ) or equivalent."""
    # Accept variations: ψ = ln(φ_n), psi = log(phi_n), ψ = ln(phi_n), etc.
    pattern = r'psi\s*=\s*ln\s*\(\s*phi\s*_?\s*n\s*\)'
    return re.search(pattern, text, re.IGNORECASE) is not None

def entropy_observable_check(text: str) -> bool:
    """Entropy observable + gauge coupling hint."""
    # Look for entropy or Shannon entropy and a gauge field mention
    entropy_pat = r'entropy|shannon\s*entropy|S_h'
    gauge_pat   = r'𝒜_μ|\\mathcal{A}_μ|gauge\s*field|∂_μ'
    return (re.search(entropy_pat, text, re.IGNORECASE) and
            re.search(gauge_pat, text, re.IGNORECASE))

def boundary_condition_check(text: str) -> bool:
    """Shredding Event / Informational Freeze expressed via ψ limits."""
    # Accept ψ → +∞, ψ → -∞, psi -> inf, psi -> -inf, or Φ_N/Φ_Δ limits
    shred_pat   = r'Shredding\s*Event.*ψ\s*→\s*\+\s*∞|psi\s*->\s*inf'
    freeze_pat  = r'Informational\s*Freeze.*ψ\s*→\s*-\s*∞|psi\s*->\s*-inf'
    # Also accept Φ_N → 0, Φ_Δ → ∞ etc.
    mode_pat    = r'Φ_N\s*→\s*0|Phi_N\s*->\s*0|Φ_Δ\s*→\s*∞|Phi_Delta\s*->\s*inf'
    return (re.search(shred_pat, text, re.IGNORECASE) or
            re.search(freeze_pat, text, re.IGNORECASE) or
            re.search(mode_pat, text, re.IGNORECASE))

def dimensional_check(text: str) -> bool:
    """Any explicit dimensional consistency reference."""
    return re.search(r'dimensional|\[.*\]|units?', text, re.IGNORECASE) is not None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 omega_check.py <proposal_file>")
        sys.exit(1)

    proposal = load_proposal(sys.argv[1])

    # 1. NO BOILERPLATE
    if boilerplate_check(proposal):
        print("FAIL: Boilerplate detected (headings, bold, lists).")
        sys.exit(0)

    # 2. Required symbols
    for sym in ['psi', 'Phi_N', 'Phi_Delta', 'J*']:
        if not symbol_present(proposal, sym):
            print(f"FAIL: Missing required symbol '{sym}'.")
            sys.exit(0)

    # 3. ψ definition
    if not psi_definition_check(proposal):
        print("FAIL: No explicit definition ψ = ln(φₙ) found.")
        sys.exit(0)

    # 4. Entropy observable + gauge
    if not entropy_observable_check(proposal):
        print("FAIL: Entropy-based observable or its gauge coupling missing.")
        sys.exit(0)

    # 5. Boundary conditions
    if not boundary_condition_check(proposal):
        print("FAIL: Shredding Event / Informational Freeze not expressed via ψ limits.")
        sys.exit(0)

    # 6. Dimensional consistency cue
    if not dimensional_check(proposal):
        print("FAIL: No explicit dimensional consistency check found.")
        sys.exit(0)

    print("COMPLIANT (passes syntactic Omega Rubric checks).")

if __name__ == "__main__":
    main()