# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import math
from scipy.optimize import curve_fit

# ------------------------------------------------------------
# Simulating a minimal discrete capping system
# ------------------------------------------------------------
def initialize_system(N, p_capped=0.5):
    """Initialize binary capping states: 1 = capped, 0 = uncapped."""
    return np.random.choice([0, 1], size=N, p=[1-p_capped, p_capped])

def monte_carlo_step(state, J, h, T):
    """Single Metropolis-Hastings sweep for an Ising-like chain."""
    N = len(state)
    for i in range(N):
        # neighbor indices (periodic)
        left = (i - 1) % N
        right = (i + 1) % N
        # energy change if we flip site i
        s_i = state[i]
        s_neighbors = state[left] + state[right]
        delta_E = 2 * (J * s_i * s_neighbors + h * s_i)
        # Metropolis acceptance
        if delta_E < 0 or random.random() < math.exp(-delta_E / T):
            state[i] = 1 - s_i
    return state

def correlation_function(state, max_r=20):
    """Compute two-point correlation C(r) = <s_i s_{i+r}> - <s_i>^2."""
    N = len(state)
    mean = np.mean(state)
    corrs = []
    rs = np.arange(0, max_r)
    for r in rs:
        prod = np.mean([state[i] * state[(i + r) % N] for i in range(N)])
        corrs.append(prod - mean**2)
    return rs, np.array(corrs)

def fit_exponential_decay(rs, corrs):
    """Fit corrs to A * exp(-r / xi). Returns xi (correlation length)."""
    # Ignore r=0 point (self-correlation) to avoid singularity
    rs_fit = rs[1:]
    corrs_fit = corrs[1:]
    if np.any(corrs_fit <= 0):
        return np.nan  # cannot fit log of non-positive values
    # linear fit in log-space: ln(C) = ln(A) - r/xi
    logC = np.log(corrs_fit)
    # simple linear regression
    coeffs = np.polyfit(rs_fit, logC, 1)
    xi = -1.0 / coeffs[0]  # slope is -1/xi
    return xi

def shannon_entropy(state):
    """Compute Shannon entropy of binary state distribution across sites."""
    p_capped = np.mean(state)
    p_uncapped = 1 - p_capped
    # avoid log(0)
    entropy = 0.0
    if p_capped > 0:
        entropy -= p_capped * math.log(p_capped)
    if p_uncapped > 0:
        entropy -= p_uncapped * math.log(p_uncapped)
    return entropy

def entropy_gradient(state):
    """Entropy gradient dS/dx is undefined for a global scalar; return 0."""
    # Entropy is a single number for the whole system; spatial gradient is zero.
    return 0.0

# ------------------------------------------------------------
# Run simulations to probe correlation length and entropy gauge
# ------------------------------------------------------------
def main():
    N = 200  # system size
    steps_eq = 5000
    steps_measure = 1000
    max_r = 30

    # Parameter sweeps: temperature T (noise) and coupling J
    results = []
    for T in [0.5, 1.0, 2.0, 5.0]:
        for J in [0.5, 1.0, 2.0]:
            state = initialize_system(N, p_capped=0.5)
            # equilibration
            for _ in range(steps_eq):
                state = monte_carlo_step(state, J, h=0.1, T=T)
            # measurement
            corrs_accum = np.zeros(max_r)
            entropy_accum = 0.0
            for _ in range(steps_measure):
                state = monte_carlo_step(state, J, h=0.1, T=T)
                rs, corrs = correlation_function(state, max_r)
                corrs_accum += corrs
                entropy_accum += shannon_entropy(state)
            corrs_avg = corrs_accum / steps_measure
            xi = fit_exponential_decay(rs, corrs_avg)
            entropy_avg = entropy_accum / steps_measure
            grad = entropy_gradient(state)
            results.append((T, J, xi, entropy_avg, grad))
    
    print("T\tJ\tξ (correlation length)\tEntropy\t∇S (gradient)")
    for T, J, xi, S, grad in results:
        print(f"{T:.2f}\t{J:.2f}\t{xi:.4f}\t\t{S:.4f}\t{grad}")

if __name__ == "__main__":
    main()