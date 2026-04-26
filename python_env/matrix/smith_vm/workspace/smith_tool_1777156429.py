# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Φ‑density invariant validator.

Checks:
  - Sum of incremental Φ changes equals declared net Φ (tolerance 0.01%).
  - Each incremental change lies within [-10, +10] percent.
  - Net Φ change is finite (not NaN or infinite).

Usage:
  python3 validate_phi.py   # reads constants defined below
  # or import and call validate_phi(increments, net)
"""

from __future__ import annotations
import math
import sys
from typing import List, Tuple

# ----------------------------------------------------------------------
# ----  USER‑DEFINED CONSTANTS (replace with parsing from file if needed) ----
# Example: OnePlus 12 timeline increments
ONEPLUS_INCREMENTS: List[float] = [-1.0, 0.0, 4.0, 2.0, 1.0]
ONEPLUS_NET_CLAIMED: float = 6.0   # %

# Example: Protocol‑level gain breakdown
PROTOCOL_INCREMENTS: List[float] = [2.5, 2.0, 1.0, 1.0]
PROTOCOL_NET_CLAIMED: float = 6.5  # %
# ----------------------------------------------------------------------


TOLERANCE = 0.01  # percent
MIN_DELTA, MAX_DELTA = -10.0, 10.0  # percent bounds per Omega Protocol


def validate_phi(increments: List[float], net_claimed: float, label: str) -> Tuple[bool, List[str]]:
    """Return (is_ok, list_of_error_messages)."""
    errors: List[str] = []

    # 1. Check each increment is within protocol bounds
    for i, d in enumerate(increments, start=1):
        if not (MIN_DELTA <= d <= MAX_DELTA):
            errors.append(
                f"{label}: increment #{i} = {d}% outside allowed range [{MIN_DELTA}, {MAX_DELTA}]%"
            )
        if not math.isfinite(d):
            errors.append(f"{label}: increment #{i} is not a finite number")

    # 2. Check sum matches claimed net (within tolerance)
    net_calc = sum(increments)
    if not math.isclose(net_calc, net_claimed, rel_tol=0, abs_tol=TOLERANCE):
        errors.append(
            f"{label}: sum of increments = {net_calc:.3f}% does not equal claimed net "
            f"{net_claimed:.3f}% (diff > {TOLERANCE}%)"
        )
    if not math.isfinite(net_claimed):
        errors.append(f"{label}: claimed net Φ is not finite")

    return len(errors) == 0, errors


def main() -> int:
    all_ok = True

    ok, errs = validate_phi(ONEPLUS_INCREMENTS, ONEPLUS_NET_CLAIMED, "OnePlus 12 timeline")
    if not ok:
        all_ok = False
        print("❌ OnePlus 12 Φ‑density validation failed:")
        for e in errs:
            print("   -", e)
    else:
        print("✅ OnePlus 12 Φ‑density validation passed.")

    ok, errs = validate_phi(PROTOCOL_INCREMENTS, PROTOCOL_NET_CLAIMED, "Protocol gain breakdown")
    if not ok:
        all_ok = False
        print("❌ Protocol Φ‑gain validation failed:")
        for e in errs:
            print("   -", e)
    else:
        print("✅ Protocol Φ‑gain validation passed.")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())