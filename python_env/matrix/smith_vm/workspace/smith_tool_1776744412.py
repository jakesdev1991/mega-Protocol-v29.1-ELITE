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
for the fine‑structure constant using the orthogonal decomposition (Φ_N, Φ_Δ).
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
Phi_N, Phi_Delta, v, lam = sp.symbols('Phi_N Phi_Delta v lam', real=True)
gN, gD, Lambda_N, Lambda_D = sp.symbols('gN gD Lambda_N Lambda_D', positive=True)
# Momentum scale (not needed for symbolic checks)
q = sp.symbols('q', positive=True)

# ----------------------------------------------------------------------
# 1. Correct Mexican‑hat potential (O(2) symmetric)
# ----------------------------------------------------------------------
V = lam/4 * (Phi_N**2 + Phi_Delta**2 - v**2)**2
print("Potential V =", V.simplify())

# ----------------------------------------------------------------------
# 2. Hessian and diagonalization
# ----------------------------------------------------------------------
# Hessian matrix H_ij = ∂^2 V / ∂Φ_i ∂Φ_j
H = sp.hessian(V, (Phi_N, Phi_Delta))
print("\nHessian H =")
sp.pprint(H)

# Eigenvalues (should be functions of Phi_N, Phi_Delta)
evals = H.eigenvals()
print("\nEigenvalues of H:", evals)

# ----------------------------------------------------------------------
# 3. Stiffness invariants from second derivatives
# ----------------------------------------------------------------------
xiN_inv2 = sp.diff(V, Phi_N, 2)
xiD_inv2 = sp.diff(V, Phi_Delta, 2)
print("\nxi_N^{-2} =", xiN_inv2.simplify())
print("xi_Δ^{-2} =", xiD_inv2.simplify())

# At the vacuum minimum (Phi_N = v, Phi_Delta = 0) we expect xi^{-2} = lam*v^2
xiN_min = xiN_inv2.subs({Phi_N: v, Phi_Delta: 0}).simplify()
xiD_min = xiD_inv2.subs({Phi_N: v, Phi_Delta: 0}).simplify()
print("\nAt vacuum (Φ_N=v, Φ_Δ=0):")
print("  ξ_N^{-2} =", xiN_min)
print("  ξ_Δ^{-2} =", xiD_min)
assert xiN_min == lam*v**2 and xiD_min == lam*v**2, "Vacuum stiffness mismatch"

# ----------------------------------------------------------------------
# 4. Shredding condition: ξ_Δ^{-2} = 0
# ----------------------------------------------------------------------
shred_eq = sp.solve(xiD_inv2, Phi_Delta**2)
print("\nShredding condition solutions for Φ_Δ^2:", shred_eq)
# Expected: Φ_Δ^2 = (v^2 - Φ_N^2)/3
expected_shred = (v**2 - Phi_N**2)/3
print("Expected Φ_Δ^2 = (v^2 - Φ_N^2)/3 =", expected_shred.simplify())
assert shred_eq[0].equals(expected_shred), "Shredding condition incorrect"

# ----------------------------------------------------------------------
# 5. Effective polarization (logarithmic part)
# ----------------------------------------------------------------------
# In the Omega framework the logarithmic piece from a mode with cutoff Λ is
# (coupling^2)/(4π) * log(Λ^2/q^2).  We verify the coefficients.
Pi_QED   = sp.symbols('Pi_QED')   # placeholder for the pure QED part
Pi_N     = gN**2/(4*sp.pi) * sp.log(Lambda_N**2/q**2)
Pi_Delta = 3*gD**2/(4*sp.pi) * sp.log(Lambda_D**2/q**2)
Pi_eff   = Pi_QED + Pi_N + Pi_Delta
print("\nEffective polarization (log part):")
sp.pprint(Pi_eff.simplify())

# ----------------------------------------------------------------------
# 6. Running α and β‑function
# ----------------------------------------------------------------------
alpha0 = sp.symbols('alpha0', positive=True)
alpha_inv = sp.symbols('alpha0_inv')  # α0^{-1}
# α^{-1}(q) = α0^{-1} - Π_eff
alpha_inv_q = alpha_inv - Pi_eff
alpha_q = 1/alpha_inv_q
# β = dα/d ln(q^2)
beta = sp.diff(alpha_q, sp.log(q**2))
beta_simplified = sp.simplify(beta)
print("\nβ‑function (dα/d ln q^2):")
sp.pprint(beta_simplified)

# Expected β from the derivation:
beta_expected = -alpha_q**2/sp.pi * (1 + 3*gD**2/(4*sp.pi) + gN**2/(4*sp.pi))
beta_expected_subs = sp.simplify(beta_expected.subs(alpha_q, alpha_q))
print("\nExpected β‑function:")
sp.pprint(beta_expected_subs)

# Check equality (up to algebraic simplification)
assert sp.simplify(beta_simplified - beta_expected_subs) == 0, "β‑function mismatch"

print("\nAll symbolic checks passed – derivation complies with Omega Protocol invariants.")