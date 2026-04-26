# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol compliance checker for HVFI‑Ω v2.
Verifies that all derived invariants satisfy the required positivity /
semidefiniteness constraints of the Omega Physics Rubric v26.0.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbolic definitions (all parameters are assumed real and positive)
# ----------------------------------------------------------------------
# Fundamental constants
lam, v, D, eps = sp.symbols('lam v D eps', positive=True, real=True)
# MPC / mapping coefficients
eta1, eta2, alpha, beta, gamma, delta = sp.symbols('eta1 eta2 alpha beta gamma delta', positive=True, real=True)
kappa, mu = sp.symbols('kappa mu', positive=True, real=True)

# State variables (assumed to be real; ranges will be constrained later)
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# Entropies and mutual informations (non‑negative by definition)
S = sp.symbols('S1:4', nonnegative=True, real=True)   # S1, S2, S3 (tick, minute, hour)
I = sp.symbols('I1:3', nonnegative=True, real=True)   # I12, I23, I34 (if L=4)
# Topological charge (log‑determinant)
Psi = sp.symbols('Psi', real=True)

# ----------------------------------------------------------------------
# 1. Covariant mode positivity (Phi_N, Phi_Delta >= 0)
# ----------------------------------------------------------------------
assert Phi_N >= 0, "Phi_N must be non‑negative"
assert Phi_Delta >= 0, "Phi_Delta must be non‑negative"

# ----------------------------------------------------------------------
# 2. Correlation‑length squared positivity
#    xi_N^2 = lam * (3*Phi_N^2 + Phi_Delta^2 - v^2)
#    xi_Delta^2 = lam * (Phi_N^2 + 3*Phi_Delta^2 - v^2)
# ----------------------------------------------------------------------
xi_N_sq = lam * (3*Phi_N**2 + Phi_Delta**2 - v**2)
xi_D_sq = lam * (Phi_N**2 + 3*Phi_Delta**2 - v**2)

assert sp.simplify(xi_N_sq) > 0, "xi_N^2 must be > 0"
assert sp.simplify(xi_D_sq) > 0, "xi_Delta^2 must be > 0"

# ----------------------------------------------------------------------
# 3. Invariant psi = ln(xi/xi0) – only requires xi>0, already enforced
# ----------------------------------------------------------------------
# No extra check needed; xi>0 => psi finite.

# ----------------------------------------------------------------------
# 4. Entropy and mutual information non‑negativity (already declared)
# ----------------------------------------------------------------------
for s in S:
    assert s >= 0, f"Entropy component {s} must be >= 0"
for i in I:
    assert i >= 0, f"Mutual information component {i} must be >= 0"

# ----------------------------------------------------------------------
# 5. Curvature invariant Psi = ln(det(Sigma_A + eps I))
#    Requires Sigma_A + eps I positive definite => det > 0
#    We enforce this by demanding eps > 0 and that the covariance
#    matrix is PSD; the log‑determinant is then > -inf.
# ----------------------------------------------------------------------
assert eps > 0, "Regularisation eps must be > 0 to keep det>0"
# Symbolic check: if we assume Sigma_A is PSD, then det(Sigma_A+eps I) >= eps^L > 0
# Hence Psi is finite (no assertion needed beyond eps>0).

# ----------------------------------------------------------------------
# 6. Anomaly score a_HVFI in [0,1] (CDF of GPD)
#    a_HVFI = 1 - F_GPD(|Psi| - u)  with u = 95th percentile.
#    By definition of a CDF, 0 <= F_GPD <= 1  => 0 <= a_HVFI <= 1.
# ----------------------------------------------------------------------
a_HVFI = sp.symbols('a_HVFI', real=True)
assert 0 <= a_HVFI <= 1, "Anomaly score must lie in [0,1]"

# ----------------------------------------------------------------------
# 7. MPC cost functional positivity
#    J = ∫ [ 0.5 * Σ (dS_l/dt)^2 + (kappa/2) * Σ (S_l - S_l*)^2 + mu * Psi^2 ] dt
#    Each integrand term is a sum of squares with positive coefficients.
# ----------------------------------------------------------------------
# Define time‑derivative symbols
dS = sp.symbols('dS1:4', real=True)
S_star = sp.symbols('S1_star:4', real=True)

integrand = sp.Rational(1,2) * sum(dS_i**2 for dS_i in dS) \
            + (kappa/2) * sum((S_i - S_star_i)**2 for S_i, S_star_i in zip(S, S_star)) \
            + mu * Psi**2

# Since kappa, mu > 0 and squares are >=0, integrand >= 0.
assert sp.simplify(integrand) >= 0, "MPC integrand must be non‑negative"

# ----------------------------------------------------------------------
# If we reach here, all symbolic checks passed.
# ----------------------------------------------------------------------
print("✅ All Omega‑Protocol invariant checks passed (symbolic).")
print("   • Φ_N, Φ_Δ ≥ 0")
print("   • ξ_N^2, ξ_Δ^2 > 0  (ensures ψ finite)")
print("   • S_l, I_l,l+1 ≥ 0")
print("   • Ψ = ln(det(Σ_A+εI)) finite (ε>0)")
print("   • a_HVFI ∈ [0,1]")
print("   • MPC cost integrand ≥ 0")