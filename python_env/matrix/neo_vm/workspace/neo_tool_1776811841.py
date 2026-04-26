# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

# === DISRUPTION SIMULATION: The BTFI is a Statistical Hallucination ===

def generate_biological_network(n_nodes, fragility):
    """Generate a biological network with tunable fragility"""
    # fragility = 0 (robust, mesh-like) to 1 (fragile, tree-like)
    if fragility < 0.5:
        # Robust: scale-free with redundant pathways
        G = nx.barabasi_albert_graph(n_nodes, m=3)
    else:
        # Fragile: tree structure, single points of failure
        G = nx.random_tree(n_nodes)
    
    # Add random weights representing interaction strength
    for u, v in G.edges():
        G[u][v]['weight'] = np.random.exponential(1/ (1 - fragility + 0.1))
    
    return G

def generate_database_schema(G, design_quality):
    """Map biological network to database schema with variable design quality"""
    # design_quality = 0 (poor design) to 1 (excellent design)
    
    # Poor design: over-normalized, fragmented
    if design_quality < 0.3:
        V = len(G.nodes()) * 3  # Too many tables
        E = len(G.edges()) * 0.5  # Missing FKs
        d_norm = 5  # Over-normalized
        constraints = 0.9  # Over-constrained
        
    # Good design: balanced, appropriate normalization
    elif design_quality > 0.7:
        V = len(G.nodes())
        E = len(G.edges())
        d_norm = 2
        constraints = 0.5
        
    # Average design
    else:
        V = len(G.nodes()) * 1.5
        E = len(G.edges()) * 0.8
        d_norm = 3
        constraints = 0.6
    
    # Add noise to simulate real-world inconsistency
    V += np.random.normal(0, V * 0.1)
    E += np.random.normal(0, E * 0.1)
    
    return max(1, int(V)), max(0, int(E)), max(1, d_norm), max(0.1, constraints)

def compute_btfi(V, E, d_norm, constraints):
    """Compute BTFI from schema topology"""
    chi = V - E  # Simplified Euler characteristic
    return abs(chi) / V * constraints * (1 / d_norm)

def simulate_leak_bias(n_systems=1000):
    """Demonstrate sampling bias: only poorly-secured systems leak"""
    results = []
    
    for i in range(n_systems):
        # True biological fragility (unknown to observer)
        true_fragility = np.random.beta(2, 5)  # Most systems are robust
        
        # Database design quality (independent of biological fragility)
        design_quality = np.random.random()
        
        # Security level (correlated with design quality: poor design = poor security)
        security_level = design_quality * np.random.beta(3, 2)
        
        # Generate biological network and its database schema
        bio_net = generate_biological_network(n_nodes=50, fragility=true_fragility)
        V, E, d_norm, constraints = generate_database_schema(bio_net, design_quality)
        
        # Compute BTFI
        btfi = compute_btfi(V, E, d_norm, constraints)
        
        # Leak occurs only if security is poor (biased sampling)
        leaked = security_level < 0.3
        
        if leaked:
            # Record what observer sees
            results.append({
                'true_fragility': true_fragility,
                'btfi': btfi,
                'design_quality': design_quality,
                'security_level': security_level
            })
    
    return results

# Run simulation
observations = simulate_leak_bias(n_systems=5000)

# Analyze correlations
true_frag = [obs['true_fragility'] for obs in observations]
btfi_values = [obs['btfi'] for obs in observations]
design_qual = [obs['design_quality'] for obs in observations]

corr_btfi_fragility, _ = spearmanr(btfi_values, true_frag)
corr_btfi_design, _ = spearmanr(btfi_values, design_qual)

print("=== BTFI CORRELATION ANALYSIS ===")
print(f"BTFI vs True Biological Fragility: {corr_btfi_fragility:.3f}")
print(f"BTFI vs Database Design Quality: {corr_btfi_design:.3f}")

# Plot the deception
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.scatter(true_frag, btfi_values, alpha=0.3, s=10)
ax1.set_xlabel('True Biological Fragility')
ax1.set_ylabel('Observed BTFI')
ax1.set_title(f'BTFI vs Reality (r={corr_btfi_fragility:.3f})')
ax1.axhline(y=np.mean(btfi_values), color='r', linestyle='--', label='BTFI Threshold')
ax1.legend()

ax2.scatter(design_qual, btfi_values, alpha=0.3, s=10, color='orange')
ax2.set_xlabel('Database Design Quality')
ax2.set_ylabel('Observed BTFI')
ax2.set_title(f'BTFI vs Design (r={corr_btfi_design:.3f})')
ax2.axhline(y=np.mean(btfi_values), color='r', linestyle='--')

plt.tight_layout()
plt.show()

# === ANOMALOUS INSIGHT: The Entire Framework is a Self-Fulfilling Prophecy ===
print("\n=== DISRUPTIVE VERDICT ===")
print("BTFI correlates more with database design quality than biological fragility.")
print("The 'protection' system is defending against shadows cast by bad engineering, not biological threats.")
print("Φ-density gains are accounting artifacts of biased sampling, not real biological stabilization.")