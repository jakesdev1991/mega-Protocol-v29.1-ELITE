# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ω‑Protocol Validation for the Omega‑Psych‑Theorist thought.
Checks:
  • Φ_N : Normalization of the intent state.
  • Φ_Δ : Non‑degeneracy of the decision metric after regularization.
  • J*  : Conservation of the probability current (∇_μ J^μ = 0).
Assumes:
  • |Ψ_intent> is a normalized ket in a finite‑dimensional Hilbert space.
  • M_rule is a Hermitian operator (rule filter).
  • Ξ_rule ≥ 0 is a scalar stiffness parameter.
  • The decision manifold metric g is perturbed by Ξ_rule·M_rule†M_rule.
  • Stabilization operator R_reg is a metric‑compatible, unitary connection.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbolic definitions
# ----------------------------------------------------------------------
dim = sp.Symbol('dim', integer=True, positive=True)  # Hilbert space dimension
i, j = sp.symbols('i j', integer=True, nonnegative=True)

# Basis kets |e_i>
e = sp.MatrixSymbol('e', dim, 1)  # placeholder; we treat inner products abstractly

# Intent state |Ψ_intent> = Σ c_i |e_i>
c = sp.MatrixSymbol('c', dim, 1)  # complex coefficients
Psi = e  # we will work with the coefficient vector c directly

# Normalization condition (Φ_N)
norm_cond = sp.simplify(c.H * c - 1)  # should be zero

# Rule operator M_rule (Hermitian)
M = sp.MatrixSymbol('M', dim, dim)
herm_cond = sp.simplify(M - M.H)  # should be zero matrix

# Stiffness scalar (real, non‑negative)
Xi = sp.Symbol('Xi', real=True)
stiff_cond = sp.And(Xi >= 0, sp.im(Xi) == 0)

# Decision manifold metric g0 (background, assumed non‑degenerate)
g0 = sp.MatrixSymbol('g0', dim, dim)
# Assume g0 is symmetric positive‑definite for simplicity
g0_sym = sp.simplify(g0 - g0.T)  # symmetry
g0_pos = sp.MatrixSymbol('g0_pos', dim, dim)  # placeholder for PD check

# Perturbation due to rule stiffness: δg = Xi * M† M
delta_g = Xi * (M.H * M)
g = g0 + delta_g  # full metric

# Metric degeneracy condition (Φ_Δ): det(g) = 0 <=> degeneracy
det_g = g.det()
# We require that for *any* Xi >= 0, det(g) ≠ 0 unless Xi exceeds a critical bound.
# For validation we enforce that the background metric is PD and that
# the perturbation cannot zero‑out the determinant for small Xi.
# We'll check the first‑order condition: d/dXi det(g) at Xi=0 must be zero only if M†M has zero eigen.
# Simpler: enforce that M†M is positive semidefinite (so Xi·M†M only adds PSD term).
Psd_cond = sp.simplify(M.H * M)  # should be PSD; we check eigenvalues symbolically via principal minors later.

# Stabilization operator R_reg: we model as a covariant derivative
# ∇_μ = ∂_μ + Γ_μ, with Γ_μ = - (1/2) g^{-1} (∂_μ g)  (Levi‑Civita)
# For matrix case we use: Γ = -1/2 * g^{-1} * dg/dXi (since only Xi varies)
# We'll compute the connection and test metric compatibility: ∇_λ g_μν = 0
# In symbolic matrix form:
g_inv = g.inv()  # assumes invertible; will fail if degenerate -> caught by Φ_Δ
# Derivative of g w.r.t Xi:
dg_dXi = M.H * M
Gamma = -sp.Rational(1, 2) * g_inv * dg_dXi

# Metric compatibility condition: ∇_λ g = 0  <=>  dg/dXi + [Γ, g] = 0
# Since Γ depends on Xi only via g_inv, we compute:
compat = sp.simplify(dg_dXi + Gamma * g - g * Gamma)  # should be zero matrix

# Current conservation (J*): J^μ = <Ψ| γ^μ |Ψ> ; ∇_μ J^μ = 0
# For simplicity we adopt a single gamma matrix γ = Identity (so J = <Ψ|Ψ> = 1)
# Then conservation reduces to d/dXi (<Ψ|Ψ>) = 0.
# Since we enforce normalization (Φ_N) and R_reg is unitary, this holds.
# We'll explicitly check that R_reg preserves norm:
# R_reg = exp(-i * theta * Gamma)  (unitary if Gamma Hermitian)
theta = sp.Symbol('theta', real=True)
R_reg = sp.exp(-sp.I * theta * Gamma)  # matrix exponential
norm_after = sp.simplify((Psi.H * R_reg.H * R_reg * Psi) - (Psi.H * Psi))
# Should be zero if R_reg is unitary (R_reg.H * R_reg = I)

# ----------------------------------------------------------------------
# Numeric sanity check (random matrices) to catch symbolic oversights
# ----------------------------------------------------------------------
np.random.seed(42)
n = 4  # test dimension

def rand_herm():
    A = np.random.randn(n, n) + 1j * np.random.randn(n, n)
    return A + A.conj().T

def rand_vec():
    v = np.random.randn(n) + 1j * np.random.randn(n)
    v /= np.linalg.norm(v)
    return v.reshape(-1, 1)

M_num = rand_herm()
c_num = rand_vec()
g0_num = np.eye(n) + 0.1 * rand_herm()  # make SPD
Xi_num = max(0.0, np.random.randn())  # enforce non‑negative

# Φ_N
assert np.vdot(c_num.ravel(), c_num.ravel()).real == 1.0, "Φ_N failed: state not normalized"

# Hermiticity
assert np.allclose(M_num, M_num.conj().T), "M_rule not Hermitian"

# Stiffness
assert Xi_num >= 0, "Xi_rule negative"

# Metric PD check (background)
eigvals = np.linalg.eigvalsh(0.5*(g0_num + g0_num.T))
assert np.all(eigvals > 0), "Background metric not positive‑definite"

# Perturbed metric
g_num = g0_num + Xi_num * (M_num.conj().T @ M_num)
eigvals_g = np.linalg.eigvalsh(0.5*(g_num + g_num.T))
assert np.all(eigvals_g > -1e-12), "Metric became degenerate or non‑PD (Φ_Δ violation)"

# Connection metric compatibility (numeric)
g_inv_num = np.linalg.inv(g_num)
dg_dXi_num = M_num.conj().T @ M_num
Gamma_num = -0.5 * g_inv_num @ dg_dXi_num
compat_num = dg_dXi_num + Gamma_num @ g_num - g_num @ Gamma_num
assert np.allclose(compat_num, 0, atol=1e-10), "Metric compatibility failed (∇g ≠ 0)"

# Unitarity of R_reg (small angle approximation)
theta_num = 0.1
R_reg_num = scipy.linalg.expm(-1j * theta_num * Gamma_num)
unitary_check = R_reg_num.conj().T @ R_reg_num
assert np.allclose(unitary_check, np.eye(n), atol=1e-8), "R_reg not unitary (norm not preserved)"

print("All Ω‑Protocol invariants satisfied for random test instance.")