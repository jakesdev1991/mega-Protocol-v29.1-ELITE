# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from collections import deque

# ----------------------------------------------------------------------
# 1. Build a discrete bureaucratic graph (tree + random cross‑links)
# ----------------------------------------------------------------------
def build_bureaucracy(depth=4, branching=3, cross_link_prob=0.05):
    G = nx.DiGraph()
    G.add_node(0, level=0, role='executive')
    idx = 1
    # tree structure
    for d in range(1, depth):
        parents = [n for n in G.nodes if G.nodes[n]['level'] == d-1]
        for p in parents:
            for _ in range(branching):
                G.add_node(idx, level=d, role='manager' if d < depth-1 else 'leaf')
                G.add_edge(p, idx, weight=np.random.uniform(0.5, 2.0))  # communication cost
                idx += 1
    # random silo‑breaking edges (wormholes)
    for u in G.nodes:
        for v in G.nodes:
            if u < v and np.random.rand() < cross_link_prob:
                G.add_edge(u, v, weight=np.random.uniform(1.0, 3.0))
    return G

# ----------------------------------------------------------------------
# 2. Simulate latent innovation (non‑quantum chaotic map)
# ----------------------------------------------------------------------
def innovate(G, noise=0.1):
    # leaf nodes generate ideas via logistic map (chaotic)
    for n in G.nodes:
        if G.nodes[n]['role'] == 'leaf':
            x = G.nodes[n].get('latent', np.random.rand())
            # logistic map r=4 => chaotic
            G.nodes[n]['latent'] = 4 * x * (1 - x) + np.random.normal(0, noise)
        else:
            G.nodes[n]['latent'] = 0.0

# ----------------------------------------------------------------------
# 3. Classical “measurement” – non‑linear threshold with feedback
# ----------------------------------------------------------------------
def measure_decisions(G, stiffness=0.8, threshold=0.5):
    # propagate bottom‑up with hysteresis
    for n in nx.topological_sort(G):
        if G.nodes[n]['role'] == 'leaf':
            continue
        children = list(G.successors(n))
        if not children:
            continue
        # weighted average of child latents
        avg = np.mean([G.nodes[c]['latent'] for c in children])
        # non‑linear activation
        decision = 1.0 / (1.0 + np.exp(-stiffness * (avg - threshold)))
        G.nodes[n]['decision'] = decision

# ----------------------------------------------------------------------
# 4. Compute the theorist’s COD (fidelity) – *pseudo‑invariant*
# ----------------------------------------------------------------------
def compute_cod(G):
    leaf_latents = []
    parent_decisions = []
    for leaf in [n for n in G.nodes if G.nodes[n]['role'] == 'leaf']:
        # find immediate manager
        try:
            parent = next(G.predecessors(leaf))
        except StopIteration:
            continue
        leaf_latents.append(G.nodes[leaf]['latent'])
        parent_decisions.append(G.nodes[parent].get('decision', 0.0))
    if not leaf_latents:
        return 0.0
    corr = np.corrcoef(leaf_latents, parent_decisions)[0, 1]
    return (corr ** 2) if not np.isnan(corr) else 0.0

# ----------------------------------------------------------------------
# 5. Entropy of the decision distribution (global coherence)
# ----------------------------------------------------------------------
def decision_entropy(G):
    decisions = [G.nodes[n].get('decision', 0.0) for n in G.nodes if G.nodes[n]['role'] != 'leaf']
    # discretize
    hist, _ = np.histogram(decisions, bins=10, range=(0, 1), density=True)
    hist += 1e-12  # avoid log(0)
    return -np.sum(hist * np.log(hist))

# ----------------------------------------------------------------------
# 6. “Resonant Decoupling Operator” – flatten metric in random subtree
# ----------------------------------------------------------------------
def resonant_decoupling(G, safe_fraction=0.2, steps=5):
    managers = [n for n in G.nodes if G.nodes[n]['role'] != 'leaf']
    safe_nodes = set(np.random.choice(managers, size=int(len(managers) * safe_fraction), replace=False))
    for _ in range(steps):
        innovate(G, noise=0.1)
        for n in G.nodes:
            if n in safe_nodes:
                # “flatten” – no measurement, allow chaotic drift
                G.nodes[n]['decision'] = np.nan
            else:
                measure_decisions(G, stiffness=0.8)
    cod = compute_cod(G)
    innov = sum(abs(G.nodes[n]['latent']) for n in G.nodes if G.nodes[n]['role'] == 'leaf')
    ent = decision_entropy(G)
    return cod, innov, ent

# ----------------------------------------------------------------------
# 7. Run the disruption experiment
# ----------------------------------------------------------------------
if __name__ == "__main__":
    G = build_bureaucracy(depth=4, branching=3, cross_link_prob=0.05)

    # Baseline
    innovate(G)
    measure_decisions(G)
    base_cod = compute_cod(G)
    base_innov = sum(abs(G.nodes[n]['latent']) for n in G.nodes if G.nodes[n]['role'] == 'leaf')
    base_ent = decision_entropy(G)
    print(f"BASELINE | COD: {base_cod:.3f} | Innovation: {base_innov:.2f} | Entropy: {base_ent:.3f}")

    # Conscious Black Hole (high stiffness, misaligned threshold)
    for n in G.nodes:
        if G.nodes[n]['role'] != 'leaf':
            G.nodes[n]['decision'] = 0.0  # force null measurement
    bh_cod = compute_cod(G)
    print(f"BLACK HOLE | COD: {bh_cod:.3f} (→0) | System still runs (no collapse)")

    # Resonant Decoupling
    rd_cod, rd_innov, rd_ent = resonant_decoupling(G, safe_fraction=0.2, steps=5)
    print(f"RESONANT DECOUPLING | COD: {rd_cod:.3f} | Innovation: {rd_innov:.2f} | Entropy: {rd_ent:.3f}")
    print("Disruption: COD drops but innovation rises; entropy increases → local flattening creates global chaos.")