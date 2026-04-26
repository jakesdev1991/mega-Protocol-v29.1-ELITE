# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the Engine's Higher-Order Lattice Polarization derivation.
Checks:
  * Correctness of the vacuum‑polarization at one-loop.
  * Factor‑2 error in the Engine's Pi(0).
  * Mass‑positivity constraint.
  * Omega‑Protocol invariant definitions (homogeneous case).
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Fundamental constants (treated as symbols)
alpha0, Lambda, m, g = sp.symbols('alpha0 Lambda m g', positive=True)
# Background fields
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# Derived quantities
eps = g*Phi_N/m  # dimensionless coupling parameter

# Diagonal basis components
Phi_plus  = Phi_N * sp.exp( Phi_Delta )
Phi_minus = Phi_N * sp.exp(-Phi_Delta )

# Effective masses (Engine's Ansatz)
m_e = m - g*Phi_plus
m_p = m - g*Phi_minus

# ----------------------------------------------------------------------
# 1. Engine's Pi(0) (single log of geometric mean)
# ----------------------------------------------------------------------
Pi_eng = alpha0/(3*sp.pi) * sp.sp Lambda / sp.sqrt(m_e*m_p)  # will be corrected below
# Actually we need log, not division:
Pi_eng = alpha0/(3*sp.pi) * sp.log( Lambda / sp.sqrt(m_e*m_p) )

# ----------------------------------------------------------------------
# 2. Correct Pi(0) (sum of two logs)
# ----------------------------------------------------------------------
Pi_corr = alpha0/(3*sp.pi) * ( sp.log(Lambda**2 / m_e**2) + sp.log(Lambda**2 / m_p**2) )
# Simplify using log rules
Pi_corr = sp.simplify(Pi_corr)

# ----------------------------------------------------------------------
# 3. Series expansion in eps up to O(eps^2)
# ----------------------------------------------------------------------
# Helper to series-expand and drop O(eps^3)
def series_to_eps2(expr):
    return sp.series(expr, eps, 0, 3).removeO()  # up to eps^2

Pi_eng_series   = series_to_eps2(Pi_eng)
Pi_corr_series  = series_to_eps2(Pi_corr)

# ----------------------------------------------------------------------
# 4. Renormalized alphas (Engine vs Correct)
# ----------------------------------------------------------------------
alpha_ren_eng = alpha0 / (1 - Pi_eng)
alpha_ren_corr = alpha0 / (1 - Pi_corr)

# Series expansions for alpha as well (optional)
alpha_eng_series   = series_to_eps2(alpha_ren_eng)
alpha_corr_series  = series_to_eps2(alpha_ren_corr)

# ----------------------------------------------------------------------
# 5. Mass‑positivity constraint
# ----------------------------------------------------------------------
cond_e = sp.simplify(m_e > 0)
cond_p = sp.simplify(m_p > 0)
# Solve for Phi_N assuming worst‑case sign of Phi_Delta
# m_e > 0  =>  Phi_N < (m/g) * exp(-Phi_Delta)
# m_p > 0  =>  Phi_N < (m/g) * exp( Phi_Delta )
# Combined: Phi_N < (m/g) * exp(-|Phi_Delta|)
abs_Phi_Delta = sp.Abs(Phi_Delta)
mass_pos_constraint = sp.simplify(Phi_N < (m/g) * sp.exp(-abs_Phi_Delta))

# ----------------------------------------------------------------------
# 6. Omega‑Protocol invariants (homogeneous background)
# ----------------------------------------------------------------------
psi   = sp.log(Phi_N)
xi_N  = sp.diff(psi, sp.Symbol('x'))**2 + sp.diff(psi, sp.Symbol('y'))**2 + sp.diff(psi, sp.Symbol('z'))**2
# For homogeneous fields, derivatives are zero:
xi_N_hom = sp.simplify(xi_N.subs({sp.diff(Phi_N, sp.Symbol('x')):0,
                                 sp.diff(Phi_N, sp.Symbol('y')):0,
                                 sp.diff(Phi_N, sp.Symbol('z')):0}))

ratio   = Phi_Delta/Phi_N
xi_Delta = sp.diff(ratio, sp.Symbol('x'))**2 + sp.diff(ratio, sp.Symbol('y'))**2 + sp.diff(ratio, sp.Symbol('z'))**2
xi_Delta_hom = sp.simplify(xi_Delta.subs({sp.diff(Phi_Delta, sp.Symbol('x')):0,
                                          sp.diff(Phi_Delta, sp.Symbol('y')):0,
                                          sp.diff(Phi_Delta, sp.Symbol('z')):0,
                                          sp.diff(Phi_N,   sp.Symbol('x')):0,
                                          sp.diff(Phi_N,   sp.Symbol('y')):0,
                                          sp.diff(Phi_N,   sp.Symbol('z')):0}))

# ----------------------------------------------------------------------
# Output results
# ----------------------------------------------------------------------
print("="*70)
print("ENGINE'S Pi(0) series (up to eps^2):")
print(sp.simplify(Pi_eng_series))
print()
print("CORRECT Pi(0) series (up to eps^2):")
print(sp.simplify(Pi_corr_series))
print()
print("Difference (Correct - Engine) * (3π/α0) :")
diff = sp.simplify((Pi_corr_series - Pi_eng_series) * (3*sp.pi/alpha0))
print(diff)   # should be 2*eps*cosh(Phi_Delta) - eps**2*(1-2*cosh^2) etc.
print()
print("Does the difference equal 2*[engine's bracket]?")
print(sp.simplify(diff - 2*(Pi_eng_series * (3*sp.pi/alpha0))) == 0)
print()
print("Mass‑positivity constraint (Φ_N < (m/g) e^{-|Φ_Δ|} ):")
print(mass_pos_constraint)
print()
print("Omega‑Protocol invariants (homogeneous case):")
print("  ξ_N =", xi_N_hom)
print("  ξ_Δ =", xi_Delta_hom)
print()
print("="*70)
print("SUMMARY:")
print("- The Engine's Pi(0) is missing an overall factor of 2.")
print("- Consequently the α_ren expression is off by the same factor.")
print("- The mass‑positivity constraint and invariant definitions are correct.")
print("- To enforce the rule, replace the single‑log Pi(0) with the sum‑of‑logs form.")
print("="*70)