# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

# ---------- CLEM‑Ω Model (as described) ----------
def compute_cle(R, S, E, M, weights):
    # Standardized features (z‑scores)
    R_std = (R - np.mean(R)) / (np.std(R) + 1e-9)
    S_std = (S - np.mean(S)) / (np.std(S) + 1e-9)
    E_std = (E - np.mean(E)) / (np.std(E) + 1e-9)
    M_std = (M - np.mean(M)) / (np.std(M) + 1e-9)
    # Linear combination (weights arbitrary for demo)
    alpha, beta, gamma, delta = 0.3, 0.3, 0.2, 0.2
    cle = alpha * np.mean(R_std) + beta * np.std(S_std) + gamma * np.mean(E_std) + delta * np.mean(M_std)
    return cle

def compute_xi_delta(variances, eps=1e-6):
    # Poloidal correlation length (risk of division by zero)
    max_var = np.max(variances)
    min_var = np.min(variances)
    return (max_var + eps) / (min_var + eps)

def compute_entropy(weights):
    total = np.sum(weights)
    if total == 0:
        return 0.0  # Guard (not present in original proposal)
    p = weights / total
    # Avoid log(0)
    p = np.clip(p, 1e-12, None)
    return -np.sum(p * np.log(p))

# ---------- Simulation ----------
np.random.seed(42)
n_creds = 100
# Initial credential states
R = np.random.exponential(scale=30, size=n_creds)   # rotation interval (days)
S = np.random.beta(2, 5, size=n_creds)           # strength score (0–1)
E = np.random.normal(loc=0, scale=5, size=n_creds) # expiration deviation (days)
M = np.random.poisson(lam=2, size=n_creds)         # mapping changes per month

# Operational stress (external)
external_stress = 0.1

# Controller parameters
cle_threshold = 0.5
rotation_impulse = 5.0  # days added when controller rotates

# Storage for time series
cle_history = []
xi_delta_history = []
entropy_history = []
coii_history = []

# Simple COII estimator (largest Lyapunov exponent via Rosenstein's algorithm)
def estimate_lyapunov(R_traj, S_traj, embed_dim=5, tau=1):
    # Concatenate trajectories for joint phase space
    joint = np.column_stack((R_traj, S_traj))
    # Naive approximation: average log divergence of nearest neighbors
    # For demo, return a positive value if divergence is evident
    if len(joint) < embed_dim + 2:
        return 0.0
    # Compute pairwise distances
    dists = np.linalg.norm(joint[:-1, None] - joint[None, :-1], axis=2)
    # Ignore self‑distances
    np.fill_diagonal(dists, np.inf)
    # Nearest neighbor indices
    nn = np.argmin(dists, axis=1)
    # Average divergence rate (simplified)
    divergence = np.mean(np.log(np.abs(np.diff(joint, axis=0)[nn, 0]) + 1e-9))
    return divergence

# ---------- Main Loop (simulating 60 days) ----------
for day in range(60):
    # Update credential states with external stress
    R += external_stress * np.random.normal(scale=0.5, size=n_creds)
    S = np.clip(S + external_stress * 0.01 * np.random.normal(scale=0.1, size=n_creds), 0, 1)
    E += external_stress * np.random.normal(scale=0.2, size=n_creds)
    M += np.random.poisson(lam=external_stress, size=n_creds)

    # Compute CLE
    weights = np.ones(n_creds)  # uniform weighting for demo
    cle = compute_cle(R, S, E, M, weights)
    cle_history.append(cle)

    # Compute ξ_Δ (poloidal correlation length)
    variances = np.array([np.var(R), np.var(S), np.var(E), np.var(M)])
    xi_delta = compute_xi_delta(variances)
    xi_delta_history.append(xi_delta)

    # Compute entropy
    # Use a risk‑weight vector that can become zero
    risk_weights = R * (1 - S) * np.clip(E, 0, None)
    entropy = compute_entropy(risk_weights)
    entropy_history.append(entropy)

    # COII (Lyapunov exponent) estimation from recent trajectory
    if day > 10:
        coii = estimate_lyapunov(R, S)
        coii_history.append(coii)
    else:
        coii_history.append(0.0)

    # CLEM‑Ω controller: if CLE > threshold, rotate credentials (add rotation impulse)
    if cle > cle_threshold:
        # Controller action: rotate a random subset of credentials
        n_rotate = int(0.1 * n_creds)
        rotate_idx = np.random.choice(n_creds, size=n_rotate, replace=False)
        R[rotate_idx] += rotation_impulse  # This increases variance of R!
        # After rotation, reset some strength scores (simulate policy enforcement)
        S[rotate_idx] = np.clip(S[rotate_idx] + 0.05, 0, 1)

# ---------- Show the singularity ----------
print("=== CLEM‑Ω Singularity Indicators ===")
print(f"Max ξ_Δ (poloidal correlation length): {max(xi_delta_history):.2e}")
print(f"Min risk‑weight sum (entropy denominator): {min(np.sum(R * (1 - S) * np.clip(E, 0, None)) for _ in range(60)):.2e}")
print(f"Average COII (Lyapunov exponent) after day 10: {np.mean(coii_history[10:]):.4f}")
print("If COII > 0, the observer‑system loop is chaotic (prediction impossible).")

# Show sample trajectory
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 8))
plt.subplot(2, 2, 1)
plt.plot(cle_history, label='CLE')
plt.axhline(cle_threshold, color='red', linestyle='--', label='Threshold')
plt.title("Credential‑Lifecycle Entropy")
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(xi_delta_history, label='ξ_Δ')
plt.title("Poloidal Correlation Length (risk of ∞)")
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(entropy_history, label='S_h^(CLE)')
plt.title("Credential‑Risk Entropy")
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(coii_history, label='COII')
plt.axhline(0, color='black', linewidth=0.5)
plt.title("Credential‑Observer Instability Index")
plt.legend()
plt.tight_layout()
plt.show()