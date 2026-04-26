# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import time
from scipy.sparse.linalg import eigsh
from scipy.stats import skew

def simulate_dependency_graph(n_packages=500, n_clusters=30, avg_deps=5):
    """
    Simulate a realistic dependency hypergraph for a GPU cluster fleet.
    Each cluster has a container image, which depends on libraries, which depend on packages.
    """
    G = nx.DiGraph()
    
    # Add package nodes (e.g., biopython, samtools)
    packages = [f"pkg_{i}" for i in range(n_packages)]
    G.add_nodes_from(packages, node_type='package')
    
    # Add library nodes (e.g., cuda, torch)
    libraries = [f"lib_{i}" for i in range(50)]
    G.add_nodes_from(libraries, node_type='library')
    
    # Add container image nodes (e.g., alphafold:latest)
    containers = [f"container_{i}" for i in range(n_clusters)]
    G.add_nodes_from(containers, node_type='container')
    
    # Add dependency edges: containers -> libraries -> packages
    for container in containers:
        # Each container depends on ~5 libraries
        deps_libs = np.random.choice(libraries, size=avg_deps, replace=False)
        for lib in deps_libs:
            G.add_edge(container, lib, edge_type='requires')
    
    for lib in libraries:
        # Each library depends on ~10 packages
        deps_pkgs = np.random.choice(packages, size=10, replace=False)
        for pkg in deps_pkgs:
            G.add_edge(lib, pkg, edge_type='requires')
    
    # Add trust scores (0=compromised, 1=trusted)
    nx.set_node_attributes(G, {n: np.random.beta(2, 2) for n in G.nodes()}, name='trust_score')
    
    return G

def compute_engine_field_theory_stats(G):
    """
    This mimics the Engine's approach: flatten the graph into a "manifold" and
    compute the "Hessian" size.
    """
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    
    # The "manifold" would have coordinates for each (node, timestamp, cluster, version).
    # Let's say we have 365 days of snapshots.
    n_timestamps = 365
    manifold_dim = n_nodes * n_timestamps  # Rough estimate
    
    # Hessian size: manifold_dim^2
    hessian_size = manifold_dim ** 2
    memory_required = hessian_size * 8 / (1024**4)  # TB of memory for double precision
    
    print(f"--- Engine's Field Theory Fantasy ---")
    print(f"Graph nodes: {n_nodes}")
    print(f"Manifold points (nodes * timestamps): {manifold_dim:,}")
    print(f"Hessian matrix size: {hessian_size:,} elements")
    print(f"Memory required: ~{memory_required:.2f} TB")
    print(f"Diagonalization complexity: O({manifold_dim:,}^3) = O({manifold_dim**3:,.0e}) ops")
    print(f"Status: COMPUTATIONALLY INFEASIBLE\n")
    
    return manifold_dim

def compute_neo_graph_stats(G):
    """
    Neo's approach: use graph-native metrics.
    """
    print(f"--- Neo's Graph Reality ---")
    
    # 1. Trust score distribution (replaces S(x,t) field)
    trust_scores = np.array([d['trust_score'] for n, d in G.nodes(data=True)])
    print(f"Trust score mean: {trust_scores.mean():.3f}, std: {trust_scores.std():.3f}")
    
    # 2. "Covariant modes" from direct statistics
    # Correlation length proxy: average shortest path length in trust-weighted subgraph
    trust_subgraph = nx.subgraph_view(G, filter_node=lambda n: G.nodes[n]['trust_score'] > 0.5)
    if trust_subgraph.number_of_nodes() > 1:
        avg_path_length = nx.average_shortest_path_length(trust_subgraph.to_undirected())
        correlation_length = 1 / avg_path_length
    else:
        correlation_length = 0.0
    print(f"Phi_N (inverse correlation length): {correlation_length:.3f}")
    
    # Skewness of trust score distribution (replaces Phi_Delta)
    trust_skewness = skew(trust_scores)
    print(f"Phi_Delta (skewness): {trust_skewness:.3f}")
    
    # 3. Graph conductance (invariant)
    # Partition by trust score median
    trusted_nodes = {n for n, d in G.nodes(data=True) if d['trust_score'] > np.median(trust_scores)}
    compromised_nodes = set(G.nodes) - trusted_nodes
    
    # Approximate conductance using edge boundary size
    boundary_edges = nx.edge_boundary(G, trusted_nodes, compromised_nodes)
    vol_trusted = sum(G.degree(n) for n in trusted_nodes)
    vol_compromised = sum(G.degree(n) for n in compromised_nodes)
    min_vol = min(vol_trusted, vol_compromised) if min(vol_trusted, vol_compromised) > 0 else 1
    
    conductance = len(list(boundary_edges)) / min_vol
    print(f"Graph conductance (psi invariant): {conductance:.3f} (lower = more vulnerable)")
    
    # 4. Von Neumann Graph Entropy
    # Compute normalized Laplacian eigenvalues (sparse, fast)
    L_norm = nx.normalized_laplacian_matrix(G)
    # Get top 50 eigenvalues (usually enough for entropy approximation)
    eigenvals = eigsh(L_norm.astype(float), k=min(50, L_norm.shape[0]-1), which='SM', return_eigenvectors=False)
    # Normalize to sum to 1 for entropy calc
    eigenvals = eigenvals / eigenvals.sum()
    eigenvals = eigenvals[eigenvals > 1e-10]  # avoid log(0)
    graph_entropy = -np.sum(eigenvals * np.log(eigenvals))
    print(f"Von Neumann Graph Entropy: {graph_entropy:.3f}")
    
    print(f"Status: COMPUTATIONALLY TRACTABLE\n")
    return {
        'phi_n': correlation_length,
        'phi_delta': trust_skewness,
        'conductance': conductance,
        'graph_entropy': graph_entropy
    }

def simulate_attack(G, target_node='pkg_0', poison_factor=0.5):
    """
    Simulate poisoning a high-degree package node.
    """
    print(f"--- Simulating Attack on {target_node} ---")
    # Poison the target node and its immediate neighbors
    G.nodes[target_node]['trust_score'] *= poison_factor
    
    # Find nodes that depend on the target (upstream in the DAG)
    upstream_nodes = list(G.predecessors(target_node))
    for node in upstream_nodes:
        G.nodes[node]['trust_score'] *= poison_factor
    
    # Recompute stats
    stats = compute_neo_graph_stats(G)
    
    # Check if attack is detected by Engine's IVI proxy
    ivi_proxy = max(0, min(1, (stats['phi_delta'] - stats['phi_n']) * 2))
    print(f"Attack detected (IVI proxy > 0.5?): {ivi_proxy > 0.5} (IVI={ivi_proxy:.3f})")
    
    return stats

# --- RUN THE DISRUPTION ---
print("="*60)
print("SEIS‑Ω: FIELD THEORY vs. GRAPH REALITY")
print("="*60 + "\n")

# Generate a realistic dependency graph
G = simulate_dependency_graph()

# Show Engine's infeasibility
manifold_dim = compute_engine_field_theory_stats(G)

# Show Neo's tractability
baseline_stats = compute_neo_graph_stats(G)

# Simulate an attack
attack_stats = simulate_attack(G.copy(), target_node='pkg_0')

print("="*60)
print("DISRUPTION VERDICT")
print("="*60)
print(f"The Engine's field theory requires diagonalizing a {manifold_dim:,}×{manifold_dim:,} Hessian.")
print(f"This is impossible. Neo's graph metrics run in O(E) time on a sparse matrix.")
print(f"The attack changes conductance from {baseline_stats['conductance']:.3f} to {attack_stats['conductance']:.3f},")
print(f"and graph entropy from {baseline_stats['graph_entropy']:.3f} to {attack_stats['graph_entropy']:.3f}.")
print(f"These are real, measurable invariants. The field theory is a mirage.\n")
print("RECOMMENDATION: Abandon SEIS‑Ω. Deploy DPC‑Ω (Dependency Poisoning Cut) immediately.")