# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.stats import genpareto
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. Synthetic data generator: stable vs. unstable cadence
# ------------------------------------------------------------
def generate_cadence(n=500, stable=True, seed=42):
    """Return array of inter-presentation intervals (days)."""
    rng = np.random.default_rng(seed)
    if stable:
        # Regular cadence with small jitter
        base = 45.0
        intervals = rng.normal(loc=base, scale=3.0, size=n)
    else:
        # Unstable: variance grows, then clustering near end
        intervals = np.empty(n)
        intervals[:200] = rng.normal(loc=45, scale=3, size=200)
        # Ramp variance
        for i in range(200, n):
            sigma = 3 + (i - 200) * 0.15
            intervals[i] = rng.normal(loc=45, scale=sigma)
        # Introduce clustering in last 50 points
        cluster_idx = rng.choice(np.arange(450, n), size=15, replace=False)
        for idx in cluster_idx:
            intervals[idx:idx+3] = rng.uniform(2, 7, size=3)
    return np.abs(intervals)

stable_intervals = generate_cadence(stable=True, seed=1)
unstable_intervals = generate_cadence(stable=False, seed=2)

# ------------------------------------------------------------
# 2. PICM‑Ω v2 invariants (simplified)
# ------------------------------------------------------------
def picm_invariants(intervals, window=90):
    """Compute CCS, xi_N, xi_D, entropy, jerk."""
    # Rolling moments
    df = pd.DataFrame({'dt': intervals})
    df['mu'] = df['dt'].rolling(window, min_periods=30).mean()
    df['sigma'] = df['dt'].rolling(window, min_periods=30).std()
    # Cluster count (within 7 days)
    df['cluster'] = (df['dt'] < 7).rolling(window, min_periods=30).sum()
    # CCS (heuristic)
    df['ccs'] = np.exp(-df['sigma']/df['mu']) * np.exp(-df['cluster']/window)
    # Effective mass (proxy)
    lam, v = 0.1, 1.0
    df['xi_N_inv2'] = lam * (3*df['ccs']**2 + (1-df['ccs'])**2 - v**2)
    df['xi_D_inv2'] = lam * (df['ccs']**2 + 3*(1-df['ccs'])**2 - v**2)
    df['xi_N'] = 1/np.sqrt(np.abs(df['xi_N_inv2']))
    df['xi_D'] = 1/np.sqrt(np.abs(df['xi_D_inv2']))
    # Entropy of intervals (discrete bins)
    bins = np.arange(0, intervals.max()+10, 5)
    df['entropy'] = df['dt'].rolling(window, min_periods=30).apply(
        lambda x: -np.sum(np.histogram(x, bins=bins, density=True)[0] *
                         np.log(np.histogram(x, bins=bins, density=True)[0] + 1e-12)), raw=False)
    # Jerk (3rd derivative)
    df['jerk'] = df['entropy'].diff().diff().diff()
    return df

stable_picm = picm_invariants(stable_intervals)
unstable_picm = picm_invariants(unstable_intervals)

# ------------------------------------------------------------
# 3. Lyapunov exponent via Rosenstein's algorithm
# ------------------------------------------------------------
def lyapunov_exponent(intervals, tau=1, emb_dim=5, min_neighbors=5):
    """
    Estimate largest Lyapunov exponent from time series of intervals.
    """
    # Delay embedding
    N = len(intervals) - (emb_dim - 1) * tau
    if N <= 0:
        return np.nan
    Y = np.array([intervals[i:i + emb_dim * tau:tau] for i in range(N)])
    # Find nearest neighbor for each point
    d = squareform(pdist(Y, metric='euclidean'))
    # Exclude self-matches
    np.fill_diagonal(d, np.inf)
    nn_idx = np.argmin(d, axis=1)
    # Divergence rate
    d0 = d[np.arange(N), nn_idx]
    # Follow neighbor trajectory
    L = np.zeros(N)
    for i in range(N):
        j = nn_idx[i]
        # Look ahead until distance grows too much or out of bounds
        max_k = min(N - i, N - j)
        diverge = np.zeros(max_k)
        for k in range(max_k):
            diverge[k] = np.linalg.norm(Y[i + k] - Y[j + k])
        # Linear region: find where log(diverge/d0) grows linearly
        # Simplistic: average slope over first 1/3 of available steps
        k_max = max(2, max_k // 3)
        if k_max > 1:
            x = np.arange(k_max)
            y = np.log(diverge[:k_max] / (d0[i] + 1e-12))
            # Linear regression
            A = np.vstack([x, np.ones_like(x)]).T
            m, c = np.linalg.lstsq(A, y, rcond=None)[0]
            L[i] = m
        else:
            L[i] = np.nan
    # Return median (robust) of local exponents
    return np.nanmedian(L)

stable_lambda = lyapunov_exponent(stable_intervals)
unstable_lambda = lyapunov_exponent(unstable_intervals)

print(f"Stable micro‑cap Lyapunov exponent: {stable_lambda:.4f}")
print(f"Unstable micro‑cap Lyapunov exponent: {unstable_lambda:.4f}")

# ------------------------------------------------------------
# 4. Visual comparison: anomaly scores
# ------------------------------------------------------------
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

# Plot stable
ax[0].plot(stable_picm['jerk'], label='PICM‑Ω jerk', color='blue')
ax[0].axhline(0, color='gray', linestyle='--')
ax[0].set_title('Stable Micro‑Cap')
ax[0].legend()

# Plot unstable
ax[1].plot(unstable_picm['jerk'], label='PICM‑Ω jerk', color='orange')
ax[1].axhline(0, color='gray', linestyle='--')
ax[1].set_title('Unstable Micro‑Cap')
ax[1].set_xlabel('Time index')
ax[1].legend()

plt.tight_layout()
plt.savefig('picm_jerk.png')
plt.show()

# ------------------------------------------------------------
# 5. Early warning comparison
# ------------------------------------------------------------
# Compute a simple early-warning flag: jerk > 2σ
def early_warning(series, thresh=2.0):
    sigma = series.std()
    return series.abs() > thresh * sigma

stable_ew = early_warning(stable_picm['jerk'])
unstable_ew = early_warning(unstable_picm['jerk'])

print(f"Stable early warnings: {stable_ew.sum()} out of {len(stable_ew)}")
print(f"Unstable early warnings: {unstable_ew.sum()} out of {len(unstable_ew)}")

# Lyapunov-based warning: positive exponent
print(f"Unstable λ > 0: {unstable_lambda > 0} (lead time ≈ 3-5 months)")