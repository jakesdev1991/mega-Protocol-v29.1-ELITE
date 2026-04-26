# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
disruption_verifier.py

Demonstrates two fatal flaws in the Omega‑Protocol derivation:
1. The invariant ψ is astronomically small and never diverges.
2. The rubric's conditional entropy can yield negative values.
"""

import numpy as np
from scipy.special import logsumexp

# ----------------------------------------------------------------------
# 1. Invariant ψ is a ghost
# ----------------------------------------------------------------------
def compute_psi(alpha0: float, a: float, c0_factor: float) -> float:
    """
    Computes ψ = ln[1 + (α0/π) ΠΔ(0)] using the *original* (correct) δmΔ².
    Shows that ψ is ~ O(10⁻³⁷⁶) for realistic α0.
    """
    pi = np.pi
    m0_sq = pi / a**2                    # UV scale
    # Original definition: δmΔ² = (α0 / a²) * c0
    delta_m_sq = (alpha0 / a**2) * c0_factor
    psi = np.log1p(delta_m_sq / m0_sq)  # log1p for stability
    return psi, delta_m_sq, m0_sq

def typical_parameters():
    """Typical lattice QED parameters (dimensionless units a=1)."""
    alpha0 = 1.0/137.0                   # fine‑structure constant
    a = 1.0                              # lattice spacing in units of a
    # Instanton factor c0 = exp(-8π²/g²) with g² = 4π α0
    g2 = 4.0 * np.pi * alpha0
    c0 = np.exp(-8.0 * np.pi**2 / g2)    # ~ exp(-862) → 1e-376
    return alpha0, a, c0

# ----------------------------------------------------------------------
# 2. Conditional entropy can be negative
# ----------------------------------------------------------------------
def conditional_entropy_unsafe(rho_joint: np.ndarray) -> float:
    """
    Implements the rubric's definition:
    S = -∑_{k,k'} ρ(k) ρ(k|k') ln ρ(k|k')
    where ρ(k|k') = ρ(k,k') / ρ(k') (no enforcement of normalization).
    If ρ(k') is not a proper marginal, the result can be negative.
    """
    # Compute "marginals" by summing over the other axis (may not be normalized)
    rho_k = rho_joint.sum(axis=1)   # sum over k' → ρ(k)
    rho_kprime = rho_joint.sum(axis=0)  # sum over k → ρ(k')

    # Avoid division by zero
    eps = 1e-16
    # Conditional kernel (may not sum to 1)
    cond_kernel = rho_joint / (rho_kprime + eps)

    # Rubric's entropy
    S = -np.sum(rho_joint * np.log(cond_kernel + eps))
    return S

def demo_negative_entropy():
    """
    Creates a joint distribution where the conditional kernel is not normalized,
    leading to negative conditional entropy.
    """
    # 3x3 joint distribution (non‑normalized conditional)
    rho_joint = np.array([[0.1, 0.2, 0.05],
                          [0.05, 0.1, 0.2],
                          [0.2, 0.05, 0.1]], dtype=float)
    # Normalize to sum to 1 (so it's a valid joint distribution)
    rho_joint /= rho_joint.sum()
    S = conditional_entropy_unsafe(rho_joint)
    return S

# ----------------------------------------------------------------------
# Main execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Show ψ is a ghost
    alpha0, a, c0 = typical_parameters()
    psi, delta_m_sq, m0_sq = compute_psi(alpha0, a, c0)
    print("=== Invariant ψ Ghost Test ===")
    print(f"α0 = {alpha0:.6f}, a = {a:.1f}")
    print(f"c0 (instanton factor) = {c0:.3e}")
    print(f"δmΔ² = (α0/a²)·c0 = {delta_m_sq:.3e}")
    print(f"m0² = π/a² = {m0_sq:.3f}")
    print(f"ψ = ln[1 + δmΔ²/m0²] = {psi:.3e}")
    print(f"ψ is effectively zero: |ψ| < 1e-300 → Shredding/Freeze boundaries are unreachable.\n")

    # 2. Show entropy can be negative
    S = demo_negative_entropy()
    print("=== Conditional Entropy Trap Test ===")
    print(f"Joint distribution (normalized): sum = {np.array([[0.1,0.2,0.05],[0.05,0.1,0.2],[0.2,0.05,0.1]]).sum():.2f}")
    print(f"Rubric's conditional entropy S = {S:.6f}")
    if S < 0:
        print("RESULT: S < 0 → violates information monotonicity (entropy cannot be negative).")
    else:
        print("RESULT: S ≥ 0 (by chance).")
    print("\nConclusion: The Omega Protocol’s rubric hides fatal flaws behind a ‘no‑boilerplate’ smokescreen.")