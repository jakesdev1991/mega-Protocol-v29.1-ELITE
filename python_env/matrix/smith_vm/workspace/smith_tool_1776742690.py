# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Validation script for the Higher-Order Lattice Polarization corrections
# to the fine-structure constant in the Omega Protocol diagonal basis.
# This script checks:
#   1. The structure of the effective polarization Π_eff(q²)
#   2. The derived running α_fs(q²) expansion
#   3. The β‑function (RG equation) coefficient of the Φ_Δ term
#   4. That the factor 3 multiplying g_Δ² appears exactly as required.
#
# Uses SymPy for symbolic manipulation. If all checks pass, prints "PASS".

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Couplings and scales
e, gN, gD = sp.symbols('e gN gD', positive=True)          # e: bare charge, gN,gD: mode couplings
α0 = sp.symbols('α0', positive=True)                     # bare fine-structure constant α0 = e²/(4π)
# Momentum scales
q, Λ, ΛN, ΛD = sp.symbols('q Λ ΛN ΛD', positive=True)    # external momentum and UV cutoffs
# Logarithms
L  = sp.log(Λ**2 / q**2)
LN = sp.log(ΛN**2 / q**2)
LD = sp.log(ΛD**2 / q**2)

# ----------------------------------------------------------------------
# 1. Effective polarization Π_eff(q²) as given in the engine output
# ----------------------------------------------------------------------
# Standard QED one-loop term (leading log): (e²/3π) * ln(Λ²/q²)
Pi_QED = e**2 / (3 * sp.pi) * L

# Mode contributions: (gN²/4π) ln(ΛN²/q²)  and  (3 gD²/4π) ln(ΛD²/q²)
Pi_N   = gN**2 / (4 * sp.pi) * LN
Pi_D   = 3 * gD**2 / (4 * sp.pi) * LD

Pi_eff = Pi_QED + Pi_N + Pi_D
print("Effective polarization Π_eff(q²):")
sp.pprint(Pi_eff.simplify())
print()

# ----------------------------------------------------------------------
# 2. Inverse running coupling α_fs⁻¹(q²) = α0⁻¹ - Π_eff(q²)
# ----------------------------------------------------------------------
alpha_inv = 1/α0 - Pi_eff
print("Inverse coupling α_fs⁻¹(q²):")
sp.pprint(alpha_inv.simplify())
print()

# ----------------------------------------------------------------------
# 3. Expand α_fs(q²) to first order in small couplings (α0, gN², gD²)
#    α ≈ α0 [1 + α0 * Π_eff]  (since α0⁻¹ - Π ≈ α0 (1 + α0 Π))
# ----------------------------------------------------------------------
alpha_approx = α0 * (1 + α0 * Pi_eff)
print("Approximate α_fs(q²) (first order):")
sp.pprint(alpha_approx.expand().simplify())
print()

# ----------------------------------------------------------------------
# 4. Extract coefficients of the three logarithms
# ----------------------------------------------------------------------
coeff_L  = sp.collect(alpha_approx, L, evaluate=False).get(L, 0)
coeff_LN = sp.collect(alpha_approx, LN, evaluate=False).get(LN, 0)
coeff_LD = sp.collect(alpha_approx, LD, evaluate=False).get(LD, 0)

print("Coefficient of ln(Λ²/q²)  :", coeff_L.simplify())
print("Coefficient of ln(ΛN²/q²) :", coeff_LN.simplify())
print("Coefficient of ln(ΛD²/q²) :", coeff_LD.simplify())
print()

# Expected coefficients from the engine output:
expected_L  = α0**2 / (3 * sp.pi)
expected_LN = α0 * gN**2 / (4 * sp.pi)
expected_LD = 3 * α0 * gD**2 / (4 * sp.pi)

print("Expected coefficient of ln(Λ²/q²)  :", expected_L.simplify())
print("Expected coefficient of ln(ΛN²/q²) :", expected_LN.simplify())
print("Expected coefficient of ln(ΛD²/q²) :", expected_LD.simplify())
print()

# ----------------------------------------------------------------------
# 5. Check equality (should be True)
# ----------------------------------------------------------------------
check_L  = sp.simplify(coeff_L  - expected_L)  == 0
check_LN = sp.simplify(coeff_LN - expected_LN) == 0
check_LD = sp.simplify(coeff_LD - expected_LD) == 0

print("Check L  term matches:", check_L)
print("Check LN term matches:", check_LN)
print("Check LD term matches:", check_LD)
print()

# ----------------------------------------------------------------------
# 6. RG equation: β = dα/dln(q²) = - (α²/π) [1 + 3 gD²/(4π) + gN²/(4π)]
#    Compute β from alpha_inv and compare.
# ----------------------------------------------------------------------
# Treat α as function of ln(q²). Use derivative of alpha_inv:
# dα/dln(q²) = - α² * d(alpha_inv)/dln(q²)
lnq2 = sp.symbols('lnq2')
# Express logs in terms of lnq2: L = ln(Λ²) - lnq2, etc.
L_sub  = sp.log(Λ**2) - lnq2
LN_sub = sp.log(ΛN**2) - lnq2
LD_sub = sp.log(LD**2) - lnq2

Pi_eff_sub = (e**2/(3*sp.pi))*L_sub + (gN**2/(4*sp.pi))*LN_sub + (3*gD**2/(4*sp.pi))*LD_sub
alpha_inv_sub = 1/α0 - Pi_eff_sub

# derivative of inverse coupling w.r.t lnq2
d_alpha_inv_dlnq2 = sp.diff(alpha_inv_sub, lnq2)
# β = -α² * d(alpha_inv)/dlnq2
beta = -α0**2 * d_alpha_inv_dlnq2  # using α≈α0 at leading order for consistency
print("Beta function from derivation:")
sp.pprint(beta.simplify())
print()

# Expected beta (keeping α≈α0)
beta_expected = -α0**2/sp.pi * (1 + 3*gD**2/(4*sp.pi) + gN**2/(4*sp.pi))
print("Expected beta function:")
sp.pprint(beta_expected.simplify())
print()

beta_check = sp.simplify(beta - beta_expected) == 0
print("Beta function matches expected:", beta_check)
print()

# ----------------------------------------------------------------------
# Final verdict
# ----------------------------------------------------------------------
if all([check_L, check_LN, check_LD, beta_check]):
    print("PASS: All mathematical checks are consistent with the Omega Protocol invariants.")
else:
    print("FAIL: Discrepancy detected in the derivation.")