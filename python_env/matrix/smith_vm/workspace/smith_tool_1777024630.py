# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
----------------------------------
Validates a design proposal (JSON) against the absolute invariants
required by the Omega Protocol (RCOD/DEDS, TOE steps, Smith Audit,
dimensional analysis, audit-cost subtraction, identity continuity).

Usage:
    >>> import json, sys
    >>> proposal = json.load(open("proposal.json"))
    >>> result = validate_proposal(proposal)
    >>> print(result["pass"], result["report"])
"""

import math
from typing import Dict, Any, List, Tuple

# ----------------------------------------------------------------------
# Constants (protocol‑defined)
# ----------------------------------------------------------------------
K_BOLTZMANN = 1.0          # we work in natural units; k = 1
AUDIT_COST = K_BOLTZMANN * math.log(2)   # ΔS_audit = k ln 2
MIN_PSI = math.log(0.95)   # identity continuity lower bound
ALLOWED_TOE_STEPS = {4, 5, 6, 7}   # example: Metric Non‑Degeneracy, Crossed‑Product, etc.
REQUIRED_SMITH_INVARIANTS = 6      # minimum number of enforceable invariants
REQUIRED_RCOD_DEDS = True          # must present RCOD/DEDS substrate

# ----------------------------------------------------------------------
# Helper predicates
# ----------------------------------------------------------------------
def is_dimensionless(term: Any) -> bool:
    """
    Placeholder for a real dimensional analysis.
    In this minimal VM we assume the proposer has already tagged
    each term with a 'dimensionless': True flag.
    """
    return term.get("dimensionless", False)

def psi_ok(psi: float) -> bool:
    return psi >= MIN_PSI

def audit_cost_subtracted(claimed: float, correction: float, audit_cost: float) -> float:
    """Net Φ after removing audit entropy cost."""
    return claimed - correction - audit_cost

# ----------------------------------------------------------------------
# Core validator
# ----------------------------------------------------------------------
def validate_proposal(prop: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a dict:
        {
            "pass": bool,
            "report": List[str]   # human‑readable diagnostics
        }
    """
    report: List[str] = []
    passed = True

    # 1. Informational‑First substrate (RCOD/DEDS)
    if not prop.get("uses_rcod_deds", False):
        report.append("❌ RCOD/DEDS substrate not declared.")
        passed = False
    else:
        report.append("✅ RCOD/DEDS substrate present.")

    # 2. TOE step mapping
    toe_step = prop.get("toe_step")
    if toe_step not in ALLOWED_TOE_STEPS:
        report.append(f"❌ TOE step {toe_step} not in allowed set {ALLOWED_TOE_STEPS}.")
        passed = False
    else:
        report.append(f"✅ TOE step {toe_step} mapped correctly.")

    # 3. Smith Audit invariants (count & HoTT verification flag)
    smith_invs = prop.get("smith_invariants", [])
    if len(smith_invs) < REQUIRED_SMITH_INVARIANTS:
        report.append(f"❌ Smith Audit invariants insufficient: {len(smith_invs)} < {REQUIRED_SMITH_INVARIANTS}.")
        passed = False
    else:
        report.append(f"✅ Smith Audit invariants count: {len(smith_invs)}.")
    # HoTT verification (optional but encouraged)
    if not all(inv.get("hott_verified", False) for inv in smith_invs):
        report.append("⚠️  Not all Smith invariants HoTT‑verified (recommended).")
    else:
        report.append("✅ All Smith invariants HoTT‑verified.")

    # 4. Dimensional consistency (all terms dimensionless)
    terms = prop.get("terms", [])
    nondim_ok = all(is_dimensionless(t) for t in terms)
    if not nondim_ok:
        report.append("❌ Some terms are not dimensionless.")
        passed = False
    else:
        report.append("✅ All terms dimensionless.")

    # 5. Audit cost subtraction & net Φ‑density
    claimed = prop.get("claimed_phi_gain", 0.0)
    correction = prop.get("audit_correction", 0.0)
    net = audit_cost_subtracted(claimed, correction, AUDIT_COST)
    if net < 0:
        report.append(f"❌ Net Φ‑density after audit cost is negative: {net:.3f}.")
        passed = False
    else:
        report.append(f"✅ Net Φ‑density after audit cost: {net:.3f} ≥ 0.")

    # 6. Identity continuity (ψ)
    psi = prop.get("identity_psi", 0.0)
    if not psi_ok(psi):
        report.append(f"❌ Identity continuity ψ = {psi:.3f} < ln(0.95) = {MIN_PSI:.3f}.")
        passed = False
    else:
        report.append(f"✅ Identity continuity ψ = {psi:.3f} ≥ ln(0.95).")

    # 7. Reflective consistency (audit cost subtracted from Φ‑density claims)
    # Already covered in #5; we add a note for clarity.
    report.append("ℹ️  Reflective consistency: audit cost subtracted from all Φ‑density claims (checked).")

    return {"pass": passed, "report": report}

# ----------------------------------------------------------------------
# Example usage (for manual testing)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    example = {
        "uses_rcod_deds": True,
        "toe_step": 4,
        "smith_invariants": [
            {"hott_verified": True},
            {"hott_verified": True},
            {"hott_verified": True},
            {"hott_verified": True},
            {"hott_verified": True},
            {"hott_verified": True},
        ],
        "terms": [{"dimensionless": True} for _ in range(5)],
        "claimed_phi_gain": 1.50,
        "audit_correction": 0.15,
        "identity_psi": math.log(0.96),  # safely above threshold
    }
    result = validate_proposal(example)
    print("PASS:" if result["pass"] else "FAIL:", result["pass"])
    for line in result["report"]:
        print(line)