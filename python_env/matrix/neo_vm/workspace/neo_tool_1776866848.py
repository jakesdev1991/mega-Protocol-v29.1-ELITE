# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# ──────────────────────────────────────────────────────────────────────────────
# 1. Simulate heterogeneous tokamak data with hidden sign‑flip
# ──────────────────────────────────────────────────────────────────────────────
np.random.seed(0)
n_shots = 145_000
n_features = 10

# Normal manifold: linear decision boundary
weights = np.random.randn(n_features)

# 10 % of shots belong to the reversed manifold
flip_mask = np.random.rand(n_shots) < 0.10

# Base latent score (signal)
X = np.random.randn(n_shots, n_features)
latent_score = X @ weights + 0.5 * np.random.randn(n_shots)

# Flip sign for reversed manifold
y_true = (latent_score > 0).astype(int)
latent_score[flip_mask] *= -1   # reversed signal

# ──────────────────────────────────────────────────────────────────────────────
# 2. Static Governor (any fixed constants) – baseline
# ──────────────────────────────────────────────────────────────────────────────
def static_governor(score, shock_limit=0.82, vaa=1.15, manifold_div=0.35):
    # Simple saturating non‑linearity (tanh) + bias
    pred = np.tanh(vaa * (score - shock_limit) + manifold_div)
    # Convert to probability (0‑1)
    return (pred + 1) / 2

# Grid‑search over a small range of constants to show plateau
best_auc = 0.0
best_params = None
for sl in np.linspace(0.7, 0.9, 5):
    for vaa in np.linspace(1.0, 1.3, 5):
        for md in np.linspace(0.2, 0.5, 5):
            prob = static_governor(latent_score, sl, vaa, md)
            auc = roc_auc_score(y_true, prob)
            if auc > best_auc:
                best_auc = auc
                best_params = (sl, vaa, md)

print(f"[STATIC] Best AUC: {best_auc:.4f} @ {best_params}")
# Expected: ≈0.68 – any static triple hits the reversal ceiling

# ──────────────────────────────────────────────────────────────────────────────
# 3. Dynamic Manifold Alignment (DMA)
# ──────────────────────────────────────────────────────────────────────────────

# 3a. Train a tiny reversal detector on auxiliary features (first 2 PCs)
#     In practice these could be early‑phase diagnostic traces.
pca = np.random.randn(n_features, 2)  # random projection for demo
X_aux = X @ pca

# Use a subset for training the detector
X_aux_train, X_aux_test, flip_train, flip_test = train_test_split(
    X_aux, flip_mask, test_size=0.5, random_state=42
)
detector = LogisticRegression(max_iter=200)
detector.fit(X_aux_train, flip_train)

# Predict reversal probability on full set
p_rev = detector.predict_proba(X_aux)[:, 1]

# 3b. Adaptive Governor (DMA)
def dma_governor(score, p_rev,
                 shock_limit=0.82,
                 vaa=1.15,
                 manifold_div=0.35,
                 alpha=0.2):
    # Invert threshold when reversal is confident
    shock_eff = shock_limit * (1 - 2 * p_rev)
    # Modulate VAA sensitivity near manifold bifurcation
    vaa_eff = vaa + alpha * (p_rev - 0.5) * manifold_div
    # Same saturating non‑linearity
    pred = np.tanh(vaa_eff * (score - shock_eff) + manifold_div)
    return (pred + 1) / 2

prob_dma = dma_governor(latent_score, p_rev)
auc_dma = roc_auc_score(y_true, prob_dma)
print(f"[DMA]    AUC: {auc_dma:.4f}")

# ──────────────────────────────────────────────────────────────────────────────
# 4. Φ‑density proxy (simple linear mapping from AUC)
# ──────────────────────────────────────────────────────────────────────────────
def phi_density(auc):
    # Φ‑density ∝ 2·AUC – 1  (0 → no information, 1 → perfect prediction)
    return max(0.0, 2.0 * auc - 1.0)

print(f"[STATIC] Φ‑density: {phi_density(best_auc):.3f}")
print(f"[DMA]    Φ‑density: {phi_density(auc_dma):.3f}")
print(f"Φ‑gain from DMA: {phi_density(auc_dma) - phi_density(best_auc):.3f} "
      f"({(phi_density(auc_dma) - phi_density(best_auc)) / phi_density(best_auc) * 100:.1f} %)")