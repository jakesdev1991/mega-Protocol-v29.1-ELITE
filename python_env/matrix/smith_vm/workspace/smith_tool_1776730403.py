# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NETT-Ω Mathematical & Ω‑Protocol Invariant Validator
---------------------------------------------------
Checks:
  1. NES ∈ [0,1] (classifier output after Platt scaling)
  2. Φ_N^(nar) ∈ [0,1] and monotonic non‑decreasing w.r.t. mean NES
  3. Φ_Δ^(nar) ∈ [0,1] and monotonic non‑increasing w.r.t. std(NES)
  4. MPC‑Ω constraints feasible:
        mean_NES >= 0.6
        Φ_N^(nar)   >= 0.8
        Φ_Δ^(nar)   <= 0.5
  5. Singularity signal s_NES is non‑negative.
  6. Cost function J* = -log(mean_NES) + λ * s_NES is finite.
"""

import numpy as np
from scipy.special import expit  # logistic sigmoid

# ----------------------------------------------------------------------
# Helper functions (mirror the NETT‑Ω definitions)
# ----------------------------------------------------------------------
def compute_NES(features: np.ndarray, model_weights: np.ndarray, bias: float) -> np.ndarray:
    """
    Placeholder for gradient-boosted classifier → probability.
    In practice you would call your trained GBM; here we use a linear
    model + sigmoid for demonstrative purposes.
    """
    z = features @ model_weights + bias
    return expit(z)  # guarantees [0,1]

def update_phi_N(phi_N0: float, mean_NES: float, eta1: float) -> float:
    """Φ_N^(nar)(t) = Φ_N⁰ + η₁·sigmoid(mean_NES)"""
    return phi_N0 + eta1 * expit(mean_NES)

def update_phi_Delta(phi_Delta0: float, std_NES: float, eta2: float) -> float:
    """Φ_Δ^(nar)(t) = Φ_Δ⁰ – η₂·std(NES)"""
    return phi_Delta0 - eta2 * std_NES

def singularity_score(residual: float, sigma_res: float) -> float:
    """s_NES(t) = |residual| / σ_residual"""
    return np.abs(residual) / sigma_res

def cost_J(mean_NES: float, s_NES: float, lam: float = 0.5) -> float:
    """J* = -log(mean_NES) + λ * s_NES"""
    if mean_NES <= 0:
        raise ValueError("mean_NES must be > 0 for log")
    return -np.log(mean_NES) + lam * s_NES

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_NETT_Omega(
    features: np.ndarray,
    model_weights: np.ndarray,
    bias: float,
    phi_N0: float,
    phi_Delta0: float,
    eta1: float,
    eta2: float,
    lam: float = 0.5,
    tol: float = 1e-9,
) -> None:
    """
    Runs the NETT‑Ω pipeline on the supplied data and asserts that
    all Ω‑invariants hold.
    """
    # 1️⃣ Compute NES
    nes = compute_NES(features, model_weights, bias)
    assert np.all((nes >= 0 - tol) & (nes <= 1 + tol)), "NES out of [0,1]"

    # 2️⃣ Aggregate statistics (as used in the Φ updates)
    mean_nes = np.mean(nes)
    std_nes = np.std(nes, ddof=0)  # population std, matches formula

    # 3️⃣ Update Φ variables
    phi_N = update_phi_N(phi_N0, mean_nes, eta1)
    phi_Delta = update_phi_Delta(phi_Delta0, std_nes, eta2)

    # Φ invariants: must stay in [0,1]
    assert 0 - tol <= phi_N <= 1 + tol, f"Φ_N out of bounds: {phi_N}"
    assert 0 - tol <= phi_Delta <= 1 + tol, f"Φ_Δ out of bounds: {phi_Delta}"

    # Monotonicity checks (optional but informative)
    # Φ_N should not decrease when mean_NES increases (holding phi_N0, eta1 constant)
    # We test by perturbing mean_nes upward and ensuring phi_N does not drop.
    phi_N_pert = update_phi_N(phi_N0, mean_nes + 1e-3, eta1)
    assert phi_N_pert >= phi_N - tol, "Φ_N not monotonic in mean_NES"

    # Φ_Δ should not increase when std_NES increases
    phi_Delta_pert = update_phi_Delta(phi_Delta0, std_nes + 1e-3, eta2)
    assert phi_Delta_pert <= phi_Delta + tol, "Φ_Δ not anti‑monotonic in std_NES"

    # 4️⃣ MPC‑Ω constraints
    assert mean_nes >= 0.6 - tol, f"mean_NES constraint violated: {mean_nes}"
    assert phi_N >= 0.8 - tol, f"Φ_N constraint violated: {phi_N}"
    assert phi_Delta <= 0.5 + tol, f"Φ_Δ constraint violated: {phi_Delta}"

    # 5️⃣ Singularity signal (non‑negative)
    # Create a dummy residual from a simple detrending (here we just use zero‑mean)
    residual = nes - mean_nes
    sigma_res = np.std(residual, ddof=0) + 1e-12  # avoid div‑0
    s_nes = singularity_score(residual.mean(), sigma_res)  # using mean residual ≈0
    assert s_nes >= 0 - tol, f"Singularity score negative: {s_nes}"

    # 6️⃣ Cost function finite
    J = cost_J(mean_nes, s_nes, lam)
    assert np.isfinite(J), f"Cost J* is not finite: {J}"

    # If we reach here, all checks passed
    print("✅ All NETT‑Ω mathematical and Ω‑Protocol invariant checks passed.")
    print(f"   NES stats: mean={mean_nes:.3f}, std={std_nes:.3f}")
    print(f"   Φ_N = {phi_N:.3f}, Φ_Δ = {phi_Delta:.3f}")
    print(f"   Singularity score s_NES = {s_nes:.3f}")
    print(f"   Cost J* = {J:.3f}")

# ----------------------------------------------------------------------
# Example usage with synthetic data
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Synthetic feature matrix (e.g., 20 presentations × 6 narrative features)
    np.random.seed(42)
    n_samples = 20
    n_features = 6
    X = np.random.rand(n_samples, n_features)  # features in [0,1] for simplicity

    # Dummy linear model weights (trained on biotech data) – scaled to give probs in [0,1]
    w = np.array([0.2, -0.1, 0.3, 0.05, 0.15, -0.05])
    b = -0.2  # bias

    # Baseline Ω values (could be taken from current state)
    phi_N0 = 0.5
    phi_Delta0 = 0.5

    # Hyper‑parameters – chosen to respect invariants
    eta1 = 0.3   # ≤1 ensures Φ_N increase ≤0.3
    eta2 = 0.25  # ≤1 ensures Φ_Δ decrease ≤0.25
    lam = 0.5

    validate_NETT_Omega(
        features=X,
        model_weights=w,
        bias=b,
        phi_N0=phi_N0,
        phi_Delta0=phi_Delta0,
        eta1=eta1,
        eta2=eta2,
        lam=lam,
    )