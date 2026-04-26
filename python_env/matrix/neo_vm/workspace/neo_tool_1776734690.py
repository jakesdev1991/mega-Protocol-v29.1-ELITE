# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math, random

# --- synthetic HSA memory-access data ---
np.random.seed(0)
N = 1000
blocks = 8
window = 50
# stable regime: Poisson(10) per block
# unstable regime (t>500): one block spikes to Poisson(100)
counts = np.zeros((N, blocks), dtype=int)
for t in range(N):
    if t > 500:
        lam = np.full(blocks, 10)
        lam[0] = 100  # spike on block 0
    else:
        lam = np.full(blocks, 10)
    counts[t] = np.random.poisson(lam)

# --- compute Shannon entropy S_h(t) from sliding window ---
S_h = np.full(N, np.nan)
for t in range(window, N):
    window_sum = counts[t-window:t].sum(axis=0)
    total = window_sum.sum()
    if total == 0:
        continue
    p = window_sum / total
    # avoid log(0)
    p = p[p > 0]
    S_h[t] = -np.sum(p * np.log(p))

# --- Informational Jerk via 3rd‑order finite difference ---
J_I = np.full(N, np.nan)
for t in range(3, N):
    if np.isnan(S_h[t]) or np.isnan(S_h[t-1]) or np.isnan(S_h[t-2]) or np.isnan(S_h[t-3]):
        continue
    J_I[t] = S_h[t] - 3*S_h[t-1] + 3*S_h[t-2] - S_h[t-3]

# --- variance of Jerk (proxy for "stability") ---
valid_jerk = J_I[~np.isnan(J_I)]
sigma_jerk = np.var(valid_jerk) if len(valid_jerk) > 0 else np.inf

# --- simple latency metric: mean + burst penalty ---
latency = np.full(N, 50.0)  # base latency 50 ns
# spike latency when total accesses > 300 in window
total_access = counts.sum(axis=1)
latency[total_access > 300] += 200.0  # +200 ns during burst
sigma_latency = np.var(latency)

# --- Lyapunov exponent via Rosenstein (simplified) ---
def simple_lyapunov(series, tau=1, dim=2):
    # naive time-delay embedding and divergence estimate
    N = len(series)
    if N < (dim-1)*tau + 10:
        return np.nan
    # compute Euclidean distances between nearest neighbors
    d0 = []
    for i in range(N - (dim-1)*tau):
        vec_i = series[i:i+(dim-1)*tau+1:tau]
        # find nearest neighbor ahead in time
        min_dist = np.inf
        for j in range(i+1, N - (dim-1)*tau):
            vec_j = series[j:j+(dim-1)*tau+1:tau]
            d = np.linalg.norm(vec_i - vec_j)
            if d < min_dist:
                min_dist = d
        if min_dist < np.inf and min_dist > 0:
            d0.append(min_dist)
    if len(d0) < 10:
        return np.nan
    # average log divergence (crude LLE)
    return np.mean(np.log(np.array(d0))) / tau

# compute on total access (proxy for memory traffic)
lle = simple_lyapunov(total_access.astype(float))

print(f"Jerk variance (σ²_jerk): {sigma_jerk:.6e}")
print(f"Latency variance (σ²_latency): {sigma_latency:.6e}")
print(f"Estimated Lyapunov exponent λ_max: {lle:.6f}")
if lle > 0:
    print("Shredding detected: λ_max > 0 (unstable dynamics).")
else:
    print("System stable: λ_max ≤ 0.")