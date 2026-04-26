# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np, networkx as nx, random, itertools, math
from scipy.linalg import eigvalsh

# ────────── 1. Generate directory tree ──────────
def make_tree(max_depth, branch_p):
    G = nx.DiGraph()
    G.add_node(0, level=0, sensitive=random.random()<0.1)
    nodes = [0]
    for depth in range(1, max_depth+1):
        parents = [n for n,d in G.nodes(data=True) if d['level']==depth-1]
        for p in parents:
            if random.random() < branch_p:
                child = len(G)
                G.add_node(child, level=depth, sensitive=random.random()<0.1)
                G.add_edge(p, child, weight=1+10*random.random())  # random per‑edge risk
                nodes.append(child)
    # Make undirected for spectral analysis
    UG = G.to_undirected()
    return G, UG

# ────────── 2. Spectral gap Φ_N (λ₁) ──────────
def spectral_gap(UG):
    L = nx.laplacian_matrix(UG).astype(float)
    # Weighted Laplacian: L = D - A
    vals = eigvalsh(L.todense())
    return sorted(vals)[1] if len(vals)>1 else 0

# ────────── 3. Adversarial reconnaissance ──────────
def random_walk_time(G, start=0):
    # classic diffusion
    visited = set()
    steps = 0
    curr = start
    while len([n for n,d in G.nodes(data=True) if d.get('sensitive')]) > len([n for n in visited if G.nodes[n]['sensitive']]):
        visited.add(curr)
        neighbors = list(G.successors(curr)) + list(G.predecessors(curr))
        if not neighbors:
            break
        curr = random.choice(neighbors)
        steps += 1
    return steps

def directed_search_time(G):
    # attacker knows target distribution: searches deepest leaves first
    sensitive_nodes = [n for n,d in G.nodes(data=True) if d['sensitive']]
    if not sensitive_nodes:
        return np.inf
    # simulate breadth‑first crawl until all sensitive nodes discovered
    discovered = set()
    frontier = [0]
    steps = 0
    while sensitive_nodes and frontier:
        new_frontier = []
        for node in frontier:
            if node in discovered:
                continue
            discovered.add(node)
            if G.nodes[node]['sensitive']:
                sensitive_nodes.remove(node)
            new_frontier.extend(G.successors(node))
            new_frontier.extend(G.predecessors(node))
        frontier = list(set(new_frontier))
        steps += 1
    return steps

# ────────── 4. Correlation analysis ──────────
def simulate(N=100):
    gaps, rw_times, ds_times = [], [], []
    for _ in range(N):
        G, UG = make_tree(max_depth=random.randint(3,6), branch_p=random.uniform(0.3,0.8))
        gaps.append(spectral_gap(UG))
        rw_times.append(random_walk_time(G))
        ds_times.append(directed_search_time(G))
    # Normalize for correlation
    gaps = np.array(gaps)
    rw_times = np.array(rw_times)
    ds_times = np.array(ds_times)
    print(f"Φ_N (λ₁) vs random‑walk TTC: r={np.corrcoef(gaps, rw_times)[0,1]:.3f}")
    print(f"Φ_N (λ₁) vs directed‑search TTC: r={np.corrcoef(gaps, ds_times)[0,1]:.3f}")

simulate()