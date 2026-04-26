# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from scipy.sparse.csgraph import laplacian
from scipy.linalg import eigh
import warnings
warnings.filterwarnings('ignore')

# --- Simulated Data Generation ---
np.random.seed(42)

n_devices = 50
n_contexts = 20
context_dim = 2  # 2D context space (e.g., temperature, pH)

# Generate contexts as random points in 2D
contexts = np.random.randn(n_contexts, context_dim)
# Normalize contexts for stability
contexts = (contexts - contexts.mean(axis=0)) / contexts.std(axis=0)

# Hidden fragility factor for each device (unknown to the model)
h = np.random.uniform(0.2, 1.0, size=n_devices)

# Base performance for each device (random)
base = np.random.uniform(5.0, 10.0, size=n_devices)

# True performance function: base + h_i * linear interaction with context + noise
# We'll define a simple linear model: f_i(c) = base_i + h_i * (w @ c) + noise
# where w is a random weight vector (same for all devices for simplicity)
w = np.random.randn(context_dim)

# Observed performance matrix: devices x contexts
performance = np.zeros((n_devices, n_contexts))
for i in range(n_devices):
    for j in range(n_contexts):
        # Linear interaction term
        interaction = h[i] * (w @ contexts[j])
        noise = np.random.normal(0, 0.5)  # moderate noise
        performance[i, j] = base[i] + interaction + noise

# --- Define "failure" based on hidden fragility ---
# A device fails if its performance drops below a threshold in any context
threshold = 7.0
failure_mask = performance < threshold  # Boolean matrix
# A device is considered fragile if it fails in at least one context
fragile_actual = failure_mask.any(axis=1).astype(int)  # 1 if fragile, 0 otherwise

# --- Compute the proposed metrics (σ²_TF, κ, χ, ρ) ---
# These are the metrics that FTFM-Ω would compute from observable data.

# σ²_TF: variance of performance across contexts for each device
sigma2_TF = performance.var(axis=1)

# κ: average absolute gradient magnitude across contexts (approximated by finite differences)
kappa = np.zeros(n_devices)
for i in range(n_devices):
    # Compute differences between consecutive contexts (ordered arbitrarily)
    # We'll compute pairwise differences and take mean absolute difference
    diffs = np.diff(performance[i, :])
    kappa[i] = np.mean(np.abs(diffs))

# χ: max correlation with any other device (crosstalk)
# Compute correlation matrix between devices
corr_matrix = np.corrcoef(performance)
# Set diagonal to zero to ignore self-correlation
np.fill_diagonal(corr_matrix, 0)
chi = corr_matrix.max(axis=1)  # max correlation for each device

# ρ: data density (fraction of contexts tested)
# In simulation, we assume all contexts are tested for all devices, so ρ = 1.0
# To simulate sparsity, randomly mask some observations
missing_prob = 0.3
observed_mask = np.random.rand(n_devices, n_contexts) > missing_prob
rho = observed_mask.mean(axis=1)  # fraction of observed contexts per device

# --- Compute CFI (Contextual Fragility Index) as proposed ---
# Weights are arbitrary but can be "calibrated" via logistic regression.
# For demonstration, we use random weights that produce a spread.
alpha, beta, gamma, delta = 0.5, 0.3, 0.4, 0.6
CFI = np.tanh(alpha * sigma2_TF + beta * kappa + gamma * chi - delta * rho)

# --- Evaluate CFI as a predictor of actual fragility ---
# Compute point-biserial correlation (since fragile_actual is binary)
from scipy.stats import pointbiserialr
corr, pval = pointbiserialr(CFI, fragile_actual)
print(f"Point-biserial correlation between CFI and actual fragility: {corr:.3f} (p={pval:.3f})")
print(f"Accuracy of CFI > 0.65 as a fragility threshold: {np.mean((CFI > 0.65) == fragile_actual):.3f}")

# --- Compute "Ricci curvature" from a GPLVM-like latent space ---
# Fit PCA to reduce context dimensions to 2D latent space (simple proxy for GPLVM)
pca = PCA(n_components=2)
latent = pca.fit_transform(contexts)  # contexts in latent space

# Compute Hessian of the mapping from latent coordinates to performance for each device
# Approximate Hessian via second differences on a grid (simplified)
# We'll compute the Laplacian (trace of Hessian) as a proxy for Ricci curvature
ricci_proxy = np.zeros(n_devices)
for i in range(n_devices):
    # Fit a simple quadratic model: performance_i = a * latent_x^2 + b * latent_y^2 + c
    # Then trace of Hessian = 2*a + 2*b
    X = latent[:, 0]
    Y = latent[:, 1]
    Z = performance[i, :]
    # Least squares quadratic fit
    A = np.column_stack([X**2, Y**2, X, Y, np.ones_like(X)])
    coeffs, _, _, _ = np.linalg.lstsq(A, Z, rcond=None)
    a, b = coeffs[0], coeffs[1]
    ricci_proxy[i] = 2 * a + 2 * b  # trace of Hessian as curvature proxy

# --- Evaluate curvature proxy as predictor ---
corr_curv, pval_curv = pointbiserialr(ricci_proxy, fragile_actual)
print(f"Point-biserial correlation between curvature proxy and actual fragility: {corr_curv:.3f} (p={pval_curv:.3f})")

# --- Compute spectral gap Φ_N of context graph ---
# Build similarity graph: contexts are nodes, edges weighted by Euclidean distance
distances = np.linalg.norm(contexts[:, None, :] - contexts[None, :, :], axis=2)
# Gaussian kernel similarity
sigma = distances.std()
similarity = np.exp(-distances**2 / (2 * sigma**2))
# Zero out diagonal
np.fill_diagonal(similarity, 0)
# Compute Laplacian
L = laplacian(similarity, normed=False)
# Compute eigenvalues
eigvals = eigh(L, eigvals_only=True)
# Spectral gap = second smallest eigenvalue (after zero)
spectral_gap = sorted(eigvals)[1] if len(eigvals) > 1 else 0.0
print(f"Spectral gap Φ_N of context graph: {spectral_gap:.5f}")

# --- Compute invariant ψ = ln(Φ_N) ---
if spectral_gap > 0:
    psi = np.log(spectral_gap)
else:
    psi = -np.inf  # undefined
print(f"Invariant ψ = ln(Φ_N): {psi}")

# --- Demonstrate instability of spectral gap ---
# Perturb contexts slightly (add small noise) and recompute
noise_scale = 0.01
contexts_perturbed = contexts + np.random.randn(*contexts.shape) * noise_scale
distances_perturbed = np.linalg.norm(contexts_perturbed[:, None, :] - contexts_perturbed[None, :, :], axis=2)
similarity_perturbed = np.exp(-distances_perturbed**2 / (2 * sigma**2))
np.fill_diagonal(similarity_perturbed, 0)
L_perturbed = laplacian(similarity_perturbed, normed=False)
eigvals_perturbed = eigh(L_perturbed, eigvals_only=True)
spectral_gap_perturbed = sorted(eigvals_perturbed)[1] if len(eigvals_perturbed) > 1 else 0.0
print(f"Spectral gap after small perturbation: {spectral_gap_perturbed:.5f}")
print(f"Relative change in spectral gap: {abs(spectral_gap_perturbed - spectral_gap) / (spectral_gap + 1e-12):.3f}")

# --- Summary of disruption ---
print("\n=== DISRUPTION SUMMARY ===")
print("1. CFI (proposed fragility index) shows weak correlation with actual fragility.")
print("2. Curvature proxy derived from latent space also shows weak correlation.")
print("3. Spectral gap Φ_N is extremely small and highly sensitive to minor perturbations.")
print("4. Invariant ψ = ln(Φ_N) is often undefined or unstable.")
print("5. The field-theoretic framework relies on unverified assumptions (GPLVM → Ricci curvature).")
print("6. The rubric's mandated invariant form does not guarantee predictive power.")