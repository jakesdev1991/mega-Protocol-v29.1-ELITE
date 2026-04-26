# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator
----------------------------------
Checks the three non‑negotiable mathematical conditions for a proposal
to be Ω‑Physics Rubric v26.0 compliant:

  1. Fokker‑Planck diffusion term carries factor 1/2.
  2. Action contains the entropy gauge coupling A_mu J^mu.
  3. Invariant ψ equals ln(Φ_N) (up to an additive constant).

The script is deliberately minimal: it works on symbolic expressions
provided as strings.  Replace the placeholder expressions with the
actual ones from the proposal to run a real validation.
"""

import sympy as sp
import sys

# ----------------------------------------------------------------------
# Helper: parse a string into a sympy expression (safe for our controlled input)
# ----------------------------------------------------------------------
def expr(s):
    return sp.sympify(s)

# ----------------------------------------------------------------------
# 1. Fokker‑Planck check
# ----------------------------------------------------------------------
# Canonical FP: ∂_t P = -∂_x[μ P] + (1/2) ∂_x^2[D P] + S
# We verify that the coefficient of the second‑order derivative term is 1/2.
# Assume the user supplies the expression for the RHS of the FP equation.
fp_rhs_str = "-mu*D_P + 0.5*D2_P + S"   # <-- replace with actual RHS from proposal
fp_rhs = expr(fp_rhs_str)

# Extract the term that multiplies the second‑order derivative (symbol D2_P)
# For simplicity we look for a term containing D2_P and check its coefficient.
coeff_D2 = sp.Poly(fp_rhs, sp.Symbol('D2_P')).coeff_monomial(sp.Symbol('D2_P')) if fp_rhs.has(sp.Symbol('D2_P')) else None

if coeff_D2 is None:
    print("[FAIL] Fokker‑Planck RHS does not contain a second‑order derivative term.")
    sys.exit(1)

if not sp.simplify(coeff_D2 - sp.Rational(1,2)) == 0:
    print(f"[FAIL] Fokker‑Planck diffusion coefficient = {coeff_D2}, expected 1/2.")
    sys.exit(1)
else:
    print("[PASS] Fokker‑Planck diffusion term has correct 1/2 factor.")

# ----------------------------------------------------------------------
# 2. Entropy gauge term in the action
# ----------------------------------------------------------------------
# Action S = ∫ d^4x sqrt(-g) [ ½ g^{μν} ∂_μΛ ∂_νΛ + V(Λ) + λ_Ω L_Ω(Φ_N,Φ_Δ) + A_μ J^μ ]
# We check that the integrand contains a term A_mu * J^mu.
action_integrand_str = "0.5*g^{mu nu}*dLambda_mu*dLambda_nu + V(Lambda) + lambda_Omega*L_Omega + A_mu*J^mu"
action_integrand = expr(action_integrand_str)

# Look for a product A_mu * J^mu (any contraction)
A_mu = sp.Symbol('A_mu')
J_mu = sp.Symbol('J_mu')
# Simple check: does the expression contain the product A_mu*J_mu?
if not action_integrand.has(A_mu*J_mu):
    print("[FAIL] Action integrand missing entropy gauge term A_mu J^mu.")
    sys.exit(1)
else:
    print("[PASS] Action contains entropy gauge term A_mu J^mu.")

# ----------------------------------------------------------------------
# 3. Invariant ψ = ln(Φ_N) (up to additive constant)
# ----------------------------------------------------------------------
# ψ_cog from proposal: ln(|R_cog|/R0) + λ * max(TFFI)
# We require ψ_cog - ln(Φ_N) to be a constant (i.e., independent of dynamical fields).
# For the test we treat Φ_N, R_cog, TFFI as independent symbols.
psi_cog_str = "log(abs(R_cog)/R0) + lam * max_TFFI"
psi_N_str   = "log(Phi_N)"   # the rubric‑required form

psi_cog = expr(psi_cog_str)
psi_N   = expr(psi_N_str)

# Compute difference and check if it depends on any of the dynamical fields.
diff = sp.simplify(psi_cog - psi_N)
# List of symbols that should *not* appear in the difference for a pure constant.
forbidden = [sp.Symbol('R_cog'), sp.Symbol('max_TFFI'), sp.Symbol('Phi_N')]
depends_on_forbidden = any(diff.has(sym) for sym in forbidden)

if depends_on_forbidden:
    print(f"[FAIL] Invariant difference depends on dynamical fields: {diff}")
    print("       ψ must be ln(Φ_N) up to an additive constant only.")
    sys.exit(1)
else:
    print(f"[PASS] Invariant ψ reduces to ln(Φ_N) + constant: {diff}")
    # Optionally show the constant
    const = sp.simplify(diff - sp.log(sp.Symbol('Phi_N')))
    if const != 0:
        print(f"       Constant offset = {const}")

# ----------------------------------------------------------------------
# If we reach here, all Ω‑critical checks passed.
# ----------------------------------------------------------------------
print("\nAll Ω‑Protocol invariant checks PASSED.")
sys.exit(0)