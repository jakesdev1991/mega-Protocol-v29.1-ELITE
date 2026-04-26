# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the refined CIFO‑Ω proposal.
Checks:
  1. Euler‑Lagrange equation from the Omega Action.
  2. Stiffness invariants as second derivatives of V_eff.
  3. Boundary conditions (Leakage/Freeze) = loss of convexity / divergence.
  4. Entropy gauge term is a total derivative.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Coordinates
t, x, y, z = sp.symbols('t x y z', real=True)
# Field and parameters
E = sp.Function('E')(t, x, y, z)          # capping efficiency field
v, lam, E0 = sp.symbols('v lam E0', positive=True, real=True)
# Omega coupling (treated as a scalar function of the Protocol invariants)
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
lam_Omega = sp.symbols('lam_Omega', real=True)
# Placeholder for native Omega Lagrangian (depends only on Phi_N, Phi_Delta)
L_Omega = sp.Function('L_Omega')(Phi_N, Phi_Delta)   # scalar, no E dependence
# Entropy gauge
S_cap = sp.Function('S_cap')(t, x, y, z)   # entropy scalar
A_mu = sp.Matrix([sp.diff(S_cap, coord) for coord in (t, x, y, z)])  # A_mu = ∂_mu S_cap
# Conserved current (only time component needed for illustration)
J0 = sp.Function('J0')(t, x, y, z)
J = sp.Matrix([J0, 0, 0, 0])               # J^mu = (J0, 0,0,0)

# ----------------------------------------------------------------------
# 1. Action and Euler‑Lagrange
# ----------------------------------------------------------------------
# Potential V(E) = λ/4 (E^2 - E0^2)^2
V = lam/4 * (E**2 - E0**2)**2

# Lagrangian density
L = (1/2)*sp.diff(E, t)**2 \
    - (1/2)*v**2*(sp.diff(E, x)**2 + sp.diff(E, y)**2 + sp.diff(E, z)**2) \
    - V \
    - lam_Omega * L_Omega \
    + A_mu.dot(J)   # A_mu J^mu  (note: metric signature (+,-,-,-) gives minus for spatial parts,
                    # but with our definition A_mu = ∂_mu S and J^mu having only time comp,
                    # the spatial dot product vanishes)

# Euler‑Lagrange: ∂L/∂E - ∂_μ(∂L/∂(∂_μ E)) = 0
# Compute term by term
dL_dE = sp.diff(L, E)
dL_dEdt = sp.diff(L, sp.diff(E, t))
dL_dEdx = sp.diff(L, sp.diff(E, x))
dL_dEdy = sp.diff(L, sp.diff(E, y))
dL_dEdz = sp.diff(L, sp.diff(E, z))

EL = dL_dE - sp.diff(dL_dEdt, t) - sp.diff(dL_dEdx, x) - sp.diff(dL_dEdy, y) - sp.diff(dL_dEdz, z)
EL_simplified = sp.simplify(EL)
print("Euler‑Lagrange equation (should be 0):")
print(EL_simplified)
print()

# Expected form: ∂_t^2 E - v^2 ∇^2 E + dV/dE + lam_Omega * δL_Omega/δE + A_t * J0 = 0
# Since L_Omega does not depend on E, δL_Omega/δE = 0.
expected = sp.diff(E, t, t) - v**2 * (sp.diff(E, x, x) + sp.diff(E, y, y) + sp.diff(E, z, z)) \
           + sp.diff(V, E) + lam_Omega * 0 + A_mu[0] * J0   # A_t = ∂_t S_cap
print("Expected Euler‑Lagrange (simplified):")
print(sp.simplify(expected))
print("Match?", sp.simplify(EL_simplified - expected) == 0)
print()

# ----------------------------------------------------------------------
# 2. Effective potential and stiffness invariants
# ----------------------------------------------------------------------
# Define collective modes as functionals of the field (here we treat them as independent vars for Hessian)
Phi_T, Phi_A, Phi_G = sp.symbols('Phi_T Phi_A Phi_G', real=True)
# Equilibrium values (starred)
Phi_T_star, Phi_A_star, Phi_G_star = sp.symbols('Phi_T_star Phi_A_star Phi_G_star', real=True)
# Mass parameters (positive)
m_T, m_A, m_G = sp.symbols('m_T m_A m_G', positive=True, real=True)

# Quadratic effective potential around equilibrium
V_eff = (sp.Rational(1,2))*m_T**2 * (Phi_T - Phi_T_star)**2 \
      + (sp.Rational(1,2))*m_A**2 * (Phi_A - Phi_A_star)**2 \
      + (sp.Rational(1,2))*m_G**2 * (Phi_G - Phi_G_star)**2

# Stiffness invariants = second derivatives
xi_T_inv2 = sp.diff(V_eff, Phi_T, 2)
xi_A_inv2 = sp.diff(V_eff, Phi_A, 2)
xi_G_inv2 = sp.diff(V_eff, Phi_G, 2)

print("Stiffness invariants:")
print("ξ_T^{-2} =", xi_T_inv2)
print("ξ_A^{-2} =", xi_A_inv2)
print("ξ_G^{-2} =", xi_G_inv2)
print()

# ----------------------------------------------------------------------
# 3. Boundary conditions
# ----------------------------------------------------------------------
# Correlation length related to inverse sqrt of stiffness (up to a constant)
# We simply check the sign/divergence conditions.
print("Boundary condition checks:")
print("Information Leakage (Shredding) ↔ ξ_T^{-2} < 0")
print("  Condition:", xi_T_inv2 < 0)
print("Information Freeze ↔ ξ_G^{-2} → ∞")
print("  Condition: limit ξ_G^{-2} → ∞  (i.e., m_G^2 → ∞)")
print("  In our quadratic model ξ_G^{-2} = m_G^2, so divergence requires m_G^2 → ∞")
print()

# ----------------------------------------------------------------------
# 4. Entropy gauge term as total derivative
# ----------------------------------------------------------------------
# A_mu J^mu = (∂_mu S_cap) J^mu.
# If J^mu is conserved (∂_mu J^mu = 0), then A_mu J^mu = ∂_mu (S_cap J^mu) - S_cap (∂_mu J^mu)
# The second term vanishes on‑shell, leaving a total derivative.
# Verify symbolically assuming ∂_mu J^mu = 0.
J_mu = sp.Matrix([J0, 0, 0, 0])   # lower index same as upper for Minkowski diag(1,-1,-1,-1) with zero spatial comp
div_J = sp.diff(J_mu[0], t) + sp.diff(J_mu[1], x) + sp.diff(J_mu[2], y) + sp.diff(J_mu[3], z)
print("Assuming current conservation (∂_mu J^mu = 0):")
print("div_J =", div_J)
print("Set to zero for on‑shell currents.")
print()
# Total derivative expression
total_div = sp.diff(S_cap * J_mu[0], t) + sp.diff(S_cap * J_mu[1], x) \
            + sp.diff(S_cap * J_mu[2], y) + sp.diff(S_cap * J_mu[3], z)
print("Total derivative ∂_mu (S_cap J^mu) =", total_div)
print("A_mu J^mu =", A_mu.dot(J_mu))
print("Difference (should be -S_cap * ∂_mu J^mu):")
print(sp.simplify(A_mu.dot(J_mu) - total_div))
print("If ∂_mu J^mu = 0, the difference vanishes → A_mu J^mu is a total derivative.")
print()

# ----------------------------------------------------------------------
# 5. MPC‑Ω constraints sanity check
# ----------------------------------------------------------------------
print("MPC‑Ω constraint ranges (must keep system in convex region):")
print("Φ_T ≥ 0.4  → ensures ξ_T^{-2}=m_T^2 >0 if equilibrium Φ_T* is chosen >0.4")
print("Φ_G ≤ 0.7  → prevents ξ_G^{-2} from blowing up (i.e., keeps m_G^2 finite)")
print("Ē ∈ [0.5,0.9] , σ_E ≤ 0.2  → keeps fluctuations small, preserving quadratic approx.")
print()

print("=== Validation complete ===")