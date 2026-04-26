# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 Compliance Checker
---------------------------------------
Validates a free‑form narrative against the rubric pillars.
Returns a detailed report and a final PASS/FAIL verdict.
"""

import re
from typing import List, Tuple

# ----------------------------------------------------------------------
# Configuration: required keywords/patterns for each rubric pillar
# ----------------------------------------------------------------------
REQUIRED_PATTERNS = {
    "NO_BOILERPLATE": [
        # Disallow markdown headings, numeric lists, bold markup
        (r"^\s*#{1,6}\s", "markdown heading"),
        (r"^\s*\d+\.\s", "ordered list"),
        (r"\*\*.*?\*\*", "bold markup"),
    ],
    "COVARIANT_MODES": [
        r"\bΦ_N\b",
        r"\bΦ_Δ\b",
    ],
    "INVARIANTS": [
        r"\bψ\b",
        r"\bξ_N\b",
        r"\bξ_Δ\b",
    ],
    "BOUNDARIES": [
        r"ξ_Δ\s*→\s*∞",
        r"ξ_N\s*→\s*∞",
        r"Shredding",
        r"Informational Freeze",
    ],
    "ENTROPY": [
        r"Shannon",
        r"conditional entropy",
        r"S_h\(t\)",
        r"entropy",
    ],
    "EQUATION_LEVEL_DERIVATION": [
        r"action functional",
        r"variational principle",
        r"Hessian",
        r"derivation",
        r"step‑by‑step",
    ],
    "DIMENSIONAL_CHECK": [
        r"dimension",
        r"units",
        r"[Ee]nergy\s*[·\*]\s*[Tt]ime",
        r"[Jj]erk\s*\[",
    ],
    "PHI_DENSITY_IMPACT": [
        r"Φ.*density",
        r"short‑term",
        r"long‑term",
        r"%",
    ],
}

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def _contains_any(text: str, patterns: List[str]) -> Tuple[bool, List[str]]:
    """Return (found, missing_patterns)."""
    missing = []
    for pat in patterns:
        if not re.search(pat, text, re.IGNORECASE | re.MULTILINE):
            missing.append(pat)
    return (len(missing) == 0, missing)

def _check_boilerplate(text: str) -> Tuple[bool, List[str]]:
    """Return (ok, violations)."""
    violations = []
    for pat, label in REQUIRED_PATTERNS["NO_BOILERPLATE"]:
        if re.search(pat, text, re.MULTILINE):
            violations.append(label)
    return (len(violations) == 0, violations)

def _extract_percentages(text: str) -> List[float]:
    """Find all numbers followed by a '%' sign."""
    return [float(m) for m in re.findall(r"([-+]?\d*\.?\d+)\s*%", text)]

def validate_omega_compliance(narrative: str) -> dict:
    """
    Main validation routine.
    Returns a dict with per‑pillar results and an overall verdict.
    """
    report = {}

    # 1. Boilerplate check (must PASS)
    boiler_ok, boiler_viol = _check_boilerplate(narrative)
    report["NO_BOILERPLATE"] = {
        "pass": boiler_ok,
        "details": "clean" if boiler_ok else f"violations: {', '.join(boiler_viol)}",
    }

    # 2. Content pillars
    for pillar, patterns in REQUIRED_PATTERNS.items():
        if pillar == "NO_BOILERPLATE":
            continue  # already handled
        found, missing = _contains_any(narrative, patterns)
        report[pillar] = {
            "pass": found,
            "details": "all required tokens present"
            if found
            else f"missing: {', '.join(missing)}",
        }

    # 3. Simple sanity check on any percentages found
    percents = _extract_percentages(narrative)
    if percents:
        # Example rule: any claimed Φ‑density impact should be within [-100, +200] %
        out_of_range = [p for p in percents if p < -100 or p > 200]
        report["PERCENTAGE_SANITY"] = {
            "pass": len(out_of_range) == 0,
            "details": f"found percentages: {percents}"
            + ("" if not out_of_range else f"; out‑of‑range: {out_of_range}"),
        }
    else:
        report["PERCENTAGE_SANITY"] = {
            "pass": True,
            "details": "no percentage claims to sanity‑check",
        }

    # Overall verdict: all required pillars must pass
    overall_pass = all(
        report[p]["pass"]
        for p in [
            "NO_BOILERPLATE",
            "COVARIANT_MODES",
            "INVARIANTS",
            "BOUNDARIES",
            "ENTROPY",
            "EQUATION_LEVEL_DERIVATION",
            "DIMENSIONAL_CHECK",
            "PHI_DENSITY_IMPACT",
        ]
    )
    report["OVERALL"] = {"pass": overall_pass}

    return report


# ----------------------------------------------------------------------
# Example usage (replace `candidate_text` with the actual output to audit)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    candidate_text = """\
    The Engine’s output consisting solely of the string “None” does not meet the Omega Physics Rubric v26.0 requirements.
    It lacks covariant modes Φ_N and Φ_Δ, invariants ψ, ξ_N, ξ_Δ, boundary‑condition analysis (ξ_Δ→∞, ξ_N→∞),
    entropy observable (Shannon‑conditional entropy S_h(t)), equation‑level derivation from an action functional,
    dimensional consistency check, and Φ‑density impact assessment.
    Even though it avoids explicit boilerplate formatting, it provides no substantive narrative or technical content,
    which is obligatory for any refinement task under the protocol.
    """

    result = validate_omega_compliance(candidate_text)

    print("=== Omega Protocol Compliance Report ===")
    for pillar, info in result.items():
        status = "PASS" if info["pass"] else "FAIL"
        print(f"{pillar:30} [{status}] : {info['details']}")
    print("\nOVERALL VERDICT:", "PASS" if result["OVERALL"]["pass"] else "FAIL")