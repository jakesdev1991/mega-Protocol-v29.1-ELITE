# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Φ‑impact validator.

Checks:
  * Φ_N  : net change equals sum of phase impacts.
  * Φ_Δ  : each phase impact lies within [-max_delta, +max_delta].
  * J*   : (optional) placeholder for a divergence check – not implemented
           without a reference distribution.

Usage:
    python3 validate_phi.py
"""

from typing import List, Tuple

# ----------------------------------------------------------------------
# Configuration – adjust these values to match the specific Omega Policy
# ----------------------------------------------------------------------
MAX_DELTA_PERCENT = 50.0   # maximum allowed |ΔΦ| per phase (percent)
TOLERANCE = 1e-9           # tolerance for floating‑point equality

# ----------------------------------------------------------------------
# Input data – extracted from the response under review
# ----------------------------------------------------------------------
# Each tuple: (label, claimed_delta_percent)
PHASE_DATA: List[Tuple[str, float]] = [
    ("Immediate", -5.0),
    ("Months 1-6", +5.0),
    ("Months 7-12", +10.0),
    ("Months 13-24", +15.0),
]

# The net Φ claimed in the text
CLAIMED_NET_PERCENT = +10.0


def validate_phi(
    phases: List[Tuple[str, float]],
    claimed_net: float,
    max_delta: float = MAX_DELTA_PERCENT,
    tol: float = TOLERANCE,
) -> Tuple[bool, dict]:
    """
    Validate Φ‑impact consistency.

    Returns
    -------
    (is_compliant, report)
        is_compliant : bool
        report       : dict with details for debugging / logging
    """
    total = sum(delta for _, delta in phases)
    net_error = total - claimed_net

    # Φ_N check: net must equal sum of deltas
    phi_n_ok = abs(net_error) <= tol

    # Φ_Δ check: each phase within allowed bounds
    delta_violations = [
        (label, delta)
        for label, delta in phases
        if abs(delta) > max_delta + tol
    ]
    phi_delta_ok = len(delta_violations) == 0

    # J* placeholder – we cannot compute without a reference distribution.
    # For now we assume it passes if the other two invariants hold.
    j_star_ok = phi_n_ok and phi_delta_ok

    is_compliant = phi_n_ok and phi_delta_ok and j_star_ok

    report = {
        "sum_of_phases": total,
        "claimed_net": claimed_net,
        "net_error": net_error,
        "phi_n_ok": phi_n_ok,
        "phi_delta_ok": phi_delta_ok,
        "delta_violations": delta_violations,
        "j_star_ok": j_star_ok,  # placeholder
    }
    return is_compliant, report


if __name__ == "__main__":
    compliant, report = validate_phi(PHASE_DATA, CLAIMED_NET_PERCENT)

    print("Ω Protocol Φ‑impact validation report")
    print("-" * 40)
    print(f"Sum of phase impacts   : {report['sum_of_phases']: .2f}%")
    print(f"Claimed net impact     : {report['claimed_net']: .2f}%")
    print(f"Net error (sum‑claimed): {report['net_error']: .2f}%")
    print(f"Φ_N (net consistency)  : {'PASS' if report['phi_n_ok'] else 'FAIL'}")
    print(f"Φ_Δ (per‑phase bound)  : {'PASS' if report['phi_delta_ok'] else 'FAIL'}")
    if report["delta_violations"]:
        print("  Violations:")
        for label, delta in report["delta_violations"]:
            print(f"    {label}: {delta:.2f}% (limit ±{MAX_DELTA_PERCENT}%)")
    print(f"J* (placeholder)       : {'PASS' if report['j_star_ok'] else 'FAIL'}")
    print("-" * 40)
    print(f"Overall compliance     : {'COMPLIANT' if compliant else 'NON‑COMPLIANT'}")

    # Exit with a non‑zero code if non‑compliant – useful for CI pipelines
    raise SystemExit(0 if compliant else 1)