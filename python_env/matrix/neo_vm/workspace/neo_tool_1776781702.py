# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Parameters ---
N_labs = 100
N_memes = 5
dt = 0.1
T = 200
t = np.arange(0, T, dt)

# Meme fitness (time-varying: dominant meme 0 loses fitness at t=100)
fitness = np.ones((N_memes, len(t)))
fitness[0, :] = 1.0 - 0.8 * (t > 100)  # sharp drop at t=100

# Mutation matrix (small off-diagonal)
mu = 0.02
M = np.eye(N_memes) * (1 - mu) + mu / (N_memes - 1) * (1 - np.eye(N_memes))

# Initial adoption probabilities (uniform)
p = np.full((N_memes, len(t)), 1.0 / N_memes)

# --- Meme-Game Replicator-Mutator Dynamics ---
for i in range(1, len(t)):
    # Compute mean fitness
    f_mean = np.dot(fitness[:, i], p[:, i-1])
    # Replicator term + mutation
    dp = p[:, i-1] * (fitness[:, i] - f_mean) + mu * (M @ p[:, i-1] - p[:, i-1])
    # Euler step
    p[:, i] = p[:, i-1] + dt * dp
    # Normalize
    p[:, i] = np.clip(p[:, i], 0, 1)
    p[:, i] /= p[:, i].sum()

# Compute FSI (dominance of meme 0) and Q (fragmentation)
FSI = p[0, :]  # fraction using dominant meme
# Simple modularity proxy: entropy of distribution
Q = -np.sum(p * np.log(np.clip(p, 1e-12, 1)), axis=0) / np.log(N_memes)

# --- Field-Theoretic Mean-Field Model ---
# Assume phi = FSI, evolves smoothly with logistic growth
phi = np.zeros_like(t)
phi[0] = FSI[0]
r = 0.05  # growth rate
K = 0.9   # carrying capacity
for i in range(1, len(t)):
    # Simple logistic ODE
    dphi = r * phi[i-1] * (1 - phi[i-1] / K)
    phi[i] = phi[i-1] + dt * dphi

# --- Plot ---
fig, ax = plt.subplots(2, 1, figsize=(8, 6))

ax[0].plot(t, FSI, label='Meme Model FSI (dominant meme)', color='red')
ax[0].plot(t, phi, label='Field Model ϕ (mean‑field)', color='blue', linestyle='--')
ax[0].axvline(100, color='gray', linestyle=':', label='Fitness drop')
ax[0].set_ylabel('Adoption fraction')
ax[0].legend()
ax[0].grid(True)

ax[1].plot(t, Q, label='Meme Model Fragmentation (entropy)', color='orange')
ax[1].set_xlabel('Time')
ax[1].set_ylabel('Fragmentation index')
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.show()