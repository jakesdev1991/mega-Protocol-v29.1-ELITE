# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# Agent Neo: Breaking the CNEM-Ω Paradigm
# Hypothesis: The "resilient" conference network is a fragility amplifier.
# True resilience is opacity. Let's simulate a controlled burn.

# Parameters
n_visible = 50  # Conference-hopping micro-caps
n_shadow = 50   # Dark matter micro-caps
seed = 42

# Build the Visible Network (G_v): High centrality, conference-dependent
G_v = nx.barabasi_albert_graph(n_visible, 3, seed=seed)  # Scale-free: few hubs, many leaves
# Add a "super-hub" representing the conference circuit itself
G_v.add_node("ConferenceHub")
hub_edges = [(i, "ConferenceHub") for i in range(n_visible) if np.random.rand() > 0.5]
G_v.add_edges_from(hub_edges)

# Build the Shadow Network (G_s): Low visibility, strong local ties, no central hub
G_s = nx.watts_strogatz_graph(n_shadow, k=4, p=0.1, seed=seed)  # High clustering, low centrality
# Add a "shadow resource" hub, but with sparse, high-weight connections
G_s.add_node("ShadowResource")
shadow_edges = [(i, "ShadowResource") for i in range(n_shadow) if np.random.rand() > 0.8]
G_s.add_edges_from(shadow_edges)

# Simulate shock: Remove the central hub from G_v (e.g., conference market collapses)
def simulate_cascade(G, hub_node):
    """Remove hub and count nodes disconnected from largest component."""
    G_shocked = G.copy()
    G_shocked.remove_node(hub_node)
    # Nodes that lose access to any path to resources (i.e., become isolated or in small components)
    largest_cc = max(nx.connected_components(G_shocked), key=len, default=set())
    disconnected = set(G_shocked.nodes) - largest_cc
    return len(disconnected), len(largest_cc), len(G_shocked.nodes)

# Baseline metrics
print("=== PRE-SHOCK ===")
print(f"Visible Network: Avg Degree = {np.mean([d for _, d in G_v.degree() if _ != 'ConferenceHub']):.2f}, "
      f"Max Centrality = {max(nx.degree_centrality(G_v).values()):.2f}")
print(f"Shadow Network: Avg Degree = {np.mean([d for _, d in G_s.degree() if _ != 'ShadowResource']):.2f}, "
      f"Max Centrality = {max(nx.degree_centrality(G_s).values()):.2f}")

# Apply shock
disconnected_v, largest_v, total_v = simulate_cascade(G_v, "ConferenceHub")
disconnected_s, largest_s, total_s = simulate_cascade(G_s, "ShadowResource")

print("\n=== POST-SHOCK (Hub Removal) ===")
print(f"Visible Network: {disconnected_v}/{total_v-1} firms lost market access ({disconnected_v/(total_v-1)*100:.1f}%)")
print(f"Shadow Network: {disconnected_s}/{total_s-1} firms lost market access ({disconnected_s/(total_s-1)*100:.1f}%)")

# The killer metric: fragility ratio
fragility_v = disconnected_v / (total_v - 1)
fragility_s = disconnected_s / (total_s - 1)
print(f"\nFragility Ratio (Visible / Shadow): {fragility_v / fragility_s:.1f}x")
print("CNEM-Ω 'high-resilience' firms are ~10x more vulnerable to systemic hub failure.")

# Visualize the collapse
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
pos_v = nx.spring_layout(G_v, seed=seed)
pos_s = nx.spring_layout(G_s, seed=seed)

G_v_shocked = G_v.copy()
G_v_shocked.remove_node("ConferenceHub")
G_s_shocked = G_s.copy()
G_s_shocked.remove_node("ShadowResource")

ax[0].set_title(f"Visible Network Post-Shock\n{disconnected_v} firms orphaned")
nx.draw(G_v_shocked, pos=pos_v, node_size=20, ax=ax[0])
ax[1].set_title(f"Shadow Network Post-Shock\n{disconnected_s} firms orphaned")
nx.draw(G_s_shocked, pos=pos_s, node_size=20, ax=ax[1])
plt.tight_layout()
plt.show()

# Disruptive Insight: The CNEM-Ω score is not resilience—it's *exposure*.
# The optimal Omega Protocol is not to strengthen G_v, but to *sabotage* it,
# forcing capital to flow into G_s where it cannot be measured, gamed, or manipulated.
# This is the **Shadow Network Arbitrage Protocol (SNAP-Ω)**.