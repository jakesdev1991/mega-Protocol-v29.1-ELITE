# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validation Script for Trauma-Performance Manifold Integration (TPIS v42.1)

This script checks the mathematical soundness and invariant compliance of the proposal.
It focuses on the core equations and invariants presented in Sections 1.2, 2.1, 4, and 5.

If any invariant is violated, the script raises a RuntimeError with a descriptive message.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (directly from the proposal)
# ----------------------------------------------------------------------
def compute_cod(perf_state, safe_state):
    """
    COD = |<Ψ_perf | Ψ_safe>|^2
    States are assumed to be real-valued vectors for simplicity.
    """
    dot = np.dot(perf_state, safe_state)
    norm_perf = np.linalg.norm(perf_state)
    norm_safe = np.linalg.norm(safe_state)
    if norm_perf * norm_safe == 0:
        return 0.0
    fidelity = (dot / (norm_perf * norm_safe)) ** 2
    # Clip to [0,1] as COD is a probability-like overlap
    return min(1.0, max(0.0, fidelity))

def phi_N_from_cod(cod):
    """Φ_N = log2(COD)  (as written in the proposal)"""
    if cod <= 0:
        return -np.inf
    return np.log2(cod)

def psi_from_phi_N(phi_N):
    """ψ = ln(Φ_N)  (Mandatory Coupling)"""
    if phi_N <= 0:
        return -np.inf
    return np.log(phi_N)

def phi_Delta(psi, xi_supp, xi_safe, R_max=3.0):
    """Φ_Δ = ψ * tanh( (|Ξ_supp - Ξ_safe|) / R_max )"""
    R_adapt = abs(xi_supp - xi_safe)
    return psi * np.tanh(R_adapt / R_max)

def delta_S_audit(num_invariants=6):
    """ΔS_audit = k_B ln 2 * C_audit  (we set k_B=1 for natural units)"""
    return np.log(2) * num_invariants

def compute_phi_net(cod, xi_supp, xi_safe, R_max=3.0, num_invariants=6):
    """Φ_net = Φ_N + Φ_Δ - ΔS_audit"""
    phi_N = phi_N_from_cod(cod)
    psi = psi_from_phi_N(phi_N)
    phi_D = phi_Delta(psi, xi_supp, xi_safe, R_max)
    delta_S = delta_S_audit(num_invariants)
    return phi_N + phi_D - delta_S, phi_N, psi, phi_D, delta_S

def metric_non_degeneracy_metric_tensor(xi_supp, xi_safe, gamma=0.01, t=0.0):
    """
    Simplified metric from Section 3.1:
        g_ij = <∂_i Ψ_perf | ∂_j Ψ_safe> * exp(-Γ * |Ξ_supp - Ξ_safe|)
    For validation we assume the inner product term = 1 (aligned basis).
    """
    g = np.exp(-gamma * abs(xi_supp - xi_safe)) * np.eye(2)  # 2x2 for simplicity
    return g

# ----------------------------------------------------------------------
# Invariant checks (Smith Audit)
# ----------------------------------------------------------------------
def check_invariants(state):
    """
    state: dict with keys:
        'cod', 'xi_supp', 'xi_safe', 'H_trauma'
    Returns None if all pass, otherwise raises RuntimeError.
    """
    cod = state['cod']
    xi_supp = state['xi_supp']
    xi_safe = state['xi_safe']
    H_trauma = state['H_trauma']

    # 1. Metric Non-Degeneracy: det(g) > 1e-15
    g = metric_non_degeneracy_metric_tensor(xi_supp, xi_safe)
    det_g = np.linalg.det(g)
    if abs(det_g) <= 1e-15:
        raise RuntimeError(f"Invariant 1 violated: |det(g)| = {det_g:.3e} ≤ 1e-15")

    # 2. Identity Continuity: ψ = ln(Φ_N) ≥ ln(0.95)
    phi_N = phi_N_from_cod(cod)
    if phi_N <= 0:
        raise RuntimeError(f"Invariant 2 violated: Φ_N = log2(COD) = {phi_N:.3f} ≤ 0 (ψ undefined)")
    psi = np.log(phi_N)
    if psi < np.log(0.95):
        raise RuntimeError(f"Invariant 2 violated: ψ = ln(Φ_N) = {psi:.3f} < ln(0.95) ≈ {np.log(0.95):.3f}")

    # 3. Stiffness Matching: Ξ_safe ≥ Ξ_supp
    if xi_safe < xi_supp:
        raise RuntimeError(f"Invariant 3 violated: Ξ_safe = {xi_safe:.3f} < Ξ_supp = {xi_supp:.3f}")

    # 4. Entropy Cap: H_trauma ≤ 0.80
    if H_trauma > 0.80:
        raise RuntimeError(f"Invariant 4 violated: H_trauma = {H_trauma:.3f} > 0.80")

    # 5. Information Conservation: Φ_net ≥ 0 (post-audit)
    phi_net, _, _, _, _ = compute_phi_net(cod, xi_supp, xi_safe)
    if phi_net < 0:
        raise RuntimeError(f"Invariant 5 violated: Φ_net = {phi_net:.3f} < 0")

    # 6. Asymmetry Control: Φ_Δ < 0.5 * Φ_N
    phi_N = phi_N_from_cod(cod)
    psi = np.log(phi_N)
    phi_D = phi_Delta(psi, xi_supp, xi_safe)
    if phi_D >= 0.5 * phi_N:
        raise RuntimeError(f"Invariant 6 violated: Φ_Δ = {phi_D:.3f} ≥ 0.5*Φ_N = {0.5*phi_N:.3f}")

    # All good
    return True

# ----------------------------------------------------------------------
# Example validation using numbers implied by the proposal
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # The proposal claims:
    #   COD ≥ 0.75 (from Section 6.2)
    #   They also claim a net Φ gain of +0.45Φ after audit.
    #   We will test a point that *should* satisfy the claims if the math were consistent.
    #
    # Let's pick COD = 0.80 (just above the threshold)
    # We need to choose xi_supp and xi_safe such that stiffness matching holds (xi_safe >= xi_supp)
    # and H_trauma within cap.
    #
    test_state = {
        'cod': 0.80,
        'xi_supp': 1.0,   # arbitrary suppression stiffness
        'xi_safe': 1.2,   # safety built higher than supply (invariant 3)
        'H_trauma': 0.60  # within entropy cap
    }

    print("Testing state:", test_state)
    try:
        check_invariants(test_state)
        phi_net, phi_N, psi, phi_D, delta_S = compute_phi_net(
            test_state['cod'],
            test_state['xi_supp'],
            test_state['xi_safe']
        )
        print("✅ All invariants satisfied.")
        print(f"   Φ_N = log2(COD) = {phi_N:.3f}")
        print(f"   ψ   = ln(Φ_N)   = {psi:.3f}")
        print(f"   Φ_Δ = {phi_D:.3f}")
        print(f"   ΔS_audit = {delta_S:.3f}")
        print(f"   Φ_net    = {phi_net:.3f}")
    except RuntimeError as e:
        print("❌ Invariant violation:", e)

    # ------------------------------------------------------------------
    # Additionally, demonstrate the internal inconsistency in the proposal:
    #   If COD ∈ [0,1] then Φ_N = log2(COD) ≤ 0, making ψ undefined/negative.
    #   This directly violates Invariant 2 (ψ ≥ ln(0.95) > 0).
    # ------------------------------------------------------------------
    print("\n--- Consistency Check on Φ_N definition ---")
    for cod_test in [0.5, 0.75, 0.9, 1.0]:
        phi_N_test = phi_N_from_cod(cod_test)
        print(f"COD = {cod_test:.2f} → Φ_N = log2(COD) = {phi_N_test:.3f}")
        if phi_N_test > 0:
            print("   → Φ_N positive (would require COD > 1, impossible for overlap density)")
        else:
            print("   → Φ_N ≤ 0 → ψ = ln(Φ_N) undefined or negative → Invariant 2 fails")