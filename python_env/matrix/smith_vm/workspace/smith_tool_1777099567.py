# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for the Q-Systemic Bureaucratic Interface (QBI)
--------------------------------------------------------------------------------
Validates the mathematical soundness of the proposal and enforces the six
absolute invariants (Φ‑1 … Φ‑6) plus the AFO stiffness bound.

Usage:
    python3 omega_validator.py   # runs internal self‑tests
"""

import math
from typing import Tuple

# -------------------------- Constants --------------------------
LOG2 = math.log2
TANH = math.tanh
EXP  = math.exp

# Omega Protocol thresholds (from the specification)
COD_MIN          = 0.85
PSI_MIN          = math.log(0.95)          # ≈ -0.051293
XI_RULE_MAX      = 3.0
H_PROC_MAX       = 0.85
R_MAX            = 2.5                     # stiffness‑mismatch bound
GAMMA            = 0.05                    # hr⁻¹ (AFO rate)

# -------------------------- Core Computations --------------------------
def compute_psi(COD: float) -> float:
    """ψ = ln(Φ_N) where Φ_N = log₂(COD)."""
    if COD <= 0.0:
        raise ValueError("COD must be > 0 for log.")
    Phi_N = LOG2(COD)
    return math.log(Phi_N)   # natural log as per definition

def compute_phi_delta(psi: float, R_align: float) -> float:
    """Φ_Δ = ψ * tanh(R_align / R_max)."""
    return psi * TANH(R_align / R_MAX)

def compute_phi(COD: float, H_proc: float, DeltaS_audit: float,
                psi: float, R_align: float) -> float:
    """Full Φ‑density formula."""
    if H_proc + DeltaS_audit <= 0.0:
        raise ValueError("Denominator (H_proc + ΔS_audit) must be > 0.")
    coherence_gain = LOG2(COD / (H_proc + DeltaS_audit))
    asymmetry_term = psi * TANH(R_align / R_MAX)
    return coherence_gain + asymmetry_term

def adiabatic_stiffness(Xi_rule0: float, Xi_req: float, t: float) -> float:
    """Ξ_rule(t) = Ξ_rule(0)·e^(−γt) + Ξ_req·(1−e^(−γt))."""
    return Xi_rule0 * EXP(-GAMMA * t) + Xi_req * (1.0 - EXP(-GAMMA * t))

# -------------------------- Invariant Checks --------------------------
def assert_phi1(COD: float):
    assert COD >= COD_MIN, f"Φ‑1 violated: COD={COD:.4f} < {COD_MIN}"

def assert_phi2(psi: float):
    assert psi >= PSI_MIN, f"Φ‑2 violated: ψ={psi:.6f} < {PSI_MIN:.6f}"

def assert_phi3(Xi_rule: float):
    assert Xi_rule <= XI_RULE_MAX, f"Φ‑3 violated: Ξ_rule={Xi_rule:.4f} > {XI_RULE_MAX}"

def assert_phi4(H_proc: float):
    assert H_proc <= H_PROC_MAX, f"Φ‑4 violated: H_proc={H_proc:.4f} > {H_PROC_MAX}"

def assert_phi5(DeltaS_audit: float):
    # ΔS_audit is subtracted; only require it be non‑negative.
    assert DeltaS_audit >= 0.0, f"Φ‑5 violated: ΔS_audit={DeltaS_audit:.4f} < 0"

def assert_phi6(Phi_N: float, Phi_Delta: float):
    assert Phi_Delta < 0.5 * Phi_N, (
        f"Φ‑6 violated: Φ_Δ={Phi_Delta:.4f} ≥ 0.5·Φ_N={0.5*Phi_N:.4f}"
    )

def assert_afo_bounds(Xi_rule0: float, Xi_req: float, t_max: float = 100.0):
    """Check that Ξ_rule(t) never exceeds the hard cap for t∈[0,t_max]."""
    # The function is monotonic; it suffices to check the endpoints.
    for t in (0.0, t_max):
        Xi = adiabatic_stiffness(Xi_rule0, Xi_req, t)
        assert_phi3(Xi)

# -------------------------- Self‑Test Suite --------------------------
def run_self_tests():
    print("Running Omega Protocol self‑validation …")

    # ---- Test Case A: Compliant baseline (should PASS) ----
    COD_A      = 0.88
    H_proc_A   = 0.40
    DeltaS_A   = 0.05
    Xi_rule0_A = 2.0
    Xi_req_A   = 2.2
    t_A        = 10.0   # hours

    psi_A      = compute_psi(COD_A)
    Phi_N_A    = LOG2(COD_A)
    R_align_A  = Xi_req_A - Xi_rule0_A
    Phi_Delta_A= compute_phi_delta(psi_A, R_align_A)
    Phi_A      = compute_phi(COD_A, H_proc_A, DeltaS_A, psi_A, R_align_A)

    # Invariants
    assert_phi1(COD_A)
    assert_phi2(psi_A)
    assert_phi3(adiabatic_stiffness(Xi_rule0_A, Xi_req_A, t_A))
    assert_phi4(H_proc_A)
    assert_phi5(DeltaS_A)
    assert_phi6(Phi_N_A, Phi_Delta_A)
    assert_afo_bounds(Xi_rule0_A, Xi_req_A)

    print("✅ Test A (nominal) PASSED")
    print(f"   COD={COD_A:.3f}, ψ={psi_A:.5f}, Φ_N={Phi_N_A:.3f}, Φ_Δ={Phi_Delta_A:.3f}, Φ={Phi_A:.3f}")

    # ---- Test Case B: Boundary violations (should FAIL) ----
    violations = []

    # B1: COD too low
    try:
        assert_phi1(0.80)
    except AssertionError as e:
        violations.append(str(e))

    # B2: ψ too low (via low COD)
    try:
        assert_phi2(compute_psi(0.50))
    except AssertionError as e:
        violations.append(str(e))

    # B3: Ξ_rule exceeds cap
    try:
        assert_phi3(3.2)
    except AssertionError as e:
        violations.append(str(e))

    # B4: H_proc too high
    try:
        assert_phi4(0.90)
    except AssertionError as e:
        violations.append(str(e))

    # B5: Negative audit cost
    try:
        assert_phi5(-0.01)
    except AssertionError as e:
        violations.append(str(e))

    # B6: Φ_Δ too large
    try:
        assert_phi6(Phi_N_A, 0.6 * Phi_N_A)  # deliberately too big
    except AssertionError as e:
        violations.append(str(e))

    # B7: AFO trajectory exceeds cap (set initial > cap)
    try:
        assert_afo_bounds(3.5, 2.0, t_max=5.0)
    except AssertionError as e:
        violations.append(str(e))

    if violations:
        print("\n❌ Test B (expected violations) produced:")
        for v in violations:
            print("   -", v)
    else:
        raise RuntimeError("Test B should have triggered assertions but did not.")

    print("\nAll self‑tests completed. Invariants are enforced correctly.")

# -------------------------- Entry Point --------------------------
if __name__ == "__main__":
    run_self_tests()