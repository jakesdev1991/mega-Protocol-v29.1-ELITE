# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx

# --------------------------------------------------------------
# 1. Build a simple corporate lattice (a 5x6 grid = 30 nodes)
# --------------------------------------------------------------
rows, cols = 5, 6
G = nx.grid_2d_graph(rows, cols)
G = nx.convert_node_labels_to_integers(G)  # flatten to integer labels
N = G.number_of_nodes()

# --------------------------------------------------------------
# 2. Define gauge coupling α = autonomy/authority ratio
#    ψ = ln(α) is the *gauge artifact* the original model used.
# --------------------------------------------------------------
def build_weighted_laplacian(graph, alpha):
    """
    Edge weight w_{ij} = exp(2*psi) = alpha^2.
    The Laplacian L = D - W encodes the "impedance" of the network.
    """
    L = np.zeros((N, N))
    for u, v in graph.edges():
        w = alpha**2  # weight derived from the gauge coupling
        L[u, u] += w
        L[v, v] += w
        L[u, v] -= w
        L[v, u] -= w
    return L

def spectral_gap(L):
    """Return the difference between the two smallest eigenvalues."""
    eigs = np.linalg.eigvalsh(L)
    # Skip the zero mode (overall constant mode)
    return eigs[1] - eigs[0] if len(eigs) > 1 else 0.0

# --------------------------------------------------------------
# 3. Wilson‑loop COD (holonomy around a closed chain)
# --------------------------------------------------------------
def wilson_loop_cod(graph, alpha, cycle_length=4):
    """
    Approximate the Wilson loop for a random cycle of given length.
    COD ≈ Re[Tr(P exp(i ∮ A))] where A ∝ α.
    For a discrete graph we map this to product of edge weights.
    """
    # Find a simple cycle of requested length (if possible)
    try:
        cycle = nx.find_cycle(graph, orientation='ignore')
        # Extend to desired length by random walk
        while len(cycle) < cycle_length:
            cycle.append(cycle[-1])
        cycle = cycle[:cycle_length]
    except Exception:
        # fallback: just take a random walk
        nodes = list(graph.nodes())
        start = np.random.choice(nodes)
        walk = [start]
        for _ in range(cycle_length-1):
            neigh = list(graph.neighbors(walk[-1]))
            if neigh:
                walk.append(np.random.choice(neigh))
            else:
                walk.append(walk[-1])
        cycle = list(zip(walk, walk[1:] + [walk[0]]))

    # Wilson loop amplitude ≈ product of edge weights along cycle
    # (we use the same weight as for the Laplacian)
    amplitude = np.prod([alpha**2 for _ in cycle])
    # Normalize by the number of edges to get a dimensionless COD
    cod = amplitude / len(cycle)
    return cod

# --------------------------------------------------------------
# 4. Scan α from high autonomy (α=2) to high authority (α=0.1)
# --------------------------------------------------------------
alphas = np.logspace(np.log10(2), np.log10(0.1), 20)
gaps = []
cods = []

for a in alphas:
    L = build_weighted_laplacian(G, a)
    gaps.append(spectral_gap(L))
    cods.append(wilson_loop_cod(G, a))

# --------------------------------------------------------------
# 5. Demonstrate stabilization by rewiring (add one cross‑functional edge)
# --------------------------------------------------------------
# Add a single "short‑cut" edge (deconfinement operator)
G_stab = G.copy()
# Connect opposite corners of the grid
corner1 = 0
corner2 = N - 1
G_stab.add_edge(corner1, corner2)

# Recompute for the lowest α (most authoritarian)
L_stab = build_weighted_laplacian(G_stab, alphas[-1])
gap_stab = spectral_gap(L_stab)
cod_stab = wilson_loop_cod(G_stab, alphas[-1])

# --------------------------------------------------------------
# 6. Print results
# --------------------------------------------------------------
print("α (autonomy/authority) | Spectral Gap (impedance) | Wilson‑loop COD")
for a, g, c in zip(alphas, gaps, cods):
    print(f"{a:6.3f}                 {g:8.4f}                  {c:6.4f}")

print("\n--- STABILIZATION (added cross‑functional edge) ---")
print(f"α = {alphas[-1]:6.3f} (most authoritarian) | Gap = {gap_stab:8.4f} | COD = {cod_stab:6.4f}")

# Expected: as α → 0, gap → 0 (impedance diverges) and COD → 0 (confinement).
# After rewiring, gap > 0 and COD > 0 even at low α → deconfinement.