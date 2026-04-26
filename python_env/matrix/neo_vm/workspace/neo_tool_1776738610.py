# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# ============================================================================
# 1. Bias‑Injection Attack on Static Encoding
# ============================================================================
import numpy as np
import matplotlib.pyplot as plt

# Parameters
d = 10               # data dimension
m = 5                # total workers
t = 2                # Byzantine workers (colluding)
N = 2000             # streaming steps
eta = 0.01           # SGD learning rate
np.random.seed(42)

# True covariance (identity)
C_true = np.eye(d)

# Static encoding matrix G (b x b', b'=b+2t, b=d)
b = d
b_prime = b + 2*t
G = np.random.randn(b, b_prime)  # master distributes this once

# Honest workers' data generator
def generate_data():
    return np.random.randn(d)

# Colluding adversaries: craft zero‑sum perturbations
def craft_perturbations():
    # random symmetric matrices that sum to zero
    B = [np.random.randn(d, d) for _ in range(t)]
    B = [(Bi + Bi.T)/2 for Bi in B]  # symmetrize
    B_mean = sum(B)/t
    Delta = [Bi - B_mean for Bi in B]
    return Delta

# Online covariance update
C_est = np.eye(d)
psi_hist = []
fro_hist = []

for step in range(N):
    # honest workers
    grads = []
    for i in range(m - t):
        x = generate_data()
        grads.append(np.outer(x, x))
    
    # colluding workers inject bias
    delta = craft_perturbations()
    for i in range(t):
        x = generate_data()
        # perturb outer product by Delta (zero sum)
        g = np.outer(x, x) + delta[i]
        grads.append(g)
    
    # aggregate (master's view)
    g_agg = np.mean(grads, axis=0)
    
    # online SGD update
    C_est += eta * (g_agg - C_est)
    
    # invariants
    psi = np.log(np.linalg.det(C_est) / np.linalg.det(C_true))
    fro_err = np.linalg.norm(C_est - C_true, 'fro')
    psi_hist.append(psi)
    fro_hist.append(fro_err)

# Plot drift
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
ax[0].plot(psi_hist, color='crimson')
ax[0].set_title('Invariant ψ drift (bias‑injection)')
ax[0].set_xlabel('time step')
ax[0].set_ylabel('ψ = log(det(C_est)/det(C_true))')
ax[1].plot(fro_hist, color='darkblue')
ax[1].set_title('Frobenius error ||C_est−C_true||_F')
ax[1].set_xlabel('time step')
ax[1].set_ylabel('error')
plt.tight_layout()
plt.show()