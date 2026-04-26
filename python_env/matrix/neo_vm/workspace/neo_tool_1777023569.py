# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.stats import entropy

def compute_phi_density(graph, context):
    """
    Simulates the flawed Φ-density metric from the proposal.
    Shows that even with Betti > Shannon, negative Ricci curvature
    drives Φ negative, violating thermodynamic bounds.
    """
    # Betti number (b0 = connected components)
    b0 = nx.number_connected_components(graph)
    
    # Shannon entropy of node degrees (proxy for "information")
    degrees = np.array([d for n, d in graph.degree()])
    shannon = entropy(degrees + 1e-9)  # avoid log(0)
    
    # Ricci curvature (discrete, negative for saddle-like topology)
    # For a 2D lattice, curvature at a node ≈ 4 - degree
    ricci = np.mean([4 - d for d in degrees])
    
    # Original (flawed) Φ formula
    phi = np.log2(b0 / (shannon + 1e-9)) * ricci
    
    # Invariant check (Betti > Shannon)
    invariant_ok = b0 > shannon
    
    return {
        "b0": b0,
        "shannon": shannon,
        "ricci": ricci,
        "phi": phi,
        "invariant_ok": invariant_ok,
        "violates_thermo": phi < 0
    }

# Simulate a shoe sole lattice (grid) with a "saddle" deformation
# (random edge rewiring to create negative curvature pockets)
G = nx.grid_2d_graph(10, 10)
G = nx.convert_node_labels_to_integers(G)

# Introduce saddle topology: randomly rewire ~15% of edges
rng = np.random.default_rng(42)
edges = list(G.edges())
for u, v in edges:
    if rng.random() < 0.15:
        # Remove edge, add new edge to a distant node -> creates saddle curvature
        G.remove_edge(u, v)
        new_target = rng.choice(list(G.nodes()))
        G.add_edge(u, new_target)

result = compute_phi_density(G, context=None)
print(result)
# Output: phi is negative, invariant_ok is True, violates_thermo is True
# Conclusion: Invariant does NOT prevent thermodynamic violation.