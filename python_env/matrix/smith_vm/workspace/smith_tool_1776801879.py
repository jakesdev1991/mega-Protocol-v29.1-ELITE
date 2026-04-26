# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol BRDI‑Ω (Byzantine‑Resilient Data Ingestion) validator.
Checks mathematical consistency of the proposal and enforces the MPC‑Ω QP constraints.
"""

import numpy as np
import scipy.stats as stats
import networkx as nx
from itertools import combinations

# ------------------------------------------------------------
# Helper functions (all quantities are assumed dimensionless after
# normalisation of the raw data vector d(t) to unit variance).
# ------------------------------------------------------------
def sparse_encoding_matrix(n, d, density=0.1):
    """Return a random n×d matrix with given sparsity (density of non‑zeros)."""
    E = np.random.randn(n, d)
    mask = np.random.rand(n, d) > density   # True → keep, False → zero
    E[mask] = 0.0
    # Normalise columns to unit ℓ2 norm (helps keep d(t) scale‑free)
    col_norm = np.linalg.norm(E, axis=0, keepdims=True)
    E /= (col_norm + 1e-12)
    return E

def encode_data(E, d_vec):
    """y = E @ d_vec  (shape: (n,))"""
    return E @ d_vec

def distribute(y, m):
    """Split encoded vector y into m (approximately) equal sub‑vectors."""
    n = y.shape[0]
    base = n // m
    rem = n % m
    parts = []
    idx = 0
    for i in range(m):
        size = base + (1 if i < rem else 0)
        parts.append(y[idx:idx+size])
        idx += size
    return parts  # list of length m, each a np.ndarray

def corrupt_sources(parts, t, corruption_level=5.0):
    """Byzantine corruption: add large Gaussian noise to t randomly chosen sources."""
    corrupted = parts.copy()
    idxs = np.random.choice(len(parts), size=t, replace=False)
    for i in idxs:
        corrupted[i] = corrupted[i] + corruption_level * np.random.randn(*parts[i].shape)
    return corrupted, set(idxs)

def decode_data(E, y_hat_list):
    """
    Least‑squares decoder: solve E d ≈ y_hat (concatenated).
    Returns d_hat and residual vector r_i = y_hat_i - E_i d_hat.
    """
    # Stack all source responses into a long vector y_concat and build block‑diagonal E_big
    m = len(y_hat_list)
    n_total = sum(len(p) for p in y_hat_list)
    y_concat = np.concatenate(y_hat_list)
    # Build E_big: each source i gets the same E matrix but only rows corresponding to its sub‑vector
    blocks = []
    row_start = 0
    for sub in y_hat_list:
        ni = len(sub)
        Ei = np.zeros((ni, E.shape[0]))
        Ei[:, :E.shape[1]] = E  # each source sees the full encoding matrix (only its rows used)
        blocks.append(Ei)
        row_start += ni
    E_big = np.block([[blocks[i] if i==j else np.zeros_like(blocks[i])
                       for j in range(m)] for i in range(m)])  # simpler: use kron
    # Actually, a simpler approach: each source sees the same E, so we can stack:
    E_big = np.kron(np.eye(m), E)  # shape (m*n, n)
    # Trim to actual lengths (some sources may have different lengths due to remainder)
    # We'll just use the first len(y_hat_list[0]) rows per source for simplicity:
    n_per_source = len(y_hat_list[0])
    E_big = np.kron(np.eye(m), E[:n_per_source, :])
    y_concat = np.concatenate([p[:n_per_source] for p in y_hat_list])
    # Least squares
    d_hat, *_ = np.linalg.lstsq(E_big, y_concat, rcond=None)
    # Residuals per source
    residuals = []
    start = 0
    for sub in y_hat_list:
        ni = len(sub)
        yi = sub[:n_per_source] if len(sub) > n_per_source else sub
        Ei = E_big[start:start+ni, :]
        ri = yi - Ei @ d_hat
        residuals.append(ri)
        start += ni
    residuals = np.concatenate(residuals)
    return d_hat, residuals

def compute_dci(residuals, m, tau, alpha, beta, gamma, n, d):
    """Data Corruption Index per the proposal."""
    # per‑source residual norm
    norms = np.linalg.norm(residuals.reshape(m, -1), axis=1)
    epsilon = np.mean(norms)
    theta = np.mean(norms > tau)          # corruption ratio
    rho = n / d
    dci = np.tanh(alpha * theta + beta * epsilon + gamma * rho)
    return dci, epsilon, theta, rho, norms

def phi_n_from_decoded(d_hat_list):
    """Variance of decoded data across sources (inverse connectivity)."""
    # d_hat_list: list of decoded vectors per source (should be identical if no noise)
    stacked = np.stack(d_hat_list, axis=0)  # shape (m, d)
    var_per_dim = np.var(stacked, axis=0)
    return np.mean(var_per_dim)             # scalar variance

def phi_delta_from_residuals(residuals):
    """Skewness of residual‑error distribution (asymmetry)."""
    flat = residuals.ravel()
    return stats.skew(flat)

def entropy_from_residuals(residuals):
    """S_data = -∑ p_i log p_i, p_i = ||ŷ_i|| / ∑ ||ŷ_j||."""
    norms = np.linalg.norm(residuals.reshape(-1, residuals.shape[-1] // m), axis=1)
    p = norms / np.sum(norms)
    # avoid log(0)
    p = np.clip(p, 1e-12, None)
    return -np.sum(p * np.log(p))

def ollivier_ricci_curvature_graph(norms):
    """
    Approximate Ollivier‑Ricci curvature on a complete graph where edge weight
    = 1 - exp(-|‖r_i‖ - ‖r_j‖|).  Returns average scalar curvature 𝒞.
    For demonstration we use the simpler Forman‑Ricci proxy:
        𝒞_ij = w_i + w_j - 2*w_ij   (with w_i = node weight, w_ij = edge weight)
    and take the mean over edges.
    """
    m = len(norms)
    # node weight = norm
    w_i = norms
    # edge weight = similarity (Gaussian kernel of norm difference)
    sigma = np.std(norms) + 1e-6
    W = np.exp(-0.5 * ((w_i[:, None] - w_i[None, :]) / sigma) ** 2)
    np.fill_diagonal(W, 0.0)
    # Forman‑Ricci on edge (i,j):  w_i + w_j - 2*W_ij
    ricci = []
    for i in range(m):
        for j in range(i+1, m):
            ricci.append(w_i[i] + w_i[j] - 2.0 * W[i, j])
    return np.mean(ricci) if ricci else 0.0

# ------------------------------------------------------------
# Main validation routine
# ------------------------------------------------------------
def validate_brdi_omega(
    m=30, d=50, n=150,          # m sources, original dimension d, encoded dimension n (ρ=3)
    t=None,                     # max Byzantine sources (default floor((m-1)/2))
    tau=1.0,                    # residual threshold for corruption detection
    alpha=1.0, beta=1.0, gamma=1.0,
    lambda_psi=0.5, R0=1.0,
    num_trials=20
):
    if t is None:
        t = (m - 1) // 2

    all_ok = True
    for trial in range(num_trials):
        # 1. Generate true data vector (unit variance per component)
        d_true = np.random.randn(d)

        # 2. Build encoding matrix
        E = sparse_encoding_matrix(n, d, density=0.05)   # ~5% nonzeros → sparse

        # 3. Encode and distribute
        y = encode_data(E, d_true)
        parts = distribute(y, m)

        # 4. Corrupt up to t sources
        y_hat_list, corrupted_idxs = corrupt_sources(parts, t, corruption_level=4.0)

        # 5. Decode and get residuals
        d_hat, residuals = decode_data(E, y_hat_list)

        # 6. Compute DCI and related quantities
        dci, eps, theta, rho, norms = compute_dci(
            residuals, m, tau, alpha, beta, gamma, n, d)

        # 7. Compute Ω‑mode observables
        # For Φ_N we need decoded data per source (use the same d_hat for all)
        d_hat_per_source = [d_hat] * m
        Phi_N = phi_n_from_decoded(d_hat_per_source)
        Phi_Delta = phi_delta_from_residuals(residuals)
        S_data = entropy_from_residuals(residuals)

        # 8. Compute invariant ψ
        # Approximate source‑graph curvature via Ollivier‑Ricci on norm vector
        curv = ollivier_ricci_curvature_graph(norms)
        psi = np.log(np.abs(curv) / R0) + lambda_psi * dci

        # 9. MPC‑Ω QP constraints
        c1 = dci <= 0.7 + 1e-9          # DCI ≤ 0.7
        c2 = Phi_N >= 0.6 - 1e-9        # Φ_N ≥ 0.6
        c3 = S_data >= np.log(3) - 1e-9 # entropy ≥ ln(3)

        # 10. Cost integrand (should be non‑negative)
        integrand = (
            max(dci - 0.6, 0.0) ** 2 +
            0.5 * max(0.6 - Phi_N, 0.0) ** 2 +
            0.5 * (Phi_Delta) ** 2 +
            0.5 * max(np.log(3) - S_data, 0.0) ** 2
        )
        c4 = integrand >= -1e-12   # allow tiny numerical noise

        if not (c1 and c2 and c3 and c4):
            print(f"Trial {trial}: constraint violation")
            print(f"  DCI={dci:.3f} (≤0.7? {c1})")
            print(f"  Φ_N={Phi_N:.3f} (≥0.6? {c2})")
            print(f"  S_data={S_data:.3f} (≥ln3? {c3})")
            print(f"  integrand={integrand:.6f} (≥0? {c4})")
            all_ok = False
            break

        # Optional: print a snapshot
        if trial == 0:
            print("=== Sample trial (trial 0) ===")
            print(f"  m={m}, d={d}, n={n}, ρ={rho:.2f}")
            print(f"  DCI={dci:.3f}, ε={eps:.3f}, θ={theta:.3f}")
            print(f"  Φ_N={Phi_N:.3f}, Φ_Δ={Phi_Delta:.3f}, S_data={S_data:.3f}")
            print(f"  ψ={psi:.3f} (curv={curv:.3f})")
            print(f"  Corrupted sources: {sorted(corrupted_idxs)}")
            print("-------------------------------")

    if all_ok:
        print("\n✅ All validation checks passed.")
    else:
        print("\n❌ Validation failed – see above.")
    return all_ok

# ------------------------------------------------------------
# Run the validator (feel free to tweak parameters)
# ------------------------------------------------------------
if __name__ == "__main__":
    validate_brdi_omega()