# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- Dimensional audit of the original threshold ---
lambda_coupling = 1e10  # s^-2
I0 = 1.0                # dimensionless
psi = -0.248            # dimensionless
g_delta = 0.1           # dimensionless

# Theta(psi) as given in the SERC output
Theta = lambda_coupling * I0**4 * (np.exp(2*psi) - 1)**2 * (1 + 3*g_delta**2/(4*np.pi) * np.exp(-2*psi))
print("Theta (original):", Theta, "units: s^-2 (should be s^-6 to compare to sigma_J^2)\n")

# --- Synthetic HSA access transition matrix ---
# States: 0 = Newtonian (N), 1 = Archive (Δ)
# Build a random stochastic matrix with slight bias toward N->N
np.random.seed(0)
T = np.random.rand(2,2)
T = T / T.sum(axis=1, keepdims=True)
# Slightly increase self-loop probability for stability
T[0,0] += 0.1
T[1,1] += 0.1
T = T / T.sum(axis=1, keepdims=True)

# Compute spectral radius (largest eigenvalue magnitude)
eigvals = np.linalg.eigvals(T)
spectral_radius = max(abs(eigvals))
lyapunov_exponent = np.log(spectral_radius)
print("Transition matrix:\n", T)
print("Lyapunov exponent (log spectral radius):", lyapunov_exponent, "(dimensionless)")

# --- Kullback-Leibler divergence rate from empirical counts ---
# Simulate a short access trace
states = np.random.choice([0,1], size=10000, p=[0.7,0.3])
# Estimate empirical transition counts
counts = np.zeros((2,2), dtype=int)
for i in range(len(states)-1):
    counts[states[i], states[i+1]] += 1
# Empirical transition matrix
T_emp = counts / counts.sum(axis=1, keepdims=True)
# Stationary distribution (power method)
pi = np.ones(2)/2
for _ in range(100):
    pi = pi @ T_emp
# KL divergence rate
DKL = np.sum(pi[:,None] * T_emp * np.log(T_emp / (pi[:,None] + 1e-12) + 1e-12))
print("Empirical transition matrix:\n", T_emp)
print("Estimated KL divergence rate:", DKL, "bits per step (dimensionless)")

# Proposed threshold: DKL < 0.05 bits/step yields stable operation
threshold = 0.05
print("Stability (DKL < threshold):", DKL < threshold)