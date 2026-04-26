# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def curvature_proxy(embeddings):
    """Naive curvature proxy: trace of covariance matrix."""
    cov = np.cov(embeddings, rowvar=False)
    return np.trace(cov)

# Demonstrate curvature instability
np.random.seed(0)
N, D = 50, 300
embeddings = np.random.randn(N, D)
print("Initial curvature proxy:", curvature_proxy(embeddings))
# Perturb a single document slightly
embeddings[0] += np.random.randn(D) * 0.01
print("After small perturbation:", curvature_proxy(embeddings))
# Show high variance across runs
vals = [curvature_proxy(np.random.randn(N, D)) for _ in range(100)]
print("Mean, std of curvature proxy:", np.mean(vals), np.std(vals))

def simulate_contagion(N, p):
    """Simple percolation‑style contagion on a random graph."""
    # Random adjacency matrix with probability p
    adj = np.random.rand(N, N) < p
    np.fill_diagonal(adj, False)
    # Start with one fragmented agent
    fragmented = np.zeros(N, dtype=bool)
    fragmented[np.random.randint(N)] = True
    # Propagation: if neighbor is fragmented, flip with probability p
    changed = True
    while changed:
        changed = False
        for i in range(N):
            if not fragmented[i] and np.any(adj[i] & fragmented):
                if np.random.rand() < p:
                    fragmented[i] = True
                    changed = True
    return fragmented.mean()

# Scan the control parameter p to locate percolation threshold
for p in np.linspace(0.1, 0.9, 9):
    print(f"p={p:.2f}, fraction fragmented: {simulate_contagion(200, p):.3f}")