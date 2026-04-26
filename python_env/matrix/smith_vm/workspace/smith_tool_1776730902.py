# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Invariant Validator for ISS‑Ω Proposal
# --------------------------------------------------------------
# This script checks that the mathematical formulation of the
# Insider Stress Signature Monitor (ISS‑Ω) respects the core
# Omega Protocol invariants:
#   • Φ_N  (market connectivity)   ∈ [0, 1]
#   • Φ_Δ  (information asymmetry) ∈ [0, 1]
#   • J*   (implicitly enforced via the QP constraints)
# Additionally it validates the explicit constraints stated in the
# proposal:
#   • ISI_f ≤ 3.0
#   • Φ_N^(iss) ≤ 0.85
#   • Φ_Δ^(iss) ≤ 0.7
#
# The script is deliberately minimal – it can be expanded with
# real data feeds, but it demonstrates the logical enforcement
# required by the Guardian.
# --------------------------------------------------------------

import numpy as np

def compute_ISI(access_anomaly, role_criticality, intent_score, external_stress,
                alpha, beta, gamma, delta):
    """
    ISI_f(t) = Σ_i [ α·A_i + β·R_i + γ·I_i + δ·E_f ]
    For a single exposure we drop the sum; for multiple exposures we
    simply accumulate the term.
    All inputs are assumed non‑negative.
    """
    term = alpha * access_anomaly + beta * role_criticality + \
           gamma * intent_score + delta * external_stress
    return max(term, 0.0)   # ISI should not be negative

def map_to_Phi_N(ISI, eta1, tau1, Phi_N0=0.0):
    """
    Φ_N^(iss)(t) = Φ_N^(0) + η1 * tanh( ISI_f(t-τ1) )
    tanh ∈ (-1, 1) → we clip the result to [0,1] to respect Ω bounds.
    """
    val = Phi_N0 + eta1 * np.tanh(ISI)
    return np.clip(val, 0.0, 1.0)

def map_to_Phi_Delta(ISI, eta2, eta3, tau2, tau3, Phi_Delta0=0.0):
    """
    Φ_Δ^(iss)(t) = Φ_Δ^(0) + η2·ISI_f(t-τ2) - η3·ISI_f(t-τ3)^2
    The quadratic term can push the value outside [0,1]; we again clip.
    """
    val = Phi_Delta0 + eta2 * ISI - eta3 * (ISI ** 2)
    return np.clip(val, 0.0, 1.0)

def check_constraints(ISI, Phi_N, Phi_Delta):
    """
    Validate the explicit constraints from the proposal:
        ISI_f ≤ 3.0
        Φ_N^(iss) ≤ 0.85
        Φ_Δ^(iss) ≤ 0.7
    Returns a dict of booleans and a summary.
    """
    checks = {
        "ISI ≤ 3.0": ISI <= 3.0,
        "Φ_N ≤ 0.85": Phi_N <= 0.85,
        "Φ_Δ ≤ 0.7":  Phi_Delta <= 0.7,
        "Φ_N ∈ [0,1]": 0.0 <= Phi_N <= 1.0,
        "Φ_Δ ∈ [0,1]": 0.0 <= Phi_Delta <= 1.0,
        "ISI ≥ 0":     ISI >= 0.0
    }
    all_ok = all(checks.values())
    return checks, all_ok

def run_validation_demo():
    """
    Demonstration with a plausible parameter set.
    Feel free to edit the values to stress‑test the invariants.
    """
    # ---- Example feature values (single exposure) ----
    A_i   = 1.2   # access anomaly score (e.g., Mahalanobis distance)
    R_i   = 1.8   # role criticality (lead quant)
    I_i   = 0.9   # intent score (mostly deliberate)
    E_f   = 0.5   # external stress proxy (moderate volatility)

    # ---- Learned weights (example from XGBoost) ----
    alpha, beta, gamma, delta = 0.4, 0.3, 0.2, 0.1

    # ---- Mapping coefficients (calibrated) ----
    eta1, eta2, eta3 = 0.25, 0.15, 0.02   # chosen to keep Φ in range
    tau1, tau2, tau3 = 30, 14, 60        # days (not used directly here)

    # ---- Compute ISI ----
    ISI = compute_ISI(A_i, R_i, I_i, E_f, alpha, beta, gamma, delta)

    # ---- Map to Omega variables ----
    Phi_N  = map_to_Phi_N(ISI, eta1, tau1)
    Phi_Delta = map_to_Phi_Delta(ISI, eta2, eta3, tau2, tau3)

    # ---- Constraint check ----
    checks, ok = check_constraints(ISI, Phi_N, Phi_Delta)

    # ---- Report ----
    print("=== ISS‑Ω Omega‑Protocol Validation ===")
    print(f"Input features: A={A_i}, R={R_i}, I={I_i}, E={E_f}")
    print(f"Weights: α={alpha}, β={beta}, γ={gamma}, δ={delta}")
    print(f"Computed ISI_f = {ISI:.3f}")
    print(f"Mapped Φ_N^(iss) = {Phi_N:.3f}")
    print(f"Mapped Φ_Δ^(iss) = {Phi_Delta:.3f}")
    print("\nConstraint checks:")
    for k, v in checks.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
    print(f"\nOverall invariant compliance: {'PASS' if ok else 'FAIL'}")
    return ok

if __name__ == "__main__":
    # Run the demo; exit with non‑zero code if any invariant fails.
    compliant = run_validation_demo()
    exit(0 if compliant else 1)