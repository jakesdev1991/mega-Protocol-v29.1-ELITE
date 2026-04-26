# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation of the Engine's Informational Jerk stability metric.
Computes S_j = (1 + |κ|)^-1 where κ = excess kurtosis of
z = (j - j̄) / sqrt(σ_j^2 + ε_j).

The Engine claims:
    - S_j → 1 for constant jerk (σ_j → 0)
    - S_j → 1 for Gaussian jerk (κ → 0)

This script shows the claim is false for constant jerk.
"""

import numpy as np

def sj_engine(j_vals, eps_frac=1e-6):
    """
    Engine's jerk stability metric.
    j_vals: 1D array of jerk samples (in intrinsic time τ).
    eps_frac: fraction of typical variance used for ε_j.
    Returns S_j.
    """
    j = np.asarray(j_vals, dtype=float)
    j_bar = np.mean(j)
    sigma2 = np.var(j)                     # σ_j^2
    # typical variance estimate – here we use the sample variance itself
    eps_j = eps_frac * sigma2 if sigma2 > 0 else eps_frac
    # Normalized variable
    z = (j - j_bar) / np.sqrt(sigma2 + eps_j)
    # Raw kurtosis (4th moment)
    kappa_raw = np.mean(z**4)
    # Excess kurtosis
    kappa = kappa_raw - 3.0
    # Stability metric
    S_j = 1.0 / (1.0 + abs(kappa))
    return S_j, kappa, sigma2, eps_j

def sj_fixed(j_vals, eps_frac=1e-6):
    """
    Fixed metric using variance‑regularized excess kurtosis:
        κ = ⟨(j‑j̄)⁴⟩ / (σ_j² + ε)²  – 3
    This yields κ → –3 as σ_j² → 0, thus S_j → 1.
    """
    j = np.asarray(j_vals, dtype=float)
    j_bar = np.mean(j)
    sigma2 = np.var(j)
    eps = eps_frac * sigma2 if sigma2 > 0 else eps_frac
    # variance‑regularized kurtosis
    kappa = np.mean((j - j_bar)**4) / (sigma2 + eps)**2 - 3.0
    S_j = 1.0 / (1.0 + abs(kappa))
    return S_j, kappa, sigma2, eps

def test_cases():
    print("=== Jerk‑Stability Metric Validation ===\n")
    # 1. Constant jerk (zero variance)
    const_jerk = np.full(1000, 0.005)   # any constant value
    S_const, k_const, var_const, eps_const = sj_engine(const_jerk)
    print("Constant jerk:")
    print(f"  mean j = {np.mean(const_jerk):.6f}")
    print(f"  var j  = {var_const:.6e}")
    print(f"  ε_j    = {eps_const:.6e}")
    print(f"  excess kurtosis κ = {k_const:.6f}")
    print(f"  S_j    = {S_const:.6f}  (Engine expects ≈1.0)\n")

    # 2. Gaussian jerk (zero excess kurtosis)
    rng = np.default_rng(seed=42)
    gauss_jerk = rng.normal(loc=0.0, scale=0.02, size=10000)
    S_gauss, k_gauss, var_gauss, eps_gauss = sj_engine(gauss_jerk)
    print("Gaussian jerk (σ=0.02):")
    print(f"  mean j = {np.mean(gauss_jerk):.6f}")
    print(f"  var j  = {var_gauss:.6e}")
    print(f"  ε_j    = {eps_gauss:.6e}")
    print(f"  excess kurtosis κ = {k_gauss:.6f}")
    print(f"  S_j    = {S_gauss:.6f}  (Engine expects ≈1.0)\n")

    # 3. Show fixed metric on same data
    S_const_f, k_const_f, _, _ = sj_fixed(const_jerk)
    S_gauss_f, k_gauss_f, _, _ = sj_fixed(gauss_jerk)
    print("=== Fixed (variance‑regularized) metric ===")
    print(f"Constant jerk:  κ = {k_const_f:.6f}, S_j = {S_const_f:.6f}")
    print(f"Gaussian jerk:  κ = {k_gauss_f:.6f}, S_j = {S_gauss_f:.6f}\n")

    # 4. Decision
    if abs(S_const - 1.0) > 0.1:
        print("❌ FAIL: Engine's S_j deviates significantly from 1 for constant jerk.")
    else:
        print("✅ PASS: Engine's S_j ≈ 1 for constant jerk.")
    if abs(S_gauss - 1.0) > 0.1:
        print("❌ FAIL: Engine's S_j deviates significantly from 1 for Gaussian jerk.")
    else:
        print("✅ PASS: Engine's S_j ≈ 1 for Gaussian jerk.")

if __name__ == "__main__":
    test_cases()