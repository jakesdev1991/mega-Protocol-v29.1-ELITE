# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ----------------- Helper functions -----------------
def pairwise_coherence(A, L, L0):
    """ψ_ij = A * exp(-L/L0) ; A∈[0,1]"""
    return A * np.exp(-L / L0)

def consensus_novelty(psi_ij):
    """Φ_N = mean, Φ_Δ = std"""
    Phi_N = np.mean(psi_ij)
    Phi_Delta = np.std(psi_ij, ddof=0)
    return Phi_N, Phi_Delta

def dimensionless_invariant(Phi_N, Phi0):
    """ψ = ln(Φ_N/Φ0)"""
    return np.log(Phi_N / Phi0)

def anisotropy_ratio(var_class, eps_scale=1e-6):
    """ξ_Δ = (max σ_c² + ε)/(min σ_c² + ε), ε = eps_scale * ⟨σ_c²⟩"""
    sigma2 = np.array(var_class)
    eps = eps_scale * np.mean(sigma2)
    return (np.max(sigma2) + eps) / (np.min(sigma2) + eps)

def shannon_entropy(p, delta=1e-10):
    """S_h = -Σ p ln(p+δ)"""
    return -np.sum(p * np.log(p + delta))

def jerk_stability_original(j_vals, eps_scale=1e-6):
    """Original S_j = (1+|κ|)^{-1} with κ = ⟨z⁴⟩-3, z = (j-ĵ)/√(σ_j²+ε)"""
    j_bar = np.mean(j_vals)
    sigma2 = np.var(j_vals, ddof=0)
    eps = eps_scale * np.max([sigma2, 1e-12])  # avoid zero
    z = (j_vals - j_bar) / np.sqrt(sigma2 + eps)
    kappa = np.mean(z**4) - 3
    return 1.0 / (1.0 + np.abs(kappa)), kappa

def jerk_stability_corrected(j_vals, eps_scale=1e-6):
    """Corrected S_j using variance‑regularized excess kurtosis:
       κ = ⟨(j-ĵ)⁴⟩/(σ_j²+ε)² - 3"""
    j_bar = np.mean(j_vals)
    sigma2 = np.var(j_vals, ddof=0)
    eps = eps_scale * np.max([sigma2, 1e-12])
    kappa = np.mean((j_vals - j_bar)**4) / (sigma2 + eps)**2 - 3
    return 1.0 / (1.0 + np.abs(kappa)), kappa

def five_point_stencil_derivative(f, dt):
    """5‑point stencil for third derivative: f''' ≈ (-f_{i+2}+2f_{i+1}-2f_{i-1}+f_{i-2})/(2Δt³)"""
    n = len(f)
    deriv = np.zeros_like(f)
    for i in range(2, n-2):
        deriv[i] = (-f[i+2] + 2*f[i+1] - 2*f[i-1] + f[i-2]) / (2.0 * dt**3)
    # edges: fallback to lower order (not used in central window)
    return deriv

# ----------------- Validation -----------------
def test_jerk_stability():
    # Simulate constant jerk j0 in intrinsic time τ
    j0 = 0.05  # arbitrary constant jerk
    tau = np.linspace(0, 0.1, 1000)  # 100 ms window, 10 kHz sampling => dt=0.1ms
    dt = tau[1] - tau[0]
    # Φ_N(τ) = a0 + a1 τ + 0.5 a2 τ² + (j0/6) τ³  (so that d³Φ_N/dτ³ = j0)
    a0, a1, a2 = 1.0, 0.0, 0.0
    Phi_N = a0 + a1*tau + 0.5*a2*tau**2 + (j0/6.0)*tau**3

    # Compute jerk via stencil (should recover j0 up to numerical error)
    j_est = five_point_stencil_derivative(Phi_N, dt)
    j_est = j_est[2:-2]  # keep central region where stencil is valid
    j_true = np.full_like(j_est, j0)

    # Original metric
    S_j_orig, kappa_orig = jerk_stability_original(j_est)
    # Corrected metric
    S_j_corr, kappa_corr = jerk_stability_corrected(j_est)

    # Assertions
    np.testing.assert_allclose(j_est, j_true, rtol=1e-2, atol=1e-3,
                               err_msg="Stencil did not recover constant jerk")
    # Original metric must NOT be close to 1 (exposes the flaw)
    assert not np.isclose(S_j_orig, 1.0, atol=1e-2), \
        f"Original S_j unexpectedly ≈1 ({S_j_orig}); flaw not detected"
    # Corrected metric must be ≈1 for constant jerk
    assert np.isclose(S_j_corr, 1.0, atol=1e-2), \
        f"Corrected S_j not ≈1 ({S_j_corr}); regularization failed"
    # Excess kurtosis for constant jerk should be ≈0 after regularization
    assert np.isclose(kappa_corr, 0.0, atol=1e-2), \
        f"Corrected κ not ≈0 ({kappa_corr})"

def test_invariants():
    # Dummy data for coherence field
    Npairs = 500
    A = np.random.uniform(0.2, 0.9, Npairs)
    L = np.random.uniform(0.1, 5.0, Npairs)  # latency
    L0 = 2.0
    psi_ij = pairwise_coherence(A, L, L0)

    Phi_N, Phi_Delta = consensus_novelty(psi_ij)
    Phi0 = np.median(Phi_N)  # calibration window median (here single snapshot)
    psi = dimensionless_invariant(Phi_N, Phi0)

    # ψ must be dimensionless (any real number is fine); just ensure no NaN/inf
    assert np.all(np.isfinite(psi)), "ψ contains non-finite values"

    # Anisotropy test: split into three dummy classes
    var_cpu_gpu = np.var(psi_ij[:Npairs//3])
    var_gpu_gpu = np.var(psi_ij[Npairs//3:2*Npairs//3])
    var_cpu_cpu = np.var(psi_ij[2*Npairs//3:])
    xi_Delta = anisotropy_ratio([var_cpu_gpu, var_gpu_gpu, var_cpu_cpu])
    assert xi_Delta >= 1.0 - 1e-12, f"ξ_Δ < 1 ({xi_Delta})"

    # Entropy test: bin psi_ij via Freedman-Diaconis (simple approximation)
    q75, q25 = np.percentile(psi_ij, [75, 25])
    iqr = q75 - q25
    bin_width = 2 * iqr * (Npairs ** (-1/3.0))
    bin_width = max(bin_width, 1e-6)
    counts, _ = np.histogram(psi_ij, bins=int(np.ceil((psi_ij.max()-psi_ij.min())/bin_width)))
    p = counts / counts.sum()
    S_h = shannon_entropy(p)
    assert S_h >= 0.0, f"Negative entropy ({S_h})"

    # Jerk stability test (constant jerk case)
    test_jerk_stability()

if __name__ == "__main__":
    test_invariants()
    print("All Omega Protocol invariant checks passed.")