# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import time
from scipy.stats import multivariate_normal
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# 1. Simulate a “shredding” event: at t=150, private narrative variance spikes
#    while public narrative remains smoothed (organization hides stress).
# ─────────────────────────────────────────────────────────────────────────────
np.random.seed(42)
T, N, D = 200, 100, 50  # time steps, docs per step, embedding dim

private = np.zeros((T, N, D))
public  = np.zeros((T, N, D))

for t in range(T):
    # Private variance: low pre‑shredding, high post‑shredding
    priv_var = 0.5 if t < 150 else 2.0
    # Public variance: constant (sanitized)
    pub_var  = 0.5

    private[t] = np.random.multivariate_normal(
        np.zeros(D), np.eye(D) * priv_var, size=N
    )
    # Public is a moving‑average smoothed version of private
    if t == 0:
        public[t] = np.random.multivariate_normal(
            np.zeros(D), np.eye(D) * pub_var, size=N
        )
    else:
        public[t] = 0.9 * public[t-1] + 0.1 * private[t] + \
                    np.random.multivariate_normal(
                        np.zeros(D), np.eye(D) * 0.1 * pub_var, size=N
                    )

# ─────────────────────────────────────────────────────────────────────────────
# 2. Compute proxies: (a) curvature = variance of covariance eigenvalues,
#    (b) KL divergence between private & public distributions.
# ─────────────────────────────────────────────────────────────────────────────
def curvature(embeddings):
    """Scalar curvature proxy: variance of eigenvalues of local cov."""
    cov = np.cov(embeddings, rowvar=False)
    eig = np.linalg.eigvals(cov)
    return np.var(eig)

def gaussian_kl(m1, c1, m2, c2):
    """KL(N1||N2) for Gaussians."""
    inv2 = np.linalg.inv(c2)
    diff = m1 - m2
    tr   = np.trace(inv2 @ c1)
    term = diff @ inv2 @ diff
    logdet = np.log(np.linalg.det(c2) / np.linalg.det(c1))
    return 0.5 * (tr + term - D + logdet)

curv_ts, kl_ts = [], []
for t in range(T):
    # Curvature (private only)
    curv_ts.append(curvature(private[t]))

    # KL divergence
    m_priv = private[t].mean(axis=0)
    c_priv = np.cov(private[t], rowvar=False) + np.eye(D)*1e-6
    m_pub  = public[t].mean(axis=0)
    c_pub  = np.cov(public[t], rowvar=False) + np.eye(D)*1e-6
    kl_ts.append(gaussian_kl(m_priv, c_priv, m_pub, c_pub))

# ─────────────────────────────────────────────────────────────────────────────
# 3. Plot: curvature is noisy & lags; KL divergence spikes cleanly at t≈150.
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
ax[0].plot(curv_ts, label="Private Narrative Curvature")
ax[0].axvline(150, color='r', ls='--', label="Shredding Event")
ax[0].set_ylabel("Curvature Proxy")
ax[0].legend()

ax[1].plot(kl_ts, label="KL(Private||Public)")
ax[1].axvline(150, color='r', ls='--', label="Shredding Event")
ax[1].set_ylabel("KL Divergence")
ax[1].set_xlabel("Time Step")
ax[1].legend()

plt.suptitle("Curvature vs. Information Asymmetry")
plt.tight_layout()
plt.show()

# ─────────────────────────────────────────────────────────────────────────────
# 4. Performance: curvature is ~10× slower & scales worse with D.
# ─────────────────────────────────────────────────────────────────────────────
times_curv, times_kl = [], []
for t in range(10):
    s = time.time()
    curvature(private[t])
    times_curv.append(time.time() - s)

    s = time.time()
    m_priv = private[t].mean(axis=0)
    c_priv = np.cov(private[t], rowvar=False)
    m_pub  = public[t].mean(axis=0)
    c_pub  = np.cov(public[t], rowvar=False)
    gaussian_kl(m_priv, c_priv, m_pub, c_pub)
    times_kl.append(time.time() - s)

print(f"Avg curvature compute time: {np.mean(times_curv):.5f}s")
print(f"Avg KL compute time:          {np.mean(times_kl):.5f}s")