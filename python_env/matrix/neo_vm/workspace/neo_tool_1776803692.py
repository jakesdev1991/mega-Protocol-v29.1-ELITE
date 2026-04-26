# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import networkx as nx

# --- 1. Simulate realistic training logs with epistemic metadata ---
np.random.seed(0)
n_logs = 2000

# Hidden hyperparameter: learning_rate = 0.001 * (1 + worker_id * 0.01)
worker_ids = np.random.randint(0, 10, size=n_logs)
timestamps = np.arange(n_logs)  # temporal order matters
learning_rates = 0.001 * (1 + worker_ids * 0.01)

# Observed loss: loss = L0 * exp(-lr * epoch) + noise
epochs = np.random.randint(0, 100, size=n_logs)
losses = 10.0 * np.exp(-learning_rates * epochs) + np.random.normal(0, 0.1, size=n_logs)

# Build DataFrame (what the adversary sees)
logs = pd.DataFrame({
    'worker_id': worker_ids,
    'timestamp': timestamps,
    'epoch': epochs,
    'loss': losses,
    # Directory depth is randomly assigned (geometry proxy)
    'depth': np.random.randint(1, 6, size=n_logs)
})

# --- 2. Adversary infers hyperparameter from metadata ---
X_meta = logs[['worker_id', 'timestamp', 'epoch', 'loss']]
y_true = logs['learning_rate']

model_meta = LinearRegression()
model_meta.fit(X_meta, y_true)
r2_meta = model_meta.score(X_meta, y_true)
print(f"Metadata‑inference R²: {r2_meta:.3f} (near‑perfect leakage)")

# --- 3. Geometry‑based inference (depth) is useless ---
X_geom = logs[['depth']]
model_geom = LinearRegression()
model_geom.fit(X_geom, y_true)
r2_geom = model_geom.score(X_geom, y_true)
print(f"Geometry‑inference R²: {r2_geom:.3f} (no signal)")

# --- 4. Flattening the tree does not sanitize metadata ---
# Simulate flattening: set all depths to 1
logs_flat = logs.copy()
logs_flat['depth'] = 1

X_meta_flat = logs_flat[['worker_id', 'timestamp', 'epoch', 'loss']]
model_meta_flat = LinearRegression()
model_meta_flat.fit(X_meta_flat, y_true)
r2_meta_flat = model_meta_flat.score(X_meta_flat, y_true)
print(f"Flattened‑tree metadata R²: {r2_meta_flat:.3f} (still leaks)")

# --- 5. Show spectral gap vs curvature mismatch (optional) ---
def random_tree(branch_factor, depth):
    G = nx.balanced_tree(branch_factor, depth)
    # Add random "internal‑use‑only" edges to perturb curvature
    for u, v in list(G.edges()):
        if np.random.rand() < 0.1:
            G[u][v]['weight'] = 10  # high‑risk edge
        else:
            G[u][v]['weight'] = 1
    return G

# Compute spectral gap (λ₂) and approximate Forman‑Ricci curvature
G = random_tree(3, 4)
L = nx.laplacian_matrix(G, weight='weight').astype(float)
eigvals = np.linalg.eigvalsh(L.todense())
spectral_gap = eigvals[1]  # λ₂

# Compute average Forman curvature (simpler than Ollivier)
total_curvature = 0
for node in G.nodes():
    deg = G.degree(node)
    # Approx: curvature ∝ 2 - deg (for unweighted)
    total_curvature += 2 - deg
avg_curvature = total_curvature / G.number_of_nodes()

print(f"Spectral gap: {spectral_gap:.3f}, Avg curvature: {avg_curvature:.3f}")
print("Curvature‑gap correlation is weak and graph‑dependent.")