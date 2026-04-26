# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation for AMM Homogeneity Monitor (AHM‑Ω)

This script checks the internal mathematical consistency of the quantities
introduced in the AHM‑Ω proposal:
    - AHI ∈ [0,1]
    - Shannon entropy ≥ 0
    - Φ_N, Φ_Δ remain within plausible bounds (we enforce [0,1] after scaling)
    - Ψ = ln(det Σ / det Σ0) behaves monotonically with correlation
    - MPC‑Ω hard constraints are satisfiable for a feasible parameter set

If any check fails, an AssertionError is raised with a descriptive message.
"""

import numpy as np
import scipy.stats as stats

# -------------------------- Helper Functions --------------------------

def compute_covariance(thetas):
    """Sample covariance matrix of parameter vectors."""
    return np.cov(thetas, rowvar=False, bias=False)  # unbiased estimator

def compute_ahi(cov, d):
    """AHI = (1 + (1/d) * Tr(cov))^{-1}"""
    tr = np.trace(cov)
    ahi = 1.0 / (1.0 + tr / d)
    return ahi

def shannon_entropy(samples, bins=20):
    """Discretize each dimension independently and compute joint entropy via histogram."""
    # Build a histogram over the flattened samples (simple approach)
    hist, _ = np.histogramdd(samples, bins=bins, density=True)
    p = hist.flatten()
    p = p[p > 0]  # remove zeros to avoid log(0)
    return -np.sum(p * np.log(p))

def phi_n_contribution(ahi, ahi_prev, eta1=0.3, eta2=0.1, alpha1=2.0, tau1=3):
    """Phi_N^{(amm)} = Phi_N0 + eta1*tanh(alpha1*AHI(t-tau1)) - eta2*AHI(t)^2"""
    # Assume baseline Phi_N0 = 0.5 (mid‑range)
    phi_n0 = 0.5
    term = eta1 * np.tanh(alpha1 * ahi_prev) - eta2 * ahi**2
    return phi_n0 + term

def phi_delta_contribution(ahi, ahi_prev, eta3=0.2, eta4=0.15, tau2=2):
    """Phi_Delta^{(amm)} = Phi_Delta0 + eta3*AHI(t-tau2) + eta4*|dAHI/dt|"""
    phi_delta0 = 0.3
    # Approximate derivative via finite difference (previous step)
    dadt = (ahi - ahi_prev) / 1.0  # assuming unit time step
    return phi_delta0 + eta3 * ahi_prev + eta4 * np.abs(dadt)

def compute_psi(cov, cov0):
    """Psi = ln(det(cov) / det(cov0))"""
    det_cov = np.linalg.det(cov)
    det_cov0 = np.linalg.det(cov0)
    # Guard against numerical zero
    if det_cov <= 0 or det_cov0 <= 0:
        raise ValueError("Determinant must be positive for log.")
    return np.log(det_cov / det_cov0)

# -------------------------- Synthetic Data Generation --------------------------

np.random.seed(42)
N_pools = 500          # number of AMM pools to simulate
dim = 3                # (a, b, kappa)

# Baseline healthy diversity: parameters spread around [1,1,0.01] with moderate variance
baseline_mean = np.array([1.0, 1.0, 0.01])
baseline_cov = np.diag([0.2**2, 0.2**2, 0.005**2])

# Current state: we will test three regimes
regimes = {
    "healthy": {"mean": baseline_mean, "cov": baseline_cov},
    "homogeneous": {"mean": baseline_mean, "cov": 0.01 * baseline_cov},  # low variance
    "heterogeneous": {"mean": baseline_mean, "cov": 5.0 * baseline_cov}  # high variance
}

# -------------------------- Validation Loop --------------------------

for regime_name, params in regimes.items():
    print(f"\n=== Regime: {regime_name} ===")
    thetas = np.random.multivariate_normal(params["mean"], params["cov"], size=N_pools)
    
    cov = compute_covariance(thetas)
    cov0 = compute_covariance(np.random.multivariate_normal(baseline_mean, baseline_cov, size=N_pools))
    
    ahi = compute_ahi(cov, dim)
    # For Phi_N we need a previous AHI; use the same value as a proxy (steady state)
    ahi_prev = ahi
    
    entropy = shannon_entropy(thetas, bins=15)
    
    phi_n = phi_n_contribution(ahi, ahi_prev)
    phi_delta = phi_delta_contribution(ahi, ahi_prev)
    
    psi = compute_psi(cov, cov0)
    
    # ----- Assertions (Omega invariants) -----
    # 1. AHI in [0,1]
    assert 0.0 <= ahi <= 1.0 + 1e-12, f"AHI out of bounds: {ahi}"
    # 2. Entropy non‑negative
    assert entropy >= -1e-12, f"Negative entropy: {entropy}"
    # 3. Phi_N and Phi_Delta should be in a reasonable normalized range.
    #    We enforce [0,1] after a simple linear rescaling for demonstration.
    phi_n_norm = (phi_n - 0.0) / (1.0 - 0.0)  # identity if already in [0,1]
    phi_d_norm = (phi_delta - 0.0) / (1.0 - 0.0)
    assert 0.0 - 1e-12 <= phi_n_norm <= 1.0 + 1e-12, f"Phi_N out of [0,1]: {phi_n}"
    assert 0.0 - 1e-12 <= phi_d_norm <= 1.0 + 1e-12, f"Phi_Delta out of [0,1]: {phi_delta}"
    # 4. Psi should decrease as covariance shrinks (more correlation)
    #    Compare healthy vs homogeneous vs heterogeneous:
    #    We'll store values and check monotonicity after the loop.
    
    print(f"AHI: {ahi:.4f}")
    print(f"Entropy: {entropy:.4f}")
    print(f"Phi_N^{(amm)}: {phi_n:.4f}")
    print(f"Phi_Delta^{(amm)}: {phi_delta:.4f}")
    print(f"Psi: {psi:.4f}")
    
    # ----- MPC‑Ω hard constraints (example thresholds) -----
    Psi_min = -3.0          # arbitrary but illustrative
    S_min   = 0.5           # minimal entropy to avoid freeze
    Phi_N_lb = 0.6
    Phi_Delta_ub = 0.7
    
    assert psi >= Psi_min, f"Psi ({psi}) below safety threshold ({Psi_min})"
    assert entropy >= S_min, f"Entropy ({entropy}) below safety threshold ({S_min})"
    assert phi_n >= Phi_N_lb, f"Phi_N ({phi_n}) below lower bound ({Phi_N_lb})"
    assert phi_delta <= Phi_Delta_ub, f"Phi_Delta ({phi_delta}) above upper bound ({Phi_Delta_ub})"
    
    print("All Omega invariants and MPC‑Ω constraints SATISFIED.")
    
# ----- Monotonicity check for Psi across regimes -----
print("\n=== Cross‑regime Psi monotonicity check ===")
psi_values = {}
for regime_name, params in regimes.items():
    thetas = np.random.multivariate_normal(params["mean"], params["cov"], size=N_pools)
    cov = compute_covariance(thetas)
    cov0 = compute_covariance(np.random.multivariate_normal(baseline_mean, baseline_cov, size=N_pools))
    psi_values[regime_name] = compute_psi(cov, cov0)

# Expected ordering: heterogeneous (high variance) → highest Psi,
# healthy → medium, homogeneous (low variance) → lowest (most negative)
order = ["heterogeneous", "healthy", "homogeneous"]
for i in range(len(order)-1):
    cur = psi_values[order[i]]
    nxt = psi_values[order[i+1]]
    assert cur >= nxt - 1e-9, f"Psi not monotonic: {order[i]} ({cur}) < {order[i+1]} ({nxt})"
print("Psi monotonicity across regimes holds.")

print("\n✅ All validation checks passed. The AHM‑Ω mathematics is internally consistent with the Omega Protocol invariants.")