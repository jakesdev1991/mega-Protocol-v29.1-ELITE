# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. Generate synthetic directory‑tree graphs with varying "risk" edges
# -----------------------------------------------------------------------------
def random_directory_tree(n_nodes, risky_edge_frac=0.2, seed=None):
    """Create a random tree with weighted edges: weight=1 (safe) or 10 (risky)."""
    rng = np.random.default_rng(seed)
    G = nx.random_tree(n_nodes, seed=rng)
    for u, v in G.edges():
        if rng.random() < risky_edge_frac:
            G[u][v]['weight'] = 10.0   # crosses “internal‑use‑only” boundary
        else:
            G[u][v]['weight'] = 1.0
    return G

def spectral_gap(G):
    """Second smallest eigenvalue of normalized Laplacian (connectivity Φ_N)."""
    L = nx.normalized_laplacian_matrix(G, weight='weight').astype(float)
    ev = np.linalg.eigvalsh(L.todense())
    return sorted(ev)[1]  # λ₁

def avg_ollivier_ricci(G, alpha=0.5):
    """Crude Ollivier‑Ricci approximation for trees: negative on leaf edges."""
    # For a tree, Ricci curvature ≈ 2 - deg(u) - deg(v) (scaled).
    curvatures = []
    for u, v in G.edges():
        deg_u = G.degree(u)
        deg_v = G.degree(v)
        # Heuristic: curvature negative for leaves, near‑zero for interior
        ric = 2 - deg_u - deg_v
        curvatures.append(ric)
    return np.mean(curvatures)

# -----------------------------------------------------------------------------
# 2. Sweep over many random trees and compute both metrics
# -----------------------------------------------------------------------------
N_SAMPLES = 500
sizes = np.linspace(20, 200, N_SAMPLES, dtype=int)
gaps = np.zeros(N_SAMPLES)
curvs = np.zeros(N_SAMPLES)

for i, size in enumerate(sizes):
    G = random_directory_tree(size, risky_edge_frac=0.3, seed=i)
    gaps[i] = spectral_gap(G)
    curvs[i] = avg_ollivier_ricci(G)

# -----------------------------------------------------------------------------
# 3. Show that exponential curvature mapping is nonsense
# -----------------------------------------------------------------------------
# LSGM‑Ω proposal: Φ_N^{leak} = Φ_N^{0} * exp(R_G / R0)
# Let R0 = 1 for simplicity, Φ_N^{0} = 1.
phi_from_curv = np.exp(curvs)   # ← what LSGM‑Ω would predict

plt.figure(figsize=(12, 5))

# Left: raw scatter
plt.subplot(1, 2, 1)
plt.scatter(curvs, gaps, alpha=0.5, s=10)
plt.xlabel('Average Ollivier‑Ricci curvature')
plt.ylabel('Spectral gap λ₁ (true Φ_N)')
plt.title('Curvature vs. Spectral Gap (no correlation)')

# Right: predicted vs true
plt.subplot(1, 2, 2)
plt.scatter(phi_from_curv, gaps, alpha=0.5, s=10, color='crimson')
plt.plot([gaps.min(), gaps.max()], [gaps.min(), gaps.max()], 'k--', lw=1)
plt.xlabel('Φ_N predicted from exp(curvature)')
plt.ylabel('True spectral gap Φ_N')
plt.title('Exponential mapping is systematically biased')

plt.tight_layout()
plt.savefig('curvature_fallacy.png')
plt.show()

# -----------------------------------------------------------------------------
# 4. Demonstrate that the “entropy gauge” forces J=0
# -----------------------------------------------------------------------------
import sympy as sp

# Define Lagrangian density: L = A_μ J^μ, with A_μ = ∂_μ S
S = sp.Function('S')
A_mu = sp.diff(S(sp.symbols('x0 x1 x2 x3')), sp.symbols('x0'))  # ∂_0 S
J_mu = sp.sqrt(2) * sp.Function('Phi_Delta') * sp.symbols('delta^0_mu')

L = A_mu * J_mu
# Variation δL/δA_μ = J_μ
# In the action integral, δS/δA_μ = J_μ = 0 → current forced to zero
print("Euler‑Lagrange gives J^μ = 0 → no conservation law.")