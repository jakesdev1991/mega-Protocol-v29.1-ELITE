# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol audit of the Higher‑Order Lattice Polarization correction.
Checks:
  1. Infrared convergence of the integral I(v,Λ) = ∫_{k<Λ} e^{-k²/(2Λ²)} / (1+(k·v)²) d³k
  2. Orthogonality Φ_N·Φ_Δ = 0 under Z₂ symmetry.
  3. Entropy bound H ≥ 0.85 for the Bose‑Einstein occupation.
  4. Sensitivity of Δα/α to regulator parameters (should be negligible).
"""

import numpy as np
from scipy.stats import qmc

# ------------------- Parameters -------------------
Lambda = 0.82          # cutoff
v_nom  = 1.28          # nominal velocity‑like parameter
v_safe = 1.25          # tightened bound suggested in the text
eps_reg = 1e-4         # regulator ε² added to denominator
k_min_frac = 0.1       # IR cutoff as fraction of Lambda
N_samples = 2_000_000  # Monte‑Carlo samples for integral & angular average
seed = 20250924
rng = np.random.default_rng(seed)

# ------------------- Helper Functions -------------------
def kernel(k, v, eps=0.0):
    """Kernel 1/(1+(k·v)²) with optional regulator ε²."""
    # k is shape (N,3), v is shape (3,)
    dot = np.einsum('ij,j->i', k, v)   # k·v for each sample
    return 1.0 / (1.0 + dot**2 + eps**2)

def integrand_mc(N, Lambda, v, eps=0.0):
    """
    Monte‑Carlo estimate of I = ∫_{0}^{Λ} 4π k² e^{-k²/(2Λ²)} ⟨kernel⟩ dk
    where ⟨kernel⟩ is the angular average over the sphere.
    """
    # Sample k magnitude uniformly in [0,Λ] (importance sampling optional)
    k = rng.uniform(0, Lambda, N)
    # Sample uniform directions on the unit sphere
    # Using Marsaglia method
    z = rng.uniform(-1, 1, N)
    r = np.sqrt(1 - z**2)
    phi = rng.uniform(0, 2*np.pi, N)
    ux = r * np.cos(phi)
    uy = r * np.sin(phi)
    uz = z
    dirs = np.stack([ux, uy, uz], axis=1)   # (N,3)
    k_vec = k[:,None] * dirs                # (N,3)

    # Angular average of kernel for each k magnitude
    ker = kernel(k_vec, v, eps)             # (N,)
    # Weight from radial part: 4π k² e^{-k²/(2Λ²)}
    weight = 4.0 * np.pi * k**2 * np.exp(-k**2/(2*Lambda**2))
    integrand = weight * ker
    # Monte‑Carlo estimate: (Λ/N) * Σ integrand  (since k sampled uniformly)
    I_est = (Lambda / N) * np.sum(integrand)
    return I_est

def entropy_bose_einstein(Lambda, k_min=0.0, N=500_000):
    """
    Compute Shannon entropy H = - Σ n_k ln n_k for modes k∈[k_min,Λ]
    with Bose‑Einstein occupation n_k = 1/(exp(k²/(2Λ²))-1).
    Integral approximated via MC sampling of k magnitude (isotropic).
    """
    k = rng.uniform(k_min, Lambda, N)
    # Density of states in 3D: 4π k²
    nk = 1.0 / (np.exp(k**2/(2*Lambda**2)) - 1.0)
    # Avoid log(0) for extremely large nk (should not happen for k>0)
    nk = np.maximum(nk, 1e-15)
    integrand = -nk * np.log(nk) * 4.0 * np.pi * k**2
    H_est = (Lambda - k_min) / N * np.sum(integrand)
    return H_est

def orthogonality_check(N=200_000):
    """
    Generate random mode pairs that respect Z₂ symmetry:
    Φ_N corresponds to even parity modes, Φ_Δ to odd parity.
    Under exact Z₂ decoupling the dot product should vanish.
    We test by constructing random vectors with definite parity
    and measuring their dot product.
    """
    # Even parity: components symmetric under inversion (no sign change)
    # Odd parity: antisymmetric (sign flips). We'll simulate by assigning
    # random Gaussian components and then enforcing parity.
    vec_N = rng.normal(size=(N,3))
    # For even parity we keep as is; for odd we flip sign of a random axis
    flip_axis = rng.integers(0,3,size=N)
    vec_Delta = vec_N.copy()
    vec_Delta[np.arange(N), flip_axis] *= -1.0   # odd parity
    dot = np.einsum('ij,ij->i', vec_N, vec_Delta)
    return np.mean(dot), np.std(dot)

# ------------------- 1. Integral Convergence -------------------
print("=== Infrared Convergence Test ===")
I_nom   = integrand_mc(N_samples, Lambda, v_nom, eps=0.0)
I_reg   = integrand_mc(N_samples, Lambda, v_nom, eps=eps_reg)
I_safe  = integrand_mc(N_samples, Lambda, v_safe, eps=0.0)
print(f"I(v={v_nom:.3f}, Λ={Lambda:.3f}, ε=0)   = {I_nom:.6e}")
print(f"I(v={v_nom:.3f}, Λ={Lambda:.3f}, ε={eps_reg:.1e}) = {I_reg:.6e}")
print(f"I(v={v_safe:.3f}, Λ={Lambda:.3f}, ε=0)   = {I_safe:.6e}")
print("Relative change due to regulator:", (I_reg-I_nom)/I_nom if I_nom!=0 else 0)
print("Relative change due to v‑tightening:", (I_safe-I_nom)/I_nom if I_nom!=0 else 0)
print()

# ------------------- 2. Entropy Bound -------------------
print("=== Entropy Bound Test ===")
H_full   = entropy_bose_einstein(Lambda, k_min=0.0, N=800_000)
H_cutoff = entropy_bose_einstein(Lambda, k_min=k_min_frac*Lambda, N=800_000)
print(f"H(k_min=0)          = {H_full:.5f}")
print(f"H(k_min=0.1Λ)       = {H_cutoff:.5f}")
print(f"Entropy ≥0.85?      = {H_full >= 0.85} (full), {H_cutoff >= 0.85} (cutoff)")
print()

# ------------------- 3. Orthogonality -------------------
print("=== Orthogonality (Z₂) Check ===")
mean_dot, std_dot = orthogonality_check(N=300_000)
print(f"⟨Φ_N·Φ_Δ⟩ = {mean_dot:.3e} ± {std_dot:.3e}")
print(f"Orthogonality satisfied? |mean| < 1e-3 ? {abs(mean_dot) < 1e-3}")
print()

# ------------------- 4. Δα/α Sensitivity -------------------
print("=== Δα/α Sensitivity ===")
prefactor = 0.0000321   # claimed dimensionless factor from paper
Delta_alpha_nom   = prefactor * I_nom   / (Lambda**2)
Delta_alpha_reg   = prefactor * I_reg   / (Lambda**2)
Delta_alpha_safe  = prefactor * I_safe  / (Lambda**2)
print(f"Δα/α (nom)   = {Delta_alpha_nom:.3e}")
print(f"Δα/α (reg)   = {Delta_alpha_reg:.3e}")
print(f"Δα/α (safe)  = {Delta_alpha_safe:.3e}")
print(f"Variation due to ε: {(Delta_alpha_reg-Delta_alpha_nom)/Delta_alpha_nom:.2%}")
print(f"Variation due to v: {(Delta_alpha_safe-Delta_alpha_nom)/Delta_alpha_nom:.2%}")
print()

# ------------------- Final Verdict -------------------
print("=== Omega‑Protocol Verdict ===")
issues = []
if not np.isfinite(I_nom):
    issues.append("Integral diverges without regulator (IR instability).")
if abs(mean_dot) > 1e-3:
    issues.append("Orthogonality Φ_N·Φ_Δ ≠ 0 detected.")
if H_full < 0.85:
    issues.append("Entropy bound violated for exact Bose‑Einstein distribution.")
if abs((Delta_alpha_reg-Delta_alpha_nom)/Delta_alpha_nom) > 0.01:
    issues.append("Δα/α overly sensitive to ad‑hoc regulator ε.")
if abs((Delta_alpha_safe-Delta_alpha_nom)/Delta_alpha_nom) > 0.01:
    issues.append("Δα/α overly sensitive to v‑tightening.")
if issues:
    print("FAIL – the following protocol violations were found:")
    for i, msg in enumerate(issues,1):
        print(f"  {i}. {msg}")
else:
    print("PASS – all Omega‑Protocol invariants satisfied within numerical tolerance.")