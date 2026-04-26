# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script for AMMHM‑Ω Integration
------------------------------------------------------
This script synthetically generates AMM pool data and checks that the
mathematical constructions proposed in the AMMHM‑Ω proposal respect the
Omega Protocol invariants (Φ_N, Φ_Δ, ψ) and the imposed constraints:
    HFI ≤ 0.68
    Φ_N ≥ 0.6
    S_amm ≥ ln(3)

If any invariant is violated, the script raises an AssertionError with
details.  The purpose is to demonstrate that the proposed formulas are
*mathematically sound* (i.e., they produce values in the expected ranges)
and that the Ω‑constraints can be enforced algorithmically.

NOTE: Because we do not have real on‑chain data, we use random but
physically plausible synthetic data.  The validation focuses on the
internal consistency of the formulas, not on the empirical accuracy of
the model.
"""

import numpy as np
import itertools

# ----------------------------------------------------------------------
# Helper functions (stand‑ins for complex geometric/statistical ops)
# ----------------------------------------------------------------------
def synthetic_pool_data(n_pools=200, n_tokens=3, seed=42):
    """
    Generate synthetic reserve vectors for AMM pools.
    Returns:
        reserves: shape (n_pools, n_tokens) – token balances (positive)
        fees: shape (n_pools,) – trading fee in [0.001, 0.01]
        exponent: shape (n_pools,) – constant‑function exponent (≈1)
        volume: shape (n_pools,) – daily volume (log‑normal)
    """
    rng = np.random.default_rng(seed)
    # Reserve balances – log‑normal to mimic wide distribution
    reserves = rng.lognormal(mean=10, sigma=1.5, size=(n_pools, n_tokens))
    # Trading fees – typical range 0.1%–1%
    fees = rng.uniform(0.001, 0.01, size=n_pools)
    # Constant‑function exponent – Uniswap‑like ~1, allow small variation
    exponent = rng.normal(loc=1.0, scale=0.05, size=n_pools)
    exponent = np.clip(exponent, 0.5, 2.0)  # keep physically plausible
    # Daily volume – log‑normal
    volume = rng.lognormal(mean=12, sigma=1.0, size=n_pools)
    return reserves, fees, exponent, volume

def compute_manifold_curvature(reserves):
    """
    Very rough proxy for Ricci scalar curvature of the liquidity manifold.
    We approximate the manifold by a Gaussian kernel density estimate (KDE)
    over the reserve vectors and compute the trace of the Hessian of log‑density.
    For a multivariate Gaussian, Ricci = -dimension (constant).  To introduce
    variability we perturb the covariance with random noise.
    Returns:
        kappa: scalar curvature estimate (can be positive or negative)
    """
    # Center the data
    X = reserves - reserves.mean(axis=0)
    # Empirical covariance
    cov = np.cov(X, rowvar=False)
    # Add small random perturbation to simulate heterogeneity
    rng = np.random.default_rng(123)
    cov_pert = cov + rng.normal(scale=1e-3, size=cov.shape)
    cov_pert = (cov_pert + cov_pert.T) / 2  # enforce symmetry
    # Precision matrix (inverse covariance)
    try:
        prec = np.linalg.inv(cov_pert)
    except np.linalg.LinAlgError:
        # fallback: add ridge
        prec = np.linalg.inv(cov_pert + 1e-6 * np.eye(cov_pert.shape[0]))
    # For a Gaussian, log‑density Hessian = -prec
    # Ricci scalar (trace of Hessian) = -trace(prec)
    kappa = -np.trace(prec)
    return kappa

def compute_impermanent_loss(reserves, price_change_ratio=0.2):
    """
    Approximate IL for each pool using the paper's formula:
        IL = 2*sqrt(delta)/(1+delta) - 1, where delta = price_change_ratio.
    In reality IL depends on token price ratio; we use a uniform delta for
    simplicity and then add pool‑specific noise.
    """
    delta = price_change_ratio
    base_il = 2 * np.sqrt(delta) / (1 + delta) - 1  # negative number
    # Add pool‑specific variation (±10%)
    rng = np.random.default_rng(2024)
    noise = rng.uniform(-0.1, 0.1, size=reserves.shape[0])
    il = base_il * (1 + noise)
    return il

def compute_reserve_concentration(reserves):
    """
    Herfindahl‑Hirschman Index (HHI) across all tokens pooled together.
    """
    total_per_token = reserves.sum(axis=0)          # shape (n_tokens,)
    total_overall = total_per_token.sum()
    shares = total_per_token / total_overall
    hhi = np.sum(shares**2)
    return hhi  # ∈ [1/n_tokens, 1]

def compute_slippage_skew(volume, reserves):
    """
    Proxy slippage for a fixed trade size (e.g., 0.1% of pool depth).
    We approximate slippage ∝ trade_size / liquidity depth.
    Then compute skewness of the resulting distribution.
    """
    trade_size = 0.001 * reserves.sum(axis=1)  # 0.1% of total reserves
    # Simple constant‑product slippage approximation: Δp/p ≈ trade_size / reserves
    slippage = trade_size / reserves.min(axis=1)  # worst‑case token
    # Skewness (Fisher‑Pearson)
    mean = np.mean(slippage)
    std = np.std(slippage)
    if std == 0:
        skew = 0.0
    else:
        skew = np.mean(((slippage - mean) / std) ** 3)
    return skew

def compute_entropy_designs(n_pools, n_designs=3, n_chains=3, seed=2025):
    """
    Synthetic design‑chain distribution.
    Returns Shannon conditional entropy S_amm = - Σ p(k|c) p(c) log p(k|c).
    """
    rng = np.random.default_rng(seed)
    # Random joint distribution p(k,c)
    joint = rng.dirichlet(np.ones(n_designs * n_chains))
    joint = joint.reshape((n_designs, n_chains))
    p_c = joint.sum(axis=0)          # p(c)
    p_k_given_c = joint / p_c[None, :]  # p(k|c)
    # Avoid log(0)
    eps = 1e-12
    S = -np.sum(p_k_given_c * p_c[None, :] * np.log(p_k_given_c + eps))
    return S

# ----------------------------------------------------------------------
# Core AMMHM‑Ω calculations
# ----------------------------------------------------------------------
def ammhm_omega_step(reserves, fees, exponent, volume,
                     Phi_N0=1.0, Phi_Delta0=0.5,
                     eta1=0.3, eta2=0.2,
                     eta3=0.25, eta4=0.15,
                     alpha=0.4, beta=0.3, gamma=0.2, delta=0.1,
                     lambd=0.5, R0=1.0,
                     tau=0):  # tau=0 for simplicity (no lag in synthetic test)
    """
    Execute one time‑step of the AMMHM‑Ω pipeline and return the
    relevant Ω‑variables and constraints.
    """
    # 1. Manifold curvature (proxy Ricci scalar)
    kappa = compute_manifold_curvature(reserves)

    # 2. Impermanent loss dispersion
    il = compute_impermanent_loss(reserves)
    sigma_IL = np.std(il)

    # 3. Reserve concentration (HHI)
    C = compute_reserve_concentration(reserves)

    # 4. Slippage skewness
    s = compute_slippage_skew(volume, reserves)

    # 5. Homogeneity Fragility Index (HFI) – tanh maps to [0,1)
    inner = alpha * np.abs(kappa) + beta * sigma_IL + gamma * C + delta * s
    HFI = np.tanh(inner)  # ensures 0 ≤ HFI < 1

    # 6. Map to Ω‑variables (with optional lag tau – ignored here)
    Phi_N = Phi_N0 - eta1 * HFI + eta2 * (1 - C)
    Phi_Delta = Phi_Delta0 + eta3 * s - eta4 * np.abs(kappa)

    # 7. Invariant ψ from AMM‑manifold curvature
    psi = np.log(np.abs(kappa) / R0) + lambd * HFI

    # 8. Stiffness coefficients (finite‑difference approx.)
    #    We perturb HFI slightly and recompute Phi_N, Phi_Delta.
    eps_h = 1e-6
    inner_plus = alpha * np.abs(kappa) + beta * sigma_IL + gamma * C + delta * (s + eps_h)
    HFI_plus = np.tanh(inner_plus)
    Phi_N_plus = Phi_N0 - eta1 * HFI_plus + eta2 * (1 - C)
    Phi_Delta_plus = Phi_Delta0 + eta3 * (s + eps_h) - eta4 * np.abs(kappa)
    xi_N = (Phi_N_plus - Phi_N) / eps_h
    xi_D = (Phi_Delta_plus - Phi_Delta) / eps_h

    # 9. Entropy gauge from design diversity
    S_amm = compute_entropy_designs(reserves.shape[0])

    # ------------------------------------------------------------------
    # Return a dict for easy inspection / assertion
    # ------------------------------------------------------------------
    return {
        "kappa": kappa,
        "sigma_IL": sigma_IL,
        "C": C,
        "s": s,
        "HFI": HFI,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "psi": psi,
        "xi_N": xi_N,
        "xi_D": xi_D,
        "S_amm": S_amm
    }

# ----------------------------------------------------------------------
# Validation routine – runs many random instances and checks invariants
# ----------------------------------------------------------------------
def validate_ammhm_omega(num_trials=500):
    """
    Run the AMMHM‑Ω step on multiple synthetic data sets and assert that
    all Omega Protocol constraints hold:
        HFI ≤ 0.68
        Φ_N ≥ 0.6
        S_amm ≥ ln(3)  ≈ 1.0986
    If any trial fails, an AssertionError is raised with the offending
    values.
    """
    rng = np.random.default_rng(999)
    for t in range(num_trials):
        # Vary seed slightly to get diverse synthetic pools
        reserves, fees, exponent, volume = synthetic_pool_data(
            n_pools=rng.integers(100, 300),
            n_tokens=rng.choice([2, 3, 4]),
            seed=int(rng.integers(0, 1e6))
        )
        out = ammhm_omega_step(reserves, fees, exponent, volume)

        # ---- Invariant checks ----
        if out["HFI"] > 0.68 + 1e-12:
            raise AssertionError(
                f"Trial {t}: HFI = {out['HFI']:.6f} exceeds 0.68 "
                f"(kappa={out['kappa']:.3f}, sigma_IL={out['sigma_IL']:.3f}, "
                f"C={out['C']:.3f}, s={out['s']:.3f})"
            )
        if out["Phi_N"] < 0.6 - 1e-12:
            raise AssertionError(
                f"Trial {t}: Phi_N = {out['Phi_N']:.6f} below 0.6 "
                f"(HFI={out['HFI']:.3f}, C={out['C']:.3f})"
            )
        if out["S_amm"] < np.log(3) - 1e-12:
            raise AssertionError(
                f"Trial {t}: S_amm = {out['S_amm']:.6f} below ln(3) "
                f"(design entropy too low)"
            )
        # Optional: ensure psi is real (|kappa|>0 guarantees log real)
        assert np.isfinite(out["psi"]), f"Trial {t}: psi non‑finite (kappa={out['kappa']})"

    print(f"All {num_trials} trials passed Omega Protocol invariant checks.")
    print("Sample output from last trial:")
    for k, v in out.items():
        print(f"  {k}: {v:.6f}")

# ----------------------------------------------------------------------
# Run validation when script is executed directly
# ----------------------------------------------------------------------
if __name__ == "__main__":
    validate_ammhm_omega(num_trials=1000)