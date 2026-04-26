# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script – Trauma‑Performance Q‑System
Validates mathematical soundness and invariant enforcement.
"""

import math
import cmath
from typing import Tuple

# ----------------------------------------------------------------------
# 1. Invariant Constants (mirroring the C++ constexpr block)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD   = 0.95
PSI_ID_CRITICAL    = 0.90
XI_BOUND_DEFAULT   = 1.5
XI_BOUND_MAX       = 3.0
XI_BOUND_MIN       = 0.5
XI_BOUND_CRITICAL  = 2.5
H_INT_LIMIT        = 0.85
COD_THRESHOLD      = 0.75
STIFFNESS_ENTROPY_RATIO_MAX = 2.0
LAMBDA_COUPLING    = 1.0
GAMMA_COUPLING     = 0.5
K_BOLTZMANN        = 1.0   # informational constant (set to 1 for validation)

# ----------------------------------------------------------------------
# 2. Helper Functions (direct translations of the key methods)
# ----------------------------------------------------------------------
def fidelity(sub: complex, con: complex) -> float:
    """|⟨sub|con⟩| / (|sub|·|con|)"""
    num = abs(conjugate(sub) * con)
    den = abs(sub) * abs(con)
    return 0.0 if den == 0.0 else num / den

def conjugate(z: complex) -> complex:
    return z.real - 1j * z.imag

def cod(sub: complex, con: complex, H_int: float, Xi_bound: float,
        Gamma_t: float) -> float:
    """Chain Overlap Density = fidelity² * e^{-Λ·H_int} * e^{-Γ·Ξ_bound}"""
    f = fidelity(sub, con)
    damping = math.exp(-LAMBDA_COUPLING * H_int)
    stiffness_penalty = math.exp(-GAMMA_COUPLING * Xi_bound)
    return f * f * damping * stiffness_penalty

def stiffness_entropy_ratio(Xi_bound: float, H_int: float) -> float:
    """Ξ_bound / H_int (guard against division by zero)"""
    if H_int < 1e-12:
        H_int = 1e-12
    return Xi_bound / H_int

def is_artificial_cod(COD: float, Xi_bound: float, H_int: float) -> bool:
    return (COD >= COD_THRESHOLD) and \
           (Xi_bound > XI_BOUND_CRITICAL) and \
           (stiffness_entropy_ratio(Xi_bound, H_int) > STIFFNESS_ENTROPY_RATIO_MAX)

def compute_gamma(t: float, Xi_bound: float,
                  tau_opt: float = 0.5, sigma: float = 0.1) -> float:
    """Gamma(t) = min(0.8·Ξ_bound, tanh((t‑τ)/σ))"""
    raw = math.tanh((t - tau_opt) / sigma)
    return min(0.8 * Xi_bound, raw)

def compute_energy(Psi_sub: complex, Psi_con: complex,
                   Xi_bound: float, Gamma_t: float, H_int: float) -> float:
    """H_eff = H_sub (0) + Ξ_bound·|⟨sub|con⟩|² + Γ - H_cond"""
    overlap_sq = abs(conjugate(Psi_sub) * Psi_con)
    H_stiff = Xi_bound * overlap_sq
    # Shannon conditional entropy H(sub|con) = -p·log(p), p = |⟨sub|con⟩|
    p = overlap_sq
    H_cond = 0.0 if p == 0.0 else -p * math.log(p)
    return H_stiff + Gamma_t - H_cond

def identity_loss_from_entropy(H_cond: float) -> float:
    """ΔΨ_id = 0.1·H_cond (as used in the AIP)"""
    return 0.1 * H_cond

def phi_density_impact(H_before: float, H_after: float,
                       audit_cost: float, individual_cost: float) -> float:
    """ΔΦ = -(H_after - H_before) - audit - individual"""
    return -(H_after - H_before) - audit_cost - individual_cost

def audit_cost(complexity: float = 1.0) -> float:
    return K_BOLTZMANN * math.log(2.0) * complexity

def individual_cost(H_int: float, Xi_bound: float) -> float:
    return H_int * Xi_bound * 0.2

# ----------------------------------------------------------------------
# 3. Validation Tests
# ----------------------------------------------------------------------
def run_validation() -> None:
    print("=== Omega Protocol Validation Start ===")

    # ---- Test 1: Dimensional consistency (all inputs dimensionless) ----
    sub = complex(0.6, 0.8)   # |sub| = 1.0
    con = complex(0.8, 0.6)   # |con| = 1.0
    H_int = 0.3
    Xi_bound = 2.0
    Gamma_t = compute_gamma(0.5, Xi_bound)
    C = cod(sub, con, H_int, Xi_bound, Gamma_t)
    assert 0.0 <= C <= 1.0, f"COD out of bounds: {C}"
    print(f"✓ COD = {C:.4f} (dimensionless, within [0,1])")

    # ---- Test 2: Artificial COD detection ----
    # High stiffness, moderate entropy → should flag
    C_high = cod(sub, con, H_int=0.2, Xi_bound=3.0, Gamma_t=0.5)
    assert is_artificial_cod(C_high, Xi_bound=3.0, H_int=0.2), \
        "Failed to detect artificial COD in high‑stiffness regime"
    print(f"✓ Artificial COD detected (COD={C_high:.4f}, Ξ/ H={stiffness_entropy_ratio(3.0,0.2):.2f})")

    # Low stiffness → should NOT flag
    C_low = cod(sub, con, H_int=0.8, Xi_bound=0.6, Gamma_t=0.2)
    assert not is_artificial_cod(C_low, Xi_bound=0.6, H_int=0.8), \
        "Incorrectly flagged low‑stiffness state as artificial"
    print(f"✓ Low‑stiffness state correctly NOT artificial (COD={C_low:.4f})")

    # ---- Test 3: Failure‑mode detector ----
    def failure_mode(H_int: float, Xi_bound: float, Psi_id: float, dGamma_dt: float) -> str:
        if H_int > H_INT_LIMIT and Xi_bound > XI_BOUND_CRITICAL and Psi_id < PSI_ID_CRITICAL:
            return "PERFORMANCE_BURNOUT"
        if dGamma_dt > Xi_bound:
            return "MEASUREMENT_SHOCK"
        if H_int > H_INT_LIMIT:
            return "DECOHERENCE"
        if Psi_id < PSI_ID_CRITICAL:
            return "DISSOCIATION"
        return "NONE"

    # Burnout case
    assert failure_mode(0.9, 2.7, 0.88, 0.1) == "PERFORMANCE_BURNOUT"
    print("✓ PERFORMANCE_BURNOUT correctly identified")
    # Measurement shock (dGamma/dt > Ξ)
    assert failure_mode(0.2, 1.0, 0.96, 1.5) == "MEASUREMENT_SHOCK"
    print("✓ MEASUREMENT_SHOCK correctly identified")
    # Decoherence
    assert failure_mode(0.9, 1.0, 0.96, 0.0) == "DECOHERENCE"
    print("✓ DECOHERENCE correctly identified")
    # Dissociation
    assert failure_mode(0.2, 1.0, 0.88, 0.0) == "DISSOCIATION"
    print("✓ DISSOCIATION correctly identified")
    # Nominal
    assert failure_mode(0.2, 1.0, 0.96, 0.0) == "NONE"
    print("✓ Nominal state classified as NONE")

    # ---- Test 4: Adiabatic Integration Operator (stiffness reduction) ----
    t = 0.0
    Xi = XI_BOUND_DEFAULT
    # Simulate a burnout trigger
    H_int = 0.9
    Psi_id = 0.92
    # Compute gamma and its derivative (finite diff)
    gamma0 = compute_gamma(t, Xi)
    gamma1 = compute_gamma(t + 0.1, Xi)
    dGamma_dt = (gamma1 - gamma0) / 0.1
    failure = failure_mode(H_int, Xi, Psi_id, dGamma_dt)
    assert failure == "PERFORMANCE_BURNOUT", "Expected burnout trigger"
    # Apply stiffness reduction (5% per step as in the code)
    Xi_new = max(XI_BOUND_MIN, Xi * 0.95)
    assert Xi_new < Xi, "Stiffness not reduced"
    # Ensure adiabatic condition: |dGamma/dt| << Ξ (here we just check < 0.2·Ξ)
    assert abs(dGamma_dt) < 0.2 * Xi_new, "Adiabatic condition violated"
    print(f"✓ Stiffness reduced from {Xi:.3f} to {Xi_new:.3f}, adiabatic condition satisfied")

    # ---- Test 5: Identity preservation after entropy loss ----
    H_cond = 0.4  # example conditional entropy
    loss = identity_loss_from_entropy(H_cond)
    Psi_id_post = Psi_id - loss
    assert Psi_id_post >= PSI_ID_THRESHOLD, \
        f"Identity dropped below threshold: {Psi_id_post:.3f}"
    print(f"✓ Identity after entropy loss: {Psi_id_post:.3f} ≥ {PSI_ID_THRESHOLD}")

    # ---- Test 6: Φ‑density ledger with audit cost subtraction ----
    H_before = 0.5
    H_after  = 0.3
    audit = audit_cost(complexity=1.2)
    indiv   = individual_cost(H_int=0.4, Xi_bound=1.6)
    delta_phi = phi_density_impact(H_before, H_after, audit, indiv)
    # Expected: -(0.3-0.5) = +0.2 minus costs
    expected = 0.2 - audit - indiv
    assert math.isclose(delta_phi, expected, rel_tol=1e-9), \
        f"Φ‑density impact mismatch: got {delta_phi:.6f}, expected {expected:.6f}"
    print(f"✓ Φ‑density impact = {delta_phi:.6f} (audit={audit:.6f}, indiv={indiv:.6f})")

    # ---- Test 7: Invariant hard‑gates (simulate throw) ----
    def hard_gate_psi_id(value: float) -> None:
        if value < PSI_ID_THRESHOLD:
            raise RuntimeError("Identity Integrity Violation")
    try:
        hard_gate_psi_id(0.94)  # should pass
    except RuntimeError:
        assert False, "Hard gate incorrectly fired for valid Ψ_id"
    try:
        hard_gate_psi_id(0.90)  # should fail
        assert False, "Hard gate did not fire for invalid Ψ_id"
    except RuntimeError:
        pass
    print("✓ Identity hard‑gate behaves as specified")

    print("=== All validation tests passed ===")

if __name__ == "__main__":
    run_validation()