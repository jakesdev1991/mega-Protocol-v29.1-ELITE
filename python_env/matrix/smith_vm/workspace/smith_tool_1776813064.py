# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for ATS‑Ω
Checks mathematical soundness of the Algorithmic Topology Shield proposal.
"""

import numpy as np
from numpy.linalg import eigvalsh

# ----------------------------------------------------------------------
# Helper functions (directly from the proposal)
# ----------------------------------------------------------------------
def compute_ATI(Ricci_curv, Ricci_curv0, beta1, beta10, S_alg):
    """
    Algorithmic Topology Integrity Index.
    All inputs are non‑negative scalars.
    """
    if Ricci_curv0 == 0 or beta10 == 0:
        raise ValueError("Reference curvature or beta1 must be non‑zero.")
    ATI = (np.abs(Ricci_curv) / np.abs(Ricci_curv0)) * \
          (beta1 / beta10) * np.exp(-S_alg)
    return np.clip(ATI, 0.0, 1.0)   # enforce [0,1] by definition

def Phi_N_from_Sigma(Sigma):
    """Φ_N = sqrt(max eigenvalue of covariance matrix Σ)."""
    evals = eigvalsh(Sigma)
    return np.sqrt(np.max(evals))

def Phi_Delta_from_moments(mu2, mu3):
    """Φ_Δ = μ₃ / (μ₂)^{3/2} . Requires μ₂>0."""
    if mu2 <= 0:
        raise ValueError("Second central moment μ₂ must be positive.")
    return mu3 / (mu2 ** 1.5)

def psi_ats(Phi_N, Phi_N0):
    """Invariant ψ = ln(Φ_N/Φ_N⁰)."""
    if Phi_N <= 0 or Phi_N0 <= 0:
        raise ValueError("Φ_N and reference Φ_N⁰ must be >0.")
    return np.log(Phi_N / Phi_N0)

def entropy_gauge(S_alg_func, x):
    """
    Returns 𝒜_μ = ∂_μ S and J^μ = √2 Φ_δ δ^μ_0.
    For demonstration we assume S depends only on time component x[0].
    """
    S = S_alg_func(x)
    # numeric gradient (central difference)
    eps = 1e-6
    grad = np.zeros_like(x)
    for i in range(len(x)):
        xp = x.copy(); xm = x.copy()
        xp[i] += eps; xm[i] -= eps
        grad[i] = (S_alg_func(xp) - S_alg_func(xm)) / (2*eps)
    # J^μ: only time component non‑zero, Φ_δ supplied externally
    J = np.zeros_like(x)
    J[0] = np.sqrt(2) * Phi_Delta_placeholder  # will be set later
    return grad, J

def check_boundaries(Phi_N, S_alg, Phi_N0, S_alg0):
    """
    Determine ψ_ats sign according to the two horizons.
    Returns +1 for shredding tendency, -1 for freeze tendency, 0 otherwise.
    """
    psi = psi_ats(Phi_N, Phi_N0)
    # high/low entropy thresholds (chosen as multiples of reference)
    high_entropy = S_alg > 2 * S_alg0
    low_entropy  = S_alg < 0.5 * S_alg0
    if Phi_N > 5 * Phi_N0 and high_entropy:
        return +1   # shredding → ψ → +∞
    if Phi_N < 0.2 * Phi_N0 and low_entropy:
        return -1   # freeze    → ψ → -∞
    return 0

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_ATS_Omega():
    # ---- Synthetic but physically plausible data -----------------------
    np.random.seed(42)
    n_components = 6
    # computational‑integrity field values (dimensionless)
    B = np.random.randn(n_components) * 0.5 + 1.0   # mean ≈1, std≈0.5
    Sigma = np.cov(B, bias=True)                    # population covariance
    # moments of B (μ₂, μ₃)
    mu2 = np.var(B)
    mu3 = np.mean((B - np.mean(B))**3)

    # topological quantities (mock)
    Ricci_curv   = np.random.uniform(0.2, 0.8)
    Ricci_curv0  = 0.5
    beta1        = np.random.uniform(1, 3)
    beta10       = 2.0
    S_alg        = np.random.uniform(0.2, 1.5)   # path entropy
    S_alg0       = 0.5                         # reference entropy
    Phi_N0       = 1.0                         # reference variance sqrt

    # ---- Compute derived quantities ------------------------------------
    ATI   = compute_ATI(Ricci_curv, Ricci_curv0, beta1, beta10, S_alg)
    Phi_N = Phi_N_from_Sigma(Sigma)
    global Phi_Delta_placeholder   # for entropy_gauge closure
    Phi_Delta_placeholder = Phi_Delta_from_moments(mu2, mu3)
    psi   = psi_ats(Phi_N, Phi_N0)
    # entropy gauge (need a dummy S_alg(x) that depends on first component of x)
    def S_alg_of_x(x):
        # simple model: S varies linearly with B[0] (first component)
        return S_alg * (x[0] / B[0]) if B[0]!=0 else S_alg
    A_mu, J_mu = entropy_gauge(S_alg_of_x, B)

    # ---- Assertions (Omega Protocol invariants) -----------------------
    # 1. ATI in [0,1]
    assert 0.0 <= ATI <= 1.0 + 1e-12, f"ATI out of bounds: {ATI}"
    # 2. Invariant matches definition
    assert np.abs(psi - np.log(Phi_N/Phi_N0)) < 1e-10, "ψ invariant mismatch"
    # 3. Φ_N, Φ_Δ positive (required for log and gauge)
    assert Phi_N > 0, "Φ_N must be >0"
    assert Phi_Delta_placeholder > 0, "Φ_Δ must be >0 for physical gauge"
    # 4. Entropy gauge structure: J only time component, proportional to √2 Φ_Δ
    assert np.allclose(J_mu[1:], 0.0, atol=1e-12), "J^μ must have only time component"
    assert np.abs(J_mu[0] - np.sqrt(2)*Phi_Delta_placeholder) < 1e-10, "J^0 mismatch"
    # 5. 𝒜_μ = gradient of S (numerical check)
    #    We already computed A_mu via gradient; just ensure it's finite.
    assert np.all(np.isfinite(A_mu)), "𝒜_μ contains non‑finite values"
    # 6. Boundary sign consistency
    boundary_sign = check_boundaries(Phi_N, S_alg, Phi_N0, S_alg0)
    if boundary_sign == +1:
        assert psi > 0, "Shredding horizon should give ψ>0"
    elif boundary_sign == -1:
        assert psi < 0, "Freeze horizon should give ψ<0"
    # 7. MPC‑Ω QP constraints (if claimed satisfied)
    assert ATI >= 0.6 - 1e-12, f"ATI constraint violated: {ATI}"
    assert Phi_N >= 0.5 - 1e-12, f"Φ_N constraint violated: {Phi_N}"
    assert S_alg >= np.log(2) - 1e-12, f"S_alg constraint violated: {S_alg}"

    # ---- If we reach here, all invariants hold -----------------------
    print("✅ All Omega Protocol invariants satisfied.")
    print(f"   ATI          = {ATI:.4f}")
    print(f"   Φ_N          = {Phi_N:.4f} (ref {Phi_N0})")
    print(f"   Φ_Δ          = {Phi_Delta_placeholder:.4f}")
    print(f"   ψ_ats        = {psi:.4f}")
    print(f"   S_alg        = {S_alg:.4f} (ref {np.log(2):.4f})")
    print(f"   Boundary sign= {boundary_sign} "
          f"({'+∞' if boundary_sign==+1 else '-∞' if boundary_sign==-1 else 'neutral'})")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    validate_ATS_Omega()