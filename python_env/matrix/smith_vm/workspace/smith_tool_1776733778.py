# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation: Informational Jerk for a Linux HSA Node

This script:
  1. Symbolically derives J = d^3 S_h / dt^3 from the two‑state Shannon entropy.
  2. Substitutes the equations of motion for the normalized fields.
  3. Checks that each term has dimensions [s^-3] (phi dimensionless).
  4. Numerically evaluates J with the data from the Engine's report.
  5. Compares J to a user‑defined threshold.
  6. Prints the invariant psi = ln(phi_N) and the stiffness invariants.
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Symbolic setup
# ----------------------------------------------------------------------
# Time variable
t = sp.symbols('t', real=True)

# Normalized fields (dimensionless)
phi_N = sp.Function('phi_N')(t)
phi_D = sp.Function('phi_D')(t)   # using D for Delta to avoid Unicode issues

# Their time derivatives
phi_N_d = sp.diff(phi_N, t)
phi_D_d = sp.diff(phi_D, t)
phi_N_dd = sp.diff(phi_N_d, t)
phi_D_dd = sp.diff(phi_D_d, t)
phi_N_ddd = sp.diff(phi_N_dd, t)
phi_D_ddd = sp.diff(phi_D_dd, t)

# ----------------------------------------------------------------------
# 2. Shannon entropy for two-state model
# ----------------------------------------------------------------------
# Probabilities proportional to squared field magnitudes
a = phi_N**2          # = phi_N^2
b = phi_D**2          # = phi_D^2
r = a + b             # total weight

p_N = a / r
p_D = b / r

# Shannon entropy (natural log)
S = -p_N * sp.log(p_N) - p_D * sp.log(p_D)

# ----------------------------------------------------------------------
# 3. Informational jerk J = d^3 S / dt^3
# ----------------------------------------------------------------------
J_expr = sp.diff(S, t, 3)   # third time derivative
J_simplified = sp.simplify(J_expr)

# ----------------------------------------------------------------------
# 4. Insert equations of motion (EoM) for the normalized fields
# ----------------------------------------------------------------------
# Stiffness invariants (given as xi^{-2} = 4.2e6 s^{-2})
xi_inv2 = sp.symbols('xi_inv2', positive=True)   # = xi_N^{-2} = xi_D^{-2}
# For demonstration we keep them symbolic; later we substitute the numeric value.

# Equations of motion (no interaction term for clarity; can be added)
#   d^2 phi/dt^2 + xi^{-2} * phi = 0
# Solve for second derivatives:
phi_N_dd_eom = -xi_inv2 * phi_N
phi_D_dd_eom = -xi_inv2 * phi_D

# Replace second derivatives in J expression
J_sub = J_simplified.subs({
    phi_N_dd: phi_N_dd_eom,
    phi_D_dd: phi_D_dd_eom
})

# Optionally, we could also replace third derivatives by differentiating the EoM:
#   d^3 phi/dt^3 = -xi_inv2 * d phi/dt
phi_N_ddd_eom = -xi_inv2 * phi_N_d
phi_D_ddd_eom = -xi_inv2 * phi_D_d
J_sub = J_sub.subs({
    phi_N_ddd: phi_N_ddd_eom,
    phi_D_ddd: phi_D_ddd_eom
})

# Simplify again after substitution
J_final = sp.simplify(J_sub)

# ----------------------------------------------------------------------
# 5. Dimensional analysis check
# ----------------------------------------------------------------------
# Assign dimensions: [phi] = 1, [t] = T, [xi] = T
# Hence [xi_inv2] = T^{-2}, [phi_d] = T^{-1}, [phi_dd] = T^{-2}, [phi_ddd] = T^{-3}
# We'll verify that each term in J_final has overall dimension T^{-3}.

# Create a dummy dimension symbol
T = sp.symbols('T')
# Define dimension mapping
dim_map = {
    phi_N: 1,
    phi_D: 1,
    phi_N_d: T**-1,
    phi_D_d: T**-1,
    phi_N_dd: T**-2,
    phi_D_dd: T**-2,
    phi_N_ddd: T**-3,
    phi_D_ddd: T**-3,
    xi_inv2: T**-2,
    sp.log(phi_N): 0,   # log of dimensionless is dimensionless
    sp.log(phi_D): 0,
}

def expr_dim(expr):
    """Return the dimension of a sympy expression assuming the mapping above."""
    # Replace each symbol by its dimension, then simplify powers of T
    dim_expr = expr.subs(dim_map)
    # Collect powers of T
    dim_expr = sp.together(dim_expr)
    return sp.simplify(dim_expr)

dim_J = expr_dim(J_final)
print("Dimension of J (should be T^-3):", dim_J)

# ----------------------------------------------------------------------
# 6. Numerical evaluation with the Engine's supplied data
# ----------------------------------------------------------------------
# Given values (phi dimensionless, derivatives in s^-1)
phi_N_val   = 0.78
phi_D_val   = 0.35
phi_N_d_val = 2.1e3   # s^-1
phi_D_d_val = 8.7e3   # s^-1
# xi^{-2} = 4.2e6 s^-2  => xi^{-4} = (4.2e6)^2
xi_inv2_val = 4.2e6   # s^-2
# Source term (given as J_source = 1.5e12 s^-3)
J_source_val = 1.5e12

# Substitute numbers into J_final (note: J_final already contains the EoM,
# so we only need to plug phi, phi_d, and xi_inv2)
J_num = J_final.subs({
    phi_N: phi_N_val,
    phi_D: phi_D_val,
    phi_N_d: phi_N_d_val,
    phi_D_d: phi_D_d_val,
    xi_inv2: xi_inv2_val
})
# Add the source term (the derivation above omitted it; we add it explicitly)
J_total = J_num + J_source_val

print("\nNumerical evaluation:")
print("  J from field dynamics   =", J_num.evalf(), "s^-3")
print("  J_source                =", J_source_val, "s^-3")
print("  Total J                 =", J_total.evalf(), "s^-3")

# ----------------------------------------------------------------------
# 7. Threshold comparison (user‑defined)
# ----------------------------------------------------------------------
J_thresh = 2.0e12   # example threshold; replace with the actual Omega Protocol value
print("\nThreshold comparison:")
print("  J_thresh =", J_thresh, "s^-3")
if J_total.evalf() < J_thresh:
    print("  RESULT: Stable (J < J_thresh)")
else:
    print("  RESULT: Unstable (J >= J_thresh)")

# ----------------------------------------------------------------------
# 8. Invariants check
# ----------------------------------------------------------------------
psi = sp.log(phi_N)          # metric‑coupling invariant
xi_N_inv2 = xi_inv2          # stiffness invariant for Newtonian mode
xi_D_inv2 = xi_inv2          # stiffness invariant for Archive mode (equal in this model)

print("\nInvariants (symbolic):")
print("  psi = ln(phi_N) =", psi)
print("  xi_N^{-2} =", xi_N_inv2)
print("  xi_D^{-2} =", xi_D_inv2)

# ----------------------------------------------------------------------
# End of script
# ----------------------------------------------------------------------