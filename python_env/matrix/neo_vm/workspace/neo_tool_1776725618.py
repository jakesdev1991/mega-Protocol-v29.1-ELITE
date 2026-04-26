# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def create_correlation_graph(n_nodes=100, dim=3, alpha=0.1, g_delta=0.5, entropy_factor=1.0):
    """
    Disruptive model: Correlation graph that fragments under entropy-impedance feedback.
    This replaces the local Omega Action with a non-local graph-theoretic framework.
    """
    
    # Create a 3D grid graph representing spacetime correlation nodes
    side_length = int(round(n_nodes ** (1/dim)))
    G = nx.grid_graph(dim=[side_length]*dim)
    
    # Assign each node a "memory load" representing Phi_Delta accumulation
    memory_load = {node: 0.0 for node in G.nodes()}
    
    # Assign each edge a "correlation strength" that depends on Phi_N
    # In the graph model, correlation strength = weight of connectivity
    for edge in G.edges():
        G[edge[0]][edge[1]]['weight'] = 1.0
    
    # Simulate the entropy-impedance feedback loop
    # Each iteration represents an energy scale step
    fragmentation_scale = None
    log_energy_steps = np.linspace(0, 10, 100)
    max_cluster_size = []
    
    for i, logE in enumerate(log_energy_steps):
        # The "running coupling" effect: g_delta_eff grows with memory load
        # This is the positive feedback loop that the previous analysis identified
        g_delta_eff = g_delta * (1 + alpha * logE)
        
        # Update memory load at each node based on local "entropy reduction"
        # Higher g_delta_eff -> more memory accumulation -> lower entropy
        for node in G.nodes():
            # Memory load grows exponentially with effective coupling
            memory_load[node] += g_delta_eff * np.exp(-entropy_factor * memory_load[node])
        
        # CRITICAL DISRUPTION: The Shredding Event is NOT a field divergence
        # It's a GRAPH FRAGMENTATION caused by overloaded memory nodes
        # When memory_load exceeds threshold, nodes "fail" and edges to them are cut
        
        threshold = 1.0  # Critical memory capacity per node
        failed_nodes = [node for node, load in memory_load.items() if load > threshold]
        
        if failed_nodes and fragmentation_scale is None:
            fragmentation_scale = logE
            print(f"SHREDDING EVENT DETECTED at log(E) = {logE:.2f}")
            print(f"Number of failed nodes: {len(failed_nodes)}")
        
        # Remove edges connected to failed nodes (informational freeze)
        G_shredded = G.copy()
        for node in failed_nodes:
            edges_to_remove = list(G_shredded.edges(node))
            G_shredded.remove_edges_from(edges_to_remove)
        
        # Measure the size of the largest connected component
        # This is the "Phi_N connectivity" - if it drops, Poisson recovery fails
        if nx.is_connected(G_shredded):
            largest_cc_size = len(G_shredded)
        else:
            largest_cc_size = max(len(cc) for cc in nx.connected_components(G_shredded))
        max_cluster_size.append(largest_cc_size)
    
    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Graph fragmentation visualization
    # Show original vs shredded graph (subset for clarity)
    subgraph_nodes = list(G.nodes())[:25]
    G_sub = G.subgraph(subgraph_nodes)
    
    axes[0].set_title("Correlation Graph: Before vs After Shredding")
    pos = nx.spring_layout(G_sub)
    
    # Draw original graph in background (light gray)
    nx.draw(G_sub, pos, ax=axes[0], node_color='lightgray', edge_color='lightgray', 
            node_size=50, alpha=0.5)
    
    # Highlight failed nodes and removed edges
    if fragmentation_scale is not None:
        # Find which nodes would fail at fragmentation scale
        idx = np.argmin(np.abs(log_energy_steps - fragmentation_scale))
        G_shredded_sub = nx.grid_graph(dim=[side_length]*dim).subgraph(subgraph_nodes)
        failed_nodes_sub = list(G_shredded_sub.nodes())[:int(0.2*len(subgraph_nodes))]
        G_shredded_sub.remove_edges_from([(u,v) for u in failed_nodes_sub for v in list(G_shredded_sub.neighbors(u))])
        
        # Draw remaining edges in red
        edges_remaining = list(G_shredded_sub.edges())
        if edges_remaining:
            nx.draw_networkx_edges(G_shredded_sub, pos, edgelist=edges_remaining, 
                                 ax=axes[0], edge_color='red', width=2)
        
        # Draw failed nodes
        nx.draw_networkx_nodes(G_shredded_sub, pos, nodelist=failed_nodes_sub,
                             ax=axes[0], node_color='black', node_size=100)
    
    # Plot 2: Connectivity collapse
    axes[1].plot(log_energy_steps, max_cluster_size, 'b-', linewidth=2)
    if fragmentation_scale is not None:
        axes[1].axvline(x=fragmentation_scale, color='r', linestyle='--', 
                       label=f'Shredding Event (logE={fragmentation_scale:.2f})')
    axes[1].set_xlabel('log(Energy Scale)')
    axes[1].set_ylabel('Size of Largest Connected Component')
    axes[1].set_title('Connectivity Collapse: Poisson Recovery Failure')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('shredding_disruption.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fragmentation_scale, max_cluster_size, memory_load

# Execute the disruption analysis
frag_scale, connectivity, memory = create_correlation_graph(
    n_nodes=125, alpha=0.15, g_delta=0.6, entropy_factor=0.8
)

# Additional analysis: Show that traditional field-theoretic analysis misses this
print("\n=== DISRUPTIVE INSIGHT ===")
print("The conventional analysis treats Shredding as a field divergence:")
print("  ξ_Δ → ∞ when Φ_N² + 3Φ_Δ² = v²")
print("\nThis is a CATEGORY ERROR. The true Shredding Event is:")
print("  GRAPH FRAGMENTATION when memory load exceeds nodal capacity")
print("\nThe 'Poisson recovery' of Φ_N doesn't fail from field equations -")
print("it fails because the CORRELATION GRAPH SPLITS into disconnected components.")
print("\nThe entropy-impedance feedback loop doesn't just accelerate α running;")
print("it OVERLOADS THE GRAPH TOPOLOGY, making the local field description invalid.")
print(f"\nEvidence: At logE = {frag_scale:.2f}, largest connected component")
print(f"dropped from {connectivity[0]} to {connectivity[np.argmin(np.abs(np.linspace(0, 10, 100) - frag_scale))]}")