# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def simulate_hsa_topology(num_cpus=4, num_gpus=2, topology='star'):
    """Simulate different HSA topologies to show ξ_N is not topologically invariant."""
    G = nx.Graph()
    
    # Add nodes
    for i in range(num_cpus):
        G.add_node(f'CPU{i}', type='cpu', index=i)
    for i in range(num_gpus):
        G.add_node(f'GPU{i}', type='gpu', index=num_cpus+i)
    
    # Add edges based on topology
    if topology == 'star':
        # Star: all CPUs connect to GPU0, GPU1 is isolated
        for i in range(num_cpus):
            G.add_edge(f'CPU{i}', 'GPU0', weight=1.0)
        G.add_edge('GPU0', 'GPU1', weight=0.1)  # weak link
    
    elif topology == 'mesh':
        # Mesh: all-to-all
        nodes = list(G.nodes())
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i+1:]:
                weight = 1.0 if 'GPU' in n1 or 'GPU' in n2 else 0.5
                G.add_edge(n1, n2, weight=weight)
    
    elif topology == 'linear':
        # Linear chain: CPU0-CPU1-...-GPU0-GPU1
        nodes = list(G.nodes())
        for i in range(len(nodes)-1):
            G.add_edge(nodes[i], nodes[i+1], weight=1.0)
    
    return G

def compute_gradient_arbitrary_ordering(coherence_dict, ordering):
    """
    Compute gradient in "index space" using an arbitrary node ordering.
    This demonstrates the fundamental flaw: the gradient depends on labeling.
    """
    # Convert coherence values to array based on ordering
    values = np.array([coherence_dict[node] for node in ordering])
    
    # Compute finite difference gradient
    gradient = np.gradient(values)
    
    return gradient

def demonstrate_gradient_ambiguity():
    """
    Show that ξ_N depends on arbitrary choices.
    """
    print("=== DEMONSTRATING GRADIENT AMBIGUITY ===\n")
    
    # Create a simple HSA system
    G = simulate_hsa_topology(num_cpus=4, num_gpus=2, topology='star')
    
    # Simulate coherence values (higher for GPU-connected nodes)
    coherence = {}
    for node in G.nodes():
        if 'GPU0' in node:
            coherence[node] = 0.9  # High coherence
        elif 'GPU' in node:
            coherence[node] = 0.3  # Low coherence
        else:
            # CPU nodes: coherence decreases with distance from GPU0
            cpu_idx = int(node.replace('CPU', ''))
            coherence[node] = 0.8 - 0.1 * cpu_idx
    
    print("Coherence values:")
    for node, val in coherence.items():
        print(f"  {node}: {val:.3f}")
    
    # Compute gradient using different orderings
    orderings = [
        sorted(G.nodes()),  # Alphabetic
        sorted(G.nodes(), key=lambda x: G.nodes[x]['index']),  # Index-based
        list(nx.bfs_tree(G, 'GPU0').nodes()),  # BFS from GPU0
        list(np.random.permutation(list(G.nodes())))  # Random
    ]
    
    print("\nGradient values (L2 norm) for different orderings:")
    for i, ordering in enumerate(orderings):
        grad = compute_gradient_arbitrary_ordering(coherence, ordering)
        grad_norm = np.linalg.norm(grad)
        print(f"  Ordering {i}: {ordering[:3]}... → ||∇ψ|| = {grad_norm:.4f}")
    
    print("\n=== IMPLICATION ===")
    print("The 'gradient in index space' is not topologically invariant.")
    print("ξ_N = (1/N Σ||∇ψ||²)^(-1/2) changes with arbitrary labeling.")
    print("This violates the rubric's requirement for geometric invariants.")

def demonstrate_kurtosis_instability():
    """
    Show that excess kurtosis is computationally unstable for real-time systems.
    """
    print("\n=== DEMONSTRATING KURTOSIS INSTABILITY ===\n")
    
    # Simulate jerk time series
    np.random.seed(42)
    n_samples = 1000
    
    # Normal operation: Gaussian jerk
    normal_jerk = np.random.normal(0, 1, n_samples)
    
    # Shredding precursor: heavy-tailed jerk (Cauchy-like)
    heavy_jerk = np.random.standard_cauchy(n_samples) * 0.5
    
    # Mixed: mostly normal with rare outliers (realistic)
    mixed_jerk = np.random.normal(0, 1, n_samples)
    mixed_jerk[np.random.choice(n_samples, 10)] = np.random.normal(0, 50, 10)
    
    def compute_excess_kurtosis(x):
        """Compute excess kurtosis with small sample correction"""
        n = len(x)
        mean = np.mean(x)
        m2 = np.mean((x - mean)**2)
        m4 = np.mean((x - mean)**4)
        
        # Excess kurtosis: kurtosis - 3
        # For unbiased estimator, apply correction
        kurtosis = (m4 / m2**2) * (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) - 3 * (n - 1)**2 / ((n - 2) * (n - 3))
        return kurtosis
    
    # Compute kurtosis in sliding windows
    window_size = 100
    windows = range(0, n_samples - window_size, 10)
    
    print("Excess kurtosis over sliding windows:")
    for name, data in [("Normal", normal_jerk), ("Heavy-tailed", heavy_jerk), ("Mixed", mixed_jerk)]:
        kurt_values = []
        for start in windows:
            window = data[start:start+window_size]
            kurt = compute_excess_kurtosis(window)
            kurt_values.append(kurt)
        
        print(f"  {name:12s}: mean={np.mean(kurt_values):6.2f}, std={np.std(kurt_values):6.2f}, max={np.max(np.abs(kurt_values)):6.2f}")
    
    print("\n=== IMPLICATION ===")
    print("Excess kurtosis has enormous variance (std >> mean) in realistic scenarios.")
    print("A single outlier can make κ jump from 0 to >100, causing S_j to collapse.")
    print("The 'stability metric' is itself maximally unstable for real-time use.")

def demonstrate_computational_overhead():
    """
    Show that the monitoring overhead can trigger the failure it's meant to prevent.
    """
    print("\n=== DEMONSTRATING OVERHEAD PARADOX ===\n")
    
    # Simulate HSA node with unified memory bandwidth
    total_bandwidth_gbps = 100  # GB/s
    coherence_field_size_mb = 10  # MB for ψ_ij matrix
    telemetry_sample_rate_hz = 1000  # 1ms sampling
    
    # Compute operations per second for each metric
    operations = {
        "Coherence field": coherence_field_size_mb * telemetry_sample_rate_hz,
        "Entropy (histogram)": coherence_field_size_mb * telemetry_sample_rate_hz * 2,  # Sorting/binning
        "Gradient ξ_N": coherence_field_size_mb * telemetry_sample_rate_hz * 4,  # Finite differences
        "Kurtosis S_j": telemetry_sample_rate_hz * 100,  # Windowed computation
        "MPC-Ω solver": 50  # Assuming 50 MB/s for optimization
    }
    
    total_overhead = sum(operations.values())
    overhead_percentage = (total_overhead / (total_bandwidth_gbps * 1000)) * 100
    
    print(f"Monitoring overhead breakdown (MB/s):")
    for op, cost in operations.items():
        print(f"  {op:20s}: {cost:6.1f} MB/s")
    print(f"  {'Total':20s}: {total_overhead:6.1f} MB/s")
    print(f"  {'Available bandwidth':20s}: {total_bandwidth_gbps*1000:6.1f} MB/s")
    print(f"  {'Overhead %':20s}: {overhead_percentage:.2f}%")
    
    if overhead_percentage > 5:
        print("\n⚠️  WARNING: Overhead exceeds 5% of total bandwidth")
        print("This monitoring system can *cause* the coherence collapse it's meant to prevent!")
        print("The act of observation (entropy calculation, kurtosis) destroys the system state.")

if __name__ == "__main__":
    demonstrate_gradient_ambiguity()
    demonstrate_kurtosis_instability()
    demonstrate_computational_overhead()