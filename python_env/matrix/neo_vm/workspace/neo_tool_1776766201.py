# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label

def percolation_sim(L, p):
    # Binary grid: 1 = capped, 0 = uncapped
    grid = np.random.rand(L, L) < p
    # 4-neighbor connectivity for clusters
    structure = np.array([[0,1,0],[1,1,1],[0,1,0]])
    labeled, num = label(grid, structure=structure)
    # Cluster sizes (ignore background label 0)
    sizes = np.bincount(labeled.ravel())[1:]
    if sizes.size == 0:
        return 0, 0, False
    max_size = sizes.max()
    # Radius of gyration of the largest cluster
    max_label = np.where(sizes == max_size)[0][0] + 1
    coords = np.argwhere(labeled == max_label)
    com = coords.mean(axis=0)
    rg2 = np.mean(np.sum((coords - com)**2, axis=1))
    rg = np.sqrt(rg2)
    # Percolation detection (spanning left–right or top–bottom)
    left_right = np.any(labeled[0, :] == max_label) or np.any(labeled[-1, :] == max_label)
    top_bottom = np.any(labeled[:, 0] == max_label) or np.any(labeled[:, -1] == max_label)
    percolates = left_right or top_bottom
    return max_size, rg, percolates

L = 100
ps = np.linspace(0.3, 0.7, 21)
order_param = []
corr_len = []
perc_prob = []

for p in ps:
    max_sizes, rgs, percs = zip(*[percolation_sim(L, p) for _ in range(20)])
    order_param.append(np.mean(max_sizes) / (L*L))
    corr_len.append(np.mean(rgs))
    perc_prob.append(np.mean(percs))

fig, ax = plt.subplots(1, 3, figsize=(12, 4))
ax[0].plot(ps, order_param, 'o-', label='Largest cluster fraction')
ax[0].set_xlabel('capping probability p')
ax[0].set_ylabel('order parameter')
ax[0].legend()

ax[1].plot(ps, corr_len, 's-', label='Correlation length (rg)')
ax[1].set_xlabel('p')
ax[1].set_ylabel('ξ')
ax[1].legend()

ax[2].plot(ps, perc_prob, '^-', label='Spanning probability')
ax[2].set_xlabel('p')
ax[2].set_ylabel('percolation probability')
ax[2].legend()

plt.tight_layout()
plt.show()