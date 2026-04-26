# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith validation script for the Higher-Order Lattice Polarization derivation.
Checks consistency between the explicit running of α_fs and the quoted β-function.
"""

import sympy as sp

# Symbols
α0, gN, gΔ, Λ, ΛN, ΛΔ, q = sp.symbols('α0 gN gΔ Λ ΛN ΛΔ q', positive=True)
# Coefficients as in the *original* boxed formula (missing α0 in g-terms)
A_orig = α0/(3*sp.pi)                     # QED piece
B_orig = gN**2/(4*sp.pi)                  # Newtonian piece (missing α0)
C_orig = 3*gΔ**2/(4*sp.pi)                # Archive piece (missing α0)

# Coefficients as in the *corrected* formula (α0 present)
A_corr = α0/(3*sp.pi)
B_corr = α0*gN**2/(4*sp.pi)
C_corr = 3*α0*gΔ**2/(4*sp.pi)

# Generic running coupling: α = α0 * [1 + A*ln(Λ^2/q^2) + B*ln(ΛN^2/q^2) + C*ln(ΛΔ^2/q^2)]
def beta_from_coeffs(A, B, C):
    # α(q^2)
    α = α0 * (1 + A*sp.log(Λ**2/q**2) + B*sp.log(ΛN**2/q**2) + C*sp.log(ΛΔ**2/q**2))
    # dα/d ln(q^2)  (note: d/d ln(q^2) = q^2 * d/d(q^2))
    beta = sp.diff(α, sp.log(q**2))
    return sp.simplify(beta)

beta_orig = beta_from_coeffs(A_orig, B_orig, C_orig)
beta_corr = beta_from_coeffs(A_corr, B_corr, C_corr)

# Quoted β-function (using α≈α0 at leading order)
beta_quoted = -α0**2/sp.pi * (1 + 3*gΔ**2/(4*sp.pi) + gN**2/(4*sp.pi))

print("β from original boxed formula:")
sp.pprint(beta_orig)
print("\nβ from corrected formula:")
sp.pprint(beta_corr)
print("\nQuoted β-function (leading order in α0):")
sp.pprint(beta_quoted)

# Check equality (up to ordering)
print("\nDoes original match quoted? ", sp.simplify(beta_orig - beta_quoted) == 0)
print("Does corrected match quoted? ", sp.simplify(beta_corr - beta_quoted) == 0)

# Optional: show the difference expressions
print("\nDifference (original - quoted):")
sp.pprint(sp.simplify(beta_orig - beta_quoted))
print("\nDifference (corrected - quoted):")
sp.pprint(sp.simplify(beta_corr - beta_quoted))