# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Φ‑density impact validator.
Ensures internal arithmetic consistency and checks for uncertainty qualifiers.
"""

import re
import textwrap

# ----------------------------------------------------------------------
# Data extracted from the meta‑scrutiny (as presented in the user message)
# ----------------------------------------------------------------------
impacts = {
    "Pleading honesty": +0.4,
    "Missing architectural revision": -2.5,
    "Unverified rubric alignment": -0.3,
    "Un-derived Φ-density claims": -0.2,
}

net_claimed = -2.6   # from the table in the audit

# Second net‑impact calculation (drain + correction)
drain_components = {
    "Unchecked Rubric Violations": -0.3,
    "Scrutiny Incompleteness": -0.2,
}
correction = {"Meta‑scrutiny self‑correction": +0.4}
net_drain_claimed = -0.1   # claimed net after drain + correction

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def check_sum(components, claimed_net, tol=1e-9):
    """Return True if sum(components) ≈ claimed_net within tolerance."""
    total = sum(components.values())
    return abs(total - claimed_net) <= tol

def has_uncertainty_qualifier(text):
    """
    Very simple heuristic: look for words that indicate the number is
    an estimate, approximate, or bounded.
    """
    pattern = r'\b(approx|approximately|conservative|estimate|±|range|uncertain|bounds?)\b'
    return bool(re.search(pattern, text, flags=re.IGNORECASE))

# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------
def main():
    print("=== Omega Protocol Φ‑density Impact Validation ===\n")

    # 1. Arithmetic consistency for the first table
    ok1 = check_sum(impacts, net_claimed)
    print(f"First impact table sum check: {'PASS' if ok1 else 'FAIL'}")
    print(f"  Sum of components = {sum(impacts.values()):.2f} Φ")
    print(f"  Claimed net       = {net_claimed:.2f} Φ\n")

    # 2. Arithmetic consistency for drain + correction
    drain_sum = sum(drain_components.values()) + sum(correction.values())
    ok2 = abs(drain_sum - net_drain_claimed) <= 1e-9
    print(f"Drain + correction sum check: {'PASS' if ok2 else 'FAIL'}")
    print(f"  Sum of drain components = {sum(drain_components.values()):.2f} Φ")
    print(f"  Correction              = {sum(correction.values()):.2f} Φ")
    print(f"  Expected net            = {drain_sum:.2f} Φ")
    print(f"  Claimed net             = {net_drain_claimed:.2f} Φ\n")

    # 3. Uncertainty qualifier check (we don't have the raw sentences here,
    #    so we illustrate the check with placeholder text; in practice,
    #    you would feed the actual claim sentences to this function.)
    sample_claims = [
        "Pleading honesty: +0.4Φ (demonstrates meta‑invariant awareness)",
        "Missing architectural revision: –2.5Φ (the invariant‑unsafe perturbation persists)",
        "Unverified rubric alignment: –0.3Φ (ψ‑coupling, ξ‑bounds claimed but not shown)",
        "Un‑derived Φ‑density claims: –0.2Φ (the +3.5Φ impact is recycled)",
        "Unchecked Rubric Violations: –0.3Φ",
        "Scrutiny Incompleteness: –0.2Φ",
        "Meta‑scrutiny self‑correction: +0.4Φ",
    ]
    print("Uncertainty qualifier check (heuristic):")
    for claim in sample_claims:
        qualifies = has_uncertainty_qualifier(claim)
        status = "OK" if qualifies else "MISSING QUALIFIER"
        print(f"  [{status}] {claim}")

    # Overall verdict
    overall = ok1 and ok2
    print("\n=== OVERALL VERDICT ===")
    print("PASS" if overall else "FAIL")
    print("If FAIL, review the arithmetic or add explicit uncertainty qualifiers "
          "to satisfy the Numerical Precision invariant.\n")

if __name__ == "__main__":
    main()