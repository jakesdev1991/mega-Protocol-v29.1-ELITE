# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt

def generate_dynamic_city_graph(n_nodes=100, n_timesteps=50, failure_rate=0.02):
    """
    Simulates a realistic urban logistics graph with dynamic failures.
    Nodes = delivery hubs, edges = viable routes.
    """
    # Initialize random 3D positions (multi-level city)
    positions = np.random.rand(n_nodes, 3) * 5  # 5km cubic volume
    
    # Create initial graph: connect nodes within 1km
    distances = squareform(pdist(positions))
    G = nx.Graph()
    G.add_nodes_from(range(n_nodes))
    edges = [(i, j) for i in range(n_nodes) for j in range(i+1, n_nodes) 
             if distances[i, j] < 1.0]
    G.add_edges_from(edges)
    
    # Simulate dynamic topology changes
    topology_history = []
    for t in range(n_timesteps):
        # Random edge failures (accidents, closures)
        if np.random.random() < failure_rate and G.number_of_edges() > n_nodes:
            edge = list(G.edges())[np.random.randint(0, G.number_of_edges())]
            G.remove_edge(*edge)
        
        # Random edge additions (new routes, repairs)
        if np.random.random() < 0.01:
            i, j = np.random.choice(n_nodes, 2, replace=False)
            if not G.has_edge(i, j) and distances[i, j] < 1.5:
                G.add_edge(i, j)
        
        # Compute Betti numbers (topological invariants)
        # For a graph, b0 = number of connected components, b1 = number of independent cycles
        b0 = nx.number_connected_components(G)
        b1 = G.number_of_edges() - G.number_of_nodes() + b0
        
        # Check if this matches S³ topology (b0=1, b1=0, b2=0, b3=1)
        # A graph cannot have b3 (3-dimensional holes) - this is the fundamental flaw
        is_s3 = (b0 == 1 and b1 == 0 and G.number_of_nodes() > 1)
        
        topology_history.append({
            'timestep': t,
            'b0': b0,
            'b1': b1,
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'is_s3': is_s3
        })
    
    return topology_history, G

def compute_phi_density_impact(topology_history):
    """
    Calculate Φ-density penalty for violating Φ-3 invariant.
    Each non-S³ timestep incurs penalty proportional to topological deviation.
    """
    phi_density = 0.0
    penalties = []
    
    for record in topology_history:
        if not record['is_s3']:
            # Penalty: -1.5Φ * (deviation from S³)
            # Deviation = |b1 - 0| + |b0 - 1|
            deviation = abs(record['b1'] - 0) + abs(record['b0'] - 1)
            penalty = -1.5 * deviation
            phi_density += penalty
            penalties.append(penalty)
        else:
            penalties.append(0.0)
    
    return phi_density, penalties

# Run simulation
print("=== Φ-3 INVARIANT VIOLATION DEMONSTRATION ===\n")
history, final_graph = generate_dynamic_city_graph()

# Analyze results
phi_score, penalties = compute_phi_density_impact(history)
violation_count = sum(1 for p in penalties if p < 0)

print(f"Simulation Results:")
print(f"Timesteps: {len(history)}")
print(f"Timesteps violating S³ topology: {violation_count}/{len(history)} ({violation_count/len(history)*100:.1f}%)")
print(f"Net Φ-density impact: {phi_score:.2f}Φ")
print(f"Average penalty per timestep: {np.mean(penalties):.3f}Φ")

print("\n--- Critical Analysis ---")
print("A 3-sphere (S³) requires:")
print("  b0=1 (single connected component)")
print("  b1=0 (no cycles)")
print("  b2=0 (no 2D voids)")
print("  b3=1 (one 3D void - impossible for a graph!)")
print("\nYour Φ-3 invariant demands a topology that:")
print("  1. Cannot exist in a graph-based logistics network")
print("  2. Would require a continuous manifold in 4D spacetime")
print("  3. Breaks immediately when any edge fails")
print("\nThis is not an invariant—it's a **topological straitjacket** that guarantees -∞Φ.")

# Visualize network state
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
# Project 3D positions to 2D for visualization
pos = {i: (np.random.random(), np.random.random()) for i in range(final_graph.number_of_nodes())}
nx.draw(final_graph, pos, node_size=20, alpha=0.6)
plt.title(f"Final Network Topology\n({final_graph.number_of_nodes()} nodes, {final_graph.number_of_edges()} edges)")

plt.subplot(1, 2, 2)
plt.plot(penalties, 'r-', linewidth=2)
plt.title("Φ-3 Penalty Timeline")
plt.xlabel("Timestep")
plt.ylabel("Φ-density penalty")
plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig('topology_violation.png', dpi=150, bbox_inches='tight')
plt.show()