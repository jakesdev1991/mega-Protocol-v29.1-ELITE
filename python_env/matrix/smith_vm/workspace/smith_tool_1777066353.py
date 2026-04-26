# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Physics Rubric (v26.0) compliance checker.
Usage: python3 rubric_check.py <proposal_text_file>
"""

import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Rubric‑required tokens (case‑insensitive)
REQUIRED_TOKENS = [
    r"\bΦ_N\b",          # covariant mode Newtonian
    r"\bΦ_Δ\b",          # covariant mode Asymmetry (Δ as Greek Delta)
    r"psi\s*=\s*ln\s*\(\s*phi_N\s*\)",  # ψ = ln(φ_N)
    r"\bxi_N\b",
    r"\bxi_Δ\b",
    r"\bShredding\s+Event\b",
    r"\bInformational\s+Freeze\b",
    r"\bShannon\s+conditional\s+entropy\b",
    r"\btopological\s+impedance\b",
]

# Pattern for a LaTeX‑style equation (display or inline)
EQUATION_PATTERN = re.compile(
    r"\$\$.*?\$\$|"          # $$ ... $$ display
    r"\$.*?\$|"              # $ ... $ inline
    r"\\\(.*?\\\)|"          # \( ... \)
    r"\\\[.*?\\\]",          # \[ ... \]
    re.DOTALL
)

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def check_tokens(text: str):
    missing = []
    for tok in REQUIRED_TOKENS:
        if not re.search(tok, text, flags=re.IGNORECASE):
            missing.append(tok)
    return missing

def check_equations(text: str):
    matches = EQUATION_PATTERN.findall(text)
    return [m for m in matches if m.strip()]  # non‑empty

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <proposal_file>", file=sys.stderr)
        sys.exit(1)

    proposal_path = Path(sys.argv[1])
    if not proposal_path.is_file():
        print(f"Error: file not found: {proposal_path}", file=sys.stderr)
        sys.exit(1)

    text = load_text(proposal_path)

    missing = check_tokens(text)
    equations = check_equations(text)

    print("\n=== Omega Physics Rubric Check ===")
    if missing:
        print("FAIL – Missing required tokens:")
        for m in missing:
            print(f"  - {m}")
    else:
        print("PASS – All required tokens present.")

    if equations:
        print(f"PASS – Found {len(equations)} equation‑level expression(s).")
        # Optional: show first equation for sanity
        print(f"  Example: {equations[0][:80]}...")
    else:
        print("FAIL – No LaTeX‑style equation detected.")

    overall = not missing and bool(equations)
    print("\nRESULT:", "SUBMISSION‑GRADE (physics compliant)" if overall else "NON‑COMPLIANT")
    sys.exit(0 if overall else 1)

if __name__ == "__main__":
    main()