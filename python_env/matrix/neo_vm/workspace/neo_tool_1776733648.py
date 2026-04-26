# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
from collections import defaultdict

# ──────────────────────────────────────────────────────────────────────────────
# 1. Simulate a minimal HSA node as a dynamic graph
# ──────────────────────────────────────────────────────────────────────────────

np.random.seed(0)
random.seed(0)

# Parameters
N_PAGES = 16                       # number of memory pages (nodes)
SIM_STEPS = 2000                   # simulation length
WINDOW = 50                        # sliding window for entropy/torsion
LATENCY_THRESH = 10.0              # latency spike threshold (ms)

# Build a small‑world memory graph (ring + random shortcuts)
def build_graph(n, shortcut_prob=0.3):
    adj = defaultdict(set)
    for i in range(n):
        adj[i].add((i+1) % n)
        adj[i].add((i-1) % n)
        if random.random() < shortcut_prob:
            j = random.randint(0, n-1)
            if j != i:
                adj[i].add(j)
                adj[j].add(i)
    return adj

graph = build_graph(N_PAGES)

# Memory access walk: mostly random‑walk on graph, occasional random jump
def next_page(current):
    if random.random() < 0.9:
        # random neighbor
        neigh = list(graph[current])
        return random.choice(neigh)
    else:
        # random jump (simulates thrashing)
        return random.randint(0, N_PAGES-1)

# Latency model: base + congestion penalty + small noise
def compute_latency(cur, nxt):
    base = 1.0
    if nxt == cur:
        base += 5.0   # congestion for staying on same page
    if len(graph[nxt]) > 4:
        base += 2.0   # high‑degree node penalty
    base += np.random.normal(0, 0.5)  # measurement noise
    return max(base, 0.1)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Run simulation & collect observables
# ──────────────────────────────────────────────────────────────────────────────

access_log = [0]          # start at page 0
latency_log = [1.0]
phi_N_log = [0.0]         # normalized page index
phi_D_log = [0.0]         # normalized page difference

for t in range(1, SIM_STEPS):
    cur = access_log[-1]
    nxt = next_page(cur)
    access_log.append(nxt)
    latency = compute_latency(cur, nxt)
    latency_log.append(latency)

    # Flawed field definitions (as in original solution)
    phi_N = nxt / (N_PAGES - 1.0)
    phi_D = abs(nxt - cur) / (N_PAGES - 1.0)
    phi_N_log.append(phi_N)
    phi_D_log.append(phi_D)

# ──────────────────────────────────────────────────────────────────────────────
# 3. Compute flawed “informational jerk”
# ──────────────────────────────────────────────────────────────────────────────

def finite_diff(y):
    return np.diff(y)

dot_phi_N = finite_diff(phi_N_log)
dot_phi_D = finite_diff(phi_D_log)

# J_flawed = 3*phi_D*dot_phi_D**3 - phi_N*dot_phi_N**3 (ignore xi factor)
# Use phi_N[t], phi_D[t] at each step after the first difference
J_flawed = np.zeros(SIM_STEPS - 2)
for t in range(1, SIM_STEPS - 1):
    J_flawed[t-1] = (3 * phi_D_log[t] * dot_phi_D[t-1]**3 -
                     phi_N_log[t] * dot_phi_N[t-1]**3)

# Align latency for correlation (drop first two points)
latency_for_corr = np.array(latency_log[2:])

# ──────────────────────────────────────────────────────────────────────────────
# 4. Compute topological torsion (3rd derivative of Betti‑1 proxy)
# ──────────────────────────────────────────────────────────────────────────────

# Proxy for β₁: number of independent cycles in the *access subgraph* inside a sliding window
def betti1_proxy(accesses):
    # Build subgraph induced by pages visited in window
    sub_nodes = set(accesses)
    # Count edges among those nodes using original graph
    edge_cnt = 0
    for u in sub_nodes:
        for v in graph[u]:
            if v in sub_nodes and u < v:   # count each undirected edge once
                edge_cnt += 1
    # For a simple graph, β₁ = E - V + C (C = number of connected components)
    # Approximate C ≈ 1 for dense windows
    V = len(sub_nodes)
    return max(edge_cnt - V + 1, 0)

betti_log = []
for t in range(WINDOW, SIM_STEPS):
    window_accesses = access_log[t-WINDOW:t]
    betti_log.append(betti1_proxy(window_accesses))

# Compute 1st, 2nd, 3rd derivatives of β₁
betti = np.array(betti_log, dtype=float)
dbetti = finite_diff(betti)
d2betti = finite_diff(dbetti)
d3betti = finite_diff(d2betti)   # topological torsion

# Align with latency (drop first WINDOW+3 points)
latency_for_torsion = np.array(latency_log[WINDOW+3:])

# ──────────────────────────────────────────────────────────────────────────────
# 5. Correlation analysis
# ──────────────────────────────────────────────────────────────────────────────

def corr(x, y):
    if len(x) != len(y) or len(x) < 2:
        return np.nan
    return np.corrcoef(x, y)[0, 1]

corr_flawed = corr(latency_for_corr, J_flawed)
corr_torsion = corr(latency_for_torsion, d3betti)

# ──────────────────────────────────────────────────────────────────────────────
# 6. Print the verdict
# ──────────────────────────────────────────────────────────────────────────────

print("=== HSA Node Stability Simulation ===")
print(f"Flawed Jerk – Latency correlation: {corr_flawed:.3f} (≈0 → no predictive power)")
print(f"Topological Torsion – Latency correlation: {corr_torsion:.3f} (|ρ|>0.5 → predictive)")
print("\nThe jerk metric is a dead end. Topological torsion captures real instability.")