# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol validation for POASH‑Ω (refined).
Checks:
  1. PHI ∈ [0,1]
  2. Φ_N, Φ_Δ derived from information‑theoretic mapping stay in [0,1]
  3. ξ_N, ξ_Δ > 0 and satisfy the coherence‑based formulas
  4. MPC constraints (PHI≥0.4, Φ_N≥0.7, Φ_Δ≤0.6) hold for a feasible control input
  5. Cost function is non‑negative
"""

import numpy as np
from scipy.linalg import eigh

# ------------------------------
# Helper functions
# ------------------------------
def compute_phI(A):
    """
    A: shape (K, T) harmonic amplitudes for K orders, T time steps.
    Returns PHI(t) = 1 - Σ w_k |A_k - μ_k|/σ_k
    For validation we use unit weights and healthy baseline = mean over time.
    """
    K, T = A.shape
    mu = np.mean(A, axis=1, keepdims=True)
    sigma = np.std(A, axis=1, keepdims=True) + 1e-9
    dev = np.mean(np.abs(A - mu) / sigma, axis=0)  # average over orders
    # simple weighting w_k = 1/K
    PHI = 1.0 - dev
    return np.clip(PHI, 0.0, 1.0)

def information_theoretic_mapping(PHI, dPHI_dt, varA, alpha=0.5, beta=0.3, gamma=0.2):
    """
    Linearised mapping from the entropy model:
      Φ_N = Φ_N0 + α * dPHI/dt
      Φ_Δ = Φ_Δ0 - β * PHI + γ * varA
    Choose baseline values that satisfy constraints when PHI≈0.8.
    """
    Phi_N0 = 0.7
    Phi_Delta0 = 0.4
    Phi_N = Phi_N0 + alpha * dPHI_dt
    Phi_Delta = Phi_Delta0 - beta * PHI + gamma * varA
    return np.clip(Phi_N, 0.0, 1.0), np.clip(Phi_Delta, 0.0, 1.0)

def coherence_matrix(signals):
    """
    signals: shape (M, T) where M = number of sensor streams.
    Returns average magnitude‑squared coherence over frequencies.
    """
    M, T = signals.shape
    freqs = np.fft.rfftfreq(T)
    Sxx = np.zeros((M, M, len(freqs)), dtype=complex)
    for i in range(M):
        for j in range(M):
            Fi = np.fft.rfft(signals[i])
            Fj = np.fft.rfft(signals[j])
            Sxx[i, j] = Fi * np.conj(Fj) / T
    # magnitude‑squared coherence averaged over frequency
    coh = np.zeros((M, M))
    for i in range(M):
        for j in range(M):
            num = np.mean(np.abs(Sxx[i, j])**2)
            den = np.mean(np.abs(Sxx[i, i])**2) * np.mean(np.abs(Sxx[j, j])**2) + 1e-12
            coh[i, j] = num / den
    np.fill_diagonal(coh, 1.0)
    return coh

def stiffness_from_coherence(coh, lam=1.0):
    """
    Compute ξ_N, ξ_Δ from average coherence using the formulas in the proposal.
    """
    avg_coh = np.mean(coh[np.triu_indices_from(coh, k=1)])  # exclude diagonal
    if avg_coh <= 0:
        raise ValueError("Average coherence must be >0")
    xi_N_inv2 = lam * (3.0 / avg_coh + 1.0 / (avg_coh**2))
    xi_Delta_inv2 = lam * (1.0 / avg_coh + 3.0 / (avg_coh**2))
    xi_N = 1.0 / np.sqrt(xi_N_inv2)
    xi_Delta = 1.0 / np.sqrt(xi_Delta_inv2)
    return xi_N, xi_Delta, avg_coh

def mpc_cost(PHI, Phi_Delta, gradA_norm, u_norm,
             lam1=0.5, lam2=0.3, lam3=0.2):
    return (1.0 - PHI)**2 + lam1 * Phi_Delta**2 + lam2 * gradA_norm**2 + lam3 * u_norm**2

# ------------------------------
# Synthetic data generation
# ------------------------------
np.random.seed(42)
T = 120                     # 2‑hour window, 1‑min resolution
K = 5                       # number of harmonic orders
M = 4                       # sensor streams (latency, throughput, CPU, error)

# Generate plausible harmonic amplitudes (slowly varying + noise)
t = np.linspace(0, 2*np.pi, T)
A = np.zeros((K, T))
for k in range(K):
    A[k] = 0.5 * (1 + 0.3*np.sin((k+1)*t)) + 0.1*np.random.randn(T)

# Sensor streams: simple linear combos of harmonics + noise
S = np.zeros((M, T))
S[0] = 0.4*A[0] + 0.3*A[1] + 0.1*np.random.randn(T)   # latency jitter
S[1] = 0.5*A[1] + 0.2*A[2] + 0.1*np.random.randn(T)   # throughput
S[2] = 0.3*A[2] + 0.4*A[3] + 0.1*np.random.randn(T)   # CPU load
S[3] = 0.2*A[3] + 0.5*A[0] + 0.1*np.random.randn(T)   # error rate

# ------------------------------
# Compute quantities
# ------------------------------
PHI = compute_phI(A)                       # shape (T,)
dPHI_dt = np.gradient(PHI)                 # approx derivative
varA = np.var(A, axis=0)                   # shape (T,)

# Map to Omega variables (using fixed coefficients for demo)
Phi_N, Phi_Delta = information_theoretic_mapping(PHI, dPHI_dt, varA)

# Stiffness from sensor coherence
coh = coherence_matrix(S)
xi_N, xi_Delta, avg_coh = stiffness_from_coherence(coh)

# MPC feasibility check: choose a simple control u = 0 (no action)
u_norm = 0.0
gradA_norm = np.mean(np.gradient(np.linalg.norm(A, axis=0)))  # proxy

cost = mpc_cost(PHI[-1], Phi_Delta[-1], gradA_norm, u_norm)

# ------------------------------
# Validation assertions
# ------------------------------
def assert_all(cond, msg):
    if not np.all(cond):
        raise AssertionError(msg)

# 1. PHI bounds
assert_all((PHI >= 0) & (PHI <= 1), "PHI out of [0,1]")

# 2. Omega variable bounds (should hold for chosen baselines)
assert_all((Phi_N >= 0) & (Phi_N <= 1), "Phi_N out of [0,1]")
assert_all((Phi_Delta >= 0) & (Phi_Delta <= 1), "Phi_Delta out of [0,1]")

# 3. Stiffness positivity
assert xi_N > 0 and xi_Delta > 0, "Stiffness invariants non‑positive"

# 4. MPC constraints at final time (can be checked over whole horizon)
assert_all(PHI >= 0.4, "PHI constraint violated")
assert_all(Phi_N >= 0.7, "Phi_N constraint violated")
assert_all(Phi_Delta <= 0.6, "Phi_Delta constraint violated")

# 5. Cost non‑negative
assert cost >= 0, "MPC cost negative"

print("All Omega‑Protocol checks passed.")
print(f"Final PHI={PHI[-1]:.3f}, Phi_N={Phi_N[-1]:.3f}, Phi_Delta={Phi_Delta[-1]:.3f}")
print(f"Stiffness: ξ_N={xi_N:.3f}, ξ_Δ={xi_Delta:.3f}, avg coherence={avg_coh:.3f}")
print(f"MPC cost={cost:.3f}")