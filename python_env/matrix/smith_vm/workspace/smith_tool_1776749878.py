# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validation Script
--------------------------------
Checks the engine's claimed expression for the fine‑structure constant
alpha_fs(q^2) for:
  * dimensional consistency,
  * correctness of the QED one‑loop sign,
  * RG consistency (beta function from alpha_fs matches expected form),
  * basic sanity of the lattice term.
Run in the isolated VM; any assertion failure indicates a violation of
the Omega Protocol invariants.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Fundamental constants (set ħ = c = 1 for simplicity)
alpha0, gDelta, e = sp.symbols('alpha0 gDelta e', positive=True)
# Yukawa coupling relation: e^2 = 4π α0  (in natural units)
# We keep e as an independent symbol to check consistency later.
q2, m = sp.symbols('q2 m', real=True)   # q^2 is Euclidean (−q^2 > 0 for log)
psi, xi0, C = sp.symbols('psi xi0 C', real=True)  # Omega invariants
# ----------------------------------------------------------------------
# Helper: natural log of (-q^2/m^2)  (assume -q^2 > 0)
L = sp.log(-q2 / m**2)

# ----------------------------------------------------------------------
# Engine's claimed expression (as given in the audit)
# ----------------------------------------------------------------------
# alpha_fs = alpha0 * [ 1 + (alpha0/(3π))*L
#                     + (gDelta**2 * alpha0)/(32π**4) * L**2
#                     + C * xi0**(-2) * exp(2*psi) * q2
#                     + O(alpha0**2, gDelta**4) ]
pi = sp.pi
alpha_fs = alpha0 * (
    1
    + alpha0/(3*pi) * L
    + (gDelta**2 * alpha0) / (32 * pi**4) * L**2
    + C * xi0**(-2) * sp.exp(2*psi) * q2
)

# ----------------------------------------------------------------------
# 1. Dimensional check: each term inside [] must be dimensionless
# ----------------------------------------------------------------------
# In natural units: [alpha0] = 1, [gDelta] = 1, [e] = 1,
# [q2] = mass^2, [m] = mass, [xi0] = length, [psi] = 1,
# [C] must be length^2 to make C * xi0^{-2} * q2 dimensionless.
dim_check = sp.simplify(
    (alpha0/(3*pi) * L).has(sp.log)  # log is dimensionless
    and (gDelta**2 * alpha0) / (32 * pi**4) * L**2).has(sp.log**2)
    and (C * xi0**(-2) * sp.exp(2*psi) * q2).has(C * xi0**(-2) * q2)
)  # symbolic check; we will instead assert dimensions manually below

# Explicit dimensional assertion: treat xi0 as length, q2 as mass^2
# In natural units length = 1/mass, so xi0^{-2} * q2 is dimensionless.
# Therefore C must be dimensionless. We'll enforce C == 1 for the test.
# (If C carries dimensions, the user must supply them.)
assert C == 1, "C must be dimensionless (or set to 1 in natural units) for the lattice term to be dimensionless."

# ----------------------------------------------------------------------
# 2. One-loop QED sign check
# ----------------------------------------------------------------------
# Extract the coefficient of L (the one‑loop piece)
coeff_L = sp.Poly(alpha_fs/alpha0 - 1, L).coeff_monomial(L)
expected_coeff_L = alpha0/(3*pi)   # correct sign (+)
assert sp.simplify(coeff_L - expected_coeff_L) == 0, \
    f"One-loop coefficient mismatch: got {coeff_L}, expected {expected_coeff_L}"

# ----------------------------------------------------------------------
# 3. RG consistency: beta function from alpha_fs
# ----------------------------------------------------------------------
# Define t = ln(-q^2/m^2) = L
t = L
# alpha_fs as function of t (treat other symbols as constants)
alpha_of_t = alpha0 * (
    1
    + alpha0/(3*pi) * t
    + (gDelta**2 * alpha0) / (32 * pi**4) * t**2
    + C * xi0**(-2) * sp.exp(2*psi) * q2   # note: this term does NOT depend on t
)
# Beta function: β = dα/dt
beta = sp.diff(alpha_of_t, t)
beta_simplified = sp.simplify(beta)
# Expected beta from known QED + scalar Yukawa (two‑loop) :
# β_QED = 2*alpha0**2/(3π)
# β_Yukawa = alpha0 * gDelta**2 / (16π**2)   (scheme‑dependent, we use this as reference)
expected_beta = 2*alpha0**2/(3*pi) + alpha0 * gDelta**2/(16*pi**2)
assert sp.simplify(beta_simplified - expected_beta) == 0, \
    f"Beta function mismatch:\n computed {beta_simplified}\n expected {expected_beta}"

# ----------------------------------------------------------------------
# 4. Lattice term independence from t (should be pure power‑law)
# ----------------------------------------------------------------------
# The lattice term must not contain logs; otherwise it would mix with running.
lattice_term = C * xi0**(-2) * sp.exp(2*psi) * q2
assert lattice_term.has(t) == False, "Lattice term incorrectly contains log(t)."

# ----------------------------------------------------------------------
# If we reach here, all basic invariants are satisfied.
# ----------------------------------------------------------------------
print("All Omega‑Protocol invariant checks passed.")
print("Note: Passing these checks does NOT guarantee the derivation is correct;"
      " it only confirms that the expression respects dimensional analysis,"
      " the known one‑loop QED sign, RG consistency, and lattice‑term form.")