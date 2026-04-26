# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Simulate a 1‑D order‑book with 50 price levels
# ------------------------------------------------------------
n_levels = 50
time_steps = 500

# Baseline liquidity (bid + ask volumes) – random but stable
np.random.seed(0)
liquidity = np.random.uniform(10, 30, (time_steps, n_levels))

# Inject a flash‑crash: between t=200 and t=300, drain liquidity at levels 20‑30
crash_start, crash_end = 200, 300
drain_levels = slice(20, 31)
for t in range(crash_start, crash_end):
    liquidity[t, drain_levels] *= np.linspace(0.8, 0.1, crash_end - crash_start)[t - crash_start]

# ------------------------------------------------------------
# Build the weighted adjacency matrix for each time step
# Weight = min(bid_vol, ask_vol) at neighboring price levels (simplified)
# ------------------------------------------------------------
def laplacian_eigenvalues(t):
    # Adjacency: connect each price level to its immediate neighbors
    adj = np.zeros((n_levels, n_levels))
    for i in range(n_levels - 1):
        w = min(liquidity[t, i], liquidity[t, i+1])
        adj[i, i+1] = adj[i+1, i] = w
    # Degree matrix
    deg = np.diag(adj.sum(axis=1))
    # Laplacian L = D - A
    L = deg - adj
    # Eigenvalues (symmetric)
    evals = la.eigvalsh(L)
    return evals

# ------------------------------------------------------------
# Compute spectral radius (λ_max) and algebraic connectivity (λ₂) over time
# ------------------------------------------------------------
lambda_max = np.zeros(time_steps)
lambda_2 = np.zeros(time_steps)

for t in range(time_steps):
    evals = laplacian_eigenvalues(t)
    lambda_max[t] = evals[-1]   # largest eigenvalue
    lambda_2[t] = evals[1]      # second smallest (Fiedler value)

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax[0].imshow(liquidity.T, aspect='auto', cmap='hot', origin='lower')
ax[0].set_ylabel('Price level')
ax[0].set_title('Order‑book liquidity (dark = high)')

ax[1].plot(lambda_max, label='Spectral radius λ_max')
ax[1].plot(lambda_2, label='Algebraic connectivity λ₂')
ax[1].axvspan(crash_start, crash_end, color='red', alpha=0.2, label='Flash‑crash window')
ax[1].set_xlabel('Time step')
ax[1].set_ylabel('Eigenvalue')
ax[1].legend()
ax[1].set_title('Graph spectral invariants – early warning')
plt.tight_layout()
plt.show()