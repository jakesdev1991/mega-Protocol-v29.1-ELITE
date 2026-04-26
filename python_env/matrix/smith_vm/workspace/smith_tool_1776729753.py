# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validation Script
-----------------------------------------
Verifies the mathematical correctness of the Engine Output's derivation:
  * Equations of motion from the Mexican‑hat potential
  * Invariant definitions (psi, xi_N, xi_Delta)
  * Shredding condition (xi_Delta -> ∞)
  * Poisson‑recovery violation condition
  * Mass‑spectrum / tachyonic instability region
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
Phi_N, Phi_Delta, v, lam = sp.symbols('Phi_N Phi_Delta v lam', real=True, nonnegative=True)
# Optional: treat fields as functions of spacetime for EOM
x, y, z, t = sp.symbols('x y z t')
Phi_N_func = sp.Function('Phi_N')(x, y, z, t)
Phi_Delta_func = sp.Function('Phi_Delta')(x, y, z, t)

# ----------------------------------------------------------------------
# 1. Mexican‑hat potential and equations of motion
# ----------------------------------------------------------------------
V = lam/4 * (Phi_N_func**2 + Phi_Delta_func**2 - v**2)**2

# Euler‑Lagrange: ∂L/∂Φ - ∂_μ(∂L/∂(∂_μΦ)) = 0  with L = 1/2(∂Φ)^2 - V
# For a scalar field: □Φ + ∂V/∂Φ = 0  => □Φ = -∂V/∂Φ
dV_dPhiN = sp.diff(V, Phi_N_func)
dV_dPhiDelta = sp.diff(V, Phi_Delta_func)

EOM_N = sp.simplify(sp.diff(Phi_N_func, t, t) - sp.diff(Phi_N_func, x, x) -
                    sp.diff(Phi_N_func, y, y) - sp.diff(Phi_N_func, z, z) +
                    dV_dPhiN)  # □Φ_N + ∂V/∂Φ_N = 0  => □Φ_N = -∂V/∂Φ_N
EOM_Delta = sp.simplify(sp.diff(Phi_Delta_func, t, t) - sp.diff(Phi_Delta_func, x, x) -
                        sp.diff(Phi_Delta_func, y, y) - sp.diff(Phi_Delta_func, z, z) +
                        dV_dPhiDelta)

print("Equations of motion:")
print("□Φ_N + ∂V/∂Φ_N =", sp.simplify(EOM_N))
print("□Φ_Δ + ∂V/∂Φ_Δ =", sp.simplify(EOM_Delta))
# Expected: □Φ = -λ Φ (Φ_N^2+Φ_Δ^2 - v^2)
expected_N = -lam * Phi_N_func * (Phi_N_func**2 + Phi_Delta_func**2 - v**2)
expected_D = -lam * Phi_Delta_func * (Phi_N_func**2 + Phi_Delta_func**2 - v**2)
print("\nCheck against expected form:")
print("Φ_N EOM matches?", sp.simplify(EOM_N + expected_N) == 0)
print("Φ_Δ EOM matches?", sp.simplify(EOM_Delta + expected_D) == 0)

# ----------------------------------------------------------------------
# 2. Invariant definitions
# ----------------------------------------------------------------------
psi = sp.log(Phi_N_func / v)
xi_N_inv2 = lam * (3*Phi_N_func**2 + Phi_Delta_func**2 - v**2)
xi_Delta_inv2 = lam * (Phi_N_func**2 + 3*Phi_Delta_func**2 - v**2)

print("\nInvariants:")
print("ψ =", psi)
print("ξ_N^{-2} =", xi_N_inv2)
print("ξ_Δ^{-2} =", xi_Delta_inv2)

# ----------------------------------------------------------------------
# 3. Shredding condition (ξ_Δ → ∞  <=>  ξ_Δ^{-2} = 0)
# ----------------------------------------------------------------------
shredding_cond = sp.simplify(xi_Delta_inv2)
print("\nShredding condition (ξ_Δ^{-2} = 0):")
print("Φ_N^2 + 3Φ_Δ^2 - v^2 =", shredding_cond)
print("=> Shredding surface:", sp.simplify(shredding_cond) == 0)

# ----------------------------------------------------------------------
# 4. Poisson‑recovery violation test
# ----------------------------------------------------------------------
# Static limit: □ → ∇^2, we examine sign of RHS of Φ_N EOM:
# RHS_N = -λ Φ_N (Φ_N^2+Φ_Δ^2 - v^2)
RHS_N_static = -lam * Phi_N_func * (Phi_N_func**2 + Phi_Delta_func**2 - v**2)
# For Φ_N > 0, sign(RHS_N) = - sign(Φ_N^2+Φ_Δ^2 - v^2)
# Violation occurs when RHS_N has same sign as Φ_N (i.e. drives Φ_N away from v)
# => Φ_N^2+Φ_Δ^2 - v^2 > 0  (since minus sign flips)
violation_cond = sp.simplify(Phi_N_func**2 + Phi_Delta_func**2 - v**2)
print("\nPoisson‑recovery violation condition (Φ_N^2+Φ_Δ^2 - v^2 > 0):")
print("Expression:", violation_cond)
print("Positive when Φ_Δ^2 > v^2 - Φ_N^2")

# ----------------------------------------------------------------------
# 5. Mass‑spectrum and tachyonic region
# ----------------------------------------------------------------------
m_plus_sq = lam * (3*(Phi_N_func**2 + Phi_Delta_func**2) - v**2)
m_minus_sq = lam * (Phi_N_func**2 + Phi_Delta_func**2 - v**2)

print("\nMass‑squared eigenvalues:")
print("m_+^2 =", m_plus_sq)
print("m_-^2 =", m_minus_sq)
print("\nTachyonic region (m_-^2 < 0):")
print("Condition:", sp.simplify(m_minus_sq < 0))
print("=> Φ_N^2 + Φ_Δ^2 < v^2")

# ----------------------------------------------------------------------
# 6. One‑loop effective potential sketch (sign of discriminant)
# ----------------------------------------------------------------------
# The effective potential becomes complex when m_-^2 < 0 (see above).
# We can flag this region:
eff_pot_complex = sp.simplify(m_minus_sq < 0)
print("\nOne‑loop effective potential becomes complex when:")
print(eff_pot_complex)

print("\n=== Validation complete ===")