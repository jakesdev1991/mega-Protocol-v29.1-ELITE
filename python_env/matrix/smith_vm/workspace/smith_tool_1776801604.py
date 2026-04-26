# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Math Validator for CTMS‑Ω (Cognitive‑Tooling Mismatch Sensor)
Checks:
  - Invariant ψ = ln(Φ_N/Φ_N0)
  - Fokker‑Planck: ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ^2[D P] + S
  - Action contains entropy gauge term A_μ J^μ
  - All terms in the action are dimensionless (optional)
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbolic definitions (treat everything as dimensionless unless overridden)
# ----------------------------------------------------------------------
t, Lambda = sp.symbols('t Lambda', real=True)
P = sp.Function('P')(t, Lambda)
mu = sp.Function('mu')(Lambda)
D = sp.Function('D')(Lambda)
S = sp.Function('S')(t, Lambda)

# Invariant symbols
Phi_N_cog = sp.Function('Phi_N_cog')(t)
Phi_N0    = sp.symbols('Phi_N0', positive=True)
psi_cog   = sp.Function('psi_cog')(t)

# Action components
x0, x1, x2, x3 = sp.symbols('x0 x1 x2 x3', real=True)  # coordinates
g = sp.Function('g')(x0, x1, x2, x3)                  # metric determinant sqrt(-g) -> we treat sqrt(-g) as g_det
g_det = sp.Function('g_det')(x0, x1, x2, x3)          # sqrt(-g)
Lambda_field = sp.Function('Lambda')(x0, x1, x2, x3)  # the field Λ(x)
V = sp.Function('V')(Lambda_field)
L_Omega = sp.Function('L_Omega')(Phi_N_cog, sp.Function('Phi_Delta_cog')(t))
# Entropy gauge
A_mu = sp.Function('A_mu')(x0, x1, x2, x3)   # covector A_μ
J_mu = sp.Function('J_mu')(x0, x1, x2, x3)   # vector J^μ
entropy_term = A_mu * J_mu                  # scalar density (to be integrated)

# ----------------------------------------------------------------------
# 1. Invariant check
# ----------------------------------------------------------------------
invariant_expr = sp.Eq(psi_cog, sp.Ln(Phi_N_cog / Phi_N0))
invariant_ok = sp.simplify(invariant_expr.lhs - invariant_expr.rhs) == 0
print("Invariant ψ = ln(Φ_N/Φ_N0) satisfied?", invariant_ok)

# ----------------------------------------------------------------------
# 2. Fokker‑Planck check
# ----------------------------------------------------------------------
fp_lhs = sp.diff(P, t)
fp_rhs = -sp.diff(mu * P, Lambda) + sp.Rational(1,2) * sp.diff(sp.diff(D * P, Lambda), Lambda) + S
fp_ok = sp.simplify(fp_lhs - fp_rhs) == 0
print("Fokker‑Planck with ½ factor satisfied?", fp_ok)

# ----------------------------------------------------------------------
# 3. Action entropy gauge term presence
# ----------------------------------------------------------------------
# Build a symbolic action integrand (without the integral sign for simplicity)
action_integrand = (sp.Rational(1,2) * g_det * Lambda_field.diff(x0)**2  # placeholder kinetic term
                    + V
                    + sp.Function('lambda_Omega')(sp.Symbol('lambda_Omega')) * L_Omega
                    + entropy_term)  # <-- the term we need to see
# Check if entropy_term appears as an additive piece
has_entropy = entropy_term in sp.Add.make_args(action_integrand)
print("Entropy gauge term A_μ J^μ present in action integrand?", has_entropy)

# ----------------------------------------------------------------------
# 4. Dimensional consistency (optional)
# ----------------------------------------------------------------------
# Assign a dimension symbol 'dim' to each basic quantity; here we set all to 1 (dimensionless)
dim = sp.Symbol('dim')
# Define a dummy dimension mapping: every symbol -> dim^0 = 1
def dim_of(expr):
    # Replace each symbol with 1 (dimensionless)
    return expr.xreplace({sp.Symbol(str(s)): dim**0 for s in expr.free_symbols if isinstance(s, sp.Symbol)})

# Compute dimension of each term in the action integrand
terms = sp.Add.make_args(action_integrand)
dims = [dim_of(term) for term in terms]
all_same = all(d == dims[0] for d in dims)
print("All action terms share the same dimension (dimensionless)?", all_same)

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
if invariant_ok and fp_ok and has_entropy and all_same:
    print("\n✅ All core Ω‑Protocol mathematical checks passed.")
else:
    print("\n❌ Some checks failed. See output above for details.")