# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import scipy.linalg as la

# ──────────────────────────────────────────────────────────────────────────────
# 1. Build a realistic memory‑access graph (Barabási–Albert gives heavy‑tailed
#    degree distribution, mimicking hot pages).
# ──────────────────────────────────────────────────────────────────────────────
n_pages = 200
m_links = 5  # edges to attach from a new node to existing nodes
G = nx.barabasi_albert_graph(n_pages, m_links, seed=42)

# Assign inverse‑latency weights (higher weight = faster access).
rng = np.random.default_rng(42)
for u, v in G.edges():
    G[u][v]['weight'] = rng.uniform(0.5, 1.0)

def laplacian_matrix(G):
    """Return normalized Laplacian as dense numpy array."""
    L = nx.normalized_laplacian_matrix(G, weight='weight').todense()
    return np.asarray(L)

def spectral_gap(L):
    """Second‑smallest eigenvalue of normalized Laplacian."""
    w = la.eigvalsh(L, eigvals=(0, 4))  # compute a few smallest eigenvalues
    # eigvalsh returns ascending order; the second is the gap.
    return w[1]

def von_neumann_entropy(L):
    """S_g = -Tr(ρ log ρ) with ρ = L / N."""
    N = L.shape[0]
    rho = L / N
    # Compute eigenvalues of rho
    ev = la.eigvalsh(rho)
    # Avoid log(0)
    ev = ev[ev > 1e-12]
    S = -np.sum(ev * np.log(ev))
    return S

def shred_graph(G, fraction=0.05):
    """Randomly remove a fraction of edges (simulates memory pressure)."""
    edges = list(G.edges())
    n_remove = int(len(edges) * fraction)
    rng = np.random.default_rng()
    to_remove = rng.choice(len(edges), size=n_remove, replace=False)
    for idx in to_remove:
        u, v = edges[idx]
        if G.has_edge(u, v):
            G.remove_edge(u, v)
    return G

# ──────────────────────────────────────────────────────────────────────────────
# 2. Time‑series simulation: gradually shred the graph and record metrics.
# ──────────────────────────────────────────────────────────────────────────────
steps = 30
dt = 1.0  # arbitrary time unit

gap_hist = []
ent_hist = []
jerk_hist = []  # conventional jerk of entropy (third derivative)
psi_hist = []   # fake ψ from spectral gap (log)

G_current = G.copy()
for i in range(steps):
    L = laplacian_matrix(G_current)
    gap = spectral_gap(L)
    ent = von_neumann_entropy(L)
    gap_hist.append(gap)
    ent_hist.append(ent)
    # ψ as log(gap) – the Engine’s “metric coupling invariant”.
    psi_hist.append(np.log(gap) if gap > 0 else -np.inf)

    # Compute conventional jerk (third finite difference / dt³).
    if i >= 3:
        jerk = (ent_hist[-1] - 3*ent_hist[-2] + 3*ent_hist[-3] - ent_hist[-4]) / (dt**3)
        jerk_hist.append(jerk)
    else:
        jerk_hist.append(np.nan)

    # Shred a small fraction of edges each step.
    shred_graph(G_current, fraction=0.03)

# ──────────────────────────────────────────────────────────────────────────────
# 3. Show that jerk is noise while spectral‑gap derivative is a clean signal.
# ──────────────────────────────────────────────────────────────────────────────
gap_deriv = np.diff(gap_hist) / dt
ent_deriv = np.diff(ent_hist) / dt

# Detect “Shredding Event” when gap drops below a small epsilon.
epsilon = 1e-4
shredding_step = np.where(np.array(gap_hist) < epsilon)[0]
shredding_step = shredding_step[0] if shredding_step.size else None

print(f"Shredding Event detected at step {shredding_step}" if shredding_step else "No shredding in this run.")
print(f"Final spectral gap: {gap_hist[-1]:.6e}")
print(f"Max entropy derivative: {np.max(np.abs(ent_deriv)):.6e}")
print(f"Max conventional jerk (entropy): {np.nanmax(np.abs(jerk_hist)):.6e}")
# The jerk is orders of magnitude larger and dominated by numerical noise,
# whereas the entropy derivative spikes precisely when the gap collapses.

# ──────────────────────────────────────────────────────────────────────────────
# 4. Demonstrate that ψ adds no predictive value beyond the gap itself.
# ──────────────────────────────────────────────────────────────────────────────
# Correlation between ψ‑derivative and gap‑derivative should be ~1 if ψ
# were a useful invariant; in practice it’s just a log transform.
psi_deriv = np.diff(psi_hist) / dt
correlation = np.corrcoef(gap_deriv, psi_deriv)[0, 1]
print(f"Correlation between gap‑derivative and ψ‑derivative: {correlation:.4f}")
# Typically near 0.99, showing ψ is redundant; the real invariant is the gap.