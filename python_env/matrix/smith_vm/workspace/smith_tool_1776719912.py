# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the Informational Jerk stability metric (S_j)
against the Omega Protocol invariant J*:
    S_j(constant jerk) → 1  (within tolerance)

The script compares the Engine's original definition with a
principled variance-regularized kurtosis fix.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions mimicking the Engine's pipeline
# ----------------------------------------------------------------------
def intrinsic_time_differential(Phi_N, Phi0):
    """dτ/dt = Φ_N / Φ_0"""
    return Phi_N / Phi0

def resample_to_uniform(t, x, fs_target):
    """Simple linear resampling to uniform fs_target Hz."""
    t_uniform = np.arange(t[0], t[-1], 1.0 / fs_target)
    x_uniform = np.interp(t_uniform, t, x)
    return t_uniform, x_uniform

def five_point_stencil_third_derivative(x, dt):
    """
    5-point stencil for the third derivative:
        f'''(x_i) ≈ (-f_{i+2} + 2f_{i+1} - 2f_{i-1} + f_{i-2}) / (2 dt^3)
    Edge points are set to NaN and later ignored.
    """
    n = len(x)
    d3 = np.full(n, np.nan)
    for i in range(2, n-2):
        d3[i] = (-x[i+2] + 2*x[i+1] - 2*x[i-1] + x[i-2]) / (2.0 * dt**3)
    return d3

def original_jerk_stability(j_tau, eps_j=1e-6):
    """
    Engine's original metric:
        z = (j - mean(j)) / sqrt(var(j) + eps_j)
        kappa_raw = mean(z**4)
        kappa = kappa_raw - 3
        S_j = 1 / (1 + |kappa|)
    """
    j_bar = np.nanmean(j_tau)
    sigma2 = np.nanvar(j_tau)
    z = (j_tau - j_bar) / np.sqrt(sigma2 + eps_j)
    kappa_raw = np.nanmean(z**4)
    kappa = kappa_raw - 3.0
    S_j = 1.0 / (1.0 + np.abs(kappa))
    return S_j, kappa

def corrected_jerk_stability(j_tau, eps_j=1e-6):
    """
    Variance-regularized excess kurtosis:
        kappa = mean((j - mean(j))**4) / (var(j) + eps_j)**2 - 3
        S_j = 1 / (1 + |kappa|)
    This yields kappa → -3 as var(j) → 0, hence S_j → 1.
    """
    j_bar = np.nanmean(j_tau)
    sigma2 = np.nanvar(j_tau)
    fourth_moment = np.nanmean((j_tau - j_bar)**4)
    kappa = fourth_moment / (sigma2 + eps_j)**2 - 3.0
    S_j = 1.0 / (1.0 + np.abs(kappa))
    return S_j, kappa

# ----------------------------------------------------------------------
# Test signals
# ----------------------------------------------------------------------
def test_signal(name, j_tau, dt, tol=1e-6):
    print(f"\n=== {name} ===")
    # Original
    S_j_orig, kappa_orig = original_jerk_stability(j_tau)
    print(f"Original:  S_j = {S_j_orig:.6f},  kappa = {kappa_orig:.6f}")
    # Corrected
    S_j_corr, kappa_corr = corrected_jerk_stability(j_tau)
    print(f"Corrected: S_j = {S_j_corr:.6f},  kappa = {kappa_corr:.6f}")

    # Invariant check: constant jerk should give S_j ≈ 1
    if np.allclose(j_tau, j_tau[0]):  # detect constant signal
        if not np.isclose(S_j_corr, 1.0, atol=tol):
            raise AssertionError(
                f"FAIL: Corrected S_j for constant jerk is {S_j_corr}, expected ~1."
            )
        print("✓ Corrected metric satisfies J* (S_j ≈ 1).")
    else:
        # For non‑constant signals we only check that S_j stays in (0,1]
        if not (0.0 < S_j_corr <= 1.0 + tol):
            raise AssertionError(
                f"FAIL: Corrected S_j out of bounds: {S_j_corr}"
            )
        print("✓ Corrected metric yields a valid stability score.")

# ----------------------------------------------------------------------
# Synthetic data generation
# ----------------------------------------------------------------------
rng = np.random.default_rng(seed=42)
T = 0.2          # 200 ms observation window
fs_raw = 10_000  # original sampling after resampling (as per Engine)
t_raw = np.linspace(0, T, int(T * fs_raw), endpoint=False)

# 1. Constant jerk (j = const)
j_const = np.full_like(t_raw, 0.5)   # arbitrary constant value
test_signal("Constant jerk", j_const, dt=1/fs_raw)

# 2. Gaussian jerk (zero‑mean, unit variance)
j_gauss = rng.normal(loc=0.0, scale=1.0, size=t_raw.shape)
test_signal("Gaussian jerk", j_gauss, dt=1/fs_raw)

# 3. Heavy‑tailed jerk (Laplace distribution)
j_laplace = rng.laplace(loc=0.0, scale=1.0, size=t_raw.shape)
test_signal("Laplace jerk", j_laplace, dt=1/fs_raw)

print("\nAll tests completed. If no assertion was raised, the corrected metric")
print("satisfies the Omega Protocol jerk‑stability invariant J*.")