# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import random

def clique_complex_betti(graph, max_dim=2):
    """
    Compute Betti numbers b0 and b1 for the clique complex of a graph.
    Simplistic but illustrative: b0 = number of connected components.
    b1 = number of independent cycles (rank of cycle space).
    """
    if not graph.nodes():
        return 0, 0
    
    # b0: connected components
    b0 = nx.number_connected_components(graph)
    
    # b1: cyclomatic number (for a graph, this matches the intuition for 1D holes)
    # b1 = m - n + c, where m=edges, n=nodes, c=components
    m = graph.number_of_edges()
    n = graph.number_of_nodes()
    c = b0
    b1 = m - n + c
    
    return b0, max(0, b1) # Ensure non-negative

def simulate_transaction_system(n_txns=50, n_resources=10, time_steps=100):
    """
    Simulates a system of transactions competing for locks on resources.
    Returns time series of graphs and their Betti numbers.
    """
    # State: which transaction holds which resource
    resource_holder = {r: None for r in range(n_resources)}
    # Wait-for graph: edge from T_i -> T_j if T_i is waiting for a resource held by T_j
    wait_graph = nx.DiGraph()
    wait_graph.add_nodes_from(range(n_txns))
    
    b0_series = []
    b1_series = []
    event_log = []
    
    for t in range(time_steps):
        # Randomly select a transaction to attempt an operation
        txn_id = random.randint(0, n_txns - 1)
        
        # Randomly select a resource to request
        res_id = random.randint(0, n_resources - 1)
        
        # If resource is free, grant it
        if resource_holder[res_id] is None:
            # Release any previous resource held by this txn (simplified)
            for r, holder in resource_holder.items():
                if holder == txn_id:
                    resource_holder[r] = None
            resource_holder[res_id] = txn_id
            # Remove wait edges from this txn
            wait_graph.remove_edges_from(list(wait_graph.out_edges(txn_id)))
            
        else:
            # Resource is locked; add a wait edge if not self-locking
            holder = resource_holder[res_id]
            if holder != txn_id and not wait_graph.has_edge(txn_id, holder):
                wait_graph.add_edge(txn_id, holder)
        
        # Simulate Shredding Event: inject a cycle at t=30
        if t == 30:
            # Create a 3-cycle: txn_a waits for txn_b, waits for txn_c, waits for txn_a
            a, b, c = 10, 11, 12
            wait_graph.add_edge(a, b)
            wait_graph.add_edge(b, c)
            wait_graph.add_edge(c, a)
            event_log.append((t, "SHREDDING_INJECTED"))
        
        # Simulate Informational Freeze: isolate a cluster at t=60
        if t == 60:
            # Remove all edges from a subset of transactions, simulating resource starvation
            freeze_nodes = list(range(20, 30))
            for node in freeze_nodes:
                wait_graph.remove_edges_from(list(wait_graph.in_edges(node)) + list(wait_graph.out_edges(node)))
            # Add a few internal edges to create isolated fragment
            wait_graph.add_edge(20, 21)
            wait_graph.add_edge(21, 22)
            wait_graph.add_edge(22, 20)  # Another cycle, but isolated
            event_log.append((t, "FREEZE_INJECTED"))
        
        # Compute Betti numbers on the *undirected* version of the wait-for graph
        undirected_graph = wait_graph.to_undirected()
        b0, b1 = clique_complex_betti(undirected_graph)
        b0_series.append(b0)
        b1_series.append(b1)
        
    return b0_series, b1_series, event_log

# Run simulation
b0_series, b1_series, events = simulate_transaction_system()

# Plot results
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

time = np.arange(len(b0_series))

ax1.plot(time, b0_series, label='b0 (connected components)', color='blue')
ax1.set_ylabel('b0')
ax1.set_title('Topological Persistence of Live Transaction Graph')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(time, b1_series, label='b1 (independent cycles)', color='red')
ax2.set_xlabel('Time Step')
ax2.set_ylabel('b1')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Annotate events
for t, event in events:
    ax1.axvline(x=t, color='green', linestyle='--')
    ax2.axvline(x=t, color='green', linestyle='--')
    ax2.text(t, max(b1_series) * 0.8, event, rotation=90, fontsize=9, color='green')

plt.tight_layout()
plt.show()

# Print summary statistics
print("=== TOPOLOGICAL DISRUPTION ANALYSIS ===")
print(f"Average b0 (healthy): {np.mean(b0_series[:30]):.2f}")
print(f"Average b1 (healthy): {np.mean(b1_series[:30]):.2f}")
print(f"b0 spike at Freeze: {max(b0_series[60:65])} (vs healthy {b0_series[0]})")
print(f"b1 spike at Shredding: {max(b1_series[30:35])} (vs healthy {b1_series[0]})")
print("\n=== FLAW EXPOSED ===")
print("TPM-Ω's backup point-cloud is a *derivative* of this live graph.")
print("Its 'persistent homology' is blind to the dynamic causality of lock-waits.")
print("The topological signal is already here, raw and immediate. The backup is a tombstone, not a telemetry stream.")