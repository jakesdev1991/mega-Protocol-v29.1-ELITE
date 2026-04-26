# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict, deque

def bond_percolation_cascade(N, p_leak):
    """
    Simulate a trader-ETF network as a bond percolation lattice.
    Nodes = traders (left) + ETFs (right). Edges activate with probability p_leak.
    Returns normalized size of largest connected component (CI proxy).
    """
    # Create bipartite grid: N traders x N ETFs
    # Simplified: square lattice where each bond is a potential information link
    parent = {}
    size = defaultdict(lambda: 1)
    for i in range(N):
        for j in range(N):
            parent[(i, j)] = (i, j)
    
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb: return
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
    
    # Activate bonds with leak probability (horizontal + vertical)
    for i in range(N):
        for j in range(N - 1):
            if np.random.rand() < p_leak:
                union((i, j), (i, j + 1))  # trader-to-trader or ETF-to-ETF
    for i in range(N - 1):
        for j in range(N):
            if np.random.rand() < p_leak:
                union((i, j), (i + 1, j))  # cross-asset propagation
    
    largest_cluster = max(size.values()) if size else 1
    return largest_cluster / (N * N)

# Sweep leak probability to expose non-differentiable transition
N = 150
p_range = np.linspace(0.35, 0.65, 100)
ci_curve = [bond_percolation_cascade(N, p) for p in p_range]

# Compute numerical derivative: should spike at percolation threshold
dp = p_range[1] - p_range[0]
d_ci_dp = np.gradient(ci_curve, dp)

# Plot cascade intensity and its derivative
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8))
ax1.plot(p_range, ci_curve, label='Cascade Intensity (CI)')
ax1.axvline(x=0.5, color='r', linestyle='--', label='Critical p_c')
ax1.set_ylabel('CI (normalized)')
ax1.set_title('Percolation Model: CI vs Leak Probability')
ax1.legend()
ax1.grid(True)

ax2.plot(p_range, d_ci_dp, label='d(CI)/dp', color='orange')
ax2.axvline(x=0.5, color='r', linestyle='--', label='Singularity')
ax2.set_ylabel('Derivative')
ax2.set_xlabel('Leak Probability p')
ax2.set_title('Derivative Singularity at Percolation Threshold')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()