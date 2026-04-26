# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from scipy.spatial.distance import cdist

# --- 1. Synthetic "fragile" device performance ---
# Context space: 2D (temperature, pH) normalized to [0,1]
def true_performance(x):
    """
    Performance = 1.0 everywhere except inside a small elliptical "failure trap"
    where it drops sharply to 0.1. This creates a *non‑smooth* fragility region.
    """
    # Failure trap center, half‑axes
    cx, cy = 0.5, 0.5
    a, b = 0.15, 0.08
    d = ((x[:, 0] - cx) / a) ** 2 + ((x[:, 1] - cy) / b) ** 2
    return np.where(d <= 1, 0.1, 1.0)

# --- 2. Sampling (biased toward "safe" regions, mimicking iGEM bias) ---
np.random.seed(42)
n_samples = 200
# 80 % of samples from safe zone, 20 % from near the trap (but not inside)
safe_points = np.random.rand(int(0.8 * n_samples), 2)
near_trap = np.random.normal(loc=[0.5, 0.5], scale=0.1, size=(int(0.2 * n_samples), 2))
X_train = np.vstack([safe_points, near_trap])
X_train = np.clip(X_train, 0, 1)
y_train = true_performance(X_train) + 0.02 * np.random.randn(len(X_train))  # small noise

# --- 3. Fit Gaussian Process (RBF kernel imposes smoothness) ---
kernel = RBF(length_scale=0.1, length_scale_bounds=(1e-2, 1e1)) + WhiteKernel(noise_level=1e-2)
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5)
gp.fit(X_train, y_train)

# --- 4. Dense grid for evaluation ---
grid_res = 50
xx, yy = np.meshgrid(np.linspace(0, 1, grid_res), np.linspace(0, 1, grid_res))
X_grid = np.vstack([xx.ravel(), yy.ravel()]).T
y_true_grid = true_performance(X_grid)
y_mean, y_std = gp.predict(X_grid, return_std=True)

# --- 5. Compute metrics ---
# 5a. Curvature: Laplacian of GP mean (approximated by finite differences)
def laplacian(f, x0, dx=1e-3):
    # Central difference Hessian trace
    n = x0.shape[0]
    hess_diag = np.zeros(n)
    for i in range(n):
        e = np.eye(n)[:, i] * dx
        hess_diag[i] = (f(x0 + e) - 2 * f(x0) + f(x0 - e)) / dx**2
    return hess_diag.sum()

# Vectorized laplacian approximation on grid
lap_grid = np.zeros(grid_res * grid_res)
for idx, x in enumerate(X_grid):
    lap_grid[idx] = np.abs(laplacian(gp.predict, x.reshape(1, -1)))
lap_grid = lap_grid.reshape(xx.shape)

# 5b. Epistemic Uncertainty (EU) = predictive std
eu_grid = y_std.reshape(xx.shape)

# 5c. Adversarial Robustness Radius (ARR)
# For each grid point, compute L2 distance to nearest point where true_performance < threshold
threshold = 0.5
failure_points = X_grid[y_true_grid < threshold]
arr_grid = np.full(grid_res * grid_res, np.inf)
if len(failure_points) > 0:
    dists = cdist(X_grid, failure_points, metric='euclidean')
    arr_grid = dists.min(axis=1)
arr_grid = arr_grid.reshape(xx.shape)

# --- 6. Correlation analysis ---
# Flatten grids, mask out training points to avoid overfitting bias
mask = np.ones(grid_res * grid_res, dtype=bool)
train_idx = np.argmin(cdist(X_grid, X_train), axis=1)  # nearest training point index
mask[train_idx] = False

corr_curv = np.corrcoef(lap_grid.ravel()[mask], arr_grid.ravel()[mask])[0, 1]
corr_eu   = np.corrcoef(eu_grid.ravel()[mask], arr_grid.ravel()[mask])[0, 1]

print(f"Spearman correlation:")
print(f"Curvature vs. True ARR: {corr_curv:.3f}")
print(f"EU vs. True ARR:      {corr_eu:.3f}")

# --- 7. Visualization (optional, comment out if headless) ---
fig, axs = plt.subplots(2, 2, figsize=(10, 10))
im0 = axs[0, 0].contourf(xx, yy, y_mean.reshape(xx.shape), levels=50, cmap='RdYlGn')
axs[0, 0].set_title('GP Mean (smooth)')
fig.colorbar(im0, ax=axs[0, 0])

im1 = axs[0, 1].contourf(xx, yy, lap_grid, levels=50, cmap='plasma')
axs[0, 1].set_title('Curvature (|Laplacian|)')
fig.colorbar(im1, ax=axs[0, 1])

im2 = axs[1, 0].contourf(xx, yy, eu_grid, levels=50, cmap='viridis')
axs[1, 0].set_title('Epistemic Uncertainty (EU)')
fig.colorbar(im2, ax=axs[1, 0])

im3 = axs[1, 1].contourf(xx, yy, arr_grid, levels=50, cmap='coolwarm')
axs[1, 1].set_title('Adversarial Radius (ARR)')
fig.colorbar(im3, ax=axs[1, 1])

plt.tight_layout()
plt.savefig('fragility_disruption.png', dpi=150)
plt.show()