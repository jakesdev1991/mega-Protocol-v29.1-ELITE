# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol v57.0 – Covariant Decomposition Validator for FSG‑v57
# Checks the mathematical soundness of the proposed Φ-density formula:
#   Φ_net = log2(COD) + ψ * tanh(R_align/R_max) - ΔS_audit
#   where ψ = ln(Φ_N) and Φ_N = log2(COD)
#
# Invariants enforced:
#   1. COD ∈ (0, 1]   (fidelity squared, bounded)
#   2. Φ_N = log2(COD) must be > 0  →  ψ = ln(Φ_N) defined and finite
#   3. ψ must be a real scalar (no singularities)
#   4. tanh argument is dimensionless; output ∈ (-1, 1)
#   5. ΔS_audit ≥ 0 (Landauer cost, non‑negative)
#   6. Φ_net must be finite (no ±inf or NaN)
#
# If any invariant fails → META-FAIL, else META-PASS.

import math
import numpy as np

def validate_fsg_v57(COD, R_align, R_max, delta_S_audit):
    """
    Returns (bool_pass, dict_of_violations)
    """
    violations = {}

    # 1. COD bounds (fidelity squared)
    if not (0 < COD <= 1.0):
        violations["COD_bounds"] = f"COD={COD} must be in (0, 1]"

    # 2. Φ_N = log2(COD) must be > 0 for ψ = ln(Φ_N) to be real
    Phi_N = math.log2(COD) if COD > 0 else -float('inf')
    if Phi_N <= 0:
        violations["Phi_N_positive"] = f"Φ_N=log2(COD)={Phi_N} must be > 0 (so that ln(Φ_N) is defined)"

    # 3. ψ = ln(Φ_N) must be finite real
    if "Phi_N_positive" not in violations:
        psi = math.log(Phi_N)
        if not math.isfinite(psi):
            violations["psi_finite"] = f"ψ=ln(Φ_N)={psi} is not finite"

    # 4. tanh argument dimensionless & output bounded
    if R_max == 0:
        violations["R_max_zero"] = "R_max cannot be zero (division by zero)"
    else:
        arg = R_align / R_max
        tanh_val = math.tanh(arg)
        if not (-1 <= tanh_val <= 1):
            violations["tanh_bounds"] = f"tanh({arg})={tanh_val} out of [-1,1]"

    # 5. Audit cost non‑negative
    if delta_S_audit < 0:
        violations["DeltaS_audit_nonneg"] = f"ΔS_audit={delta_S_audit} must be ≥ 0"

    # 6. Φ_net finite (only compute if no prior critical violations)
    if not any(k in violations for k in ["COD_bounds", "Phi_N_positive", "psi_finite", "R_max_zero"]):
        Phi_N = math.log2(COD)
        psi = math.log(Phi_N)
        tanh_val = math.tanh(R_align / R_max) if R_max != 0 else 0.0
        Phi_net = Phi_N + psi * tanh_val - delta_S_audit
        if not math.isfinite(Phi_net):
            violations["Phi_net_finite"] = f"Φ_net={Phi_net} is not finite"

    passed = len(violations) == 0
    return passed, violations

# Example test sweep (including edge cases)
test_cases = [
    # nominally valid region (should still fail because Φ_N ≤ 0 for COD<1)
    {"COD": 0.5, "R_align": 0.2, "R_max": 1.0, "delta_S_audit": 0.01},
    {"COD": 1.0, "R_align": 0.0, "R_max": 1.0, "delta_S_audit": 0.0},
    {"COD": 0.9, "R_align": 0.5, "R_max": 0.5, "delta_S_audit": 0.0},
    # boundary COD → 0 (should trigger COD_bounds and Phi_N_positive)
    {"COD": 1e-12, "R_align": 0.1, "R_max": 1.0, "delta_S_audit": 0.0},
    # R_max = 0 (division by zero)
    {"COD": 0.8, "R_align": 0.1, "R_max": 0.0, "delta_S_audit": 0.0},
    # negative audit cost
    {"COD": 0.8, "R_align": 0.1, "R_max": 1.0, "delta_S_audit": -0.01},
]

all_pass = True
for i, tc in enumerate(test_cases):
    ok, viol = validate_fsg_v57(**tc)
    print(f"Test {i+1}: COD={tc['COD']}, R_align={tc['R_align']}, R_max={tc['R_max']}, ΔS_audit={tc['delta_S_audit']}")
    if ok:
        print("  → META-PASS (all invariants satisfied)")
    else:
        all_pass = False
        print("  → META-FAIL")
        for k, v in viol.items():
            print(f"     * {k}: {v}")

print("\nOverall verdict:", "META-PASS" if all_pass else "META-FAIL (covariant structure violated)")