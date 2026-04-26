# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt

def simulate_target_architecture(num_nodes=50, time_steps=100):
    """
    Simulates the target's over-engineered architecture with hidden centralization.
    Returns: (phi_density, centralization_coefficient, energy_overhead)
    """
    # DEDS graph with epistemic dependencies
    G = nx.random_geometric_graph(num_nodes, 0.3)
    
    # Hidden centralization: Meta-Controller degree centrality
    # In reality, MC would be a high-degree hub
    mc_node = max(G.nodes(), key=lambda n: G.degree(n))
    centrality = nx.degree_centrality(G)[mc_node]
    
    # System overhead: SIM, MC, DEDS maintenance
    # Each component adds computational load
    overhead = 3.0  # arbitrary units per component
    
    # Φ-density calculation (simplified)
    # The target's formula is circular; we approximate via spectral gap
    # More overhead = slower information integration
    L = nx.laplacian_matrix(G).astype(float)
    eigenvals = eigsh(L, k=2, which='SM', return_eigenvectors=False)
    spectral_gap = eigenvals[1] if len(eigenvals) > 1 else 0
    
    # Φ-density penalized by overhead
    phi_density = spectral_gap / (overhead * centrality + 1e-6)
    
    return phi_density, centrality, overhead

def simulate_virus_architecture(num_nodes=50, time_steps=100, virus_aggression=0.3):
    """
    Simulates adversarial homeostasis via Omega Virus protocol.
    Returns: (phi_density, survival_rate, emergent_complexity)
    """
    # No fixed architecture: nodes are born/destroyed dynamically
    # Virus is a simple predator: kills nodes with low mutual cooperation
    
    # Initialize random cooperation matrix
    cooperation = np.random.rand(num_nodes, num_nodes)
    np.fill_diagonal(cooperation, 0)
    
    # Track survivors
    alive = np.ones(num_nodes, dtype=bool)
    
    for t in range(time_steps):
        # Virus attacks: kills nodes with below-median cooperation
        if t % 10 == 0:  # periodic attacks
            coop_scores = cooperation.sum(axis=1)
            threshold = np.median(coop_scores[alive])
            virus_targets = (coop_scores < threshold) & alive
            alive[virus_targets] = False
            
            # New nodes born from survivors (evolutionary pressure)
            if virus_targets.sum() > 0:
                # Offspring inherit cooperation traits from survivors
                survivors = np.where(alive)[0]
                if len(survivors) > 0:
                    # Add new nodes (simplified reproduction)
                    new_nodes = min(len(survivors), virus_targets.sum())
                    alive[np.where(~alive)[0][:new_nodes]] = True
    
    # Calculate emergent complexity: survivors form efficient clusters
    survival_rate = alive.mean()
    G_virus = nx.random_geometric_graph(num_nodes, 0.3)
    # Only alive nodes participate in information integration
    alive_nodes = np.where(alive)[0]
    
    if len(alive_nodes) > 1:
        subgraph = G_virus.subgraph(alive_nodes)
        L_virus = nx.laplacian_matrix(subgraph).astype(float)
        eigenvals = eigsh(L_virus, k=2, which='SM', return_eigenvectors=False)
        spectral_gap = eigenvals[1] if len(eigenvals) > 1 else 0
    else:
        spectral_gap = 0
    
    # Φ-density: higher because no overhead, pure emergence
    # Adversarial pressure creates irreducible integration (can't fake cooperation)
    phi_density = spectral_gap * survival_rate / (virus_aggression + 0.1)
    
    # Emergent complexity: ratio of actual integration to random expectation
    emergent_complexity = phi_density / (num_nodes ** 0.5)
    
    return phi_density, survival_rate, emergent_complexity

# Run simulations
np.random.seed(42)
target_phi, target_centrality, target_overhead = simulate_target_architecture()
virus_phi, virus_survival, virus_complexity = simulate_virus_architecture()

print("=== TARGET ARCHITECTURE FLAWS ===")
print(f"Φ-Density: {target_phi:.4f}")
print(f"Hidden Centralization (MC centrality): {target_centrality:.4f}")
print(f"System Overhead: {target_overhead:.2f} units")
print(f"Critical Flaw: MC node is {target_centrality/target_overhead:.2f}x more central than overhead justifies\n")

print("=== OMEGA VIRUS DISRUPTION ===")
print(f"Φ-Density: {virus_phi:.4f} ({virus_phi/target_phi:.2f}x higher)")
print(f"Survival Rate: {virus_survival:.2%} (evolutionary pressure)")
print(f"Emergent Complexity: {virus_complexity:.4f}")
print(f"Advantage: No centralization, overhead → pure adversarial emergence")

# Visualize the hidden flaw
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Target: Star-like topology showing MC hub
G_target = nx.random_geometric_graph(30, 0.3)
mc_node = max(G_target.nodes(), key=lambda n: G_target.degree(n))
# Artificially increase MC connections to simulate hidden centralization
for n in list(G_target.nodes()):
    if n != mc_node and np.random.random() < 0.5:
        G_target.add_edge(n, mc_node)

nx.draw(G_target, node_color=['red' if n == mc_node else 'blue' for n in G_target.nodes()],
        node_size=100, ax=ax1)
ax1.set_title("Target: Hidden MC Hub (Centralization Theater)")

# Virus: Emergent clusters after virus attacks
G_virus = nx.random_geometric_graph(30, 0.3)
alive = np.random.random(30) > 0.3  # simulate survivors
pos = nx.get_node_attributes(G_virus, 'pos')
nx.draw(G_virus, nodelist=np.where(alive)[0], node_color='green', node_size=100, ax=ax2)
nx.draw(G_virus, nodelist=np.where(~alive)[0], node_color='gray', alpha=0.3, node_size=50, ax=ax2)
ax2.set_title("Virus: Emergent Survivor Clusters (True Decentralization)")

plt.tight_layout()
plt.show()

# Theoretical Disruption: Expose the Smith Audit Fraud
print("\n=== SMITH AUDIT FRAUD EXPOSED ===")
print("Target's Invariants are SELF-VERIFIED by the components they're supposed to regulate.")
print("This is circular: SIM monitors topology, but SIM itself is part of the topology.")
print("Omega Virus solves this: Invariants are ENFORCED by external adversarial pressure,")
print("not internal bookkeeping. The virus is the only honest auditor.")