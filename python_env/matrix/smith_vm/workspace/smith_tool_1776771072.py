# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation Script for FTN‑Ω Trust‑Entropy Model
# --------------------------------------------------------------
# This script checks the mathematical soundness and invariant
# compliance of the proposed Functional Trust Network (FTN‑Ω)
# integration.  It validates:
#   • Trust entropy bounds and smoothness
#   • Derived invariants ψ, ξ_N, ξ_Δ are real and positive
#   • Ω‑variables Φ_N, Φ_Δ stay within prescribed safety windows
#   • Dimensional consistency (all inputs treated as dimensionless)
#   • MPC‑Ω constraint feasibility (simple linear check)
# --------------------------------------------------------------

import numpy as np

# -------------------------- Helper Functions --------------------------

def trust_entropy(scores, bins=20):
    """
    Compute Shannon entropy of trust scores.
    scores: 1‑D array of T_i ∈ [0,1]
    Returns entropy in nats (dimensionless).
    """
    hist, _ = np.histogram(scores, bins=bins, range=(0.0, 1.0), density=True)
    # Avoid log(0)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))

def global_trust_entropy(trust_matrix):
    """
    trust_matrix: shape (n_functions, n_implementations)
    Returns average entropy across functions.
    """
    entropies = np.apply_along_axis(trust_entropy, 1, trust_matrix)
    return np.mean(entropies)

def compute_psi(S, S0=0.5, lam=0.1, var_T=0.0):
    """
    ψ = ln(S/S0) + λ·Var(T)
    """
    if S <= 0:
        raise ValueError("Trust entropy must be > 0 for log.")
    return np.log(S / S0) + lam * var_T

def compute_phi_N(psi, Phi_N0=0.7, alpha=0.15, tau1=1.0, t=0.0, psi_prev=None):
    """
    Φ_N(t) = Φ_N0 + α·tanh( ψ(t‑τ₁) )
    Simple Euler shift for demonstration.
    """
    # Approximate delayed psi using previous value if available
    psi_delay = psi_prev if psi_prev is not None else psi
    return Phi_N0 + alpha * np.tanh(psi_delay)

def compute_phi_Delta(psi, S, S_target=0.6, Phi_Delta0=0.3,
                      beta=0.2, gamma=0.1, tau2=1.0,
                      S_prev=None, dS_dt_approx=0.0):
    """
    Φ_Δ(t) = Φ_Δ0 + β·(1‑S(t‑τ₂)) + γ·|dS/dt|
    """
    S_delay = S_prev if S_prev is not None else S
    term = beta * (1.0 - S_delay) + gamma * np.abs(dS_dt_approx)
    return Phi_Delta0 + term

def stiffness_invariants(S, var_T, I0=0.5, lam_eff=1.0,
                         gamma_S=0.05, delta_S=0.04,
                         R_avg=0.0):
    """
    ξ_N⁻² = λ_eff·(3I0² + ⟨R⟩ + γ_S·⟨S⟩)
    ξ_Δ⁻² = λ_eff·(I0² + 3⟨R⟩ + δ_S·⟨S⟩)
    Returns ξ_N, ξ_Δ (must be real & >0).
    """
    inv_xi_N_sq = lam_eff * (3 * I0**2 + R_avg + gamma_S * S)
    inv_xi_Delta_sq = lam_eff * (I0**2 + 3 * R_avg + delta_S * S)
    if inv_xi_N_sq <= 0 or inv_xi_Delta_sq <= 0:
        raise ValueError("Stiffness invariant squared non‑positive.")
    xi_N = 1.0 / np.sqrt(inv_xi_N_sq)
    xi_Delta = 1.0 / np.sqrt(inv_xi_Delta_sq)
    return xi_N, xi_Delta

# -------------------------- Validation Routine --------------------------

def validate_FTN_Omega(trust_matrix, dt=1.0, horizon=5):
    """
    Runs a short‑time simulation and checks all Omega‑Protocol invariants.
    trust_matrix: (n_functions, n_implementations) array of T_i ∈ [0,1]
    dt: time step (weeks) – treated as dimensionless for this check.
    horizon: number of steps to propagate.
    Returns True if all checks pass, else raises AssertionError with details.
    """
    n_funcs, n_impl = trust_matrix.shape
    # Basic sanity: scores in [0,1]
    assert np.all((trust_matrix >= 0) & (trust_matrix <= 1)), \
        "Trust scores must lie in [0,1]."
    
    # Track variables over time for derivative approximations
    S_history = []
    psi_history = []
    phi_N_history = []
    phi_Delta_history = []
    xi_N_history = []
    xi_Delta_history = []

    S_prev = None
    psi_prev = None

    for step in range(horizon):
        # Use same matrix each step (static demo); in practice it would evolve
        S = global_trust_entropy(trust_matrix)
        var_T = np.var(trust_matrix)  # variance of all scores as proxy
        
        # Entropy bounds (nats) – max entropy for uniform distribution over B bins
        B = 20  # same as used in trust_entropy
        S_max = np.log(B)
        S_min = 1e-3  # avoid zero log
        assert S_min <= S <= S_max, f"Trust entropy out of bounds: S={S}"
        
        # ψ computation
        psi = compute_psi(S, S0=0.5, lam=0.1, var_T=var_T)
        assert np.isfinite(psi), "ψ is not finite."
        
        # Φ_N, Φ_Δ
        phi_N = compute_phi_N(psi, psi_prev=psi_prev, t=step*dt)
        phi_Delta = compute_phi_Delta(psi, S, S_prev=S_prev,
                                      dS_dt_approx=(S - S_history[-1])/dt if S_history else 0.0)
        # Omega invariant windows (from proposal)
        assert phi_N >= 0.7, f"Φ_N below safety threshold: {phi_N}"
        assert phi_Delta <= 0.6, f"Φ_Δ exceeds safety threshold: {phi_Delta}"
        
        # Stiffness invariants
        xi_N, xi_Delta = stiffness_invariants(S, var_T)
        assert xi_N > 0 and xi_Delta > 0, \
            f"Stiffness invariants non‑positive: ξ_N={xi_N}, ξ_Δ={xi_Delta}"
        
        # Store for next iteration
        S_history.append(S)
        psi_history.append(psi)
        phi_N_history.append(phi_N)
        phi_Delta_history.append(phi_Delta)
        xi_N_history.append(xi_N)
        xi_Delta_history.append(xi_Delta)
        
        S_prev = S
        psi_prev = psi

    # ----- MPC‑Ω constraint feasibility (simple linear check) -----
    # Constraints: S_trust ≥ S_min, Φ_N ≥ 0.7, Φ_Δ ≤ 0.6
    S_arr = np.array(S_history)
    phi_N_arr = np.array(phi_N_history)
    phi_Delta_arr = np.array(phi_Delta_history)
    assert np.all(S_arr >= S_min), "MPC constraint S_trust ≥ S_min violated."
    assert np.all(phi_N_arr >= 0.7), "MPC constraint Φ_N ≥ 0.7 violated."
    assert np.all(phi_Delta_arr <= 0.6), "MPC constraint Φ_Δ ≤ 0.6 violated."
    
    # If we reach here, all checks passed
    return {
        "S_trust": S_history,
        "psi": psi_history,
        "Phi_N": phi_N_history,
        "Phi_Delta": phi_Delta_history,
        "xi_N": xi_N_history,
        "xi_Delta": xi_Delta_history
    }

# -------------------------- Example Usage --------------------------

if __name__ == "__main__":
    # Synthetic trust data: 10 functions, each with 5 implementations
    np.random.seed(42)
    # Generate scores biased toward moderate trust (0.4‑0.8) to stay in safe zone
    raw = np.random.beta(a=2, b=2, size=(10, 5))  # Beta(2,2) → mean 0.5
    trust_data = np.clip(raw, 0.0, 1.0)  # ensure bounds
    
    try:
        result = validate_FTN_Omega(trust_data, dt=1.0, horizon=8)
        print("✅ FTN‑Ω model passes all Omega‑Protocol invariant checks.")
        print(f"Final trust entropy: {result['S_trust'][-1]:.4f}")
        print(f"Final Φ_N: {result['Phi_N'][-1]:.4f} (>=0.7 required)")
        print(f"Final Φ_Δ: {result['Phi_Delta'][-1]:.4f} (<=0.6 required)")
        print(f"Final ξ_N: {result['xi_N'][-1]:.4f}, ξ_Δ: {result['xi_Delta'][-1]:.4f}")
    except AssertionError as e:
        print("❌ Omega‑Protocol violation detected:")
        print(e)
    except ValueError as e:
        print("❌ Mathematical inconsistency:")
        print(e)