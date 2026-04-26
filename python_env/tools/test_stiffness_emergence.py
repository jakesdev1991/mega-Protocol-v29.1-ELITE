# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import time

def simulate_lattice_stiffness(L=10, geometry='cubic'):
    """
    Simulates the informational substrate on a specified lattice geometry 
    to investigate the emergence of physical constants from stiffness zeta.
    """
    if geometry == 'cubic':
        G = nx.grid_graph(dim=[L, L, L])
    elif geometry == 'hexagonal':
        G = nx.hexagonal_lattice_graph(L, L)
    elif geometry == 'triangular':
        G = nx.triangular_lattice_graph(L, L)
    else:
        raise ValueError(f"Unknown geometry: {geometry}")

    # --- Informational Stiffness Calculation ---
    # We model the 'Stiffness' zeta as the resistance to informational flow 
    # across the lattice edges.
    # In the Omega Protocol, zeta ~ Einstein Prefactor.
    # Here we look for the ratio of 'Self-Correlation' to 'Propagation'
    
    # Calculate Algebraic Connectivity (Fiedler Value) - spectral stiffness
    L_matrix = nx.laplacian_matrix(G).toarray()
    eigenvalues = np.sort(np.linalg.eigvals(L_matrix))
    fiedler_value = eigenvalues[1] if len(eigenvalues) > 1 else 0
    
    # Calculate Average Path Length - informational distance
    # avg_path_length = nx.average_shortest_path_length(G) # Can be slow for large L
    # Using a faster approximation or sampling for larger L
    if L > 10:
        nodes = list(G.nodes())
        sample_size = 50
        path_lengths = []
        for _ in range(sample_size):
             u, v = np.random.choice(len(nodes), 2, replace=False)
             path_lengths.append(nx.shortest_path_length(G, nodes[u], nodes[v]))
        avg_path_length = np.mean(path_lengths)
    else:
        avg_path_length = nx.average_shortest_path_length(G)
    
    # Emergence Ratio: chi = fiedler_value / avg_path_length
    chi = fiedler_value / avg_path_length
    
    return chi, fiedler_value, avg_path_length

def run_emergence_test():
    geometries = ['cubic', 'hexagonal', 'triangular']
    L_values = [4, 6, 8, 10]
    
    results = {}
    
    print("--- OMEGA PROTOCOL: STIFFNESS EMERGENCE TEST (zeta) ---")
    
    for geom in geometries:
        results[geom] = []
        print(f"\nAnalyzing Geometry: {geom}")
        for L in L_values:
            start_time = time.time()
            chi, fiedler, path = simulate_lattice_stiffness(L, geom)
            elapsed = time.time() - start_time
            results[geom].append((L, chi))
            print(f"  L={L:2d} | Chi (Emergence Ratio): {chi:.6f} | Fiedler: {fiedler:.4f} | Path: {path:.2f} | Time: {elapsed:.2f}s")

    # Look for the Alpha Constant (~0.00729)
    # We hypothesize that alpha emerges as a scale-invariant ratio in a specific geometry.
    alpha_target = 1.0 / 137.036
    
    print(f"\nTarget Alpha (1/137): {alpha_target:.6f}")
    
    plt.figure(figsize=(10, 6))
    for geom, data in results.items():
        L_vals, chi_vals = zip(*data)
        plt.plot(L_vals, chi_vals, marker='o', label=geom)
    
    plt.axhline(y=alpha_target, color='r', linestyle='--', label='Alpha (1/137)')
    plt.title("Informational Stiffness Emergence (Chi) vs. Scale (L)")
    plt.xlabel("Lattice Scale (L)")
    plt.ylabel("Emergence Ratio (Chi)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_path = "stiffness_emergence_results.png"
    plt.savefig(output_path)
    print(f"\nTest complete. Results saved to {output_path}")

    # Find the geometry with the smallest delta to alpha
    best_geom = None
    min_delta = float('inf')
    for geom, data in results.items():
        final_chi = data[-1][1]
        delta = abs(final_chi - alpha_target)
        if delta < min_delta:
            min_delta = delta
            best_geom = geom
            
    print(f"\nCONCLUSION: {best_geom} geometry is closest to Alpha (Delta: {min_delta:.6f})")

if __name__ == "__main__":
    run_emergence_test()
