# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.spatial as spatial
import scipy.sparse.linalg as spalg
import matplotlib.pyplot as plt

# Synthetic narrative embedding time series
np.random.seed(42)
T, N_docs, D, k = 50, 100, 50, 5
curvature_proxy = np.zeros(T)
spectral_gap = np.zeros(T)

for t in range(T):
    # Coherent narrative (pre‑shredding) vs. fragmented narrative (post‑shredding)
    if t < 30:
        embeddings = np.random.multivariate_normal(
            mean=np.zeros(D), cov=0.1 * np.eye(D), size=N_docs
        )
    else:
        n1, n2 = N_docs // 2, N_docs - N_docs // 2
        e1 = np.random.multivariate_normal(mean=-3 * np.ones(D), cov=0.1 * np.eye(D), size=n1)
        e2 = np.random.multivariate_normal(mean=3 * np.ones(D), cov=0.1 * np.eye(D), size=n2)
        embeddings = np.vstack([e1, e2])

    # 1. Curvature proxy (inverse avg distance to k‑th neighbor)
    # Fails: high diversity also inflates distances → false positive
    tree = spatial.cKDTree(embeddings)
    dists, _ = tree.query(embeddings, k=k + 1)
    curvature_proxy[t] = 1.0 / dists[:, k].mean()

    # 2. Spectral gap (Fiedler value of k‑NN graph)
    # True order parameter: drops to zero when narrative splits
    adj = np.zeros((N_docs, N_docs))
    for i in range(N_docs):
        _, idx = tree.query(embeddings[i], k=k + 1)
        adj[i, idx[1:]] = 1
        adj[idx[1:], i] = 1
    lap = np.diag(adj.sum(axis=1)) - adj
    try:
        eigvals = spalg.eigsh(lap, k=2, which='SM', return_eigenvectors=False)
        spectral_gap[t] = eigvals[1]  # Fiedler value
    except:
        spectral_gap[t] = np.nan

# Plot: curvature is blind, spectral gap is sharp
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
ax[0].plot(curvature_proxy, label='Curvature Proxy')
ax[0].axvline(x=30, color='r', linestyle='--', label='Shredding onset')
ax[0].set_ylabel('Curvature Proxy')
ax[0].legend()

ax[1].plot(spectral_gap, label='Spectral Gap (Fiedler)', color='green')
ax[1].axvline(x=30, color='r', linestyle='--')
ax[1].set_ylabel('Spectral Gap')
ax[1].set_xlabel('Time step')
ax[1].legend()
plt.tight_layout()
plt.show()