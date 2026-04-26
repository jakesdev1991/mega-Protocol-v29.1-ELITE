# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Rubric v26.0 Validator
-------------------------------------
Checks a candidate text for:
  1. No boilerplate (no markdown headings, no numbered lists, no bold markup).
  2. Presence of required Omega‑Physics concepts:
       - Covariant modes: Φ_N, Φ_Δ
       - Invariants: ψ, ξ_N, ξ_Δ
       - Entropy observable: S_h(t) (or Shannon‑conditional entropy)
       - Boundaries: ξ_Δ → ∞ (shredding) and ξ_N → ∞ (informational freeze)
       - Equation‑level derivation: action integral S = ∫ L dt, δS = 0, etc.
       - Dimensional consistency check: explicit mention of dimensions or units.
       - Φ‑density impact assessment: short‑term cost and long‑term gain (numeric or %).
  3. Free‑form continuous narrative (paragraphs allowed, but no list‑like lines).

The validator is deliberately conservative: missing any item => FAIL.
"""

import re
import textwrap

def load_candidate(text: str) -> str:
    """Normalize line endings and strip trailing spaces."""
    return "\n".join(line.rstrip() for line in text.splitlines())

def check_boilerplate(text: str) -> dict:
    """Return dict of violations."""
    violations = {}

    # Markdown headings: lines starting with one or more '#'
    if re.search(r'^\s*#{1,6}\s', text, re.M):
        violations["headings"] = "Markdown heading detected."

    # Numbered lists: lines start with digit(s) followed by '.' or ')'
    if re.search(r'^\s*\d+[.)]\s', text, re.M):
        violations["numbered_list"] = "Numbered list detected."

    # Bold markup: **text** or __text__
    if re.search(r'\*\*.*?\*\*|__.*?__', text):
        violations["bold"] = "Bold markup detected."

    return violations

def check_terms(text: str) -> dict:
    """Check for required Omega‑Physics terminology."""
    required = {
        "Φ_N": r'Φ_N|\\[Phi\\]_N',
        "Φ_Δ": r'Φ_Δ|\\[Phi\\]_Δ',
        "ψ": r'ψ|\\psi',
        "ξ_N": r'ξ_N|\\[xi\\]_N',
        "ξ_Δ": r'ξ_Δ|\\[xi\\]_Δ',
        "S_h(t)": r'S_h\(t\)|S_h\\(t\\)',
        "action": r'action|\\\\mathcal{S}|\\\\int.*\\\\mathcal{L}\\\\s*\\\\\\\\ dt',
        "variational": r'δS|variational|\\\\delta S',
        "dimension": r'dimension|units?|[\\\\[][^]]*[\\\\]]',  # very loose
        "Φ_density": r'Φ[-_]density|Phi[-_]density',
        "short_term": r'short[- ]term|short-term',
        "long_term": r'long[- ]term|long-term',
    }
    found = {}
    missing = {}
    for name, pattern in required.items():
        if re.search(pattern, text, re.I | re.X):
            found[name] = True
        else:
            missing[name] = False
    return {"found": found, "missing": missing}

def check_continuous_narrative(text: str) -> dict:
    """Ensure no line looks like a list item or heading."""
    lines = text.splitlines()
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if re.match(r'^\d+[.)]\s', stripped):
            issues.append(f"Line {i}: numbered list item.")
        if re.match(r'^\s*#{1,6}\s', stripped):
            issues.append(f"Line {i}: heading.")
        if re.match(r'^\s*[-*]\s', stripped):
            issues.append(f"Line {i}: bullet list.")
    return {"continuous_narrative_violations": issues}

def validate(text: str) -> dict:
    normalized = load_candidate(text)
    report = {}

    # 1. Boilerplate
    boiler = check_boilerplate(normalized)
    report["boilerplate"] = boiler
    report["boilerplate_pass"] = len(boiler) == 0

    # 2. Terms
    terms = check_terms(normalized)
    report["terms"] = terms
    # Require all terms present
    report["terms_pass"] = len(terms["missing"]) == 0

    # 3. Continuous narrative
    cont = check_continuous_narrative(normalized)
    report["continuous_narrative"] = cont
    report["continuous_narrative_pass"] = len(cont["continuous_narrative_violations"]) == 0

    # Overall
    report["overall_pass"] = (
        report["boilerplate_pass"]
        and report["terms_pass"]
        and report["continuous_narrative_pass"]
    )
    return report

def pretty_print(rep: dict):
    print("=== Omega Protocol Rubric v26.0 Validation Report ===")
    for key, val in rep.items():
        if key == "overall_pass":
            continue
        print(f"\n{key.upper()}:")
        if isinstance(val, dict):
            for k, v in val.items():
                print(f"  {k}: {v}")
        else:
            print(f"  {val}")
    print("\n--------------------------------------------------")
    print(f"OVERALL VERDICT: {'PASS' if rep['overall_pass'] else 'FAIL'}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            candidate = f.read()
    else:
        # Example: read from stdin
        candidate = sys.stdin.read()
    report = validate(candidate)
    pretty_print(report)
    sys.exit(0 if report["overall_pass"] else 1)