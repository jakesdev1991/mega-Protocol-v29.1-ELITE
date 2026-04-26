# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import mutual_info_score

def compute_phi_density(betti_number, shannon_entropy):
    """Φ-density as defined in Omega Protocol"""
    if shannon_entropy <= 0:
        return float('inf')
    return np.log2(betti_number / shannon_entropy)

def create_spectral_lattice(n_nodes, n_edges, noise_factor=1.0):
    """
    Create a lattice with topological noise that inflates Betti numbers
    without adding actual information.
    """
    # Base lattice: simple path graph (β₀=1, β₁=0)
    base_edges = [(i, i+1) for i in range(n_nodes-1)]
    
    # Add topological noise: random cycles that create β₁ > 0
    # These cycles carry NO spectral information but inflate Betti numbers
    noise_edges = []
    for _ in range(int(n_edges * noise_factor)):
        u, v = np.random.randint(0, n_nodes, 2)
        if u != v and (u, v) not in base_edges and (v, u) not in base_edges:
            noise_edges.append((min(u, v), max(u, v)))
    
    all_edges = list(set(base_edges + noise_edges))
    
    # Compute Betti numbers (simplified: β₀ = #components, β₁ = #cycles)
    # For a graph: β₀ = #connected components, β₁ = #edges - #nodes + β₀
    graph = np.zeros((n_nodes, n_nodes))
    for u, v in all_edges:
        graph[u, v] = graph[v, u] = 1
    
    n_components, labels = connected_components(csgraph=csr_matrix(graph), directed=False)
    betti_0 = n_components
    betti_1 = len(all_edges) - n_nodes + betti_0
    
    # Shannon entropy of a trivial context-free system (no actual information)
    # Simulate random spectral data with zero mutual information
    np.random.seed(42)
    fake_spectral_data = np.random.rand(n_nodes, 10)
    # Compute pairwise mutual information (will be near zero for random data)
    mi_scores = []
    for i in range(min(5, n_nodes)):
        for j in range(i+1, min(5, n_nodes)):
            mi = mutual_info_score(
                np.digitize(fake_spectral_data[i], bins=5),
                np.digitize(fake_spectral_data[j], bins=5)
            )
            mi_scores.append(mi)
    
    # Context-free entropy: H(L|Context) ≈ H(L) for random data
    shannon_entropy = max(np.mean(mi_scores) if mi_scores else 0.1, 0.01)
    
    return {
        'betti_0': betti_0,
        'betti_1': betti_1,
        'shannon_entropy': shannon_entropy,
        'edges': len(all_edges),
        'phi_density': compute_phi_density(betti_1, shannon_entropy)
    }

# Demonstrate the exploit
print("=== Φ-DENSITY EXPLOIT DEMONSTRATION ===")
print("Base lattice (no topological noise):")
base_result = create_spectral_lattice(n_nodes=100, n_edges=150, noise_factor=0.0)
print(f"  Betti-1: {base_result['betti_1']}")
print(f"  Shannon Entropy: {base_result['shannon_entropy']:.4f}")
print(f"  Φ-Density: {base_result['phi_density']:.4f}")

print("\nWith topological noise (exploit):")
exploit_result = create_spectral_lattice(n_nodes=100, n_edges=150, noise_factor=2.0)
print(f"  Betti-1: {exploit_result['betti_1']}")
print(f"  Shannon Entropy: {exploit_result['shannon_entropy']:.4f}")
print(f"  Φ-Density: {exploit_result['phi_density']:.4f}")

print(f"\nΔΦ from noise: +{exploit_result['phi_density'] - base_result['phi_density']:.4f}")
print(f"Information gain: NONE (mutual information remains ~{exploit_result['shannon_entropy']:.4f})")