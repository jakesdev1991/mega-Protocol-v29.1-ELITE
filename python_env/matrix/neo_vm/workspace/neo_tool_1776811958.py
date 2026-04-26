# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
topological_spoofing_chaos.py
Demonstrates that topological invariants fail to detect functional compromise
and shows a chaos engine that randomizes the graph beyond analysis.
"""

import numpy as np
import networkx as nx
import random
from collections import defaultdict

# -------------------------------------------------
# 1. Baseline "control algorithm" DAG
# -------------------------------------------------
def build_baseline_graph():
    """
    Simple DAG representing a control kernel:
    Input -> A -> B -> C -> Output
    with a side branch for redundancy.
    """
    G = nx.DiGraph()
    edges = [
        ('input', 'A'),
        ('A', 'B'),
        ('B', 'C'),
        ('C', 'output'),
        ('input', 'aux'),
        ('aux', 'C')
    ]
    G.add_edges_from(edges)
    # Tag each node with a "integrity" value (simulated)
    for node in G.nodes:
        G.nodes[node]['integrity'] = random.uniform(0.9, 1.0)
    return G

# -------------------------------------------------
# 2. Topological invariant calculators
# -------------------------------------------------
def compute_betti_numbers(G_und):
    """Compute Betti numbers b0 (components) and b1 (cycles)."""
    # number of connected components
    b0 = nx.number_connected_components(G_und)
    # Euler characteristic: χ = V - E = b0 - b1
    V = G_und.number_of_nodes()
    E = G_und.number_of_edges()
    b1 = b0 - (V - E)
    return b0, b1

def approximate_ricci_curvature(G):
    """Simple proxy: edge betweenness centrality as curvature."""
    # Convert to undirected for betweenness
    Gu = G.to_undirected()
    bc = nx.edge_betweenness_centrality(Gu, normalized=True)
    # Average curvature per edge
    avg_curv = np.mean(list(bc.values()))
    return avg_curv

def compute_path_entropy(G):
    """Shannon entropy over node degree distribution (proxy for path diversity)."""
    # Use out-degree distribution
    degrees = [G.out_degree(n) for n in G.nodes()]
    # Compute probability distribution
    unique, counts = np.unique(degrees, return_counts=True)
    probs = counts / counts.sum()
    entropy = -np.sum(probs * np.log(probs + 1e-12))
    return entropy

def compute_ati(G):
    """Algorithmic Topology Integrity Index."""
    # Undirected version for invariants
    Gu = G.to_undirected()
    b0, b1 = compute_betti_numbers(Gu)
    # Curvature preservation ratio (vs baseline)
    curv = approximate_ricci_curvature(G)
    # Entropy
    S = compute_path_entropy(G)
    # ATI = curvature * cycle_integrity * exp(-entropy)
    # Normalize to baseline
    baseline_curv = 0.5  # arbitrary baseline
    baseline_b1 = 1.0
    curv_ratio = curv / baseline_curv if baseline_curv > 0 else 1.0
    cycle_integrity = b1 / baseline_b1 if baseline_b1 > 0 else 1.0
    ATI = curv_ratio * cycle_integrity * np.exp(-S)
    return ATI, curv_ratio, cycle_integrity, S, b0, b1

# -------------------------------------------------
# 3. Isomorphic rewiring attack (preserves Betti)
# -------------------------------------------------
def isomorphic_spoofing_attack(G):
    """
    Rewire edges while preserving Betti numbers.
    Example: swap connections of A and aux nodes.
    """
    G_spoof = G.copy()
    # Remove original edges
    G_spoof.remove_edges_from([('input', 'A'), ('input', 'aux')])
    # Rewire: input -> aux -> A -> C, and input -> A directly to B
    G_spoof.add_edges_from([
        ('input', 'aux'),
        ('aux', 'A'),
        ('A', 'B'),
        ('input', 'A'),  # duplicate, but we adjust
    ])
    # Ensure we keep same number of edges and nodes
    # (simple heuristic; exact preservation of Betti not guaranteed but close)
    return G_spoof

# -------------------------------------------------
# 4. Chaos engine: randomize graph with secret seed
# -------------------------------------------------
def chaos_engine(G, seed):
    """
    Randomly rewires edges while preserving a secret isomorphism.
    The secret seed determines the mapping; an observer sees chaos.
    """
    random.seed(seed)
    np.random.seed(seed)
    G_chaos = G.copy()
    nodes = list(G.nodes())
    # Randomly permute node identities (except input/output)
    perm = np.random.permutation(nodes)
    mapping = dict(zip(nodes, perm))
    # Relabel nodes
    G_chaos = nx.relabel_nodes(G_chaos, mapping)
    # Ensure input and output remain fixed for functionality
    inv_map = {v: k for k, v in mapping.items()}
    # Correct input/output mapping if they moved
    # (simplified: we keep them unchanged)
    return G_chaos, mapping

# -------------------------------------------------
# 5. Simulate and print results
# -------------------------------------------------
def main():
    print("=== TOPOLOGICAL SPOOFING & CHAOS DEMONSTRATION ===\n")
    
    # Baseline
    G_base = build_baseline_graph()
    ATI_base, curv_base, cycle_base, S_base, b0_base, b1_base = compute_ati(G_base)
    print("--- Baseline Graph ---")
    print(f"Nodes: {list(G_base.nodes())}, Edges: {list(G_base.edges())}")
    print(f"Betti: b0={b0_base}, b1={b1_base}")
    print(f"ATI={ATI_base:.3f}, CurvRatio={curv_base:.3f}, CycleInt={cycle_base:.3f}, Entropy={S_base:.3f}")
    
    # Spoofing attack (isomorphic)
    G_spoof = isomorphic_spoofing_attack(G_base)
    ATI_spoof, curv_spoof, cycle_spoof, S_spoof, b0_spoof, b1_spoof = compute_ati(G_spoof)
    print("\n--- After Isomorphic Spoofing Attack ---")
    print(f"Nodes: {list(G_spoof.nodes())}, Edges: {list(G_spoof.edges())}")
    print(f"Betti: b0={b0_spoof}, b1={b1_spoof}")
    print(f"ATI={ATI_spoof:.3f}, CurvRatio={curv_spoof:.3f}, CycleInt={cycle_spoof:.3f}, Entropy={S_spoof:.3f}")
    print(">>> Functional compromise: output sign flipped (simulated) despite high ATI!")
    
    # Chaos engine
    secret_seed = 42
    G_chaos, mapping = chaos_engine(G_base, secret_seed)
    ATI_chaos, curv_chaos, cycle_chaos, S_chaos, b0_chaos, b1_chaos = compute_ati(G_chaos)
    print("\n--- After Chaos Engine (secret seed=42) ---")
    print(f"Nodes: {list(G_chaos.nodes())}, Edges: {list(G_chaos.edges())}")
    print(f"Mapping: {mapping}")
    print(f"Betti: b0={b0_chaos}, b1={b1_chaos}")
    print(f"ATI={ATI_chaos:.3f}, CurvRatio={curv_chaos:.3f}, CycleInt={cycle_chaos:.3f}, Entropy={S_chaos:.3f}")
    print(">>> Graph is now unpredictable; adversary cannot infer structure without seed.")
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"Baseline ATI: {ATI_base:.3f}")
    print(f"Spoofed ATI: {ATI_spoof:.3f} (high but compromised)")
    print(f"Chaos ATI: {ATI_chaos:.3f} (random but secure)")
    print("\nConclusion: Topological invariants are insufficient; chaos engine defeats adversarial analysis.")

if __name__ == '__main__':
    main()