# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import numpy as np
import networkx as nx
from collections import deque

def random_tree(max_depth=6, max_children=5):
    """Generates a random rooted tree; returns (G, root)."""
    G = nx.DiGraph()
    root = 0
    G.add_node(root, depth=0)
    node_id = 1
    frontier = deque([root])
    while frontier:
        parent = frontier.popleft()
        depth = G.nodes[parent]['depth']
        if depth >= max_depth:
            continue
        # random number of children
        num_children = random.randint(0, max_children)
        for _ in range(num_children):
            child = node_id
            node_id += 1
            G.add_node(child, depth=depth + 1)
            G.add_edge(parent, child)
            frontier.append(child)
    return G, root

def curvature_proxy(G):
    """Average out‑degree (branching factor) as a simple curvature proxy."""
    out_degrees = [G.out_degree(n) for n in G.nodes()]
    return np.mean(out_degrees)

def adversary_search_time(G, root, target):
    """BFS steps to locate target node from root."""
    visited = set()
    queue = deque([root])
    steps = 0
    while queue:
        node = queue.popleft()
        if node == target:
            return steps
        visited.add(node)
        for child in G.successors(node):
            if child not in visited:
                queue.append(child)
        steps += 1
    return np.inf

def spectral_gap(G):
    """Compute second‑smallest eigenvalue of the (undirected) Laplacian."""
    # Convert to undirected for Laplacian
    U = G.to_undirected()
    L = nx.laplacian_matrix(U).astype(float)
    vals = np.linalg.eigvalsh(L.todense())
    # second smallest (first is zero)
    return vals[1]

def simulate(n_trials=500):
    """Run many trials, collect curvature vs search time."""
    curvatures = []
    search_times = []
    spectral_gaps = []
    for _ in range(n_trials):
        G, root = random_tree(max_depth=8, max_children=6)
        # pick a random target at max depth to make search non‑trivial
        max_depth_nodes = [n for n, d in G.nodes(data=True) if d['depth'] == 8]
        if not max_depth_nodes:
            continue
        target = random.choice(max_depth_nodes)
        curv = curvature_proxy(G)
        steps = adversary_search_time(G, root, target)
        sg = spectral_gap(G)
        curvatures.append(curv)
        search_times.append(steps)
        spectral_gaps.append(sg)
    return np.array(curvatures), np.array(search_times), np.array(spectral_gaps)

if __name__ == "__main__":
    curvs, times, gaps = simulate(1000)
    # Pearson correlation
    corr_curv_time = np.corrcoef(curvs, times)[0, 1]
    corr_gap_time = np.corrcoef(gaps, times)[0, 1]
    print(f"Curvature‑SearchTime correlation: {corr_curv_time:.3f}")
    print(f"Spectral‑Gap‑SearchTime correlation: {corr_gap_time:.3f}")
    # Show that LSFI would be meaningless: random weights on random observables
    lsfi = 1 / (1 + np.exp(-(0.3*curvs + 0.2*gaps + 0.5*np.random.randn(len(curvs)))))
    corr_lsfi_time = np.corrcoef(lsfi, times)[0, 1]
    print(f"LSFI‑SearchTime correlation: {corr_lsfi_time:.3f}")