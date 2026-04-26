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
Validates:
  1. Constant values are within declared stability bounds.
  2. Step changes match the narrative priors.
  3. AUC projection uses a mathematically sound aggregation model.
     (Here we test the linear-additive model implicitly used in the engine's
      reasoning; if the model fails, we flag the projection as unsound.)
"""

# ----- INPUT: Engine's proposed constants -----
SHOCK_LIMIT = 0.82
VAA_SENSITIVITY = 1.15
MANIFOLD_DIVERGENCE = 0.35

# ----- PRIOR VALUES (as stated in engine's internal thought) -----
SHOCK_LIMIT_PRIOR = 0.85
VAA_SENSITIVITY_PRIOR = 1.0
MANIFOLD_DIVERGENCE_PRIOR = 0.3

# ----- STABILITY BOUNDS (claimed by engine, attributed to "Smith's audit") -----
SHOCK_LIMIT_MIN = 0.80   # lower bound to avoid excessive false positives
VAA_SENSITIVITY_MAX = 1.2  # upper bound to avoid runaway amplification
MANIFOLD_DIVERGENCE_MIN = 0.0
MANIFOLD_DIVERGENCE_MAX = 1.0

# ----- AUC BASELINE AND CLAIMED IMPROVEMENTS -----
AUC_BASELINE_GLOBAL = 0.6793
AUC_BASELINE_PROBLEM = 0.3391  # T093727

# Engine's claimed percentage gains (as written)
GAIN_SHOCK_LIMIT_PCT = 5.5   # from shock optimization
GAIN_VAA_SENSITIVITY_PCT = 2.3 # from VAA tuning
# The engine then incorrectly adds a second baseline (0.89) – we treat this as an error.

# Engine's claimed final AUCs (as stated)
AUC_FINAL_GLOBAL_CLAIMED = 0.91
AUC_FINAL_PROBLEM_CLAIMED = 0.71

def check_bounds(name, value, low, high):
    if not (low <= value <= high):
        return f"FAIL: {name}={value} outside [{low}, {high}]"
    return f"PASS: {name} within bounds"

def check_step(name, current, prior, expected_delta=None):
    delta = current - prior
    if expected_delta is not None and not abs(delta - expected_delta) < 1e-9:
        return f"FAIL: {name} step delta={delta:.5f}, expected {expected_delta:.5f}"
    return f"PASS: {name} step delta={delta:.5f}"

def linear_auc_projection(baseline, *percent_gains):
    """
    Simulates the engine's implicit linear-additive model:
        AUC_final = baseline + sum(baseline * gain_i/100)
    This is equivalent to baseline * (1 + sum(gain_i)/100)
    """
    total_gain = sum(percent_gains)
    return baseline * (1.0 + total_gain / 100.0)

def main():
    print("=== Omega Protocol Constant Validation ===\n")

    # 1. Bound checks
    print(check_bounds("SHOCK_LIMIT", SHOCK_LIMIT, SHOCK_LIMIT_MIN, 1.0))
    print(check_bounds("VAA_SENSITIVITY", VAA_SENSITIVITY, 0.0, VAA_SENSITIVITY_MAX))
    print(check_bounds("MANIFOLD_DIVERGENCE", MANIFOLD_DIVERGENCE,
                       MANIFOLD_DIVERGENCE_MIN, MANIFOLD_DIVERGENCE_MAX))
    print()

    # 2. Step consistency with priors
    print(check_step("SHOCK_LIMIT", SHOCK_LIMIT, SHOCK_LIMIT_PRIOR,
                     expected_delta=SHOCK_LIMIT - SHOCK_LIMIT_PRIOR))
    print(check_step("VAA_SENSITIVITY", VAA_SENSITIVITY, VAA_SENSITIVITY_PRIOR,
                     expected_delta=VAA_SENSITIVITY - VAA_SENSITIVITY_PRIOR))
    print(check_step("MANIFOLD_DIVERGENCE", MANIFOLD_DIVERGENCE,
                     MANIFOLD_DIVERGENCE_PRIOR,
                     expected_delta=MANIFOLD_DIVERGENCE - MANIFOLD_DIVERGENCE_PRIOR))
    print()

    # 3. AUC projection sanity check (linear-additive model)
    projected_global = linear_auc_projection(
        AUC_BASELINE_GLOBAL,
        GAIN_SHOCK_LIMIT_PCT,
        GAIN_VAA_SENSITIVITY_PCT
    )
    projected_problem = linear_auc_projection(
        AUC_BASELINE_PROBLEM,
        GAIN_SHOCK_LIMIT_PCT,
        GAIN_VAA_SENSITIVITY_PCT
    )

    print("--- AUC Projection (linear-additive model) ---")
    print(f"Baseline Global AUC: {AUC_BASELINE_GLOBAL:.4f}")
    print(f"Claimed gains: shock {GAIN_SHOCK_LIMIT_PCT}% + VAA {GAIN_VAA_SENSITIVITY_PCT}%")
    print(f"Projected Global AUC: {projected_global:.4f}")
    print(f"Claimed Final Global AUC: {AUC_FINAL_GLOBAL_CLAIMED:.4f}")
    print(f"Match? {'PASS' if abs(projected_global - AUC_FINAL_GLOBAL_CLAIMED) < 1e-3 else 'FAIL'}")
    print()
    print(f"Baseline Problematic Shot AUC: {AUC_BASELINE_PROBLEM:.4f}")
    print(f"Projected Problematic AUC: {projected_problem:.4f}")
    print(f"Claimed Final Problematic AUC: {AUC_FINAL_PROBLEM_CLAIMED:.4f}")
    print(f"Match? {'PASS' if abs(projected_problem - AUC_FINAL_PROBLEM_CLAIMED) < 1e-3 else 'FAIL'}")
    print()

    # Overall verdict: if any core check fails, we FAIL
    fail_conditions = [
        "FAIL:" in check_bounds("SHOCK_LIMIT", SHOCK_LIMIT, SHOCK_LIMIT_MIN, 1.0),
        "FAIL:" in check_bounds("VAA_SENSITIVITY", VAA_SENSITIVITY, 0.0, VAA_SENSITIVITY_MAX),
        "FAIL:" in check_bounds("MANIFOLD_DIVERGENCE", MANIFOLD_DIVERGENCE,
                                MANIFOLD_DIVERGENCE_MIN, MANIFOLD_DIVERGENCE_MAX),
        "FAIL:" in check_step("SHOCK_LIMIT", SHOCK_LIMIT, SHOCK_LIMIT_PRIOR),
        "FAIL:" in check_step("VAA_SENSITIVITY", VAA_SENSITIVITY, VAA_SENSITIVITY_PRIOR),
        "FAIL:" in check_step("MANIFOLD_DIVERGENCE", MANIFOLD_DIVERGENCE,
                              MANIFOLD_DIVERGENCE_PRIOR),
        "FAIL" in f"{'PASS' if abs(projected_global - AUC_FINAL_GLOBAL_CLAIMED) < 1e-3 else 'FAIL'}",
        "FAIL" in f"{'PASS' if abs(projected_problem - AUC_FINAL_PROBLEM_CLAIMED) < 1e-3 else 'FAIL'}"
    ]

    overall = "FAIL" if any(fail_conditions) else "PASS"
    print(f"=== OVERALL VERDICT: {overall} ===")
    if overall == "FAIL":
        print("Reason: One or more invariant checks failed (bounds, step consistency, or AUC projection).")
    else:
        print("All checks passed; the constants are mathematically sound under the assumed linear model.")

if __name__ == "__main__":
    main()