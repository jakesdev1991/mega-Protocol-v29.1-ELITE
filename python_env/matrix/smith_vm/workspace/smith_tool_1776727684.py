# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol – CLEM-Ω v2 Mathematical Soundness Validator
-----------------------------------------------------------
Checks:
  * Feature standardization (zero mean, unit variance)
  * Poloidal correlation length regularisation (eps)
  * Credential entropy zero‑weight guard
  * Radial correlation length via explicit Euclidean metric
  * Jerk-stability metric bounds (using corrected definition)
  * Constraint feasibility (CLE_max vs dynamic CLE0)
  * Dimensionless CLE combination
"""

import numpy as np
from typing import Tuple, List

# ----------------------------------------------------------------------
# Helper functions (to be replaced by actual implementations in production)
# ----------------------------------------------------------------------
def standardize(X: np.ndarray) -> np.ndarray:
    """Zero‑mean, unit‑variance standardization (column‑wise)."""
    return (X - np.nanmean(X, axis=0)) / (np.nanstd(X, axis=0) + 1e-12)

def jerk_stability(j: np.ndarray) -> float:
    """
    Corrected jerk‑stability metric:
        S_j = 1 / (1 + |excess kurtosis|)
    excess kurtosis = E[(j-μ)^4]/σ^4 - 3
    Returns value in (0,1]; 1 for perfectly stable (Gaussian) jerk.
    """
    mu = np.nanmean(j)
    sigma = np.nanstd(j) + 1e-12
    excess_kurt = np.nanmean(((j - mu) / sigma) ** 4) - 3
    return 1.0 / (1.0 + np.abs(excess_kurt))

def compute_CLE(R: np.ndarray, S: np.ndarray, E: np.ndarray, M: np.ndarray,
                weights: Tuple[float, float, float, float]) -> np.ndarray:
    """Linear CLE with standardized inputs."""
    a, b, g, d = weights
    return a * R + b * S + g * E + d * M

def poloidal_corr_length(R: np.ndarray, S: np.ndarray,
                         E: np.ndarray, M: np.ndarray, eps: float = 1e-8) -> float:
    """Regularised poloidal correlation length."""
    vars_ = [np.nanvar(R), np.nanvar(S), np.nanvar(E), np.nanvar(M)]
    num = max(vars_) + eps
    den = min(vars_) + eps
    return num / den

def credential_entropy(R: np.ndarray, S: np.ndarray, E: np.ndarray,
                       eps: float = 1e-12) -> float:
    """Shannon entropy of risk weights w = R*(1-S)*E, with zero‑weight guard."""
    w = R * (1.0 - S) * E
    total = np.nansum(w)
    if total < eps:                     # no credible risk weight
        return 0.0
    p = w / total
    # avoid log(0)
    p = np.where(p < eps, eps, p)
    return -np.nansum(p * np.log(p))

def radial_corr_length(unit_features: np.ndarray,
                       CLE_vals: np.ndarray) -> float:
    """
    unit_features: (B, F) matrix of standardized unit‑level features
    CLE_vals:    (B,) CLE per unit
    Returns ξ_N = ( (1/B) Σ ||∇_b CLE_b||^2 )^{-1/2}
    Gradient approximated by finite differences on each feature dimension.
    """
    B, F = unit_features.shape
    grad_sq_sum = 0.0
    for f in range(F):
        # central difference gradient w.r.t. feature f
        # perturb feature f by small delta and recompute CLE (linear model)
        delta = 1e-6
        pert = unit_features.copy()
        pert[:, f] += delta
        # Assuming linear CLE: CLE = w·[R,S,E,M] ; we need mapping from unit_features
        # to the four credential features. For validation we treat unit_features as
        # a proxy; in practice replace with actual Jacobian.
        CLE_pert = a * pert[:, 0] + b * pert[:, 1] + g * pert[:, 2] + d * pert[:, 3]
        grad = (CLE_pert - CLE_vals) / delta
        grad_sq_sum += np.nansum(grad ** 2)
    xi_sq = (1.0 / B) * grad_sq_sum
    return 1.0 / np.sqrt(xi_sq + eps)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_clem_omega(
    R_raw: np.ndarray,
    S_raw: np.ndarray,
    E_raw: np.ndarray,
    M_raw: np.ndarray,
    unit_feat_raw: np.ndarray,
    weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25),
    CLE_max: float = 2.0,
    eps: float = 1e-8,
    jerk_data: np.ndarray = None,
) -> None:
    """
    Raises AssertionError if any Omega‑Protocol invariant is violated.
    """
    # 1. Standardize inputs
    R = standardize(R_raw)
    S = standardize(S_raw)
    E = standardize(E_raw)
    M = standardize(M_raw)

    # 2. Compute CLE
    CLE = compute_CLE(R, S, E, M, weights)

    # 3. Poloidal correlation length (must be finite)
    xi_delta = poloidal_corr_length(R, S, E, M, eps)
    assert np.isfinite(xi_delta), f"Poloidal correlation length non‑finite: {xi_delta}"
    assert xi_delta > 0, f"Poloidal correlation length non‑positive: {xi_delta}"

    # 4. Credential entropy (must be defined)
    Sh = credential_entropy(R, S, E, eps)
    assert np.isfinite(Sh), f"Credential entropy non‑finite: {Sh}"
    assert Sh >= 0, f"Credential entropy negative: {Sh}"

    # 5. Radial correlation length (requires explicit metric)
    xi_N = radial_corr_length(standardize(unit_feat_raw), CLE)
    assert np.isfinite(xi_N), f"Radial correlation length non‑finite: {xi_N}"
    assert xi_N > 0, f"Radial correlation length non‑positive: {xi_N}"

    # 6. Jerk‑stability metric (if provided)
    if jerk_data is not None:
        Sj = jerk_stability(jerk_data)
        assert 0.0 < Sj <= 1.0 + 1e-12, f"Jerk stability out of bounds: {Sj}"

    # 7. Scalar invariant ψ_CLE ≤ 0  (using dynamic CLE0 = rolling median)
    CLE0 = np.nanmedian(CLE)          # dynamic reference
    psi = np.log(CLE / (CLE0 + eps))
    assert np.all(psi <= 1e-9), f"ψ_CLE > 0 (CLE exceeds reference): max psi = {np.nanmax(psi)}"

    # 8. Hard CLE constraint
    assert np.all(CLE <= CLE_max + eps), f"CLE exceeds hard limit {CLE_max}: max CLE = {np.nanmax(CLE)}"

    # 9. Dimensionless check (already ensured by standardization)
    #    Additionally, verify that weights sum to 1 (optional convention)
    assert abs(np.sum(weights) - 1.0) < 1e-9, "Weights should sum to 1 for dimensionless CLE"

    print("✅ All Omega‑Protocol mathematical invariants satisfied.")

# ----------------------------------------------------------------------
# Example usage (replace with real data in production)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Synthetic data for demonstration
    np.random.seed(42)
    n_samples = 100
    R_raw = np.random.randn(n_samples) * 0.5 + 1.0   # rotation velocity (arbitrary units)
    S_raw = np.random.rand(n_samples)               # strength score [0,1]
    E_raw = np.random.randn(n_samples) * 0.2        # expiration deviation
    M_raw = np.random.randn(n_samples) * 0.3        # mapping volatility
    unit_feat_raw = np.random.randn(n_samples, 4)   # e.g., size, sector, geography, budget
    jerk_data = np.random.randn(n_samples) * 0.1    # jerk time series

    try:
        validate_clem_omega(
            R_raw, S_raw, E_raw, M_raw,
            unit_feat_raw,
            weights=(0.3, 0.2, 0.3, 0.2),
            CLE_max=2.0,
            jerk_data=jerk_data,
        )
    except AssertionError as e:
        print("❌ Omega‑Protocol violation:", e)