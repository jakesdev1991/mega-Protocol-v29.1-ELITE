# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Rubric v26.0 Compliance Checker
-----------------------------------------------
This script validates a given text against the core formatting and
substantive requirements of the Omega Physics Rubric v26.0.
It is deliberately lightweight: it looks for prohibited boilerplate
patterns and checks for the presence of mandatory symbolic elements.
If any violation is found, the script reports it and returns a non‑zero
exit code (suitable for CI/CD gating).

Usage:
    python omega_compliance_checker.py "<text to validate>"
"""

import re
import sys

def check_boilerplate(text: str) -> list[str]:
    """Return a list of boilerplate violations found in `text`."""
    violations = []

    # 1. Numbered steps or enumerated lists (e.g., "1.", "Step 2 –")
    if re.search(r'(?m)^\s*\d+\.\s', text) or re.search(r'(?m)^\s*Step\s+\d+', text, re.I):
        violations.append("Numbered steps or explicit sequencing detected (NO BOILERPLATE).")

    # 2. Bold markdown markers (**text**)
    if re.search(r'\*\*.*?\*\*', text):
        violations.append("Bold markdown (**) detected (NO BOILERPLATE).")

    # 3. Headings that look like markdown or explicit labels (e.g., "Title:", "Core Insight:")
    if re.search(r'(?m)^\s*(Title|Core Insight|Technical Implementation|Reflection|Final Output):\s*', text, re.I):
        violations.append("Explicit section headings detected (NO BOILERPLATE).")

    # 4. Bullet points or dash‑list items at line start
    if re.search(r'(?m)^\s*[-*]\s', text):
        violations.append("Bullet‑point list detected (NO BOILERPLATE).")

    return violations

def check_mandatory_symbols(text: str) -> list[str]:
    """Check for the presence of required Omega symbols."""
    required = [r'Φ_N', r'Φ_Δ', r'ψ', r'ξ_N', r'ξ_Δ']
    missing = []
    for sym in required:
        if not re.search(sym, text):
            missing.append(sym)
    if missing:
        return [f"Missing mandatory symbol(s): {', '.join(missing)}"]
    return []

def check_boundary_conditions(text: str) -> list[str]:
    """Look for explicit mention of the two boundary conditions."""
    # The rubric expects phrases like "Shredding Event" and "Informational Freeze"
    # (case‑insensitive) and the symbolic limits PHI→0, ξ→0 and PHI→1, ξ→∞.
    has_shred = bool(re.search(r'Shredding\s+Event', text, re.I))
    has_freeze = bool(re.search(r'Informational\s+Freeze', text, re.I))
    has_phi0_xi0 = bool(re.search(r'PHI\s*→\s*0\s*,\s*ξ\s*→\s*0', text, re.I))
    has_phi1_xiinf = bool(re.search(r'PHI\s*→\s*1\s*,\s*ξ\s*→\s*∞', text, re.I))
    violations = []
    if not (has_shred and has_freeze):
        violations.append("Explicit reference to both Shredding Event and Informational Freeze missing.")
    if not (has_phi0_xi0 and has_phi1_xiinf):
        violations.append("Explicit symbolic boundary limits (PHI→0,ξ→0 and PHI→1,ξ→∞) missing.")
    return violations

def main():
    if len(sys.argv) < 2:
        print("Usage: python omega_compliance_checker.py \"<text>\"")
        sys.exit(1)

    text = sys.argv[1]

    all_violations = []
    all_violations.extend(check_boilerplate(text))
    all_violations.extend(check_mandatory_symbols(text))
    all_violations.extend(check_boundary_conditions(text))

    if all_violations:
        print("Ω Protocol Compliance FAILURES:")
        for v in all_violations:
            print(f" - {v}")
        sys.exit(1)
    else:
        print("Ω Protocol Compliance PASS")
        sys.exit(0)

if __name__ == "__main__":
    main()