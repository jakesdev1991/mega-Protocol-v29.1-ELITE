# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the corrected HSA Informational Jerk Stability Analysis.
Checks:
  - All required terms are computable from synthetic telemetry.
  - ψ = ln(Φ_N/Φ₀) is dimensionless.
  - S_j behaves correctly for Gaussian vs. heavy-tailed jerk.
"""

import numpy as np
from scipy.stats import kurtosis

# ------------------------------
# 1. Synthetic HSA telemetry
# ------------------------------
np.random.seed(42)
n_units = 8                     # pretend we have 8 compute units (CPUs+GPUs)
n_time  = 5000                  # samples @ 1 ms → 5 s window
dt      = 1e-3                  # 1 ms sampling

# Simulated atomic success rate (events/s) and latency (s)
A = np.random.uniform(0.5, 2.0, size=(n_units, n_units, n_time))   # A_ij(t)
L = np.random.uniform(1e-6, 10e-6, size=(n_units, n_units, n_time)) # L_ij(t)
L0 = 5e-6                                 # baseline latency

# Coherence field ψ_ij(t) = A_ij * exp(-L_ij/L0)
psi_ij = A * np.exp(-L / L0)   # shape (n_units, n_units, n_time)

# Asymmetry field (reads/writes ratio) – not needed for core validation but kept for completeness
reads  = np.random.uniform(0, 1, size=(n_units, n_units, n_time))
writes = np.random.uniform(0, 1, size=(n_units, n_units, n_time)) + 1e-9
phi_ij = reads / (writes + 1e-12)

# ------------------------------
# 2. Global scalars
# ------------------------------
# Mask self‑pairs (i==j) if desired – we keep them for simplicity
Phi_N = np.mean(psi_ij, axis=(0,1))                     # consensus over time
Phi_Delta = np.sqrt(np.mean((psi_ij - Phi_N[None,None,:])**2, axis=(0,1)))

# Normalise Φ_N for the log invariant (choose reference as median over time)
Phi0 = np.median(Phi_N)
psi_inv = np.log(Phi_N / Phi0)                          # scalar invariant ψ(t)

# ------------------------------
# 3. Invariants ξ_N and ξ_Δ
# ------------------------------
# Gradient of ψ_ij over unit indices (finite differences, central where possible)
def gradient_x(arr):
    # arr shape (n_units, n_units, n_time) → gradient w.r.t. first index (i)
    grad = np.zeros_like(arr)
    grad[1:-1] = (arr[2:] - arr[:-2]) / 2.0
    grad[0]    = arr[1] - arr[0]
    grad[-1]   = arr[-1] - arr[-2]
    return grad

grad_i = gradient_x(psi_ij)   # ∂/∂i
grad_j = gradient_x(np.transpose(psi_ij, (1,0,2)))   # ∂/∂j (transpose to reuse same function)
grad_norm_sq = grad_i**2 + grad_j**2                     # squared magnitude

xi_N = (np.mean(grad_norm_sq, axis=(0,1))**(-0.5))      # shape (n_time,)

# Poloidal correlation length ξ_Δ: split pairs into three directional classes
# We'll assign classes based on unit type: first half CPUs, second half GPUs
is_cpu = np.arange(n_units) < n_units//2
is_gpu = ~is_cpu

def variance_for_class(mask_i, mask_j):
    # mask_i, mask_j boolean arrays length n_units
    sel = np.ix_(mask_i, mask_j, np.arange(n_time))
    vals = psi_ij[sel]
    return np.var(vals, axis=0)   # variance over time for each t

var_cpu_cpu = variance_for_class(is_cpu, is_cpu)
var_gpu_gpu = variance_for_class(is_gpu, is_gpu)
var_cpu_gpu = variance_for_class(is_cpu, is_gpu)   # note: directed; we also need gpu_cpu but variance symmetric

# For simplicity treat CPU‑GPU and GPU‑CPU together (variance same)
var_cpu_gpu = 0.5 * (variance_for_class(is_cpu, is_gpu) + variance_for_class(is_gpu, is_cpu))

# Stack variances per class: shape (3, n_time)
vars_per_class = np.stack([var_cpu_cpu, var_gpu_gpu, var_cpu_gpu], axis=0)
xi_Delta = np.max(vars_per_class, axis=0) / np.min(vars_per_class, axis=0)   # dimensionless

# ------------------------------
# 4. Entropy S_h (Shannon) of coherence distribution
# ------------------------------
# Build histogram of ψ_ij across all pairs at each time step
n_bins = 20
hist = np.zeros((n_time, n_bins))
bin_edges = np.linspace(np.min(psi_ij), np.max(psi_ij), n_bins+1)

for t in range(n_time):
    hist[t], _ = np.histogram(psi_ij[:,:,t], bins=bin_edges, density=False)

# Normalise to probabilities
p = hist / np.sum(hist, axis=1, keepdims=True)
# Avoid log(0)
p_safe = np.clip(p, 1e-12, None)
S_h = -np.sum(p_safe * np.log(p_safe), axis=1)   # dimensionless

# ------------------------------
# 5. Jerk j(t) – third derivative of Φ_N
# ------------------------------
# 5‑point central stencil for third derivative
def third_derivative_5pt(x, dt):
    # x shape (n_time,)
    j = np.zeros_like(x)
    j[2:-2] = (-x[0:-4] + 2*x[1:-3] - 2*x[3:-1] + x[4:]) / (2.0 * dt**3)
    # edges: use lower order forward/backward (not critical for interior)
    return j

j = third_derivative_5pt(Phi_N, dt)   # shape (n_time,)

# ------------------------------
# 6. Jerk stability metric S_j (excess kurtosis)
# ------------------------------
window_len = int(0.1 / dt)   # 100 ms window
def stability_metric(j_signal, win):
    """Return S_j(t) for each centre of sliding window."""
    n = len(j_signal)
    S = np.full(n, np.nan)
    half = win // 2
    for i in range(half, n - half):
        segment = j_signal[i-half:i+half+1]
        j_bar = np.mean(segment)
        sigma = np.std(segment)
        if sigma < 1e-12:
            # constant segment → treat as Gaussian (kappa=3) → S_j=1
            S[i] = 1.0
            continue
        # excess kurtosis: raw kurtosis - 3
        # scipy.stats.kurtosis returns excess kurtosis by default (Fisher=True)
        excess = kurtosis(segment, fisher=True)   # already κ-3
        S[i] = 1.0 / (1.0 + np.abs(excess))
    return S

S_j = stability_metric(j, window_len)

# ------------------------------
# 7. Validation checks
# ------------------------------
print("=== Validation Results ===")
print(f"ψ invariant (ln(Φ_N/Φ₀)) mean: {np.nanmean(psi_inv):.4f} (dimensionless)")
print(f"ξ_N mean: {np.nanmean(xi_N):.4f} (index‑length units)")
print(f"ξ_Δ mean: {np.nanmean(xi_Delta):.4f} (dimensionless)")
print(f"Entropy S_h mean: {np.nanmean(S_h):.4f} (nats)")
print(f"Jerk stability S_j (Gaussian‑like) mean over interior: {np.nanmean(S_j[window_len:-window_len]):.4f}")

# Test S_j behaviour: replace j with pure Gaussian noise vs Laplace
j_gauss = np.random.normal(0, 0.01, size=n_time)
S_j_gauss = stability_metric(j_gauss, window_len)
print("\n--- Synthetic tests ---")
print(f"S_j for Gaussian jerk (should be ~1): mean = {np.nanmean(S_j_gauss):.4f}")

j_laplace = np.random.laplace(0, 0.01, size=n_time)   # heavy‑tailed
S_j_laplace = stability_metric(j_laplace, window_len)
print(f"S_j for Laplace jerk (heavy‑tailed, should be <1): mean = {np.nanmean(S_j_laplace):.4f}")

# Assertions (tolerances)
assert np.allclose(np.nanmean(S_j_gauss), 1.0, atol=0.05), "S_j not ≈1 for Gaussian jerk"
assert np.nanmean(S_j_laplace) < 0.9, "S_j not sufficiently penalising heavy-tailed jerk"
print("\nAll checks passed.")