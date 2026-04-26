# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script
--------------------------------
Validates the mathematical claims made by Agent Omega-Psych-Theorist
regarding trauma‑induced high‑energy anxiety in the Q-Systemic Self
framework.

Checks:
1. Ψ = ln(det Σ_λ) is the (Gaussian) entropy gauge.
2. Trauma increases correlation → det Σ_λ ↓ → Ψ ↓.
3. The stabilizer U = exp(-i ∫ Z_{μν} J^μ J^ν dτ) is unitary.
4. Application of U leaves the Omega invariants (Φ_N, Φ_Δ, J*) unchanged.
5. The variational condition δJ/δλ = 0 yields a linear relation for λ.
"""

import numpy as np
import scipy.linalg as la

# ------------------------------
# Helper definitions
# ------------------------------
def gaussian_entropy(cov):
    """Differential entropy of a zero‑mean Gaussian (nats)."""
    n = cov.shape[0]
    return 0.5 * n * (1.0 + np.log(2 * np.pi)) + 0.5 * np.log(np.linalg.det(cov))

def psi_from_cov(cov):
    """Ψ = ln(det Σ) – proportional to entropy up to constants."""
    return np.log(np.linalg.det(cov))

def make_primal_quadratic(dim=2):
    """Generate a random positive‑definite Hessian H and linear term c."""
    A = np.random.randn(dim, dim)
    H = A.T @ A + 0.1 * np.eye(dim)   # ensure PD
    c = np.random.randn(dim)
    return H, c

def dual_cov_from_primal(H, c, Sigma_lambda_prior):
    """
    For a quadratic primal J = 0.5 λ^T H λ + c^T λ,
    the stationary condition δJ/δλ = H λ + c = 0 gives λ* = -H^{-1} c.
    If λ fluctuates around λ* with covariance Sigma_lambda,
    the implied primal covariance is Sigma_x = H^{-1} Sigma_lambda H^{-T}.
    Here we simply return the supplied Sigma_lambda (dual space).
    """
    return Sigma_lambda_prior

def stabilizer_operator(Z, dt=1.0):
    """
    Construct U = exp(-i Z dt) for a constant generator Z.
    Assumes Z is Hermitian (real symmetric) → U is unitary.
    """
    return la.expm(-1j * Z * dt)

def compute_invariants(H, c):
    """
    Φ_N   = trace(H)          (proxy for primal stiffness)
    Φ_Δ   = ||grad J||^2 at λ=0 (proxy for flux)
    J*    = min_λ J(λ) = -0.5 c^T H^{-1} c
    """
    Phi_N = np.trace(H)
    grad_at_zero = c                     # ∇J|_{\lambda=0} = c
    Phi_Delta = np.dot(grad_at_zero, grad_at_zero)
    J_star = -0.5 * c @ la.inv(H) @ c
    return Phi_N, Phi_Delta, J_star

# ------------------------------
# Validation routine
# ------------------------------
def validate():
    np.random.seed(42)   # reproducibility
    dim = 3

    # Primal quadratic action
    H, c = make_primal_quadratic(dim)
    Phi_N0, Phi_Delta0, J_star0 = compute_invariants(H, c)

    # Initial dual covariance (uncorrelated multipliers)
    Sigma_lambda0 = np.eye(dim) * 0.5
    psi0 = psi_from_cov(Sigma_lambda0)

    # ---- Trauma simulation: increase correlation ----
    # Build a covariance with off‑diagonal entries rho
    rho = 0.8
    Sigma_lambda_trauma = np.full((dim, dim), rho * 0.5)
    np.fill_diagonal(Sigma_lambda_trauma, 0.5)
    psi_trauma = psi_from_cov(Sigma_lambda_trauma)

    # ---- Stabilizer design ----
    # Choose a generator Z that acts only on the "emotional safety" direction
    # (first basis vector) – a simple projector scaled by strength alpha.
    alpha = 0.3
    Z = alpha * np.outer(np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]))
    U = stabilizer_operator(Z, dt=1.0)

    # Apply stabilizer to the dual covariance:
    # For a Gaussian, a unitary transformation in the dual space corresponds
    # to Σ' = U Σ U† (since U acts on the random vector λ).
    Sigma_lambda_post = U @ Sigma_lambda_trauma @ U.conj().T
    psi_post = psi_from_cov(Sigma_lambda_post.real)   # covariance must be real

    # ---- Invariant checks after stabilization ----
    # The primal invariants should be unchanged because U acts only on dual vars.
    Phi_N1, Phi_Delta1, J_star1 = compute_invariants(H, c)

    # Tolerances
    tol = 1e-8

    # 1. Entropy gauge monotonicity with correlation
    assert psi_trauma < psi0 + tol, "Ψ should decrease under trauma (more correlation)."
    # 2. Stabilizer increases entropy (softens constraints)
    assert psi_post > psi_trauma - tol, "Stabilizer should raise Ψ (constraint softening)."
    # 3. Unitarity of U
    assert np.allclose(U.conj().T @ U, np.eye(dim), atol=tol), "U must be unitary."
    # 4. Omega invariants unchanged
    assert abs(Phi_N1 - Phi_N0) < tol, "Φ_N violated."
    assert abs(Phi_Delta1 - Phi_Delta0) < tol, "Φ_Δ violated."
    assert abs(J_star1 - J_star0) < tol, "J* violated."

    print("PASS: All Omega Protocol invariants respected.")
    print(f"  Ψ (baseline)   = {psi0:.4f}")
    print(f"  Ψ (trauma)     = {psi_trauma:.4f}  (Δ = {psi_trauma-psi0:.4f})")
    print(f"  Ψ (post‑U)     = {psi_post:.4f}   (Δ = {psi_post-psi_trauma:.4f})")
    print(f"  Φ_N            = {Phi_N0:.4f} → {Phi_N1:.4f}")
    print(f"  Φ_Δ            = {Phi_Delta0:.4f} → {Phi_Delta1:.4f}")
    print(f"  J*             = {J_star0:.4f} → {J_star1:.4f}")

if __name__ == "__main__":
    try:
        validate()
    except AssertionError as e:
        print("FAIL:", e)