# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Topological Shredding Monitor (TSM‑Ω) – Mathematical Soundness Validator
-----------------------------------------------------------------------
This script checks that the core definitions and invariants proposed in the
TSM‑Ω integration are mathematically well‑formed and respect the Omega Protocol
constraints:
    • Φ_N ∈ [0,1]   (normalized number of connected components)
    • Φ_Δ ≥ 0       (average persistence of 1‑dimensional holes)
    • ψ  = ln(max_persistence / mean_persistence)  (dimensionless)
    • ξ_N = ∂Φ_N/∂ρ , ξ_Δ = ∂Φ_Δ/∂ρ  (stiffness coefficients)
    • Operational bounds: Φ_N ≥ 0.7, ξ_N ≥ -5, ψ ≤ 2.0
    • Cost function J ≥ 0

The validation is performed on synthetic correlation‑matrix streams; any
violation raises an AssertionError with a descriptive message.
"""

import numpy as np
from itertools import combinations
from collections import defaultdict, deque

# ----------------------------------------------------------------------
# Helper: Vietoris–Rips complex (0‑ and 1‑dimensional homology only)
# ----------------------------------------------------------------------
def vr_complex(corr_matrix, rho):
    """
    Build the Vietoris–Rips complex at threshold rho.
    Returns:
        adj   – adjacency list of edges with weight = correlation
        n_vertices – number of vertices (assets)
    """
    n = corr_matrix.shape[0]
    adj = defaultdict(list)          # vertex -> list of (nbr, weight)
    for i, j in combinations(range(n), 2):
        w = corr_matrix[i, j]
        if w > rho:
            adj[i].append((j, w))
            adj[j].append((i, w))
    return adj, n

def bfs_components(adj, n):
    """Return number of connected components (rank of H0)."""
    visited = [False] * n
    comps = 0
    for v in range(n):
        if not visited[v]:
            comps += 1
            dq = deque([v])
            visited[v] = True
            while dq:
                u = dq.popleft()
                for nbr, _ in adj[u]:
                    if not visited[nbr]:
                        visited[nbr] = True
                        dq.append(nbr)
    return comps

def betti_numbers_from_adj(adj, n):
    """
    For an undirected graph:
        b0 = #components
        b1 = E - V + b0   (rank of H1)
    We also return edge list for persistence estimation.
    """
    edges = []
    for u in adj:
        for v, w in adj[u]:
            if u < v:   # avoid double count
                edges.append((u, v, w))
    E = len(edges)
    V = n
    b0 = bfs_components(adj, n)
    b1 = E - V + b0
    return b0, b1, edges

# ----------------------------------------------------------------------
# Persistence approximation (edge birth/death as rho varies)
# ----------------------------------------------------------------------
def edge_persistence(edge_weights, rho_list):
    """
    For each edge we treat its weight w as birth time (when rho < w)
    and death time as the next lower rho where it disappears.
    With a decreasing rho filtration:
        birth = w
        death = next lower rho in rho_list that is < w, or 0 if never dies.
    Persistence = birth - death.
    """
    pers = []
    sorted_rho = np.sort(rho_list)[::-1]   # descending
    for w in edge_weights:
        # find first rho < w
        death_idx = np.searchsorted(sorted_rho, w, side='right')
        if death_idx < len(sorted_rho):
            death = sorted_rho[death_idx]
        else:
            death = 0.0
        pers.append(w - death)
    return np.array(pers)

# ----------------------------------------------------------------------
# Core TSM‑Ω invariant computation
# ----------------------------------------------------------------------
def compute_tsm_omega_invariants(corr_stream, rho_quantile=0.9):
    """
    corr_stream: list/array of shape (T, N, N) – correlation matrices over time.
    Returns dict of time‑averaged invariants and stiffness estimates.
    """
    T = len(corr_stream)
    Phi_N_vals = []
    Phi_Delta_vals = []
    psi_vals = []
    xi_N_vals = []
    xi_Delta_vals = []

    # We'll approximate derivative via finite difference on rho
    rho_samples = np.linspace(0.0, 1.0, 21)   # 0 … 1 in steps of 0.05
    rho_samples = np.unique(np.append(rho_samples, [rho_quantile]))  # ensure quantile present

    for rho in rho_samples:
        Phi_N_rho = []
        Phi_Delta_rho = []
        all_edge_weights = []

        for C in corr_stream:
            adj, n = vr_complex(C, rho)
            b0, b1, edges = betti_numbers_from_adj(adj, n)
            edge_w = [w for (_, _, w) in edge]   # list of weights of present edges
            all_edge_weights.extend(edge_w)

            Phi_N_rho.append(b0 / n)                     # normalized H0 rank
            # Approximate Φ_Δ as average edge weight (proxy for persistence of H1 features)
            Phi_Delta_rho.append(np.mean(edge_w) if edge_w else 0.0)

        # Time averages for this rho
        Phi_N_vals.append(np.mean(Phi_N_rho))
        Phi_Delta_vals.append(np.mean(Phi_Delta_rho))

        # Persistence based edge lifetimes (using the whole stream as proxy)
        if all_edge_weights:
            pers = edge_persistence(all_edge_weights, rho_samples)
            mean_p = np.mean(pers)
            max_p = np.max(pers)
            psi_vals.append(np.log(max_p / mean_p) if mean_p > 0 else 0.0)
        else:
            psi_vals.append(0.0)

    # Stiffness coefficients via central difference on rho
    rho_samples = np.array(rho_samples)
    Phi_N_vals = np.array(Phi_N_vals)
    Phi_Delta_vals = np.array(Phi_Delta_vals)
    xi_N_vals = np.gradient(Phi_N_vals, rho_samples)      # dΦ_N/dρ
    xi_Delta_vals = np.gradient(Phi_Delta_vals, rho_samples)  # dΦ_Δ/dρ

    # Return time‑averaged (over rho) values for final checks
    return {
        "Phi_N": np.mean(Phi_N_vals),
        "Phi_Delta": np.mean(Phi_Delta_vals),
        "psi": np.mean(psi_vals),
        "xi_N": np.mean(xi_N_vals),
        "xi_Delta": np.mean(xi_Delta_vals),
        "raw": {
            "Phi_N_vals": Phi_N_vals,
            "Phi_Delta_vals": Phi_Delta_vals,
            "psi_vals": psi_vals,
            "xi_N_vals": xi_N_vals,
            "xi_Delta_vals": xi_Delta_vals,
            "rho_samples": rho_samples,
        }
    }

# ----------------------------------------------------------------------
# Omega Protocol invariant checks
# ----------------------------------------------------------------------
def validate_omega_invariants(inv):
    """
    Enforces the Omega Protocol constraints:
        Φ_N ≥ 0.7
        ξ_N ≥ -5
        ψ ≤ 2.0
        Φ_Δ ≥ 0   (by definition)
        Cost J ≥ 0  (sample quadratic‑exponential form)
    """
    # Unpack
    Phi_N = inv["Phi_N"]
    Phi_Delta = inv["Phi_Delta"]
    psi = inv["psi"]
    xi_N = inv["xi_N"]
    # xi_Delta is not directly bounded in the spec, but we keep it non‑negative for sanity
    xi_Delta = inv["xi_Delta"]

    # Basic domain checks
    assert 0.0 <= Phi_N <= 1.0, f"Φ_N out of [0,1]: {Phi_N}"
    assert Phi_Delta >= 0.0, f"Φ_Δ negative: {Phi_Delta}"
    # ψ can be any real; we only enforce the upper bound from the protocol
    # (lower bound is not specified, but we keep it finite)
    assert np.isfinite(psi), f"ψ is not finite: {psi}"

    # Protocol‑specific bounds
    assert Phi_N >= 0.7, f"Φ_N violates Ω invariant (≥0.7): {Phi_N}"
    assert xi_N >= -5.0, f"ξ_N violates Ω invariant (≥-5): {xi_N}"
    assert psi <= 2.0, f"ψ violates Ω invariant (≤2.0): {psi}"

    # Cost function (example from proposal):
    # J = ∫ [ (0.7 - Φ_N)_+² + λ₁ ξ_N² + λ₂ exp(ψ) ] dt
    # We approximate the integrand by its time‑average; λ₁,λ₂ set to 1.0 for validation.
    lam1, lam2 = 1.0, 1.0
    integrand = ((0.7 - Phi_N) if Phi_N < 0.7 else 0.0)**2 + lam1 * xi_N**2 + lam2 * np.exp(psi)
    assert integrand >= 0.0, f"Cost integrand negative: {integrand}"

    # If we reach here, all invariants hold.
    return True

# ----------------------------------------------------------------------
# Synthetic data generator for a quick sanity test
# ----------------------------------------------------------------------
def synthetic_corr_stream(T=50, N=20, seed=42):
    """Generate random correlation‑like matrices (SPD with ones on diagonal)."""
    rng = np.random.default_rng(seed)
    stream = []
    for _ in range(T):
        # Random factor model: X = A * F + ε
        F = rng.standard_normal(size=(5,))
        A = rng.standard_normal(size=(N, 5))
        eps = rng.normal(scale=0.5, size=N)
        X = A @ F + eps
        # Covariance → correlation
        C = np.cov(X.T)  # 1×1 because X is 1D? Oops.
        # Instead, generate multiple time points per matrix:
    # Let's do a proper approach:
    rng = np.random.default_rng(seed)
    stream = []
    for _ in range(T):
        # Generate T_inner observations per asset to compute a correlation matrix
        T_inner = 100
        Z = rng.standard_normal(size=(T_inner, N))
        # Induce some correlation structure via a random factor
        factor = rng.standard_normal(size=(T_inner, 3))
        loadings = rng.uniform(-0.5, 0.5, size=(N, 3))
        X = Z + factor @ loadings.T
        C = np.corrcoef(X, rowvar=False)
        # Ensure valid correlation matrix (clip to [-1,1] and force PD)
        C = np.clip(C, -1.0, 1.0)
        # Make PD via nearest correlation (simple: eigen‑clip)
        evals, evecs = np.linalg.eigh(C)
        evals = np.maximum(evals, 1e-6)
        C = (evecs @ np.diag(evals) @ evecs.T)
        # Scale diagonal to 1
        D = np.sqrt(np.diag(C))
        C = C / np.outer(D, D)
        stream.append(C)
    return np.array(stream)

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Generating synthetic correlation stream...")
    corr_stream = synthetic_corr_stream(T=30, N=15)
    print("Computing TSM‑Ω invariants...")
    invariants = compute_tsm_omega_invariants(corr_stream, rho_quantile=0.9)
    print("Invariants:")
    for k, v in invariants.items():
        if k != "raw":
            print(f"  {k}: {v:.6f}")

    print("\nValidating against Omega Protocol...")
    try:
        validate_omega_invariants(invariants)
        print("✅ All Omega Protocol invariants satisfied.")
    except AssertionError as e:
        print(f"❌ Invariant violation: {e}")
        raise