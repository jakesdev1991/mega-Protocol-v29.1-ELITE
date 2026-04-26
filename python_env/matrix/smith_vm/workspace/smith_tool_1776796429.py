# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega‑Protocol Validation for the Abstraction‑Leakage Fragility Monitor (ALFM‑Ω)

The script checks the mathematical consistency of the core equations
presented in the proposal and verifies that the Ω‑invariants
(Φ_N, Φ_Δ, ψ) respect the prescribed bounds when the MPC‑Ω
constraints are enforced.

Assumptions for the validation:
- All raw quantities (entropy, variance, version‑skew, centrality) are
  already normalised to the interval [0, 1].
- Weight coefficients (α,β,γ,δ) and mapping coefficients (η₁…η₄, λ) are
  positive scalars chosen by the user.
- Lead times τ₁, τ₂ are non‑negative integers (weeks).
- The abstraction‑manifold Ricci curvature R_abstr is supplied as a
  scalar (positive for “fragmented”, negative for “coherent”).
- S_abstr is the Shannon entropy of the functional‑type distribution,
  already normalised so that its maximum possible value is log(N_types).

If any assertion fails, the script raises an AssertionError with a
descriptive message.
"""

import numpy as np
from typing import Tuple

# ----------------------------------------------------------------------
# Helper functions (direct transcription of the proposal)
# ----------------------------------------------------------------------
def compute_ALI(
    H_map: float,
    sigma2_ann: float,
    V_skew: float,
    centrality: float,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    delta: float = 1.0,
) -> float:
    """
    Abstraction Leakage Index (ALI) ∈ [0,1].
    All inputs are assumed normalised to [0,1].
    """
    raw = alpha * H_map + beta * sigma2_ann + gamma * V_skew + delta * centrality
    return np.tanh(raw)


def map_ALI_to_PhiN(
    ALI: float,
    PhiN0: float = 0.8,
    eta1: float = 0.2,
    eta2: float = 0.1,
    V_skew_lag: float = 0.0,
    tau1: int = 0,
) -> float:
    """
    Φ_N^{(alfm)}(t) = Φ_N^{(0)} - η₁·ALI(t‑τ₁) + η₂·(1‑V_skew(t‑τ₁))
    """
    return PhiN0 - eta1 * ALI + eta2 * (1.0 - V_skew_lag)


def map_ALI_to_PhiDelta(
    ALI: float,
    sigma2_ann_lag: float,
    PhiDelta0: float = 0.2,
    eta3: float = 0.15,
    eta4: float = 0.1,
    tau2: int = 0,
) -> float:
    """
    Φ_Δ^{(alfm)}(t) = Φ_Δ^{(0)} + η₃·σ²_ann(t‑τ₂) - η₄·H_map(t‑τ₂)
    (here we reuse ALI as a proxy for the combined entropy term;
     in a full implementation H_map would be passed separately.)
    """
    # For validation we approximate H_map ≈ ALI (worst‑case bound)
    H_map_est = ALI
    return PhiDelta0 + eta3 * sigma2_ann_lag - eta4 * H_map_est


def compute_psi(
    R_abstr: float,
    ALI: float,
    R0: float = 1.0,
    lam: float = 0.5,
) -> float:
    """
    ψ_alfm(t) = ln(|R_abstr| / R₀) + λ·ALI(t)
    """
    return np.log(np.abs(R_abstr) / R0) + lam * ALI


def compute_S_abstr(
    type_probs: np.ndarray,
) -> float:
    """
    Shannon entropy of the functional‑type distribution.
    Input: array of probabilities that sum to 1.
    Output: raw entropy (not normalised).
    """
    # Avoid log(0)
    p = type_probs[type_probs > 0]
    return -np.sum(p * np.log(p))


# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_alfm_invariants(
    # Raw telemetry (already normalised where indicated)
    H_map: float,
    sigma2_ann: float,
    V_skew: float,
    centrality: float,
    # Lagged versions used in the Φ mappings
    H_map_lag: float,
    sigma2_ann_lag: float,
    V_skew_lag: float,
    # Curvature of the abstraction manifold
    R_abstr: float,
    # Functional‑type distribution (probabilities)
    type_probs: np.ndarray,
    # Hyper‑parameters (can be tuned; defaults reflect a “reasonable” regime)
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    delta: float = 1.0,
    eta1: float = 0.2,
    eta2: float = 0.1,
    eta3: float = 0.15,
    eta4: float = 0.1,
    lam: float = 0.5,
    PhiN0: float = 0.8,
    PhiDelta0: float = 0.2,
    R0: float = 1.0,
    tau1: int = 0,
    tau2: int = 0,
) -> Tuple[float, float, float, float, float]:
    """
    Returns (ALI, Φ_N, Φ_Δ, ψ, S_abstr) after checking all Ω‑constraints.
    Raises AssertionError if any invariant is violated.
    """
    # 1. Compute ALI
    ALI = compute_ALI(H_map, sigma2_ann, V_skew, centrality,
                      alpha, beta, gamma, delta)
    assert 0.0 <= ALI <= 1.0, f"ALI out of bounds: {ALI}"

    # 2. Map to Ω‑variables
    PhiN = map_ALI_to_PhiN(ALI, PhiN0, eta1, eta2, V_skew_lag, tau1)
    PhiDelta = map_ALI_to_PhiDelta(ALI, sigma2_ann_lag,
                                   PhiDelta0, eta3, eta4, tau2)

    # 3. Compute ψ from abstraction‑manifold curvature
    psi = compute_psi(R_abstr, ALI, R0, lam)

    # 4. Compute abstraction‑type entropy (gauge)
    S_abstr = compute_S_abstr(type_probs)

    # ------------------------------------------------------------------
    # Ω‑Invariant checks (as stated in the proposal)
    # ------------------------------------------------------------------
    # ALI must stay below the leakage threshold used in the MPC‑Ω QP
    assert ALI <= 0.65, f"ALI too high (≥0.65): {ALI}"

    # Φ_N connectivity must remain above the minimal viable value
    assert PhiN >= 0.6, f"Φ_N below safety limit: {PhiN}"

    # Abstraction‑type entropy must be at least log(3) ≈ 1.099
    # (ensures sufficient diversity of functional types)
    assert S_abstr >= np.log(3), f"S_abstr too low: {S_abstr} < log(3)"

    # Optional: ψ should remain finite (no numerical overflow)
    assert np.isfinite(psi), f"ψ is non‑finite: {psi}"

    # Optional: Φ_Δ should be non‑negative (asymmetry measure)
    assert PhiDelta >= 0.0, f"Φ_Δ negative: {PhiDelta}"

    return ALI, PhiN, PhiDelta, psi, S_abstr


# ----------------------------------------------------------------------
# Example usage with synthetic data
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Simulated telemetry (all in [0,1] except curvature)
    np.random.seed(42)
    H_map = np.random.rand()
    sigma2_ann = np.random.rand()
    V_skew = np.random.rand()
    centrality = np.random.rand()

    # Lagged values (could be same as current for a steady‑state test)
    H_map_lag = H_map
    sigma2_ann_lag = sigma2_ann
    V_skew_lag = V_skew

    # Curvature: choose a small negative value (coherent basin)
    R_abstr = -0.3

    # Functional‑type distribution: 4 types, random probabilities
    raw = np.random.rand(4)
    type_probs = raw / raw.sum()

    # Run validation
    try:
        ALI, PhiN, PhiDelta, psi, S_abstr = validate_alfm_invariants(
            H_map, sigma2_ann, V_skew, centrality,
            H_map_lag, sigma2_ann_lag, V_skew_lag,
            R_abstr, type_probs
        )
        print("✅ All Ω‑invariants satisfied.")
        print(f"ALI          : {ALI:.4f}")
        print(f"Φ_N          : {PhiN:.4f}")
        print(f"Φ_Δ          : {PhiDelta:.4f}")
        print(f"ψ            : {psi:.4f}")
        print(f"S_abstr      : {S_abstr:.4f}  (log(3) = {np.log(3):.4f})")
    except AssertionError as e:
        print("❌ Ω‑Invariant violation:")
        print(e)