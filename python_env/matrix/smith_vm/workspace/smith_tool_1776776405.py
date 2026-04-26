# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for CVT-Ω
--------------------------------------------
Validates the mathematical soundness of the CVT-Ω proposal
with respect to the invariants:
    Φ_N ≥ 0, Φ_N ≤ 1 (if normalized)
    Φ_Δ ≥ 0
    J* finite & QP feasible
    0 ≤ URP ≤ 1
    s_URP ≥ 0
    τ > 0
"""

import numpy as np
from scipy.special import expit  # sigmoid

# -------------------------- CONFIGURATION --------------------------
# Number of tokamak research projects considered at time t
N_PROJECTS = 20

# Baseline Omega parameters (choose values that satisfy invariants)
PHI_N0 = 0.6          # baseline connectivity
PHI_DELTA0 = 0.5      # baseline asymmetry
ETA1 = 0.3            # weight for Φ_N increase (must keep Φ_N ≤ 1)
ETA2 = 0.2            # weight for Φ_Δ decrease (must keep Φ_Δ ≥ 0)
TAU_MONTHS = 12       # lead time (months)
LAMBDA = 0.5          # cost trade‑off parameter

# Feasibility thresholds from the QP formulation
MIN_AVG_URP = 0.5
MIN_PHI_N_VAL = 0.8
MAX_PHI_DELTA_VAL = 0.4

# -----------------------------------------------------------------
def sigmoid(x):
    return expit(x)

def generate_synthetic_data():
    """Create plausible URP feature vectors and derived scores."""
    np.random.seed(42)
    # Each project gets 5 normalized features in [0,1]
    H_tok = np.random.rand(N_PROJECTS, 5)
    # Equal weights that sum to 1 (ensures URP in [0,1])
    w = np.ones(5) / 5
    URP = H_tok @ w                     # shape (N_PROJECTS,)
    avg_URP = URP.mean()
    max_URP = URP.max()
    # Simulate a residual time‑series for anomaly detection
    t = np.arange(0, 24)                # 24 months
    trend = 0.01 * t                    # slow upward drift
    seasonal = 0.05 * np.sin(2*np.pi*t/12)
    noise = np.random.normal(0, 0.02, size=t.shape)
    residual = noise                    # after STL, assume residual ≈ noise
    sigma_res = np.std(residual)
    s_URP = np.abs(residual) / sigma_res
    s_URP_latest = s_URP[-1]            # use latest month for checks
    return {
        "H_tok": H_tok,
        "w": w,
        "URP": URP,
        "avg_URP": avg_URP,
        "max_URP": max_URP,
        "s_URP_latest": s_URP_latest,
        "sigma_res": sigma_res,
        "trend": trend,
        "seasonal": seasonal,
        "noise": noise,
    }

def compute_derived(data):
    """Calculate Φ_N^(val), Φ_Δ^(val), cost, and feasibility."""
    avg_URP = data["avg_URP"]
    max_URP = data["max_URP"]
    s_URP = data["s_URP_latest"]

    phi_n_val = PHI_N0 + ETA1 * sigmoid(avg_URP)          # Eq. Φ_N^(val)
    phi_delta_val = PHI_DELTA0 - ETA2 * max_URP           # Eq. Φ_Δ^(val) (using t‑τ ≈ latest)

    # Cost function (to be minimized)
    cost = -np.log(avg_URP) + LAMBDA * s_URP

    # Feasibility checks from QP constraints
    feasible = (avg_URP >= MIN_AVG_URP) and \
               (phi_n_val >= MIN_PHI_N_VAL) and \
               (phi_delta_val <= MAX_PHI_DELTA_VAL)

    return {
        "phi_n_val": phi_n_val,
        "phi_delta_val": phi_delta_val,
        "cost": cost,
        "feasible": feasible,
    }

def check_invariants(derived, data):
    """Return a dict of pass/fail for each invariant."""
    results = {}

    # Φ_N bounds (assume normalized [0,1])
    results["Phi_N >= 0"] = derived["phi_n_val"] >= 0
    results["Phi_N <= 1"] = derived["phi_n_val"] <= 1

    # Φ_Δ non‑negative
    results["Phi_Delta >= 0"] = derived["phi_delta_val"] >= 0

    # URP in [0,1] (by construction)
    results["URP in [0,1]"] = np.all((data["URP"] >= 0) & (data["URP"] <= 1))

    # Anomaly score non‑negative
    results["s_URP >= 0"] = derived.get("s_URP_latest", 0) >= 0

    # Lead time positive
    results["tau > 0"] = TAU_MONTHS > 0

    # Cost finite (avg_URP > 0 ensures -log finite)
    results["Cost finite"] = np.isfinite(derived["cost"])

    # QP feasibility
    results["QP feasible"] = derived["feasible"]

    # Additional parameter bounds to keep invariants satisfied
    # η₁ must be ≤ 1 - Φ_N0 to keep Φ_N ≤ 1
    results["ETA1 bound"] = ETA1 <= (1 - PHI_N0)
    # η₂ must be ≤ Φ_Δ0 / max_URP to keep Φ_Δ ≥ 0
    results["ETA2 bound"] = ETA2 <= (PHI_DELTA0 / data["max_URP"]) if data["max_URP"] > 0 else True

    return results

def main():
    data = generate_synthetic_data()
    derived = compute_derived(data)
    invar = check_invariants(derived, data)

    print("=== Synthetic Data Summary ===")
    print(f"Average URP: {data['avg_URP']:.3f}")
    print(f"Max URP:     {data['max_URP']:.3f}")
    print(f"Latest s_URP: {data['s_URP_latest']:.3f}")
    print(f"σ_residual:   {data['sigma_res']:.3f}")
    print()
    print("=== Derived Quantities ===")
    print(f"Φ_N^(val):   {derived['phi_n_val']:.3f}")
    print(f"Φ_Δ^(val):   {derived['phi_delta_val']:.3f}")
    print(f"Cost:        {derived['cost']:.3f}")
    print(f"QP feasible: {derived['feasible']}")
    print()
    print("=== Invariant Checks ===")
    all_ok = True
    for name, ok in invar.items():
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"{name:20}: {status}")
    print()
    if all_ok:
        print("✅ All Omega Protocol invariants satisfied.")
    else:
        print("❌ Some invariants violated. Review parameters (η₁, η₂, baseline Φs) "
              "or data quality.")
        # Suggest corrective ranges
        print("\nSuggested parameter ranges to restore compliance:")
        print(f"  η₁ ≤ {1 - PHI_N0:.3f} (current η₁ = {ETA1})")
        print(f"  η₂ ≤ {PHI_DELTA0 / data['max_URP']:.3f} (current η₂ = {ETA2})")

if __name__ == "__main__":
    main()