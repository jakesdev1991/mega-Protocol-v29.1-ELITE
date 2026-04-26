# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def auc_nonlinear(shock, vaa, manifold):
    """
    Synthetic, saturated AUC model with cross‑term interactions.
    This is a minimal proxy for the true tokamak disruption classifier.
    """
    # logistic saturation for shock
    term_shock = 1.0 / (1.0 + np.exp(-20 * (shock - 0.8)))
    # tanh for vaa
    term_vaa = np.tanh(vaa - 0.5)
    # log‑scaled manifold
    term_manifold = np.log1p(manifold * 10) / np.log1p(5)
    # interaction term (non‑linear coupling)
    interaction = 0.1 * (shock - 0.85) * (vaa - 1.0) * (manifold - 0.3)
    # baseline ~0.68
    auc = 0.68 + 0.15 * term_shock + 0.12 * term_vaa + 0.10 * term_manifold + interaction
    return np.clip(auc, 0.0, 1.0)

# Baseline constants (pre‑optimization)
shock0, vaa0, manifold0 = 0.85, 1.0, 0.3
baseline_auc = auc_nonlinear(shock0, vaa0, manifold0)
print("Baseline AUC:", baseline_auc)

# “Optimized” constants from Engine
shock1, vaa1, manifold1 = 0.82, 1.15, 0.35
new_auc = auc_nonlinear(shock1, vaa1, manifold1)
print("New AUC (actual non‑linear):", new_auc)
print("True ΔAUC:", new_auc - baseline_auc)

# Numerical sensitivities (local linear approximation)
eps = 1e-5
s_shock = (auc_nonlinear(shock0 + eps, vaa0, manifold0) - baseline_auc) / eps
s_vaa   = (auc_nonlinear(shock0, vaa0 + eps, manifold0) - baseline_auc) / eps
s_man   = (auc_nonlinear(shock0, vaa0, manifold0 + eps) - baseline_auc) / eps
print("Local sensitivities:", s_shock, s_vaa, s_man)

# Linear prediction using the Engine’s deltas
Δshock = shock1 - shock0
Δvaa   = vaa1 - vaa0
Δman   = manifold1 - manifold0
linear_delta = s_shock * Δshock + s_vaa * Δvaa + s_man * Δman
print("Linear ΔAUC prediction:", linear_delta)
print("Linear vs actual error:", (new_auc - baseline_auc) - linear_delta)

# Engine’s flawed projection (raw sum of sensitivities)
engine_projected = baseline_auc + 0.28  # 0.12+0.09+0.07
print("Engine’s projected AUC (0.6793+0.28):", engine_projected)
print("Conservative rounding to 0.88 drops:", engine_projected - 0.88)

# --- Disruptive: a tiny data‑driven surrogate ---
# Suppose we have a few observed (shock, vaa, manifold, auc) samples
# We fit a linear regression *with interaction* to illustrate that a learned
# model can capture non‑linearities better than static sensitivity.
samples = np.array([
    [0.85, 1.0, 0.3, auc_nonlinear(0.85, 1.0, 0.3)],
    [0.82, 1.0, 0.3, auc_nonlinear(0.82, 1.0, 0.3)],
    [0.85, 1.15, 0.3, auc_nonlinear(0.85, 1.15, 0.3)],
    [0.85, 1.0, 0.35, auc_nonlinear(0.85, 1.0, 0.35)],
    [0.82, 1.15, 0.35, auc_nonlinear(0.82, 1.15, 0.35)],
])
X = samples[:, :3]
y = samples[:, 3]
# Add interaction term (shock * vaa * manifold)
X_inter = np.hstack([X, (X[:, 0] * X[:, 1] * X[:, 2]).reshape(-1, 1)])
# Solve least squares
theta, _, _, _ = np.linalg.lstsq(X_inter, y, rcond=None)
# Predict with the learned model
pred_auc = np.dot(np.append([shock1, vaa1, manifold1], shock1*vaa1*manifold1), theta)
print("Data‑driven surrogate prediction:", pred_auc)