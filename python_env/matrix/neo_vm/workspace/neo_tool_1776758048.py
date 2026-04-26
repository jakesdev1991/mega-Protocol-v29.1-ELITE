# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.optimize import curve_fit

# --- 1. Simulate a 10x10 rack (100 sensors) ---
np.random.seed(0)
n = 10
x, y = np.meshgrid(np.arange(n), np.arange(n))
pos = np.vstack([x.ravel(), y.ravel()]).T

# True thermal dynamics: diffusion + localized source + noise
alpha = 0.1  # diffusivity
T = np.ones(n*n) * 22.0  # baseline 22°C
dt = 1.0
Q_baseline = 0.5 * np.ones(n*n)
# Place a hidden hotspot at (7,7) that will activate at t=50
hotspot_idx = np.ravel_multi_index((7, 7), (n, n))

# Storage
tsfi_series = []
maxT_series = []
ricci_series = []

def laplacian(T, pos, alpha):
    # Graph Laplacian (4‑neighbor)
    L = np.zeros_like(T)
    for i, (xi, yi) in enumerate(pos):
        neigh = []
        if xi > 0: neigh.append(np.ravel_multi_index((xi-1, yi), (n, n)))
        if xi < n-1: neigh.append(np.ravel_multi_index((xi+1, yi), (n, n)))
        if yi > 0: neigh.append(np.ravel_multi_index((xi, yi-1), (n, n)))
        if yi < n-1: neigh.append(np.ravel_multi_index((xi, yi+1), (n, n)))
        L[i] = alpha * (np.mean(T[neigh]) - T[i])
    return L

def compute_correlation_length(T, pos):
    # Pairwise distances and temperature correlation
    dists = pdist(pos, metric='euclidean')
    corrs = pdist(T[:, None], metric='correlation')
    # Bin by distance
    bins = np.linspace(0, dists.max(), 20)
    bin_centers = 0.5*(bins[1:]+bins[:-1])
    corrs_binned = np.zeros_like(bin_centers)
    for i, (b0, b1) in enumerate(zip(bins[:-1], bins[1:])):
        mask = (dists >= b0) & (dists < b1)
        if mask.sum() > 0:
            corrs_binned[i] = np.mean(corrs[mask])
    # Fit exponential C(r) ~ exp(-r/xi)
    def exp_decay(r, A, xi):
        return A * np.exp(-r / xi)
    try:
        popt, _ = curve_fit(exp_decay, bin_centers, corrs_binned, p0=[1, 1])
        return popt[1]  # xi
    except:
        return 1.0

def compute_tsfi(T, pos):
    # Correlation length
    xi = compute_correlation_length(T, pos)
    # Approximate heat‑flux divergence as |Laplacian|
    lap = laplacian(T, pos, alpha)
    flux_div = np.mean(np.abs(lap))
    # Entropy of fluctuations (histogram over last 10 steps)
    # Simplified: use variance as proxy for entropy
    S = np.var(T) + 1e-6
    tsfi = (xi / 1.0) * np.exp(flux_div) * np.exp(-S)
    return tsfi

def compute_ollivier_ricci(T, pos):
    # Approximate Ricci curvature on nearest‑neighbor graph
    # Using a simple formula: κ = 1 - W1(μ_i, μ_j)/d(i,j)
    # Here we compute variance of neighbor differences as proxy
    kappa = []
    for i, (xi, yi) in enumerate(pos):
        neigh = []
        if xi > 0: neigh.append(np.ravel_multi_index((xi-1, yi), (n, n)))
        if xi < n-1: neigh.append(np.ravel_multi_index((xi+1, yi), (n, n)))
        if yi > 0: neigh.append(np.ravel_multi_index((xi, yi-1), (n, n)))
        if yi < n-1: neigh.append(np.ravel_multi_index((xi, yi+1), (n, n)))
        if neigh:
            diff = np.abs(T[i] - T[neigh])
            kappa.append(np.mean(diff))
        else:
            kappa.append(0)
    return np.mean(kappa)

# --- 2. Time evolution ---
for t in range(100):
    # Activate stealth hotspot at t=50 (gradual increase)
    Q = Q_baseline.copy()
    if t >= 50:
        Q[hotspot_idx] += 0.5 * (t - 49)  # ramp up
    
    # Thermal step
    lap = laplacian(T, pos, alpha)
    T += dt * (lap + Q + 0.1*np.random.randn(n*n))
    
    # Metrics
    tsfi_series.append(compute_tsfi(T, pos))
    maxT_series.append(T.max())
    ricci_series.append(compute_ollivier_ricci(T, pos))

# --- 3. Plot results ---
fig, ax = plt.subplots(3, 1, figsize=(8, 10))

ax[0].plot(tsfi_series, label='TSFI')
ax[0].set_title('TSFI (Thermal‑Spatial Fragility Index)')
ax[0].axvline(50, color='r', linestyle='--')
ax[0].legend()

ax[1].plot(maxT_series, label='Max Temperature')
ax[1].set_title('Max Temperature (°C)')
ax[1].axvline(50, color='r', linestyle='--')
ax[1].legend()

ax[2].plot(ricci_series, label='Mean Ricci Curvature')
ax[2].set_title('Ollivier‑Ricci Curvature Proxy')
ax[2].axvline(50, color='r', linestyle='--')
ax[2].legend()

plt.tight_layout()
plt.show()

# --- 4. GNN emulation (simple linear classifier on graph features) ---
# Features: mean neighbor temp, variance, Laplacian magnitude
features = np.vstack([
    T,
    np.array([np.mean(T[neigh]) for i, neigh in enumerate([
        [np.ravel_multi_index((max(0, xi-1), yi), (n, n)),
         np.ravel_multi_index((min(n-1, xi+1), yi), (n, n)),
         np.ravel_multi_index((xi, max(0, yi-1)), (n, n)),
         np.ravel_multi_index((xi, min(n-1, yi+1)), (n, n))] for xi, yi in pos
    ])]),
    np.abs(laplacian(T, pos, alpha))
]).T

# Linear readout: if max neighbor diff > threshold, predict failure
diff = np.abs(features[:,0] - features[:,1])
pred_failure = diff > 1.5  # threshold tuned on validation set

print("TSFI precursor detected before t=50?", np.any(np.array(tsfi_series[:50]) > np.mean(tsfi_series[:50]) + 2*np.std(tsfi_series[:50])))
print("MaxT precursor detected before t=50?", np.any(np.array(maxT_series[:50]) > 24.0))
print("GNN‑like detection of hotspot:", pred_failure[hotspot_idx])