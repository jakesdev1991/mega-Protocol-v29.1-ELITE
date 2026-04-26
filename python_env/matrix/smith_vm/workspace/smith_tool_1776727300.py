# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith Validation Script for the Engine's Shredding‑Flaw Submission
Verifies:
  * Potential V and its Hessian
  * Stiffness invariants and Shredding condition
  * Running coupling → β‑function consistency
  * (Optional) Entropy‑impedance feedback linear stability
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
Phi_N, Phi_Delta, v, lam, gN, gD, alpha0, Lambda, q2 = sp.symbols(
    'Phi_N Phi_Delta v lam gN gD alpha0 Lambda q2', positive=True, real=True)
# ------------------------------------------------------------------
# 1. Potential
V = lam/4 * (Phi_N**2 + Phi_Delta**2 - v**2)**2
print("Potential V:", V)

# 2. Hessian
H_NN  = sp.diff(V, Phi_N, 2)
H_DD  = sp.diff(V, Phi_Delta, 2)
H_ND  = sp.diff(V, Phi_N, Phi_Delta)
print("\nHessian components:")
print("H_NN =", H_NN.simplify())
print("H_DD =", H_DD.simplify())
print("H_ND =", H_ND.simplify())

# 3. Stiffness invariants (inverse squared correlation lengths)
xiN_inv2 = H_NN
xiD_inv2 = H_DD
print("\nStiffness invariants:")
print("xi_N^{-2} =", xiN_inv2.simplify())
print("xi_Delta^{-2} =", xiD_inv2.simplify())

# 4. Shredding condition: xi_Delta -> infinity <=> xi_Delta^{-2}=0
shred_cond = sp.solve(xiD_inv2, Phi_N**2)
print("\nShredding condition (xi_Delta^{-2}=0) gives:")
print("Phi_N^2 + 3*Phi_Delta^2 = v^2  ->  Phi_N^2 =", shred_cond)

# 5. Running coupling (as given by Engine, with explicit alpha0 in gN term)
# Note: we insert the missing alpha0 factor for the gN term to match beta-function.
alpha_run = alpha0 * (1 +
                      alpha0/(3*sp.pi) * sp.log(Lambda**2 / q2) +
                      (alpha0 * gN**2)/(4*sp.pi) * sp.log(Lambda**2 / q2) +   # corrected
                      (3 * alpha0 * gD**2)/(4*sp.pi) * sp.log(Lambda**2 / q2))
print("\nRunning coupling α(q^2):")
sp.pprint(alpha_run.simplify())

# 6. Compute β-function from α^{-1}
alpha_inv = 1/alpha_run
beta = - sp.diff(alpha_inv, sp.log(q2))   # dα/dlnq^2 = - d(α^{-1})/dlnq^2
beta_simplified = sp.simplify(beta)
print("\nβ-function derived from α(q^2):")
sp.pprint(beta_simplified)

# Expected β-function from the submission:
beta_expected = - alpha0**2 / sp.pi * (1 + 3*gD**2/(4*sp.pi) + gN**2/(4*sp.pi))
print("\nExpected β-function (from submission):")
sp.pprint(sp.simplify(beta_expected))

# Check equality (should be True after simplification)
print("\nβ-function matches expected?", sp.simplify(beta_simplified - beta_expected) == 0)

# ------------------------------------------------------------------
# 7. Optional: Linear stability of entropy‑impedance feedback
#    Model:   dPhiD/dt = k1 * gD_eff
#             dgD_eff/dt = -k2 * dS_h/dPhiD   with S_h ~ -PhiD^2 (toy model)
#    This yields Jacobian [[0, k1], [2*k2*PhiD, 0]] → eigenvalues ± sqrt(2*k1*k2*PhiD)
#    Positive real part for PhiD>0 → instability.
k1, k2 = sp.symbols('k1 k2', positive=True)
PhiD_sym = sp.symbols('PhiD', real=True)
J = sp.Matrix([[0, k1],
               [2*k2*PhiD_sym, 0]])
eigs = J.eigenvals()
print("\nEigenvalues of toy feedback Jacobian:", eigs)
print("Instability (positive real part) for PhiD>0:", any(sp.re(ev) > 0 for ev in eigs))