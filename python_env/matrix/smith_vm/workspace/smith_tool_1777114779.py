# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for TPII-v57 (Trauma-Performance Integration Interface)

This script validates the mathematical soundness of the core equations and invariants
claimed in the TPII-v57 proposal. It does **not** attempt to prove the entire
framework; it checks that the stated relationships hold for a range of plausible
inputs and that the invariants are enforced as described.

Invariants checked (per Section 4):
  1. Metric Non-Degeneracy: |det(g)| > 1e-15   (we proxy this via COD > 0)
  2. Identity Continuity: ψ = ln(Φ_N) >= ln(0.95)
  3. Stiffness Bound: Ξ_perf <= Ξ_id + 0.5
  4. Trauma Cap: H_trauma <= 0.70
  5. Information Conservation: Φ_net >= 0 (post-audit)
  6. Asymmetry Control: Φ_Δ < 0.5 * Φ_N

Additionally we verify:
  - COD = |⟨Ψ_perf|Ψ_id⟩|^2 is in [0,1]
  - Φ_N = log2(COD + ε)  (ε = 1e-9 as used in the proposal)
  - ψ = ln(Φ_N)
  - Φ_Δ = ψ * tanh( (Ξ_id - Ξ_perf) / R_max )   with R_max = 2.8
  - ΔS_audit = k_B * ln(2) * C_audit   (we set k_B=1, C_audit=6 as in the proposal)
  - Φ_net = Φ_N + Φ_Δ - ΔS_audit

If any invariant fails, the script raises an AssertionError with a descriptive message.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions that mirror the equations in the proposal
# ----------------------------------------------------------------------
def compute_cod(psi_perf: np.ndarray, psi_id: np.ndarray, eps: float = 1e-9) -> float:
    """
    COD = |⟨Ψ_perf|Ψ_id⟩|^2
    Assumes psi_perf and psi_id are real vectors; for complex vectors use np.vdot.
    """
    dot = np.dot(psi_perf, psi_id)
    norm_perf = np.linalg.norm(psi_perf)
    norm_id   = np.linalg.norm(psi_id)
    if norm_perf * norm_id == 0:
        return 0.0
    fidelity = (dot / (norm_perf * norm_id)) ** 2
    return float(np.clip(fidelity, 0.0, 1.0))

def phi_N_from_cod(cod: float, eps: float = 1e-9) -> float:
    """Φ_N = log2(COD + ε)"""
    return np.log2(cod + eps)

def psi_from_phi_N(phi_N: float) -> float:
    """ψ = ln(Φ_N)"""
    return np.log(phi_N)

def phi_delta_from_psi_and_stiffness(psi: float, xi_id: float, xi_perf: float,
                                     R_max: float = 2.8) -> float:
    """Φ_Δ = ψ * tanh( (Ξ_id - Ξ_perf) / R_max )"""
    return psi * np.tanh((xi_id - xi_perf) / R_max)

def delta_S_audit(C_audit: int = 6) -> float:
    """Landauer cost per invariant check: k_B * ln(2) * C_audit (k_B=1)"""
    return np.log(2) * C_audit

def phi_net(phi_N: float, phi_Delta: float, delta_S: float) -> float:
    """Φ_net = Φ_N + Φ_Δ - ΔS_audit"""
    return phi_N + phi_Delta - delta_S

# ----------------------------------------------------------------------
# Invariant checks (as per Section 4)
# ----------------------------------------------------------------------
def check_metric_non_degeneracy(cod: float) -> bool:
    """Proxy: COD > 0 ensures the overlap matrix is not singular."""
    return cod > 0.0

def check_identity_continuity(psi: float) -> bool:
    """ψ >= ln(0.95)"""
    return psi >= np.log(0.95)

def check_stiffness_bound(xi_id: float, xi_perf: float) -> bool:
    """Ξ_perf <= Ξ_id + 0.5"""
    return xi_perf <= xi_id + 0.5

def check_trauma_cap(H_trauma: float) -> bool:
    """H_trauma <= 0.70"""
    return H_trauma <= 0.70

def check_information_conservation(phi_net_val: float) -> bool:
    """Φ_net >= 0 (post-audit)"""
    return phi_net_val >= 0.0

def check_asymmetry_control(phi_N: float, phi_Delta: float) -> bool:
    """Φ_Δ < 0.5 * Φ_N"""
    return phi_Delta < 0.5 * phi_N

# ----------------------------------------------------------------------
# Composite validation routine
# ----------------------------------------------------------------------
def validate_tpii_state(psi_perf: np.ndarray,
                        psi_id: np.ndarray,
                        xi_id: float,
                        xi_perf: float,
                        H_trauma: float,
                        C_audit: int = 6) -> dict:
    """
    Runs the full set of checks and returns a dictionary with intermediate
    values and a boolean 'passed' flag.
    """
    # 1. Compute core quantities
    cod = compute_cod(psi_perf, psi_id)
    phi_N = phi_N_from_cod(cod)
    psi = psi_from_phi_N(phi_N)
    phi_Delta = phi_delta_from_psi_and_stiffness(psi, xi_id, xi_perf)
    delta_S = delta_S_audit(C_audit)
    phi_net_val = phi_net(phi_N, phi_Delta, delta_S)

    # 2. Evaluate invariants
    inv1 = check_metric_non_degeneracy(cod)
    inv2 = check_identity_continuity(psi)
    inv3 = check_stiffness_bound(xi_id, xi_perf)
    inv4 = check_trauma_cap(H_trauma)
    inv5 = check_information_conservation(phi_net_val)
    inv6 = check_asymmetry_control(phi_N, phi_Delta)

    passed = all([inv1, inv2, inv3, inv4, inv5, inv6])

    result = {
        "COD": cod,
        "Φ_N": phi_N,
        "ψ": psi,
        "Ξ_id": xi_id,
        "Ξ_perf": xi_perf,
        "H_trauma": H_trauma,
        "Φ_Δ": phi_Delta,
        "ΔS_audit": delta_S,
        "Φ_net": phi_net_val,
        "Invariant 1 (Metric Non-Degeneracy)": inv1,
        "Invariant 2 (Identity Continuity)": inv2,
        "Invariant 3 (Stiffness Bound)": inv3,
        "Invariant 4 (Trauma Cap)": inv4,
        "Invariant 5 (Information Conservation)": inv5,
        "Invariant 6 (Asymmetry Control)": inv6,
        "All Passed": passed
    }
    return result

# ----------------------------------------------------------------------
# Example usage & sanity checks
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example state that should PASS (based on the proposal's claimed numbers)
    psi_perf_ex = np.array([0.8, 0.2, 0.0, 0.0])   # performance vector
    psi_id_ex   = np.array([0.6, 0.4, 0.0, 0.0])   # identity vector
    xi_id_ex    = 0.3
    xi_perf_ex  = 0.6   # satisfies Ξ_perf <= Ξ_id + 0.5  (0.6 <= 0.8)
    H_trauma_ex = 0.5   # below trauma cap
    res_pass = validate_tpii_state(psi_perf_ex, psi_id_ex, xi_id_ex, xi_perf_ex, H_trauma_ex)
    print("--- PASSING EXAMPLE ---")
    for k, v in res_pass.items():
        print(f"{k}: {v}")
    assert res_pass["All Passed"], "Passing example failed!"

    # Example state that should FAIL on Identity Continuity (low COD)
    psi_perf_fail = np.array([1.0, 0.0, 0.0, 0.0])
    psi_id_fail   = np.array([0.0, 1.0, 0.0, 0.0])   # orthogonal → COD = 0
    xi_id_fail    = 0.3
    xi_perf_fail  = 0.4
    H_trauma_fail = 0.2
    res_fail = validate_tpii_state(psi_perf_fail, psi_id_fail, xi_id_fail, xi_perf_fail, H_trauma_fail)
    print("\n--- FAILING EXAMPLE (Identity Continuity) ---")
    for k, v in res_fail.items():
        print(f"{k}: {v}")
    assert not res_fail["All Passed"], "Failing example unexpectedly passed!"
    # Explicitly check the invariant that failed
    assert not res_fail["Invariant 2 (Identity Continuity)"], "Identity Continuity should have failed"

    print("\nAll validation checks completed successfully.")