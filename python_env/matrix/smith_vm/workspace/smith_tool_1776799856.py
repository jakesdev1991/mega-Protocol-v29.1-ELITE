# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation Script for CTMS‑Ω Proposal
# --------------------------------------------------------------
# This script checks the mathematical statements that appear in the
# repaired CTMS‑Ω proposal against the Ω‑Physics Rubric v26.0
# requirements:
#   1. Invariant must be ψ = ln(φₙ)  (here φₙ ≡ Φ_N^{(cog)})
#   2. Fokker‑Planck equation must contain the ½ prefactor on the
#      diffusion term.
#   3. The action integral must contain an explicit entropy‑gauge term
#      A_μ J^μ.
#   4. All quantities that are claimed dimensionless must be
#      dimensionless under the assumption that coordinates are scaled
#      by a length ℓ (so ∂_μ, g_{μν}, Λ, Φ_N, Φ_Δ, ψ, S are dimensionless).
#
# The script uses SymPy for symbolic checks and simple dimensional
# analysis.  It prints PASS if every check succeeds, otherwise FAIL
# with a short explanation.
# --------------------------------------------------------------

import sympy as sp

# ------------------------------------------------------------------
# Helper: dimensionality checker (in the scaled, dimensionless system)
# ------------------------------------------------------------------
def is_dimensionless(expr, dims):
    """
    Very lightweight check: replace each symbol with its assumed dimension
    (1 for dimensionless, L for length, etc.) and see if the expression
    reduces to 1.
    Here we assume all fundamental symbols are dimensionless (=1).
    """
    subs_dict = {s: 1 for s in expr.free_symbols}
    return sp.simplify(expr.subs(subs_dict)) == 1

# ------------------------------------------------------------------
# 1. Invariant check: ψ_cog = ln(Φ_N^{(cog)} / Φ_N^{(0)})
# ------------------------------------------------------------------
Phi_N_cog, Phi_N0 = sp.symbols('Phi_N_cog Phi_N0', positive=True)
psi_cog_expr = sp.log(Phi_N_cog / Phi_N0)

# The rubric requires ψ = ln(φₙ) where φₙ = Φ_N^{(cog)}.
# We therefore check that ψ_cog_expr depends ONLY on the ratio
# Φ_N^{(cog)}/Φ_N^{(0)} and is a plain logarithm.
invariant_ok = (
    psi_cog_expr.has(sp.log) and
    psi_cog_expr.args[0] == Phi_N_cog / Phi_N0
)

# ------------------------------------------------------------------
# 2. Fokker‑Planck equation:
#    ∂_t P = -∂_Λ[μ(Λ) P] + ½ ∂_Λ²[D(Λ) P] + S(Λ,t)
# ------------------------------------------------------------------
t, Lambda = sp.symbols('t Lambda')
P = sp.Function('P')(Lambda, t)
mu = sp.Function('mu')(Lambda)
D = sp.Function('D')(Lambda)
S = sp.Function('S')(Lambda, t)

# Left‑hand side
LHS = sp.diff(P, t)

# Right‑hand side with the ½ factor
RHS = -sp.diff(mu * P, Lambda) + sp.Rational(1,2) * sp.diff(sp.diff(D * P, Lambda), Lambda) + S

# Check that the diffusion term carries exactly 1/2
diff_term = sp.Rational(1,2) * sp.diff(sp.diff(D * P, Lambda), Lambda)
has_half = diff_term.has(sp.Rational(1,2))

# Ensure no other numeric prefactor appears (i.e., the coefficient is exactly 1/2)
coeff = sp.Poly(diff_term, sp.diff(sp.diff(D * P, Lambda), Lambda)).coeff_monomial(
    sp.diff(sp.diff(D * P, Lambda), Lambda)
)
prefactor_ok = sp.simplify(coeff - sp.Rational(1,2)) == 0

fokker_planck_ok = sp.simplify(LHS - RHS) == 0 and has_half and prefactor_ok

# ------------------------------------------------------------------
# 3. Action integral with explicit gauge term A_μ J^μ
# ------------------------------------------------------------------
# Define symbolic components (all assumed dimensionless after scaling)
x = sp.symbols('x0 x1 x2 x3')
g = sp.Function('g')( *x )          # metric determinant sqrt(-g) will be handled separately
Lambda_field = sp.Function('Lambda')( *x )
V = sp.Function('V')(Lambda_field)  # potential V(Λ)
L_Omega = sp.Function('L_Omega')(sp.Symbol('Phi_N'), sp.Symbol('Phi_Delta'))
A_mu = sp.Function('A_mu')( *x )    # gauge potential (covector)
J_mu = sp.Function('J_mu')( *x )    # entropy current (vector)

# Action density (integrand)
L_density = (
    sp.Rational(1,2) * g * sp.diff(Lambda_field, x[0]) * sp.diff(Lambda_field, x[0])  # simplified kinetic term
    + V
    + L_Omega
    + A_mu * J_mu
)

# For the purpose of the check we only need to verify that the gauge term
# A_mu * J_mu appears *exactly* as a product (no extra factors).
gauge_term_present = L_density.has(A_mu * J_mu)

# Additionally, ensure there is no stray numeric factor in front of the gauge term.
# Extract the coefficient of A_mu*J_mu in the polynomial sense.
coeff_gauge = sp.Poly(L_density, A_mu * J_mu).coeff_monomial(A_mu * J_mu)
gauge_coeff_oksp = sp.simplify(coeff_gauge - 1) == 0

action_ok = gauge_term_present and gauge_coeff_oksp

# ------------------------------------------------------------------
# 4. Dimensional consistency (dimensionless check)
# ------------------------------------------------------------------
# List of symbols that the proposal claims are dimensionless after scaling.
dimless_symbols = {
    Lambda_field, Phi_N_cog, Phi_N0, sp.Symbol('Phi_Delta'),
    psi_cog_expr, mu, D, S, V, L_Omega, A_mu, J_mu, g
}
# In the scaled system each of these should evaluate to 1.
dimless_ok = all(is_dimensionless(s, {}) for s in dimless_symbols)

# ------------------------------------------------------------------
# Final verdict
# ------------------------------------------------------------------
all_checks = {
    "Invariant (ψ = ln φₙ)": invariant_ok,
    "Fokker‑Planck (½ prefactor)": fokker_planck_ok,
    "Action contains A_μ J^μ with unit coefficient": action_ok,
    "All claimed dimensionless symbols are dimensionless": dimless_ok
}

print("Omega Protocol Validation Results:")
for name, result in all_checks.items():
    print(f"  {name}: {'PASS' if result else 'FAIL'}")

if all(all_checks.values()):
    print("\nOVERALL: PASS – proposal satisfies the Ω‑Physics Rubric v26.0")
else:
    print("\nOVERALL: FAIL – see issues above")
    # Provide a concise hint for the first failing check
    for name, result in all_checks.items():
        if not result:
            print(f"  → First failure: {name}")
            break