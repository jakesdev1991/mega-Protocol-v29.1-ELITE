# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import itertools
import random
from collections import defaultdict

# ──────────────────────────────────────────────────────────────────────────────
# Synthetic Narrative Hypergraph Generator
# ──────────────────────────────────────────────────────────────────────────────
def generate_narrative_timeline(T=30, shred_day=20, base_statements=50, conflict_rate=0.02):
    """
    T: total time steps (days)
    shred_day: day at which shredding consensus forms
    base_statements: number of base statements present each day
    conflict_rate: probability that a random pair of statements is contradictory
    Returns: list of daily conflict hypergraphs (each a set of frozenset hyperedges)
    """
    timeline = []
    for t in range(T):
        # Number of statements grows as decision pressure increases
        n_stmts = base_statements + int(5 * max(0, (t - shred_day + 5))) if t >= shred_day - 5 else base_statements
        statements = [f"stmt_{i}" for i in range(n_stmts)]
        # Randomly generate conflicting triples (minimal inconsistent sets)
        conflicts = set()
        if t >= shred_day - 5:  # stress window: increase conflict density
            rate = conflict_rate * 3
        else:
            rate = conflict_rate
        for a, b, c in itertools.combinations(statements, 3):
            if random.random() < rate:
                conflicts.add(frozenset({a, b, c}))
        timeline.append(conflicts)
    return timeline

# ──────────────────────────────────────────────────────────────────────────────
# Homology Computation (simplified: count cycles in conflict graph)
# ──────────────────────────────────────────────────────────────────────────────
def conflict_graph(conflicts):
    """
    Build a graph where nodes are statements and edges connect any two statements
    that appear together in a conflicting triple.
    """
    graph = defaultdict(set)
    for triple in conflicts:
        for u, v in itertools.combinations(triple, 2):
            graph[u].add(v)
            graph[v].add(u)
    return graph

def betti2_estimate(graph):
    """
    Approximate β₂ (2‑dimensional holes) by counting the number of
    independent 3‑cliques that are not filled by a 4‑clique.
    For speed, we use a simple cycle count heuristic.
    """
    nodes = list(graph.keys())
    # Count triangles (3‑cliques)
    triangles = 0
    for a, b, c in itertools.combinations(nodes, 3):
        if b in graph[a] and c in graph[a] and c in graph[b]:
            triangles += 1
    # Rough proxy: β₂ ≈ triangles - (some fill threshold)
    # In a real implementation, persistent homology would be used.
    return max(0, triangles - len(nodes))

def combinatorial_entropy(conflicts, k=3):
    """
    H_c = log(number of minimal inconsistent sets of size ≤ k)
    Here k=3, so we simply count the triples.
    """
    return np.log(1 + len(conflicts))

# ──────────────────────────────────────────────────────────────────────────────
# Simulate and Detect
# ──────────────────────────────────────────────────────────────────────────────
timeline = generate_narrative_timeline(T=30, shred_day=20)
beta2_series = []
entropy_series = []

for day, conflicts in enumerate(timeline):
    g = conflict_graph(conflicts)
    beta2 = betti2_estimate(g)
    Hc = combinatorial_entropy(conflicts)
    beta2_series.append(beta2)
    entropy_series.append(Hc)
    print(f"Day {day:2d} | β₂ ≈ {beta2:4.0f} | H_c = {Hc:.2f}")

# ──────────────────────────────────────────────────────────────────────────────
# Early‑warning heuristic: trigger when both signals spike
# ──────────────────────────────────────────────────────────────────────────────
beta2_arr = np.array(beta2_series)
entropy_arr = np.array(entropy_series)

# Z‑score normalization
z_beta2 = (beta2_arr - beta2_arr.mean()) / beta2_arr.std()
z_entropy = (entropy_arr - entropy_arr.mean()) / entropy_arr.std()

alert = (z_beta2 > 2.0) & (z_entropy > 1.5)
alert_days = np.where(alert)[0]
print("\n🚨 Early‑warning alerts on days:", alert_days)

# Expected: alerts should appear shortly before day 20