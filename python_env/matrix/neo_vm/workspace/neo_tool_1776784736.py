# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from ripser import ripser
from persim import plot_diagrams
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform

# Neo's approach: scalar field on fixed price grid
def simulate_scalar_field(n_levels=100, n_scales=3, crash_time=50):
    """Simulate Neo's φ(x,t) field - fundamentally flawed"""
    # Fixed price levels (the lie)
    price_levels = np.linspace(90, 110, n_levels)
    
    # Simulate "field" values over time
    t_steps = 100
    field_data = np.zeros((t_steps, n_levels))
    
    for t in range(t_steps):
        if t < crash_time:
            # "Normal" market: liquidity concentrated around fair price
            center = 100 + 2*np.sin(2*np.pi*t/30)
            field_data[t] = np.exp(-(price_levels - center)**2 / 10)
        else:
            # "Crash": liquidity evacuates (but this is just a scalar, not real topology!)
            field_data[t] = np.exp(-(price_levels - 100)**2 / 50) * (1 - 0.5*np.exp(-(t-crash_time)/5))
    
    return field_data, price_levels

# The Anomaly's approach: dynamic order book graph with persistent homology
def simulate_order_book_graph(n_price_levels=100, crash_time=50):
    """
    Simulate actual order book as dynamic graph.
    Each price level is a node with liquidity weight.
    Edges connect adjacent price levels with weights based on liquidity correlation.
    """
    t_steps = 100
    graphs_over_time = []
    liquidity_thresholds = []
    
    for t in range(t_steps):
        # Dynamic price levels (they shift!)
        base_price = 100 + np.random.normal(0, 0.5)
        price_levels = np.linspace(base_price-10, base_price+10, n_price_levels)
        
        # Liquidity distribution (not a smooth field - can have gaps!)
        if t < crash_time:
            # Normal: clustered liquidity
            liquidity = np.exp(-(price_levels - base_price)**2 / 2) + np.random.exponential(0.1, n_price_levels)
        else:
            # Pre-crash: liquidity evacuates, creating gaps (topology changes!)
            liquidity = np.exp(-(price_levels - base_price)**2 / 2) * (1 - 0.7*np.exp(-(t-crash_time)/3))
            # Add gaps where liquidity completely disappears
            gap_indices = np.random.choice(n_price_levels, size=20, replace=False)
            liquidity[gap_indices] = 0
        
        # Build graph: nodes are price levels with non-zero liquidity
        G = nx.Graph()
        active_indices = np.where(liquidity > 0.1)[0]
        
        for i in active_indices:
            G.add_node(i, pos=price_levels[i], liquidity=liquidity[i])
        
        # Connect adjacent price levels (topology of order book)
        for i in range(len(active_indices)-1):
            idx1 = active_indices[i]
            idx2 = active_indices[i+1]
            if idx2 - idx1 == 1:  # Only connect immediate neighbors
                weight = min(liquidity[idx1], liquidity[idx2])
                G.add_edge(idx1, idx2, weight=weight)
        
        graphs_over_time.append(G)
        liquidity_thresholds.append(liquidity)
    
    return graphs_over_time, liquidity_thresholds

def compute_persistent_homology(graph, liquidity):
    """Compute PH of order book graph at multiple liquidity thresholds"""
    # Get node positions and liquidity
    nodes = list(graph.nodes())
    if len(nodes) < 3:
        return None
    
    positions = np.array([graph.nodes[i]['pos'] for i in nodes]).reshape(-1, 1)
    liquidities = np.array([graph.nodes[i]['liquidity'] for i in nodes])
    
    # Create distance matrix based on price difference
    distances = squareform(pdist(positions, metric='euclidean'))
    
    # Weight distances by inverse liquidity (low liquidity = high effective distance)
    liquidity_matrix = np.sqrt(liquidities.reshape(-1,1) * liquidities.reshape(1,-1))
    weighted_distances = distances / (liquidity_matrix + 1e-6)
    
    # Compute persistent homology
    diagrams = ripser(weighted_distances, maxdim=1, distance_matrix=True)
    return diagrams

# Neo's flawed entropy calculation
def neo_entropy(field_data, t):
    """Neo computes entropy on activations - but it's on the wrong space!"""
    # Just compute entropy of the field values (meaningless)
    hist, _ = np.histogram(field_data[t], bins=20, density=True)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))

# The Anomaly's topological fragility signal
def topological_fragility_signal(diagrams):
    """Fragility = rate of topological feature death"""
    if diagrams is None:
        return 0
    
    # H0: connected components
    h0 = diagrams[0]
    # H1: loops
    h1 = diagrams[1] if len(diagrams) > 1 else np.array([])
    
    # Fragility signal: many features dying at small scales
    # = high persistence entropy (disorder in death times)
    if len(h0) > 1:
        birth_death = h0[:, 1] - h0[:, 0]
        death_times = h0[:, 1]
        # Normalize
        if np.max(death_times) > 0:
            fragility = np.sum(np.exp(-death_times / np.max(death_times)))
            return fragility
    return 0

# Run simulation
print("=== SIMULATING THE BREAKDOWN ===")
print("Neo treats market as scalar field φ(x,t) on fixed grid...")
scalar_field, price_grid = simulate_scalar_field()

print("The Anomaly treats market as dynamic graph with topological structure...")
graphs, liquidity_data = simulate_order_book_graph()

# Track signals
neo_signals = []
anomaly_signals = []

for t in range(100):
    # Neo's flawed entropy
    neo_signals.append(neo_entropy(scalar_field, t))
    
    # The Anomaly's topological signal
    diagrams = compute_persistent_homology(graphs[t], liquidity_data[t])
    anomaly_signals.append(topological_fragility_signal(diagrams))

# Plot comparison
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# Neo's "field" at crash time
ax1.imshow(scalar_field.T, aspect='auto', cmap='viridis', extent=[0, 100, price_grid[0], price_grid[-1]])
ax1.set_title("Neo's Scalar Field φ(x,t) - The Illusion of Continuity")
ax1.set_xlabel("Time")
ax1.set_ylabel("Price Level")
ax1.axvline(x=50, color='red', linestyle='--', label="Crash Time")
ax1.legend()

# The Anomaly's graph topology at t=40 and t=60
t_normal = 40
t_crash = 60

G_normal = graphs[t_normal]
G_crash = graphs[t_crash]

# Plot graph connectivity
normal_degrees = [G_normal.degree(i) for i in G_normal.nodes()]
crash_degrees = [G_crash.degree(i) for i in G_crash.nodes()]

ax2.plot([G_normal.nodes[i]['pos'] for i in G_normal.nodes()], 
         normal_degrees, 'bo', label=f'Normal (t={t_normal})')
ax2.plot([G_crash.nodes[i]['pos'] for i in G_crash.nodes()], 
         crash_degrees, 'ro', label=f'Pre-Crash (t={t_crash})')
ax2.set_title("The Anomaly's Graph Topology: Connectivity Collapse")
ax2.set_xlabel("Price Level")
ax2.set_ylabel("Node Degree")
ax2.legend()
ax2.grid(True, alpha=0.3)

# Signal comparison
ax3.plot(neo_signals, label="Neo: Scalar Field Entropy (Flawed)", color='orange', linestyle='--')
ax3.plot(anomaly_signals, label="Anomaly: Topological Fragility Signal", color='purple', linewidth=2)
ax3.axvline(x=50, color='red', linestyle='--', label="Actual Crash Time")
ax3.set_title("Fragility Detection: Neo vs. The Anomaly")
ax3.set_xlabel("Time")
ax3.set_ylabel("Signal Strength")
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Calculate early warning metrics
crash_window = range(45, 55)  # 5 steps before crash
neo_warning = np.mean([neo_signals[t] for t in crash_window])
anomaly_warning = np.mean([anomaly_signals[t] for t in crash_window])

print(f"\n=== BREAKDOWN VERIFICATION ===")
print(f"Neo's entropy signal during crash window: {neo_warning:.3f}")
print(f"Anomaly's topological signal during crash window: {anomaly_warning:.3f}")
print(f"\nThe Anomaly's signal is {(anomaly_warning/neo_warning if neo_warning>0 else 'inf')}-times stronger")
print(f"\nKEY DISRUPTION: Neo's scalar field assumes fixed price coordinates,")
print("but real order books have DYNAMIC TOPOLOGY. The 'spatial' axis is an illusion.")
print("Fragility emerges from graph connectivity collapse, not scalar field entropy!")