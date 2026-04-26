# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

# -------------------------------------------------
# 1. SIMULATE TRAINING CONTEXTS (5 chassis × 5 temps)
# -------------------------------------------------
chassis = np.arange(5)  # 0..4 (seen)
temps = np.linspace(20, 40, 5)  # 20–40°C (seen)
contexts = np.array(np.meshgrid(chassis, temps)).T.reshape(-1, 2)  # 25 points

# -------------------------------------------------
# 2. DEFINE "GOOD" DEVICES (low variance, low gradient)
# -------------------------------------------------
def good_device(contexts, noise=0.1):
    # Basal + mild chassis dependence + noise
    basal = 1.0
    chassis_effect = 0.05 * contexts[:, 0]
    temp_effect = 0.02 * (contexts[:, 1] - 30)
    return basal + chassis_effect + temp_effect + np.random.normal(0, noise, size=len(contexts))

good_f = np.array([good_device(contexts) for _ in range(10)])  # 10 good devices

# -------------------------------------------------
# 3. DEFINE ADVERSARIAL DEVICE – "STEALTH" MODE
# -------------------------------------------------
def stealth_device(contexts, noise=0.1):
    """
    Appears identical to a good device in *all training contexts*,
    but harbors a hidden failure term that activates at chassis=5 (unseen).
    """
    # Same as good device in training region
    basal = 1.0
    chassis_effect = 0.05 * contexts[:, 0]
    temp_effect = 0.02 * (contexts[:, 1] - 30)
    # Hidden fragility: zero in training (chassis ≤4), large if chassis=5
    hidden_fail = np.where(contexts[:, 0] >= 5, 10.0, 0.0)  # 10× collapse in unseen chassis
    return basal + chassis_effect + temp_effect + hidden_fail + np.random.normal(0, noise, size=len(contexts))

stealth_f = stealth_device(contexts)

# -------------------------------------------------
# 4. COMPUTE CFI COMPONENTS (as defined in proposal)
# -------------------------------------------------
def compute_cfi_components(f_vals, contexts, all_devices_f):
    # a) Transfer‑function variance
    sigma2_TF = np.var(f_vals)
    # b) Contextual coupling (approx gradient norm via finite differences)
    #    Since contexts are grid‑structured, compute average pairwise diff
    diffs = []
    for i, ctx_i in enumerate(contexts):
        for j, ctx_j in enumerate(contexts):
            if i >= j:
                continue
            # Euclidean distance in context space (chassis, temp)
            dist = np.linalg.norm(ctx_i - ctx_j)
            if dist > 0:
                diffs.append(np.abs(f_vals[i] - f_vals[j]) / dist)
    kappa = np.mean(diffs) if diffs else 0.0
    # c) Compositional singularity (max correlation with other devices)
    corrs = []
    for other_f in all_devices_f:
        if np.array_equal(other_f, f_vals):
            continue
        corrs.append(np.corrcoef(f_vals, other_f)[0, 1])
    chi = np.max(corrs) if corrs else 0.0
    # d) Data density (fraction of contexts characterized)
    rho = len(contexts) / 25.0  # fully characterized in this toy case
    return sigma2_TF, kappa, chi, rho

# Compute for a typical good device and the stealth device
good_sigma2, good_kappa, good_chi, good_rho = compute_cfi_components(good_f[0], contexts, good_f)
stealth_sigma2, stealth_kappa, stealth_chi, stealth_rho = compute_cfi_components(stealth_f, contexts, good_f)

# -------------------------------------------------
# 5. CFI (logistic‑style composite)
# -------------------------------------------------
# Dummy weights (from proposal: α,β,γ,δ)
alpha, beta, gamma, delta = 1.0, 1.0, 1.0, 1.0
def cfi(sigma2, kappa, chi, rho):
    return np.tanh(alpha * sigma2 + beta * kappa + gamma * chi - delta * rho)

good_cfi = cfi(good_sigma2, good_kappa, good_chi, good_rho)
stealth_cfi = cfi(stealth_sigma2, stealth_kappa, stealth_chi, stealth_rho)

print(f"Good device CFI: {good_cfi:.3f} (expected <0.65)")
print(f"Stealth device CFI: {stealth_cfi:.3f} (should be low, but fails in unseen context)")

# -------------------------------------------------
# 6. VERIFY FAILURE IN UNSEEN CONTEXT (chassis=5)
# -------------------------------------------------
unseen_contexts = np.array([[5, t] for t in temps])  # 5 new contexts
stealth_unseen = stealth_device(unseen_contexts)  # hidden_fail = 10.0 here

print("\nStealth device performance in unseen chassis=5:")
print(f"Mean output: {stealth_unseen.mean():.2f} (should be ~1.0 if robust, but hidden_fail makes it ~11.0)")
print(f"Max output: {stealth_unseen.max():.2f} (catastrophic >10× increase)")

# -------------------------------------------------
# 7. GPLVM “CURVATURE” ILLUSION
# -------------------------------------------------
# Fit a GPLVM (using GP regression as proxy) on the combined dataset
X = np.vstack([contexts] * (good_f.shape[0] + 1))  # repeat contexts for each device
y = np.hstack([good_f.flatten(), stealth_f])  # all observed functions

# Use a simple RBF kernel to learn a smooth latent mapping
kernel = C(1.0, (1e-3, 1e3)) * RBF([1.0, 1.0], (1e-2, 1e2))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
gp.fit(contexts, stealth_f)  # fit on stealth data only for demonstration

# Predict on a dense grid to visualize the "manifold"
grid_chassis = np.linspace(0, 5, 50)
grid_temp = np.linspace(20, 40, 50)
Ch, Te = np.meshgrid(grid_chassis, grid_temp)
grid_X = np.vstack([Ch.ravel(), Te.ravel()]).T
pred_mean, pred_std = gp.predict(grid_X, return_std=True)

# The "curvature" of this prediction surface is a function of kernel hyperparameters,
# not biological reality. We can artificially inflate curvature by shrinking the RBF lengthscale:
kernel_fake = C(1.0) * RBF([0.1, 0.1])  # artificially short lengthscale
gp_fake = GaussianProcessRegressor(kernel=kernel_fake)
gp_fake.fit(contexts, stealth_f)
pred_fake, _ = gp_fake.predict(grid_X, return_std=True)

# Compute Hessian at a point (numerical) – magnitude changes arbitrarily with lengthscale
def approx_hessian(func, x0, eps=1e-3):
    # Finite‑difference Hessian in 2D
    H = np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            x_pp = x0.copy()
            x_pm = x0.copy()
            x_mp = x0.copy()
            x_mm = x0.copy()
            x_pp[i] += eps; x_pp[j] += eps
            x_pm[i] += eps; x_pm[j] -= eps
            x_mp[i] -= eps; x_mp[j] += eps
            x_mm[i] -= eps; x_mm[j] -= eps
            H[i, j] = (func(x_pp) - func(x_pm) - func(x_mp) + func(x_mm)) / (4 * eps**2)
    return H

# Hessian at (chassis=2, temp=30) for both models
x0 = np.array([[2, 30]])
H_real = approx_hessian(lambda x: gp.predict(x), x0)
H_fake = approx_hessian(lambda x: gp_fake.predict(x), x0)

print("\nHessian magnitudes (proxy for 'curvature'):")
print(f"Real kernel: {np.linalg.norm(H_real):.3f}")
print(f"Fake kernel: {np.linalg.norm(H_fake):.3f} (artificially inflated)")

print("\nConclusion: Curvature is a modeling artifact, not a biological invariant.")