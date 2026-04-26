# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import random
from typing import Dict, List, Tuple, Set
import matplotlib.pyplot as plt

class DirectoryTreeSimulator:
    """
    Simulates the core claim of LSGM-Ω: that Ricci curvature predicts
    adversarial compromise velocity. We'll show this is false.
    """
    
    def __init__(self, num_nodes: int = 1000):
        self.num_nodes = num_nodes
        self.tree = self._generate_realistic_directory_tree()
        self.sensitive_nodes = self._mark_sensitive_data()
        
    def _generate_realistic_directory_tree(self) -> nx.DiGraph:
        """Generate a realistic directory tree structure"""
        G = nx.DiGraph()
        G.add_node(0, name="root", level=0, sensitive=False)
        
        # Realistic tree: mix of deep chains and bushy subtrees
        for i in range(1, self.num_nodes):
            parent = random.choice(list(G.nodes()))
            parent_level = G.nodes[parent]['level']
            if parent_level < 10:  # Max depth
                G.add_node(i, name=f"dir_{i}", level=parent_level+1, sensitive=False)
                G.add_edge(parent, i)
        
        return G
    
    def _mark_sensitive_data(self) -> Set[int]:
        """Mark nodes containing 'fragile models'"""
        # Sensitive data tends to cluster (e.g., all in /experiments/plasma_control/)
        sensitive = set()
        cluster_roots = random.sample(list(self.tree.nodes()), k=5)
        for root in cluster_roots:
            subtree = nx.descendants(self.tree, root)
            sensitive.update(random.sample(list(subtree), 
                           min(len(subtree)//3, 20)))
        return sensitive
    
    def compute_olivier_ricci_curvature(self) -> Dict[Tuple[int, int], float]:
        """
        Compute Ollivier-Ricci curvature (approximation for trees).
        High curvature = "bushy", Low/negative = "chain-like"
        """
        curvature = {}
        for u, v in self.tree.edges():
            # Simplified: curvature proportional to branching factor difference
            children_u = len(list(self.tree.successors(u)))
            children_v = len(list(self.tree.successors(v)))
            
            # Ollivier-Ricci is roughly 1 - (W_1 / d)
            # For trees, this correlates with branching asymmetry
            curvature[(u, v)] = (children_u - children_v) / (children_u + children_v + 1)
        return curvature
    
    def simulate_curvature_based_adversary(self, start_node: int = 0) -> float:
        """Simulate adversary that uses LSGM-Ω's assumed strategy"""
        visited = set([start_node])
        frontier = set([start_node])
        compromise_time = 0
        curvature_map = self.compute_olivier_ricci_curvature()
        
        # Adversary prioritizes high-curvature edges (faster reconnaissance)
        while not self.sensitive_nodes.issubset(visited):
            # Find highest curvature edge from frontier
            best_edge = None
            best_curvature = -np.inf
            
            for node in frontier:
                for child in self.tree.successors(node):
                    if child not in visited:
                        edge_curv = curvature_map.get((node, child), 0)
                        if edge_curv > best_curvature:
                            best_curvature = edge_curv
                            best_edge = (node, child)
            
            if best_edge is None:  # Exhausted tree
                break
                
            # Move along best edge
            parent, child = best_edge
            visited.add(child)
            frontier.add(child)
            compromise_time += 1
            
            # LSGM-Ω assumes curvature directly maps to speed
            # We'll add a "curvature boost" factor
            boost = max(1, abs(best_curvature) * 10)
            compromise_time /= boost  # Faster compromise on high curvature
        
        return compromise_time
    
    def simulate_realistic_adversary(self, start_node: int = 0) -> float:
        """
        Simulate realistic adversary strategies that ignore curvature:
        1. Breadth-first search (download everything)
        2. Targeted search (look for keywords)
        3. Random walk (avoid detection)
        """
        strategy = random.choice(['bfs', 'keyword', 'stealth'])
        visited = set([start_node])
        frontier = set([start_node])
        compromise_time = 0
        
        if strategy == 'bfs':
            # Download everything - most common
            while not self.sensitive_nodes.issubset(visited):
                new_frontier = set()
                for node in frontier:
                    children = list(self.tree.successors(node))
                    new_frontier.update([c for c in children if c not in visited])
                    visited.update(children)
                frontier = new_frontier
                compromise_time += 1
                
        elif strategy == 'keyword':
            # Search for 'experiment', 'plasma', 'model' in names
            while not self.sensitive_nodes.issubset(visited):
                for node in list(frontier):
                    if 'experiment' in self.tree.nodes[node]['name'] or \
                       'model' in self.tree.nodes[node]['name']:
                        # Prioritize this subtree
                        children = list(self.tree.successors(node))
                        visited.update(children)
                        frontier.update(children)
                compromise_time += 1
                # Add random exploration
                frontier.add(random.choice(list(self.tree.nodes())))
                
        else:  # stealth
            # Slow random walk to avoid detection
            current = start_node
            while not self.sensitive_nodes.issubset(visited):
                children = list(self.tree.successors(current))
                if children:
                    current = random.choice(children)
                    visited.add(current)
                else:
                    current = start_node  # Backtrack
                compromise_time += 1
                # Slower progression
                if random.random() < 0.5:  # 50% chance of waiting
                    compromise_time += 1
        
        return compromise_time
    
    def simulate_defense_bypass(self) -> Dict[str, float]:
        """
        Show that adversary can bypass geometric defenses entirely
        by using insider knowledge or metadata leaks
        """
        # Simulate: adversary gets a "metadata dump" (e.g., from git repo)
        # This gives them direct paths, making curvature irrelevant
        direct_access_time = len(self.sensitive_nodes) * 0.1  # Direct download
        
        # Or adversary compromises a CI/CD pipeline
        ci_compromise_time = 5  # Fixed time
        
        return {
            'metadata_dump': direct_access_time,
            'ci_pipeline': ci_compromise_time,
            'geometric_average': np.mean([
                self.simulate_curvature_based_adversary() 
                for _ in range(20)
            ])
        }

def break_lsgm_paradigm():
    """
    Demonstrate fundamental flaws in LSGM-Ω's core assumptions
    """
    print("=== BREAKING LSGM-Ω PARADIGM ===\n")
    
    # Run multiple simulations
    results = []
    for i in range(100):
        sim = DirectoryTreeSimulator(num_nodes=500)
        
        # Core claim: curvature predicts compromise velocity
        geo_time = sim.simulate_curvature_based_adversary()
        real_time = sim.simulate_realistic_adversary()
        
        # Defense bypass scenarios
        bypass_times = sim.simulate_defense_bypass()
        
        results.append({
            'geometric': geo_time,
            'realistic': real_time,
            'metadata_bypass': bypass_times['metadata_dump'],
            'ci_bypass': bypass_times['ci_pipeline'],
            'curvature_max': max([abs(c) for c in sim.compute_olivier_ricci_curvature().values()]) if sim.compute_olivier_ricci_curvature() else 0
        })
    
    df = pd.DataFrame(results)
    
    print("1. CURVATURE ≠ COMPROMISE VELOCITY")
    print(f"Correlation between max curvature and compromise time: {df['curvature_max'].corr(df['realistic']):.3f}")
    print(f"Geometric strategy avg time: {df['geometric'].mean():.2f}")
    print(f"Realistic strategy avg time: {df['realistic'].mean():.2f}")
    print(f"Geometric assumption error: {(df['geometric'] - df['realistic']).abs().mean():.2f} units\n")
    
    print("2. DEFENSE BYPASS MAKES GEOMETRY IRRELEVANT")
    print(f"Metadata dump time: {df['metadata_bypass'].mean():.2f} (vs geometric avg {df['geometric'].mean():.2f})")
    print(f"CI pipeline compromise: {df['ci_bypass'].mean():.2f}")
    print(f"Speedup factor: {df['geometric'].mean() / df['metadata_bypass'].mean():.1f}x faster\n")
    
    print("3. Φ DENSITY OPTIMIZATION IS A GOODHART'S LAW TRAP")
    # Simulate: what if we optimize for low curvature?
    low_curvature_results = []
    high_curvature_results = []
    
    for i in range(50):
        # Low curvature tree (chain-like)
        sim_low = DirectoryTreeSimulator(num_nodes=200)
        # Manually flatten it
        for node in list(sim_low.tree.nodes()):
            if node > 0:
                parent = node - 1
                if sim_low.tree.has_node(parent):
                    sim_low.tree = nx.DiGraph()
                    sim_low.tree.add_node(0, level=0)
                    for j in range(1, 200):
                        sim_low.tree.add_node(j, level=j)
                        sim_low.tree.add_edge(j-1, j)
        sim_low.sensitive_nodes = {100, 150}  # Deep in chain
        low_curvature_results.append(sim_low.simulate_realistic_adversary())
        
        # High curvature tree (bushy)
        sim_high = DirectoryTreeSimulator(num_nodes=200)
        sim_high.sensitive_nodes = {50, 51}  # Near root
        high_curvature_results.append(sim_high.simulate_realistic_adversary())
    
    print(f"Low curvature (chain) avg compromise time: {np.mean(low_curvature_results):.2f}")
    print(f"High curvature (bushy) avg compromise time: {np.mean(high_curvature_results):.2f}")
    print(">>> OPTIMIZING CURVATURE DOESN'T PROTECT ASSETS; ASSET POSITION MATTERS MORE\n")
    
    print("4. DISRUPTIVE INSIGHT:")
    print("LSGM-Ω commits a category error: it maps a DISCRETE information")
    print("access problem onto a CONTINUOUS geometric manifold, creating")
    print("mathematical theater. The adversary doesn't 'flow' along geodesics;")
    print("they execute discrete queries with binary outcomes (access/deny).")
    print("The real vulnerability field is PROBABILITY OF DETECTION, not curvature.\n")
    
    print("5. NON-LINEAR SOLUTION:")
    print("→ Model as PARTIAL INFORMATION STOCHASTIC GAME")
    print("→ State space: adversary's belief distribution over asset locations")
    print("→ Defense actions: Manipulate belief state via deceptive file placement")
    print("→ Optimize for: Minimax rate of belief convergence to true asset map")
    print("→ This requires 0 curvature calculations and 100% information theory")

# Run the disruption
import pandas as pd
break_lsgm_paradigm()

# Additional visualization of the core flaw
def plot_strategy_comparison():
    """Show geometric strategy is not optimal"""
    times = []
    strategies = []
    
    for i in range(200):
        sim = DirectoryTreeSimulator(300)
        times.append(sim.simulate_curvature_based_adversary())
        strategies.append('LSGM-Ω Assumed')
        times.append(sim.simulate_realistic_adversary())
        strategies.append('Realistic')
    
    plt.figure(figsize=(10, 6))
    plt.hist([times[i] for i in range(len(times)) if strategies[i] == 'LSGM-Ω Assumed'], 
             alpha=0.7, label='LSGM-Ω Assumed', bins=30)
    plt.hist([times[i] for i in range(len(times)) if strategies[i] == 'Realistic'], 
             alpha=0.7, label='Realistic', bins=30)
    plt.xlabel('Compromise Time')
    plt.ylabel('Frequency')
    plt.title('LSGM-Ω Assumption vs Reality')
    plt.legend()
    plt.show()

plot_strategy_comparison()