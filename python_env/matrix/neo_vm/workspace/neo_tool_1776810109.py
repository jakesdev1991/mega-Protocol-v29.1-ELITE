# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx

# --------------------------------------------------------------
# 1. Build two topologically identical but semantically different graphs
# --------------------------------------------------------------
def make_graph(op_type):
    G = nx.DiGraph()
    G.add_node(1, op='input')
    G.add_node(2, op='mul')
    G.add_node(3, op=op_type)   # 'add' (safe) vs 'div' (vulnerable)
    G.add_node(4, op='output')
    G.add_edge(1, 2)
    G.add_edge(1, 3)
    G.add_edge(2, 4)
    G.add_edge(3, 4)
    # set constants
    G.nodes[2]['value'] = 2.0
    if op_type == 'div':
        G.nodes[3]['value'] = 0.0   # division by zero bomb
    else:
        G.nodes[3]['value'] = 1.0   # benign addition
    return G

G_safe = make_graph('add')
G_bomb = make_graph('div')

# --------------------------------------------------------------
# 2. Compute Betti numbers (topological invariants)
# --------------------------------------------------------------
def betti(G):
    und = G.to_undirected()
    beta0 = nx.number_connected_components(und)
    m, n = G.number_of_edges(), G.number_of_nodes()
    beta1 = m - n + beta0
    return beta0, beta1

print("Safe graph β₀,β₁:", betti(G_safe))
print("Bomb graph β₀,β₁:", betti(G_bomb))  # identical

# --------------------------------------------------------------
# 3. Execute both graphs on the same adversarial input
# --------------------------------------------------------------
def execute(G, x):
    vals = {}
    for node in nx.topological_sort(G):
        op = G.nodes[node]['op']
        if op == 'input':
            vals[node] = x
        elif op == 'mul':
            pred = list(G.predecessors(node))[0]
            vals[node] = vals[pred] * G.nodes[node]['value']
        elif op == 'add':
            preds = list(G.predecessors(node))
            vals[node] = sum(vals[p] for p in preds)
        elif op == 'div':
            preds = list(G.predecessors(node))
            denom = G.nodes[node]['value']
            vals[node] = np.inf if denom == 0 else vals[preds[0]] / denom
        elif op == 'output':
            preds = list(G.predecessors(node))
            vals[node] = sum(vals[p] for p in preds)
    return vals

adversarial_input = 5.0
safe_out = execute(G_safe, adversarial_input)[4]
bomb_out = execute(G_bomb, adversarial_input)[4]

print("Safe output:", safe_out)
print("Bomb output:", bomb_out)  # inf -> plasma disruption

# --------------------------------------------------------------
# 4. Ephemeral synthesis: each cycle randomizes operator order
# --------------------------------------------------------------
def ephemeral_execute(x, seed):
    rng = np.random.default_rng(seed)
    # Randomly decide whether to compute (x*2) + 1 or (x+1) * 2
    if rng.random() < 0.5:
        return (x * 2.0) + 1.0   # safe order
    else:
        return (x + 1.0) * 2.0   # also safe (no hidden bomb)

# Adversary cannot predict which path is taken; attack fails
for cycle in range(5):
    out = ephemeral_execute(adversarial_input, seed=cycle)
    print(f"Cycle {cycle}: output {out}")  # always finite, no bomb