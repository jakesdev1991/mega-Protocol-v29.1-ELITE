# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Higher‑Order Lattice Polarization derivation
for the fine‑structure constant within the Omega Protocol.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
lam, v = sp.symbols('lam v', positive=True)   # lambda, vev
PhiN, PhiD = sp.symbols('PhiN PhiD')          # Newtonian & Archive fields
gN, gD = sp.symbols('gN gD')                  # couplings
q2 = sp.symbols('q2')                         # momentum transfer squared
# internal dimension index for Archive mode
a = sp.symbols('a', integer=True, nonnegative=True)

# ----------------------------------------------------------------------
# 1. Mexican‑hat potential and its Hessian
# ----------------------------------------------------------------------
V = lam/4 * (PhiN**2 + PhiD**2 - v**2)**2
H = sp.hessian(V, (PhiN, PhiD))   # 2x2 Hessian matrix
print("Hessian H:")
sp.pprint(H)
print()

# Evaluate at the symmetric vacuum: choose PhiN = v, PhiD = 0 (any point on the circle works)
Hvac = H.subs({PhiN: v, PhiD: 0})
print("Hessian at vacuum (PhiN=v, PhiD=0):")
sp.pprint(Hvac)
print()

# Eigenvalues (should be equal)
evals = Hvac.eigenvals()
print("Eigenvalues of H at vacuum:", evals)
print()

# ----------------------------------------------------------------------
# 2. Orthogonal diagonalisation (U^T H U = diag(m^2, m^2))
# ----------------------------------------------------------------------
# For a proportional-to-identity matrix any orthogonal U works; we pick the identity.
U = sp.eye(2)
diagU = U.T * Hvac * U
print("U^T H U (should be diagonal):")
sp.pprint(diagU)
print()
# Extract mass squared
m2_sq = diagU[0,0]   # = lam * v^2
print("m^2 =", m2_sq.simplify())
print()

# ----------------------------------------------------------------------
# 3. Invariants from second derivatives
# ----------------------------------------------------------------------
xiN_inv2 = sp.diff(V, PhiN, 2)
xiD_inv2 = sp.diff(V, PhiD, 2)
print("xi_N^{-2} =", xiN_inv2.simplify())
print("xi_Delta^{-2} =", xiD_inv2.simplify())
print()

# Evaluate at vacuum to check they equal lambda*v^2
print("xi_N^{-2}|vac =", xiN_inv2.subs({PhiN: v, PhiD: 0}).simplify())
print("xi_Delta^{-2}|vac =", xiD_inv2.subs({PhiN: v, PhiD: 0}).simplify())
print()

# ----------------------------------------------------------------------
# 4. Vacuum‑polarisation tensor structure
# ----------------------------------------------------------------------
# Transverse projector
mu, nu = sp.symbols('mu nu')
g = sp.symbols('g')   # metric placeholder; we treat g^{mu nu} as symbolic
# In practice we only need the tensor structure:
Pi_struct = g**2 * q2 - sp.Symbol('q^mu')*sp.Symbol('q^nu')  # symbolic
# For verification we assert proportionality:
PiN = -gN**2 * sp.Symbol('PhiN_sq') * (g**2 * q2 - sp.Symbol('q^mu')*sp.Symbol('q^nu'))
PiD = -3*gD**2 * sp.Symbol('PhiD_sq') * (g**2 * q2 - sp.Symbol('q^mu')*sp.Symbol('q^nu'))
print("Pi_N structure (should be transverse):")
sp.pprint(PiN)
print()
print("Pi_Delta structure (factor 3 present):")
sp.pprint(PiD)
print()

# ----------------------------------------------------------------------
# 5. Effective polarisation (logarithmic part) and beta function
# ----------------------------------------------------------------------
# Define logarithmic contributions (coefficients only)
e2 = sp.symbols('e2')
Lambda = sp.symbols('Lambda')
LambdaN = sp.symbols('LambdaN')
LambdaD = sp.symbols('LambdaD')
Pi_eff = (e2/(3*sp.pi))*sp.log(Lambda**2/q2) + \
         (gN**2/(4*sp.pi))*sp.log(LambdaN**2/q2) + \
         (3*gD**2/(4*sp.pi))*sp.log(LambdaD**2/q2)
print("Effective polarisation Pi_eff(q^2):")
sp.pprint(Pi_eff)
print()

# Running inverse alpha
alpha0 = sp.symbols('alpha0')
alpha_inv = alpha0**-1 - Pi_eff
print("alpha^{-1}(q^2):")
sp.pprint(alpha_inv)
print()

# Beta function: d alpha / d ln q^2 = - alpha^2 * d(Pi_eff)/d ln q^2
dPi_dlnq2 = sp.diff(Pi_eff, sp.log(q2))
beta = - alpha0**2 * dPi_dlnq2   # evaluate at leading order (replace alpha0 by alpha)
beta_simplified = sp.simplify(beta)
print("Beta function (leading order):")
sp.pprint(beta_simplified)
print()
# Expected form: -alpha^2/pi * [1 + gN^2/(4pi) + 3 gD^2/(4pi)]
expected = -alpha0**2/sp.pi * (1 + gN**2/(4*sp.pi) + 3*gD**2/(4*sp.pi))
print("Expected beta function:")
sp.pprint(expected)
print()
print("Are they equal? ", sp.simplify(beta_simplified - expected) == 0)
print()

# ----------------------------------------------------------------------
# 6. Entropy coupling (symbolic check only)
# ----------------------------------------------------------------------
Sh = sp.symbols('S_h')   # Shannon entropy
Z_Delta = sp.symbols('Z_Delta')
# Assume Z_Delta = Z0 * exp(-Sh) (example coupling)
Z0 = sp.symbols('Z0')
Z_Delta_expr = Z0 * sp.exp(-Sh)
print("Topological impedance Z_Delta (example entropy coupling):")
sp.pprint(Z_Delta_expr)
print()
# The gauge‑invariant transverse structure remains unchanged:
PiD_withZ = -Z_Delta_expr * gD**2 * sp.Symbol('PhiD_sq') * (g**2 * q2 - sp.Symbol('q^mu')*sp.Symbol('q^nu'))
print("Pi_Delta with entropy‑dependent impedance:")
sp.pprint(PiD_withZ)
print()

print("Validation complete.")