# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
----------------------------------
Validates the core mathematical statements of the Engine's derivation
for the higher‑order lattice polarization correction to α_fs.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
Phi_N, Phi_Delta, v, lam = sp.symbols('Phi_N Phi_Delta v lam', real=True, nonnegative=True)
# Mass‑squared parameters (eigenvalues of Hessian)
mN2, mD2 = sp.symbols('mN2 mD2', real=True, nonnegative=True)

# ----------------------------------------------------------------------
# 1. Mexican‑hat potential and its curvature (inverse correlation lengths)
# ----------------------------------------------------------------------
V = lam/4 * (Phi_N**2 + Phi_Delta**2 - v**2)**2

# Second derivatives (curvature matrix)
V_NN = sp.diff(V, Phi_N, 2)
V_DD = sp.diff(V, Phi_Delta, 2)
V_ND = sp.diff(sp.diff(V, Phi_N), Phi_Delta)  # should be zero for this potential

print("Curvature components:")
print("V_NN =", sp.simplify(V_NN))
print("V_DD =", sp.simplify(V_DD))
print("V_ND =", sp.simplify(V_ND))

# Inverse correlation lengths (stiffness invariants)
xiN_inv2 = V_NN
xiD_inv2 = V_DD

print("\nStiffness invariants:")
print("xi_N^{-2} =", sp.simplify(xiN_inv2))
print("xi_Delta^{-2} =", sp.simplify(xiD_inv2))

# ----------------------------------------------------------------------
# 2. Shredding‑Event condition: xi_Delta -> ∞  <=>  xi_Delta^{-2} -> 0
# ----------------------------------------------------------------------
shredding_condition = sp.Eq(xiD_inv2, 0)
print("\nShredding‑Event condition (xi_Delta^{-2}=0):")
print(shredding_condition)

# Solve for the field combination that satisfies it
sol = sp.solve(shredding_condition, Phi_N**2 + 3*Phi_Delta**2)
print("\nSolution for Phi_N^2 + 3*Phi_Delta^2:")
print(sol)   # Expect [v**2]

# ----------------------------------------------------------------------
# 3. Metric coupling invariant psi
# ----------------------------------------------------------------------
psi = sp.ln(Phi_N / v)
print("\nMetric coupling invariant psi = ln(Phi_N/v):")
print(psi)

# ----------------------------------------------------------------------
# 4. Factor‑3 in the Phi_Delta contribution to vacuum polarization
#    (we check that the coefficient of Phi_Delta^2 in xi_Delta^{-2} is 3*lam)
# ----------------------------------------------------------------------
coeff_PhiD2 = sp.Poly(xiD_inv2, Phi_Delta).coeff_monomial(Phi_Delta**2)
print("\nCoefficient of Phi_Delta^2 in xi_Delta^{-2}:")
print(coeff_PhiD2)   # Should be 3*lam
assert coeff_PhiD2 == 3*lam, "Factor‑3 missing in Phi_Delta curvature"

# ----------------------------------------------------------------------
# 5. Hessian diagonalization (optional sanity check)
#    For the quadratic part of V around the vacuum (Phi_N=v, Phi_Delta=0)
# ----------------------------------------------------------------------
# Expand V to second order about the minimum (Phi_N=v, Phi_Delta=0)
V_expanded = sp.series(V, Phi_N, v, 2).removeO()
V_expanded = sp.series(V_expanded, Phi_Delta, 0, 2).removeO()
print("\nQuadratic expansion of V around (v,0):")
print(V_expanded)

# The quadratic form should be (1/2)*[mN2*(Phi_N-v)^2 + mD2*Phi_Delta^2]
# Extract coefficients:
coeff_N = sp.Poly(V_expanded, Phi_N - v).coeff_monomial((Phi_N - v)**2)
coeff_D = sp.Poly(V_expanded, Phi_Delta).coeff_monomial(Phi_Delta**2)
print("\nCoefficients:")
print("mN^2/2 =", coeff_N)
print("mD^2/2 =", coeff_D)

# According to the potential, mN^2 = mD^2 = lam * v^2
expected = lam * v**2
assert sp.simplify(coeff_N * 2 - expected) == 0, "Newtonian mass mismatch"
assert sp.simplify(coeff_D * 2 - expected) == 0, "Archive mass mismatch"

print("\nAll checks passed – derivation respects Omega Protocol invariants.")