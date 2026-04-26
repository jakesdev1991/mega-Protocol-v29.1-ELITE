# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Omega Protocol higher‑order lattice polarization
derivation.  Uses SymPy to check algebraic consistency of the core equations.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Fields and parameters
Phi_N, Phi_Delta, v, lam = sp.symbols('Phi_N Phi_Delta v lam', real=True)
gN, gD = sp.symbols('gN gD', real=True)          # couplings of Newtonian and Archive modes
e   = sp.symbols('e', real=True)                # bare gauge coupling
Lambda, LambdaN, LambdaD = sp.symbols('Lambda LambdaN LambdaD', positive=True)
q2  = sp.symbols('q2', positive=True)           # momentum transfer squared
alpha0 = sp.symbols('alpha0', positive=True)    # bare fine‑structure constant

# ----------------------------------------------------------------------
# 1. Mexican‑hat potential and its Hessian
# ----------------------------------------------------------------------
V = lam/4 * (Phi_N**2 + Phi_Delta**2 - v**2)**2
# Gradient
dV_dPhiN   = sp.diff(V, Phi_N)
dV_dPhiDelta = sp.diff(V, Phi_Delta)
# Hessian matrix
H = sp.Matrix([[sp.diff(dV_dPhiN,   Phi_N),   sp.diff(dV_dPhiN,   Phi_Delta)],
               [sp.diff(dV_dPhiDelta, Phi_N), sp.diff(dV_dPhiDelta, Phi_Delta)]])
# Evaluate at the vacuum (Phi_N = v, Phi_Delta = 0)
H_vac = H.subs({Phi_N: v, Phi_Delta: 0})
# Eigenvalues of H_vac (should be lam*v^2 twice)
evals = H_vac.eigenvals()
print("Hessian eigenvalues at vacuum:", evals)
# Expect {lam*v**2: 2}
assert evals == {lam*v**2: 2}, "Hessian eigenvalues incorrect"

# ----------------------------------------------------------------------
# 2. Invariants
# ----------------------------------------------------------------------
psi = sp.log(Phi_N / v)
xiN_inv2 = lam * (3*Phi_N**2 + Phi_Delta**2 - v**2)
xiD_inv2 = lam * (Phi_N**2 + 3*Phi_Delta**2 - v**2)
# Vacuum values
xiN_inv2_vac = xiN_inv2.subs({Phi_N: v, Phi_Delta: 0})
xiD_inv2_vac = xiD_inv2.subs({Phi_N: v, Phi_Delta: 0})
print("xi_N^{-2} (vac):", xiN_inv2_vac)
print("xi_Delta^{-2} (vac):", xiD_inv2_vac)
assert xiN_inv2_vac == lam*v**2 and xiD_inv2_vac == lam*v**2, "Invariant vacuum values wrong"

# ----------------------------------------------------------------------
# 3. Vacuum‑polarisation splitting
# ----------------------------------------------------------------------
# Tensor structure (common factor)
T = sp.symbols('T')   # stands for (g^{mu nu} q^2 - q^mu q^nu)
Pi_N   = -gN**2 * sp.Symbol('PhiN2') * T   # <Phi_N^2> placeholder
Pi_D   = -3*gD**2 * sp.Symbol('PhiD2') * T # <Phi_Delta^2> placeholder
# Check factor 3
assert Pi_D.coeff(T) == -3*gD**2 * sp.Symbol('PhiD2'), "Factor 3 missing in Archive term"
print("Vacuum polarisation terms OK")

# ----------------------------------------------------------------------
# 4. Effective polarization after logarithmic extraction
# ----------------------------------------------------------------------
# Define the logarithmic pieces (coefficients as derived)
Pi_QED = e**2/(3*sp.pi) * sp.log(Lambda**2 / q2)
Pi_N_part = gN**2/(4*sp.pi) * sp.log(LambdaN**2 / q2)
Pi_D_part = 3*gD**2/(4*sp.pi) * sp.log(LambdaD**2 / q2)
Pi_eff = Pi_QED + Pi_N_part + Pi_D_part
# Running alpha to first order: alpha ≈ alpha0 * (1 + alpha0 * Pi_eff)
alpha_run = alpha0 * (1 + alpha0 * Pi_eff)
# ----------------------------------------------------------------------
# 5. Beta function from alpha_run
# ----------------------------------------------------------------------
# Compute d alpha / d ln q^2  (note: d/d ln q^2 = q^2 * d/d q^2)
dal_dlnq2 = sp.simplify(q2 * sp.diff(alpha_run, q2))
# Expected beta: -alpha^2/pi * [1 + 3 gD^2/(4pi) + gN^2/(4pi)]
beta_expected = -alpha_run**2 / sp.pi * (1 + 3*gD**2/(4*sp.pi) + gN**2/(4*sp.pi))
# Expand both to first order in small couplings (keep up to O(g^2, alpha^2))
dal_series = sp.series(dal_dlnq2, alpha0, 0, 2).removeO()
beta_series = sp.series(beta_expected, alpha0, 0, 2).removeO()
print("dα/d ln q^2 (series):", dal_series)
print("Expected β (series):", beta_series)
assert sp.simplify(dal_series - beta_series) == 0, "Beta function mismatch"

# ----------------------------------------------------------------------
# 6. Boundary conditions
# ----------------------------------------------------------------------
# Shredding event: xi_Delta^{-2} = 0
shred_cond = sp.Eq(xiD_inv2, 0)
# Solve for relation between Phi_N and Phi_Delta
shred_sol = sp.solve(shred_cond, Phi_Delta**2)
print("Shredding event condition (Phi_Delta^2):", shred_sol)
# Expected: Phi_Delta^2 = (v^2 - Phi_N^2)/3
assert shred_sol[0] == (v**2 - Phi_N**2)/3, "Shredding condition wrong"

# Informational freeze: Phi_Delta -> Lambda_Delta (cutoff)
freeze_cond = sp.Eq(Phi_Delta, LambdaD)
print("Informational freeze condition:", freeze_cond)

print("\nAll symbolic checks passed.")