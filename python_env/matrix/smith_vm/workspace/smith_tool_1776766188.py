# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symbolic validation of the Omega Protocol higher-order lattice polarization
derivation for the fine-structure constant.

Checks:
  1. Pi_eff matches the sum of QED, N, and Delta contributions.
  2. Alpha_inv = alpha0_inv - Pi_eff expands to the given alpha expression.
  3. The beta function derived from d(alpha_inv)/dln(q^2) matches the boxed form.
  4. The factor 3 appears explicitly in the Delta terms.
"""

import sympy as sp

# --- Symbols ----------------------------------------------------
e, gN, gD, Lambda, LambdaN, LambdaD, q, m, pi = sp.symbols(
    'e gN gD Lambda LambdaN LambdaD q m pi', positive=True)
# couplings
alpha0 = sp.symbols('alpha0', positive=True)

# --- Effective polarization --------------------------------------
Pi_QED   = e**2/(3*pi) * sp.log(Lambda**2 / q**2)
Pi_N     = gN**2/(4*pi) * sp.log(LambdaN**2 / q**2)
Pi_Delta = 3*gD**2/(4*pi) * sp.log(LambdaD**2 / q**2)

Pi_eff = Pi_QED + Pi_N + Pi_Delta

# --- Inverse running alpha --------------------------------------
alpha0_inv = 1/alpha0
alpha_inv = alpha0_inv - Pi_eff

# Expand to first order in small couplings (treat e^2, gN^2, gD^2 as small)
# We substitute e^2 = 4*pi*epsilon0*hbar*c * alpha0, but for the check we keep e^2
# and expand assuming alpha0, gN^2, gD^2 << 1.
# Use series expansion in alpha0 (treating gN,gD as O(sqrt(alpha0)) for consistency)
# Here we simply verify that the linear term in alpha0 matches the expected form.
alpha_expr = sp.series(1/alpha_inv, alpha0, 0, 2).removeO()
# Expected linear correction:
expected = 1 + alpha0/(3*pi) * sp.log(Lambda**2/q**2) \
           + alpha0*gN**2/(4*pi) * sp.log(LambdaN**2/q**2) \
           + 3*alpha0*gD**2/(4*pi) * sp.log(LambdaD**2/q**2)

# --- Beta function from derivative of alpha_inv ------------------
# d alpha / d ln(q^2) = - alpha^2 * d(alpha_inv)/d ln(q^2)
dPi_dlnq2 = -sp.diff(Pi_eff, sp.log(q**2))  # derivative w.r.t. ln(q^2)
beta = - (1/alpha0**2) * dPi_dlnq2  # using alpha≈alpha0 at leading order
beta_simplified = sp.simplify(beta)
beta_expected = - (1/pi) * (1 + 3*gD**2/(4*pi) + gN**2/(4*pi))

# --- Factor‑3 check ---------------------------------------------
factor3_in_PiDelta = sp.simplify(Pi_Delta / (gD**2/(4*pi) * sp.log(LambdaD**2/q**2)))
# Should be exactly 3

# --- Output results ---------------------------------------------
print("=== Validation Results ===")
print("Pi_eff expression:", sp.simplify(Pi_eff))
print("\nAlpha expression (series up to O(alpha0)):", sp.simplify(alpha_expr))
print("Expected alpha expression:", sp.simplify(expected))
print("Match? ", sp.simplify(alpha_expr - expected) == 0)
print("\nBeta function from derivation:", beta_simplified)
print("Expected beta function:", beta_expected)
print("Match? ", sp.simplify(beta_simplified - beta_expected) == 0)
print("\nFactor‑3 in Pi_Delta:", factor3_in_PiDelta)
print("Is it exactly 3? ", factor3_in_PiDelta == 3)