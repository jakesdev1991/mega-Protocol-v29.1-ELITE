# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
SOUL-N Invariant Validator (Omega Protocol)
-------------------------------------------
Checks the three Absolute Invariants (Φ-1, Φ-2, Φ-3) for a given
state of the Self-Optimizing Urban Logistics Nexus.

Assumptions (all quantities are in normalized units):
    - Speed of light c = 1.
    - Baseline entropy H0 is known from a pre‑optimisation run.
    - The logistics mesh is represented as an undirected graph
      (networkx.Graph) where nodes = vehicles, edges = active
      low‑latency links.
    - Metric tensor g is a 4x4 numpy array (logistics‑environment
      spacetime) expressed in the local basis.
"""

import numpy as np
import networkx as nx
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
import itertools

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def metric_non_degenerate(g: np.ndarray, eps: float = 1e-6) -> bool:
    """
    TOE Step 9: det(g) != 0.
    Returns True if |det(g)| > eps.
    """
    det = np.linalg.det(g)
    return abs(det) > eps

def causal_fidelity(route_updates: list, dt: float, c: float = 1.0) -> bool:
    """
    Φ-1: No information may propagate faster than c.
    route_updates: list of (src_node, dst_node, distance) tuples
                   representing a routing decision that was applied
                   during the last control interval dt.
    """
    for src, dst, dist in route_updates:
        # Minimum time needed for a signal to travel dist at speed c
        min_time = dist / c
        if dt < min_time:          # decision applied too quickly → superluminal
            return False
    return True

def entropy_increase(H0: float, H1: float, max_frac: float = 0.025) -> bool:
    """
    Φ-2: Informational mass conservation.
    Allows at most max_frac (default 2.5 %) relative increase.
    """
    if H0 == 0:
        # Avoid division by zero; if baseline entropy is zero,
        # any increase is a violation.
        return H1 == 0
    return (H1 - H0) / H0 <= max_frac

def betti_numbers(graph: nx.Graph, max_dim: int = 3):
    """
    Compute Betti numbers β₀..β_max_dim for an undirected graph
    using simplicial homology of the clique complex (flag complex).
    For a 3‑torus we expect [1, 3, 3, 1].
    """
    # Build the flag complex up to dimension max_dim
    simplices = []
    # 0-simplices (vertices)
    simplices.extend([(v,) for v in graph.nodes()])
    # 1-simplices (edges)
    simplices.extend(tuple(sorted(e)) for e in graph.edges())
    # Higher‑dim simplices: all cliques of size k+1
    for k in range(2, max_dim + 1):          # k = dimension of simplex
        # Find all (k+1)-cliques via brute force (ok for small graphs)
        nodes = list(graph.nodes())
        for combo in itertools.combinations(nodes, k + 1):
            sub = graph.subgraph(combo)
            if sub.number_of_edges() == (k + 1) * k // 2:  # clique test
                simplices.append(tuple(sorted(combo)))
    # Convert to boundary matrices
    def simplex_index(s):
        return simplex_to_index[s]

    # Map each simplex to a unique index
    simplex_to_index = {s: i for i, s in enumerate(simplices)}
    n_simplices = len(simplices)

    # Build boundary matrices ∂_k: C_k -> C_{k-1}
    boundaries = [None] * (max_dim + 1)   # boundaries[k] corresponds to ∂_k
    for k in range(1, max_dim + 1):
        rows, cols, data = [], [], []
        for idx, simplex in enumerate(simplices):
            if len(simplex) == k + 1:   # a k-simplex
                # Its boundary consists of (k)-faces obtained by omitting one vertex
                for i, v in enumerate(simplex):
                    face = simplex[:i] + simplex[i+1:]
                    face_idx = simplex_to_index[face]
                    # Alternating sign
                    sign = -1 if i % 2 else 1
                    rows.append(face_idx)
                    cols.append(idx)
                    data.append(sign)
        boundaries[k] = csr_matrix((data, (rows, cols)),
                                   shape=(n_simplices, n_simplices))
    # ∂_0 is zero matrix
    boundaries[0] = csr_matrix((n_simplices, n_simplices))

    # Compute rank of each boundary matrix to get Betti numbers via
    # β_k = rank(Z_k) - rank(B_k) = (n_k - rank(∂_{k+1})) - rank(∂_k)
    betti = []
    n_k = [sum(1 for s in simplices if len(s) == k+1) for k in range(max_dim+1)]
    for k in range(max_dim+1):
        rank_kp1 = boundaries[k+1].rank() if k+1 <= max_dim else 0
        rank_k   = boundaries[k].rank()
        beta = (n_k[k] - rank_kp1) - rank_k
        betti.append(int(beta))
    return betti

def topological_integrity(graph: nx.Graph) -> bool:
    """
    Φ-3: Logistics mesh must be homotopy-equivalent to a 3‑torus.
    """
    expected = [1, 3, 3, 1]   # β₀, β₁, β₂, β₃ for T³
    actual = betti_numbers(graph, max_dim=3)
    return actual == expected

# ----------------------------------------------------------------------
# Example validation routine (replace with real telemetry)
# ----------------------------------------------------------------------
def validate_soul_n_state(
    g: np.ndarray,
    route_updates: list,
    dt: float,
    H0: float,
    H1: float,
    logistics_graph: nx.Graph
) -> dict:
    """
    Run all three invariant checks and return a report.
    """
    report = {}

    # Φ-0: Metric non-degeneracy (TOE Step 9) – prerequisite
    report["metric_non_degenerate"] = metric_non_degenerate(g)
    if not report["metric_non_degenerate"]:
        report["violation"] = "Metric degeneracy detected (det(g)≈0)."

    # Φ-1: Causal fidelity
    report["causal_fidelity"] = causal_fidelity(route_updates, dt)

    # Φ-2: Entropy bound
    report["entropy_increase_ok"] = entropy_increase(H0, H1)

    # Φ-3: Topological integrity
    report["topological_integrity"] = topological_integrity(logistics_graph)

    # Overall compliance
    report["overall_pass"] = all([
        report["metric_non_degenerate"],
        report["causal_fidelity"],
        report["entropy_increase_ok"],
        report["topological_integrity"]
    ])

    return report

# ----------------------------------------------------------------------
# Demo with synthetic data (for illustration only)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Metric tensor: a small perturbation of Minkowski η = diag(-1,1,1,1)
    g = np.array([[-1.0, 0.0, 0.0, 0.0],
                  [0.0,  1.0, 0.0, 0.0],
                  [0.0,  0.0, 1.0, 0.0],
                  [0.0,  0.0, 0.0, 1.0]])   # det = -1 → non‑degenerate

    # 2. Route updates applied in the last dt seconds
    #    (src, dst, distance) – distances are in normalized length units
    dt = 0.1   # 100 ms control cycle
    route_updates = [
        (0, 1, 0.05),   # 5 cm → min time 0.05 s  (< dt? no, 0.05 < 0.1 → OK)
        (2, 3, 0.12),   # 12 cm → min time 0.12 s (> dt) → would violate Φ-1
    ]

    # 3. Entropy values (Shannon, bits)
    H0 = 2.0   # baseline uncertainty
    H1 = 2.04  # after optimisation → 2 % increase

    # 4. Logistics mesh: a simple 3‑torus lattice (2×2×2 periodic)
    #    We construct a graph whose clique complex yields β = [1,3,3,1]
    #    For brevity we use a known 3‑torus triangulation (6 vertices).
    #    This is a placeholder; real LEM would feed its actual graph.
    G = nx.Graph()
    # vertices of a 2×2×2 torus with periodic identification
    coords = list(itertools.product([0,1], repeat=3))
    for i, v in enumerate(coords):
        G.add_node(i, pos=v)
    # edges: connect nearest neighbours (6 directions) with wrap‑around
    for i, (x,y,z) in enumerate(coords):
        for dx,dy,dz in [(1,0,0),(0,1,0),(0,0,1)]:
            nb = ((x+dx)%2, (y+dy)%2, (z+dz)%2)
            j = coords.index(nb)
            G.add_edge(i, j)

    # Run validation
    result = validate_soul_n_state(
        g=g,
        route_updates=route_updates,
        dt=dt,
        H0=H0,
        H1=H1,
        logistics_graph=G
    )

    print("=== SOUL‑N Invariant Validation Report ===")
    for k, v in result.items():
        print(f"{k:30}: {v}")