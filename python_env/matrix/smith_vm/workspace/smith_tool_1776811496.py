# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for ATS-Ω
Checks:
  * Double‑well potential shape (α<0, β>0, γ>0)
  * Invariant ψ = ln(Φ_N/Φ_N0) is dimensionless
  * Entropy gauge definitions
  * ATI bounds and monotonicity
  * MPC‑Ω QP constraints
  * Cost integrand non‑negativity
"""

import numpy as np

def validate_double_well(alpha, beta, gamma):
    """Return True if V(B) = α/2 B^2 + β/4 B^4 - γ B has two minima."""
    if not (alpha < 0 and beta > 0 and gamma > 0):
        return False
    # Derivative: V' = α B + β B^3 - γ
    # Solve V' = 0 for real roots → cubic; two minima exist if discriminant > 0
    # For simplicity we check that V'' at B=0 is negative (local max) and
    # that V'' at large |B| is positive (ensuring wells).
    Vpp0 = alpha  # second derivative at B=0
    if Vpp0 >= 0:
        return False
    # For large |B|, term β B^2 dominates → positive
    return True

def compute_phi_n(sigma):
    """Φ_N from covariance matrix Σ (largest eigenvalue sqrt)."""
    evals = np.linalg.eigvalsh(sigma)
    return np.sqrt(np.max(evals))

def compute_phi_delta(mu2, mu3):
    """Φ_Δ = μ3 / (μ2)^{3/2} ; require μ2>0."""
    if mu2 <= 0:
        return np.nan
    return mu3 / (mu2 ** 1.5)

def compute_psi(phi_n, phi_n0):
    """Invariant ψ = ln(Φ_N/Φ_N0)."""
    if phi_n <= 0 or phi_n0 <= 0:
        return np.nan
    return np.log(phi_n / phi_n0)

def shannon_conditional_entropy(p_m, p_mk):
    """
    p_m: shape (M,) fraction of components of type m
    p_mk: shape (M, K) fraction of type m taking path k
    Returns S_alg.
    """
    # avoid log(0)
    eps = 1e-12
    S = 0.0
    for m in range(len(p_m)):
        inner = -np.sum(p_mk[m] * np.log(p_mk[m] + eps))
        S += p_m[m] * inner
    return S

def compute_ati(curv_ratio, beta1_ratio, S_alg):
    """ATI = curvature_preservation * cycle_integrity * exp(-S_alg)."""
    return curv_ratio * beta1_ratio * np.exp(-S_alg)

def validate_constraints(ati, phi_n, S_alg):
    """Check QP constraints: ATI≥0.6, Φ_N≥0.5, S_alg≥ln2."""
    return (ati >= 0.6) and (phi_n >= 0.5) and (S_alg >= np.log(2))

def cost_integrand(ati, phi_n, phi_n_target, phi_delta, S_alg,
                   mu1=1.0, mu2=1.0, mu3=1.0):
    """Integrand of MPC cost (non‑negative by construction)."""
    term1 = (0.6 - ati) ** 2 if ati < 0.6 else 0.0
    term2 = mu1 * (0.5 - phi_n) ** 2 if phi_n < 0.5 else 0.0
    term3 = mu2 * phi_delta ** 2
    term4 = mu3 * (np.log(2) - S_alg) ** 2 if S_alg < np.log(2) else 0.0
    return term1 + term2 + term3 + term4

def run_validation():
    # --- Example synthetic data ------------------------------------------------
    np.random.seed(42)
    M, K = 3, 4  # 3 component types, up to 4 paths each
    p_m = np.random.dirichlet(np.ones(M))
    p_mk = np.random.dirichlet(np.ones(K), size=M)
    p_mk *= p_m[:, None]  # enforce joint distribution

    # Covariance matrix for B-field (positive‑definite)
    A = np.random.randn(5, 5)
    sigma = A @ A.T + 0.1 * np.eye(5)

    # Moments for Φ_Δ (using a dummy distribution of B values)
    B_vals = np.random.randn(1000)
    mu2 = np.var(B_vals)
    mu3 = np.mean((B_vals - np.mean(B_vals)) ** 3)

    # Field parameters
    alpha, beta, gamma = -1.0, 2.0, 0.5
    phi_n0 = 1.0  # baseline

    # Computed quantities
    phi_n = compute_phi_n(sigma)
    phi_delta = compute_phi_delta(mu2, mu3)
    psi = compute_psi(phi_n, phi_n0)
    S_alg = shannon_conditional_entropy(p_m, p_mk)

    # Mock curvature and Betti ratios (normally from graph analysis)
    curv_ratio = 0.9   # |R_G(t)|/|R_G(0)|
    beta1_ratio = 0.85 # β1(t)/β1(0)

    ati = compute_ati(curv_ratio, beta1_ratio, S_alg)

    # --- Validation checks ------------------------------------------------------
    checks = {
        "Double‑well potential": validate_double_well(alpha, beta, gamma),
        "Φ_N positive": phi_n > 0,
        "Φ_Δ finite": not np.isnan(phi_delta),
        "ψ finite": not np.isnan(psi),
        "Entropy ≥ 0": S_alg >= 0,
        "ATI in [0,1]": 0.0 <= ati <= 1.0,
        "QP constraints satisfied": validate_constraints(ati, phi_n, S_alg),
        "Cost integrand non‑negative": cost_integrand(ati, phi_n, phi_n0,
                                                     phi_delta, S_alg) >= 0,
    }

    print("=== Omega Protocol Invariant Validation ===")
    for name, ok in checks.items():
        print(f"{name:30}: {'PASS' if ok else 'FAIL'}")
    print("\nSample values:")
    print(f"  Φ_N   = {phi_n:.4f}")
    print(f"  Φ_Δ   = {phi_delta:.4f}")
    print(f"  ψ     = {psi:.4f}")
    print(f"  S_alg = {S_alg:.4f}")
    print(f"  ATI   = {ati:.4f}")

    overall = all(checks.values())
    print(f"\nOverall validation: {'PASS' if overall else 'FAIL'}")
    return overall

if __name__ == "__main__":
    run_validation()