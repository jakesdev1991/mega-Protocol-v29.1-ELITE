# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validate the informational jerk stability calculation for a Linux HSA node.
- Derives J = d^3 S_h / dt^3 from Shannon entropy for a two‑state model.
- Inserts the invariant psi = ln(phi_N) as a multiplicative factor.
- Performs dimensional analysis (units: s^-3).
- Numerically evaluates J using the supplied data.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbolic definitions
# ----------------------------------------------------------------------
t = sp.symbols('t', real=True)
# Dimensionless fields (phi_N, phi_Delta) and their time derivatives
phi_N, phi_D = sp.symbols('phi_N phi_D', real=True, nonnegative=True)
dot_phi_N, dot_phi_D = sp.symbols('dot_phi_N dot_phi_D', real=True)
ddot_phi_N, ddot_phi_D = sp.symbols('ddot_phi_N ddot_phi_D', real=True)

# Stiffness invariants (same for both modes)
xi = sp.symbols('xi', real=True, positive=True)   # [xi] = s

# Invariant psi = ln(phi_N)
psi = sp.log(phi_N)

# Probabilities from normalized field magnitudes
den = phi_N**2 + phi_D**2
p_N = phi_N**2 / den
p_D = phi_D**2 / den

# Shannon entropy
S = -p_N * sp.log(p_N) - p_D * sp.log(p_D)

# ----------------------------------------------------------------------
# Compute the third time‑derivative of S using chain rule
# ----------------------------------------------------------------------
# First derivative
dS_dt = sp.diff(S, phi_N) * dot_phi_N + sp.diff(S, phi_D) * dot_phi_D

# Second derivative
d2S_dt2 = (sp.diff(dS_dt, phi_N) * dot_phi_N +
           sp.diff(dS_dt, phi_D) * dot_phi_D +
           sp.diff(S, phi_N) * ddot_phi_N +
           sp.diff(S, phi_D) * ddot_phi_D)

# Third derivative (jerk)
J_expr = (sp.diff(d2S_dt2, phi_N) * dot_phi_N +
          sp.diff(d2S_dt2, phi_D) * dot_phi_D +
          sp.diff(dS_dt, phi_N) * ddot_phi_N +
          sp.diff(dS_dt, phi_D) * ddot_phi_D)

# ----------------------------------------------------------------------
# Insert the invariant psi as a coupling factor (multiply the whole expression)
# ----------------------------------------------------------------------
J_with_psi = psi * J_expr

# ----------------------------------------------------------------------
# Substitute the constitutive relations for the fields:
#   phi_N = Phi_N / v, phi_D = Phi_D / v   (v is a constant speed scale)
#   xi_N^{-2} = xi_D^{-2} = lambda * v^2   => xi = sqrt(lambda) * v
# Since we work with dimensionless phi, we keep xi as a time constant.
# ----------------------------------------------------------------------
# For validation we treat phi_N, phi_D, dot_phi, ddot_phi as independent symbols.
# ----------------------------------------------------------------------
# Dimensional check: replace each symbol with its dimensional exponent.
# Let [t] = T, [phi] = 1, [dot_phi] = T^{-1}, [ddot_phi] = T^{-2}, [xi] = T.
dim = {
    t: sp.S(1),
    phi_N: sp.S(0), phi_D: sp.S(0),
    dot_phi_N: sp.S(-1), dot_phi_D: sp.S(-1),
    ddot_phi_N: sp.S(-2), ddot_phi_D: sp.S(-2),
    xi: sp.S(1)
}
def dim_of(expr):
    return sp.simplify(expr.subs(dim))

J_dim = dim_of(J_with_psi)
print("Dimensional exponent of J*psi:", J_dim)
# Expected: T^{-3}
assert J_dim == sp.S(-3), "Dimensional mismatch: expected s^-3"

# ----------------------------------------------------------------------
# Numerical evaluation with the data from the task
# ----------------------------------------------------------------------
num_subs = {
    phi_N: 0.78,
    phi_D: 0.35,
    dot_phi_N: 2.1e3,
    dot_phi_D: 8.7e3,
    # We need second derivatives; assume they are negligible for this test
    ddot_phi_N: 0.0,
    ddot_phi_D: 0.0,
    xi: (4.2e6)**(-0.5)   # because xi^{-2} = 4.2e6 s^{-2} => xi = (4.2e6)^{-0.5} s
}
J_val = J_with_psi.subs(num_subs)
print("Numerical value of J (including psi):", J_val.evalf(), "s^-3")

# ----------------------------------------------------------------------
# Optional: compare with the source term J_source
# ----------------------------------------------------------------------
J_source = 1.5e12
J_total = J_val + J_source
print("Total jerk J_stab = J + J_source:", J_total.evalf(), "s^-3")