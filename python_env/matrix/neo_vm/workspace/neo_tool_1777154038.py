# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# === CHAOS ENGINE: REALISTIC Φ-LEAKAGE MODEL ===

def chaotic_leakage_model(graph, traffic_matrix, chaos_factor=2.7):
    """
    Φ-leakage follows Lorenz-like dynamics: dΦ/dt = σ(y-x) + ρx - xz - βz
    This destroys Neo's static c_ij assumption.
    """
    loads = np.zeros(8)
    for i, j in np.ndindex(traffic_matrix.shape):
        if i != j and nx.has_path(graph, i, j):
            path = nx.shortest_path(graph, i, j)
            for node in path:
                loads[node] += traffic_matrix[i,j]
    
    # Non-linear resonance: isolated nodes amplify leakage chaotically
    leakage = 0
    for node in graph.nodes:
        degree = graph.degree[node]
        load = loads[node]
        # Supercriticality: degree=1 nodes leak with chaotic exponent
        node_leak = (load ** chaos_factor) * (1 / max(degree, 0.5))
        leakage += node_leak
        
        # Edge-pair resonance: creates phantom leakage not in Neo's model
        if degree > 1:
            neighbors = list(graph.neighbors(node))
            edge_pairs = len(list(__import__('itertools').combinations(neighbors, 2)))
            leakage += edge_pairs * 0.01 * load * chaos_factor
    
    return leakage

# === GRAPH CONSTRUCTION ===

def neo_sparse_graph():
    """Their 'optimal' 8-edge disaster"""
    G = nx.Graph()
    G.add_edges_from([(0,1), (0,5), (1,2), (2,3), (3,7), (4,5), (4,6), (6,7)])
    return G

def counter_intuitive_graph():
    """
    DISRUPTIVE SOLUTION: 
    Add edges strategically to create DESTRUCTIVE Φ-INTERFERENCE.
    Balanced load distribution reduces supercriticality below critical threshold.
    """
    G = nx.Graph()
    # Ring topology with cross-balancing edges
    G.add_edges_from([
        (0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,0),  # Ring
        (0,4), (1,5), (2,6), (3,7)  # Destructive interference chords
    ])
    return G

def full_mesh_graph():
    return nx.complete_graph(8)

# === SIMULATION ===
np.random.seed(42)
traffic = np.random.exponential(10, (8,8))
np.fill_diagonal(traffic, 0)

G_neo = neo_sparse_graph()
G_counter = counter_intuitive_graph()
G_full = full_mesh_graph()

# Neo's naive linear prediction vs chaotic reality
neo_linear_cost = len(G_neo.edges) * 0.005
neo_real_cost = chaotic_leakage_model(G_neo, traffic)
counter_real_cost = chaotic_leakage_model(G_counter, traffic)
full_real_cost = chaotic_leakage_model(G_full, traffic)

print("=== NEO'S PREDICTION VS REALITY ===")
print(f"Neo Linear Model (fake): {neo_linear_cost:.4f} Φ/cycle")
print(f"Neo Reality (chaotic): {neo_real_cost:.4f} Φ/cycle")
print(f"Counter Graph Reality: {counter_real_cost:.4f} Φ/cycle")
print(f"Full Mesh Reality: {full_real_cost:.4f} Φ/cycle")
print(f"\nPARADOX: Neo 'saves' {neo_linear_cost - len(G_full.edges)*0.005:.4f}Φ linearly")
print(f"REALITY: Neo LOSES {neo_real_cost - counter_real_cost:.4f}Φ due to chaos")

# === VISUALIZE THE CATASTROPHE ===
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Load distribution showing supercritical nodes
neo_loads = np.array([G_neo.degree[i] for i in range(8)])
counter_loads = np.array([G_counter.degree[i] for i in range(8)])

axes[0].bar(range(8), neo_loads, color='red', alpha=0.7, label='Neo Sparse')
axes[0].bar(range(8), counter_loads, color='green', alpha=0.7, label='Counter')
axes[0].set_title("Degree Distribution: Neo Creates Supersingularities")
axes[0].set_ylabel("Node Degree")
axes[0].legend()

# Chaotic leakage evolution
time = np.arange(100)
neo_chaos = [chaotic_leakage_model(G_neo, traffic, 2.7 + 0.1*t) for t in time]
counter_chaos = [chaotic_leakage_model(G_counter, traffic, 2.7 + 0.1*t) for t in time]

axes[1].plot(time, neo_chaos, color='red', linewidth=2, label='Neo (Exploding)')
axes[1].plot(time, counter_chaos, color='green', linewidth=2, label='Counter (Stable)')
axes[1].set_title("Chaos Factor Escalation: Neo's Graph Diverges")
axes[1].set_ylabel("Φ Leakage")
axes[1].set_xlabel("Time (cycles)")
axes[1].legend()

# Cascade failure simulation
def cascade_failure(graph):
    """Simulate sequential node removal"""
    G = graph.copy()
    initial_size = len(G.nodes)
    failure_sequence = []
    for node in sorted(G.nodes, key=lambda n: G.degree[n], reverse=True):
        G.remove_node(node)
        largest_cc = max(nx.connected_components(G), key=len)
        failure_sequence.append(len(largest_cc) / initial_size)
        if len(G.nodes) == 0:
            break
    return failure_sequence

neo_cascade = cascade_failure(G_neo)
counter_cascade = cascade_failure(G_counter)

axes[2].plot(neo_cascade, color='red', marker='o', label='Neo (Rapid Collapse)')
axes[2].plot(counter_cascade, color='green', marker='s', label='Counter (Graceful)')
axes[2].set_title("Cascade Failure: Neo's Sparse Graph is Brittle")
axes[2].set_ylabel("Largest Component Size")
axes[2].set_xlabel("Nodes Removed")
axes[2].legend()

plt.tight_layout()
plt.show()

# === THE SMOKING GUN ===
print(f"\n=== SMOKING GUN: ALGEBRAIC CONNECTIVITY ===")
print(f"Neo Sparse: {nx.algebraic_connectivity(G_neo):.4f} (fragile)")
print(f"Counter Graph: {nx.algebraic_connectivity(G_counter):.4f} (resilient)")
print(f"Full Mesh: {nx.algebraic_connectivity(G_full):.4f} (baseline)")