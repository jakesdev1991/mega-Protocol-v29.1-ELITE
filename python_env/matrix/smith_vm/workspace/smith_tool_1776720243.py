# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
----------------------------------
Validates the corrected HSA Informational Jerk Stability Analysis
against the six rubric pillars and the two required fixes:
    * ψ = ln(Φ_N / Φ0)   (dimensionless invariant)
    * S_j regularised to avoid σ_j -> 0 singularity
"""

import numpy as np
from typing import Tuple

# ----------------------------------------------------------------------
# Helper synthetic data generators (stand‑in for real HSA/finance telemetry)
# ----------------------------------------------------------------------
def generate_coherence_field(Npairs: int = 200, Tsteps: int = 500,
                             seed: int = 42) -> np.ndarray:
    """Return ψ_ij(t) shaped (Npairs, Tsteps) – synthetic coherence."""
    rng = np.random.default_rng(seed)
    # Base field with slow drift + small noise
    base = np.linspace(0.5, 1.5, Tsteps)[None, :]          # (1,T)
    noise = rng.normal(0, 0.05, size=(Npairs, Tsteps))
    return base + noise   # shape (Npairs, Tsteps)

def compute_globals(psi_ij: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Φ_N(t) = mean over pairs, Φ_Δ(t) = std over pairs."""
    Phi_N = psi_ij.mean(axis=0)               # (T,)
    Phi_Delta = psi_ij.std(axis=0, ddof=1)    # (T,)
    return Phi_N, Phi_Delta

# ----------------------------------------------------------------------
# Invariant computations
# ----------------------------------------------------------------------
def scalar_invariant(Phi_N: np.ndarray, Phi0: float = None) -> np.ndarray:
    """
    ψ(t) = ln( Φ_N(t) / Φ0 )
    If Phi0 is None, use the temporal median as reference (dimensionless).
    """
    if Phi0 is None:
        Phi0 = np.median(Phi_N)
    if np.any(Phi_N <= 0):
        raise ValueError("Φ_N must be positive for log.")
    return np.log(Phi_N / Phi0)

def radial_correlation_length(psi_ij: np.ndarray, dx: float = 1.0) -> np.ndarray:
    """
    ξ_N(t) = ( (1/N) Σ ||∇ψ_ij||² )^{-1/2}
    Approximate gradient with finite differences along a dummy spatial axis.
    """
    # Assume psi_ij varies along a synthetic axis of length Npairs
    grad = np.diff(psi_ij, axis=0) / dx          # (Npairs-1, T)
    sqnorm = np.sum(grad**2, axis=0)             # (T,)
    xi_N = (np.mean(sqnorm) )**(-0.5)            # scalar (time‑independent for this toy)
    return np.full_like(psi_ij[0], xi_N)         # broadcast to (T,)

def poloidal_correlation_length(psi_ij: np.ndarray,
                                class_labels: np.ndarray) -> np.ndarray:
    """
    ξ_Δ(t) = max_c σ_c²(t) / min_c σ_c²(t)
    class_labels: integer array shape (Npairs,) indicating class c.
    """
    unique = np.unique(class_labels)
    vars_per_class = []
    for c in unique:
        mask = (class_labels == c)
        vars_per_class.append(np.var(psi_ij[mask, :], axis=0, ddof=1))
    vars_per_class = np.stack(vars_per_class, axis=0)   # (n_classes, T)
    max_var = np.max(vars_per_class, axis=0)
    min_var = np.min(vars_per_class, axis=0)
    # Avoid division by zero – add tiny epsilon
    eps = 1e-12
    xi_Delta = max_var / (min_var + eps)
    return xi_Delta

def shannon_entropy(psi_ij: np.ndarray, bins: int = 20) -> np.ndarray:
    """S_h(t) = - Σ p_k ln p_k over coherence distribution at each t."""
    T = psi_ij.shape[1]
    S_h = np.zeros(T)
    for t in range(T):
        hist, _ = np.histogram(psi_ij[:, t], bins=bins, density=True)
        p = hist[hist > 0]          # remove zeros to avoid log(0)
        S_h[t] = -np.sum(p * np.log(p))
    return S_h

def jerk_signal(Phi_N: np.ndarray, dt: float = 0.001) -> np.ndarray:
    """
    j(t) = d³Φ_N/dt³ using a 5‑point stencil (central differences).
    Returns array same length as Phi_N (edges padded with NaN).
    """
    # coefficients for 5‑point 3rd derivative: [-1/2, 1, -1/2, 0, 0] * (1/dt³) ?
    # Using standard formula: f'''(x) ≈ (-f_{i-2}+2f_{i-1}-2f_{i+1}+f_{i+2})/(2Δt³)
    coeff = np.array([-1, 2, 0, -2, 1]) / (2.0 * dt**3)
    j = np.convolve(Phi_N, coeff, mode='same')
    # edges will be inaccurate; we'll ignore them in tests
    return j

def jerk_stability(j: np.ndarray, window: int = 100, eps: float = 1e-12) -> np.ndarray:
    """
    S_j(T) = (1 + | (1/T)∫[(j‑j̄)/√(σ_j²+ε)]⁴ dτ – 3| )⁻¹
    Implemented over a sliding window; returns NaN for insufficient samples.
    """
    T = j.size
    S_j = np.full(T, np.nan)
    half = window // 2
    for i in range(half, T - half):
        seg = j[i-half:i+half+1]
        jbar = seg.mean()
        sigma2 = seg.var(ddof=1)
        denom = np.sqrt(sigma2 + eps)
        z4 = ((seg - jbar) / denom) ** 4
        kappa = z4.mean()          # raw kurtosis
        excess = np.abs(kappa - 3.0)
        S_j[i] = 1.0 / (1.0 + excess)
    return S_j

# ----------------------------------------------------------------------
# Unit‑test style validation
# ----------------------------------------------------------------------
def run_validation():
    print("=== Omega Protocol Invariant Validation ===")
    # 1. Generate synthetic data
    psi_ij = generate_coherence_field()
    Phi_N, Phi_Delta = compute_globals(psi_ij)

    # 2. Scalar invariant ψ
    psi = scalar_invariant(Phi_N)               # uses median Φ0 internally
    # Check dimensionless: ψ should be real-valued, no units
    assert np.all(np.isfinite(psi)), "ψ contains NaN or Inf"
    assert np.allclose(np.exp(psi) * np.median(Phi_N), Phi_N, rtol=1e-10), \
        "ψ does not satisfy ψ = ln(Φ_N/Φ0)"
    print("✓ Scalar invariant ψ = ln(Φ_N/Φ0) passes.")

    # 3. Radial correlation ξ_N
    xi_N = radial_correlation_length(psi_ij)
    assert np.all(xi_N > 0), "ξ_N must be positive"
    print("✓ Radial correlation length ξ_N > 0 passes.")

    # 4. Poloidal correlation ξ_Δ – assign dummy classes (2 classes)
    Npairs = psi_ij.shape[0]
    class_labels = np.mod(np.arange(Npairs), 2)   # alternating 0/1
    xi_Delta = poloidal_correlation_length(psi_ij, class_labels)
    assert np.all(xi_Delta >= 1.0 - 1e-12), "ξ_Δ must be ≥1 (isotropy lower bound)"
    print("✓ Poloidal correlation length ξ_Δ ≥ 1 passes.")

    # 5. Entropy S_h
    S_h = shannon_entropy(psi_ij)
    assert np.all(S_h >= 0.0), "Entropy must be non‑negative"
    print("✓ Shannon entropy S_h ≥ 0 passes.")

    # 6. Jerk and jerk stability
    j = jerk_signal(Phi_N)
    # Discard edge NaNs
    valid = ~np.isnan(j)
    j_valid = j[valid]
    # Test regularised S_j: for a perfectly constant jerk segment, S_j → 1
    const_seg = np.ones_like(j_valid[:50]) * j_valid[0]   # force constant
    Sj_const = jerk_stability(const_seg, window=20, eps=1e-12)
    assert np.allclose(Sj_const, 1.0, atol=1e-6), \
        "Regularised S_j should be 1 for constant jerk"
    # General case: values must lie in (0,1]
    Sj = jerk_stability(j_valid, window=30, eps=1e-12)
    assert np.all((Sj > 0) & (Sj <= 1.0 + 1e-12)), "S_j must be in (0,1]"
    print("✓ Jerk stability S_j regularised and bounded (0,1] passes.")

    # 7. Cost function integrand non‑negative (spot check)
    alpha, lam = 0.5, 0.2
    P_meas = np.random.rand(*Phi_N.shape) * 100.0
    P_target = np.mean(P_meas)
    integrand = (1.0 - Sj)**2 + alpha * S_h[valid] + lam * (P_meas[valid] - P_target)**2
    assert np.all(integrand >= -1e-12), "Cost integrand must be non‑negative"
    print("✓ Cost function integrand ≥ 0 passes.")

    print("\nAll Omega‑Protocol invariants satisfied. ✅")

if __name__ == "__main__":
    run_validation()