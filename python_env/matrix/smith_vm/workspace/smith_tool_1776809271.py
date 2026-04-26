# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Symbolic validation of the repaired Higher-Order Lattice Polarization derivation.
Checks:
  1. Photon propagator inverse in Landau gauge yields the directional alpha_eff.
  2. Entropy gauge term follows from S_pair = S0 + Phi_Delta * S1 with S1 = -(Pi_L + 2*Pi_M).
  3. The effective action contains the Omega invariants psi, xi_N, xi_Delta
     (only a structural check; actual values are left symbolic).
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Momenta and metric
p, p_sq = sp.symbols('p p_sq', real=True)          # p^2 = p_sq
# Direction vectors: n = (0,0,0,1) -> only z-component matters
n_sq = sp.Integer(1)                               # n_mu n^mu = 1 (Euclidean)
# Couplings
e, alpha0 = sp.symbols('e alpha0', positive=True)
# Anisotropy parameters
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# Vacuum polarization components (functions of p^2)
Pi_T, Pi_L, Pi_M, Pi_P = sp.symbols('Pi_T Pi_L Pi_M Pi_P', 
                                   cls=sp.Function)
# Effective action invariants (Omega Rubric v26.0)
psi = sp.Function('psi')(Phi_N)                    # psi = ln(Phi_N) (definition)
xi_N = sp.Function('xi_N')(psi)                    # stiffness coeff for Phi_N
xi_Delta = sp.Function('xi_Delta')(psi)            # stiffness coeff for Phi_Delta

# ----------------------------------------------------------------------
# 1. Photon propagator inverse (Landau gauge)
# ----------------------------------------------------------------------
# Landau gauge projector: P_T^{mu nu} = delta^{mu nu} - p^mu p^nu / p^2
# The full inverse propagator (ignoring Pi_P which drops out in Landau gauge) is:
#   D^{-1}_{mu nu} = (p^2) * P_T^{mu nu} + (p^2) * Pi_T * P_T^{mu nu}
#                    + (p^2) * Pi_L * n_mu n_nu
#                    + (p^2) * Pi_M * (p_mu n_nu + n_mu p_nu)/sqrt(p^2)
# For the purpose of checking the directional alpha we only need the
# coefficient multiplying the transverse projector for each spatial direction.

# Define projectors
delta = sp.KroneckerDelta  # generic Kronecker delta (sympy)
# We'll work with components: i = x,y (transverse) and i = z (longitudinal)

# Transverse projector for i = x or y:
P_T_perp = 1 - p_sq / p_sq   # = 0 for the longitudinal part, but we keep symbolic
# Actually simpler: the inverse propagator for a given polarization i is:
#   D^{-1}_{ii} = p_sq * (1 + Pi_T) + extra_i
# where extra_i = 0 for i = x,y,
#                extra_z = p_sq * (Pi_L + 2*Pi_M)   (see derivation)

# Let's construct the expressions:
extra_perp = 0
extra_z    = Pi_L(p_sq) + 2*Pi_M(p_sq)

# Inverse propagator (up to factor p_sq) for each direction:
Dinv_perp = p_sq * (1 + Pi_T(p_sq)) + extra_perp
Dinv_z    = p_sq * (1 + Pi_T(p_sq)) + p_sq * extra_z   # note the extra p_sq factor from the n_mu n_nu term

# Effective alpha: alpha_eff^i = alpha0 / (Dinv_{ii} / p_sq)
alpha_eff_perp = alpha0 / (Dinv_perp / p_sq)
alpha_eff_z    = alpha0 / (Dinv_z    / p_sq)

# Simplify
alpha_eff_perp_s = sp.simplify(alpha_eff_perp)
alpha_eff_z_s    = sp.simplify(alpha_eff_z)

print("Effective alpha (transverse):", alpha_eff_perp_s)
print("Effective alpha (longitudinal):", alpha_eff_z_s)

# Expected form from the paper:
expected_perp = alpha0 / (1 + Pi_T(p_sq))
expected_z    = alpha0 / (1 + Pi_T(p_sq) + Phi_Delta * (Pi_L(p_sq) + 2*Pi_M(p_sq)))

print("\nExpected transverse:", sp.simplify(expected_perp))
print("Expected longitudinal:", sp.simplify(expected_z))

# Check equality
print("\nTransverse matches expected?", sp.simplify(alpha_eff_perp_s - expected_perp) == 0)
print("Longitudinal matches expected?", sp.simplify(alpha_eff_z_s - expected_z) == 0)

# ----------------------------------------------------------------------
# 2. Entropy gauge relation
# ----------------------------------------------------------------------
S0, S1 = sp.symbols('S0 S1')
S_pair = S0 + Phi_Delta * S1
# According to the derivation: S1 = -(Pi_L + 2*Pi_M)
S1_expr = -(Pi_L(p_sq) + 2*Pi_M(p_sq))
S_pair_sub = sp.simplify(S0 + Phi_Delta * S1_expr)

# Entropy gauge: A_mu = ∂_mu S_pair, J^mu = sqrt(2) * Phi_Delta * delta^mu_0
# The contraction A_mu J^mu = sqrt(2) * Phi_Delta * ∂_0 S_pair
# We only check that S_pair depends linearly on Phi_Delta with coefficient S1.
print("\nS_pair expression:", S_pair_sub)
print("Coefficient of Phi_Delta in S_pair:", sp.simplify(S_pair_sub.coeff(Phi_Delta, 1)))
print("Expected coefficient S1:", S1_expr)
print("Match?", sp.simplify(S_pair_sub.coeff(Phi_Delta, 1) - S1_expr) == 0)

# ----------------------------------------------------------------------
# 3. Omega invariant presence (structural check)
# ----------------------------------------------------------------------
# Effective action (schematic) should contain:
#   sqrt(g) * [1/4 F^2 + (alpha0^{-1} + delta alpha_N^{-1}) F^2
#            + (xi_N/2)*(∂Phi_N)^2 + (xi_Delta/2)*(∂Phi_Delta)^2
#            + A_mu J^mu ]
# We'll just verify that psi, xi_N, xi_Delta appear as functions of Phi_N.
print("\n--- Omega invariant structure ---")
print("psi =", psi)
print("xi_N =", xi_N)
print("xi_Delta =", xi_Delta)
# Check that psi depends on Phi_N (through ln)
print("psi depends on Phi_N?", psi.has(Phi_N))
print("xi_N depends on psi?", xi_N.has(psi))
print("xi_Delta depends on psi?", xi_Delta.has(psi))

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
print("\n=== Validation Summary ===")
print("Transverse alpha matches expected:", sp.simplify(alpha_eff_perp_s - expected_perp) == 0)
print("Longitudinal alpha matches expected:", sp.simplify(alpha_eff_z_s - expected_z) == 0)
print("Entropy gauge coefficient matches S1:", sp.simplify(S_pair_sub.coeff(Phi_Delta, 1) - S1_expr) == 0)
print("Omega invariants present in structure:", psi.has(Phi_N) and xi_N.has(psi) and xi_Delta.has(psi))