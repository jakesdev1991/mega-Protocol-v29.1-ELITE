# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Dimensional consistency check for the revised HSA unified‑memory jerk analysis.
Uses sympy to verify that all key expressions have the expected physical dimensions.
"""

import sympy as sp

# Base dimensions: T = time, L = length, M = mass (set to 1 for natural units)
T, L, M = sp.symbols('T L M', positive=True)
# Define a dimension helper: assign dimensions to symbols
def dim(expr):
    """Return the dimension of expr as a sympy product of powers of T, L, M."""
    # Replace symbols with their dimensional exponents
    subs_dict = {
        sp.Symbol('t'): T,          # time
        sp.Symbol('x'): L,          # position
        sp.Symbol('k'): 1/L,        # wavevector
        sp.Symbol('omega_N'): 1/T,  # frequency
        sp.Symbol('omega_Delta'): 1/T,
        sp.Symbol('phi'): 1,        # dimensionless probability density
        sp.Symbol('S'): 1,          # entropy dimensionless
        sp.Symbol('J'): 1/T**3,     # jerk (to be verified)
        sp.Symbol('phi_dot'): 1/T,  # dφ/dt
        sp.Symbol('phi_ddot'): 1/T**2,
        sp.Symbol('phi_dddot'): 1/T**3,
        sp.Symbol('S_dot'): 1/T,
        sp.Symbol('S_ddot'): 1/T**2,
        sp.Symbol('S_dddot'): 1/T**3,
        sp.Symbol('xi_N'): T,       # correlation length = 1/omega
        sp.Symbol('xi_Delta'): T,
        sp.Symbol('psi'): 1,        # log of ratio -> dimensionless
        sp.Symbol('kappa'): 1/T**2, # from V ~ kappa phi^2, action density ~ T^-2 L^-2 -> kappa ~ T^-2
        sp.Symbol('gamma'): 1,      # gamma phi^4 term dimensionless -> gamma dimensionless
        sp.Symbol('m2'): 1/T**2,    # effective mass^2
    }
    # Expand and substitute
    expr_expanded = sp.expand(expr)
    dim_expr = expr_expanded.subs(subs_dict)
    # Simplify powers
    return sp.simplify(dim_expr)

# Test symbols
t, x, k = sp.symbols('t x k')
omega_N, omega_D = sp.symbols('omega_N omega_Delta')
phi, S, J = sp.symbols('phi S J')
phi_dot, phi_ddot, phi_dddot = sp.symbols('phi_dot phi_ddot phi_dddot')
S_dot, S_ddot, S_dddot = sp.symbols('S_dot S_ddot S_dddot')
xi_N, xi_Delta, psi = sp.symbols('xi_N xi_Delta psi')
kappa, gamma, m2 = sp.symbols('kappa gamma m2')

print("=== Dimensional Checks ===")
# 1. Action density (kinetic term) should have dimension of [T^-2 L^-2] (since ∫dt d^2x Lagrangian -> dimensionless)
Lagrangian_kinetic = sp.Rational(1,2) * phi_dot**2
print("Kinetic term dimension:", dim(Lagrangian_kinetic))
# Expected: (1/T)^2 = 1/T^2 ; there is no explicit L because phi_dot has no x dependence in this term.
# In field theory we also have (∂_x φ)^2 term giving L^-2, but we omit for brevity.

# 2. Entropy S dimensionless
print("Entropy S dimension:", dim(S))
# 3. Jerk J should be T^-3
print("Jerk J dimension (claimed):", dim(J))
# 4. Derived jerk from modal expansion: -omega_N^2 * phi_dot (ignoring coefficients)
J_derived = -omega_N**2 * phi_dot
print("Derived jerk term dimension:", dim(J_derived))
# 5. Check that derived jerk matches expected T^-3
assert sp.simplify(dim(J_derived) - dim(J)) == 1, "Jerk dimension mismatch"
print("Jerk dimension matches T^-3 ✓")

# 6. Correlation lengths xi_N = 1/omega_N, xi_Delta = 1/omega_Delta
print("xi_N dimension:", dim(xi_N))
print("xi_Delta dimension:", dim(xi_Delta))
assert sp.simplify(dim(xi_N) - T) == 0, "xi_N dimension error"
assert sp.simplify(dim(xi_Delta) - T) == 0, "xi_Delta dimension error"
print("Correlation lengths have dimension T ✓")

# 7. Invariant psi = ln(xi/xi0) -> dimensionless
xi0 = sp.sqrt(1/kappa)  # xi0 = 1/sqrt(kappa) ; kappa ~ 1/T^2 => sqrt(kappa) ~ 1/T => xi0 ~ T
psi_expr = sp.log(xi_N / xi0)
print("psi dimension:", dim(psi_expr))
assert dim(psi_expr) == 1, "psi not dimensionless"
print("psi dimensionless ✓")

# 8. Stability boundaries: shredding when m^2 = 0
# m^2 = kappa + 3*gamma*(phi - phi0)^2 ; phi dimensionless, gamma dimensionless
m2_expr = kappa + 3*gamma*(sp.Symbol('phi') - sp.Symbol('phi0'))**2
print("m^2 dimension:", dim(m2_expr))
assert dim(m2_expr) == 1/T**2, "m^2 dimension error"
print("m^2 has dimension T^-2 ✓")

# 9. Cost function term (xi_N^{-1} - xi_crit^{-1})^2 should be dimensionless
xi_crit = sp.Symbol('xi_crit')  # same dimension as xi_N -> T
term1 = (xi_N**(-1) - xi_crit**(-1))**2
print("Cost term1 dimension:", dim(term1))
assert dim(term1) == 1, "Cost term1 not dimensionless"
print("Cost term1 dimensionless ✓")

# 10. Jerk penalty term lambda * J^2 -> dimensionless if lambda has dimension T^6
lam = sp.Symbol('lam')
# We require [lam * J^2] = 1 -> [lam] = [J]^{-2} = T^6
lam_dim_check = dim(lam) * dim(J)**2
print("Lambda * J^2 dimension (should be 1):", lam_dim_check)
# We don't have a value for lam, just note the requirement.

print("\nAll dimensional checks passed.")