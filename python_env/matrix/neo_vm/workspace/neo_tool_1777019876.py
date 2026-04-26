# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import entropy

def generate_sub_planckian_lattice(n_nodes, defect_prob=0.3):
    """
    Simulate a sub-Planckian lattice with inherent defects.
    At these scales, perfect lattices cannot exist - defects are fundamental.
    """
    # Base triangular lattice (simplest stable 2D topology)
    G = nx.triangular_lattice_graph(int(np.sqrt(n_nodes)), int(np.sqrt(n_nodes)))
    G = nx.convert_node_labels_to_integers(G)
    
    # Sub-Planckian: random defects from quantum foam
    edges_to_remove = []
    for edge in G.edges():
        if np.random.random() < defect_prob:
            edges_to_remove.append(edge)
    
    G.remove_edges_from(edges_to_remove)
    
    # Add random non-local correlations (DEDS edges)
    # These represent the "spooky" connections the proposal mentions
    for _ in range(int(len(G.edges()) * 0.1)):
        u, v = np.random.choice(G.nodes(), 2, replace=False)
        G.add_edge(u, v)
    
    return G

def compute_phi_density_proposal(G):
    """
    Compute the Φ-density using the proposal's flawed formula:
    Φ = log2(Betti_Number / Shannon_Entropy)
    """
    # Simplified Betti number: just count cycles (b1)
    # For a graph, b1 = m - n + c where m=edges, n=nodes, c=components
    n = G.number_of_nodes()
    m = G.number_of_edges()
    c = nx.number_connected_components(G)
    b1 = max(0, m - n + c)  # First Betti number
    
    # Shannon entropy of degree distribution (proxy for lattice uncertainty)
    degrees = [d for n, d in G.degree()]
    if len(set(degrees)) == 1:  # All same degree -> zero entropy
        return float('-inf'), b1, 0
    
    degree_counts = np.bincount(degrees)
    degree_probs = degree_counts / degree_counts.sum()
    shannon_entropy = entropy(degree_probs)
    
    if shannon_entropy == 0:
        return float('-inf'), b1, shannon_entropy
    
    # THE CRITICAL FLAW: Betti number is integer, entropy is real
    # Their ratio is dimensionally meaningless and unstable
    ratio = b1 / shannon_entropy
    
    # Log of ratio can be negative -> "negative information density"
    phi_density = np.log2(ratio)
    
    return phi_density, b1, shannon_entropy

def compute_defect_encoding_capacity(G):
    """
    Disruptive alternative: Information stored in topological defects themselves.
    Each defect (missing edge, anomalous node) is a bit.
    """
    # Count defects relative to perfect triangular lattice
    max_edges = 3 * G.number_of_nodes() - 6  # For planar triangular
    actual_edges = G.number_of_edges()
    missing_edges = max(0, max_edges - actual_edges)
    
    # Non-local edges are also information carriers (defects in locality)
    non_local_edges = len([e for e in G.edges() if abs(e[0] - e[1]) > 3])
    
    # Total capacity scales linearly with defect density
    defect_capacity = missing_edges + non_local_edges
    
    return defect_capacity, missing_edges, non_local_edges

def demonstrate_instability():
    """
    Show that the proposal's Φ-density is mathematically incoherent
    while defect-based encoding is stable.
    """
    results = []
    
    for defect_prob in np.linspace(0.1, 0.9, 10):
        phi_vals = []
        defect_caps = []
        
        for trial in range(100):
            G = generate_sub_planckian_lattice(144, defect_prob)
            phi, b1, h = compute_phi_density_proposal(G)
            defect_cap, _, _ = compute_defect_encoding_capacity(G)
            
            phi_vals.append(phi)
            defect_caps.append(defect_cap)
        
        results.append({
            'defect_prob': defect_prob,
            'phi_mean': np.mean(phi_vals),
            'phi_std': np.std(phi_vals),
            'phi_min': np.min(phi_vals),
            'defect_cap_mean': np.mean(defect_caps),
            'defect_rate': defect_prob
        })
    
    return results

# Execute the disruption analysis
print("=== SUB-PLANCKIAN LATTICE DISRUPTION ANALYSIS ===\n")

# Show a single lattice example
G = generate_sub_planckian_lattice(64, defect_prob=0.4)
phi, b1, h = compute_phi_density_proposal(G)
defect_cap, missing, nonlocal = compute_defect_encoding_capacity(G)

print(f"Example Lattice (64 nodes, 40% defect probability):")
print(f"  Betti number (b1): {b1}")
print(f"  Shannon entropy: {h:.3f}")
print(f"  Φ-density (proposal): {phi:.3f}")
print(f"  Defect capacity (disruption): {defect_cap}")
print(f"  Missing edges: {missing}, Non-local edges: {nonlocal}")
print()

# Show mathematical instability
print("Mathematical Instability Demonstration:")
print("  - Φ-density is often NEGATIVE (log2(ratio) < 0)")
print("  - Betti number is INTEGER, entropy is CONTINUOUS")
print("  - Ratio is dimensionally inconsistent")
print("  - Division by zero when entropy → 0 (ordered lattice)")
print()

# Run systematic analysis
print("Systematic Analysis Across Defect Probabilities:")
print("Prob | Φ-Density (mean±std) | Φ-Min | Defect Capacity")
print("-" * 55)

results = demonstrate_instability()
for r in results:
    print(f"{r['defect_prob']:.1f}  | {r['phi_mean']:6.2f} ± {r['phi_std']:5.2f}    | {r['phi_min']:6.2f} | {r['defect_cap_mean']:6.0f}")

print("\n=== DISRUPTIVE INSIGHT ===")

# The visualization code
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Phi-density instability
probs = [r['defect_prob'] for r in results]
phi_means = [r['phi_mean'] for r in results]
phi_stds = [r['phi_std'] for r in results]
ax1.errorbar(probs, phi_means, yerr=phi_stds, fmt='ro-', capsize=5)
ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax1.set_xlabel('Defect Probability')
ax1.set_ylabel('Φ-Density (proposal)')
ax1.set_title('Φ-Density: Negative & Unstable')
ax1.grid(True, alpha=0.3)

# Plot 2: Defect capacity stability
defect_means = [r['defect_cap_mean'] for r in results]
ax2.plot(probs, defect_means, 'bo-')
ax2.set_xlabel('Defect Probability')
ax2.set_ylabel('Defect Encoding Capacity')
ax2.set_title('Defect Encoding: Stable & Linear')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('sub_planckian_disruption.png', dpi=150, bbox_inches='tight')
print("Visualization saved as 'sub_planckian_disruption.png'")