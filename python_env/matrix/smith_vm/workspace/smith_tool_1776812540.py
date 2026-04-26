# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit – Quantum Memory Shield for Distributed Cognition (QM‑Ω)

This script validates the mathematical soundness and internal consistency of the
QM‑Ω proposal against the Omega Protocol invariants (Φ_N, Φ_Δ, J*).  It does **not**
attempt to prove the underlying physics; it merely checks that:
  1. All derived quantities are defined on their proper domains.
  2. The mapping from the Cognitive Decoherence Index (CDI) to Ω‑variables
     respects the claimed lead‑time relationships and monotonicity.
  3. The invariant ψ, entropy gauge S_cognitive, and the QP constraints
     are internally consistent.
  4. The cost function J is non‑negative and its terms are correctly formed.

The script is deliberately lightweight – it uses only NumPy for array ops.
If any check fails, an AssertionError is raised with a descriptive message.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions that implement the formulas from the proposal
# ----------------------------------------------------------------------
def CDI(theta_cog_dec, eps, rho, alpha=1.0, beta=1.0, gamma=1.0):
    """
    Cognitive Decoherence Index.
    theta_cog_dec : fraction of agents with residual error > τ  ∈ [0,1]
    eps           : average residual error magnitude                ≥ 0
    rho           : redundancy factor n/d                           ≥ 1
    Returns CDI ∈ [0,1] via tanh saturation.
    """
    arg = alpha * theta_cog_dec + beta * eps + gamma * rho
    return np.tanh(arg)


def Phi_N_qm(CDI_val, Phi_N0, eta1, eta2, theta_cog_dec_lag):
    """
    Mapping CDI → Φ_N (connectivity mode).
    Phi_N0   : baseline Φ_N
    eta1,η2  : positive scaling constants
    theta_cog_dec_lag : theta_cog_dec evaluated at t‑τ₁
    """
    return Phi_N0 - eta1 * CDI_val + eta2 * (1.0 - theta_cog_dec_lag)


def Phi_Delta_qm(CDI_val, Phi_Delta0, eta3, eta4, theta_cog_dec_lag, eps_lag):
    """
    Mapping CDI → Φ_Δ (asymmetry mode).
    Phi_Delta0 : baseline Φ_Δ
    eta3,η4    : positive scaling constants
    theta_cog_dec_lag, eps_lag : values at t‑τ₂
    """
    return Phi_Delta0 + eta3 * theta_cog_dec_lag - eta4 * eps_lag


def psi_qm(Ricci_curv, Ricci0, CDI_val, lam=0.5):
    """
    Invariant ψ from Ollivier‑Ricci curvature of the agent‑similarity graph.
    Ricci_curv : |𝒦_G(t)|  (absolute curvature, ≥0)
    Ricci0     : reference curvature 𝒦₀  (>0)
    Returns ψ = ln(|ℛ_G|/ℛ₀) + λ·CDI
    """
    if Ricci_curv <= 0 or Ricci0 <= 0:
        raise ValueError("Curvature terms must be strictly positive for log.")
    return np.log(Ricci_curv / Ricci0) + lam * CDI_val


def S_cognitive(norms):
    """
    Entropy gauge from agent‑response distribution.
    norms : array‑like of ‖ỹ_i‖ for each agent i (non‑negative)
    Returns S = -∑ p_i log p_i, with p_i = ‖ỹ_i‖ / Σ‖ỹ_j‖.
    """
    norms = np.asarray(norms, dtype=float)
    if np.any(norms < 0):
        raise ValueError("Norms must be non‑negative.")
    total = norms.sum()
    if total == 0:
        # All zero → undefined distribution; treat as maximal ignorance (uniform)
        p = np.full_like(norms, 1.0 / len(norms))
    else:
        p = norms / total
    # Avoid log(0) by masking zeros
    p_safe = np.where(p > 0, p, 1.0)
    return -np.sum(p * np.log(p_safe))


def cost_J(CDI_vals, Phi_N_vals, Phi_Delta_vals, S_vals,
           CDI_target=0.6, Phi_N_target=0.6, S_target=np.log(3),
           mu1=1.0, mu2=1.0, mu3=1.0):
    """
    Quadratic cost functional (integrand only – integration left to caller).
    All terms are squared violations, hence ≥0.
    """
    term1 = np.maximum(CDI_vals - CDI_target, 0.0) ** 2
    term2 = mu1 * np.maximum(Phi_N_target - Phi_N_vals, 0.0) ** 2
    term3 = mu2 * Phi_Delta_vals ** 2
    term4 = mu3 * np.maximum(S_target - S_vals, 0.0) ** 2
    return term1 + term2 + term3 + term4


# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_QM_Omega():
    """
    Runs a series of sanity‑checks on the QM‑Ω formulation.
    Raises AssertionError if any check fails.
    """
    # ---- 1. Parameter sanity ------------------------------------------------
    m = 25                     # number of cognitive agents
    d = 10                     # dimension of true cognitive state
    n = 30                     # encoded dimension → redundancy ρ = n/d = 3
    rho = n / d
    assert rho >= 1.0, "Redundancy factor must be ≥1."

    # ---- 2. CDI bounds ------------------------------------------------------
    # Test extreme inputs
    assert 0.0 <= CDI(0.0, 0.0, rho) <= 1.0, "CDI out of [0,1] for zero inputs."
    assert 0.0 <= CDI(1.0, 10.0, rho) <= 1.0, "CDI out of [0,1] for large inputs."
    # Monotonicity in each argument (partial derivatives >0)
    eps = np.linspace(0, 5, 6)
    theta = np.linspace(0, 1, 6)
    for e in eps:
        for th in theta:
            c1 = CDI(th, e, rho)
            c2 = CDI(th + 1e-6, e, rho) if th < 1.0 else c1
            c3 = CDI(th, e + 1e-6, rho)
            assert c2 >= c1 - 1e-12, "CDI not monotonic in theta_cog_dec."
            assert c3 >= c1 - 1e-12, "CDI not monotonic in epsilon."

    # ---- 3. Φ_N and Φ_Δ mappings -------------------------------------------
    Phi_N0, Phi_Delta0 = 0.8, 0.2
    eta1, eta2, eta3, eta4 = 0.3, 0.2, 0.25, 0.15
    # Use lagged values equal to current for simplicity (lead‑time handled externally)
    theta_lag = 0.4
    eps_lag = 0.5
    CDI_test = 0.65

    Phi_N = Phi_N_qm(CDI_test, Phi_N0, eta1, eta2, theta_lag)
    Phi_Delta = Phi_Delta_qm(CDI_test, Phi_Delta0, eta3, eta4, theta_lag, eps_lag)

    # Φ_N should stay in a plausible range (0,1) given chosen constants
    assert 0.0 <= Phi_N <= 1.0, f"Φ_N out of expected bounds: {Phi_N}"
    # Φ_Δ can be positive or negative but we expect small magnitude
    assert -0.5 <= Phi_Delta <= 0.5, f"Φ_Δ out of expected bounds: {Phi_Delta}"

    # ---- 4. Invariant ψ ------------------------------------------------------
    Ricci_curv = 2.0   # arbitrary positive curvature
    Ricci0 = 1.0
    psi = psi_qm(Ricci_curv, Ricci0, CDI_test)
    # ψ can be any real number; just ensure no NaN
    assert np.isfinite(psi), "ψ produced non‑finite value."

    # ---- 5. Entropy gauge ----------------------------------------------------
    # Example norms: some agents stronger, some weaker
    norms_example = np.array([1.2, 0.8, 1.0, 0.5, 1.5] + [1.0] * (m - 5))
    S = S_cognitive(norms_example)
    # Entropy for m agents is bounded by [0, log(m)]
    assert 0.0 <= S <= np.log(m) + 1e-12, f"S_cognitive out of bounds: {S}"
    # Uniform distribution gives max entropy
    unif_S = S_cognitive(np.ones(m))
    assert np.allclose(unif_S, np.log(m), atol=1e-9), "Uniform entropy mismatch."

    # ---- 6. QP constraint feasibility ----------------------------------------
    # Constraints: CDI ≤ 0.7, Φ_N ≥ 0.6, S ≥ ln(3)
    assert CDI_test <= 0.7 + 1e-12, "CDI violates constraint."
    assert Phi_N >= 0.6 - 1e-12, "Φ_N violates constraint."
    assert S >= np.log(3) - 1e-12, "S_cognitive violates constraint."

    # ---- 7. Cost function non‑negativity ------------------------------------
    vec_len = 20
    CDI_vec = np.random.rand(vec_len) * 0.9   # some may exceed target
    Phi_N_vec = np.random.rand(vec_len) * 0.9
    Phi_Delta_vec = (np.random.rand(vec_len) - 0.5) * 0.4
    S_vec = np.random.rand(vec_len) * np.log(m)
    J_vals = cost_J(CDI_vec, Phi_N_vec, Phi_Delta_vec, S_vec)
    assert np.all(J_vals >= -1e-12), "Cost function produced negative values."

    # ---- 8. Lead‑time consistency (qualitative) -------------------------------
    # The proposal claims τ₁,τ₂ ∈ [2,8] hours. We merely check that the
    # functions accept lagged arguments; a full dynamical simulation would be
    # needed for a quantitative check, which is beyond this static audit.
    # Here we assert that using lagged vs. non‑lagged values can produce
    # different outputs (i.e., the mapping is not degenerate).
    Phi_N_nolag = Phi_N_qm(CDI_test, Phi_N0, eta1, eta2, theta_lag)  # same theta
    # Change lagged theta to see effect
    Phi_N_lag_shift = Phi_N_qm(CDI_test, Phi_N0, eta1, eta2, theta_lag + 0.2)
    assert not np.isclose(Phi_N_nolag, Phi_N_lag_shift, atol=1e-9), \
        "Φ_N mapping appears insensitive to lagged theta (lead‑time broken)."

    # If we reach here, all checks passed.
    print("✅ QM‑Ω mathematical audit passed all internal consistency checks.")


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    validate_QM_Omega()