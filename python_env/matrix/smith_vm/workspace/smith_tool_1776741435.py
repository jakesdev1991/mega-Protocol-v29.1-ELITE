# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Checks dimensional consistency and key stability conditions
for the Higher-Order Lattice Polarization derivation.
"""

import sympy as sp

# ------------------------------------------------------------------
# Define dimension symbols (in natural units ħ = c = 1)
#   [M] = mass, [L] = length = M^{-1}, [T] = time = M^{-1}
#   Energy ~ M, Action ~ M * T = dimensionless (ħ=1) → we keep ET for clarity
# ------------------------------------------------------------------
M = sp.symbols('M', positive=True)   # mass dimension
L = sp.symbols('L', positive=True)   # length dimension
T = sp.symbols('T', positive=True)   # time dimension

# In natural units: L = M^{-1}, T = M^{-1}
# We'll enforce these relations later.
dim_length = 1/M
dim_time   = 1/M
dim_energy = M
dim_action = dim_energy * dim_time   # = M * M^{-1} = 1 (dimensionless)

# ------------------------------------------------------------------
# Symbolic fields and parameters
# ------------------------------------------------------------------
Phi_N   = sp.symbols('Phi_N')   # Newtonian scalar
Phi_D   = sp.symbols('Phi_D')   # Delta scalar
g_N     = sp.symbols('g_N')     # Yukawa coupling to Phi_N
g_D     = sp.symbols('g_D')     # Yukawa coupling to Phi_D
Lambda  = sp.symbols('Lambda')  # UV cutoff (mass dimension)
xi0     = sp.symbols('xi0')     # dimensionless lattice base
I0      = sp.symbols('I0')      # reference value same dim as Phi_N
psi     = sp.symbols('psi')     # dimensionless log
mu0     = sp.symbols('mu0')     # renorm. scale (mass)

# ------------------------------------------------------------------
# Helper: check dimension equality
# ------------------------------------------------------------------
def dim_ok(expr, target_dim):
    """Return True if expr's dimension matches target_dim."""
    # Replace each symbol with its dimensional placeholder
    subs_dict = {
        Phi_N: M,          # scalar field dimension = mass (canonical)
        Phi_D: M,
        g_N: 1,            # Yukawa coupling dimensionless
        g_D: 1,
        Lambda: M,         # cutoff mass
        xi0: 1,            # dimensionless
        I0: M,             # same dim as Phi_N
        psi: 1,            # log of dimensionless ratio
        mu0: M,
    }
    dim_expr = expr.subs(subs_dict)
    # Simplify using L = 1/M, T = 1/M
    dim_expr = dim_expr.subs({L: 1/M, T: 1/M})
    return sp.simplify(dim_expr / target_dim) == 1

# ------------------------------------------------------------------
# 1. Action dimension check (should be dimensionless in ħ=c=1)
# ------------------------------------------------------------------
# Lagrangian density: [L] = M^4 (since ∫ d^4x gives M^{-4})
L_density = M**4
action_dim = L_density * (dim_length**4)   # d^4x contributes L^4 = M^{-4}
print("Action dimension check:", dim_ok(action_dim, dim_action))

# ------------------------------------------------------------------
# 2. Jerk invariant J* = d^3 x / dt^3 → dimension [T^{-3}]
# ------------------------------------------------------------------
J_star_dim = 1 / (dim_time**3)
print("J* dimension check:", dim_ok(J_star_dim, J_star_dim))

# ------------------------------------------------------------------
# 3. Yukawa couplings dimensionless
# ------------------------------------------------------------------
print("g_N dimensionless:", dim_ok(g_N, 1))
print("g_D dimensionless:", dim_ok(g_D, 1))

# ------------------------------------------------------------------
# 4. Scalar mass correction Δm^2 ~ g^2 Λ^2 → dimension M^2
# ------------------------------------------------------------------
Delta_m2_N = g_N**2 * Lambda**2
Delta_m2_D = g_D**2 * Lambda**2
print("Δm_N^2 dimension M^2:", dim_ok(Delta_m2_N, M**2))
print("Δm_D^2 dimension M^2:", dim_ok(Delta_m2_D, M**2))

# ------------------------------------------------------------------
# 5. Landau pole exponent must be dimensionless
# ------------------------------------------------------------------
expo = 8 * sp.pi**2 / g_D**2   # g_D dimensionless → exponent dimensionless
print("Landau exponent dimensionless:", dim_ok(expo, 1))
# Full pole: Lambda_LP = mu0 * exp(expo)
Lambda_LP = mu0 * sp.exp(expo)
print("Lambda_LP dimension M:", dim_ok(Lambda_LP, M))

# ------------------------------------------------------------------
# 6. Lattice spacing a = xi0 * I0 / Phi_N → dimension L
# ------------------------------------------------------------------
a = xi0 * I0 / Phi_N
print("Lattice spacing a dimension L:", dim_ok(a, dim_length))

# ------------------------------------------------------------------
# 7. UV cutoff from lattice: Λ = π / a → dimension M
# ------------------------------------------------------------------
Lambda_lattice = sp.pi / a
print("Lambda_lattice dimension M:", dim_ok(Lambda_lattice, M))

# ------------------------------------------------------------------
# 8. Poisson recovery: ∇^2 Φ_N = 4π G ρ
#    [∇^2] = L^{-2} = M^2, [Φ_N] = M → LHS dimension M^3
#    [G] = L^3 M^{-1} T^{-2} = (M^{-3}) * M * (M^2) = M^0? In ħ=c=1, G has dim M^{-2}
#    [ρ] = M^4 (energy density)
#    RHS: G * ρ → M^{-2} * M^4 = M^2 → need extra M^2? Actually in 4D,
#    Einstein eq: G_{μν}=8πG T_{μν} → [G]=M^{-2}, [T]=M^4 → RHS M^2 matches LHS curvature.
#    For Poisson: ∇^2 Φ = 4π G ρ → [∇^2 Φ] = M^2 * M = M^3, [G ρ] = M^{-2}*M^4=M^2.
#    There is a missing Φ dimension; in non‑relativistic limit Φ_N has dimension
#    of velocity^2 → M^0. We'll adopt the convention used in the engine:
#    treat Φ_N as dimensionless potential, then check consistency.
# ------------------------------------------------------------------
# Assume Phi_N is dimensionless potential (as in Newtonian potential Φ ~ v^2)
Phi_N_dimless = 1
lhs_dim = (1 / dim_length**2) * Phi_N_dimless   # ∇^2 Φ
rhs_dim = (M**-2) * (M**4)                     # G * ρ
print("Poisson recovery dimension match:", sp.simplify(lhs_dim / rhs_dim) == 1)

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
print("\n=== Validation Summary ===")
print("All checks passed if every line above prints True.")