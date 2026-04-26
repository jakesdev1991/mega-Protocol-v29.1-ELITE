# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol validation for the AMM Homogeneity Monitor (AMMHM‑Ω).

The script synthesises on‑chain data, computes the quantities described in the
proposal, and asserts that all Omega‑Protocol invariants and constraints hold.
"""

import numpy as np
from sklearn.metrics import pairwise_distances
from sklearn.neighbors import NearestNeighbors

# ----------------------------------------------------------------------
# Helper functions (stand‑ins for more sophisticated geometry)
# ----------------------------------------------------------------------
def compute_reserve_data(n_pools=50, n_tokens=3, seed=0):
    """Generate synthetic reserve vectors and derived stats."""
    rng = np.random.default_rng(seed)
    # Reserve balances (positive)
    reserves = rng.exponential(scale=1e6, size=(n_pools, n_tokens))
    # Normalise to have comparable total liquidity
    reserves = reserves / reserves.sum(axis=1, keepdims=True) * 1e7

    # Constant‑product exponent (n=1 for Uniswap‑like)
    n_exp = np.ones(n_pools)  # could vary slightly
    # Trading fee (bps)
    fee = rng.uniform(0.0005, 0.003, size=n_pools)

    # Simulated price change ratio Δ (log‑normal around 1)
    delta = rng.lognormal(mean=0.0, sigma=0.2, size=n_pools)
    # Impermanent loss per paper: IL = 2*sqrt(delta)/(1+delta) - 1
    il = 2 * np.sqrt(delta) / (1 + delta) - 1

    # Slippage for a fixed trade size (approximate via constant‑product formula)
    trade_size = 1e4  # notional in quote token
    slippage = trade_size / (reserves[:, 0] * reserves[:, 1])  # proxy
    slippage_skew = np.mean(((slippage - np.mean(slippage))**3)) / (np.std(slippage)**3 + 1e-12)

    # Reserve concentration (HHI) across all pools for each token, then average
    token_shares = reserves / reserves.sum(axis=0)  # shape (n_pools, n_tokens)
    hhi_per_token = np.sum(token_shares**2, axis=0)  # HHI per token
    concentration = np.mean(hhi_per_token)  # overall concentration ∈ [1/n_tokens, 1]

    return {
        "reserves": reserves,
        "n_exp": n_exp,
        "fee": fee,
        "delta": delta,
        "il": il,
        "slippage": slippage,
        "slippage_skew": slippage_skew,
        "concentration": concentration,
    }

def estimate_ricci_scalar(reserve_vectors):
    """
    Very rough estimator of Ricci scalar on the point cloud of reserve vectors.
    We use the inverse of the average squared pairwise distance as a proxy for
    positive curvature (more clustered → larger value). This is ONLY for
    validation; a real implementation would use discrete Ricci curvature.
    """
    dists = pairwise_distances(reserve_vectors, metric='euclidean')
    np.fill_diagonal(dists, np.inf)  # ignore self‑distance
    avg_sq_dist = np.mean(dists**2)
    # Avoid division by zero; small distance → large curvature
    return 1.0 / (avg_sq_dist + 1e-12)

def compute_design_entropy(n_pools=50, n_designs=3, seed=1):
    """Synthetic design‑type distribution and conditional entropy."""
    rng = np.random.default_rng(seed)
    # Assign each pool a design id (0..n_designs-1) with a slight bias
    design_ids = rng.choice(n_designs, size=n_pools, p=[0.6, 0.3, 0.1])
    # Context: blockchain (2 chains)
    chain_ids = rng.choice(2, size=n_pools, p=[0.7, 0.3])
    # Joint distribution p(design, chain)
    joint = np.zeros((n_designs, 2))
    for d, c in zip(design_ids, chain_ids):
        joint[d, c] += 1
    joint /= joint.sum()
    # Marginals
    p_design = joint.sum(axis=1)
    p_chain = joint.sum(axis=0)
    # Conditional p(design|chain) = joint / p_chain
    cond = joint / p_chain[None, :]  # shape (n_designs, 2)
    # Shannon conditional entropy S = - Σ p(c) Σ p(d|c) log p(d|c)
    entropy = -np.sum(p_chain[:, None] * cond * np.log(cond + 1e-12))
    return entropy, design_ids, chain_ids

# ----------------------------------------------------------------------
# Core computation of AMMHM‑Ω quantities
# ----------------------------------------------------------------------
def compute_ammhm_omega(data):
    reserves = data["reserves"]
    il = data["il"]
    slippage_skew = data["slippage_skew"]
    concentration = data["concentration"]

    # 1. Manifold curvature proxy (Ricci scalar)
    kappa = estimate_ricci_scalar(reserves)  # positive scalar

    # 2. Impermanent loss dispersion
    sigma_il = np.std(il)

    # 3. Homogeneity Fragility Index
    # Choose positive weights (calibrated elsewhere)
    alpha, beta, gamma, delta = 1.0, 1.0, 1.0, 0.5  # δ≥0 to keep argument non‑negative
    arg = alpha * np.abs(kappa) + beta * sigma_il + gamma * concentration + delta * abs(slippage_skew)
    hfi = np.tanh(arg)  # guaranteed in [0,1]

    # 4. Mapping to Omega variables (baseline values chosen in [0,1])
    Phi_N0, Phi_Delta0 = 0.8, 0.2
    tau = 0  # ignore lag for static validation
    eta1, eta2, eta3, eta4 = 0.15, 0.1, 0.12, 0.08
    Phi_N = Phi_N0 - eta1 * hfi + eta2 * (1 - concentration)
    Phi_Delta = Phi_Delta0 + eta3 * abs(slippage_skew) - eta4 * np.abs(kappa)

    # 5. Invariant ψ
    R0 = 1.0  # reference curvature
    lam = 0.3
    psi = np.log(np.abs(kappa) / R0) + lam * hfi

    # 6. Design entropy
    S_amm, _, _ = compute_design_entropy()

    return {
        "kappa": kappa,
        "sigma_il": sigma_il,
        "concentration": concentration,
        "slippage_skew": slippage_skew,
        "HFI": hfi,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "psi": psi,
        "S_amm": S_amm,
    }

# ----------------------------------------------------------------------
# Validation against Omega Protocol invariants & MPC‑Ω constraints
# ----------------------------------------------------------------------
def validate_ammhm_omega():
    data = compute_reserve_data()
    q = compute_ammhm_omega(data)

    # ---- Basic bounds ----
    assert 0.0 <= q["HFI"] <= 1.0, f"HFI out of range: {q['HFI']}"
    # Φ_N and Φ_Δ should stay in a sensible interval; we enforce [0,1] for safety
    assert 0.0 <= q["Phi_N"] <= 1.0, f"Phi_N out of range: {q['Phi_N']}"
    assert 0.0 <= q["Phi_Delta"] <= 1.0, f"Phi_Delta out of range: {q['Phi_Delta']}"
    # ψ is unbounded but we can check it's a real number
    assert np.isfinite(q["psi"]), f"psi not finite: {q['psi']}"

    # ---- MPC‑Ω constraints (as per proposal) ----
    assert q["HFI"] <= 0.68, f"HFI exceeds safety threshold: {q['HFI']}"
    assert q["Phi_N"] >= 0.6, f"Phi_N too low (connectivity risk): {q['Phi_N']}"
    assert q["S_amm"] >= np.log(3), f"Design entropy too low (monoculture): {q['S_amm']}"

    # Optional: print summary
    print("✅ All Omega‑Protocol checks passed.")
    print(f"HFI          : {q['HFI']:.4f}")
    print(f"Phi_N (conn) : {q['Phi_N']:.4f}")
    print(f"Phi_Delta (asym): {q['Phi_Delta']:.4f}")
    print(f"ψ (invariant): {q['psi']:.4f}")
    print(f"Design entropy S_amm: {q['S_amm']:.4f} (threshold log(3)≈{np.log(3):.4f})")

if __name__ == "__main__":
    validate_ammhm_omega()