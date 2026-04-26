# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Submission Validator
-----------------------------------
Validates a submission for the "Quantum-Enhanced Children's Footwear (Adaptive Topology)"
task against the four mandatory pillars:
    1. Concept (Informational Advantage & Φ‑density maximization)
    2. Architecture (System diagram / software component structure)
    3. Physics Link (Mapping to a specific TOE step)
    4. Smith Audit (Absolute Invariants & verification)

The validator treats a completely missing pillar as a hard failure and assigns
the maximal negative Φ‑density penalty (−Φ_max).  Φ_max is set to 1.0 for
normalisation; adjust to match the protocol's calibrated scale.

Usage:
    >>> validate_submission(submission_dict)
    (is_pass, phi_score, report)
"""

from typing import Dict, Tuple, List

# ----------------------------------------------------------------------
# Configuration (tune to the Omega Protocol's calibrated Φ‑density scale)
# ----------------------------------------------------------------------
PHI_MAX = 1.0               # Maximum achievable Φ‑gain for this task
REQUIRED_KEYS = [
    "concept",
    "architecture",
    "physics_link",
    "smith_audit",
]

def _has_informational_content(text: str) -> bool:
    """
    Very light‑weight heuristic: a section is considered to contain
    informational content if it includes at least one of:
        - a defined variable (e.g., Φ, S, Δt)
        - an equation or expression containing '=' or a mathematical symbol
        - a bullet‑pointed list or numbered step (indicates structured info)
    This is intentionally conservative; replace with a full parser if needed.
    """
    if not text or not isinstance(text, str):
        return False
    lowered = text.lower()
    # Look for typical informational markers
    markers = [
        "phi", "Φ", "s_", "delta t", "Δt", "=", "+", "-", "*", "/",
        "^", "∂", "∫", "∑", "→", "←", "↔", "∀", "∃",
        "algorithm", "equation", "formula", "step", "bullet", "- ", "* "
    ]
    return any(m in lowered for m in markers)

def validate_submission(submission: Dict[str, str]) -> Tuple[bool, float, List[str]]:
    """
    Validate a submission dictionary.

    Parameters
    ----------
    submission : dict
        Mapping from pillar name to its textual content.
        Expected keys: "concept", "architecture", "physics_link", "smith_audit".

    Returns
    -------
    is_pass : bool
        True if the submission meets all Omega Protocol invariants.
    phi_score : float
        Net Φ‑density contribution (negative if penalised).
    report : list of str
        Human‑readable feedback detailing any violations.
    """
    missing = []
    weak = []
    phi_score = 0.0

    for key in REQUIRED_KEYS:
        content = submission.get(key, "")
        if not content or not content.strip():
            missing.append(key)
            phi_score -= PHI_MAX          # maximal penalty for absence
        elif not _has_informational_content(content):
            weak.append(key)
            phi_score -= PHI_MAX / 2.0    # partial penalty for informational weakness
        else:
            # Full credit for a solid, informational‑first pillar
            phi_score += PHI_MAX / len(REQUIRED_KEYS)

    # Build report
    report = []
    if missing:
        report.append(f"MISSING pillars: {', '.join(missing)}")
    if weak:
        report.append(f"Weak/informational‑insufficient pillars: {', '.join(weak)}")
    if not missing and not weak:
        report.append("All pillars present with verifiable informational content.")
    report.append(f"Net Φ‑density score: {phi_score:.3f}")

    is_pass = (len(missing) == 0 and len(weak) == 0 and phi_score >= 0.0)
    return is_pass, phi_score, report

# ----------------------------------------------------------------------
# Example usage (empty submission → FAIL)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    empty_sub = {
        "concept": "",
        "architecture": "",
        "physics_link": "",
        "smith_audit": "",
    }
    passed, score, notes = validate_submission(empty_sub)
    print("=== Omega Protocol Submission Validation ===")
    for n in notes:
        print(n)
    print(f"\nResult: {'PASS' if passed else 'FAIL'}")
    print(f"Φ‑score: {score:.3f}")