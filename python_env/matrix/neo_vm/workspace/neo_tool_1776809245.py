# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import powerlaw
import networkx as nx

def simulate_cascade_native_market(n_participants=500, n_steps=5000, 
                                   leak_probability=0.02, criticality_param=2.1):
    """
    Simulates market as cascade-native substrate where cascades are the 
    fundamental computational element, not anomalies to be suppressed.
    This breaks the containment paradigm entirely.
    """
    
    # Initialize participants as dynamical strategies, not fixed types
    # Each participant has: complexity, stress threshold, adaptability
    strategies = np.random.random((n_participants, 3))
    strategies[:, 1] = 0.5 + 0.3 * strategies[:, 1]  # Threshold in [0.5, 0.8]
    strategies[:, 2] = 0.1 + 0.4 * strategies[:, 2]   # Adaptability in [0.1, 0.5]
    
    # Scale-free interaction network (prefential attachment = cascade topology)
    G = nx.barabasi_albert_graph(n_participants, m=3)
    adjacency = nx.to_numpy_array(G)
    
    # Track cascade dynamics
    cascade_sizes = []
    phi_density = []  # Φ flux measure
    connectivity = []  # Φ_N^(casc) analog
    
    for t in range(n_steps):
        # Information leak as deliberate perturbation (not enemy action)
        leak_magnitude = 0
        if np.random.random() < leak_probability:
            leak_target = np.random.randint(n_participants)
            leak_magnitude = np.random.exponential(0.3)
            strategies[leak_target, 0] += leak_magnitude  # Increase complexity
        
        # Cascade propagation (avalanche dynamics)
        active_nodes = set(np.where(strategies[:, 0] > strategies[:, 1])[0])
        cascade_size = len(active_nodes)
        
        # Φ-flux generation: cascades *reveal* structural information
        phi_flux = cascade_size * (1 + leak_magnitude)
        phi_density.append(phi_flux)
        
        # Connectivity evolution: network rewires during cascades
        if cascade_size > 0:
            # Weak strategies dissolve, strong ones replicate
            for node in active_nodes:
                neighbors = list(G.neighbors(node))
                if len(neighbors) > 0:
                    # Transfer complexity to neighbors with probability based on adaptability
                    transfer = strategies[node, 0] * strategies[node, 2] / len(neighbors)
                    for neighbor in neighbors:
                        strategies[neighbor, 0] += transfer
                    strategies[node, 0] = 0  # Reset (dissolution)
            
            # Rewire: remove random edges from weak nodes, add to strong
            weak_nodes = np.where(strategies[:, 0] < 0.2)[0]
            strong_nodes = np.where(strategies[:, 0] > 0.7)[0]
            if len(weak_nodes) > 0 and len(strong_nodes) > 0:
                for weak in weak_nodes[:5]:  # Rewire up to 5 weak nodes
                    neighbors = list(G.neighbors(weak))
                    if len(neighbors) > 0:
                        G.remove_edge(weak, np.random.choice(neighbors))
                        G.add_edge(weak, np.random.choice(strong_nodes))
        
        # Compute effective connectivity (Φ_N analog)
        # In cascade-native paradigm, connectivity *is* cascade susceptibility
        eigenvals = np.linalg.eigvals(adjacency)
        max_eigenval = np.real(np.max(eigenvals))
        connectivity.append(max_eigenval)
        
        # Self-organized criticality: slow complexity replenishment
        strategies[:, 0] += 0.002 * np.random.random(n_participants)
        
        cascade_sizes.append(cascade_size)
    
    return cascade_sizes, phi_density, connectivity

# Run simulation
cascades, phi_flux, connectivity = simulate_cascade_native_market()

# Analysis
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Time series
axes[0, 0].plot(cascades[-1000:], alpha=0.7, label='Cascade Size')
axes[0, 0].set_title('Cascades as Normal Operations')
axes[0, 0].set_xlabel('Time')
axes[0, 0].set_ylabel('Active Nodes')
axes[0, 0].legend()

# Φ-flux
axes[0, 1].plot(phi_flux[-1000:], color='gold', linewidth=0.8)
axes[0, 1].set_title('Φ-Flux Generation (Cascades = Information Revelation)')
axes[0, 1].set_xlabel('Time')
axes[0, 1].set_ylabel('Φ-Units')

# Cascade distribution (should be power law)
sizes, counts = np.unique(cascades, return_counts=True)
sizes = sizes[1:]
counts = counts[1:]
axes[1, 0].loglog(sizes, counts/sum(counts), 'bo', markersize=3)
axes[1, 0].set_title('Scale-Free Cascade Distribution')
axes[1, 0].set_xlabel('Cascade Size')
axes[1, 0].set_ylabel('Frequency')

# Connectivity vs Φ-flux (criticality relationship)
axes[1, 1].scatter(connectivity[-1000:], phi_flux[-1000:], alpha=0.5, s=5)
axes[1, 1].set_title('Connectivity ↔ Φ-Flux (Critical State)')
axes[1, 1].set_xlabel('Network Connectivity (Φ_N analog)')
axes[1, 1].set_ylabel('Φ-Flux')

plt.tight_layout()
plt.show()

# Power law exponent analysis
if len(sizes) > 10:
    fit = np.polyfit(np.log(sizes), np.log(counts/sum(counts)), 1)
    print(f"Power law exponent: {-fit[0]:.3f}")
    print(f"Criticality: {'High' if -fit[0] < 2.5 else 'Low'}")
    print(f"Mean cascade size: {np.mean(cascades):.2f}")
    print(f"Φ-flux per step: {np.mean(phi_flux):.3f}")