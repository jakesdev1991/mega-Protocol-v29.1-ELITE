# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import random
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def generate_directory_tree(max_depth=5, branching_factor_lambda=2.0):
    """Generate a random directory tree structure."""
    G = nx.DiGraph()
    G.add_node(0, name="root", depth=0, type="dir")
    node_id = 1
    
    def add_children(parent_id, current_depth):
        nonlocal node_id
        if current_depth >= max_depth:
            return
        
        # Number of children drawn from Poisson distribution
        num_children = np.random.poisson(branching_factor_lambda)
        
        for _ in range(num_children):
            if random.random() < 0.3:  # 30% chance it's a "log file"
                node_type = "log"
                name = f"model_epoch{random.randint(0, 1000)}.log"
            else:
                node_type = "dir"
                name = f"exp_{random.randint(0, 999)}"
            
            G.add_node(node_id, name=name, depth=current_depth + 1, type=node_type)
            G.add_edge(parent_id, node_id)
            
            if node_type == "dir":
                add_children(node_id, current_depth + 1)
            node_id += 1
    
    add_children(0, 0)
    return G

def compute_geometric_metrics(G):
    """Compute simple geometric proxies: branching factor, avg depth, 'curvature' proxy."""
    depths = [G.nodes[n]['depth'] for n in G.nodes()]
    avg_depth = np.mean(depths)
    
    # 'Curvature' proxy: variance in branching factor (high = bushy = positive curvature)
    out_degrees = [G.out_degree(n) for n in G.nodes()]
    curvature_proxy = np.var(out_degrees)
    
    # LSFI proxy: combine variance and avg depth
    lsfi_proxy = 1 / (1 + np.exp(-(curvature_proxy - avg_depth * 0.1)))
    
    return {
        'avg_depth': avg_depth,
        'curvature_proxy': curvature_proxy,
        'lsfi_proxy': lsfi_proxy,
        'num_nodes': G.number_of_nodes()
    }

def simulate_geometric_crawler(G, target_node):
    """Simulates an attacker performing random walk on the directory tree."""
    current_node = 0  # Start at root
    steps = 0
    visited = {current_node}
    
    while current_node != target_node and steps < 10000:
        # Get neighbors (children and parent)
        neighbors = list(G.successors(current_node)) + list(G.predecessors(current_node))
        if not neighbors:
            break
        
        current_node = random.choice(neighbors)
        visited.add(current_node)
        steps += 1
    
    return steps, len(visited)

def simulate_strategic_attacker(G, target_pattern="model_epoch"):
    """Simulates an attacker who knows the naming pattern and searches directly."""
    # Finds all log nodes matching pattern
    target_nodes = [n for n in G.nodes() if target_pattern in G.nodes[n]['name']]
    
    if not target_nodes:
        return float('inf'), 0
    
    # Strategic attacker goes straight to the shallowest target
    depths = [G.nodes[n]['depth'] for n in target_nodes]
    min_depth = min(depths)
    shallowest_targets = [n for n in target_nodes if G.nodes[n]['depth'] == min_depth]
    
    # Time to compromise: depth + small search cost for pattern matching
    steps = min_depth + int(np.random.normal(5, 2))  # 5 steps overhead for pattern search
    
    return steps, len(shallowest_targets)

def run_disruption_experiment(num_trials=100):
    """Run experiment comparing geometric model vs strategic attacker."""
    results = []
    
    for _ in range(num_trials):
        # Generate random tree structure
        G = generate_directory_tree(max_depth=random.randint(3, 8), 
                                   branching_factor_lambda=random.uniform(1.5, 4.0))
        
        # Compute geometric metrics
        metrics = compute_geometric_metrics(G)
        
        # Find a target log file for simulation
        log_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'log']
        if not log_nodes:
            continue
        
        target_node = random.choice(log_nodes)
        
        # Simulate both attack strategies
        geo_steps, geo_visited = simulate_geometric_crawler(G, target_node)
        strat_steps, strat_targets = simulate_strategic_attacker(G)
        
        results.append({
            'lsfi_proxy': metrics['lsfi_proxy'],
            'curvature_proxy': metrics['curvature_proxy'],
            'geo_steps': geo_steps,
            'strat_steps': strat_steps,
            'tree_size': metrics['num_nodes']
        })
    
    return pd.DataFrame(results)

# Run the experiment
import pandas as pd
df = run_disruption_experiment(200)

# Analysis: Correlation between geometric metrics and actual compromise time
geo_corr = pearsonr(df['lsfi_proxy'], df['geo_steps'])
strat_corr = pearsonr(df['lsfi_proxy'], df['strat_steps'])

print("=== DISRUPTIVE INSIGHT: GEOMETRIC MODEL vs STRATEGIC REALITY ===")
print(f"\nCorrelation LSFI-Geometric Crawler: {geo_corr[0]:.3f} (p={geo_corr[1]:.3f})")
print(f"Correlation LSFI-Strategic Attacker: {strat_corr[0]:.3f} (p={strat_corr[1]:.3f})")

# Visualize the breakdown
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Left: Geometric crawler (model assumption)
ax1.scatter(df['lsfi_proxy'], df['geo_steps'], alpha=0.6)
ax1.set_xlabel("LSFI Proxy (Higher = More 'Bushy'/High Curvature)")
ax1.set_ylabel("Steps to Compromise (Geometric Crawler)")
ax1.set_title("Model Prediction: Geometry Predicts Compromise Time")
ax1.grid(True, alpha=0.3)

# Right: Strategic attacker (reality)
ax2.scatter(df['lsfi_proxy'], df['strat_steps'], alpha=0.6, color='red')
ax2.set_xlabel("LSFI Proxy (Higher = More 'Bushy'/High Curvature)")
ax2.set_ylabel("Steps to Compromise (Strategic Attacker)")
ax2.set_title("Reality: Geometry is Irrelevant to Strategic Attack")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Additional insight: Show that tree structure doesn't matter for strategic attacker
print("\n=== STRATEGIC ATTACKER PERFORMANCE IS TREE-AGNOSTIC ===")
print(f"Mean steps for strategic attacker: {df['strat_steps'].mean():.1f} ± {df['strat_steps'].std():.1f}")
print(f"Coefficient of variation: {df['strat_steps'].std()/df['strat_steps'].mean():.3f}")
print(f"Correlation with tree size: {pearsonr(df['tree_size'], df['strat_steps'])[0]:.3f}")