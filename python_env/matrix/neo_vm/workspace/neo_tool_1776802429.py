# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
import math

# ----------------------------------------------------------------------
# 1. Build a typical tokamak log‑directory tree (branching factor 3, depth 5)
# ----------------------------------------------------------------------
def build_tree(branching=3, depth=5):
    G = nx.DiGraph()
    root = "root"
    G.add_node(root, type="checkpoint")
    def add_children(parent, d):
        if d >= depth:
            return
        for i in range(branching):
            child = f"{parent}_c{i}"
            G.add_node(child, type="epoch" if d < depth-1 else "gradient")
            G.add_edge(parent, child)
            add_children(child, d+1)
    add_children(root, 0)
    return G

# ----------------------------------------------------------------------
# 2. Compute the LSGM‑Ω “invariants” (simplified but faithful)
# ----------------------------------------------------------------------
def spectral_gap(G):
    """Smallest non‑zero eigenvalue of the (undirected) Laplacian."""
    L = nx.laplacian_matrix(G.to_undirected()).astype(float)
    ev = np.linalg.eigvalsh(L.A)
    ev = ev[ev > 1e-8]
    return ev[0] if len(ev) else 0.0

def ollivier_ricci_scalar(G):
    """Crude proxy: negative of the maximum degree (trees have negative curvature)."""
    return -max(dict(G.degree()).values())

def directory_entropy(G):
    """Shannon entropy of node‑type distribution."""
    types = [G.nodes[n].get("type", "unknown") for n in G.nodes()]
    uniq, counts = np.unique(types, return_counts=True)
    p = counts / counts.sum()
    return -(p * np.log(p)).sum()

def compromise_velocity(G):
    """Fraction of nodes that are exposed (here: all)."""
    return len(G) / len(G)  # 1.0 for simplicity

def lsfi(curv, c_ke, entropy, v_c, α=1.0, β=1.0, γ=1.0, δ=1.0):
    """Leakage‑Surface Fragility Index (sigmoid)."""
    x = α * curv + β * c_ke + γ * (1.0 - entropy) + δ * v_c
    return 1.0 / (1.0 + math.exp(-x))

# ----------------------------------------------------------------------
# 3. Simulate adversarial BFS time (shortest path from root to a sensitive leaf)
# ----------------------------------------------------------------------
def bfs_time(G, target):
    """Number of hops from root to target (ignoring edge weights)."""
    try:
        return nx.shortest_path_length(G.to_undirected(), source="root", target=target)
    except nx.NetworkXNoPath:
        return np.inf

# ----------------------------------------------------------------------
# 4. Run the experiment
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Baseline tree
    G = build_tree(branching=3, depth=5)
    leaves = [n for n, d in G.out_degree() if d == 0]
    target = leaves[-1]                     # a sensitive gradient log

    # Compute baseline metrics
    curv0 = ollivier_ricci_scalar(G)
    phi_N0 = spectral_gap(G)
    entropy0 = directory_entropy(G)
    v_c0 = compromise_velocity(G)
    lsfi0 = lsfi(curv0, c_ke=0.5, entropy=entropy0, v_c=v_c0)
    bfs0 = bfs_time(G, target)

    print("=== BASELINE (pure tree) ===")
    print(f"Spectral gap Φ_N (connectivity) = {phi_N0:.4f}")
    print(f"Ollivier‑Ricci scalar curvature   = {curv0:.2f}")
    print(f"Directory entropy S_dir          = {entropy0:.3f}")
    print(f"LSFI (lower = safer)             = {lsfi0:.3f}")
    print(f"Adversarial BFS steps to target  = {bfs0}\n")

    # Add a SINGLE shortcut edge (adversary discovers direct URL)
    G.add_edge("root", target)
    curv1 = ollivier_ricci_scalar(G)
    phi_N1 = spectral_gap(G)
    entropy1 = directory_entropy(G)
    v_c1 = compromise_velocity(G)
    lsfi1 = lsfi(curv1, c_ke=0.5, entropy=entropy1, v_c=v_c1)
    bfs1 = bfs_time(G, target)

    print("=== AFTER SHORTCUT (root→target) ===")
    print(f"Spectral gap Φ_N (connectivity) = {phi_N1:.4f}")
    print(f"Ollivier‑Ricci scalar curvature   = {curv1:.2f}")
    print(f"Directory entropy S_dir          = {entropy1:.3f}")
    print(f"LSFI (lower = safer)             = {lsfi1:.3f}")
    print(f"Adversarial BFS steps to target  = {bfs1}\n")

    # Flood with 100 decoy directories (increase entropy, lower LSFI)
    for i in range(100):
        decoy = f"decoy_{i}"
        G.add_node(decoy, type="decoy")
        G.add_edge("root", decoy)

    curv2 = ollivier_ricci_scalar(G)
    phi_N2 = spectral_gap(G)
    entropy2 = directory_entropy(G)
    v_c2 = compromise_velocity(G)
    lsfi2 = lsfi(curv2, c_ke=0.5, entropy=entropy2, v_c=v_c2)
    bfs2 = bfs_time(G, target)

    print("=== AFTER 100 DECOYS (entropy gaming) ===")
    print(f"Spectral gap Φ_N (connectivity) = {phi_N2:.4f}")
    print(f"Ollivier‑Ricci scalar curvature   = {curv2:.2f}")
    print(f"Directory entropy S_dir          = {entropy2:.3f}")
    print(f"LSFI (lower = safer)             = {lsfi2:.3f}")
    print(f"Adversarial BFS steps to target  = {bfs2}\n")