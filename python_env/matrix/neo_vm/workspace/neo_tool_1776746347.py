# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

# --- Generate benign narrative embeddings (2D for visualization) ---
np.random.seed(42)
n_benign = 500
benign = np.random.multivariate_normal([0, 0], [[0.5, 0.1], [0.1, 0.5]], size=n_benign)

# --- Adversarial injection: small, far‑out cluster ---
n_adv = 20
adversarial = np.random.multivariate_normal([5, 5], [[0.05, 0], [0, 0.05]], size=n_adv)

# Combined dataset
X = np.vstack([benign, adversarial])

# --- Naive scalar curvature (Laplacian of kernel density) ---
def scalar_curvature_2d(points, bandwidth=0.5):
    # Approximate density via kernel sum
    K = np.exp(-cdist(points, points)**2 / (2 * bandwidth**2))
    density = K.sum(axis=1)
    # Approximate Laplacian via finite differences on grid
    # (simplified: just return variance of density as proxy)
    return np.var(density)

curvature = scalar_curvature_2d(X)
print(f"Scalar curvature (proxy): {curvature:.3f}")

# --- Shannon entropy of kernel‑smoothed histogram ---
def shannon_entropy(points, bins=30):
    H, _ = np.histogramdd(points, bins=bins, density=True)
    p = H[H > 0]
    return -np.sum(p * np.log(p))

entropy = shannon_entropy(X)
print(f"Shannon entropy: {entropy:.3f}")

# --- 1‑Wasserstein distance (earth‑mover distance) between benign and full set ---
# Approximate by optimal transport between empirical distributions
def wasserstein_1d(x, y, n_proj=100):
    # Project onto random directions and compute 1D EMD
    projs = np.random.randn(n_proj, x.shape[1])
    projs /= np.linalg.norm(projs, axis=1, keepdims=True)
    emds = []
    for p in projs:
        xp = x @ p
        yp = y @ p
        # Sort and compute cumulative distances
        xp_s = np.sort(xp)
        yp_s = np.sort(yp)
        emds.append(np.mean(np.abs(xp_s - yp_s)))
    return np.mean(emds)

W = wasserstein_1d(benign, X)
print(f"1‑Wasserstein distance: {W:.3f}")

# --- Interpretation ---
# Curvature low → model predicts "safe"
# Entropy high → model predicts "fragmentation"
# Wasserstein high → true adversarial shredding