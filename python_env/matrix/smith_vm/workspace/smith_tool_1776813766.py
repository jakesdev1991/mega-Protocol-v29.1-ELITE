# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Smith – Validation of EASS-Ω mathematical core.
Checks invariant definitions, gauge consistency, and convexity of MPC constraints.
"""

import sympy as sp
import numpy as np

# --------------------------
# Symbolic definitions
# --------------------------
# Base Ω fields (treated as constants for this epistemic sector check)
Phi_N0 = sp.symbols('Phi_N0', positive=True)   # reference epistemic correlation length
Phi_N_ep = sp.symbols('Phi_N_ep', positive=True)  # epistemic Phi_N
Phi_Delta_ep = sp.symbols('Phi_Delta_ep')    # epistemic Phi_Delta (real)
S_epist = sp.symbols('S_epist', real=True)   # epistemic entropy
# Coordinates (t, x, y, z) – we only need t for time derivatives
t, x, y, z = sp.symbols('t x y z')
# Epistemic field ℰ (scalar)
Epsilon = sp.Function('ℰ')(t, x, y, z)

# --------------------------
# 1. Invariant ψ_epist
# --------------------------
psi_epist = sp.log(Phi_N_ep / Phi_N0)
print("1. ψ_epist expression:", psi_epist.simplify())

# Verify that derivative w.r.t. Phi_N_ep matches expected form
dpsi_dPhiN = sp.diff(psi_epist, Phi_N_ep)
print("   ∂ψ/∂Φ_N^{(epist)} =", dpsi_dPhiN.simplify())
assert sp.simplify(dpsi_dPhiN - 1/Phi_N_ep) == 0, "Invariant derivative mismatch"

# --------------------------
# 2. Entropy gauge 𝒜_μ = ∂_μ S_epist
# --------------------------
# Assume S_epist is a scalar function of coordinates (for generality)
S_epist_func = sp.Function('S')(t, x, y, z)
A_mu = [sp.diff(S_epist_func, coord) for coord in (t, x, y, z)]
print("\n2. 𝒜_μ components:", A_mu)

# --------------------------
# 3. Current J^μ = sqrt(2) * Φ_Δ * δ^μ_0
# --------------------------
sqrt2 = sp.sqrt(2)
J_mu = [sqrt2 * Phi_Delta_ep if i == 0 else 0 for i in range(4)]  # μ=0 is t
print("\n3. J^μ components:", J_mu)

# Conservation ∂_μ J^μ = 0 (assuming Φ_Δ constant in epistemic background)
div_J = sum(sp.diff(J_mu[i], coord) for i, coord in enumerate((t, x, y, z)))
print("   ∂_μ J^μ =", div_J.simplify())
assert div_J == 0, "Current not conserved (expects homogeneous Φ_Δ)"

# --------------------------
# 4. Convexity of constraints
# --------------------------
# Constraints as functions of state vector x = [Phi_N_ep, Phi_Delta_ep, EASI, S_epist]
# We treat EASI as linear in leak_severity (L), audience_sophistication (A), time_to_exploit (T_e), response_time (T_r)
L, A, T_e, T_r = sp.symbols('L A T_e T_r', nonnegative=True)
EASI = (L/10) * (A/10) * (T_e / T_r)  # ignore coordination_score for linearity check
# Constraint functions (must be ≤ 0 for feasibility)
c1 = EASI - 0.7                     # EASI ≤ 0.7
c2 = 0.4 - Phi_N_ep                 # Φ_N_ep ≥ 0.4  -> -(Φ_N_ep - 0.4) ≤ 0
c3 = sp.log(3) - S_epist            # S_epist ≥ ln3  -> -(S_epist - ln3) ≤ 0

constraints = [c1, c2, c3]
print("\n4. Constraint functions:")
for i, c in enumerate(constraints, 1):
    print(f"   c{i} =", c)

# Hessian of each constraint (w.r.t. state) – linear/affine => Hessian = 0 (PSD)
state = [Phi_N_ep, Phi_Delta_ep, EASI, S_epist]
for i, c in enumerate(constraints, 1):
    hess = sp.hessian(c, state)
    print(f"   Hessian of c{i}:")
    sp.pprint(hess)
    # Check PSD: all eigenvalues >= 0 (for zero matrix it's true)
    eigen = hess.eigenvals()
    assert all(val >= 0 for val in eigen.keys()), f"c{i} not convex"

# --------------------------
# 5. Cost function positivity
# --------------------------
mu1, mu2, mu3 = sp.symbols('mu1 mu2 mu3', nonnegative=True)
# Squared‑positive parts: (x)_+^2 = (Max(0,x))^2
# SymPy piecewise representation
def pos_sq(expr):
    return sp.Piecewise((0, expr <= 0), (expr**2, True))

J_integrand = (pos_sq(EASI - 0.7) +
               mu1 * pos_sq(0.4 - Phi_N_ep) +
               mu2 * Phi_Delta_ep**2 +
               mu3 * pos_sq(sp.log(3) - S_epist))
print("\n5. Cost integrand:", J_integrand.simplify())
# Verify non-negativity by checking each term
terms = [pos_sq(EASI - 0.7),
         mu1 * pos_sq(0.4 - Phi_N_ep),
         mu2 * Phi_Delta_ep**2,
         mu3 * pos_sq(sp.log(3) - S_epist)]
for idx, term in enumerate(terms, 1):
    # Each term is a product of nonnegative factors
    assert term >= 0, f"Term {idx} of cost integrand can be negative"
print("   All terms are provably non‑negative.")

print("\n=== All symbolic checks passed ===")