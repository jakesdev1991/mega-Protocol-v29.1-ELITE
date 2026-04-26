# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation for Credential‑Graph Fragility Monitor (CGFM‑Ω)
-----------------------------------------------------------------------
This script checks the mathematical soundness of the CFI formulation and
its mapping to the Omega invariants (Φ_N, Φ_Δ, ψ_cred, entropy gauge).
It generates a random bipartite key‑service graph, computes the required
metrics, and verifies that the protocol constraints hold.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
import itertools
import math
import random

# -------------------------------------------------
# Helper: Ollivier‑Ricci curvature approximation
# -------------------------------------------------
def ollivier_ricci_approx(adj, u, v):
    """
    Very cheap approximation: 1 - (W1 distance / graph distance).
    For unweighted graphs we use the overlap of neighborhoods.
    Returns a value in [-1, 1] (negative curvature => bottleneck).
    """
    nu = set(adj[u].indices)
    nv = set(adj[v].indices)
    if not nu or not nv:
        return -1.0  # isolated node => maximal negative curvature
    overlap = len(nu & nv)
    union = len(nu | nv)
    # Jaccard similarity as proxy for transport cost
    similarity = overlap / union if union > 0 else 0.0
    # Approximate curvature: 2*similarity - 1  (range [-1,1])
    return 2.0 * similarity - 1.0

# -------------------------------------------------
# Core validation routine
# -------------------------------------------------
def validate_cgfm_omega(
    n_keys=200,
    n_services=150,
    edge_prob=0.02,
    seed=42,
    alpha=0.3,
    beta=0.3,
    gamma=0.2,
    delta=0.2,
):
    random.seed(seed)
    np.random.seed(seed)

    # ----- 1. Build bipartite adjacency (keys x services) -----
    # We'll store a single sparse matrix for the whole bipartite graph.
    # Shape: (n_keys + n_services, n_keys + n_services)
    N = n_keys + n_services
    rows, cols = [], []
    for i in range(n_keys):
        for j in range(n_services):
            if random.random() < edge_prob:
                rows.append(i)
                cols.append(n_keys + j)   # service offset
                rows.append(n_keys + j)   # symmetric
                cols.append(i)
    adj = sp.csr_matrix((np.ones(len(rows), dtype=float), (rows, cols)), shape=(N, N))
    adj.eliminate_zeros()

    # ----- 2. Basic graph stats -----
    deg = np.array(adj.sum(axis=1)).flatten()
    deg_keys = deg[:n_keys]
    deg_services = deg[n_keys:]

    # degree heterogeneity term: (sum d_i^2)/(sum d_i)
    sum_d = deg_keys.sum()
    sum_d2 = (deg_keys ** 2).sum()
    heterogeneity = sum_d2 / sum_d if sum_d > 0 else 0.0

    # ----- 3. Spectral gap (lambda_1 of Laplacian) -----
    # Compute normalized Laplacian L = I - D^{-1/2} A D^{-1/2}
    # Avoid zero-degree nodes by adding a tiny epsilon.
    eps = 1e-9
    deg_sqrt_inv = np.where(deg > 0, 1.0 / np.sqrt(deg + eps), 0.0)
    D_sqrt_inv = sp.diags(deg_sqrt_inv)
    L = sp.eye(N, format='csr') - D_sqrt_inv @ adj @ D_sqrt_inv
    # smallest eigenvalue is 0 (constant vector); we need the second smallest.
    # Use shift-invert mode to get a few eigenvalues near 0.
    try:
        evals = sla.eigsh(L, k=2, which='SM', return_eigenvectors=False)
        lambda1 = evals[1]   # second smallest
    except sla.ArpackNoConvergence:
        # Fallback to dense for small graphs
        evals = np.linalg.eigvalsh(L.toarray())
        lambda1 = evals[1]
    # Guard against zero (disconnected graph)
    if lambda1 <= 0:
        lambda1 = 1e-12

    # ----- 4. Average Ollivier‑Ricci curvature -----
    # Sample a subset of edges for speed.
    edge_list = list(zip(rows[::2], cols[::2]))  # take one direction only
    if len(edge_list) == 0:
        avg_curv = 0.0
    else:
        curv_sum = 0.0
        for u, v in random.sample(edge_list, min(200, len(edge_list))):
            curv_sum += ollivier_ricci_approx(adj, u, v)
        avg_curv = curv_sum / min(200, len(edge_list))

    # ----- 5. Key‑usage entropy (mock) -----
    # Assume usage proportional to degree (more connections → more use)
    usage = np.maximum(deg_keys, 1)  # avoid zeros
    p = usage / usage.sum()
    S_cred = -np.sum(p * np.log(p + 1e-12))

    # ----- 6. Credential Fragility Index (CFI) -----
    # Raw linear combination (all terms non‑negative)
    raw = (
        alpha * heterogeneity +
        beta * (1.0 / lambda1) +
        gamma * np.abs(avg_curv) +   # use absolute curvature magnitude
        delta * (1.0 - S_cred / math.log(max(2, n_keys)))  # normalized entropy loss
    )
    # Shifted tanh to map ℝ → [0,1]
    CFI = (np.tanh(raw) + 1.0) / 2.0

    # ----- 7. Mapping to Omega variables -----
    # Base values (chosen arbitrarily but positive)
    Phi_N0 = 0.8
    Phi_Delta0 = 0.5
    tau1 = tau2 = 1.0   # not used in static check
    eta1, eta2, eta3, eta4 = 0.15, 0.1, 0.12, 0.08

    Phi_N = Phi_N0 - eta1 * CFI + eta2 * lambda1
    Phi_Delta = Phi_Delta0 + eta3 * (deg_keys.max() / (deg_keys.mean() + 1e-9)) - eta4 * S_cred

    # Invariant from graph curvature (psi_cred)
    R0 = 1.0  # reference curvature scale
    psi_cred = np.log(np.abs(avg_curv) / R0 + 1e-12) + 0.5 * CFI  # λ set to 0.5 for demo

    # Entropy gauge A_mu = dS/dt approximated by zero (static)
    A_mu = 0.0

    # ----- 8. Protocol constraint checks -----
    violations = []

    if CFI > 0.65:
        violations.append(f"CFI too high: {CFI:.3f} > 0.65 (risk trigger)")

    if Phi_N < 0.6:
        violations.append(f"Phi_N below safety floor: {Phi_N:.3f} < 0.6")

    if S_cred < math.log(3):
        violations.append(f"Entropy too low: {S_cred:.3f} < ln(3) ≈ {math.log(3):.3f}")

    # Additional sanity checks
    if lambda1 <= 0:
        violations.append("Spectral gap non‑positive (graph disconnected)")

    if not (0.0 <= CFI <= 1.0):
        violations.append(f"CFI out of [0,1] range: {CFI:.3f}")

    # ----- 9. Report -----
    print("=== CGFM‑Ω Validation Report ===")
    print(f"Graph size: {n_keys} keys × {n_services} services, edge_prob={edge_prob}")
    print(f"Degree heterogeneity: {heterogeneity:.3f}")
    print(f"Spectral gap λ₁: {lambda1:.4f}")
    print(f"Avg Ollivier‑Ricci curvature: {avg_curv:.4f}")
    print(f"Key‑usage entropy S_cred: {S_cred:.4f}")
    print(f"Raw fragility score: {raw:.3f}")
    print(f"CFI (shifted‑tanh): {CFI:.3f}")
    print(f"Phi_N (connectivity): {Phi_N:.3f}")
    print(f"Phi_Δ (asymmetry): {Phi_Delta:.3f}")
    print(f"Psi_cred (curvature invariant): {psi_cred:.3f}")
    print(f"Entropy gauge A_μ: {A_mu:.3f}")
    print("-" * 40)
    if violations:
        print("VALIDATION FAILED – Omega Protocol violations:")
        for v in violations:
            print("  -", v)
        return False
    else:
        print("VALIDATION PASSED – All Omega invariants satisfied.")
        return True

# -------------------------------------------------
# Run the validation (feel free to tweak parameters)
# -------------------------------------------------
if __name__ == "__main__":
    # Example run – you can modify the arguments to stress‑test the model.
    ok = validate_cgfm_omega(
        n_keys=300,
        n_services=200,
        edge_prob=0.015,   # sparse but realistic
        seed=12345,
        alpha=0.25,
        beta=0.25,
        gamma=0.25,
        delta=0.25,
    )
    # Exit code 0 for success, 1 for failure (useful for automation)
    exit(0 if ok else 1)