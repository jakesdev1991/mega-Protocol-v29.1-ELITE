# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Φ‑Density Math Validator
--------------------------------------
This script checks the internal consistency of the Φ‑impact table
provided in the Engine's output.  The Omega Protocol invariants we
enforce here are:

1. **Φ_N (Non‑negativity of cumulative impact)** – the running total
   of impacts must never drop below zero (the protocol cannot tolerate
   a net loss of stability).
2. **Φ_Delta (Additivity)** – the sum of all phase impacts must equal
   the declared net Φ change.
3. **J* (Boundedness)** – each individual phase impact must lie within
   a realistic bounds (we choose -100 % ≤ impact ≤ +100 % as a sane
   safety margin; tighter bounds can be adjusted per policy).

If any invariant is violated the script exits with a non‑zero status
and prints a detailed diagnostic.
"""

from typing import List, Tuple

# ----------------------------------------------------------------------
# Data extracted from the Engine's Φ‑density reflection table
# ----------------------------------------------------------------------
# Each tuple: (phase_label, impact_percent)
PHASE_IMPACTS: List[Tuple[str, float]] = [
    ("Immediate", -5.0),
    ("Months 1–6", +5.0),
    ("Months 7–12", +10.0),
    ("Months 13–24", +15.0),
]

# Net impact claimed by the Engine
CLAIMED_NET: float = +10.0   # percent

# ----------------------------------------------------------------------
# Validation parameters (can be tuned to match specific Omega Policy)
# ----------------------------------------------------------------------
MIN_IMPACT = -100.0   # percent
MAX_IMPACT = +100.0   # percent
ALLOW_NEGATIVE_CUMULATIVE = False   # Φ_N invariant: forbid negative running total


def validate_impacts() -> Tuple[bool, List[str]]:
    """
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []
    cumulative: float = 0.0

    # 1. J* – per‑phase boundedness
    for label, impact in PHASE_IMPACTS:
        if not (MIN_IMPACT <= impact <= MAX_IMPACT):
            errors.append(
                f"J* violation: phase '{label}' impact {impact}% outside "
                f"allowed range [{MIN_IMPACT}, {MAX_IMPACT}]%"
            )

    # 2. Φ_N – non‑negative cumulative impact (if policy forbids negatives)
    for label, impact in PHASE_IMPACTS:
        cumulative += impact
        if (not ALLOW_NEGATIVE_CUMULATIVE) and cumulative < 0:
            errors.append(
                f"Φ_N violation: after phase '{label}' cumulative impact "
                f"dropped to {cumulative:.2f}% (negative)"
            )

    # 3. Φ_Delta – additivity: sum of impacts must equal claimed net
    total_impact = sum(impact for _, impact in PHASE_IMPACTS)
    if abs(total_impact - CLAIMED_NET) > 1e-9:  # tolerance for floating point
        errors.append(
            f"Φ_Delta violation: sum of phase impacts = {total_impact:.2f}%, "
            f"but claimed net impact = {CLAIMED_NET:.2f}%"
        )

    return len(errors) == 0, errors


def main() -> None:
    valid, errs = validate_impacts()
    if valid:
        print("✅ Φ‑density math PASSED all Omega Protocol invariants.")
        raise SystemExit(0)
    else:
        print("❌ Φ‑density math FAILED Omega Protocol validation:")
        for e in errs:
            print(f" - {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()