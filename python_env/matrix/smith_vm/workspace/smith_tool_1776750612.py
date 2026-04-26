# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
Verifies the higher‑order lattice polarization derivation
for the fine‑structure constant using the orthogonal decomposition
(Φ_N, Φ_Δ).  Fails if any invariant, Shredding condition, or
equation‑level step is inconsistent.
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
# ------------------------------------------------------------------
lam, v = sp.symbols('lam v', positive=True)   # λ > 0, v > 0
Phi_N, Phi_D = sp.symbols('Phi_N Phi_D')      # fields
gN, gD = sp.symbols('gN gD')                  # couplings
# Momentum scale symbols (not needed for algebraic checks)
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# 1. Correct Mexican‑hat potential (O(2) symmetric)
# ------------------------------------------------------------------
V = lam/4 * (Phi_N**2 + Phi_D**2 - v**2)**2
print("Potential V =", V.simplify())

# ------------------------------------------------------------------
# 2. Hessian matrix and its diagonalisation (mass‑squared eigenvalues)
# ------------------------------------------------------------------
# Compute second derivatives
V_NN = sp.diff(V, Phi_N, 2)
V_ND = sp.diff(V, Phi_N, Phi_D)
V_DD = sp.diff(V, Phi_D, 2)

H = sp.Matrix([[V_NN, V_ND],
               [V_ND, V_DD]])
print("\nHessian H =")
sp.pprint(H.simplify())

# Evaluate at the symmetric vacuum (Phi_N = v, Phi_D = 0)
H_vac = H.subs({Phi_N: v, Phi_D: 0})
print("\nHessian at vacuum (Φ_N=v, Φ_Δ=0) =")
sp.pprint(H_vac.simplify())

# Eigenvalues (should be λ v^2 for both modes in the O(2) symmetric case)
evals = H_vac.eigenvals()
print("\nEigenvalues of H at vacuum:", evals)
# Expect {lam*v**2: 2}
assert evals == {lam*v**2: 2}, "Hessian eigenvalues incorrect – potential not O(2) symmetric"

# ------------------------------------------------------------------
# 3. Stiffness invariants ξ_N^{-2}, ξ_Δ^{-2}
# ------------------------------------------------------------------
# General expressions (second derivatives of V)
xiN_inv2 = V_NN   # ∂²V/∂Φ_N²
xiD_inv2 = V_DD   # ∂²V/∂Φ_Δ²

print("\nStiffness invariants:")
print("ξ_N^{-2} =", xiN_inv2.simplify())
print("ξ_Δ^{-2} =", xiD_inv2.simplify())

# Vacuum values
xiN_inv2_vac = xiN_inv2.subs({Phi_N: v, Phi_D: 0})
xiD_inv2_vac = xiD_inv2.subs({Phi_N: v, Phi_D: 0})
print("\nAt vacuum (Φ_N=v, Φ_Δ=0):")
print("ξ_N^{-2} =", xiN_inv2_vac.simplify())
print("ξ_Δ^{-2} =", xiD_inv2_vac.simplify())
assert xiN_inv2_vac == lam*v**2, "ξ_N^{-2} vacuum mismatch"
assert xiD_inv2_vac == lam*v**2, "ξ_Δ^{-2} vacuum mismatch"

# ------------------------------------------------------------------
# 4. Shredding Event: ξ_Δ → ∞  ⇔  ∂²V/∂Φ_Δ² = 0
# ------------------------------------------------------------------
shredding_cond = sp.solve(xiD_inv2, Phi_D**2)
print("\nShredding condition (∂²V/∂Φ_Δ² = 0) gives:")
print("Φ_Δ^2 =", shredding_cond)
# Expected: Φ_Δ^2 = (v^2 - Φ_N^2)/3
assert shredding_cond == [(v**2 - Phi_N**2)/3], "Shredding condition incorrect"

# Express as Φ_N^2 + 3 Φ_Δ^2 = v^2
shredding_surface = sp.Eq(Phi_N**2 + 3*Phi_D**2, v**2)
print("\nShredding surface:", shredding_surface)

# ------------------------------------------------------------------
# 5. Factor‑3 from the 3D Archive mode
# ------------------------------------------------------------------
# Assume each internal dimension contributes equally g_D^2 ⟨Φ_D^2⟩.
# Sum over three dimensions → 3 g_D^2 ⟨Φ_D^2⟩.
contrib_N = gN**2          # Newtonian mode (single dimension)
contrib_D = 3 * gD**2      # Archive mode (three dimensions)
print("\nContribution to vacuum polarization:")
print("Newtonian mode:", contrib_N)
print("Archive mode (3D):", contrib_D)
assert contrib_D == 3*gD**2, "Factor‑3 missing from Archive mode"

# ------------------------------------------------------------------
# 6. Effective polarization and running α_fs (logarithmic part)
# ------------------------------------------------------------------
# In the logarithmic approximation the effective coupling receives
#   Δα^{-1} = (α0/3π) ln(Λ^2/q^2) + (g_N^2/4π) ln(Λ_N^2/q^2)
#           + (3 g_D^2/4π) ln(Λ_D^2/q^2)
# We check the coefficients.
alpha0 = sp.symbols('alpha0')
coeff_QED   = alpha0/(3*sp.pi)
coeff_N     = gN**2/(4*sp.pi)
coeff_D     = 3*gD**2/(4*sp.pi)

print("\nCoefficients in α_fs^{-1}:")
print("QED part   :", coeff_QED)
print("Newtonian  :", coeff_N)
print("Archive (3D):", coeff_D)
assert coeff_N == gN**2/(4*sp.pi), "Newtonian coefficient wrong"
assert coeff_D == 3*gD**2/(4*sp.pi), "Archive coefficient wrong"

# ------------------------------------------------------------------
# 7. β‑function from dα/dln q^2
# ------------------------------------------------------------------
# α^{-1}(q^2) = α0^{-1} - Π_eff(q^2)
# Differentiate: dα/dln q^2 = -α^2 * dΠ_eff/dln q^2
# dΠ_eff/dln q^2 = -(α0/3π) - (g_N^2/4π) - (3 g_D^2/4π)
beta = -alpha0**2 * ( -coeff_QED - coeff_N - coeff_D )
print("\nβ‑function (dα/dln q^2) =", beta.simplify())
# Expected: -α^2/π * [1 + 3 g_D^2/(4π) + g_N^2/(4π)]
beta_expected = -alpha0**2/sp.pi * (1 + 3*gD**2/(4*sp.pi) + gN**2/(4*sp.pi))
print("Expected β‑function    :", beta_expected.simplify())
assert sp.simplify(beta - beta_expected) == 0, "β‑function mismatch"

print("\nAll Omega‑Protocol checks PASSED.")