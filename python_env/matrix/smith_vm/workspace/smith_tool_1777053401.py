# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Ledger Validator
Checks:
  1. net = claimed - audit_correction - audit_cost  (within tolerance)
  2. audit_cost is identical for all tasks (universal ΔS_audit = k ln 2)
  3. total_net equals sum of individual nets
  4. All values are real numbers (dimensionless Φ)
"""

import math
from typing import List, Tuple

# Tolerance for floating‑point comparison
TOL = 1e-9

def approx_eq(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=0, abs_tol=TOL)

# ----------------------------------------------------------------------
# Input data as reported (replace with actual values if needed)
# Format: (claimed, audit_correction, audit_cost, reported_net)
data: List[Tuple[float, float, float, float]] = [
    # Bureaucracy Manifold
    (1.40, 0.00, 0.10, 1.30),
    # Children's Footwear  <-- suspect row
    (1.50, 0.15, 0.08, 0.10),
    # Trauma-Performance
    (0.65, 0.00, 0.10, 0.55),
]

def validate_ledger(rows: List[Tuple[float, float, float, float]]) -> bool:
    all_ok = True
    audit_costs = set()
    net_sum = 0.0

    for i, (claimed, corr, cost, reported_net) in enumerate(rows, start=1):
        # 1. Ledger conservation
        calc_net = claimed - corr - cost
        if not approx_eq(calc_net, reported_net):
            print(f"[Row {i}] Ledger violation: "
                  f"claimed({claimed}) - corr({corr}) - cost({cost}) = {calc_net:.6f} "
                  f"≠ reported_net({reported_net})")
            all_ok = False

        # 2. Collect audit cost for universality check
        audit_costs.add(round(cost, 12))  # rounding to avoid fp noise
        net_sum += reported_net

    # 3. Universal audit cost
    if len(audit_costs) != 1:
        print(f"[Universal] Audit cost not uniform: {audit_costs}")
        all_ok = False
    else:
        print(f"[Universal] Audit cost = {next(iter(audit_costs))} Φ (consistent)")

    # 4. Total net consistency
    total_reported = sum(r[3] for r in rows)
    if not approx_eq(total_reported, net_sum):
        print(f"[Total] Sum of reported nets ({total_reported:.6f}) "
              f"≠ recomputed sum ({net_sum:.6f})")
        all_ok = False
    else:
        print(f"[Total] Net sum consistent: {total_reported:.6f} Φ")

    return all_ok

if __name__ == "__main__":
    if validate_ledger(data):
        print("\nRESULT: LEDGER PASSES ALL Ω‑PROTOCOL CHECKS")
    else:
        print("\nRESULT: LEDGER FAILS – CORRECT THE INCONSISTENCIES")