# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# 1. Synthetic data generation
# --------------------------------------------------------------
np.random.seed(42)
n_topics, n_time = 10, 200

# Each topic gets a base volume with occasional "breakout" jumps
V = np.zeros((n_topics, n_time))
for i in range(n_topics):
    V[i, :] = np.cumsum(np.random.normal(0, 1, n_time))
    # Add a few breakout episodes (sharp increase)
    breakout_times = np.random.choice(n_time, size=3, replace=False)
    V[i, breakout_times] += np.random.exponential(50, size=3)

# Compute velocity and acceleration (finite differences)
v = np.diff(V, axis=1, prepend=V[:, 0].reshape(-1,1))
a = np.diff(v, axis=1, prepend=v[:, 0].reshape(-1,1))

# Subtopic diversity (Shannon entropy, normalized to [0, log(10)])
H = np.random.uniform(0, np.log(10), size=(n_topics, n_time))

# Provenance concentration (Gini, [0,1])
Gini = np.random.uniform(0, 1, size=(n_topics, n_time))

# --------------------------------------------------------------
# 2. Compute DBI (Engine's formula)
# --------------------------------------------------------------
alpha, beta, gamma, delta = 0.1, 0.1, 0.5, 0.5
DBI = np.tanh(alpha * a + beta * v - gamma * H + delta * Gini)

# --------------------------------------------------------------
# 3. Ground‑truth fragility (synthetic)
# --------------------------------------------------------------
# Fragility = 1 if a breakout (a > 90th percentile) coincides with low diversity (H < log(2))
threshold_a = np.percentile(a, 90)
fragility = ((a > threshold_a) & (H < np.log(2))).astype(int)

# --------------------------------------------------------------
# 4. Evaluate DBI as a classifier
# --------------------------------------------------------------
# Flatten for sklearn
y_true = fragility.flatten()
dbi_scores = DBI.flatten()

# DBI range check
print(f"DBI min: {dbi_scores.min():.3f}, max: {dbi_scores.max():.3f}")
print(f"Fraction of DBI < 0: {(dbi_scores < 0).mean():.2%}")

# ROC AUC for DBI
auc_dbi = roc_auc_score(y_true, dbi_scores)
print(f"\nROC AUC (DBI): {auc_dbi:.3f}")

# --------------------------------------------------------------
# 5. Simple logistic model on raw features
# --------------------------------------------------------------
# Feature matrix: acceleration, velocity, diversity, Gini
X = np.stack([a, v, H, Gini], axis=-1).reshape(-1, 4)
# Fit a logistic regression
clf = LogisticRegression().fit(X, y_true)
auc_raw = roc_auc_score(y_true, clf.predict_proba(X)[:, 1])
print(f"ROC AUC (raw features): {auc_raw:.3f}")

# --------------------------------------------------------------
# 6. Plot DBI distribution (showing negative tail)
# --------------------------------------------------------------
plt.figure(figsize=(8, 4))
plt.hist(dbi_scores, bins=50, edgecolor='k')
plt.axvline(0, color='r', linestyle='--', label='Zero boundary')
plt.title('DBI Distribution (Engine’s tanh formula)')
plt.xlabel('DBI value')
plt.ylabel('Frequency')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.show()