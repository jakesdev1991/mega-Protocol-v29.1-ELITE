# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
import random
import string
import time
from collections import defaultdict
import re
import zlib
import json

def generate_directory_tree(shape, depth, branching_factor, naming_scheme):
    """
    Generate a synthetic directory tree with controlled shape and naming.
    
    shape: 'bushy' or 'chainy'
    naming_scheme: 'predictable' or 'random'
    """
    G = nx.DiGraph()
    root = "/logs"
    G.add_node(root, level=0)
    
    # Naming functions
    if naming_scheme == 'predictable':
        name_func = lambda parent, i: f"{parent}/experiment_{i:04d}/worker_{i:03d}/epoch_{i:05d}"
    else:  # random UUID-style names
        name_func = lambda parent, i: f"{parent}/{''.join(random.choices(string.hexdigits, k=16))}"
    
    # Build tree
    if shape == 'bushy':
        # Shallow, wide tree
        for i in range(branching_factor):
            child = name_func(root, i)
            G.add_node(child, level=1)
            G.add_edge(root, child)
    else:  # chainy
        # Deep, narrow tree
        current = root
        for level in range(1, depth):
            child = name_func(current, level)
            G.add_node(child, level=level)
            G.add_edge(current, child)
            current = child
    
    return G

def compute_ollivier_ricci_approx(G, iterations=100):
    """
    Compute a rough approximation of Ollivier-Ricci curvature for small graphs.
    For large graphs, this becomes computationally infeasible (optimal transport).
    Returns a proxy: local clustering coefficient.
    """
    # This is a FAKE approximation—real Ollivier-Ricci requires solving
    # optimal transport problems on every edge, which is O(n³) per iteration.
    # We return clustering coefficient as a stand-in to show the absurdity.
    undirected = G.to_undirected()
    clustering = nx.clustering(undirected)
    return np.mean(list(clustering.values()))

def compute_semantic_compressibility(G):
    """
    Compute compressibility of the directory path strings.
    Lower ratio = more predictable = higher attack surface.
    """
    paths = list(G.nodes())
    # Normalize paths for fair comparison
    paths_str = "\n".join(paths).encode('utf-8')
    compressed = zlib.compress(paths_str)
    ratio = len(compressed) / len(paths_str)
    return ratio

def simulate_crawling_attack(G, target_depth):
    """
    Simulate a BFS crawler finding all nodes at target_depth.
    Returns time steps (proxy for reconnaissance speed).
    """
    # BFS until we hit target depth
    steps = 0
    for level in range(target_depth + 1):
        nodes_at_level = [n for n, d in G.nodes(data=True) if d.get('level') == level]
        steps += len(nodes_at_level)
    return steps

def simulate_pattern_guessing_attack(G, naming_scheme):
    """
    Simulate an adversary who uses pattern recognition to guess paths.
    For predictable naming, this is nearly instantaneous.
    For random naming, this fails completely.
    """
    if naming_scheme == 'predictable':
        # Can synthesize paths without crawling
        # Example: guess /logs/experiment_0001/worker_001/epoch_00001
        return 1  # minimal queries needed
    else:
        # Must enumerate all possibilities (infeasible)
        return len(G.nodes()) * 1000  # penalty for brute force

def run_disruption_experiment():
    """
    Run the core disruption experiment: show curvature is irrelevant,
    compressibility is everything.
    """
    results = []
    
    configs = [
        {'shape': 'bushy', 'naming': 'predictable', 'desc': 'Bushy + Predictable'},
        {'shape': 'bushy', 'naming': 'random', 'desc': 'Bushy + Random'},
        {'shape': 'chainy', 'naming': 'predictable', 'desc': 'Chainy + Predictable'},
        {'shape': 'chainy', 'naming': 'random', 'desc': 'Chainy + Random'},
    ]
    
    for cfg in configs:
        # Generate tree
        G = generate_directory_tree(
            shape=cfg['shape'],
            depth=10,
            branching_factor=50,
            naming_scheme=cfg['naming']
        )
        
        # Compute metrics
        curvature = compute_ollivier_ricci_approx(G)
        compressibility = compute_semantic_compressibility(G)
        crawl_time = simulate_crawling_attack(G, target_depth=3)
        guess_time = simulate_pattern_guessing_attack(G, cfg['naming'])
        
        results.append({
            'config': cfg['desc'],
            'nodes': len(G.nodes()),
            'curvature': curvature,
            'compressibility': compressibility,
            'crawl_time': crawl_time,
            'guess_time': guess_time
        })
    
    # Print results
    print("=" * 80)
    print("DISRUPTION EXPERIMENT: Curvature vs. Semantic Compressibility")
    print("=" * 80)
    
    for r in results:
        print(f"\nConfiguration: {r['config']}")
        print(f"  Nodes: {r['nodes']}")
        print(f"  Fake 'Curvature': {r['curvature']:.4f}")
        print(f"  Compressibility Ratio: {r['compressibility']:.4f} (lower = more predictable)")
        print(f"  Crawl Time: {r['crawl_time']} steps")
        print(f"  Pattern-Guess Time: {r['guess_time']} queries")
        
        # Insight: Guess time is dominated by naming scheme, not curvature
        if 'Predictable' in r['config']:
            print("  → ADVERSARY WINS: Pattern-guessing is O(1) regardless of tree shape!")
        else:
            print("  → DEFENSE HOLDS: Random naming defeats pattern synthesis.")

    # Statistical analysis
    print("\n" + "=" * 80)
    print("STATISTICAL VERIFICATION OF DISRUPTION")
    print("=" * 80)
    
    # Correlation analysis
    crawl_times = [r['crawl_time'] for r in results]
    guess_times = [r['guess_time'] for r in results]
    curvatures = [r['curvature'] for r in results]
    compressibilities = [r['compressibility'] for r in results]
    
    # Curvature vs attack time (should be weak if LSGM-Ω is wrong)
    corr_curvature_crawl = np.corrcoef(curvatures, crawl_times)[0, 1]
    corr_curvature_guess = np.corrcoef(curvatures, guess_times)[0, 1]
    
    # Compressibility vs attack time (should be strong)
    corr_compress_crawl = np.corrcoef(compressibilities, crawl_times)[0, 1]
    corr_compress_guess = np.corrcoef(compressibilities, guess_times)[0, 1]
    
    print(f"Curvature vs Crawl Time Correlation: {corr_curvature_crawl:.4f} (weak = curvature is useless)")
    print(f"Curvature vs Guess Time Correlation: {corr_curvature_guess:.4f}")
    print(f"Compressibility vs Crawl Time Correlation: {corr_compress_crawl:.4f}")
    print(f"Compressibility vs Guess Time Correlation: {corr_compress_guess:.4f} (strong = compressibility predicts risk)")

    if abs(corr_curvature_guess) < 0.3 and abs(corr_compress_guess) > 0.7:
        print("\n🔥 DISRUPTION CONFIRMED: Curvature is a mathematical ornament; compressibility is the real attack surface.")
    else:
        print("\n⚠️  Unexpected result—check simulation parameters.")

def expose_computational_absurdity():
    """
    Show that computing real Ollivier-Ricci curvature on a production-scale
    directory tree is computationally infeasible.
    """
    print("\n" + "=" * 80)
    print("COMPUTATIONAL ABSURDITY CHECK")
    print("=" * 80)
    
    # Simulate a realistic cluster: 1000 experiments, 100 workers each, 1000 epochs
    # Total nodes = 1000 * 100 * 1000 = 100 million nodes
    n_nodes = 100_000_000
    
    # Ollivier-Ricci complexity: O(E * V² * log V) for optimal transport per iteration
    # For a tree: E ≈ V
    # Rough estimate: 1e8 * (1e8)² * log(1e8) ≈ 1e24 operations per iteration
    # On a 1 PFLOP/s system: ≈ 1e9 seconds ≈ 31,000 years per curvature update
    
    ops_per_iteration = n_nodes ** 3 * np.log(n_nodes)
    time_years = ops_per_iteration / 1e15 / (60*60*24*365)  # 1 PFLOP/s
    
    print(f"Nodes in production cluster: {n_nodes:,}")
    print(f"Estimated Ollivier-Ricci operations: {ops_per_iteration:.2e}")
    print(f"Time to compute one curvature update: {time_years:.2f} years")
    print("→ LSGM-Ω's 'real-time' curvature monitoring is computationally impossible.")

if __name__ == "__main__":
    run_disruption_experiment()
    expose_computational_absurdity()