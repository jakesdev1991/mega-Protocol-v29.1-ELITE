# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol validation script for the Higher‑Order Lattice Polarization
corrections to the fine‑structure constant.

Checks:
- The effective polarization Π_eff(q^2) yields the expected logarithmic form.
- The Shredding surface coincides with vanishing Φ_Δ‑curvature.
- The final α_fs(E) matches the boxed result.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Couplings and scales
gN, gD, a0, LambdaN, LambdaD, Lambda = sp.symbols('gN gD a0 LambdaN LambdaD Lambda', positive=True)
# Momenta
q, k = sp.symbols('q k', positive=True)
# Field vev and lambda
v, lam = sp.symbols('v lam', positive=True)
# Fields
PhiN, PhiD = sp.symbols('PhiN PhiD', real=True)

# ----------------------------------------------------------------------
# 1. Effective polarization from lattice regularization (continuum limit)
# ----------------------------------------------------------------------
# The integrals ∫ dk k^3 /(k^2+m^2) → (1/2) ln(Λ^2/m^2) + finite.
# We keep only the logarithmic part.
Pi_QED   = a0/(3*sp.pi) * sp.log(Lambda**2 / q**2)
Pi_N     = gN**2/(4*sp.pi) * sp.log(LambdaN**2 / q**2)
Pi_Delta = 3*gD**2/(4*sp.pi) * sp.log(LambdaD**2 / q**2)

Pi_eff = Pi_QED + Pi_N + Pi_Delta

print("Effective polarization (log part):")
sp.pprint(Pi_eff.simplify())
print()

# ----------------------------------------------------------------------
# 2. Running fine‑structure constant
# ----------------------------------------------------------------------
alpha_inv = 1/a0 - Pi_eff
alpha_fs  = 1/alpha_inv   # exact inverse
# Expand to first order in small couplings (a0, gN^2, gD^2)
alpha_fs_approx = sp.series(alpha_fs, a0, 0, 2).removeO() \
                  .series(gN**2, 0, 2).removeO() \
                  .series(gD**2, 0, 2).removeO()

print("α_fs expanded to first order in couplings:")
sp.pprint(alpha_fs_approx.simplify())
print()

# Expected boxed form (with electron mass m_e as IR scale)
m_e = sp.symbols('m_e', positive=True)
expected = a0 * (1
                 + a0/(3*sp.pi) * sp.log(Lambda**2 / m_e**2)
                 + gN**2/(4*sp.pi) * sp.log(LambdaN**2 / m_e**2)
                 + 3*gD**2/(4*sp.pi) * sp.log(LambdaD**2 / m_e**2))
print("Expected boxed form (with IR scale m_e):")
sp.pprint(expected.simplify())
print()

# Check equality (up to the choice of IR scale; we set q^2 → m_e^2)
check = sp.simplify(alpha_fs_approx - expected.subs({Lambda**2/q**2: Lambda**2/m_e**2,
                                                    LambdaN**2/q**2: LambdaN**2/m_e**2,
                                                    LambdaD**2/q**2: LambdaD**2/m_e**2}))
print("Difference (should be zero):", check)
print()

# ----------------------------------------------------------------------
# 3. Shredding condition from the Mexican‑hat potential
# ----------------------------------------------------------------------
V = lam/4 * (PhiN**2 + PhiD**2 - v**2)**2
d2V_dPhiD2 = sp.diff(V, PhiD, 2)
print("∂²V/∂Φ_Δ²:")
sp.pprint(d2V_dPhiD2)
print()

# Solve ∂²V/∂Φ_Δ² = 0 for the Shredding surface
shred_eq = sp.solve(sp.Eq(d2V_dPhiD2, 0), PhiN**2)
print("Shredding condition (Φ_N² expressed):")
sp.pprint(shred_eq)
print()

# Expected condition: Φ_N² + 3Φ_Δ² = v²  →  Φ_N² = v² - 3Φ_Δ²
expected_shred = v**2 - 3*PhiD**2
print("Expected Φ_N² from Φ_N² + 3Φ_Δ² = v²:")
sp.pprint(expected_shred)
print()

# Verify equivalence
shred_check = sp.simplify(shred_eq[0] - expected_shred)
print("Difference (should be zero):", shred_check)
print()

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
if shred_check == 0 and check == 0:
    print("✓ All mathematical checks pass.")
else:
    print("✗ Discrepancy detected – review the derivation.")