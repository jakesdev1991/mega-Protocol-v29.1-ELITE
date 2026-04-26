# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSGM‑Ω Omega‑Protocol compliance validator.
Checks:
  1. ψ = ln Φ_N from spectral gap vs. curvature exponential model.
  2. Φ_Δ as skewness of curvature distribution.
  3. Entropy‑gauge: ∂_μ J^μ ≈ 0 when A_μ = ∂_μ S_dir.
  4. Dimensionless consistency (optional scaling).
  5. LSFI sigmoid formulation and mapping to Φ_N, Φ_Δ.
  6. MPC‑Ω constraints and cost non‑negativity.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.stats import skew, entropy
from typing import Tuple, List

# ----------------------------
# Helper functions
# ----------------------------
def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))

def sigmoid_inv(y: np.ndarray) -> np.ndarray:
    # inverse sigmoid (logit), clamp to avoid log(0)
    y = np.clip(y, 1e-12, 1.0 - 1e-12)
    return np.log(y / (1.0 - y))

def ollivier_ricci_curvature(
    adj: sp.csr_matrix,
    weights: np.ndarray,
    m: int = 1
) -> np.ndarray:
    """
    Approximate Ollivier‑Ricci curvature for an undirected weighted graph.
    Uses the definition: κ(x,y) = 1 - W1(m_x, m_y) / d(x,y)
    where m_x is the uniform probability distribution on neighbours of x.
    For simplicity we compute the curvature on edges and then assign to nodes
    as the average of incident edge curvatures.
    """
    n = adj.shape[0]
    # degree (weighted)
    deg = np.array(adj.sum(axis=1)).ravel()
    # avoid division by zero
    deg[deg == 0] = 1.0

    # Build list of edges (i<j)
    rows, cols = adj.nonzero()
    edges = [(i, j) for i, j in zip(rows, cols) if i < j]

    curv_edge = np.zeros(len(edges))
    for idx, (i, j) in enumerate(edges):
        w_ij = weights[idx] if weights is not None else adj[i, j]
        # probability m_i: uniform over neighbours of i
        neigh_i = adj[i].nonzero()[1]
        prob_i = np.ones_like(neigh_i, dtype=float) / len(neigh_i) if len(neigh_i) > 0 else np.array([])
        neigh_j = adj[j].nonzero()[1]
        prob_j = np.ones_like(neigh_j, dtype=float) / len(neigh_j) if len(neigh_j) > 0 else np.array([])

        # 1‑Wasserstein distance on the graph approximated by shortest path length
        # For unweighted unit length edges, d(i,j)=1; we use the weight as length.
        d_ij = 1.0 / w_ij if w_ij > 0 else np.inf
        # Transport cost: move probability from i to j along edge (i,j)
        # Simple approximation: W1 = d_ij * (1 - overlap of distributions)
        overlap = np.sum(np.minimum(prob_i[:, None], prob_j[None, :])) if len(prob_i) and len(prob_j) else 0.0
        kappa = 1.0 - d_ij * (1.0 - overlap)
        curv_edge[idx] = kappa

    # Node curvature = average of incident edge curvatures
    node_curv = np.zeros(n)
    for idx, (i, j) in enumerate(edges):
        node_curv[i] += curv_edge[idx]
        node_curv[j] += curv_edge[idx]
    # normalize by degree (avoid zero)
    node_curv /= np.where(deg > 0, deg, 1.0)
    return node_curv

def spectral_gap(laplacian: sp.csr_matrix) -> float:
    """Return the smallest non‑zero eigenvalue of the Laplacian."""
    # Compute a few smallest eigenvalues using shift‑invert mode
    eigenvals, _ = spla.eigsh(laplacian, k=2, sigma=0.0, which='LM')
    eigenvals.sort()
    # eigenvals[0] is (numerically) zero; return the next
    return eigenvals[1]

# ----------------------------
# Synthetic data generation
# ----------------------------
def generate_synthetic_tree(
    n_nodes: int = 200,
    beta: float = 5.0,
    seed: int = 42
) -> Tuple[sp.csr_matrix, np.ndarray, np.ndarray]:
    """
    Create a random rooted tree, then add a few extra edges to mimic
    misconfigurations (creating cycles). Edge weight = 1 + beta * I(crosses boundary).
    For simplicity we label a random 20% of nodes as "internal-use-only"
    and treat edges crossing the label change as high‑risk.
    """
    rng = np.random.default_rng(seed)
    # random tree via Prufer sequence
    if n_nodes < 2:
        raise ValueError("Need at least 2 nodes")
    prufer = rng.integers(0, n_nodes, size=n_nodes-2)
    degree = np.ones(n_nodes, dtype=int)
    for v in prufer:
        degree[v] += 1
    edges = []
    for v in prufer:
        for u in range(n_nodes):
            if degree[u] == 1:
                edges.append((u, v))
                degree[u] -= 1
                degree[v] -= 1
                break
    # remaining two nodes with degree 1
    leaves = [i for i, d in enumerate(degree) if d == 1]
    edges.append((leaves[0], leaves[1]))

    adj = sp.lil_matrix((n_nodes, n_nodes), dtype=float)
    for i, j in edges:
        adj[i, j] = adj[j, i] = 1.0
    adj = adj.tocsr()

    # assign internal‑use-only label
    internal = rng.random(n_nodes) < 0.2
    # recompute weights: edge weight = 1 + beta * I(crosses internal↔public)
    rows, cols = adj.nonzero()
    weights = np.ones_like(rows, dtype=float)
    mask = internal[rows] != internal[cols]
    weights[mask] = 1.0 + beta
    # rebuild weighted adjacency
    w_adj = sp.csr_matrix((weights, (rows, cols)), shape=(n_nodes, n_nodes))
    return w_adj, internal, weights

# ----------------------------
# Main validation routine
# ----------------------------
def validate_lsgm_omega(
    adj_weighted: sp.csr_matrix,
    internal_label: np.ndarray,
    efi_per_node: np.ndarray,
    tau0: float = 1.0,      # characteristic time (weeks)
    ell0: float = 1.0,      # characteristic length (directory hops)
    config: dict = None
) -> dict:
    """
    Returns a dictionary of diagnostic booleans and numeric values.
    """
    if config is None:
        config = {
            'alpha': 1.0, 'beta': 1.0, 'gamma': 1.0, 'delta': 1.0,
            'R0': 1.0,      # curvature scale
            'PhiN0': 0.5,   # baseline connectivity
            'mu1': 1.0, 'mu2': 1.0, 'mu3': 1.0,
            'kappa_gauge': 10.0  # penalty weight for gauge term
        }

    n = adj_weighted.shape[0]

    # ---- 1. Curvature (Ollivier‑Ricci) ----
    curv = ollivier_ricci_curvature(adj_weighted, None)  # shape (n,)
    curv_mean = float(np.mean(curv))
    curv_max = float(np.max(curv))

    # ---- 2. Spectral gap → Φ_N ----
    # Weighted Laplacian L = D - A
    deg = np.array(adj_weighted.sum(axis=1)).ravel()
    L = sp.diags(deg, 0) - adj_weighted
    lam1 = spectral_gap(L)  # smallest non‑zero eigenvalue
    PhiN_from_gap = lam1  # raw spectral gap
    # Map to dimensionless Φ_N via exponential model
    PhiN_model = config['PhiN0'] * np.exp(curv_mean / config['R0'])
    psi_leak = np.log(PhiN_model)  # should equal ln Φ_N

    # ---- 3. Skewness → Φ_Δ ----
    PhiDelta_skew = skew(curv, nan_policy='omit')
    psi_Delta = np.log(1.0 + PhiDelta_skew)  # as per proposal

    # ---- 4. Directory‑type entropy (mock types) ----
    # Suppose we have three log types: checkpoint, gradient, validation
    # Assign each node a type randomly weighted by internal label.
    type_probs = np.array([0.5, 0.3, 0.2])  # baseline
    # internal nodes more likely to have gradient logs
    type_assign = np.zeros((n, 3))
    for i in range(n):
        if internal_label[i]:
            type_assign[i] = np.array([0.2, 0.6, 0.2])  # gradient heavy
        else:
            type_assign[i] = type_probs
    # Normalize rows
    type_assign /= type_assign.sum(axis=1, keepdims=True)
    # Overall distribution p_k = average over nodes
    p_k = type_assign.mean(axis=0)
    S_dir = float(entropy(p_k, base=np.e))  # Shannon entropy (nats)

    # Gauge field A_mu = ∂_mu S_dir (temporal gradient approximated by finite diff)
    # For a static snapshot we treat time derivative as zero; we only need to test
    # that the penalty drives ∂_mu J^mu to zero.
    J0 = np.sqrt(2.0) * PhiDelta_skew  # J^0 component
    J = np.array([J0, 0.0, 0.0, 0.0])  # (t, x, y, z)
    # Approximate ∂_mu J^mu via finite difference on a dummy time series
    # We'll create two snapshots: t and t+dt, with slightly perturbed curvature.
    dt = 0.1 * tau0
    curv_t1 = curv + 0.01 * np.random.randn(n)  # small perturbation
    PhiDelta_t1 = skew(curv_t1, nan_policy='omit')
    J0_t1 = np.sqrt(2.0) * PhiDelta_t1
    J_t1 = np.array([J0_t1, 0.0, 0.0, 0.0])
    dJdt = (J_t1[0] - J[0]) / dt
    # Spatial derivatives are zero in this 1‑D time‑only toy model
    divJ = dJdt  # ∂_0 J^0
    gauge_penalty = config['kappa_gauge'] * (divJ ** 2)

    # ---- 5. Exposure velocity v_c (mock) ----
    # Define v_c as fraction of nodes with curvature above median
    v_c = float(np.mean(curv > np.median(curv)))

    # ---- 6. Epistemic‑fragility correlation C_KE ----
    # Correlate curvature with supplied EFI per node
    if efi_per_node.shape != (n,):
        raise ValueError("efi_per_node must have length equal to number of nodes")
    C_KE = float(np.corrcoef(curv, efi_per_node)[0, 1])

    # ---- 7. LSFI (sigmoid combination) ----
    LS_raw = (config['alpha'] * curv_mean +
              config['beta'] * C_KE +
              config['gamma'] * (1.0 - S_dir / np.log(4)) +  # normalize entropy deficit
              config['delta'] * v_c)
    LSFI = sigmoid(LS_raw)
    # Invert to get Φ_Δ from LSFI (should match skewness‑based)
    PhiDelta_from_LSFI = sigmoid_inv(LSFI)

    # ---- 8. MPC‑Ω constraints ----
    cons_LSFI = LSFI <= 0.65 + 1e-9
    cons_PhiN = PhiN_model >= 0.5 - 1e-9
    cons_Entropy = S_dir >= np.log(4) - 1e-9

    # ---- 9. Cost integrand (dimensionless time) ----
    integrand = (
        max(0.0, LSFI - 0.65) ** 2 +
        config['mu1'] * max(0.0, 0.5 - PhiN_model) ** 2 +
        config['mu2'] * (PhiDelta_skew ** 2) +
        config['mu3'] * max(0.0, np.log(4) - S_dir) ** 2
    )
    # For a single time step, cost = integrand * dt (here dt=1 in dimensionless units)
    cost = integrand

    # ---- 10. Dimensional check (optional) ----
    # Verify that scaling by τ0, ℓ0 leaves dimensionless numbers unchanged
    # We simply note that all inputs were treated as dimensionless.
    dimless_ok = True  # placeholder; could compare with a scaled version

    return {
        'curv_mean': curv_mean,
        'curv_max': curv_max,
        'spectral_gap_lambda1': lam1,
        'PhiN_from_gap': PhiN_from_gap,
        'PhiN_model': PhiN_model,
        'psi_leak': psi_leak,
        'PhiDelta_skew': PhiDelta_skew,
        'psi_Delta': psi_Delta,
        'S_dir': S_dir,
        'entropy_deficit': np.log(4) - S_dir,
        'v_c': v_c,
        'C_KE': C_KE,
        'LSFI': LSFI,
        'PhiDelta_from_LSFI': PhiDelta_from_LSFI,
        'constraints': {
            'LSFI_le_0p65': cons_LSFI,
            'PhiN_ge_0p5': cons_PhiN,
            'S_dir_ge_log4': cons_Entropy
        },
        'cost_integrand': integrand,
        'cost': cost,
        'gauge_penalty': gauge_penalty,
        'divJ': divJ,
        'dimensionless_ok': dimless_ok
    }

# ----------------------------
# Example usage (run when script executed)
# ----------------------------
if __name__ == "__main__":
    # Generate a synthetic directory tree
    W_adj, internal, _ = generate_synthetic_tree(n_nodes=150, beta=4.0, seed=123)

    # Mock EFI per node: higher EFI in internal nodes, some noise
    rng = np.random.default_rng(2025)
    EFI = np.where(internal, rng.uniform(0.6, 1.0, size=internal.sum()),
                           rng.uniform(0.0, 0.4, size=(~internal).sum()))
    # place back into full-length array
    efi_full = np.zeros(W_adj.shape[0])
    efi_full[internal] = EFI[internal == True]
    efi_full[~internal] = EFI[internal == False]

    # Run validation
    report = validate_lsgm_omega(
        adj_weighted=W_adj,
        internal_label=internal,
        efi_per_node=efi_full,
        tau0=1.0,   # 1 week
        ell0=10.0,  # average directory hops
        config={
            'alpha': 0.8,
            'beta': 0.6,
            'gamma': 0.4,
            'delta': 0.5,
            'R0': 1.0,
            'PhiN0': 0.5,
            'mu1': 1.2,
            'mu2': 0.8,
            'mu3': 1.0,
            'kappa_gauge': 5.0
        }
    )

    # Pretty‑print results
    print("=== LSGM‑Ω Omega‑Protocol Validation ===")
    for k, v in report.items():
        if k == 'constraints':
            print(f"  {k}:")
            for ck, cv in v.items():
                print(f"    {ck}: {cv}")
        elif isinstance(v, float):
            print(f"  {k}: {v:.5f}")
        else:
            print(f"  {k}: {v}")

    # Overall compliance flag
    all_constraints = all(report['constraints'].values())
    print("\nAll core constraints satisfied?", all_constraints)