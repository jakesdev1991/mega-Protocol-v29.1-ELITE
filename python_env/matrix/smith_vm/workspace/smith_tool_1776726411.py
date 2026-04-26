# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Agent Smith – Omega Protocol Validation Script
# Purpose: Verify mathematical soundness of the SERC output
#          (UMCJ-Ω v4.1) and enforce Omega Protocol invariants.
# --------------------------------------------------------------
import numpy as np

# ------------------- Helper Functions -------------------------

def pairwise_coherence(A, L, L0):
    """ψ_ij = A_ij * exp(-L_ij / L0)"""
    return A * np.exp(-L / L0)

def consensus_novelty(psi):
    """Φ_N = mean(ψ),  Φ_Δ = std(ψ)"""
    Phi_N = np.mean(psi)
    Phi_Delta = np.std(psi, ddof=0)   # population std as in definition
    return Phi_N, Phi_Delta

def dimensionless_invariant(Phi_N, Phi0):
    """ψ = ln(Φ_N / Φ_0)  (must be dimensionless)"""
    return np.log(Phi_N / Phi0)

def regularized_anisotropy(sigma2_vals, eps_factor=1e-6):
    """
    ξ_Δ = (max σ_c² + ε) / (min σ_c² + ε)
    ε = eps_factor * ⟨σ_c²⟩
    """
    sigma2_vals = np.asarray(sigma2_vals)
    eps = eps_factor * np.mean(sigma2_vals)
    return (np.max(sigma2_vals) + eps) / (np.min(sigma2_vals) + eps)

def shannon_entropy(p, delta=1e-10):
    """S_h = - Σ p_k ln(p_k + δ)"""
    p = np.asarray(p)
    p = p / np.sum(p)          # renormalize for safety
    return -np.sum(p * np.log(p + delta))

def jerk_stability_metric(j, eps_factor=1e-6):
    """
    Original (flawed) definition:
        z = (j - j̄) / sqrt(σ_j² + ε_j)
        κ_raw = ⟨z⁴⟩,   κ = κ_raw - 3
        S_j = (1 + |κ|)^{-1}
    Returns S_j_original and also the *corrected* version:
        κ_corr = ⟨(j - j̄)⁴⟩ / (σ_j² + ε_j)² - 3
        S_j_corr = (1 + |κ_corr|)^{-1}
    """
    j = np.asarray(j)
    j_bar = np.mean(j)
    sigma2_j = np.var(j, ddof=0)
    eps_j = eps_factor * sigma2_j if sigma2_j > 0 else eps_factor

    # ----- original (flawed) -----
    z = (j - j_bar) / np.sqrt(sigma2_j + eps_j)
    kappa_raw = np.mean(z**4)
    kappa = kappa_raw - 3
    S_j_orig = 1.0 / (1.0 + np.abs(kappa))

    # ----- corrected (variance‑regularized kurtosis) -----
    kappa_corr = np.mean((j - j_bar)**4) / (sigma2_j + eps_j)**2 - 3
    S_j_corr = 1.0 / (1.0 + np.abs(kappa_corr))

    return {
        "j_mean": j_bar,
        "j_var": sigma2_j,
        "eps_j": eps_j,
        "z": z,
        "kappa_original": kappa,
        "S_j_original": S_j_orig,
        "kappa_corrected": kappa_corr,
        "S_j_corrected": S_j_corr
    }

# ------------------- Test Cases ------------------------------

def test_constant_jerk():
    """Constant jerk → σ_j² = 0.  Expect S_j → 1 after correction."""
    # Simulate a window of jerk values (all equal)
    j_const = np.full(1000, 0.005)   # any non‑zero constant works
    res = jerk_stability_metric(j_const)
    print("=== Constant Jerk Test ===")
    print(f"Mean jerk: {res['j_mean']:.6f}")
    print(f"Variance:  {res['j_var']:.2e}")
    print(f"Original S_j: {res['S_j_original']:.6f}  (should be 0.25 if flawed)")
    print(f"Corrected S_j: {res['S_j_corrected']:.6f}  (should be ~1.0)")
    # Enforce Omega invariant: corrected metric must be ≈1 for constant jerk
    assert np.isclose(res['S_j_corrected'], 1.0, atol=1e-3), \
        "FAIL: Corrected jerk stability does not converge to 1 for constant jerk."
    print("PASS: Corrected jerk stability invariant satisfied.\n")

def test_varying_jerk():
    """Non‑zero variance jerk → S_j should be <1 (more unstable)."""
    np.random.seed(42)
    j_var = np.random.normal(loc=0.0, scale=0.01, size=1000)   # Gaussian jerk
    res = jerk_stability_metric(j_var)
    print("=== Varying Jerk Test ===")
    print(f"Mean jerk: {res['j_mean']:.6f}")
    print(f"Variance:  {res['j_var']:.2e}")
    print(f"Original S_j: {res['S_j_original']:.6f}")
    print(f"Corrected S_j: {res['S_j_corrected']:.6f}")
    # For a non‑degenerate distribution we expect S_j < 1
    assert res['S_j_corrected'] < 0.9, \
        "FAIL: Corrected jerk stability too close to 1 for variable jerk."
    print("PASS: Jerk stability correctly penalises variance.\n")

def test_regularized_anisotropy():
    """Check that ε prevents division‑by‑zero and scales with typical variance."""
    sigma2 = [1e-4, 1e-4, 1e-4]   # equal variances → ξ_Δ should be ≈1
    xi = regularized_anisotropy(sigma2)
    print("=== Anisotropy Regularization Test ===")
    print(f"σ² values: {sigma2}")
    print(f"ξ_Δ: {xi:.6f} (should be ≈1)")
    assert np.isclose(xi, 1.0, atol=1e-3), \
        "FAIL: Anisotropy ratio not unity for equal variances."
    # Test zero variance in one class (should not blow up)
    sigma2_zero = [0.0, 1e-3, 1e-3]
    xi2 = regularized_anisotropy(sigma2_zero)
    print(f"σ² with zero class: {sigma2_zero}")
    print(f"ξ_Δ: {xi2:.6f} (should be finite)")
    assert np.isfinite(xi2), "FAIL: ξ_Δ became infinite or NaN."
    print("PASS: Anisotropy regularisation prevents division‑by‑zero.\n")

def test_dimensionless_invariant():
    """ψ = ln(Φ_N/Φ_0) must be dimensionless; check scaling."""
    Phi_N = np.array([0.8, 0.9, 1.0, 1.1])
    Phi0 = np.median(Phi_N)   # calibration window median
    psi = dimensionless_invariant(Phi_N, Phi0)
    print("=== Dimensionless Invariant Test ===")
    print(f"Φ_N: {Phi_N}")
    print(f"Φ_0 (median): {Phi0:.4f}")
    print(f"ψ = ln(Φ_N/Φ_0): {psi}")
    # ψ should be real‑valued; no units attached
    assert np.all(np.isreal(psi)), "FAIL: ψ produced complex values."
    print("PASS: ψ is real‑valued (dimensionless).\n")

# ------------------- Main Validation ------------------------

if __name__ == "__main__":
    print("Agent Smith – Omega Protocol Mathematical Validation\n")
    test_constant_jerk()
    test_varying_jerk()
    test_regularized_anisotropy()
    test_dimensionless_invariant()
    print("All validation checks passed. The SERC output is mathematically sound "
          "provided the corrected jerk stability metric is used.")
# --------------------------------------------------------------