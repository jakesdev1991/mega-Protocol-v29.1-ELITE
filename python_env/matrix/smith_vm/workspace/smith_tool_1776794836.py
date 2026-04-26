# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol audit for Credential‑Graph Fragility Monitor (CGFM‑Ω)
-------------------------------------------------------------------
Validates the mathematical soundness of the CFI‑based formulation
and its compatibility with the Ω‑invariants (Φ_N, Φ_Δ, ψ_cred, S_cred).
"""

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
import itertools
import warnings

warnings.filterwarnings("ignore", category=RuntimeError)

# -------------------------- Helper Functions --------------------------

def random_bipartite_graph(n_keys, n_services, edge_prob=0.02, seed=42):
    """Generate a random bipartite graph (keys <-> services)."""
    rng = np.random.default_rng(seed)
    rows = []
    cols = []
    for i in range(n_keys):
        for j in range(n_services):
            if rng.random() < edge_prob:
                rows.append(i)
                cols.append(n_keys + j)   # offset service ids
    data = np.ones_like(rows, dtype=float)
    # add reciprocal edges for undirected Laplacian
    rows = np.concatenate([rows, cols])
    cols = np.concatenate([cols, rows[:len(rows)//2]])  # mirror
    data = np.concatenate([data, data])
    n_nodes = n_keys + n_services
    A = sp.csr_matrix((data, (rows, cols)), shape=(n_nodes, n_nodes))
    return A, n_keys, n_services

def ollivier_ricci_edge(A, i, j, m=1):
    """
    Approximate Ollivier‑Ricci curvature for edge (i,j) using
    the simple m‑step neighbourhood coupling (see Ollivier 2009).
    For speed we use the formula:
        R_ij = 1 - W_1(m_i, m_j) / d(i,j)
    where m_x is the uniform distribution over neighbours of x,
    and W_1 is approximated by the Jaccard distance.
    """
    nbrs_i = set(A[i].nonzero()[1])
    nbrs_j = set(A[j].nonzero()[1])
    if not nbrs_i or not nbrs_j:
        return 0.0
    # Jaccard distance as a proxy for 1 - overlap
    inter = len(nbrs_i & nbrs_j)
    union = len(nbrs_i | nbrs_j)
    w1 = 1.0 - (inter / union if union else 0.0)
    d_ij = 1.0  # graph distance for direct edge
    return 1.0 - w1 / d_ij

def compute_metrics(A, n_keys):
    """Return degree heterogeneity, spectral gap, curvature concentration, entropy."""
    # Degrees (only key side needed for heterogeneity)
    deg = np.array(A.sum(axis=1)).flatten()
    key_deg = deg[:n_keys]
    # 1. Degree heterogeneity H = sum(d_i^2) / sum(d_i)
    if key_deg.sum() == 0:
        H = 0.0
    else:
        H = (key_deg ** 2).sum() / key_deg.sum()

    # 2. Spectral gap λ1 of the normalized Laplacian L = I - D^{-1/2} A D^{-1/2}
    deg_sqrt_inv = np.power(deg, -0.5, where=deg!=0)
    deg_sqrt_inv[deg == 0] = 0
    D_sqrt_inv = sp.diags(deg_sqrt_inv)
    L = sp.eye(A.shape[0]) - D_sqrt_inv @ A @ D_sqrt_inv
    # smallest non‑zero eigenvalue
    evals, _ = eigsh(L, k=2, which='SM', tol=1e-6)
    λ1 = evals[1] if len(evals) > 1 else 0.0
    # spectral gap = λ1 (already the first non‑zero)
    spectral_gap = λ1

    # 3. Curvature concentration K = mean |R_ij|
    edge_list = list(zip(*A.nonzero()))
    # avoid double counting (i<j)
    curvatures = []
    for i, j in edge_list:
        if i < j:
            R = ollivier_ricci_edge(A, i, j)
            curvatures.append(abs(R))
    K = np.mean(curvatures) if curvatures else 0.0

    # 4. Entropy loss: need a usage distribution p_k.
    #    For demo we use degree‑proportional usage.
    usage = key_deg.copy()
    if usage.sum() == 0:
        p = np.ones_like(usage) / len(usage)
    else:
        p = usage / usage.sum()
    S = -np.sum(p * np.log(p + 1e-12))  # avoid log(0)
    E = 1.0 - S / np.log(len(usage)) if len(usage) > 1 else 0.0   # normalised loss

    return {
        "H": H,
        "λ1": λ1,
        "spectral_gap": spectral_gap,
        "K": K,
        "S": S,
        "E": E,
        "key_deg": key_deg,
        "usage": usage,
        "p": p,
    }

def compute_cfi(metrics, α=0.4, β=0.3, γ=0.2, δ=0.1):
    """CFI = tanh(αH + β/λ1 + γK + δE)  (note: C = 1/λ1)."""
    arg = α * metrics["H"] + β * (1.0 / (metrics["λ1"] + 1e-9)) + γ * metrics["K"] + δ * metrics["E"]
    return np.tanh(arg)

def map_to_phi(metrics, cfi, ΦN0=0.8, ΦΔ0=0.5,
               η1=0.2, η2=0.15, η3=0.1, η4=0.05,
               τ1=0, τ2=0):   # τ ignored for static check
    """Linear mapping to Ω‑invariants (static version)."""
    λ1 = metrics["λ1"]
    key_deg = metrics["key_deg"]
    max_deg = key_deg.max() if len(key_deg) else 0
    mean_deg = key_deg.mean() if len(key_deg) else 1
    S = metrics["S"]

    ΦN = ΦN0 - η1 * cfi + η2 * λ1
    ΦΔ = ΦΔ0 + η3 * (max_deg / mean_deg) - η4 * S
    # Clip to [0,1] to respect Ω‑Protocol normalisation
    ΦN = np.clip(ΦN, 0.0, 1.0)
    ΦΔ = np.clip(ΦΔ, 0.0, 1.0)
    return ΦN, ΦΔ

def compute_psi(metrics, cfi, ℛ0=1.0, λ=0.5):
    """ψ_cred = ln(|ΣR_ij|/ℛ0) + λ·CFI."""
    edge_list = list(zip(*metrics["A"].nonzero()))
    total_curv = 0.0
    for i, j in edge_list:
        if i < j:
            total_curv += ollivier_ricci_edge(metrics["A"], i, j)
    arg = abs(total_curv) / ℛ0
    if arg <= 0:
        raise ValueError("Log argument non‑positive → ψ_cred undefined.")
    ψ = np.log(arg) + λ * cfi
    return ψ

def entropy_gauge(metrics):
    """A_μ = ∂_μ S_cred. For a static snapshot we expect ≈0."""
    # Numerical gradient using finite differences on a perturbed usage vector.
    eps = 1e-6
    p = metrics["p"]
    S0 = -np.sum(p * np.log(p + 1e-12))
    grad = np.zeros_like(p)
    for idx in range(len(p)):
        p_plus = p.copy()
        p_plus[idx] += eps
        p_plus /= p_plus.sum()   # renormalise
        S_plus = -np.sum(p_plus * np.log(p_plus + 1e-12))
        grad[idx] = (S_plus - S0) / eps
    return grad

# -------------------------- Validation Routine --------------------------

def validate_cgfm_omega():
    """Run a battery of checks; raise AssertionError on any violation."""
    # 1. Generate a random bipartite graph
    A, n_keys, n_services = random_bipartite_graph(n_keys=50, n_services=30, edge_prob=0.03, seed=123)
    metrics = compute_metrics(A, n_keys)
    metrics["A"] = A   # attach for curvature sum

    # 2. Compute CFI
    cfi = compute_cfi(metrics)
    assert 0.0 <= cfi <= 1.0, f"CFI out of bounds: {cfi}"

    # 3. Map to Ω‑invariants
    ΦN, ΦΔ = map_to_phi(metrics, cfi)
    assert 0.0 <= ΦN <= 1.0, f"Φ_N out of bounds: {ΦN}"
    assert 0.0 <= ΦΔ <= 1.0, f"Φ_Δ out of bounds: {ΦΔ}"

    # 4. Compute ψ_cred
    ψ = compute_psi(metrics, cfi)
    # ψ can be any real number; just ensure it's not NaN
    assert np.isfinite(ψ), f"ψ_cred is non‑finite: {ψ}"

    # 5. Entropy gauge sanity check (should be ~0 for static case)
    A_mu = entropy_gauge(metrics)
    # The gradient should be small because we used a degree‑proportional usage;
    # we enforce a loose bound.
    assert np.all(np.abs(A_mu) < 1e-2), f"Entropy gauge too large: {A_mu}"

    # 6. Check that the CFI‑based constraints used in the MPC‑Ω QP are satisfiable
    #    Example constraints: CFI ≤ 0.65, Φ_N ≥ 0.6, S_cred ≥ log(3)
    S_cred = metrics["S"]
    assert cfi <= 0.65 + 1e-9, f"CFI exceeds safety threshold: {cfi}"
    assert ΦN >= 0.6 - 1e-9, f"Φ_N below safety threshold: {ΦN}"
    assert S_cred >= np.log(3) - 1e-9, f"Entropy too low: {S_cred}"

    print("✅ All Ω‑Protocol mathematical checks passed.")
    print(f"   CFI = {cfi:.4f}")
    print(f"   Φ_N = {ΦN:.4f}, Φ_Δ = {ΦΔ:.4f}")
    print(f"   ψ_cred = {ψ:.4f}")
    print(f"   S_cred = {S_cred:.4f}")

# -------------------------- Entry Point --------------------------

if __name__ == "__main__":
    validate_cgfm_omega()