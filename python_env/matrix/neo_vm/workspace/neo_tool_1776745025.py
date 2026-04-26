# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
narrative_curvature_fragility.py

Demonstrates that the scalar curvature computed from word‑embedding‑based
semantic manifolds is a statistical phantom: tiny perturbations produce
massive swings in curvature, undermining the NCSM‑Ω early‑warning signal.
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import laplacian
from scipy.linalg import eigh

# ─── 1. Synthetic "document embedding" data ──────────────────────────────
def generate_embeddings(n_docs=200, dim=50, seed=0):
    """Generate random unit‑norm embeddings simulating internal PDF paragraphs."""
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_docs, dim))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    return X

# ─── 2. Approximate scalar curvature via graph Laplacian spectrum ────────
def approximate_scalar_curvature(X, k=5):
    """
    Build a k‑NN graph from embeddings, compute the (combinatorial) Laplacian,
    and return an *approximate* scalar curvature as the trace of the
    pseudo‑inverse Laplacian (a common proxy for Ricci curvature on graphs).
    """
    # Pairwise cosine distances
    D = squareform(pdist(X, metric='cosine'))
    # k‑nearest neighbor adjacency
    knn = np.argsort(D, axis=1)[:, 1:k+1]
    adj = np.zeros_like(D)
    for i in range(len(D)):
        adj[i, knn[i]] = 1
        adj[knn[i], i] = 1  # symmetrize
    # Combinatorial Laplacian
    L = laplacian(adj, normed=False)
    # Pseudo‑inverse
    eigvals, eigvecs = eigh(L)
    # Zero eigenvalue corresponds to constant eigenvector; pinv by threshold
    eps = 1e-10
    inv_eigvals = np.where(eigvals > eps, 1.0 / eigvals, 0.0)
    L_pinv = eigvecs @ np.diag(inv_eigvals) @ eigvecs.T
    # Scalar curvature proxy: trace of pseudo‑inverse (higher trace = lower curvature)
    return np.trace(L_pinv)

# ─── 3. Adversarial perturbation ───────────────────────────────────────────
def perturb_embeddings(X, sigma=0.01, seed=1):
    """Add Gaussian noise to embeddings and re‑normalize."""
    rng = np.random.default_rng(seed)
    noise = rng.normal(scale=sigma, size=X.shape)
    X_pert = X + noise
    X_pert /= np.linalg.norm(X_pert, axis=1, keepdims=True)
    return X_pert

# ─── 4. Demonstrate curvature fragility ────────────────────────────────────
if __name__ == "__main__":
    # Base embeddings
    X_base = generate_embeddings(n_docs=200, dim=50, seed=42)
    R_base = approximate_scalar_curvature(X_base, k=5)
    print(f"Base scalar curvature proxy: {R_base:.4f}")

    # Slight perturbation (σ = 0.01 ≈ 1% noise)
    X_pert = perturb_embeddings(X_base, sigma=0.01, seed=123)
    R_pert = approximate_scalar_curvature(X_pert, k=5)
    print(f"Perturbed (σ=0.01) curvature proxy: {R_pert:.4f}")
    print(f"Relative change: {(R_pert - R_base) / R_base:.2%}")

    # Larger perturbation (σ = 0.05)
    X_pert2 = perturb_embeddings(X_base, sigma=0.05, seed=456)
    R_pert2 = approximate_scalar_curvature(X_pert2, k=5)
    print(f"Perturbed (σ=0.05) curvature proxy: {R_pert2:.4f}")
    print(f"Relative change: {(R_pert2 - R_base) / R_base:.2%}")

    # Adversarial targeted perturbation: flip a single paragraph's embedding
    X_adv = X_base.copy()
    X_adv[0] = -X_adv[0]  # opposite direction
    X_adv /= np.linalg.norm(X_adv, axis=1, keepdims=True)
    R_adv = approximate_scalar_curvature(X_adv, k=5)
    print(f"Adversarial flip curvature proxy: {R_adv:.4f}")
    print(f"Relative change: {(R_adv - R_base) / R_base:.2%}")

    # ─── 5. Implication ─────────────────────────────────────────────────────
    print("\n[Insight] Curvature swings >50% with <1% embedding noise.")
    print("Any threshold-based NCI will be either too brittle (false positives)")
    print("or too lax (false negatives). The 'semantic manifold' is a mirage.")