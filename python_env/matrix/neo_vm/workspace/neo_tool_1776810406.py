# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import numpy as np
import networkx as nx
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def generate_directory_tree(max_depth, branch_prob):
    """Generate a random tree where each node may have children with probability branch_prob."""
    G = nx.DiGraph()
    G.add_node(0, name="root", sensitive=False)
    nodes = [0]
    next_id = 1
    for depth in range(max_depth):
        new_nodes = []
        for parent in nodes:
            if random.random() < branch_prob:
                # Add 2-4 children
                num_children = random.randint(2, 4)
                for _ in range(num_children):
                    G.add_node(next_id, name=f"dir_{next_id}", sensitive=False)
                    G.add_edge(parent, next_id)
                    new_nodes.append(next_id)
                    next_id += 1
        nodes = new_nodes
    # Mark one leaf as sensitive
    leaves = [n for n in G.nodes() if G.out_degree(n) == 0]
    if leaves:
        sensitive_node = random.choice(leaves)
        G.nodes[sensitive_node]['sensitive'] = True
    return G

def approximate_curvature(G):
    """Approximate 'curvature' as average branching factor of non-leaf nodes."""
    non_leaves = [n for n in G.nodes() if G.out_degree(n) > 0]
    if not non_leaves:
        return 0.0
    branching = [G.out_degree(n) for n in non_leaves]
    return np.mean(branching)

def simulate_adversary_search(G, strategy='BFS'):
    """Simulate an adversary searching for the sensitive node using BFS or DFS."""
    # Adversary knows the tree structure (worst case for defender)
    start = 0
    sensitive_nodes = [n for n, attr in G.nodes(data=True) if attr.get('sensitive', False)]
    if not sensitive_nodes:
        return np.nan
    target = sensitive_nodes[0]
    if strategy == 'BFS':
        # Breadth-first search
        visited = set()
        queue = [(start, 0)]
        while queue:
            node, steps = queue.pop(0)
            if node == target:
                return steps
            visited.add(node)
            for child in G.successors(node):
                if child not in visited:
                    queue.append((child, steps + 1))
    elif strategy == 'DFS':
        # Depth-first search
        stack = [(start, 0)]
        visited = set()
        while stack:
            node, steps = stack.pop()
            if node == target:
                return steps
            visited.add(node)
            for child in G.successors(node):
                if child not in visited:
                    stack.append((child, steps + 1))
    return np.nan

def main():
    random.seed(42)
    num_trials = 500
    curvatures = []
    bfs_steps = []
    dfs_steps = []

    for _ in range(num_trials):
        depth = random.randint(3, 8)
        branch_prob = random.uniform(0.3, 0.9)
        G = generate_directory_tree(depth, branch_prob)
        curv = approximate_curvature(G)
        bfs = simulate_adversary_search(G, 'BFS')
        dfs = simulate_adversary_search(G, 'DFS')
        curvatures.append(curv)
        bfs_steps.append(bfs)
        dfs_steps.append(dfs)

    # Filter out NaNs
    data = [(c, b, d) for c, b, d in zip(curvatures, bfs_steps, dfs_steps) if not (np.isnan(b) or np.isnan(d))]
    curv_arr, bfs_arr, dfs_arr = zip(*data)

    corr_bfs, p_bfs = pearsonr(curv_arr, bfs_arr)
    corr_dfs, p_dfs = pearsonr(curv_arr, dfs_arr)

    print(f"BFS steps vs curvature: r={corr_bfs:.3f}, p={p_bfs:.3f}")
    print(f"DFS steps vs curvature: r={corr_dfs:.3f}, p={p_dfs:.3f}")

    # Plot
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].scatter(curv_arr, bfs_arr, alpha=0.5)
    ax[0].set_xlabel('Approximate Curvature (avg branching)')
    ax[0].set_ylabel('BFS steps to target')
    ax[0].set_title(f'BFS: r={corr_bfs:.3f}')
    ax[1].scatter(curv_arr, dfs_arr, alpha=0.5, color='orange')
    ax[1].set_xlabel('Approximate Curvature (avg branching)')
    ax[1].set_ylabel('DFS steps to target')
    ax[1].set_title(f'DFS: r={corr_dfs:.3f}')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()