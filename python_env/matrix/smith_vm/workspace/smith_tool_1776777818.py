# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Φ‑budget validator.
Checks internal consistency of cost, gain, %‑gain, baseline, and break‑even claims.
"""

import math
from typing import Optional, Tuple

def validate_phi_budget(
    cost: float,
    total_gain: float,
    baseline_phi: Optional[float] = None,
    percent_gain: Optional[float] = None,   # expressed as fraction, e.g. 0.15 for 15%
    monthly_gain: Optional[float] = None,
    break_even_months: Optional[float] = None,
    tol: float = 1e-6
) -> Tuple[bool, str]:
    """
    Returns (is_compliant, message).
    """
    # ---- Invariant I1: Net Φ non‑negative ----
    net_phi = cost + total_gain
    if net_phi + tol < 0:   # allow tiny negative due to rounding
        return False, f"Invariant I1 violated: Net Φ = {net_phi:.2f} < 0"

    # ---- Invariant I2: Percent gain consistency ----
    if baseline_phi is not None and percent_gain is not None:
        expected_percent = net_phi / baseline_phi
        if not math.isclose(expected_percent, percent_gain, rel_tol=tol, abs_tol=tol):
            return False, (
                f"Invariant I2 violated: "
                f"Net Φ / baseline = {expected_percent:.6f}, "
                f"claimed % gain = {percent_gain:.6f}"
            )
    # If only one of baseline/percent_gain is given, we cannot test I2.

    # ---- Invariant I3: Break‑even consistency ----
    if monthly_gain is not None:
        if abs(monthly_gain) < tol:
            return False, "Invariant I3 invalid: monthly_gain cannot be zero."
        t_be_calc = -cost / monthly_gain   # cost is negative, so t_be positive
        if break_even_months is not None:
            if not math.isclose(t_be_calc, break_even_months, rel_tol=tol, abs_tol=tol):
                return False, (
                    f"Invariant I3 violated: "
                    f"calculated break‑even = {t_be_calc:.2f} mo, "
                    f"claimed = {break_even_months:.2f} mo"
                )
        # If no claimed break‑even, we just note the derived value.
    elif break_even_months is not None:
        # Can't test I3 without monthly_gain
        pass

    # All tested invariants passed
    msg = (
        f"Φ‑budget compliant.\n"
        f"  Cost = {cost:.2f} Φ\n"
        f"  Total gain (12 mo) = {total_gain:.2f} Φ\n"
        f"  Net Φ = {net_phi:.2f} Φ\n"
    )
    if baseline_phi is not None:
        msg += f"  Baseline Φ₀ = {baseline_phi:.2f} Φ\n"
    if percent_gain is not None:
        msg += f"  % gain claimed = {percent_gain*100:.2f}%\n"
    if monthly_gain is not None:
        msg += f"  Monthly gain = {monthly_gain:.2f} Φ/mo\n"
        msg += f"  Derived break‑even = {-cost/monthly_gain:.2f} mo\n"
    if break_even_months is not None:
        msg += f"  Claimed break‑even = {break_even_months:.2f} mo\n"
    return True, msg


if __name__ == "__main__":
    # ---- Values extracted from the agent's thought ----
    cost = -450.0                     # short‑term Φ cost
    total_gain = +820.0               # long‑term Φ gain over 12 mo
    baseline_phi = None               # not supplied
    percent_gain = 0.15               # +15 % claimed
    monthly_gain = total_gain / 12.0  # assume linear accrual
    break_even_claim = 3.0            # claimed break‑even ≈ 3 mo

    compliant, report = validate_phi_budget(
        cost=cost,
        total_gain=total_gain,
        baseline_phi=baseline_phi,
        percent_gain=percent_gain,
        monthly_gain=monthly_gain,
        break_even_months=break_even_claim
    )
    print(report)
    if not compliant:
        raise SystemExit("Ω‑Protocol violation: Φ‑budget inconsistent.")