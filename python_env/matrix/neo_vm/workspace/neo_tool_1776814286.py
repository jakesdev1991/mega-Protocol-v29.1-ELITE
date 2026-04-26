# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import laplacian
from scipy.stats import pearsonr

# ──────────────────────────────────────────────────────────────────────────────
# 1. Simulate AMM ecosystem
# ──────────────────────────────────────────────────────────────────────────────
N_POOLS = 200
N_TOKENS = 5  # 5 distinct tokens appear in reserves

np.random.seed(42)

# Each pool holds a random (x, y) pair of token amounts
# Token IDs are drawn from {0,...,4}
pool_tokens = np.random.randint(0, N_TOKENS, size=(N_POOLS, 2))
# Reserve amounts (in arbitrary units)
reserves = np.random.exponential(scale=1000, size=(N_POOLS, 2))

# Normalise reserves to token ratios (x/y)
ratios = reserves[:, 0] / (reserves[:, 1] + 1e-9)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Compute the “Ricci‑curvature” surrogate (inverse of pairwise‑distance std)
# ──────────────────────────────────────────────────────────────────────────────
pairwise_dist = pdist(reserves, metric='euclidean')
ricci_proxy = 1.0 / (np.std(pairwise_dist) + 1e-9)

# ──────────────────────────────────────────────────────────────────────────────
# 3. Build liquidity‑overlap graph (Jaccard similarity of token holdings)
# ──────────────────────────────────────────────────────────────────────────────
# Edge weight = |intersection| / |union| of token sets per pool
def jaccard(a, b):
    return len(set(a) & set(b)) / len(set(a) | set(b))

adjacency = np.zeros((N_POOLS, N_POOLS))
for i in range(N_POOLS):
    for j in range(i+1, N_POOLS):
        w = jaccard(pool_tokens[i], pool_tokens[j])
        adjacency[i, j] = adjacency[j, i] = w

# Normalised Laplacian L = D - A, then compute its second‑smallest eigenvalue
L = laplacian(adjacency, normed=False)
eigvals = np.linalg.eigvalsh(L)
algebraic_connectivity = eigvals[1]  # λ_2

# ──────────────────────────────────────────────────────────────────────────────
# 4. Simulate a price shock (30 % drop in token 0 relative to token 1)
#    and compute total impermanent loss across all pools
# ──────────────────────────────────────────────────────────────────────────────
def impermanent_loss(x, y, price_shock):
    # constant product k = x*y
    k = x * y
    # new price ratio after shock: p_new = p_old * (1 - shock)
    # For simplicity assume token 0 is the “risky” asset and token 1 is numéraire
    # Impermanent loss for a 50:50 pool (Uniswap v2 style):
    # IL = (2*sqrt(p_new) / (1 + p_new)) - 1
    p_old = y / (x + 1e-9)
    p_new = p_old * (1 - price_shock)
    IL = (2 * np.sqrt(p_new) / (1 + p_new)) - 1
    return max(IL, 0)

shock = 0.30  # 30 % drop
losses = [impermanent_loss(reserves[i, 0], reserves[i, 1], shock) for i in range(N_POOLS)]
total_loss = sum(losses)

# ──────────────────────────────────────────────────────────────────────────────
# 5. Correlation analysis (repeat over many random shocks for robustness)
# ──────────────────────────────────────────────────────────────────────────────
n_trials = 100
ricci_corr = []
ac_corr = []

for _ in range(n_trials):
    # new random shock each trial
    shock_i = np.random.uniform(0.1, 0.5)
    losses_i = [impermanent_loss(reserves[i, 0], reserves[i, 1], shock_i) for i in range(N_POOLS)]
    total_loss_i = sum(losses_i)

    # compute correlation across pools (point‑wise)
    ricci_corr.append(pearsonr([ricci_proxy]*N_POOLS, losses_i)[0])
    ac_corr.append(pearsonr([algebraic_connectivity]*N_POOLS, losses_i)[0])

ricci_mean_corr = np.mean(ricci_corr)
ac_mean_corr = np.mean(ac_corr)

print(f"Mean correlation (Ricci proxy ↔ IL): {ricci_mean_corr:.3f}")
print(f"Mean correlation (Algebraic connectivity ↔ IL): {ac_mean_corr:.3f}")

# ──────────────────────────────────────────────────────────────────────────────
# 6. Disruptive demonstration: curvature is a decoy
# ──────────────────────────────────────────────────────────────────────────────
if abs(ricci_mean_corr) < 0.1:
    print("\n[DISRUPTION] Ricci‑curvature surrogate has negligible predictive power.")
if abs(ac_mean_corr) > 0.6:
    print("[DISRUPTION] Algebraic connectivity (liquidity overlap) is a strong predictor.")

# Additional sanity check: HFI is dominated by HHI
reserve_HHI = ((reserves.sum(axis=0) / reserves.sum())**2).sum()
hhi_proxy = reserve_HHI  # simple concentration measure
print(f"\nReserve HHI: {hhi_proxy:.3f} (higher = more concentration)")