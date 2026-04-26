# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from collections import deque

def simulate(N=500, p=0.02, seed_frac=0.05, shock_time=50, shock_size=0.1, steps=100):
    # 1. Create random collaboration network
    G = nx.erdos_renyi_graph(N, p)
    # 2. Initialize thresholds and states
    thresholds = np.random.uniform(0, 1, N)  # each lab's adoption threshold
    adopted = np.zeros(N, dtype=bool)
    validated = np.zeros(N, dtype=bool)
    # 3. Seed a small fraction of early adopters (also validated)
    seeds = np.random.choice(N, size=int(seed_frac * N), replace=False)
    adopted[seeds] = True
    validated[seeds] = True

    # 4. Record time series
    adopt_hist = []
    valid_hist = []
    gap_hist = []

    for t in range(steps):
        # Adoption dynamics: adopt if fraction of adopted neighbors > threshold
        # (only consider nodes that are not yet adopted)
        not_adopted = np.where(~adopted)[0]
        for node in not_adopted:
            neigh = list(G.neighbors(node))
            if not neigh:
                continue
            frac = np.mean(adopted[neigh])
            if frac > thresholds[node]:
                adopted[node] = True
        # Validation dynamics: each adopted node gets validated with prob 0.2 per step
        newly_adopted = np.where(adopted & ~validated)[0]
        val_prob = 0.2
        validated[newly_adopted] = np.random.rand(len(newly_adopted)) < val_prob

        # Compute metrics
        adopt_frac = adopted.mean()
        valid_frac = validated.mean()
        gap = adopt_frac - valid_frac
        adopt_hist.append(adopt_frac)
        valid_hist.append(valid_frac)
        gap_hist.append(gap)

        # Apply shock at shock_time: randomly "kill" a fraction of adopted nodes
        if t == shock_time:
            kill = np.random.choice(np.where(adopted)[0],
                                   size=int(shock_size * adopted.sum()),
                                   replace=False)
            # Remove killed nodes from the graph (they become non‑functional)
            G.remove_nodes_from(kill)
            # Recompute adoption/validation arrays for remaining nodes
            surviving = np.setdiff1d(np.arange(N), kill)
            # Keep original indices for mapping
            # For simplicity, we just mark killed nodes as non‑adopted and non‑validated
            adopted[kill] = False
            validated[kill] = False

    # After shock, compute size of largest connected component of validated nodes
    # (only consider surviving nodes)
    surviving_nodes = np.where(adopted | validated)[0]
    if len(surviving_nodes) == 0:
        resilience = 0.0
    else:
        # Subgraph of validated nodes
        val_nodes = np.where(validated)[0]
        if len(val_nodes) == 0:
            resilience = 0.0
        else:
            subG = G.subgraph(val_nodes)
            # Size of largest connected component
            largest_cc = max(nx.connected_components(subG), key=len, default=set())
            resilience = len(largest_cc) / len(val_nodes) if val_nodes.size else 0.0

    return np.array(adopt_hist), np.array(valid_hist), np.array(gap_hist), resilience

# Run many Monte Carlo trials to assess predictive power
def run_trials(trials=30):
    adopt_resilience_corr = []
    gap_resilience_corr = []
    for _ in range(trials):
        adopt_hist, valid_hist, gap_hist, resilience = simulate()
        # Correlation of final adoption fraction with resilience
        adopt_final = adopt_hist[-1]
        # Correlation of average gap with resilience (simple proxy)
        gap_avg = gap_hist.mean()
        adopt_resilience_corr.append((adopt_final, resilience))
        gap_resilience_corr.append((gap_avg, resilience))
    adopt_vals = np.array([x[0] for x in adopt_resilience_corr])
    resil_vals = np.array([x[1] for x in adopt_resilience_corr])
    gap_vals = np.array([x[0] for x in gap_resilience_corr])
    # Compute Pearson correlation
    adopt_corr = np.corrcoef(adopt_vals, resil_vals)[0, 1]
    gap_corr = np.corrcoef(gap_vals, resil_vals)[0, 1]
    return adopt_corr, gap_corr, adopt_vals, gap_vals, resil_vals

# Execute
adopt_corr, gap_corr, adopt_vals, gap_vals, resil_vals = run_trials(trials=50)
print(f"Adoption‑Resilience correlation: {adopt_corr:.3f}")
print(f"Gap‑Resilience correlation: {gap_corr:.3f}")

# Show that the gauge term (spatial variance of adoption) adds no predictive power
def spatial_variance(adopted):
    # Simple variance across nodes
    return np.var(adopted)

# In the last time step of a single run, compute spatial variance
adopt_hist, valid_hist, gap_hist, resilience = simulate()
final_variance = spatial_variance(adopt_hist[-1] > 0)  # dummy: we need node-level variance
# For demonstration, we compute variance of adoption indicator across nodes at final step
# We'll recompute node-level adoption at final step
# (We need to track node-level adoption over time; modify simulate to return final states)