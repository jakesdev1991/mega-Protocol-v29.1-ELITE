# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Whitepaper Validator v1.0
----------------------------------------
Checks Whitepaper v2.7 for compliance with the Omega Physics Rubric v26.0:
  - All symbols must be defined before first use.
  - Discrete-to-continuum limits must be accompanied by explicit scaling conditions.
  - Key derivations (Wick rotation, spectral action, area law) must be marked as
    "derived" or "proved", not merely " postulated" or "assumed".
  - No heuristic leaps may be presented as rigorous results.

Usage:
    python3 validate_whitepaper.py whitepaper.tex
"""

import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Configuration: symbols that MUST be defined before first appearance
REQUIRED_DEFINITIONS = {
    r"\\rho_i", r"\\rho_j",          # Choi states
    r"\\Phi\\+", r"\\Phi\\-",        # forward/backward Chain Overlap Densities
    r"w_{ij}",                       # adjacency weight
    r"\\Phi_{ij}",                   # Chain Overlap Density (base)
    r"L'",                           # normalized graph Laplacian
    r"\\varphi_{\\Delta}",           # asymmetry field
    r"G_{\\mu\\nu}",                 # emergent metric after Wick rotation
    r"S",                            # spectral action
    r"S(\\rho_V)",                   # entanglement entropy of region V
    r"K",                            # kinetic term (strong‑field)
    r"v_H/M_{\\mathrm{Pl}}",         # topological hierarchy ratio
}

# Patterns that indicate a definition (non‑exhaustive)
DEF_PATTERNS = [
    r"\\\\def\\\\{",                 # \def\foo{...}
    r"\\\\newcommand\\\\{",          # \newcommand{\foo}{...}
    r"\\\\let\\\\",                  # \let\foo=
    r"\\\\DeclareMathOperator\\\\{", # \DeclareMathOperator{\foo}{...}
    r"\\\\text\\\\{",                # \text{...} (often used in definitions)
    r"\\\\begin\\\\{definition\\\\}",# \begin{definition}...\end{definition}
    r"Definition",                   # plain English definition
]

# Patterns that signal a scaling limit / convergence claim
SCALING_PATTERNS = [
    r"as\s*N\s*\\\\to\s*\\\\infty",
    r"in\s*the\s*limit\s*N\\\\rightarrow\\\\infty",
    r"\\\\epsilon\\(N\\)",
    r"bandwidth\\\\s*\\\\epsilon",
    r"scaling\\\\s*condition",
    r"converges\\\\s*to",
    r"approximates",
]

# Patterns that indicate a derivation / proof
DERIVATION_PATTERNS = [
    r"\\\\begin\\\\{proof\\\\}",
    r"\\\\begin\\\\{derivation\\\\}",
    r"Proof",
    r"Derivation",
    r"Hence",
    r"Therefore",
    r"We show",
    r"We prove",
]

# Patterns that indicate a heuristic / assumption (should NOT be used for core claims)
HEURISTIC_PATTERNS = [
    r"we assume",
    r"we postulate",
    r"heuristic",
    r"analogy",
    r"inspired by",
    r"motivated by",
    r"we conjecture",
]

def load_tex(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def find_first_use(text: str, pattern: str) -> int:
    """Return index of first occurrence of pattern (regex) in text, or -1."""
    m = re.search(pattern, text, flags=re.IGNORECASE)
    return m.start() if m else -1

def find_last_def_before(text: str, pattern: str, pos: int) -> int:
    """Search backward from pos for any definition pattern."""
    snippet = text[:pos]
    # Look for any definition marker
    for def_pat in DEF_PATTERNS:
        matches = list(re.finditer(def_pat, snippet, flags=re.IGNORECASE))
        if matches:
            # Return the start of the last definition before pos
            return matches[-1].start()
    return -1

def check_definitions(text: str) -> list:
    errors = []
    for sym in REQUIRED_DEFINITIONS:
        first = find_first_use(text, sym)
        if first == -1:
            # symbol never appears – ignore (maybe commented out)
            continue
        # Verify that a definition occurs before first use
        def_pos = find_last_def_before(text, sym, first)
        if def_pos == -1:
            errors.append(f"Undefined symbol '{sym}' first used at char {first}.")
    return errors

def check_scaling_claims(text: str) -> list:
    """Ensure every claim of convergence has a scaling condition nearby."""
    errors = []
    # Find sentences that contain convergence language
    sentences = re.split(r'(?<=[.!?])\\s+', text)
    for i, sent in enumerate(sentences):
        if any(re.search(pat, sent, flags=re.IGNORECASE) for pat in SCALING_PATTERNS):
            # Look ahead/back within a window of 2 sentences for explicit scaling
            window = sentences[max(0, i-2):min(len(sentences), i+3)]
            window_text = " ".join(window)
            if not any(re.search(pat, window_text, flags=re.IGNORECASE) for pat in [
                r"\\\\epsilon\\(N\\)",
                r"bandwidth",
                r"scaling\\\\s*condition",
                r"N\\\\rightarrow\\\\infty",
            ]):
                errors.append(
                    f"Convergence claim without explicit scaling: '{sent.strip()}'"
                )
    return errors

def check_derivations_vs_heuristics(text: str) -> list:
    """Core claims must be derivations, not heuristics."""
    errors = []
    # Identify sections that discuss the three major leaps:
    # Wick rotation, spectral action, area law, strong‑field ansatz.
    key_topics = [
        r"Wick\\\\s*rotation",
        r"spectral\\\\s*action",
        r"area\\\\s*law",
        r"strong\\\\s*field",
        r"topological\\\\s*hierarchy",
    ]
    sentences = re.split(r'(?<=[.!?])\\s+', text)
    for sent in sentences:
        if any(re.search(pat, sent, flags=re.IGNORECASE) for pat in key_topics):
            # If the sentence contains a heuristic cue, flag it
            if any(re.search(pat, sent, flags=re.IGNORECASE) for pat in HEURISTIC_PATTERNS):
                errors.append(
                    f"Heuristic language used in core claim: '{sent.strip()}'"
                )
            # Otherwise, require a derivation marker nearby (within same sentence)
            if not any(re.search(pat, sent, flags=re.IGNORECASE) for pat in DERIVATION_PATTERNS):
                errors.append(
                    f"Core claim lacking derivation/proof: '{sent.strip()}'"
                )
    return errors

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 validate_whitepaper.py <whitepaper.tex>")
        sys.exit(1)

    tex_path = Path(sys.argv[1])
    if not tex_path.is_file():
        print(f"Error: File not found: {tex_path}")
        sys.exit(1)

    text = load_tex(tex_path)

    # Run checks
    def_err = check_definitions(text)
    scale_err = check_scaling_claims(text)
    deriv_err = check_derivations_vs_heuristics(text)

    all_err = def_err + scale_err + deriv_err

    if all_err:
        print("Ω Protocol Validation FAILED. The following issues must be resolved:")
        for err in all_err:
            print(f" - {err}")
        sys.exit(1)   # non‑zero exit signals rejection
    else:
        print("Ω Protocol Validation PASSED. Whitepaper satisfies all invariant checks.")
        sys.exit(0)   # zero exit signals acceptance

if __name__ == "__main__":
    main()