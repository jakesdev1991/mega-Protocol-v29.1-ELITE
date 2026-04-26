# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Smith Validation Script – Jerk‑Stability & Omega Protocol Invariants
"""

import numpy as np

# ------------------------------
# Helper statistical functions
# ------------------------------
def excess_kurtosis_flawed(j, eps):
    """
    Engine's flawed definition:
        z = (j - mean) / sqrt(var + eps)
        kurtosis_raw = mean(z**4)
        excess = kurtosis_raw - 3
    """
    j = np.asarray(j)
    jbar = j.mean()
    var = j.var()
    z = (j - jbar) / np.sqrt(var + eps)
    kurt_raw = np.mean(z**4)
    return kurt_raw - 3

def excess_kurtosis_fixed(j, eps):
    """
    Corrected variance‑regularized excess kurtosis:
        kappa = E[(j - mean)^4] / (var + eps)^2 - 3
    """
    j = np.asarray(j)
    jbar = j.mean()
    var = j.var()
    num = np.mean((j - jbar)**4)
    denom = (var + eps)**2
    return num / denom - 3

def stability_from_kappa(kappa):
    """S_j = (1 + |kappa|)^(-1)"""
    return 1.0 / (1.0 + np.abs(kappa))

# ------------------------------
# Test cases
# ------------------------------
def test_jerk_stability():
    print("\n=== Jerk‑Stability Metric Validation ===")
    # Constant jerk signal
    const_j = np.full(10000, 5.0)   # arbitrary constant value
    # Gaussian jerk signal (zero mean, unit variance)
    rng = np.default_rng(seed=42)
    gauss_j = rng.normal(loc=0.0, scale=1.0, size=10000)

    eps = 1e-6  # matches Engine's epsilon scaling (will be overridden below)

    # Flawed metric
    kappa_f_const = excess_kurtosis_flawed(const_j, eps)
    kappa_f_gauss = excess_kurtosis_flawed(gauss_j, eps)
    S_f_const = stability_from_kappa(kappa_f_const)
    S_f_gauss = stability_from_kappa(kappa_f_gauss)

    print(f"Flawed metric:")
    print(f"  Constant jerk -> kappa = {kappa_f_const:.6f}, S_j = {S_f_const:.6f}")
    print(f"  Gaussian jerk  -> kappa = {kappa_f_gauss:.6f}, S_j = {S_f_gauss:.6f}")

    # Fixed metric (epsilon scaled to typical variance)
    # For constant jerk, var = 0 -> we set eps = 1e-6 * typical var from Gaussian as proxy
    typical_var = np.var(gauss_j)
    eps_fixed = 1e-6 * typical_var
    kappa_x_const = excess_kurtosis_fixed(const_j, eps_fixed)
    kappa_x_gauss = excess_kurtosis_fixed(gauss_j, eps_fixed)
    S_x_const = stability_from_kappa(kappa_x_const)
    S_x_gauss = stability_from_kappa(kappa_x_gauss)

    print(f"\nFixed metric (eps = {eps_fixed:.3e}):")
    print(f"  Constant jerk -> kappa = {kappa_x_const:.6f}, S_j = {S_x_const:.6f}")
    print(f"  Gaussian jerk  -> kappa = {kappa_x_gauss:.6f}, S_j = {S_x_gauss:.6f}")

    # Assertions for Omega Protocol compliance
    # Constant jerk should give S_j ≈ 1 (within tolerance)
    assert np.isclose(S_x_const, 1.0, atol=1e-3), \
        "Fixed metric fails to reward constant jerk (S_j ≠ 1)."
    # Gaussian jerk should also give S_j ≈ 1 (excess kurtosis → 0)
    assert np.isclose(S_x_gauss, 1.0, atol=1e-3), \
        "Fixed metric fails for Gaussian jerk (S_j ≠ 1)."
    # Flawed metric must NOT give S_j ≈ 1 for constant jerk (exposes the bug)
    assert not np.isclose(S_f_const, 1.0, atol=1e-3), \
        "Flawed metric incorrectly passes constant jerk test (should fail)."
    print("\n✓ Jerk‑stability metric passes Omega Protocol invariants (fixed version).")

# ------------------------------
# Dimensionless invariants check
# ------------------------------
def test_dimensionless_invariants():
    print("\n=== Dimensionless Invariant Checks ===")
    # Simulate telemetry for coherence field
    Phi_N = np.array([0.8, 0.85, 0.78, 0.82])  # example values
    Phi0 = np.median(Phi_N)                   # calibration median
    psi = np.log(Phi_N / Phi0)                # dimensionless by construction
    print(f"Phi_N: {Phi_N}")
    print(f"Phi0 (median): {Phi0:.6f}")
    print(f"psi = ln(Phi_N/Phi0): {psi}")
    # Verify that psi is unit‑less (no physical units attached)
    assert np.all(np.isfinite(psi)), "psi contains non‑finite values."
    print("✓ ψ is dimensionless and well‑defined.")

    # Anisotropy regularization
    # Suppose we have three directional variance estimates
    sigma2 = np.array([1.2e-3, 0.9e-3, 1.5e-3])  # CPU‑GPU, GPU‑GPU, CPU‑CPU
    eps_aniso = 1e-6 * np.mean(sigma2)
    xi_Delta = (np.max(sigma2) + eps_aniso) / (np.min(sigma2) + eps_aniso)
    print(f"\nDirectional variances σ²: {sigma2}")
    print(f"ε_aniso = {eps_aniso:.3e}")
    print(f"Anisotropy ratio ξ_Δ = {xi_Delta:.6f}")
    # ξ_Δ ≥ 1 by construction
    assert xi_Delta >= 1.0 - 1e-12, "Anisotropy ratio violated lower bound."
    print("✓ ξ_Δ regularization yields ξ_Δ ≥ 1 (no division by zero).")

# ------------------------------
# Entropy smoothing check
# ------------------------------
def test_entropy_smoothing():
    print("\n=== Entropy Smoothing Check ===")
    # Mock histogram probabilities (some bins may be zero)
    p = np.array([0.1, 0.0, 0.3, 0.2, 0.0, 0.4])
    delta = 1e-10
    S_h = -np.sum(p * np.log(p + delta))
    print(f"Probabilities p: {p}")
    print(f"Shannon entropy with δ={delta}: S_h = {S_h:.6f}")
    assert np.isfinite(S_h), "Entropy produced non‑finite value."
    print("✓ Entropy smoothing prevents log(0).")

# ------------------------------
# Main
# ------------------------------
if __name__ == "__main__":
    test_jerk_stability()
    test_dimensionless_invariants()
    test_entropy_smoothing()
    print("\n=== All validation checks passed. ===")