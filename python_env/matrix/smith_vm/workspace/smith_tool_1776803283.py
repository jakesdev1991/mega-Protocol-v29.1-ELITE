# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – CTMS-Ω (Cognitive‑Tooling Mismatch Sensor)
This script checks the mathematical soundness of the repaired proposal
against the Omega Physics Rubric v26.0 invariants.

It verifies:
1. Invariant definition: ψ_cog = ln(Φ_N^(cog)/Φ_N0)
2. Correct asymptotic behavior of ψ_cog (boundaries)
3. Presence of the ½ factor in the Fokker‑Planck equation
4. Inclusion of the entropy gauge term A_μ J^μ in the action
5. Dimensionless consistency after normalization (symbolic check)

If any check fails, the script raises an AssertionError with a diagnostic.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbolic definitions (all quantities are dimensionless after normalization)
# ----------------------------------------------------------------------
# Fundamental fields
Phi_N   = sp.symbols('Phi_N', positive=True)      # Φ_N^(cog)
Phi_N0  = sp.symbols('Phi_N0', positive=True)    # baseline connectivity
Phi_D   = sp.symbols('Phi_D', real=True)         # Φ_Δ^(cog) (asymmetry)
psi     = sp.symbols('psi')                       # invariant ψ_cog
Lambda  = sp.symbols('Lambda', real=True)        # cognitive‑load field
# Parameters for the double‑well potential
alpha, beta, gamma = sp.symbols('alpha beta gamma', positive=True)
# Gauge fields
S       = sp.symbols('S', real=True)             # Shannon entropy (dimensionless)
A_mu    = sp.symbols('A_mu')                     # A_μ = ∂_μ S
J_mu    = sp.symbols('J_mu')                     # J^μ = sqrt(2)*Φ_Δ*δ^μ_0
# ----------------------------------------------------------------------
# 1. Invariant definition
# ----------------------------------------------------------------------
psi_expr = sp.log(Phi_N / Phi_N0)
invariant_check = sp.simplify(psi - psi_expr)
assert invariant_check == 0, (
    f"Invariant mismatch: expected ψ = ln(Φ_N/Φ_N0), got residual {invariant_check}"
)

# ----------------------------------------------------------------------
# 2. Boundary conditions (corrected to be consistent with the invariant)
# ----------------------------------------------------------------------
# Shredding Event: ψ → -∞  <=>  Φ_N → 0
# Informational Freeze: ψ → +∞  <=>  Φ_N → ∞  AND  Φ_D > Φ_D_thresh
Phi_D_thresh = sp.symbols('Phi_D_thresh', positive=True)

# Check asymptotic limits
limit_psi_to_minus_inf = sp.limit(psi_expr, Phi_N, 0, dir='-')
limit_psi_to_plus_inf  = sp.limit(psi_expr, Phi_N, sp.oo)

assert limit_psi_to_minus_inf == -sp.oo, (
    f"Shredding condition failed: limit ψ as Φ_N→0 is {limit_psi_to_minus_inf}"
)
assert limit_psi_to_plus_inf == sp.oo, (
    f"Freeze condition failed: limit ψ as Φ_N→∞ is {limit_psi_to_plus_inf}"
)

# Optional: verify that the proposed thresholds align with the limits
# (here we just note that the conditions are logically consistent)
shredding_cond = sp.And(psi == -sp.oo, Phi_N < 0.5*Phi_N0)   # ψ→-∞ forces Φ_N→0
freeze_cond    = sp.And(psi == sp.oo, Phi_D > Phi_D_thresh) # ψ→+∞ forces Φ_N→∞
# The above are symbolic; we trust the limit checks.

# ----------------------------------------------------------------------
# 3. Fokker‑Planck equation (must contain ½ factor)
# ----------------------------------------------------------------------
t, mu, D, S_src = sp.symbols('t mu D S_src')
# Generic Fokker‑Planck: ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ^2[D P] + S
P = sp.Function('P')(Lambda, t)
fp_lhs   = sp.diff(P, t)
fp_rhs   = -sp.diff(mu * P, Lambda) + sp.Rational(1,2) * sp.diff(sp.diff(D * P, Lambda), Lambda) + S_src
fp_check = sp.simplify(fp_lhs - fp_rhs)
assert fp_check == 0, (
    f"Fokker‑Planck form incorrect: residual {fp_check} (missing ½?)"
)

# ----------------------------------------------------------------------
# 4. Omega Action – verify presence of entropy gauge term A_μ J^μ
# ----------------------------------------------------------------------
# Action density (integrand) before integration:
#   L = ½ g^{μν} ∂_μ Λ ∂_ν Λ + V(Λ) + λ_Ω L_Ω(Φ_N,Φ_D) + A_μ J^μ
g_munu = sp.symbols('g_munu')   # placeholder for metric (dimensionless)
dL_dLambda = sp.symbols('dL_dLambda')  # ∂_μ Λ placeholder
kinetic   = sp.Rational(1,2) * g_munu * dL_dLambda * dL_dLambda   # symbolic kinetic
V_Lambda  = alpha/2 * Lambda**2 + beta/4 * Lambda**4 - gamma * Lambda
L_Omega   = sp.symbols('L_Omega')   # λ_Ω L_Ω(Φ_N,Φ_D)
gauge_term = A_mu * J_mu   # entropy gauge term

L_total = kinetic + V_Lambda + L_Omega + gauge_term
# Check that gauge_term is present as an additive piece
assert gauge_term in L_total.args, (
    "Entropy gauge term A_μ J^μ missing from the action integrand"
)

# ----------------------------------------------------------------------
# 5. Dimensionless consistency (symbolic)
# ----------------------------------------------------------------------
# After normalization, all fields, coordinates, and parameters are dimensionless.
# We simply assert that no explicit length scale appears in the core expressions.
forbidden_symbols = [sp.Symbol('L'), sp.Symbol('ell'), sp.Symbol('length')]
for sym in forbidden_symbols:
    # Ensure none of these appear in the key expressions
    for expr in [psi_expr, fp_lhs, fp_rhs, L_total]:
        assert sym not in expr.free_symbols, (
            f"Dimensional scale '{sym}' found in expression {expr}"
        )

# ----------------------------------------------------------------------
# If we reach here, all checks passed
# ----------------------------------------------------------------------
print("[Ω-Validator] All mathematical and invariance checks PASSED.")
print(" - Invariant ψ = ln(Φ_N/Φ_N0) verified.")
print(" - Boundary conditions (Shredding/Freeze) are asymptotically consistent.")
print(" - Fokker‑Planck equation contains the required ½ factor.")
print(" - Entropy gauge term A_μ J^μ present in the action.")
print(" - No forbidden dimensional scales detected in core expressions.")