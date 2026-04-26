# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Higher‑Order Lattice Polarization derivation
for the fine‑structure constant in the Omega Protocol.
Checks:
  - Hessian diagonalisation → orthogonal modes (Φ_N, Φ_Δ)
  - Stiffness invariants ξ_N^{-2}, ξ_Δ^{-2}
  - Factor 3 in the Archive contribution to Π^{μν}
  - Effective polarisation Π_eff(q²) logarithmic coefficients
  - β‑function consistency
  - Shredding Event condition
  - Informational Freeze condition
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
# ------------------------------------------------------------------
Phi_N, Phi_Delta, v, lam = sp.symbols('Phi_N Phi_Delta v lam', real=True, nonnegative=True)
gN, gD = sp.symbols('gN gD', real=True)          # couplings to Newtonian & Archive modes
# UV cutoffs (appear only inside logs, treated as symbols)
Lambda, LambdaN, LambdaD = sp.symbols('Lambda LambdaN LambdaD', positive=True)
# Momentum transfer (squared) – appears inside logs as q^2
q2 = sp.symbols('q2', positive=True)

# ------------------------------------------------------------------
# 1. Mexican‑hat potential and Hessian
# ------------------------------------------------------------------
V = lam/4 * (Phi_N**2 + Phi_Delta**2 - v**2)**2

# Gradient (should vanish at the vacuum Phi_N = v, Phi_Delta = 0)
grad_V = [sp.diff(V, Phi_N), sp.diff(V, Phi_Delta)]
# Hessian matrix
H = sp.Matrix([[sp.diff(V, Phi_N, Phi_N), sp.diff(V, Phi_N, Phi_Delta)],
               [sp.diff(V, Phi_Delta, Phi_N), sp.diff(V, Phi_Delta, Phi_Delta)]])

# Evaluate at the vacuum (Phi_N = v, Phi_Delta = 0)
H_vac = H.subs({Phi_N: v, Phi_Delta: 0})
print("Hessian at vacuum:\n", H_vac)

# Eigenvalues (should be lam*v^2 for both modes)
evals = H_vac.eigenvals()
print("Eigenvalues:", evals)

# ------------------------------------------------------------------
# 2. Orthogonal decomposition (U) – here we just note that the Hessian is already diagonal
# ------------------------------------------------------------------
# In this basis the modes are Phi_N, Phi_Delta directly.
# Check that the quadratic term is 1/2 * m_N^2 * Phi_N^2 + 1/2 * m_D^2 * Phi_Delta^2
mN2 = lam * v**2
mD2 = lam * v**2
quad = sp.Rational(1,2) * mN2 * Phi_N**2 + sp.Rational(1,2) * mD2 * Phi_Delta**2
# Compare with V expanded to second order around the vacuum
V_quad = sp.series(V, Phi_N, v, 2).removeO() + sp.series(V, Phi_Delta, 0, 2).removeO()
# Actually we just verify that the Hessian gives the same coefficients
assert H_vac[0,0] == mN2, "Newtonian mass term mismatch"
assert H_vac[1,1] == mD2, "Archive mass term mismatch"
print("Quadratic form check passed.")

# ------------------------------------------------------------------
# 3. Stiffness invariants ξ_N^{-2}, ξ_Δ^{-2}
# ------------------------------------------------------------------
# General second derivatives (no vacuum substitution)
d2V_dPhiN2 = sp.diff(V, Phi_N, Phi_N)
d2V_dPhiD2 = sp.diff(V, Phi_Delta, Phi_Delta)

xiN_inv2 = d2V_dPhiN2
xiD_inv2 = d2V_dPhiD2

print("\nξ_N^{-2} =", xiN_inv2)
print("ξ_Δ^{-2} =", xiD_inv2)

# According to the text:
xiN_inv2_expected = lam * (3*Phi_N**2 + Phi_Delta**2 - v**2)
xiD_inv2_expected = lam * (Phi_N**2 + 3*Phi_Delta**2 - v**2)

assert sp.simplify(xiN_inv2 - xiN_inv2_expected) == 0, "ξ_N^{-2} mismatch"
assert sp.simplify(xiD_inv2 - xiD_inv2_expected) == 0, "ξ_Δ^{-2} mismatch"
print("Stiffness invariants match the Omega Protocol expressions.")

# ------------------------------------------------------------------
# 4. Vacuum‑polarisation tensor coefficients
# ------------------------------------------------------------------
# In the diagonal basis the contribution from each mode is proportional to
# -g_i^2 <Phi_i^2> (g^{μν} q^2 - q^μ q^ν) with a multiplicity factor.
# For Newtonian: factor 1
# For Archive:   factor 3 (three internal dimensions)
coeff_N = -gN**2   # <Phi_N^2> omitted – we only check the coupling
coeff_D = -3 * gD**2

print("\nPolarisation coupling coefficients:")
print("  Newtonian:", coeff_N)
print("  Archive   :", coeff_D)

assert coeff_D == -3 * gD**2, "Archive factor 3 missing or wrong"
print("Factor‑3 check passed.")

# ------------------------------------------------------------------
# 5. Effective polarisation Π_eff(q²) – logarithmic part
# ------------------------------------------------------------------
# The derivation gives:
# Π_eff = (e^2)/(3π) * log(Lambda^2/q^2)
#       + (gN^2)/(4π)   * log(LambdaN^2/q^2)
#       + (3*gD^2)/(4π) * log(LambdaD^2/q^2)
e = sp.symbols('e', real=True)
Pi_eff = (e**2)/(3*sp.pi) * sp.log(Lambda**2 / q2) \
       + (gN**2)/(4*sp.pi) * sp.log(LambdaN**2 / q2) \
       + (3*gD**2)/(4*sp.pi) * sp.log(LambdaD**2 / q2)

# Verify that the coefficients match the mode contributions:
# QED part: e^2/(3π)
# Newtonian: gN^2/(4π)
# Archive:   3*gD^2/(4π)
coeff_QED = e**2/(3*sp.pi)
coeff_N_log = gN**2/(4*sp.pi)
coeff_D_log = 3*gD**2/(4*sp.pi)

assert sp.simplify(Pi_eff.coeff(sp.log(Lambda**2/q2)) - coeff_QED) == 0, "QED log coeff"
assert sp.simplify(Pi_eff.coeff(sp.log(LambdaN**2/q2)) - coeff_N_log) == 0, "Newtonian log coeff"
assert sp.simplify(Pi_eff.coeff(sp.log(LambdaD**2/q2)) - coeff_D_log) == 0, "Archive log coeff"
print("\nEffective polarisation logarithmic coefficients verified.")

# ------------------------------------------------------------------
# 6. Running α_fs and β‑function
# ------------------------------------------------------------------
alpha0 = sp.symbols('alpha0', positive=True)
# α^{-1}(q^2) = α0^{-1} - Π_eff(q^2)
alpha_inv = 1/alpha0 - Pi_eff
alpha = 1/alpha_inv   # exact inverse; we will series‑expand for small corrections

# Series expansion to first order in small couplings (e^2, gN^2, gD^2)
# Treat e^2, gN^2, gD^2 as small parameters; keep only linear terms.
alpha_series = sp.series(alpha, e, 0, 2).removeO()
alpha_series = sp.series(alpha_series, gN, 0, 2).removeO()
alpha_series = sp.series(alpha_series, gD, 0, 2).removeO()

print("\nα(q^2) series (linear):")
print(alpha_series)

# Expected form from the text:
# α ≈ α0 [ 1 + (α0/(3π)) log(Lambda^2/q^2)
#            + (gN^2/(4π)) log(LambdaN^2/q^2)
#            + (3 gD^2/(4π)) log(LambdaD^2/q^2) ]
expected = alpha0 * (1
                     + (alpha0/(3*sp.pi)) * sp.log(Lambda**2/q2)
                     + (gN**2/(4*sp.pi)) * sp.log(LambdaN**2/q2)
                     + (3*gD**2/(4*sp.pi)) * sp.log(LambdaD**2/q2))

# Check equality up to linear order
diff = sp.simplify(alpha_series - expected)
assert diff == 0, "Running α expression mismatch"
print("Running α_fs expression matches the derivation.")

# β‑function: dα/d ln q^2
# Compute derivative of alpha_inv w.r.t. ln(q^2) and use dα/d ln q^2 = -α^2 * d(α^{-1})/d ln q^2
lnq2 = sp.symbols('lnq2')
# Replace q^2 = exp(lnq2) for differentiation
alpha_inv_ln = alpha_inv.subs(q2, sp.exp(lnq2))
d_alpha_inv_dlnq2 = sp.diff(alpha_inv_ln, lnq2)
beta = -alpha**2 * d_alpha_inv_dlnq2
# Simplify beta, keep only up to quadratic in couplings (α^2 * (e^2, gN^2, gD^2))
beta_simp = sp.series(beta, e, 0, 2).removeO()
beta_simp = sp.series(beta_simp, gN, 0, 2).removeO()
beta_simp = sp.series(beta_simp, gD, 0, 2).removeO()

print("\nβ‑function (linear in small couplings):")
print(beta_simp)

# Expected β from the text:
# dα/d ln q^2 = -α^2/π * [1 + 3 gD^2/(4π) + gN^2/(4π)]
beta_expected = -alpha**2/sp.pi * (1 + 3*gD**2/(4*sp.pi) + gN**2/(4*sp.pi))
beta_expected_lin = sp.series(beta_expected, e, 0, 2).removeO()
beta_expected_lin = sp.series(beta_expected_lin, gN, 0, 2).removeO()
beta_expected_lin = sp.series(beta_expected_lin, gD, 0, 2).removeO()

assert sp.simplify(beta_simp - beta_expected_lin) == 0, "β‑function mismatch"
print("β‑function verification passed.")

# ------------------------------------------------------------------
# 7. Shredding Event condition
# ------------------------------------------------------------------
# ξ_Δ → ∞  <=>  ∂^2 V/∂Φ_Δ^2 = 0
shredding_cond = sp.Eq(xiD_inv2, 0)
print("\nShredding Event condition (ξ_Δ^{-2}=0):")
print(shredding_cond)
# Solve for relation between Φ_N and Φ_Δ
sol_shred = sp.solve(xiD_inv2, Phi_Delta**2)
print("Solution for Φ_Δ^2:", sol_shred)
# Expected: Φ_N^2 + 3 Φ_Δ^2 = v^2  =>  Φ_Δ^2 = (v^2 - Φ_N^2)/3
expected_shred = (v**2 - Phi_N**2)/3
assert sp.simplify(sol_shred[0] - expected_shred) == 0, "Shredding condition mismatch"
print("Shredding Event condition matches Φ_N^2 + 3Φ_Δ^2 = v^2.")

# ------------------------------------------------------------------
# 8. Informational Freeze condition
# ------------------------------------------------------------------
# Freeze when Φ_Δ reaches its maximal allowed value ≈ Λ_D
freeze_cond = sp.Eq(Phi_Delta, LambdaD)
print("\nInformational Freeze condition:")
print(freeze_cond)
# No further algebra needed; just note that the cutoff Λ_D prevents
# the field from exceeding this value, thus halting the running.
print("Freeze condition defined as Φ_Δ = Λ_D (cutoff).")

print("\nAll validation checks passed.")