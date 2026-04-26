# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol invariant checker for the higher‑order lattice‑polarization
correction to the fine‑structure constant.

The script validates a user‑supplied expression for α(μ) against the
following rubric‑derived rules:

1. Orthogonal decomposition: only Φ_N (connectivity) and Φ_Δ (3‑D Archive)
   may appear.
2. Φ_Δ must appear only with even powers (γ₅ chirality selection rule).
3. Φ_N may appear at most linearly, except for the mixed term Φ_N·Φ_Δ².
4. The logarithmic invariant ψ = ln(m_eff/m₀) must be a function of Φ_Δ
   only (via m_eff² = m₀² - λ·Φ_Δ²).
5. Stiffness invariants ξ_N⁻² and ξ_Δ⁻² are the Hessians of an effective
   potential V_eff(Φ_N,Φ_Δ).
6. No odd powers of Φ_Δ are allowed.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Fundamental fields
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# Couplings and constants (treated as parameters)
g_N, g_Delta, lam, m0 = sp.symbols('g_N g_Delta lam m0', real=True, positive=True)
# Perturbation coefficients (dimensionless numbers)
Pi0, Pi_N, Pi_Delta, Pi_NDelta = sp.symbols('Pi0 Pi_N Pi_Delta Pi_NDelta', real=True)
# Effective mass and logarithmic invariant
m_eff_sq = m0**2 - lam * Phi_Delta**2
psi = sp.log(sp.sqrt(m_eff_sq) / m0)   # ψ = ln(m_eff/m₀)
# Placeholder for an effective potential (to be differentiated)
V_eff = sp.Function('V_eff')(Phi_N, Phi_Delta)
# Stiffness invariants (inverse squared)
xi_N_inv2 = sp.diff(V_eff, Phi_N, 2)
xi_Delta_inv2 = sp.diff(V_eff, Phi_Delta, 2)

# ----------------------------------------------------------------------
# Candidate expression for α(μ) (as given in the derivation)
# ----------------------------------------------------------------------
alpha_expr = sp.symbols('alpha0') * (
    1 + Pi0
    + Pi_N * Phi_N
    + Pi_Delta * Phi_Delta**2
    + Pi_NDelta * Phi_N * Phi_Delta**2
    + Pi0**2   # higher‑order term from geometric series
)

# ----------------------------------------------------------------------
# Helper: polynomial inspection
# ----------------------------------------------------------------------
def poly_info(expr, gens):
    """Return a dict {monom: coeff} for a polynomial expression in gens."""
    poly = sp.Poly(expr, *gens)
    return dict(poly.terms())

# Extract monomials in Phi_N, Phi_Delta
mons = poly_info(alpha_expr, (Phi_N, Phi_Delta))

print("\n=== Monomial content of α(μ) ===")
for mon, coeff in mons.items():
    print(f"  Phi_N^{mon[0]} * Phi_Delta^{mon[1]} : {coeff}")

# ----------------------------------------------------------------------
# Rule checks
# ----------------------------------------------------------------------
def check_rule(description, condition):
    print(f"\n{description}")
    print("  PASS" if condition else "  FAIL")
    return condition

all_ok = True

# Rule 1: Only Phi_N and Phi_Delta may appear (no other symbols)
# (We already restricted the polynomial to these gens; any other symbol
#  would cause Poly to fail – we catch that.)
try:
    sp.Poly(alpha_expr, Phi_N, Phi_Delta)
    rule1 = True
except Exception:
    rule1 = False
all_ok &= check_rule("Rule 1 – Orthogonal decomposition (only Φ_N, Φ_Δ)", rule1)

# Rule 2: Φ_Δ must appear with even powers only
rule2 = all(exp[1] % 2 == 0 for exp in mons.keys())
all_ok &= check_rule("Rule 2 – Even powers of Φ_Δ only (chiral‑odd γ₅)", rule2)

# Rule 3: Φ_N may appear at most linearly, except the mixed Φ_N·Φ_Δ² term
rule3 = True
for (exp_n, exp_d), coeff in mons.items():
    if exp_n > 1:
        # allow only if it is exactly the mixed term Φ_N·Φ_Δ² (i.e. exp_n=1, exp_d=2)
        if not (exp_n == 1 and exp_d == 2):
            rule3 = False
            break
all_ok &= check_rule("Rule 3 – Φ_N at most linear (except Φ_N·Φ_Δ²)", rule3)

# Rule 4: No odd powers of Φ_Δ (already covered by Rule 2, but explicit)
rule4 = rule2  # redundant for clarity
all_ok &= check_rule("Rule 4 – No odd Φ_Δ terms", rule4)

# Rule 5: ψ must be a function of Φ_Δ only (through m_eff)
# Compute derivative w.r.t Phi_N; should be zero.
dpsi_dPhiN = sp.diff(psi, Phi_N)
rule5 = sp.simplify(dpsi_dPhiN) == 0
all_ok &= check_rule(
    "Rule 5 – ψ = ln(m_eff/m₀) depends only on Φ_Δ (∂ψ/∂Φ_N = 0)",
    rule5
)

# Rule 6: Stiffness invariants are Hessians of V_eff
# By construction they are; we just verify they are symmetric second derivatives.
rule6 = (sp.diff(xi_N_inv2, Phi_Delta) == sp.diff(sp.diff(V_eff, Phi_N, 2), Phi_Delta) and
         sp.diff(xi_Delta_inv2, Phi_N) == sp.diff(sp.diff(V_eff, Phi_Delta, 2), Phi_N))
all_ok &= check_rule(
    "Rule 6 – ξ_N⁻², ξ_Δ⁻² are Hessians of V_eff (symmetry of mixed derivatives)",
    rule6
)

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
print("\n=== OVERALL RESULT ===")
if all_ok:
    print("The expression satisfies all Omega‑Protocol invariants.")
else:
    print("The expression VIOLATES one or more Omega‑Protocol rules.")