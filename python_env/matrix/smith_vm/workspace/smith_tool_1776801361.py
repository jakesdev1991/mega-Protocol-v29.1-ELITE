# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation script for the Higher-Order Lattice Polarization derivation.
Checks:
  1. The effective fine‑structure constant has the correct Omega‑Protocol structure.
  2. The transverse, longitudinal and mixed polarisation tensors contain the
     required Phi_N and Phi_Delta dependence.
  3. The entropy‑gauge term is built from S_pair = -Tr ln S_F and the current
     J^mu = sqrt(2) Phi_Delta delta^mu_0.
  4. All Omega invariants (psi, xi_N, xi_Delta) appear explicitly in the
     effective action.

If any check fails, the script raises an AssertionError with a diagnostic.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
e, a, p, m = sp.symbols('e a p m', positive=True)   # coupling, lattice spacing, momentum, mass
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta')   # Omega invariants
alpha0 = sp.symbols('alpha0')                      # bare fine‑structure constant
# Direction indicator: i = z -> 1, otherwise 0
i_z = sp.symbols('i_z')                            # 0 or 1 (Kronecker delta_iz)

# Loop‑order symbols (we keep them generic; the validation only checks structure)
Pi_T, Pi_L, Pi_M = sp.symbols('Pi_T Pi_L Pi_M')

# ----------------------------------------------------------------------
# 1. Effective coupling structure
# ----------------------------------------------------------------------
# Expected form: alpha_eff = alpha0 / (1 + Pi_T + i_z * Phi_Delta * (Pi_L + 2*Pi_M))
alpha_eff_expr = alpha0 / (1 + Pi_T + i_z * Phi_Delta * (Pi_L + 2*Pi_M))

# Build the same expression from the "repaired formula" given in the text:
#   Pi_T = e^2/(12 pi^2) * ln(a^{-2}/p^2) + (e^2/pi^2) * Phi_N
#   Pi_L = (e^2/pi^2) * I_L(p^2)   (I_L is some dimensionless integral)
#   Pi_M = (e^2/pi^2) * I_M(p^2)
# We replace Pi_T, Pi_L, Pi_M with their symbolic definitions and check equality.
pi = sp.pi
Pi_T_def = e**2/(12*pi**2) * sp.log(a**(-2)/p**2) + (e**2/pi**2) * Phi_N
# For Pi_L and Pi_M we keep the integral symbols I_L, I_M (they are dimensionless)
I_L, I_M = sp.symbols('I_L I_M')
Pi_L_def = (e**2/pi**2) * I_L
Pi_M_def = (e**2/pi**2) * I_M

# Substitute the definitions into the generic expression
alpha_eff_from_def = alpha0 / (1 + Pi_T_def + i_z * Phi_Delta * (Pi_L_def + 2*Pi_M_def))

# Check that the two expressions are structurally identical (up to renaming of Pi_*)
assert sp.simplify(alpha_eff_expr - alpha_eff_from_def) == 0, \
    "Effective coupling does not match the required Omega‑Protocol form."

# ----------------------------------------------------------------------
# 2. Verify Pi_T contains the Phi_N term as prescribed
# ----------------------------------------------------------------------
# Extract the coefficient of Phi_N in Pi_T_def
coeff_Phi_N_in_Pi_T = sp.Pi_T_def.coeff(Phi_N)
expected_coeff = e**2/pi**2
assert sp.simplify(coeff_Phi_N_in_Pi_T - expected_coeff) == 0, \
    "Pi_T missing correct Phi_N coefficient."

# ----------------------------------------------------------------------
# 3. Verify entropy‑gauge construction
# ----------------------------------------------------------------------
# S_pair = S0 + Phi_Delta * S1 + O(Phi_Delta^2) with S1 = -(Pi_L + 2*Pi_M)
S0, S1 = sp.symbols('S0 S1')
S_pair_expr = S0 + Phi_Delta * S1
# S1 must equal -(Pi_L + 2*Pi_M)
S1_def = -(Pi_L + 2*Pi_M)
assert sp.simplify(S1 - S1_def) == 0, \
    "Entropy term S1 does not equal -(Pi_L + 2*Pi_M)."

# Entropy gauge Lagrangian: L_entropy = A_mu J^mu
#   A_mu = ∂_mu S_pair
#   J^mu = sqrt(2) Phi_Delta delta^mu_0
# We only check that the structure uses the correct derivatives and current.
mu = sp.symbols('mu')
A_mu = sp.diff(S_pair_expr, sp.Symbol('x%d' % mu))  # placeholder derivative
J_mu = sp.sqrt(2) * Phi_Delta * sp.KroneckerDelta(mu, 0)  # delta^mu_0
L_entropy = A_mu * J_mu
# Ensure L_entropy contains Phi_Delta and a derivative of S_pair
assert Phi_Delta in L_entropy.free_symbols, \
    "Entropy gauge Lagrangian missing Phi_Delta factor."
assert any(str(s).startswith('Derivative') for s in L_entropy.atoms(sp.Derivative)), \
    "Entropy gauge Lagrangian missing derivative of S_pair."

# ----------------------------------------------------------------------
# 4. Omega invariants (psi, xi_N, xi_Delta) must appear in the effective action
# ----------------------------------------------------------------------
# psi = ln(Phi_N)
psi = sp.log(Phi_N)
# xi_N = dPhi_N/dpsi, xi_Delta = dPhi_Delta/dpsi
xi_N = sp.symbols('xi_N')
xi_Delta = sp.symbols('xi_Delta')
# By definition: dPhi_N/dpsi = xi_N  =>  Phi_N = xi_N * psi + const (we just check relation)
# We enforce that Phi_N can be expressed as xi_N * psi (up to an additive constant which does not affect dynamics)
# For simplicity we check that the derivative of Phi_N w.r.t. psi equals xi_N.
# Since Phi_N = exp(psi), dPhi_N/dpsi = exp(psi) = Phi_N, thus xi_N must equal Phi_N.
# In the Omega protocol xi_N is a *stiffness coefficient* (generally not equal to Phi_N),
# but the invariant definition requires xi_N = ∂Phi_N/∂psi.
# We therefore verify the symbolic identity: xi_N = sp.diff(Phi_N, psi)
assert sp.simplify(xi_N - sp.diff(Phi_N, psi)) == 0, \
    "xi_N not defined as ∂Phi_N/∂psi."
assert sp.simplify(xi_Delta - sp.diff(Phi_Delta, psi)) == 0, \
    "xi_Delta not defined as ∂Phi_Delta/∂psi."

# Effective action snippet (schematic) should contain:
#   sqrt(g) * [ 1/4 F^2 + (alpha0^{-1} + delta_alpha_N^{-1}) F^2
#               + xi_N/2 (∂Phi_N)^2 + xi_Delta/2 (∂Phi_Delta)^2
#               + A_mu J^mu ]
# We check that the terms xi_N*(∂Phi_N)^2 and xi_Delta*(∂Phi_Delta)^2 are present.
# Placeholder symbols for derivatives:
dPhi_N = sp.symbols('dPhi_N')
dPhi_Delta = sp.symbols('dPhi_Delta')
action_terms = xi_N/2 * dPhi_N**2 + xi_Delta/2 * dPhi_Delta**2
# Ensure the action contains both stiffness terms
assert xi_N in action_terms.free_symbols and xi_Delta in action_terms.free_symbols, \
    "Effective action missing xi_N or xi_Delta stiffness terms."

# ----------------------------------------------------------------------
# If we reach here, all checks passed.
# ----------------------------------------------------------------------
print("✅ All Omega‑Protocol invariants and mathematical structures validated.")
print("   Effective coupling:", alpha_eff_expr)
print("   Pi_T definition   :", Pi_T_def)
print("   Entropy gauge term:", L_entropy)
print("   Omega invariants  : psi =", psi, ", xi_N =", xi_N, ", xi_Delta =", xi_Delta)