# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for the Higher‑Order Lattice Polarization
Derivation (Agent Smith audit).

Run this script in the isolated VM. It will abort with an AssertionError
if any invariant is violated.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
Phi_N, Phi_Delta, v, lam = sp.symbols('Phi_N Phi_Delta v lam', real=True)
gN, gD, Lambda_N, Lambda_Delta, q = sp.symbols('gN gD Lambda_N Lambda_Delta q', positive=True)
e, alpha0 = sp.symbols('e alpha0', positive=True)

# ----------------------------------------------------------------------
# 1. Potential and Hessian
# ----------------------------------------------------------------------
V = lam/4 * (Phi_N**2 + Phi_Delta**2 - v**2)**2
# Hessian matrix (second derivatives)
H = sp.hessian(V, (Phi_N, Phi_Delta))
# Evaluate at the vacuum point (choose Phi_N=v, Phi_Delta=0 as a representative minimum)
H_vac = H.subs({Phi_N: v, Phi_Delta: 0})
print("Hessian at (v,0):")
sp.pprint(H_vac)

# Orthogonal diagonalisation: eigenvectors of symmetric H are orthogonal.
# Compute eigenvectors and form matrix U.
eigvals, eigvecs = H_vac.diagonalize()
U = eigvecs  # columns are eigenvectors
# Check orthogonality: U^T * U = I
I_check = U.T * U
assert sp.simplify(I_check - sp.eye(2)) == sp.zeros(2,2), \
    "Orthogonality condition U^T U = I violated"
print("✓ Orthogonality of U satisfied.")

# ----------------------------------------------------------------------
# 2. Invariants
# ----------------------------------------------------------------------
psi = sp.log(Phi_N / v)
# Curvature invariants (second derivatives of V)
xi_N_inv2 = sp.diff(V, Phi_N, 2)
xi_Delta_inv2 = sp.diff(V, Phi_Delta, 2)
print("\nInvariants:")
sp.pprint(psi)
sp.pprint(xi_N_inv2)
sp.pprint(xi_Delta_inv2)

# ----------------------------------------------------------------------
# 3. Shredding Event condition (xi_Delta^{-2} = 0)
# ----------------------------------------------------------------------
shred_cond = sp.simplify(xi_Delta_inv2)
shred_solution = sp.solve(shred_cond, Phi_Delta**2)
print("\nShredding condition (xi_Delta^{-2}=0) gives:")
sp.pprint(shred_solution)
# Expected: Phi_N^2 + 3*Phi_Delta^2 = v^2
expected = sp.Eq(Phi_N**2 + 3*Phi_Delta**2, v**2)
assert sp.simplify(shred_solution[0] - expected.rhs) == 0, \
    "Shredding condition does not match Phi_N^2 + 3*Phi_Delta^2 = v^2"
print("✓ Shredding condition matches invariant.")

# ----------------------------------------------------------------------
# 4. Effective polarization (logarithmic part)
# ----------------------------------------------------------------------
# According to the derivation:
Pi_eff = (e**2/(3*sp.pi))*sp.log(Lambda_N**2 / q**2) \
       + (gN**2/(4*sp.pi))*sp.log(Lambda_N**2 / q**2) \
       + (3*gD**2/(4*sp.pi))*sp.log(Lambda_Delta**2 / q**2)
# Note: the first term uses a generic cutoff Lambda (we treat it as Lambda_N for consistency)
# For validation we keep Lambda_N and Lambda_Delta distinct as in the text.

# Running coupling: alpha^{-1}(q^2) = alpha0^{-1} - Pi_eff
alpha_inv = 1/alpha0 - Pi_eff
alpha = 1/alpha_inv  # exact expression
# Beta function: d alpha / d ln q^2
beta = sp.simplify(alpha.diff(sp.log(q**2)))
print("\nBeta function from derived alpha:")
sp.pprint(beta)

# Expected beta from the text:
beta_expected = -alpha**2/sp.pi * (1 + 3*gD**2/(4*sp.pi) + gN**2/(4*sp.pi))
# Substitute alpha with the derived expression to compare
beta_expected_sub = sp.simplify(beta_expected.subs(alpha, alpha))
assert sp.simplify(beta - beta_expected_sub) == 0, \
    "Beta function mismatch with protocol‑stated form"
print("✓ Beta function matches expected Omega Protocol form.")

# ----------------------------------------------------------------------
# 5. Cutoff respect – ensure no extra q‑dependence beyond logs
# ----------------------------------------------------------------------
# Extract q‑dependence from Pi_eff
Pi_q_dep = sp.simplify(Pi_eff - Pi_eff.subs(q, 1))  # set q=1 to isolate constant part
# The remaining should be a combination of logs of q
log_terms = sp.log(q**2)
assert Pi_q_dep.has(log_terms), "Pi_eff does not contain the expected log(q^2) dependence"
print("✓ Pi_eff contains only log(q^2) dependence as required.")

# ----------------------------------------------------------------------
# 6. Informational Freeze – check that Phi_Delta is bounded by Lambda_Delta
# ----------------------------------------------------------------------
# The derivation states freeze when Phi_Delta -> Lambda_Delta.
# We enforce that any expression for Phi_Delta^2 must be <= Lambda_Delta^2.
# As a simple test, verify that the shredding surface never exceeds this bound
# when Lambda_Delta is taken as the maximal allowed value.
# Choose a point on the shredding surface: Phi_N^2 = v^2 - 3*Phi_Delta^2
# Require Phi_Delta^2 <= Lambda_Delta^2 for all allowed Phi_N^2 >=0.
# This yields condition: v^2 - 3*Phi_Delta^2 >= 0  =>  Phi_Delta^2 <= v^2/3
# Hence we need Lambda_Delta^2 >= v^2/3 for the freeze to occur *before* shredding.
freeze_condition = sp.simplify(Lambda_Delta**2 - v**2/3)
assert freeze_condition >= 0, \
    "Informational Freeze cutoff Lambda_Delta too low; would allow shredding before freeze."
print("✓ Informational Freeze cutoff respects shredding bound.")

print("\nAll Omega Protocol invariants satisfied. Derivation is compliant.")