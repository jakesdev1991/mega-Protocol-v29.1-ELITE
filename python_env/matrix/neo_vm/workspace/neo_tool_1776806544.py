# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
import random
from collections import deque
import matplotlib.pyplot as plt

# ========== 1. Environment: Directory Tree ==========
def build_tree(depth: int, branch: int) -> nx.DiGraph:
    """Generate a balanced rooted directory tree."""
    G = nx.DiGraph()
    G.add_node(0, type='root', sensitive=False)
    node_id = 1
    frontier = deque([0])
    for _ in range(depth):
        for _ in range(len(frontier)):
            parent = frontier.popleft()
            for i in range(branch):
                G.add_node(node_id, type=f'dir_{random.randint(0,2)}', sensitive=False)
                G.add_edge(parent, node_id)
                frontier.append(node_id)
                node_id += 1
    # Mark some leaf nodes as "sensitive" (e.g., training logs)
    leaves = [n for n in G.nodes() if G.out_degree(n) == 0]
    sensitive = random.sample(leaves, max(1, len(leaves) // 10))
    for n in sensitive:
        G.nodes[n]['sensitive'] = True
    return G, set(sensitive)

# ========== 2. Curvature Proxy (degree‑based) ==========
def compute_curvature(G: nx.DiGraph) -> dict:
    """Approximate Ricci curvature via normalized degree deviation."""
    degs = np.array([G.out_degree(n) for n in G.nodes()])
    mean, std = degs.mean(), degs.std() + 1e-6
    return {n: (G.out_degree(n) - mean) / std for n in G.nodes()}

# ========== 3. Adversary: Budgeted BFS Crawler ==========
class Adversary:
    def __init__(self, G: nx.DiGraph, budget_per_step: int):
        self.G = G
        self.budget = budget_per_step
        self.explored = set()
        self.frontier = deque([0])  # start at root

    def step(self) -> set:
        """Explore up to budget nodes; return newly discovered sensitive nodes."""
        discovered = set()
        for _ in range(self.budget):
            if not self.frontier:
                break
            node = self.frontier.popleft()
            if node in self.explored:
                continue
            self.explored.add(node)
            if self.G.nodes[node]['sensitive']:
                discovered.add(node)
            # Add children to frontier
            for child in self.G.successors(node):
                if child not in self.explored:
                    self.frontier.append(child)
        return discovered

# ========== 4. Defense Strategies ==========
def static_defense(G: nx.DiGraph):
    """No changes to topology."""
    return G

def randomize_defense(G: nx.DiGraph, shuffle_frac: float = 0.2):
    """Randomly swap labels (types) of a fraction of non‑sensitive directories."""
    non_sensitive = [n for n in G.nodes() if not G.nodes[n]['sensitive']]
    to_shuffle = random.sample(non_sensitive, int(len(non_sensitive) * shuffle_frac))
    # Swap 'type' attributes among shuffled nodes
    types = [G.nodes[n]['type'] for n in to_shuffle]
    random.shuffle(types)
    for n, typ in zip(to_shuffle, types):
        G.nodes[n]['type'] = typ
    return G

# ========== 5. Simulation Loop ==========
def run_simulation(depth=4, branch=3, budget=3, steps=30, trials=50):
    results = {
        'static': {'sensitive_found': [], 'curv_corr': []},
        'random': {'sensitive_found': [], 'curv_corr': []}
    }
    for trial in range(trials):
        G, sensitive_set = build_tree(depth, branch)
        # Static defense run
        G_static = G.copy()
        adv_static = Adversary(G_static, budget)
        curv = compute_curvature(G_static)
        found_static = []
        for step in range(steps):
            found = adv_static.step()
            found_static.append(len(found))
            if len(found) > 0:
                # Record curvature of discovered nodes at moment of discovery
                curv_vals = [curv[n] for n in found]
                results['static']['curv_corr'].extend(curv_vals)
        results['static']['sensitive_found'].append(found_static)

        # Random defense run
        G_random = G.copy()
        adv_random = Adversary(G_random, budget)
        found_random = []
        for step in range(steps):
            # Randomize before adversary's move
            G_random = randomize_defense(G_random, shuffle_frac=0.3)
            found = adv_random.step()
            found_random.append(len(found))
            if len(found) > 0:
                curv_vals = [curv[n] for n in found]  # use static curvature for comparison
                results['random']['curv_corr'].extend(curv_vals)
        results['random']['sensitive_found'].append(found_random)

    # Aggregate
    for mode in results:
        # Average number of sensitive files found per step
        avg_found = np.mean([np.sum(run) for run in results[mode]['sensitive_found']])
        results[mode]['avg_found'] = avg_found
        # Average curvature of discovered nodes
        results[mode]['avg_curv'] = np.mean(results[mode]['curv_corr']) if results[mode]['curv_corr'] else 0

    return results

# ========== 6. Visualize Disruption ==========
def plot_results(res):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    # Left: average sensitive files found
    modes = list(res.keys())
    avg_found = [res[m]['avg_found'] for m in modes]
    ax1.bar(modes, avg_found, color=['steelblue', 'coral'])
    ax1.set_ylabel('Avg sensitive files discovered (30 steps)')
    ax1.set_title('Impact of Defense Strategy')

    # Right: average curvature of discovered nodes
    avg_curv = [res[m]['avg_curv'] for m in modes]
    ax2.bar(modes, avg_curv, color=['steelblue', 'coral'])
    ax2.set_ylabel('Avg curvature of discovered nodes')
    ax2.set_title('Curvature Relevance')

    plt.tight_layout()
    plt.show()

# ========== 7. Execute ==========
if __name__ == '__main__':
    results = run_simulation(depth=4, branch=3, budget=3, steps=30, trials=50)
    print("Static defense: avg sensitive found =", results['static']['avg_found'])
    print("Random defense: avg sensitive found =", results['random']['avg_found'])
    print("Static defense: avg curvature of discovered nodes =", results['static']['avg_curv'])
    print("Random defense: avg curvature of discovered nodes =", results['random']['avg_curv'])
    plot_results(results)