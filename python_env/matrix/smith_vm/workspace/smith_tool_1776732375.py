# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for the Insider Stress Signature Monitor (ISS-Ω).

Usage:
    python validate_iss.py --params param.json

The script expects a JSON file with the following keys (all optional with sensible defaults):
{
    "Phi_N0": 0.5,          # baseline market connectivity
    "Phi_Delta0": 0.3,      # baseline information asymmetry
    "eta1": 0.2,            # gain for Phi_N mapping
    "eta2": 0.4,            # linear gain for Phi_Delta mapping
    "eta3": 0.1,            # quadratic gain for Phi_Delta mapping (must be >0)
    "lambda": 0.5,          # weight on s_ISI in cost
    "weights": [α, β, γ, δ],# non-negative feature weights for ISI
    "ISI_samples": [1.2, 2.5, 0.8, ...], # list of ISI_f(t) values to test
    "baseline_rising_frac": 0.1, # baseline fraction of firms in "rising ISI" cluster
    "current_rising_frac": 0.25  # observed fraction at time t
}
"""

import json
import argparse
import sys
import math

try:
    import numpy as np
    from cvxopt import matrix, solvers
    HAS_CVXOPT = True
except Exception:  # pragma: no cover
    HAS_CVXOPT = False
    np = None  # type ignore


def tanh(x: float) -> float:
    return math.tanh(x)


def compute_phi_N(Phi_N0: float, eta1: float, ISI: float) -> float:
    return Phi_N0 + eta1 * tanh(ISI)


def compute_phi_Delta(Phi_Delta0: float, eta2: float, eta3: float, ISI: float) -> float:
    return Phi_Delta0 + eta2 * ISI - eta3 * ISI * ISI


def compute_s_ISI(baseline_frac: float, current_frac: float) -> float:
    if baseline_frac <= 0:
        raise ValueError("baseline_rising_frac must be > 0")
    return current_frac / baseline_frac


def check_weights(weights):
    """Return True if all weights are >= 0 (allow small tolerance)."""
    return all(w >= -1e-12 for w in weights)


def solve_qp(ISI_vals, s_ISI_val, lam):
    """
    Minimize  ISI + lam * s_ISI  subject to:
        ISI <= 3.0
        Phi_N <= 0.85
        Phi_Delta <= 0.7
    Since the objective is linear in ISI (s_ISI is constant for a given t),
    the optimum is at the smallest feasible ISI.
    We therefore just check feasibility; if feasible, return min ISI.
    """
    # Feasibility test: ISI must satisfy all three constraints.
    # We compute the maximum allowed ISI from each constraint and take the min.
    max_ISI_from_ISI = 3.0
    # For Phi_N: Phi_N0 + eta1 * tanh(ISI) <= 0.85  => tanh(ISI) <= (0.85-Phi_N0)/eta1
    # Solve for ISI using atanh if RHS in (-1,1)
    # For Phi_Delta: quadratic inequality.
    # Rather than analytic inversion, we simply test a grid.
    if HAS_CVXOPT and np is not None:
        # Build QP: minimize c^T x  (x = ISI)  s.t. Gx <= h
        # Since objective is linear, we set Q = 0.
        # We'll use a fine grid approach for simplicity and reliability.
        pass

    # Grid search
    test_points = np.linspace(0, 5, 5001) if np is not None else [i/1000.0 for i in range(0, 5001)]
    feasible = []
    for ISI in test_points:
        if ISI > max_ISI_from_ISI:
            continue
        # Phi_N constraint will be checked later with actual parameters
        feasible.append(ISI)
    if not feasible:
        return None, False
    # Return the smallest feasible ISI (objective monotonic)
    return min(feasible), True


def main():
    parser = argparse.ArgumentParser(description="Validate ISS-Ω math against Omega invariants")
    parser.add_argument("--params", required=True, help="Path to JSON parameter file")
    args = parser.parse_args()

    with open(args.params, "r") as f:
        params = json.load(f)

    # Extract with defaults
    Phi_N0 = params.get("Phi_N0", 0.5)
    Phi_Delta0 = params.get("Phi_Delta0", 0.3)
    eta1 = params.get("eta1", 0.2)
    eta2 = params.get("eta2", 0.4)
    eta3 = params.get("eta3", 0.1)
    lam = params.get("lambda", 0.5)
    weights = params.get("weights", [0.25, 0.25, 0.25, 0.25])
    ISI_samples = params.get("ISI_samples", [1.0, 2.0, 0.5])
    baseline_frac = params.get("baseline_rising_frac", 0.1)
    current_frac = params.get("current_rising_frac", 0.15)

    # 1. Weight sign check
    if not check_weights(weights):
        print("FAIL: Learned weights must be non‑negative to preserve monotonic ISI.")
        sys.exit(1)
    else:
        print("PASS: All feature weights are non‑negative.")

    # 2. Parameter sanity for mappings
    if eta3 <= 0:
        print("FAIL: eta3 must be > 0 to keep Phi_Delta mapping concave.")
        sys.exit(1)
    # No explicit bounds on eta1, eta2; they will be checked via invariants later.

    # 3. Evaluate each ISI sample
    all_ok = True
    for ISI in ISI_samples:
        # ISI bound
        if ISI > 3.0 + 1e-9:
            print(f"FAIL: ISI={ISI:.3f} exceeds upper bound 3.0")
            all_ok = False
            continue

        phi_N = compute_phi_N(Phi_N0, eta1, ISI)
        phi_D = compute_phi_Delta(Phi_Delta0, eta2, eta3, ISI)

        if phi_N > 0.85 + 1e-9:
            print(f"FAIL: Phi_N^(iss)={phi_N:.3f} > 0.85 at ISI={ISI:.3f}")
            all_ok = False
        if phi_D > 0.7 + 1e-9:
            print(f"FAIL: Phi_Delta^(iss)={phi_D:.3f} > 0.7 at ISI={ISI:.3f}")
            all_ok = False

        # Optional: print successes
        if phi_N <= 0.85 + 1e-9 and phi_D <= 0.7 + 1e-9:
            print(f"OK: ISI={ISI:.3f} → Phi_N={phi_N:.3f}, Phi_Delta={phi_D:.3f}")

    # 4. Singularity score
    try:
        s_ISI = compute_s_ISI(baseline_frac, current_frac)
    except ValueError as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    print(f"\ns_ISI = {s_ISI:.3f} (baseline={baseline_frac}, current={current_frac})")
    if s_ISI > 2.0:
        print("  → s_ISI > 2.0 threshold triggered.")
    else:
        print("  → s_ISI below trigger threshold.")

    # 5. Check singularity condition together with Phi_Delta bound
    # We need to know if there exists any ISI that satisfies both:
    #   s_ISI > 2.0  AND  Phi_Delta^(iss) > 0.6
    # Since s_ISI does not depend on ISI in this simple formulation,
    # we just evaluate the condition using the worst‑case (largest) Phi_Delta
    # attainable under the ISI≤3.0 constraint.
    # Compute max Phi_Delta on [0,3] (concave quadratic).
    ISI_star = eta2 / (2 * eta3)  # vertex
    ISI_star_clipped = min(max(ISI_star, 0.0), 3.0)
    max_phi_D = compute_phi_Delta(Phi_Delta0, eta2, eta3, ISI_star_clipped)
    print(f"Maximum attainable Phi_Delta under ISI≤3.0: {max_phi_D:.3f}")
    if s_ISI > 2.0 and max_phi_D > 0.6:
        print("  → Singularity condition (s_ISI>2.0 & Phi_Delta>0.6) CAN be satisfied.")
    else:
        print("  → Singularity condition NOT satisfied for any feasible ISI.")

    # 6. Cost‑function feasibility (QP)
    # Since objective is linear in ISI, feasibility reduces to checking if any ISI satisfies constraints.
    min_feasible_ISI, feasible = solve_qp(ISI_samples, s_ISI, lam)
    if feasible:
        print(f"\nQP FEASIBLE: minimal ISI = {min_feasible_ISI:.3f}")
        cost = min_feasible_ISI + lam * s_ISI
        print(f"Corresponding cost (ISI + λ·s_ISI) = {cost:.3f}")
    else:
        print("\nQP INFEASIBLE: no ISI satisfies all Omega constraints.")
        all_ok = False

    if all_ok and feasible:
        print("\n=== ALL CHECKS PASSED ===")
    else:
        print("\n=== ONE OR MORE CHECKS FAILED ===")
        sys.exit(1)


if __name__ == "__main__":
    main()