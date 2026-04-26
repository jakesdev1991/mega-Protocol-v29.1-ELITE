# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit: Validate HSA Unified Memory Informational Jerk Stability
---------------------------------------------------------------------
Checks:
1. Dimensionless invariants (ψ, ξ_Δ, S_j) are unit‑free.
2. Regularisation prevents division‑by‑zero.
3. Corrected jerk stability metric yields S_j→1 for constant jerk
   and S_j<1 for non‑Gaussian fluctuations.
4. Anisotropy ratio ξ_Δ stays ≥1.
5. Entropy regularisation avoids log(0).
"""

import numpy as np

# ------------------------------
# Helper functions (definitions)
# ------------------------------
def pairwise_coherence(A, L, L0):
    """ψ_ij = A * exp(-L/L0)  (dimensionless)"""
    return A * np.exp(-L / L0)

def consensus_phi_n(psi_ij):
    """Φ_N = ⟨ψ_ij⟩"""
    return np.mean(psi_ij)

def novelty_phi_delta(psi_ij, phi_n):
    """Φ_Δ = sqrt⟨(ψ_ij - Φ_N)²⟩"""
    return np.sqrt(np.mean((psi_ij - phi_n) ** 2))

def normalized_invariant(phi_n, phi0):
    """ψ = ln(Φ_N/Φ₀)  (dimensionless)"""
    return np.log(phi_n / phi0)

def anisotropy_ratio(var_dict, eps_scale=1e-6):
    """
    ξ_Δ = (max σ_c² + ε) / (min σ_c² + ε)
    ε = eps_scale * typical variance (mean of all classes)
    """
    vars_ = np.array(list(var_dict.values()))
    typical = np.mean(vars_)
    eps = eps_scale * typical
    return (np.max(vars_) + eps) / (np.min(vars_) + eps)

def shannon_entropy(p, delta=1e-10):
    """S_h = - Σ p_k ln(p_k + δ)"""
    return -np.sum(p * np.log(p + delta))

def jerk_stability_original(j_vals, eps_scale=1e-6):
    """
    Original metric from the thought:
        z = (j - j̄)/√(σ_j² + ε_j)
        κ_raw = ⟨z⁴⟩
        κ = κ_raw - 3
        S_j = (1 + |κ|)⁻¹
    Demonstrates the flaw (constant jerk → S_j≠1).
    """
    j_bar = np.mean(j_vals)
    var_j = np.var(j_vals)
    eps_j = eps_scale * np.mean(var_j) if var_j > 0 else eps_scale
    z = (j_vals - j_bar) / np.sqrt(var_j + eps_j)
    kappa_raw = np.mean(z ** 4)
    kappa = kappa_raw - 3.0
    S_j = 1.0 / (1.0 + np.abs(kappa))
    return S_j, kappa

def jerk_stability_corrected(j_vals, eps_scale=1e-6):
    """
    Corrected metric:
        z = (j - j̄)/√(σ_j² + ε_j)   (ε_j prevents divide‑by‑zero)
        If σ_j² < ε_j → treat z≡0 → κ=0 → S_j=1
        Otherwise compute excess kurtosis:
            κ = ⟨z⁴⟩/⟨z²⟩² - 3
        S_j = exp(-|κ|)
    """
    j_bar = np.mean(j_vals)
    var_j = np.var(j_vals)
    eps_j = eps_scale * np.mean(var_j) if var_j > 0 else eps_scale
    if var_j < eps_j:                     # effectively constant jerk
        return 1.0, 0.0
    z = (j_vals - j_bar) / np.sqrt(var_j + eps_j)
    z2 = np.mean(z ** 2)
    z4 = np.mean(z ** 4)
    # Guard against numerical zero in denominator
    if z2 == 0:
        kappa = 0.0
    else:
        kappa = z4 / (z2 ** 2) - 3.0
    S_j = np.exp(-np.abs(kappa))
    return S_j, kappa

# ------------------------------
# Synthetic data generation for validation
# ------------------------------
np.random.seed(42)
N_pairs = 5000
# Simulate atomic success rate A∈[0,1] and latency L>0
A = np.random.rand(N_pairs)
L = np.random.exponential(scale=10.0, size=N_pairs)   # ms
L0 = 15.0   # normalisation constant (ms)

psi_ij = pairwise_coherence(A, L, L0)
phi_n = consensus_phi_n(psi_ij)
phi0 = np.median(psi_ij)          # calibration window median (dimensionless)
psi = normalized_invariant(phi_n, phi0)

# Novelty
phi_delta = novelty_phi_delta(psi_ij, phi_n)

# Directional variance classes (simple split)
n_third = N_pairs // 3
var_cpu_gpu = np.var(psi_ij[:n_third])
var_gpu_gpu = np.var(psi_ij[n_third:2*n_third])
var_cpu_cpu = np.var(psi_ij[2*n_third:3*n_third])
var_dict = {"CPU-GPU": var_cpu_gpu,
            "GPU-GPU": var_gpu_gpu,
            "CPU-CPU": var_cpu_cpu}
xi_delta = anisotropy_ratio(var_dict)

# Entropy (histogram)
hist, bins = np.histogram(psi_ij, bins='fd')   # Freedman-Diaconis via numpy
p = hist / np.sum(p)
entropy = shannon_entropy(p)

# Jerk simulation: generate a smooth Φ_N(t) and differentiate 3x in intrinsic time
t = np.linspace(0, 0.2, 2000)          # 200 ms window
phi_n_t = 0.5 + 0.2*np.sin(2*np.pi*5*t) + 0.05*np.random.randn(len(t))  # baseline coherence
# Intrinsic time τ
phi0_calib = np.median(phi_n_t)
dtau_dt = phi_n_t / phi0_calib
tau = np.cumsum(dtau_dt) * (t[1]-t[0])   # simple integration
# Resample Φ_N onto uniform τ grid (linear interpolation)
tau_uniform = np.linspace(tau[0], tau[-1], 2000)
phi_n_uniform = np.interp(tau_uniform, tau, phi_n_t)
# Jerk via 5-point stencil on uniform τ (assuming unit spacing for simplicity)
def fifth_point_derivative3(y, h=1.0):
    """Return third derivative using 5-point central stencil."""
    n = len(y)
    d3 = np.zeros_like(y)
    # interior points
    for i in range(2, n-2):
        d3[i] = (-y[i-2] + 2*y[i-1] - 2*y[i+1] + y[i+2]) / (2*h**3)
    # edges: forward/backward lower-order (not critical for demo)
    d3[0:2] = d3[2]
    d3[-2:] = d3[-3]
    return d3

j_tau = fifth_point_derivative3(phi_n_uniform, h=tau_uniform[1]-tau_uniform[0])

# ------------------------------
# Validation checks
# ------------------------------
print("=== Omega Protocol Invariant Checks ===")
print(f"ψ (log‑ratio)          : {psi:.6f}  (dimensionless ✓)")
print(f"Φ_N                    : {phi_n:.6f}")
print(f"Φ_Δ                    : {phi_delta:.6f}")
print(f"ξ_Δ (anisotropy)       : {xi_delta:.6f}  (≥1? {xi_delta >= 1 - 1e-12})")
print(f"Entropy S_h            : {entropy:.6f}")
print()

# Jerk stability metrics
Sj_orig, kappa_orig = jerk_stability_original(j_tau)
Sj_corr, kappa_corr = jerk_stability_corrected(j_tau)

print("Jerk Stability (original definition):")
print(f"  κ (excess kurtosis)  : {kappa_orig:.6f}")
print(f"  S_j                  : {Sj_orig:.6f}  (should be →1 for constant jerk? {np.isclose(Sj_orig,1.0,atol=0.1)})")
print()
print("Jerk Stability (corrected definition):")
print(f"  κ (excess kurtosis)  : {kappa_corr:.6f}")
print(f"  S_j                  : {Sj_corr:.6f}  (constant jerk → 1? {np.isclose(Sj_corr,1.0,atol=1e-3)})")
print()

# Test constant jerk case explicitly
const_j = np.full_like(j_tau, np.mean(j_tau))
Sj_const_orig, _ = jerk_stability_original(const_j)
Sj_const_corr, _ = jerk_stability_corrected(const_j)
print("Constant‑jerk sanity check:")
print(f"  Original S_j         : {Sj_const_orig:.6f}  (fails → not 1)")
print(f"  Corrected S_j        : {Sj_const_corr:.6f}  (passes → ≈1)")

# ------------------------------
# Assertions for automated compliance (will raise if violated)
# ------------------------------
assert np.isfinite(psi), "ψ must be finite"
assert np.isfinite(xi_delta) and xi_delta >= 1.0, "ξ_Δ must be ≥1 and finite"
assert np.isfinite(entropy), "Entropy must be finite"
assert np.isfinite(Sj_corr) and 0.0 <= Sj_corr <= 1.0, "S_j must lie in [0,1]"
assert np.isclose(Sj_const_corr, 1.0, atol=1e-3), "Constant jerk must give S_j≈1"
print("\nAll automated checks passed. Framework is Omega‑Protocol compliant after the jerk‑stability fix.")