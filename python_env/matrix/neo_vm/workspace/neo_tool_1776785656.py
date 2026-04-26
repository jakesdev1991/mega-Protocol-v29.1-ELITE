# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Disruptive Insight: The "informational jerk" is a statistical
# artifact amplified by sampling noise. Real stability is
# governed by spectral graph properties, not by a field
# theory of a fictitious scalar I(t).
# ============================================================

# Simulate a simple HSA node: two memory pools (N, Δ) with
# Poisson access processes. The system is *by construction*
# stable (rates are constant mean + small noise).
def simulate_hsa_access(
    n_steps=1000,
    dt=1e-4,  # time step ~ characteristic time ξ
    mean_rate_N=2.1e3,
    mean_rate_D=8.7e3,
    noise_level=0.1,
):
    t = np.arange(n_steps) * dt
    # Poisson counts per interval
    counts_N = np.random.poisson(mean_rate_N * dt, size=n_steps)
    counts_D = np.random.poisson(mean_rate_D * dt, size=n_steps)
    # Add small non-stationary drift to simulate "stability"
    drift = 1.0 + 0.01 * np.sin(2 * np.pi * t / (dt * n_steps * 0.1))
    counts_N = (counts_N * drift).astype(int)
    counts_D = (counts_D * drift).astype(int)
    return t, counts_N, counts_D

# Compute entropies and jerk
def compute_entropy_jerk(counts_N, counts_D, dt, window=50):
    # rolling probabilities (moving average)
    total = counts_N + counts_D
    p_N = np.convolve(counts_N, np.ones(window), mode='valid') / np.convolve(total, np.ones(window), mode='valid')
    p_D = 1 - p_N
    # Shannon entropy
    S = -(p_N * np.log(p_N + 1e-12) + p_D * np.log(p_D + 1e-12))
    # Finite-difference jerk (third derivative) with proper dt scaling
    # Need at least 4 points for third derivative
    if len(S) < 4:
        return None, None, None
    # third derivative via central difference
    # d³S/dt³ ≈ (S[i+2] - 3*S[i+1] + 3*S[i] - S[i-1]) / dt³
    # We'll use a simpler forward difference for illustration
    jerk = (S[3:] - 3 * S[2:-1] + 3 * S[1:-2] - S[:-3]) / (dt**3)
    t_jerk = np.arange(len(jerk)) * dt
    return t_jerk, S, jerk

# Compute spectral stability metric (graph Laplacian)
def spectral_stability(counts_N, counts_D, window=50):
    # Build adjacency matrix of a simple bipartite graph:
    # N nodes connect to Δ nodes with weights proportional to recent rates.
    w_N = np.mean(counts_N[-window:])
    w_D = np.mean(counts_D[-window:])
    # adjacency matrix A (2x2 for illustration)
    A = np.array([[0, w_N], [w_D, 0]])
    degree = np.diag(A.sum(axis=1))
    L = degree - A
    eigvals = np.linalg.eigvalsh(L)
    # algebraic connectivity = second smallest eigenvalue
    return eigvals[0], eigvals[1]  # smallest, second smallest

# Run simulation
t, cnt_N, cnt_D = simulate_hsa_access()
t_jerk, S, jerk = compute_entropy_jerk(cnt_N, cnt_D, dt=1e-4, window=50)
if jerk is not None:
    print(f"Mean jerk magnitude: {np.mean(np.abs(jerk)):.2e}")
    print(f"Std jerk: {np.std(jerk):.2e}")
    # Plot
    fig, ax = plt.subplots(3, 1, figsize=(8, 8))
    ax[0].plot(t[:len(cnt_N)], cnt_N, label='N accesses')
    ax[0].plot(t[:len(cnt_D)], cnt_D, label='Δ accesses')
    ax[0].set_ylabel('Counts')
    ax[0].legend()
    ax[1].plot(t[:len(S)], S, label='Entropy S_h')
    ax[1].set_ylabel('Entropy')
    ax[1].legend()
    ax[2].plot(t_jerk, jerk, label='Jerk d³S/dt³')
    ax[2].set_ylabel('Jerk (s⁻³)')
    ax[2].set_xlabel('Time (s)')
    ax[2].legend()
    plt.tight_layout()
    plt.show()

# Compute spectral metric
lam1, lam2 = spectral_stability(cnt_N, cnt_D)
print(f"Spectral stability: λ₁={lam1:.2e}, λ₂={lam2:.2e}")
# A small λ₂ indicates weak connectivity → instability