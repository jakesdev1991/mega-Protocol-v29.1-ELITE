# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Rubric v26.0 Structural Validator
------------------------------------------------
Checks a narrative for required tokens and absence of boilerplate.
Returns PASS only if *all* constraints are satisfied.
"""

import re
import sys

def load_candidate() -> str:
    # Read from stdin; if empty, fall back to a placeholder for testing.
    data = sys.stdin.read()
    return data.strip() if data.strip() else ""

def check_no_boilerplate(text: str) -> tuple[bool, list]:
    """Detect markdown headings, list markers, bold syntax."""
    violations = []
    if re.search(r'^\s*#{1,6}\s', text, re.M):
        violations.append("Markdown heading detected")
    if re.search(r'^\s*[\d]+[\.\)]\s', text, re.M):
        violations.append("Numbered list marker detected")
    if re.search(r'^\s*[-*]\s', text, re.M):
        violations.append("Bullet list marker detected")
    if re.search(r'\*\*.*?\*\*', text):
        violations.append("Bold markup (**) detected")
    return (len(violations) == 0, violations)

def token_present(text: str, pattern: str, flags=0) -> bool:
    return re.search(pattern, text, flags) is not None

def validate(text: str) -> dict:
    results = {}

    # 1. No boilerplate
    ok, msgs = check_no_boilerplate(text)
    results["NO_BOILERPLATE"] = (ok, msgs if not ok else ["OK"])

    # 2. Covariant modes
    results["COVARIANT_MODES"] = (
        token_present(text, r'Φ_N') and token_present(text, r'Φ_Δ'),
        ["Φ_N, Φ_Δ found"] if (token_present(text, r'Φ_N') and token_present(text, r'Φ_Δ')) else ["Missing Φ_N or Φ_Δ"]
    )

    # 3. Invariants
    inv_ok = all(token_present(text, tok) for tok in [r'ψ', r'ξ_N', r'ξ_Δ'])
    results["INVARIANTS"] = (
        inv_ok,
        ["ψ, ξ_N, ξ_Δ found"] if inv_ok else ["Missing one or more of ψ, ξ_N, ξ_Δ"]
    )

    # 4. Boundaries (Shredding & Informational Freeze)
    shred_ok = token_present(text, r'Shredding|ξ_Δ\s*→\s*∞|informational\s*freeze|ξ_N\s*→\s*∞', re.IGNORECASE)
    results["BOUNDARIES"] = (
        shred_ok,
        ["Boundary language found"] if shred_ok else ["Missing shredding or informational freeze description"]
    )

    # 5. Entropy (Shannon‑conditional)
    ent_ok = token_present(text, r'S_h\(t\)|Shannon.*entropy|entropy.*observable', re.IGNORECASE)
    results["ENTROPY"] = (
        ent_ok,
        ["Entropy observable found"] if ent_ok else ["Missing entropy definition"]
    )

    # 6. Equation‑level derivation (look for any math‑like token)
    eq_ok = token_present(text, r'[=+\-*/∂∫δ∑]|\\frac|\\sum|\\int', re.IGNORECASE)
    results["EQUATION_LEVEL"] = (
        eq_ok,
        ["Equation‑like expression found"] if eq_ok else ["No detectable equation/derivation"]
    )

    # 7. Dimensional consistency check
    dim_ok = token_present(text, r'dimensional\s*consistency|\[[^\]]*energy·time[^\]]*\]|units?', re.IGNORECASE)
    results["DIMENSIONAL_CHECK"] = (
        dim_ok,
        ["Dimensional check present"] if dim_ok else ["Missing explicit dimensional consistency statement"]
    )

    # 8. Φ‑density impact assessment (short‑term dip & long‑term gain)
    phi_short = token_present(text, r'−?\d+%?\s*Φ.*(?:dip|drop|decrease|short‑term|short term)', re.IGNORECASE)
    phi_long  = token_present(text, r'\+?\d+%?\s*Φ.*(?:gain|increase|long‑term|long term)', re.IGNORECASE)
    phi_ok = phi_short and phi_long
    results["PHI_DENSITY_IMPACT"] = (
        phi_ok,
        ["Φ‑density impact (short & long term) found"] if phi_ok else ["Missing short‑term or long‑term Φ impact"]
    )

    # Overall PASS if every check is True
    overall = all(v[0] for v in results.values())
    return {"overall": overall, "details": results}

def main():
    candidate = load_candidate()
    if not candidate:
        print("ERROR: No input provided.", file=sys.stderr)
        sys.exit(1)

    report = validate(candidate)

    print("=== Omega Protocol Rubric v26.0 Structural Validation ===")
    for name, (ok, msgs) in report["details"].items():
        status = "PASS" if ok else "FAIL"
        print(f"{name:25} : {status}  ({'; '.join(msgs)})")
    print("-" * 60)
    print(f"OVERALL VERDICT : {'PASS' if report['overall'] else 'FAIL'}")
    if not report['overall']:
        print("Action: Revise the narrative to satisfy all failed constraints.", file=sys.stderr)

if __name__ == "__main__":
    main()