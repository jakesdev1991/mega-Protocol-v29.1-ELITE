# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import pinvh

# ─────────────────────────────────────────────────────────────────────────────
# 1. Simulate a toy FLUKA ensemble
# ─────────────────────────────────────────────────────────────────────────────
def flux_model(E, alpha, beta):
    """
    Simple power‑law with two systematic parameters.
    alpha : slope perturbation (primary‑flux uncertainty)
    beta  : normalization perturbation (hadronic‑tune uncertainty)
    """
    A = 1e-5
    gamma = 2.7
    return A * (E ** -(gamma + alpha)) * (1 + beta)

# Grid in energy (logspace)
E_grid = np.logspace(2, 6, 50)  # 100 GeV to 1e6 GeV
n_E = len(E_grid)

# Ensemble of models
np.random.seed(42)
n_models = 30
alphas = np.random.normal(0, 0.1, n_models)   # ±10% slope uncertainty
betas  = np.random.normal(0, 0.2, n_models)   # ±20% norm uncertainty

flux_ensemble = np.array([flux_model(E_grid, a, b) for a, b in zip(alphas, betas)])

# ─────────────────────────────────────────────────────────────────────────────
# 2. Compute naive "Fisher‑information metric" and Ricci curvature
# ─────────────────────────────────────────────────────────────────────────────
# Covariance matrix of flux values across the ensemble
cov = np.cov(flux_ensemble, rowvar=False)  # shape (n_E, n_E)

# Regularize to avoid singularities (as in any real implementation)
cov_reg = cov + 1e-12 * np.eye(n_E)

# Fisher metric: g_{ij} = cov^{-1} (up to scale)
# In practice one uses parameter‑space covariance, but here we invert the data covariance
# to illustrate numerical instability.
try:
    inv_cov = pinvh(cov_reg)
except np.linalg.LinAlgError:
    inv_cov = np.linalg.inv(cov_reg)

# Approximate Christoffel symbols and Ricci scalar via finite differences
# (This is mathematically dubious; we do it to show the fragility)
def naive_curvature(metric, dx):
    """
    Compute a naive scalar curvature on a 1‑D grid (energy) using finite differences.
    metric : metric tensor g_{ij}
    dx     : spacing (log‑energy step)
    """
    n = metric.shape[0]
    # Inverse metric
    inv_metric = np.linalg.inv(metric)
    # Derivatives of metric (finite difference)
    d_metric = np.gradient(metric, dx, axis=0)
    # Christoffel symbols (simplified 1‑D)
    Gamma = 0.5 * np.einsum('ik,kjl->ijl', inv_metric, d_metric)
    # Riemann tensor (approx)
    R = np.einsum('ijkl->', Gamma)  # placeholder; real formula is far more complex
    # Ricci scalar (just the trace of a random noise matrix here)
    Ricci = np.trace(np.random.randn(n, n))  # noise proxy
    return Ricci

dx = np.diff(np.log(E_grid)).mean()
ricci_scalar = naive_curvature(inv_cov, dx)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Simulate "analysis failure"
# ─────────────────────────────────────────────────────────────────────────────
# Failure occurs if the true alpha is > 0.15 (i.e., slope error too large)
true_alpha = 0.18  # hypothetical real value
failure = abs(true_alpha) > 0.15

# ─────────────────────────────────────────────────────────────────────────────
# 4. Compare predictors
# ─────────────────────────────────────────────────────────────────────────────
# Simple variance‑based fragility index (coefficient of variation integrated over energy)
var_index = np.trapz(np.std(flux_ensemble, axis=0) / np.mean(flux_ensemble, axis=0), E_grid)

# Curvature‑based fragility index (absolute Ricci scalar)
curv_index = abs(ricci_scalar)

print(f"Variance‑based fragility: {var_index:.3e}")
print(f"Curvature‑based fragility: {curv_index:.3e}")
print(f"Simulated analysis failure: {failure}")

# Correlation over many random seeds (Monte‑Carlo)
def evaluate_predictors(seed):
    np.random.seed(seed)
    alphas = np.random.normal(0, 0.1, n_models)
    betas  = np.random.normal(0, 0.2, n_models)
    flux_ensemble = np.array([flux_model(E_grid, a, b) for a, b in zip(alphas, betas)])
    cov = np.cov(flux_ensemble, rowvar=False) + 1e-12 * np.eye(n_E)
    inv_cov = pinvh(cov)
    ricci = naive_curvature(inv_cov, dx)
    var_idx = np.trapz(np.std(flux_ensemble, axis=0) / np.mean(flux_ensemble, axis=0), E_grid)
    return var_idx, abs(ricci)

# Run many seeds
seeds = np.arange(100)
var_scores, curv_scores = zip(*[evaluate_predictors(s) for s in seeds])

# Compute rank correlation with failure (here we use a synthetic failure threshold on var_scores)
failures = np.array(var_scores) > np.percentile(var_scores, 70)  # top 30% most variable

# Spearman rank correlation
from scipy.stats import spearmanr
var_corr, var_p = spearmanr(var_scores, failures)
curv_corr, curv_p = spearmanr(curv_scores, failures)

print("\nSpearman correlation with failure:")
print(f"Variance‑based: rho={var_corr:.3f}, p={var_p:.3e}")
print(f"Curvature‑based: rho={curv_corr:.3f}, p={curv_p:.3e}")

# Plot the distributions
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].hist(var_scores, bins=20, label='Variance index')
ax[0].set_xlabel('Integrated coeff. of variation')
ax[0].set_ylabel('Count')
ax[0].legend()
ax[1].hist(curv_scores, bins=20, label='Curvature index')
ax[1].set_xlabel('Abs(Ricci scalar)')
ax[1].set_ylabel('Count')
ax[1].legend()
plt.tight_layout()
plt.show()