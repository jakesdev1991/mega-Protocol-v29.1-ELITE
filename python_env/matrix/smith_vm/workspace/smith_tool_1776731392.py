# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the CVT‑Ω proposal (Cross‑Domain Valuation Transfer for Tokamak Research Prioritization).

The script checks that the core mathematical expressions respect the Omega Protocol invariants:
    • Φ_N (process connectivity) must remain in the interval [0, 1].
    • Φ_Δ (asymmetry) must remain non‑negative (Ω treats it as a measure of destabilising imbalance).
    • The URP (Undervalued Research Potential) score, being a weighted sum of normalized features,
      should lie in [0, 1] when the feature vectors are normalised and the weights sum to 1.
    • The cost function used in the MPC‑Ω optimisation,
          C = -log(ŪRP) + λ·s_URP
      must be finite (ŪRP > 0) and non‑negative for λ ≥ 0.

We generate synthetic data to exercise the formulas and assert the invariants.
If any assertion fails, an informative error is raised.

NOTE: This is a *minimal* sanity‑check; in practice the parameters (η₁, η₂, τ, λ, …)
would be calibrated against historical tokamak breakthrough data.
"""

import numpy as np

def sigmoid(x: np.ndarray) -> np.ndarray:
    """Standard logistic sigmoid, output in (0, 1)."""
    return 1.0 / (1.0 + np.exp(-x))

def compute_urp(feature_matrix: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Compute URP scores for a set of projects.
    Parameters
    ----------
    feature_matrix : shape (n_projects, n_features)
        Each row is a normalized feature vector h_tok(p) ∈ [0,1]^n_features.
    weights : shape (n_features,)
        Non‑negative weights that sum to 1 (transfer‑learned from biotech model).
    Returns
    -------
    urp : shape (n_projects,)
        URP(p) = w·h_tok(p)  →  lies in [0,1] if inputs are valid.
    """
    if not np.allclose(weights.sum(), 1.0):
        raise ValueError("Weights must sum to 1 for a proper convex combination.")
    if np.any(weights < 0):
        raise ValueError("Weights must be non‑negative.")
    if not (np.all(feature_matrix >= 0) and np.all(feature_matrix <= 1)):
        raise ValueError("Feature matrix entries must be normalised to [0,1].")
    urp = feature_matrix @ weights
    # Numerical safety: clip to [0,1] (should already hold)
    return np.clip(urp, 0.0, 1.0)

def update_phi_n(phi_n0: float, eta1: float, urp_vals: np.ndarray) -> float:
    """
    Φ_N^(val)(t) = Φ_N^(0) + η₁ · sigmoid( mean(URP) )
    Invariant: Φ_N ∈ [0,1].
    """
    if eta1 < 0:
        raise ValueError("η₁ must be non‑negative.")
    mean_urp = urp_vals.mean()
    phi_n = phi_n0 + eta1 * sigmoid(mean_urp)
    # Enforce invariant
    if not (0.0 <= phi_n <= 1.0):
        raise ValueError(f"Φ_N out of bounds: {phi_n:.4f} (Φ_N⁰={phi_n0}, η₁={eta1}, mean URP={mean_urp:.4f})")
    return phi_n

def update_phi_delta(phi_delta0: float, eta2: float, urp_max_lagged: float) -> float:
    """
    Φ_Δ^(val)(t) = Φ_Δ^(0) - η₂ · URP_max(t‑τ)
    Invariant: Φ_Δ ≥ 0 (asymmetry cannot be negative in Ω).
    """
    if eta2 < 0:
        raise ValueError("η₂ must be non‑negative.")
    phi_delta = phi_delta0 - eta2 * urp_max_lagged
    if phi_delta < 0:
        raise ValueError(f"Φ_Δ became negative: {phi_delta:.4f} (Φ_Δ⁰={phi_delta0}, η₂={eta2}, URP_max lagged={urp_max_lagged:.4f})")
    return phi_delta

def cost_function(mean_urp: float, s_urp: float, lam: float = 0.1) -> float:
    """
    C = -log(ŪRP) + λ·s_URP
    Requires ŪRP > 0 for the log to be finite.
    """
    if mean_urp <= 0:
        raise ValueError(f"Mean URP must be > 0 for log term, got {mean_urp}")
    if lam < 0:
        raise ValueError("λ must be non‑negative.")
    cost = -np.log(mean_urp) + lam * s_urp
    if cost < 0:
        # Theoretically possible if s_URP is negative; we enforce s_URP ≥ 0 elsewhere.
        raise ValueError(f"Cost function negative: {cost:.4f}")
    return cost

def run_validation():
    # ------------------------------
    # Synthetic data generation
    # ------------------------------
    np.random.seed(42)
    n_projects = 20
    n_features = 5

    # Normalised feature vectors (each in [0,1])
    X = np.random.rand(n_projects, n_features)

    # Transfer‑learned weights (non‑negative, sum to 1)
    w = np.random.rand(n_features)
    w = w / w.sum()

    # Baseline Omega invariants (chosen within feasible range)
    phi_n0 = 0.6      # initial process connectivity
    phi_delta0 = 0.5  # initial asymmetry
    eta1 = 0.3        # scaling for Φ_N update
    eta2 = 0.2        # scaling for Φ_Δ update
    tau = 12          # months lag (not directly used in the scalar check)
    lam = 0.1         # λ in cost function

    # ------------------------------
    # Step 1: Compute URP
    # ------------------------------
    urp = compute_urp(X, w)
    assert np.all((urp >= 0) & (urp <= 1)), "URP values outside [0,1]"

    mean_urp = urp.mean()
    urp_max = urp.max()
    # Simulate a lagged max (here we just reuse current max for simplicity)
    urp_max_lagged = urp_max

    # ------------------------------
    # Step 2: Update Omega variables
    # ------------------------------
    phi_n = update_phi_n(phi_n0, eta1, urp)
    phi_delta = update_phi_delta(phi_delta0, eta2, urp_max_lagged)

    # ------------------------------
    # Step 3: Anomaly score (s_URP) – simple z‑score of the time‑series;
    #          for synthetic data we use the standard deviation across projects.
    # ------------------------------
    s_urp = np.abs(urp - mean_urp) / (urp.std() + 1e-12)
    s_urp_agg = s_urp.mean()   # aggregate anomaly score used in MPC‑Ω

    # ------------------------------
    # Step 4: Cost function
    # ------------------------------
    cost = cost_function(mean_urp, s_urp_agg, lam)

    # ------------------------------
    # Final invariant checks (beyond those already asserted inside functions)
    # ------------------------------
    assert 0.0 <= phi_n <= 1.0, f"Φ_N invariant violated: {phi_n}"
    assert phi_delta >= 0.0, f"Φ_Δ invariant violated: {phi_delta}"
    assert cost >= 0.0, f"Cost function invariant violated: {cost}"

    # If we reach here, all invariants hold for this synthetic scenario.
    print("✅ All Omega Protocol invariants satisfied.")
    print(f"  URP stats: mean={mean_urp:.4f}, max={urp_max:.4f}")
    print(f"  Φ_N⁰={phi_n0:.3f} → Φ_N={phi_n:.4f}")
    print(f"  Φ_Δ⁰={phi_delta0:.3f} → Φ_Δ={phi_delta:.4f}")
    print(f"  Aggregated anomaly score s_URP={s_urp_agg:.4f}")
    print(f"  MPC‑Ω cost C = -log(ŪRP)+λ·s_URP = {cost:.4f}")

if __name__ == "__main__":
    run_validation()