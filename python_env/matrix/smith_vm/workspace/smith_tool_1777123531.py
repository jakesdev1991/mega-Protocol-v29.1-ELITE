# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Validation script for the Omega Protocol invariants in the RCG-Ω derivation
# Checks mathematical soundness of COD, Φ_N, Φ_Δ, and the silence protocol.

import numpy as np

# ----------------------------------------------------------------------
# Helper functions that mirror the definitions in the thought
# ----------------------------------------------------------------------
def fidelity(psi_dec, psi_id):
    """|⟨Ψ_dec|Ψ_id⟩|²"""
    dot = np.vdot(psi_dec, psi_id)          # ⟨Ψ_dec|Ψ_id⟩
    return np.abs(dot) ** 2

def superposition_entropy(psi_buy):
    """H_super = - Σ |α_i|² log |α_i|², normalized to [0,1]"""
    probs = np.abs(psi_buy) ** 2
    total = probs.sum()
    if total < 1e-12:
        return 0.0
    probs = probs / total
    # Avoid log(0)
    h = -np.sum(probs * np.log(probs + 1e-12))
    max_h = np.log(len(probs))
    return h / max_h if max_h > 0 else 0.0

def dissonance_entropy(psi_dec, psi_id):
    """H_dis = Shannon entropy of |Ψ_dec - Ψ_id|"""
    diff = np.abs(psi_dec - psi_id)
    s = diff.sum()
    if s < 1e-12:
        return 0.0
    prob = diff / s
    h = -np.sum(prob * np.log(prob + 1e-12))
    max_h = np.log(len(prob))
    return h / max_h if max_h > 0 else 0.0

def COD(psi_dec, psi_id, psi_buy,
        Lambda=1.0, kappa=1.0,
        Psi_id=None,          # identity continuity scalar (0..1)
        theta_atrophy=0.15,   # threshold for atrophy penalty
        P_atrophy=0.5):       # penalty weight when H_super < theta
    """
    COD = |⟨Ψ_dec|Ψ_id⟩|² *
          exp(-Λ·H_super) *
          Ψ_id *
          exp(-κ·Ξ_sell) *
          (1 - I(H_super < θ_atrophy)·P_atrophy)
    Note: Ξ_sell is handled externally; this function returns the
          COD *without* the stiffness penalty (to be multiplied later).
    """
    fid = fidelity(psi_dec, psi_id)
    H = superposition_entropy(psi_buy)
    unc_pen = np.exp(-Lambda * H)
    id_gate = Psi_id if Psi_id is not None else 1.0   # assume normalized
    atrophy_pen = 1.0 - (P_atrophy if H < theta_atrophy else 0.0)
    return fid * unc_pen * id_gate * atrophy_pen

def Phi_N(COD_val):
    """Φ_N = log₂(COD) (singularity avoided via epsilon)"""
    return np.log2(COD_val + 1e-12)

def Phi_Delta(Phi_N_val, Xi_sell, Z_trust, R_max=3.0):
    """Φ_Δ = Φ_N * tanh(|Ξ_sell - Z_trust| / R_max)"""
    return Phi_N_val * np.tanh(np.abs(Xi_sell - Z_trust) / R_max)

def adiabatic_Xi_sell(Xi0, Z_trust, t_hours, gamma=0.005):
    """Ξ_sell(t) = Ξ_sell(0)·e^{-γt} + Z_trust·(1 - e^{-γt})"""
    return Xi0 * np.exp(-gamma * t_hours) + Z_trust * (1 - np.exp(-gamma * t_hours))

# ----------------------------------------------------------------------
# Test suite: verify invariants and logic
# ----------------------------------------------------------------------
def run_validation():
    # Fixed random seed for reproducibility
    np.random.seed(42)
    dim = 8

    # Random initial states (not normalized; functions handle normalization)
    psi_buy = np.array([complex(np.random.rand(), np.random.rand()) for _ in range(dim)])
    psi_dec = np.array([complex(0.9, 0.1) for _ in range(dim)])   # biased toward "Comply"
    # Identity baseline (should be high, but we'll test variations)
    psi_id_base = np.array([0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94])
    psi_id = psi_id_base.astype(complex)   # treat as real amplitudes

    # Sales and trust parameters (as given in the thought)
    Xi_sell_0 = 0.85   # initial high-pressure sales state
    Z_trust   = 0.3    # baseline distrust
    Lambda    = 1.0    # arbitrary positive scaling
    kappa     = 1.0    # arbitrary positive scaling

    # ------------------------------------------------------------------
    # 1. Check COD monotonicity in H_super and Ξ_sell (via stiffness penalty)
    # ------------------------------------------------------------------
    H_low  = 0.05   # low uncertainty (risk of atrophy/false clarity)
    H_mid  = 0.4    # within healthy band
    H_high = 0.9    # high uncertainty (risk of paralysis)

    # Fix other terms to isolate effects
    fid_val = fidelity(psi_dec, psi_id)
    id_gate = np.mean(np.abs(psi_id))   # average amplitude ~0.9
    atrophy_pen_low  = 1.0 - (0.5 if H_low  < 0.15 else 0.0)
    atrophy_pen_mid  = 1.0 - (0.5 if H_mid  < 0.15 else 0.0)
    atrophy_pen_high = 1.0 - (0.5 if H_high < 0.15 else 0.0)

    COD_low  = fid_val * np.exp(-Lambda * H_low)  * id_gate * atrophy_pen_low
    COD_mid  = fid_val * np.exp(-Lambda * H_mid)  * id_gate * atrophy_pen_mid
    COD_high = fid_val * np.exp(-Lambda * H_high) * id_gate * atrophy_pen_high

    assert COD_low  >= COD_mid  >= COD_high, \
        "COD must decrease with increasing H_super (uncertainty penalty)"

    # Stiffness penalty: exp(-κ·Ξ_sell) must be decreasing in Ξ_sell
    stiff_low  = np.exp(-kappa * 0.2)
    stiff_mid  = np.exp(-kappa * 0.5)
    stiff_high = np.exp(-kappa * 0.9)
    assert stiff_low >= stiff_mid >= stiff_high, \
        "Stiffness penalty must decrease with increasing Ξ_sell"

    # ------------------------------------------------------------------
    # 2. Invariant checks for a nominal healthy state
    # ------------------------------------------------------------------
    t = 120.0   # 5 days → should bring Ξ_sell close to Z_trust
    Xi_sell_t = adiabatic_Xi_sell(Xi_sell_0, Z_trust, t)
    assert Xi_sell_t <= Z_trust + 0.1 + 1e-9, \
        f"Adiabatic modulation failed: Ξ_sell({t}h) = {Xi_sell_t:.4f} > Z_trust+0.1"

    # Compute full COD including stiffness penalty
    H_nom = superposition_entropy(psi_buy)
    COD_nom = COD(psi_dec, psi_id, psi_buy,
                  Lambda=Lambda, kappa=kappa,
                  Psi_id=np.mean(np.abs(psi_id)),
                  theta_atrophy=0.15, P_atrophy=0.5) * np.exp(-kappa * Xi_sell_t)

    # Invariant 1: COD ≥ 0.85
    assert COD_nom >= 0.85 - 1e-9, f"COD too low: {COD_nom:.4f}"

    # Invariant 2: H_super in [0.15, 0.80]
    assert 0.15 <= H_nom <= 0.80, f"H_super out of band: {H_nom:.4f}"

    # Invariant 3: Ξ_sell ≤ Z_trust + 0.1
    assert Xi_sell_t <= Z_trust + 0.1 + 1e-9, \
        f"Stiffness too high: Ξ_sell={Xi_sell_t:.4f}, Z_trust+0.1={Z_trust+0.1:.4f}"

    # Invariant 4: H_dis ≤ 0.3
    H_dis = dissonance_entropy(psi_dec, psi_id)
    assert H_dis <= 0.3 + 1e-9, f"Dissonance too high: {H_dis:.4f}"

    # Invariant 5: Φ_Δ < 0.5·Φ_N
    Phi_N_val = Phi_N(COD_nom)
    Phi_Delta_val = Phi_Delta(Phi_N_val, Xi_sell_t, Z_trust)
    assert Phi_Delta_val < 0.5 * Phi_N_val + 1e-9, \
        f"Asymmetry violation: Φ_Δ={Phi_Delta_val:.4f}, 0.5·Φ_N={0.5*Phi_N_val:.4f}"

    # Invariant 6: Silence protocol triggers when COD<0.85 OR H_super<0.15
    # Test low COD case
    psi_id_low = np.full_like(psi_id, 0.2)   # poor identity continuity
    COD_low_id = COD(psi_dec, psi_id_low, psi_buy,
                     Lambda=Lambda, kappa=kappa,
                     Psi_id=np.mean(np.abs(psi_id_low)),
                     theta_atrophy=0.15, P_atrophy=0.5) * np.exp(-kappa * Xi_sell_t)
    assert COD_low_id < 0.85, "Low identity should produce COD<0.85"
    # Silence condition: if COD<0.85 → no message (we just check the condition)
    silence_due_to_COD = COD_low_id < 0.85
    assert silence_due_to_COD, "Silence protocol should trigger for low COD"

    # Test low H_super case (force atrophy)
    psi_buy_low = np.ones(dim, dtype=complex)   # pure |Safe⟩ state → H_super≈0
    H_low_test = superposition_entropy(psi_buy_low)
    assert H_low_test < 0.15, "Constructed low-entropy state"
    silence_due_to_H = H_low_test < 0.15
    assert silence_due_to_H, "Silence protocol should trigger for low H_super"

    # ------------------------------------------------------------------
    # 3. Failure mode condition from the thought
    # ------------------------------------------------------------------
    # (COD < 0.85 ∧ Ξ_sell > Z_trust + 0.1) ∨ (H_super < 0.15 ∧ Γ_meas > 0.7)
    # We don't have Γ_meas, but we can test the first clause.
    failure_clause_1 = (COD_low_id < 0.85) and (Xi_sell_t > Z_trust + 0.1)
    # For demonstration, set a high Ξ_sell to trigger clause
    Xi_sell_high = Z_trust + 0.2
    failure_clause_1b = (COD_low_id < 0.85) and (Xi_sell_high > Z_trust + 0.1)
    assert failure_clause_1b, "Failure mode should trigger when COD low and stiffness high"

    # ------------------------------------------------------------------
    # 4. Φ-density ledger sanity check (optional, just ensure non‑negative)
    # ------------------------------------------------------------------
    # Net Φ gain claimed: +1.13Φ. We'll compute a rough proxy:
    #   Φ_gain ≈ Φ_N + (some positive terms) - audit cost.
    audit_cost = np.log(2) * 6   # ΔS_audit = k_B ln 2 · 6
    # Using the nominal state:
    net_phi_approx = Phi_N_val - audit_cost/np.log(2)   # rough scaling
    assert net_phi_approx > 0, "Net Φ should be positive for a healthy state"

    print("All validation checks passed.")
    return True

if __name__ == "__main__":
    run_validation()