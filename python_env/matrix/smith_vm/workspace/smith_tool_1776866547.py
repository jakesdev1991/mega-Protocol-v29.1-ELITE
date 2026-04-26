# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Tokamak Governor Constants
-----------------------------------------------------------------
Checks:
  - SHOCK_LIMIT in [0.80, 0.85]   (noise immunity & detection latency)
  - VAA_SENSITIVITY ≤ 1.20        (prevent runaway amplification)
  - MANIFOLD_DIVERGENCE in [0, 1] (physically meaningful switch window)
  - Projected global AUC > 0.85   (Φ_N invariant)
  - Projected problematic-shot AUC > 0.5 (Φ_Delta invariant)
  - Optional: simple penalty J* = max(0, VAA_SENSITIVITY-1.2)^2 + ...
"""

import math

# ------------------- Engineer's constants -------------------
SHOCK_LIMIT        = 0.82
VAA_SENSITIVITY   = 1.15
MANIFOLD_DIVERGENCE = 0.35

# ------------------- Invariant thresholds -------------------
SHOCK_MIN, SHOCK_MAX = 0.80, 0.85
VAA_MAX              = 1.20
MANIFOLD_MIN, MANIFOLD_MAX = 0.0, 1.0
AUC_GLOBAL_TARGET    = 0.85
AUC_PROBLEM_TARGET   = 0.5   # "no critical failure" baseline

# ------------------- Linear‑gain AUC model -------------------
# Calibration points from the Engineer's narrative:
#   Baseline global AUC = 0.6793
#   Experimental v27.5-EX gave +102% gain on problematic shot (T093727)
#   They model contributions as:
#       ΔAUC_SHOCK   ≈ 0.02  (from SHOCK_LIMIT 0.85 → 0.82)
#       ΔAUC_VAA     ≈ 0.015 (from VAA_SENSITIVITY 1.0 → 1.15)
#       ΔAUC_SYNERGY ≈ 0.025 (joint coupling)
#   Total projected ΔAUC ≈ 0.06 → 0.6793 + 0.06 ≈ 0.7393? 
#   However they claim final 0.91 after also counting VAA gain on problematic shot etc.
#   To stay faithful to their claim we reproduce their *projected* numbers:
BASELINE_GLOBAL_AUC = 0.6793
BASELINE_PROBLEM_AUC = 0.3391   # T093727 reversed signal

# Contributions as stated in the internal thought process:
DELTA_AUC_SHOCK      = 0.02   # ≈ +3% global
DELTA_AUC_VAA        = 0.015  # ≈ +2% global
DELTA_AUC_SYNERGY    = 0.025  # extra coupling gain
DELTA_AUC_PROBLEM_SHOCK   = 0.10  # approximated from +102% gain on T093727
DELTA_AUC_PROBLEM_VAA     = 0.12  # additional VAA boost on problematic shot
DELTA_AUC_PROBLEM_SYNERGY = 0.08  # joint effect on problematic shot

# Projected AUCs
proj_global_auc = BASELINE_GLOBAL_AUC + DELTA_AUC_SHOCK + DELTA_AUC_VAA + DELTA_AUC_SYNERGY
proj_problem_auc = BASELINE_PROBLEM_AUC + DELTA_AUC_PROBLEM_SHOCK + DELTA_AUC_PROBLEM_VAA + DELTA_AUC_PROBLEM_SYNERGY

# ------------------- Validation routine -------------------
def check_invariant(name, value, lo=None, hi=None, gt=None, lt=None):
    ok = True
    if lo is not None and value < lo:
        ok = False
        print(f"[FAIL] {name}: {value} < lower bound {lo}")
    if hi is not None and value > hi:
        ok = False
        print(f"[FAIL] {name}: {value} > upper bound {hi}")
    if gt is not None and value <= gt:
        ok = False
        print(f"[FAIL] {name}: {value} ≤ {gt} (must be >)")
    if lt is not None and value >= lt:
        ok = False
        print(f"[FAIL] {name}: {value} ≥ {lt} (must be <)")
    if ok:
        print(f"[PASS] {name}: {value}")
    return ok

def main():
    print("=== Omega Protocol Invariant Check ===")
    all_ok = True

    # Basic bounds
    all_ok &= check_invariant("SHOCK_LIMIT", SHOCK_LIMIT,
                              lo=SHOCK_MIN, hi=SHOCK_MAX)
    all_ok &= check_invariant("VAA_SENSITIVITY", VAA_SENSITIVITY,
                              lt=VAA_MAX+1e-12)  # strictly < max+epsilon
    all_ok &= check_invariant("MANIFOLD_DIVERGENCE", MANIFOLD_DIVERGENCE,
                              lo=MANIFOLD_MIN, hi=MANIFOLD_MAX)

    # AUC projections
    all_ok &= check_invariant("Projected Global AUC", proj_global_auc,
                              gt=AUC_GLOBAL_TARGET)
    all_ok &= check_invariant("Projected Problematic Shot AUC", proj_problem_auc,
                              gt=AUC_PROBLEM_TARGET)

    # Simple penalty J* (quadratic excess over limits)
    J_penalty = max(0.0, VAA_SENSITIVITY - VAA_MAX)**2 \
                + max(0.0, SHOCK_MIN - SHOCK_LIMIT)**2 \
                + max(0.0, SHOCK_LIMIT - SHOCK_MAX)**2
    print(f"[INFO] Stability penalty J* = {J_penalty:.6f} (0 = perfect)")

    if all_ok:
        print("\nRESULT: All Omega Protocol invariants SATISFIED.")
    else:
        print("\nRESULT: ONE OR MORE INVARIANTS VIOLATED.")
        raise SystemExit(1)

if __name__ == "__main__":
    main()