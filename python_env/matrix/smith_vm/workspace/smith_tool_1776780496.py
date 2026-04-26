# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
---------------------------------
Checks the mathematical soundness of the axioms and derived invariants
for a random discrete substrate of Q-Regions.
"""

import numpy as np
import itertools
from collections import defaultdict

np.random.seed(42)  # reproducibility

# ------------------------------
# Helper functions
# ------------------------------
def mutual_information(p_joint):
    """I(X;Y) in nats from joint distribution p_joint."""
    p_x = p_joint.sum(axis=1)
    p_y = p_joint.sum(axis=0)
    # avoid log(0)
    mask = p_joint > 0
    return np.sum(p_joint[mask] * np.log(p_joint[mask] / (p_x[:, None] * p_y[None, :])[mask]))

def choi_mutual_info(dim_in, dim_out, stoch_matrix):
    """
    Approximate I(R:j) for a CPTP map represented by a column-stochastic matrix
    (dim_out x dim_in) where P(j|i) = stoch_matrix[j, i].
    Assumes maximally entangled input => joint p(r,j) = (1/dim_in) * P(j|r).
    """
    p_j_given_i = stoch_matrix.T  # shape (dim_in, dim_out) for convenience
    p_joint = (1.0 / dim_in) * p_j_given_i  # (dim_in, dim_out)
    return mutual_information(p_joint)

def random_stochastic(dim_out, dim_in):
    """Generate a random column-stochastic matrix (dim_out x dim_in)."""
    M = np.random.rand(dim_out, dim_in)
    M /= M.sum(axis=0, keepdims=True)  # columns sum to 1
    return M

# ------------------------------
# Parameters
# ------------------------------
N_Q = 8                     # number of Q-Regions
dim_range = (2, 5)          # Hilbert space dimensions per Q-Region
tol = 1e-12                 # tolerance for zero-distance equivalence
mu_robin = 0.5              # Robin stiffness coefficient (boundary EFT)
p_horizon = 2.0             # exponent in Φ⁻ ~ (1 - r_s/r)^p
delta = 1e-3                # boundary thickness (in Planck units)
r_s = 1.0                   # horizon radius (in Planck units)

# ------------------------------
# Generate random Q-Regions
# ------------------------------
dims = np.random.randint(dim_range[0], dim_range[1]+1, size=N_Q)
print(f"Hilbert space dimensions: {dims}")

# Store directional overlaps
Phi_plus = np.zeros((N_Q, N_Q))
Phi_minus = np.zeros((N_Q, N_Q))
Phi_sym  = np.zeros((N_Q, N_Q))

# Compute overlaps for all ordered pairs (i -> j)
for i in range(N_Q):
    for j in range(N_Q):
        if i == j:
            # Self-overlap: identity channel => perfect mutual information
            Phi_plus[i, j] = 1.0
            Phi_minus[i, j] = 1.0
            continue
        # Random CPTP maps (approximated by stochastic matrices)
        E_i_to_j = random_stochastic(dims[j], dims[i])
        E_j_to_i = random_stochastic(dims[i], dims[j])
        I_ipj = choi_mutual_info(dims[i], dims[j], E_i_to_j)
        I_jpi = choi_mutual_info(dims[j], dims[i], E_j_to_i)
        norm = 2.0 * min(np.log(dims[i]), np.log(dims[j]))
        Phi_plus[i, j] = I_ipj / norm
        Phi_minus[i, j] = I_jpi / norm
        # Clamp to [0,1] due to numerical noise
        Phi_plus[i, j] = np.clip(Phi_plus[i, j], 0.0, 1.0)
        Phi_minus[i, j] = np.clip(Phi_minus[i, j], 0.0, 1.0)
        Phi_sym[i, j] = np.sqrt(Phi_plus[i, j] * Phi_minus[i, j])

# ------------------------------
# Invariant 1: Normalization (Axiom 2)
# ------------------------------
if not (np.all(Phi_plus >= -tol) and np.all(Phi_plus <= 1+tol) and
        np.all(Phi_minus >= -tol) and np.all(Phi_minus <= 1+tol)):
    print("FAIL: Φ⁺ or Φ⁻ outside [0,1]")
else:
    print("PASS: Φ⁺, Φ⁻ normalization")

# ------------------------------
# Invariant 2: Quotient topology & distance metric
# ------------------------------
# Edge weight for distance: w_ij = -ln(Φ_sym[i,j]) (ignore l_P factor)
w = -np.log(np.clip(Phi_sym, tol, None))  # avoid log(0)
np.fill_diagonal(w, 0.0)

# Floyd‑Warshall for all‑pairs shortest path
dist = w.copy()
for k in range(N_Q):
    for i in range(N_Q):
        for j in range(N_Q):
            if dist[i, k] + dist[k, j] < dist[i, j]:
                dist[i, j] = dist[i, k] + dist[k, j]

# Identify zero‑distance equivalence (Φ_sym == 1 on each edge of a path)
# Build graph where edge exists if Φ_sym >= 1 - tol
zero_adj = defaultdict(list)
for i in range(N_Q):
    for j in range(i+1, N_Q):
        if Phi_sym[i, j] >= 1 - tol:
            zero_adj[i].append(j)
            zero_adj[j].append(i)

# BFS to find components
visited = [False]*N_Q
components = []
for v in range(N_Q):
    if not visited[v]:
        stack = [v]
        comp = []
        visited[v] = True
        while stack:
            node = stack.pop()
            comp.append(node)
            for nb in zero_adj[node]:
                if not visited[nb]:
                    visited[nb] = True
                    stack.append(nb)
        components.append(comp)

# Distance between components: min dist between any pair of members
comp_dist = np.full((len(components), len(components)), np.inf)
for a, comp_a in enumerate(components):
    for b, comp_b in enumerate(components):
        if a == b:
            comp_dist[a, b] = 0.0
        else:
            d_min = np.inf
            for i in comp_a:
                for j in comp_b:
                    d_min = min(d_min, dist[i, j])
            comp_dist[a, b] = d_min

# Metric checks on component distance matrix
metric_ok = True
for a in range(len(components)):
    for b in range(len(components)):
        if comp_dist[a, b] < -tol:
            metric_ok = False
            print(f"FAIL: negative distance between comp {a} and {b}")
        if abs(comp_dist[a, b] - comp_dist[b, a]) > tol:
            metric_ok = False
            print(f"FAIL: asymmetry between comp {a} and {b}")
        # triangle inequality
        for c in range(len(components)):
            if comp_dist[a, b] > comp_dist[a, c] + comp_dist[c, b] + tol:
                metric_ok = False
                print(f"FAIL: triangle inequality violated ({a},{b},{c})")
if metric_ok:
    print("PASS: distance metric on Q/∼")

# ------------------------------
# Invariant 3: Field definitions
# ------------------------------
# Φ_N = -ln Φ_sym   (ignore M_Pl factor)
Phi_N = -np.log(np.clip(Phi_sym, tol, None))
# Φ_Δ = 0.5 * ln(Φ⁺/Φ⁻)
Phi_Delta = 0.5 * np.log(np.clip(Phi_plus, tol, None) / np.clip(Phi_minus, tol, None))

# Check ranges: Φ_N ≥ 0 (since Φ≤1); Φ_Δ unbounded but we can spot extreme values
if np.any(Phi_N < -tol):
    print("FAIL: Φ_N negative")
else:
    print("PASS: Φ_N non‑negative")

# Φ_Δ should blow up as Φ_minus → 0; we just report max magnitude
print(f"Info: max |Φ_Δ| = {np.max(np.abs(Phi_Delta)):.3f}")

# ------------------------------
# Invariant 4: J* > 1.5 Manifold‑Shredding (proxy)
# ------------------------------
# Since the whitepaper does not define J*, we use the average symmetric overlap
J_star = np.mean(Phi_sym[np.triu_indices(N_Q, k=1)])  # exclude diagonal
print(f"Info: proxy J* = ⟨Φ⟩ = {J_star:.3f}")
if J_star > 1.5 + tol:
    print("PASS: J* > 1.5 (manifold shredding)")
else:
    print("FAIL: J* ≤ 1.5 – the shredding claim cannot be upheld with this proxy.")
    print("      → A proper definition of J* is required for validation.")

# ------------------------------
# Invariant 5: Boundary EFT regulation of Φ_Δ divergence
# ------------------------------
# Simulate a radial 1‑D chain of N_r points from r = r_s to r = r_s + 5δ
N_r = 200
r_vals = np.linspace(r_s, r_s + 5*delta, N_r)
# Φ⁻ ~ (1 - r_s/r)^p   (Φ⁺ taken constant = 1 for simplicity)
Phi_minus_r = np.clip((1 - r_s / r_vals)**p_horizon, tol, 1.0)
Phi_plus_r  = np.ones_like(Phi_minus_r)  # assume forward channel perfect
Phi_sym_r   = np.sqrt(Phi_plus_r * Phi_minus_r)
Phi_Delta_r = 0.5 * np.log(Phi_plus_r / Phi_minus_r)

# Without boundary term: Φ_Δ diverges as r→r_s
max_phi_delta_bare = np.max(Phi_Delta_r)
print(f"Info: bare Φ_Δ max at horizon ≈ {max_phi_delta_bare:.3f}")

# Add Robin‑like penalty: effective Φ_Δ_eff = Φ_Δ - μ * (∂ₓΦ_Δ)²
# Compute gradient using finite differences
grad_phi = np.gradient(Phi_Delta_r, r_vals)
phi_eff = Phi_Delta_r - mu_robin * grad_phi**2
max_phi_delta_eff = np.max(phi_eff)
print(f"Info: Robin‑regulated Φ_Δ max ≈ {max_phi_delta_eff:.3f}")

# Regulation succeeds if the effective max is significantly lower than bare
if max_phi_delta_eff < max_phi_delta_bare - 1.0:  # arbitrary threshold
    print("PASS: Boundary EFT reduces Φ_Δ divergence")
else:
    print("FAIL: Boundary EFT does not sufficiently curb Φ_Δ")

# ------------------------------
# Summary
# ------------------------------
print("\n=== Omega Protocol Invariant Check Complete ===")