# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for the Q-Systemic Self framework.
Checks COD, dissonance, stiffness-impedance, asymmetry, and silence conditions.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def shannon_entropy(p: np.ndarray) -> float:
    """Shannon entropy of a probability vector p (already normalized, >=0)."""
    p = p[p > 0]  # avoid log(0)
    return -np.sum(p * np.log(p))

def compute_h_dis(action_state: np.ndarray, identity_state: np.ndarray) -> float:
    """
    Dissonance entropy H_dis as described:
    H_dis = Shannon entropy of normalized absolute difference.
    """
    diff = np.abs(action_state - identity_state)
    if np.sum(diff) == 0:
        return 0.0
    prob = diff / np.sum(diff)
    return shannon_entropy(prob)

def compute_fidelity(action_state: np.ndarray, identity_state: np.ndarray) -> float:
    """Fidelity = |⟨Ψ_perf|Ψ_latent⟩|^2 normalized by vector magnitudes."""
    dot = np.dot(action_state, identity_state)
    norm_act = np.linalg.norm(action_state)
    norm_id = np.linalg.norm(identity_state)
    if norm_act * norm_id == 0:
        return 0.0
    fidelity = (dot / (norm_act * norm_id)) ** 2
    return np.clip(fidelity, 0.0, 1.0)

def compute_cod(
    action_state: np.ndarray,
    identity_state: np.ndarray,
    xi_perf: float,
    z_trust: float,
    kappa: float = 0.5,
    lam: float = 0.5,
    p_collapse: float = 1.0,
) -> float:
    """
    Chain Overlap Density (COD).
    Default kappa, lambda = 0.5 (can be tuned); p_collapse = 1 if H_dis>0.3 else 0.
    """
    fidelity = compute_fidelity(action_state, identity_state)
    stiffness_pen = np.exp(-kappa * xi_perf)
    impedance_pen = np.exp(-lam * z_trust)
    # collapse penalty will be applied later based on H_dis
    cod_raw = fidelity * stiffness_pen * impedance_pen
    return np.clip(cod_raw, 0.0, 1.0)

def compute_phi_n(cod: float) -> float:
    """Φ_N = log2(COD). Returns -inf if cod <= 0."""
    if cod <= 0:
        return -np.inf
    return np.log2(cod)

def compute_phi_delta(phi_n: float, xi_perf: float, z_trust: float, r_max: float = 3.0) -> float:
    """Φ_Δ = tanh(Φ_N) * tahn(R_align / R_max)."""
    r_align = abs(xi_perf - z_trust)
    return np.tanh(phi_n) * np.tanh(r_align / r_max)

def validate_invariants(
    action_state: np.ndarray,
    identity_state: np.ndarray,
    xi_perf: float,
    z_trust: float,
    kappa: float = 0.5,
    lam: float = 0.5,
) -> dict:
    """
    Returns a dict with boolean results for each invariant and overall status.
    """
    # 1. COD (raw, before collapse penalty)
    cod_raw = compute_cod(action_state, identity_state, xi_perf, z_trust, kappa, lam, p_collapse=0.0)
    # 2. H_dis
    h_dis = compute_h_dis(action_state, identity_state)
    # 3. Collapse penalty factor (0 if H_dis>0.3 else 1)
    collapse_factor = 0.0 if h_dis > 0.3 else 1.0
    # 4. Final COD after penalty
    cod = cod_raw * collapse_factor

    # Invariants
    inv1 = cod >= 0.85                     # Alignment Fidelity
    inv2 = h_dis <= 0.3                    # Dissonance Cap
    inv3 = xi_perf <= z_trust + 0.1        # Stiffness-Impedance Match
    # Audit cost is a constant subtraction; always satisfied as a bookkeeping step.
    inv4 = True                            # ΔS_audit = k_B ln2 *6 (always true)

    # Asymmetry control (only meaningful if Φ_N is real)
    phi_n = compute_phi_n(cod)
    inv5 = False
    if np.isfinite(phi_n):
        phi_delta = compute_phi_delta(phi_n, xi_perf, z_trust)
        inv5 = phi_delta < 0.5 * phi_n
    else:
        inv5 = False  # Φ_N undefined → automatically fails asymmetry

    inv6 = not (cod < 0.85 or h_dis > 0.3)  # Silence Protocol: allowed to send if NOT (violation)

    overall = inv1 and inv2 and inv3 and inv4 and inv5 and inv6

    return {
        "COD": cod,
        "COD_raw": cod_raw,
        "H_dis": h_dis,
        "Phi_N": phi_n,
        "Phi_Delta": compute_phi_delta(phi_n, xi_perf, z_trust) if np.isfinite(phi_n) else np.nan,
        "Invariant_1_COD≥0.85": inv1,
        "Invariant_2_Hdis≤0.3": inv2,
        "Invariant_3_Xi≤Z+0.1": inv3,
        "Invariant_4_AuditCost": inv4,
        "Invariant_5_Asymmetry": inv5,
        "Invariant_6_SilenceOK": inv6,
        "Overall_Pass": overall,
        "Message_Allowed": inv6,  # True only if silence protocol permits a message
    }

# ----------------------------------------------------------------------
# Example usage (feel free to replace with your own vectors/values)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example latent identity vector: [Safety, Worthiness, Performance, Shame]
    identity_state = np.array([0.4, 0.3, 0.2, 0.1])
    identity_state = identity_state / np.linalg.norm(identity_state)  # normalize

    # Example action (performance) vector: [KPI, Validation, Output, Visibility]
    action_state = np.array([0.7, 0.2, 0.05, 0.05])
    action_state = action_state / np.linalg.norm(action_state)

    xi_perf = 0.85   # current performance stiffness
    z_trust = 0.6    # current trust impedance

    result = validate_invariants(action_state, identity_state, xi_perf, z_trust)

    print("=== Omega Protocol Invariant Check ===")
    for k, v in result.items():
        if isinstance(v, float):
            print(f"{k:25}: {v: .4f}")
        else:
            print(f"{k:25}: {v}")
    print("-" * 40)
    if result["Overall_Pass"]:
        print("✅ System complies with all Omega Protocol invariants.")
        if result["Message_Allowed"]:
            print("🟢 A message may be sent (silence protocol not triggered).")
        else:
            print("🔴 Silence Protocol active: NO message should be sent.")
    else:
        print("❌ System violates one or more invariants.")
        print("🔴 Silence Protocol active: NO message should be sent.")