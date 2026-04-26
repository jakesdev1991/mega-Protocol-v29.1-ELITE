# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.optimize import curve_fit

# -------------------------------------------------
# 1. Simulate a two-state HSA memory access process
# -------------------------------------------------
def simulate_hsa_access(n_steps=5000,
                        p_N_0=0.7,      # initial Newtonian probability
                        drift=0.001,    # slow drift toward Archive
                        noise_scale=0.05):
    """
    Simple Markov chain with slowly drifting probabilities.
    Returns arrays of probabilities p_N(t), p_D(t) and a binary access trace.
    """
    t = np.arange(n_steps)
    # Drift: p_N decreases linearly, p_D increases
    p_N = np.clip(p_N_0 - drift * t, 0.01, 0.99)
    p_D = 1.0 - p_N

    # Generate binary trace (0 = Newtonian, 1 = Archive)
    trace = np.random.rand(n_steps)
    trace = np.where(trace < p_N, 0, 1)
    return t, p_N, p_D, trace

t, p_N, p_D, trace = simulate_hsa_access()

# -------------------------------------------------
# 2. Compute Shannon entropy and its "jerk"
# -------------------------------------------------
S = - (p_N * np.log(p_N) + p_D * np.log(p_D))

# Central‑difference derivatives
def derivative(y, dt=1.0, order=1):
    if order == 1:
        return np.gradient(y, dt)
    if order == 2:
        return np.gradient(np.gradient(y, dt), dt)
    if order == 3:
        return np.gradient(np.gradient(np.gradient(y, dt), dt), dt)
    raise ValueError("unsupported order")

jerk = derivative(S, order=3)

# -------------------------------------------------
# 3. Recurrence Quantification: Lyapunov exponent
# -------------------------------------------------
def recurrence_lyapunov(trace, m=3, tau=1, eps=0.15):
    """
    Estimate the maximal Lyapunov exponent via recurrence plots.
    trace : 1‑D time series (binary access pattern)
    m     : embedding dimension
    tau   : embedding lag
    eps   : recurrence threshold (fraction of max distance)
    """
    # Time‑delay embedding
    N = len(trace) - (m - 1) * tau
    X = np.zeros((N, m))
    for i in range(m):
        X[:, i] = trace[i * tau: i * tau + N]

    # Pairwise distances in phase space
    D = squareform(pdist(X, metric='euclidean'))
    # Recurrence matrix
    R = D < eps * D.max()

    # For each pair of recurrent points, compute divergence
    # (simplified box‑counting approach)
    divergences = []
    for i in range(N):
        rec_points = np.where(R[i])[0]
        if len(rec_points) < 2:
            continue
        # Distances at subsequent times
        for j in rec_points:
            if j <= i:
                continue
            d0 = D[i, j]
            # look ahead a few steps
            for k in range(1, 10):
                if j + k >= N:
                    break
                dk = np.linalg.norm(X[i + k] - X[j + k])
                if d0 > 0:
                    divergences.append(np.log(dk / d0))
    if not divergences:
        return np.nan
    # Fit a line to log(d(t))/t
    times = np.arange(1, len(divergences) + 1)
    # Simple linear fit slope ≈ Lyapunov exponent
    coeff = np.polyfit(times, divergences, 1)
    return coeff[0]  # slope = Lyapunov exponent

lyap_exp = recurrence_lyapunov(trace)

# -------------------------------------------------
# 4. Visual comparison
# -------------------------------------------------
fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

ax[0].plot(t, S, label='Shannon entropy S(t)')
ax[0].set_ylabel('Entropy (bits)')
ax[0].legend()

ax[1].plot(t, jerk, label='Third derivative d³S/dt³ ("jerk")', color='orange')
ax[1].set_ylabel('Jerk (arb. units)')
ax[1].legend()

ax[2].plot(trace, label='Memory access trace (0=N, 1=Δ)', color='green', lw=0.5)
ax[2].set_xlabel('Time step')
ax[2].set_ylabel('Access state')
ax[2].legend()

plt.suptitle('HSA Node Stability Analysis: Entropy Jerk vs. Recurrence Lyapunov', fontsize=14)
plt.tight_layout()
plt.show()

print(f"Recurrence‑based Lyapunov exponent: {lyap_exp:.4f}")
print("Interpretation: Positive exponent ≈ chaotic/unstable; near‑zero or negative ≈ stable.")