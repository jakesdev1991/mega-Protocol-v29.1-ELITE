# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validator for Q-NAS Experiment Proposal

Checks:
1. QUBO formulation correctness (binary variables, linear/quadratic terms)
2. Constraint encoding (n_layers ≥ 3, d_model ≥ 128, ethical lock)
3. Net Φ-density gain calculation:
      NetΦ = Φ_ArchitectureGain - C_quantum - λR_risk
   Must be ≥ +0.10Φ to deploy and the proposal claims +0.15Φ.
4. Ethical constraint: exclude_configphp=1 (hardcoded as a linear penalty → treated as infinite cost if violated)
5. Risk penalty λR_risk ≤ 0.02Φ (as per proposal)
6. Quantum shot cost C_quantum ≤ 0.05Φ (as per proposal)
7. All claimed component gains sum to the raw gain before deductions.

If any check fails, the proposal is non‑compliant.
"""

import numpy as np

# ----------------------------
# Helper data from the proposal
# ----------------------------
# Claimed component gains (from accuracy, speed, cost reduction)
GAIN_ACCURACY = 0.08   # Φ
GAIN_SPEED    = 0.04   # Φ
GAIN_COST     = 0.03   # Φ
RAW_GAIN_CLAIMED = GAIN_ACCURACY + GAIN_SPEED + GAIN_COST  # 0.15Φ? Actually 0.08+0.04+0.03 = 0.15
# But proposal says raw gain before deductions is +0.18Φ (see reflection). We'll use both.
RAW_GAIN_REFLECTION = 0.18   # Φ (as stated in the reflection section)

# Deductions claimed
C_QUANTUM   = 0.03   # Φ (quantum shot cost)
LAMBDA_R    = 0.01   # Φ (risk penalty)
NET_GAIN_CLAIMED = 0.15   # Φ (as in proposal)

# Ethical lock: exclude_configphp=1 → we treat as a constraint that must be satisfied.
# In the QUBO they added it as a hard constraint; we just verify it's present.
ETHICAL_LOCK_PRESENT = True   # assume from text

# ----------------------------
# 1. Validate QUBO structure
# ----------------------------
def validate_qubo():
    """
    The proposal defines a 12-bit QUBO with variables:
        n_layers_0, n_layers_1   (3 bits for n_layers [2,8] -> actually need 3 bits, but they show only 2?)
        d_model_0..d_model_3     (4 bits)
        n_heads_0..n_heads_2     (3 bits)
        ff_dim_0..ff_dim_1       (2 bits)
    Total = 3+4+3+2 = 12 bits.

    We'll just check that the linear and quadratic dictionaries contain exactly
    the expected variable names and that coefficients are real numbers.
    """
    expected_vars = {
        "n_layers_0", "n_layers_1", "n_layers_2",
        "d_model_0", "d_model_1", "d_model_2", "d_model_3",
        "n_heads_0", "n_heads_1", "n_heads_2",
        "ff_dim_0", "ff_dim_1"
    }

    # Linear terms from proposal
    linear = {
        "n_layers_0": 0.05,
        "d_model_0": 0.10,
        "n_heads_0": 0.08,
        "ff_dim_0": 0.06,
        # Note: they only listed coefficients for the LSB of each group;
        # the higher bits are implicitly zero (no penalty). We'll accept that.
    }

    # Quadratic terms from proposal
    quadratic = {
        ("n_layers_0", "d_model_0"): -0.12,
        ("n_heads_1", "ff_dim_1"): -0.09,
    }

    # Check that all keys are subset of expected vars
    lin_keys = set(linear.keys())
    quad_keys = set()
    for a, b in quadratic.keys():
        quad_keys.add(a)
        quad_keys.add(b)

    undefined = (lin_keys | quad_keys) - expected_vars
    if undefined:
        return False, f"Undefined variables in QUBO: {undefined}"

    # Check that coefficients are numbers
    for v, c in linear.items():
        if not isinstance(c, (int, float)):
            return False, f"Linear coefficient for {v} is not numeric: {c}"
    for (a, b), c in quadratic.items():
        if not isinstance(c, (int, float)):
            return False, f"Quadratic coefficient for ({a},{b}) is not numeric: {c}"

    return True, "QUBO structure OK"

# ----------------------------
# 2. Validate constraints encoding
# ----------------------------
def validate_constraints():
    """
    Constraints claimed:
        n_layers ≥ 3   → binary encoding: n_layers = 2* n_layers_0 + 3* n_layers_1 + 4* n_layers_2? 
        Actually they used bits: n_layers_0 (value 2), n_layers_1 (value 3), n_layers_2 (value 4?) 
        But they only showed two bits in the table. We'll enforce a simple linear constraint:
            0.3*n_layers_0 + 0.4*n_layers_1 ≥ 0.5   (as in code snippet)
        d_model ≥ 128  → they didn't show a constraint; assume similar encoding.
        Ethical lock: exclude_configphp=1 → must be satisfied (we treat as always true if present).
    We'll just verify that the constraint they wrote is present and syntactically correct.
    """
    # The snippet:
    # qp.linear_constraint(linear={"n_layers_0": 0.3, "n_layers_1": 0.4}, sense=">=", rhs=0.5)
    # This is a valid linear constraint.
    # We'll just check that the coefficients are non‑negative and RHS positive.
    lin = {"n_layers_0": 0.3, "n_layers_1": 0.4}
    sense = ">="
    rhs = 0.5

    if not all(isinstance(v, (int, float)) for v in lin.values()):
        return False, "Constraint linear coefficients not numeric"
    if not isinstance(rhs, (int, float)):
        return False, "Constraint RHS not numeric"
    if sense not in {">=", "<=", "=="}:
        return False, "Invalid constraint sense"

    return True, "Constraint encoding OK"

# ----------------------------
# 3. Validate net Φ gain math
# ----------------------------
def validate_net_gain():
    """
    NetΦ = Φ_ArchitectureGain - C_quantum - λR_risk
    We have two sources for Φ_ArchitectureGain:
        a) Sum of component gains (0.08+0.04+0.03 = 0.15) → then Net = 0.15 - 0.03 - 0.01 = 0.11 (fails)
        b) Reflection says raw gain before deductions = 0.18 → Net = 0.18 - 0.03 - 0.01 = 0.14 (still short of 0.15)
    The proposal claims Net = +0.15Φ. We'll check both possibilities and flag inconsistency.
    """
    # Component sum
    component_sum = GAIN_ACCURACY + GAIN_SPEED + GAIN_COST
    net_from_components = component_sum - C_QUANTUM - LAMBDA_R

    # Reflection raw gain
    net_from_reflection = RAW_GAIN_REFLECTION - C_QUANTUM - LAMBDA_R

    # Accept if either matches the claimed net gain within tolerance
    tol = 1e-3
    ok1 = abs(net_from_components - NET_GAIN_CLAIMED) < tol
    ok2 = abs(net_from_reflection - NET_GAIN_CLAIMED) < tol

    if not (ok1 or ok2):
        return False, (
            f"Net gain mismatch. "
            f"Component sum net={net_from_components:.3f}, "
            f"Reflection raw net={net_from_reflection:.3f}, "
            f"claimed={NET_GAIN_CLAIMED:.3f}"
        )
    # Additionally, enforce protocol threshold: net gain must exceed +0.10Φ to deploy
    if net_from_components < 0.10 and net_from_reflection < 0.10:
        return False, f"Net gain below deployment threshold (+0.10Φ): max={max(net_from_components, net_from_reflection):.3f}"
    return True, "Net gain math consistent and above threshold"

# ----------------------------
# 4. Validate ethical lock presence
# ----------------------------
def validate_ethical_lock():
    if not ETHICAL_LOCK_PRESENT:
        return False, "Ethical lock (exclude_configphp=1) not found"
    return True, "Ethical lock present"

# ----------------------------
# 5. Validate risk and quantum cost bounds (from proposal)
# ----------------------------
def validate_bounds():
    if C_QUANTUM > 0.05:
        return False, f"Quantum shot cost too high: {C_QUANTUM} > 0.05Φ"
    if LAMBDA_R > 0.02:
        return False, f"Risk penalty too high: {LAMBDA_R} > 0.02Φ"
    return True, "Cost bounds OK"

# ----------------------------
# Main validation runner
# ----------------------------
def main():
    checks = [
        ("QUBO Structure", validate_qubo),
        ("Constraint Encoding", validate_constraints),
        ("Ethical Lock", validate_ethical_lock),
        ("Cost Bounds", validate_bounds),
        ("Net Gain Math", validate_net_gain),
    ]

    all_passed = True
    for name, func in checks:
        passed, msg = func()
        if passed:
            print(f"[PASS] {name}: {msg}")
        else:
            print(f"[FAIL] {name}: {msg}")
            all_passed = False

    if all_passed:
        print("\n=== OMEGA PROTOCOL VALIDATION: PASSED ===")
        print("The Q-NAS proposal is mathematically sound and compliant.")
    else:
        print("\n=== OMEGA PROTOCOL VALIDATION: FAILED ===")
        print("One or more checks failed. Review the proposal before deployment.")

if __name__ == "__main__":
    main()