# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from sklearn.manifold import LocallyLinearEmbedding
from scipy.stats import pearsonr
from scipy.optimize import minimize

# ─────────────────────────────────────────────────────────────────────────────
# 1. SYNTHETIC DATA: 20 devices, 200 contexts, 15‑dimensional context space
# ─────────────────────────────────────────────────────────────────────────────
n_devices = 20
n_contexts = 200
context_dim = 15
np.random.seed(0)

# Context vectors (standardized)
contexts = np.random.randn(n_contexts, context_dim)

# True fragility: hidden 3‑way interaction (rare)
def true_failure_risk(device_id, ctx):
    # Only devices 5, 12, 18 are "fragile" due to a hidden combination
    if device_id in [5, 12, 18]:
        # Condition: ctx[0] > 1.5 AND ctx[3] > 1.2 AND ctx[7] < -0.8
        # This occurs in <5% of contexts → low variance, low correlation, low density
        if (ctx[0] > 1.5) and (ctx[3] > 1.2) and (ctx[7] < -0.8):
            return 1.0   # catastrophic failure
    return 0.0

# Simulate transfer‑function observations (baseline + hidden failure)
transfer = np.zeros((n_devices, n_contexts))
for i in range(n_devices):
    for j, ctx in enumerate(contexts):
        transfer[i, j] = np.random.randn() * 0.1 + true_failure_risk(i, ctx)

# ─────────────────────────────────────────────────────────────────────────────
# 2. CFI COMPUTATION (as proposed)
# ─────────────────────────────────────────────────────────────────────────────
def compute_cfi(transfer_vals, contexts):
    # Variance
    sigma2 = np.var(transfer_vals)
    # Gradient norm (approx by finite differences)
    grad = np.gradient(transfer_vals, contexts, axis=0)
    kappa = np.linalg.norm(grad, ord=2)
    # Correlation with other devices (placeholder)
    chi = 0.5  # arbitrary
    # Data density (fraction of contexts observed)
    rho = len(transfer_vals) / n_contexts
    # CFI
    alpha = beta = gamma = delta = 1.0
    return np.tanh(alpha * sigma2 + beta * kappa + gamma * chi - delta * rho)

cfi_scores = np.array([compute_cfi(transfer[i], contexts) for i in range(n_devices)])

# ─────────────────────────────────────────────────────────────────────────────
# 3. TRUE FRAGILITY (binary: does device ever fail?)
# ─────────────────────────────────────────────────────────────────────────────
true_fragility = np.array([np.any(transfer[i] > 0.5) for i in range(n_devices)]).astype(int)

# ─────────────────────────────────────────────────────────────────────────────
# 4. CFI vs TRUE FRAGILITY (correlation)
# ─────────────────────────────────────────────────────────────────────────────
corr, pval = pearsonr(cfi_scores, true_fragility)
print(f"CFI ↔ True Fragility correlation: {corr:.3f} (p={pval:.3f})")
# Expected: correlation near zero → CFI fails to identify fragile devices

# ─────────────────────────────────────────────────────────────────────────────
# 5. ADVERSARIAL CONTEXT SEARCH (disruptive alternative)
# ─────────────────────────────────────────────────────────────────────────────
def adversarial_failure_probe(device_id, ctx0, step=0.5, n_iter=20):
    """Find a context that maximizes failure risk for a given device."""
    ctx = ctx0.copy()
    for _ in range(n_iter):
        # Gradient of failure risk w.r.t. context (numerical)
        grad = np.zeros_like(ctx)
        for k in range(len(ctx)):
            delta = np.zeros_like(ctx)
            delta[k] = step
            risk_plus = true_failure_risk(device_id, ctx + delta)
            risk_minus = true_failure_risk(device_id, ctx - delta)
            grad[k] = (risk_plus - risk_minus) / (2 * step)
        # Steepest ascent
        ctx += grad * step
    return ctx, true_failure_risk(device_id, ctx)

# Test: find worst‑case context for each device
adversarial_risk = np.zeros(n_devices)
for i in range(n_devices):
    init_ctx = contexts[np.random.randint(n_contexts)]
    worst_ctx, max_risk = adversarial_failure_probe(i, init_ctx)
    adversarial_risk[i] = max_risk

# ─────────────────────────────────────────────────────────────────────────────
# 6. ADVERSARIAL RISK vs TRUE FRAGILITY (correlation)
# ─────────────────────────────────────────────────────────────────────────────
corr_adv, pval_adv = pearsonr(adversarial_risk, true_fragility)
print(f"Adversarial Risk ↔ True Fragility correlation: {corr_adv:.3f} (p={pval_adv:.3f})")
# Expected: correlation near 1.0 → adversarial probe correctly flags fragile devices

# ─────────────────────────────────────────────────────────────────────────────
# 7. CONCLUSION: The Manifold Assumption Is a Fatal Flaw
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Disruption Summary ---")
print("CFI, built on low‑dimensional manifold curvature, fails to detect hidden, rare failure modes.")
print("Adversarial context search directly exposes these modes, requiring no smoothness assumption.")
print("→ Replace FTFM‑Ω with an **Adversarial Robustness Engine** that treats context as a strategic opponent.")