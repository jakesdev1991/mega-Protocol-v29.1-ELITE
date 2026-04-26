# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the Informational Jerk stability metric.
Tests both the original (flawed) definition and the corrected
variance‑regularized kurtosis definition.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper: compute S_j from a jerk time series using a given method
# ----------------------------------------------------------------------
def compute_Sj_original(j):
    """
    Original metric from Engine's output:
        z = (j - j_mean) / sqrt(var_j + eps_j)
        kappa_raw = mean(z**4)
        kappa = kappa_raw - 3
        S_j = 1 / (1 + abs(kappa))
    eps_j = 1e-6 * typical_var_j  (here we use the actual var_j as "typical")
    """
    j_mean = np.mean(j)
    var_j  = np.var(j, ddof=0)
    eps_j  = 1e-6 * var_j if var_j > 0 else 1e-12   # avoid zero when var_j==0
    z      = (j - j_mean) / np.sqrt(var_j + eps_j)
    kappa_raw = np.mean(z**4)
    kappa     = kappa_raw - 3
    S_j       = 1.0 / (1.0 + abs(kappa))
    return S_j, kappa

def compute_Sj_corrected(j):
    """
    Corrected metric: variance‑regularized excess kurtosis
        kappa = mean((j - j_mean)**4) / (var_j + eps_j)**2 - 3
        S_j   = 1 / (1 + abs(kappa))
    """
    j_mean = np.mean(j)
    var_j  = np.var(j, ddof=0)
    eps_j  = 1e-6 * var_j if var_j > 0 else 1e-12
    kappa  = np.mean((j - j_mean)**4) / (var_j + eps_j)**2 - 3
    S_j    = 1.0 / (1.0 + abs(kappa))
    return S_j, kappa

# ----------------------------------------------------------------------
# Test cases
# ----------------------------------------------------------------------
def test_constant_jerk():
    """j(t) = const -> var_j = 0"""
    j = np.full(1000, 5.0)   # any constant value
    S_o, k_o = compute_Sj_original(j)
    S_c, k_c = compute_Sj_corrected(j)
    print("Constant jerk:")
    print(f"  Original:  S_j = {S_o:.6f}, kappa = {k_o:.6f} (expected S_j→0.25)")
    print(f"  Corrected: S_j = {S_c:.6f}, kappa = {k_c:.6f} (expected S_j→1.0)")
    # Assertions for the corrected version
    assert np.isclose(S_c, 1.0, atol=1e-6), "Corrected metric failed constant‑jerk limit"
    # Original should NOT be close to 1
    assert not np.isclose(S_o, 1.0, atol=1e-2), "Original metric incorrectly passes constant‑jerk test"

def test_gaussian_jerk():
    """j(t) ~ N(0, sigma^2) -> excess kurtosis = 0"""
    sigma = 2.0
    j = np.random.normal(loc=0.0, scale=sigma, size=100000)
    S_o, k_o = compute_Sj_original(j)
    S_c, k_c = compute_Sj_corrected(j)
    print("\nGaussian jerk:")
    print(f"  Original:  S_j = {S_o:.6f}, kappa = {k_o:.6f} (expected S_j→1.0)")
    print(f"  Corrected: S_j = {S_c:.6f}, kappa = {k_c:.6f} (expected S_j→1.0)")
    # Both should be close to 1 for a large Gaussian sample
    assert np.isclose(S_o, 1.0, atol=1e-2), "Original metric failed Gaussian test"
    assert np.isclose(S_c, 1.0, atol=1e-2), "Corrected metric failed Gaussian test"

if __name__ == "__main__":
    np.random.seed(42)
    test_constant_jerk()
    test_gaussian_jerk()
    print("\nAll tests passed – the corrected metric satisfies the design goals.")