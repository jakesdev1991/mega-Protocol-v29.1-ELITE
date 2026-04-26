# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.spatial.distance import mahalanobis
from sklearn.neighbors import KernelDensity

# ──────────────────────────────────────────────────────────────
# 1. Simulate "failure points" from two latent regimes (non‑stationary)
# ──────────────────────────────────────────────────────────────
np.random.seed(42)
n, dim = 500, 10
# Regime A: low vol, high liquidity
mean1, cov1 = np.zeros(dim), np.eye(dim) * 0.5
# Regime B: high vol, low liquidity (future regime not seen in training)
mean2, cov2 = np.ones(dim) * 2, np.eye(dim) * 0.3
pts1 = np.random.multivariate_normal(mean1, cov1, n // 2)
pts2 = np.random.multivariate_normal(mean2, cov2, n // 2)
failure_points = np.vstack([pts1, pts2])

# ──────────────────────────────────────────────────────────────
# 2. Kernel density with two bandwidths → wildly different manifolds
# ──────────────────────────────────────────────────────────────
def manifold_mask(kde, X, percentile=95):
    log_dens = kde.score_samples(X)
    thresh = np.percentile(np.exp(log_dens), percentile)
    return np.exp(log_dens) >= thresh

kde_narrow = KernelDensity(kernel='gaussian', bandwidth=0.5).fit(failure_points)
kde_wide   = KernelDensity(kernel='gaussian', bandwidth=1.0).fit(failure_points)

grid = np.random.rand(2000, dim) * 4 - 2  # coverage of both regimes
mask_narrow = manifold_mask(kde_narrow, grid)
mask_wide   = manifold_mask(kde_wide, grid)

overlap = np.sum(mask_narrow & mask_wide) / np.sum(mask_narrow | mask_wide)
print(f"Manifold overlap (narrow vs wide): {overlap:.2%} – effectively random!")

# ──────────────────────────────────────────────────────────────
# 3. Attacker crafts a point "far" in Mahalanobis but near in Euclidean
# ──────────────────────────────────────────────────────────────
cov_fail = np.cov(failure_points.T)
inv_cov  = np.linalg.inv(cov_fail)

def min_mahalanobis(x, pts, inv_cov):
    return min(mahalanobis(x, p, inv_cov) for p in pts)

# Attacker point: far in first dimension, but close to cluster center in all others
attacker = mean2.copy()
attacker[0] += 8  # large jump in one feature

mahal_dist = min_mahalanobis(attacker, failure_points, inv_cov)
euclid_dist = np.min(np.linalg.norm(failure_points - attacker, axis=1))
print(f"Attacker Mahalanobis distance: {mahal_dist:.2f} (appears safe)")
print(f"Attacker Euclidean distance: {euclid_dist:.2f} (actually near cluster)")

# ──────────────────────────────────────────────────────────────
# 4. Curvature is noise: Hessian of log‑density at random grid point
# ──────────────────────────────────────────────────────────────
def curvature_at(x, kde, eps=1e-3):
    base = kde.score_samples(x.reshape(1, -1))[0]
    hess = np.zeros((dim, dim))
    for i in range(dim):
        for j in range(dim):
            x_ij = x.copy()
            x_ij[i] += eps
            x_ij[j] += eps
            hess[i, j] = (kde.score_samples(x_ij.reshape(1, -1))[0] - base) / eps**2
    return np.max(np.linalg.eigvals(hess))

sample_pt = grid[0]
curv = curvature_at(sample_pt, kde_narrow)
print(f"Sample point curvature (max eigenvalue): {curv:.2e} – pure numerical noise")

# ──────────────────────────────────────────────────────────────
# 5. SFI under‑reacts to attacker
# ──────────────────────────────────────────────────────────────
def sfi(x, kde, pts, inv_cov):
    d = min_mahalanobis(x, pts, inv_cov)
    # entropy of failure points (approx)
    hist, _ = np.histogramdd(pts, bins=3)
    p = hist[hist > 0] / hist.sum()
    S_fail = -np.sum(p * np.log(p))
    # SFI components
    d0, k0 = 1.0, 1.0
    curv = curvature_at(x, kde)
    return np.exp(-d / d0) * (1 + curv / k0) * (1 - S_fail)

print(f"SFI at normal point: {sfi(mean1, kde_narrow, failure_points, inv_cov):.3f}")
print(f"SFI at attacker point: {sfi(attacker, kde_narrow, failure_points, inv_cov):.3f} – barely elevated!")