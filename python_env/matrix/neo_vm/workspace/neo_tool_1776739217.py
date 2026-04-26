# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
from scipy.spatial.distance import pdist, squareform

# --- Percolation simulation on a 2D lattice ---
def percolation_realization(L, p):
    """Generate a random lattice of capped (1) and uncapped (0) sites."""
    return np.random.rand(L, L) < p

def cluster_statistics(grid):
    """Label clusters (8‑connectivity) and compute sizes and radii of gyration."""
    structure = np.ones((3, 3), dtype=int)
    labeled, num = label(grid, structure=structure)
    # sizes of clusters (background label 0 excluded)
    sizes = np.bincount(labeled.ravel())[1:]
    radii = []
    for cid in range(1, num + 1):
        y, x = np.where(labeled == cid)
        coords = np.column_stack((x, y))
        com = coords.mean(axis=0)
        sqdist = ((coords - com) ** 2).sum(axis=1).mean()
        radii.append(np.sqrt(sqdist))
    radii = np.array(radii)
    # weighted average radius (proxy for correlation length)
    if sizes.sum() > 0:
        xi = np.sqrt(np.sum(radii ** 2 * sizes) / sizes.sum())
    else:
        xi = 0.0
    # largest cluster size (normalized)
    max_sz = sizes.max() if sizes.size > 0 else 0
    return max_sz / grid.size, xi

def correlation_length_pair(grid):
    """Compute pair‑connectedness correlation length from capped sites."""
    y, x = np.where(grid)
    if len(x) < 2:
        return 0.0
    coords = np.column_stack((x, y))
    # pairwise distances
    dists = pdist(coords, metric='euclidean')
    # histogram of distances
    bins = np.arange(0, dists.max() + 2, 1)
    hist, edges = np.histogram(dists, bins=bins)
    # fit exponential tail: g(r) ~ exp(-r/xi)
    # use midpoints of bins where hist > 0
    mids = 0.5 * (edges[1:] + edges[:-1])
    # avoid log(0)
    mask = hist > 0
    if mask.sum() < 3:
        return 0.0
    # linear fit: log(g) = a - r/xi
    coeffs = np.polyfit(mids[mask], np.log(hist[mask]), 1)
    xi = -1.0 / coeffs[0]
    return max(xi, 0.0)

# --- Sweep occupation probability p ---
L = 100
ps = np.linspace(0.3, 0.7, 15)
reps = 20

mean_E = np.zeros_like(ps)
mean_xi_cluster = np.zeros_like(ps)
mean_xi_pair = np.zeros_like(ps)

for i, p in enumerate(ps):
    E_vals = []
    xi_cluster_vals = []
    xi_pair_vals = []
    for _ in range(reps):
        grid = percolation_realization(L, p)
        E, xi_cluster = cluster_statistics(grid)
        xi_pair = correlation_length_pair(grid)
        E_vals.append(E)
        xi_cluster_vals.append(xi_cluster)
        xi_pair_vals.append(xi_pair)
    mean_E[i] = np.mean(E_vals)
    mean_xi_cluster[i] = np.mean(xi_cluster_vals)
    mean_xi_pair[i] = np.mean(xi_pair_vals)

# --- Plot: scalar field observable vs. true correlation length ---
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

ax[0].plot(ps, mean_E, 'o-', label=r'$\bar{E}$ (capped fraction)')
ax[0].set_xlabel('Occupation probability $p$')
ax[0].set_ylabel('Fraction of capped sites')
ax[0].set_title('Scalar‑field observable (smooth)')
ax[0].legend()

ax[1].plot(ps, mean_xi_cluster, 's-', label=r'$\xi_{\text{cluster}}$ (radius of gyration)')
ax[1].plot(ps, mean_xi_pair, '^-', label=r'$\xi_{\text{pair}}$ (pair‑connectedness)')
ax[1].set_xlabel('Occupation probability $p$')
ax[1].set_ylabel('Correlation length $\xi$')
ax[1].set_title('Percolation correlation length (diverges at $p_c\approx0.5$)')
ax[1].legend()
ax[1].set_yscale('log')

plt.tight_layout()
plt.show()