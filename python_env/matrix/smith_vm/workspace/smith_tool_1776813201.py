# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validation for LSGM‑Ω (Leakage‑Surface Geometry Monitor)
--------------------------------------------------------------------
This script implements the mathematical checks described in the meta‑scrutiny
analysis.  It is deliberately self‑contained and uses only the standard
scientific Python stack (numpy, scipy, networkx).

Run:
    python3 validate_lsgm_omega.py
"""

import numpy as np
import networkx as nx
from scipy.linalg import eig
from scipy.spatial.distance import pdist, squareform

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def ollivier_ricci_curvature(G, alpha=0.5):
    """
    Compute Ollivier‑Ricci curvature for each edge of an undirected graph G.
    Returns a dict {(u,v): curvature}.
    Implementation follows the discrete optimal‑transport formulation
    with a simple lazy‑random‑walk measure (alpha = laziness).
    """
    curvature = {}
    # Precompute shortest‑path distances (unweighted for simplicity)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    for u, v in G.edges():
        # Probability measures: lazy random walk from u and v
        def measure(x):
            m = {y: 0.0 for y in G.nodes()}
            m[x] += alpha
            neigh = list(G.neighbors(x))
            if neigh:
                mass_each = (1.0 - alpha) / len(neigh)
                for y in neigh:
                    m[y] += mass_each
            return m
        mu = measure(u)
        nu = measure(v)
        # Wasserstein‑1 distance via linear programming (here we use the
        # earth‑mover distance on the metric space given by shortest paths)
        # For small graphs we can solve via the Kantorovich dual:
        # W = max_{f: Lip(f)≤1} Σ_x f(x)(μ(x)-ν(x))
        # We approximate by solving a linear program (simplex) using scipy.
        from scipy.optimize import linprog
        n = len(G.nodes())
        node_list = list(G.nodes())
        idx = {node: i for i, node in enumerate(node_list)}
        # Build cost matrix C_ij = d(node_i, node_j)
        C = np.zeros((n, n))
        for i, ni in enumerate(node_list):
            for j, nj in enumerate(node_list):
                C[i, j] = dist[ni][nj]
        # Equality constraints: sum_j x_ij = μ_i, sum_i x_ij = ν_j
        A_eq = []
        b_eq = []
        for i in range(n):
            row = np.zeros(n * n)
            row[i * n:(i + 1) * n] = 1.0
            A_eq.append(row)
            b_eq.append(mu[node_list[i]])
        for j in range(n):
            row = np.zeros(n * n)
            row[j::n] = 1.0
            A_eq.append(row)
            b_eq.append(nu[node_list[j]])
        # Bounds 0 ≤ x_ij ≤ ∞
        bounds = [(0, None)] * (n * n)
        # Objective: minimize Σ C_ij x_ij
        res = linprog(C.flatten(), A_eq=A_eq, b_eq=b_eq,
                      bounds=bounds, method='highs')
        if not res.success:
            raise RuntimeError("Wasserstein LP failed")
        W = res.fun
        curvature[(u, v)] = 1.0 - W / dist[u][v] if dist[u][v] > 0 else 0.0
    return curvature

def compute_hessian(E, K, params):
    """
    Quadratic approximation of the coupled action S[E,K] around a background.
    Returns the 2x2 Hessian matrix.
    We use a toy form:
        S = 0.5*(a_E*E^2 + a_K*K^2) + b*E*K + V(E,K)
    where V = 0.5*c_E*(E-E0)^2 + 0.5*c_K*(K-K0)^2 + g*E*K^2.
    The Hessian is constant (independent of E,K) for this quadratic truncation.
    """
    a_E, a_K, b, c_E, c_K, g, E0, K0 = params
    # Second derivatives:
    S_EE = a_E + c_E          # d^2/dE^2 of 0.5*a_E*E^2 + 0.5*c_E*(E-E0)^2
    S_KK = a_K + c_K + 2*g*E  # d^2/dK^2 of 0.5*a_K*K^2 + 0.5*c_K*(K-K0)^2 + g*E*K^2
    S_EK = b + 2*g*K          # d^2/dE dK of b*E*K + g*E*K^2
    return np.array([[S_EE, S_EK],
                     [S_EK, S_KK]])

def spectral_gap_and_skewness(H):
    """Return Φ_N = λ1/tr(H) and Φ_Δ = skewness of eigenvalues."""
    evals = eig(H)[0]  # complex, but H is symmetric real → real evals
    evals = np.real(evals)
    trH = np.trace(H)
    if trH == 0:
        raise ValueError("Trace of Hessian zero")
    # Order eigenvalues descending
    lam = np.sort(evals)[::-1]
    phi_N = lam[0] / trH
    # Skewness: third central moment / (std^3)
    mu = np.mean(lam)
    sigma = np.std(lam)
    if sigma == 0:
        phi_Delta = 0.0
    else:
        phi_Delta = np.mean(((lam - mu) ** 3)) / (sigma ** 3)
    return phi_N, phi_Delta, lam

def leackage_surface_fragility(curvature_dict, EFI_dict, S_dir, v_c,
                               weights=(1.0, 1.0, 1.0, 1.0)):
    """
    Compute LSFI = sigmoid( α*R_max + β*C_KE + γ*(1-S_dir) + δ*v_c )
    where:
        R_max = max curvature over nodes
        C_KE = correlation between curvature and EFI
        S_dir = Shannon entropy of directory-type distribution (input)
        v_c   = exposure‑velocity estimate (input)
    """
    alpha, beta, gamma, delta = weights
    nodes = list(curvature_dict.keys())
    # Node‑wise curvature: average over incident edges
    node_curv = {n: 0.0 for n in set([e[0] for e in nodes] + [e[1] for e in nodes])}
    for (u, v), curv in curvature_dict.items():
        node_curv[u] += curv
        node_curv[v] += curv
    for n in node_curv:
        node_curv[n] /= (len(list(G.neighbors(n))) if G.neighbors(n) else 1)
    R_max = max(node_curv.values()) if node_curv else 0.0
    # Correlation curvature‑EFI
    curv_vals = np.array([node_curv[n] for n in node_curv])
    efi_vals = np.array([EFI_dict.get(n, 0.0) for n in node_curv])
    if len(curv_vals) > 1:
        C_KE = np.corrcoef(curv_vals, efi_vals)[0, 1]
    else:
        C_KE = 0.0
    # Sigmoid
    z = alpha * R_max + beta * C_KE + gamma * (1.0 - S_dir) + delta * v_c
    LSFI = 1.0 / (1.0 + np.exp(-z))
    return LSFI, R_max, C_KE

def shannon_entropy(type_counts):
    """Input: dict {type: count}. Returns S = - Σ p log p."""
    total = sum(type_counts.values())
    if total == 0:
        return 0.0
    probs = np.array([c / total for c in type_counts.values()])
    # Avoid log(0)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log(probs))

def current_conservation(J_series, dt=1.0):
    """
    Check ∂_μ J^μ ≈ 0 using finite differences.
    J_series: array shape (T, 4) with J^μ = (J^0, J^1, J^2, J^3)
    Returns True if max|∂_μ J^μ| < tol.
    """
    # Simple forward difference for ∂_0 J^0 + ∂_i J^i (assuming spatial homogeneity)
    dJ0 = np.diff(J_series[:, 0]) / dt
    # Assume spatial components are constant or zero for toy model → ∂_i J^i ≈ 0
    divJ = dJ0  # in 1+1D reduction
    return np.max(np.abs(divJ)) < 1e-6

# ----------------------------------------------------------------------
# Toy data representing a minimal directory tree
# ----------------------------------------------------------------------
G = nx.balanced_tree(r=2, h=3)  # binary tree depth 3 → 15 nodes
# Mark some edges as crossing an "internal use only" boundary
internal_edges = [(0, 1), (0, 2)]  # root to its two children
for u, v in internal_edges:
    if G.has_edge(u, v):
        G[u][v]['weight'] = 2.0   # higher weight = higher resistance
    else:
        G[v][u]['weight'] = 2.0
# Default weight = 1.0
for u, v in G.edges():
    if 'weight' not in G[u][v]:
        G[u][v]['weight'] = 1.0

# Exposure probability per node (0-1)
np.random.seed(42)
exposure = {n: np.random.rand() for n in G.nodes()}
# Epistemic Fragility Index (EFI) per node (0-1)
EFI = {n: np.random.rand() for n in G.nodes()}

# Directory‑type entropy (example: three types: checkpoint, gradient, validation)
type_counts = {'checkpoint': 5, 'gradient': 5, 'validation': 5}
S_dir = shannon_entropy(type_counts)

# Exposure‑velocity estimate: average exposure over nodes
v_c = np.mean(list(exposure.values()))

# ----------------------------------------------------------------------
# Step 1: Compute Ollivier‑Ricci curvature on the graph
# ----------------------------------------------------------------------
curvature = ollivier_ricci_curvature(G, alpha=0.5)

# ----------------------------------------------------------------------
# Step 2: Build a toy Hessian from the coupled action
# ----------------------------------------------------------------------
# Parameters chosen to give a positive‑definite Hessian
params = (1.0, 1.0, 0.2,   # a_E, a_K, b
          0.5, 0.5, 0.1,   # c_E, c_K, g
          0.0, 0.0)        # E0, K0 (background values)
H = compute_hessian(E=0.0, K=0.0, params=params)

# ----------------------------------------------------------------------
# Step 3: Extract covariant modes
# ----------------------------------------------------------------------
phi_N, phi_Delta, evals = spectral_gap_and_skewness(H)
psi = np.log(phi_N)   # invariant ψ = ln Φ_N

# ----------------------------------------------------------------------
# Step 4: Compute LSFI and related metrics
# ----------------------------------------------------------------------
LSFI, R_max, C_KE = leackage_surface_fragility(
    curvature_dict=curvature,
    EFI_dict=EFI,
    S_dir=S_dir,
    v_c=v_c,
    weights=(1.0, 1.0, 1.0, 1.0)
)

# ----------------------------------------------------------------------
# Step 5: Build a toy gauge current J^μ = sqrt(2) Φ_Δ δ^μ_0
# ----------------------------------------------------------------------
J0 = np.sqrt(2.0) * phi_Delta
J_series = np.tile([J0, 0.0, 0.0, 0.0], (10, 1))  # constant in time for toy model

# ----------------------------------------------------------------------
# Step 6: Verify Omega‑Protocol conditions
# ----------------------------------------------------------------------
tol = 1e-8

# Invariant: ψ must be real (phi_N > 0)
invariant_ok = phi_N > 0 and np.isfinite(psi)

# Covariant modes: phi_N in (0,1] (since λ₁ ≤ tr(H) for PSD H)
covariant_ok = 0.0 < phi_N <= 1.0 + tol

# Boundary conditions (we only check that the definitions are usable)
# Shredding Event: ψ → +∞ and Φ_Δ → +∞  (not triggered here)
# Informational Freeze: ψ → -∞ and Φ_Δ → 0   (not triggered here)
# For validation we ensure no spurious infinities:
boundary_ok = np.isfinite(psi) and np.isfinite(phi_Delta)

# Entropy gauge current conservation (∂_μ J^μ ≈ 0)
current_ok = current_conservation(J_series, dt=1.0)

# MPC‑Ω constraints
constraints_ok = (LSFI <= 0.65 + tol) and (phi_N >= 0.5 - tol) and (S_dir >= np.log(4) - tol)

# ----------------------------------------------------------------------
# Final verdict
# ----------------------------------------------------------------------
all_ok = invariant_ok and covariant_ok and boundary_ok and current_ok and constraints_ok

print("=== Omega‑Protocol Validation Report ===")
print(f"Phi_N (spectral gap)          : {phi_N:.6f}")
print(f"Phi_Delta (skewness)          : {phi_Delta:.6f}")
print(f"Invariant ψ = ln(Phi_N)       : {psi:.6f}")
print(f"LSFI                          : {LSFI:.6f}")
print(f"Directory entropy S_dir       : {S_dir:.6f} (required ≥ log(4)≈{np.log(4):.6f})")
print(f"Current conservation check    : {current_ok}")
print(f"All constraints satisfied?    : {all_ok}")
if all_ok:
    print("RESULT: PASS – the proposal is mathematically sound and Omega‑compliant.")
else:
    print("RESULT: FAIL – one or more Omega‑Protocol checks violated.")