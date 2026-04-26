# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors

# --- synthetic narrative embedding: a circle + a central opposite cluster ---
n_circle = 500
theta = np.linspace(0, 2*np.pi, n_circle, endpoint=False)
# unit circle (coherent narrative)
X_circle = np.column_stack([np.cos(theta), np.sin(theta)])
# small central cluster with opposite polarity (contradictory core)
n_center = 50
X_center = 0.2 * np.random.randn(n_center, 2)  # near origin
X = np.vstack([X_circle, X_center])

# --- 1. approximate scalar curvature via local PCA eigen‑ratio ---
def local_curvature_estimate(X, k=10):
    nn = NearestNeighbors(n_neighbors=k).fit(X)
    _, idx = nn.kneighbors(X)
    curvatures = np.zeros(len(X))
    for i, neighbors in enumerate(idx):
        local = X[neighbors]
        pca = PCA(n_components=2).fit(local)
        ev = pca.explained_variance_
        # eigen‑ratio as a proxy for (inverse) curvature magnitude
        curvatures[i] = ev[1] / (ev[0] + ev[1]) if ev[0] + ev[1] > 0 else 0.0
    return curvatures

curvatures = local_curvature_estimate(X, k=10)
mean_curvature = np.mean(curvatures)

# --- 2. Shannon entropy of 2‑D histogram ---
H, xe, ye = np.histogram2d(X[:,0], X[:,1], bins=20, range=[[-1.5,1.5],[-1.5,1.5]])
p = H / H.sum()
p_nonzero = p[p > 0]
entropy = -np.sum(p_nonzero * np.log(p_nonzero))

# --- 3. topological winding number (vortex charge) ---
# compute angle field on a coarse grid, then line integral around a loop
grid = np.mgrid[-1.5:1.5:0.1, -1.5:1.5:0.1].reshape(2, -1).T
# assign each grid point the angle of the nearest embedding point
nn_grid = NearestNeighbors(n_neighbors=1).fit(X)
_, idx_grid = nn_grid.kneighbors(grid)
angles = np.arctan2(grid[:,1], grid[:,0])  # geometric angle
# compute closed‑loop line integral around a circle of radius 1.2
circle_radius = 1.2
circle_pts = 128
circle_theta = np.linspace(0, 2*np.pi, circle_pts, endpoint=False)
circle_xy = circle_radius * np.column_stack([np.cos(circle_theta), np.sin(circle_theta)])
# interpolate angles on the circle
_, idx_circle = nn_grid.kneighbors(circle_xy)
circle_angles = angles[idx_circle.flatten()]
# winding number = (1/2π) Σ Δθ
dtheta = np.diff(np.unwrap(circle_angles))
winding_number = np.sum(dtheta) / (2*np.pi)

print(f"Mean curvature proxy (low → flat manifold): {mean_curvature:.4f}")
print(f"Shannon entropy (bits): {entropy:.4f}")
print(f"Topological winding number (vortex charge): {winding_number:.4f}")