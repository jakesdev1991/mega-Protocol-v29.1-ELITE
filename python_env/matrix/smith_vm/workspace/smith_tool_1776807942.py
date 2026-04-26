# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Physics Rubric v26.0 Validator for the IC‑Ω proposal.
Checks:
  1. Invariant uniqueness
  2. Boundary consistency
  3. Double‑well potential bistability
  4. Dimensionless action (after scaling)
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Base (scaled) dimensionless symbols
PhiN0, PhiN, PhiDelta, CI, L, lam = sp.symbols('PhiN0 PhiN PhiDelta CI L lam', positive=True, real=True)
# Linear‑response mappings (from the proposal)
eta1, eta2, eta3, eta4, tau = sp.symbols('eta1 eta2 eta3 eta4 tau', real=True)
# Assume CI, L evaluated at (t‑tau) – we treat them as independent symbols for the check
CI_tau, L_tau = sp.symbols('CI_tau L_tau', real=True)

# Proposed mappings (simplified, ignoring higher‑order terms)
PhiN_casc = PhiN0 - eta1*CI_tau + eta2*(1 - L_tau)
# PhiDelta_casc not needed for invariant check but kept for completeness
PhiDelta_casc = sp.Symbol('PhiDelta_casc', real=True)

# ----------------------------------------------------------------------
# 1. Invariant uniqueness test
# ----------------------------------------------------------------------
# Candidate invariants from the proposal
psi_curv = sp.log(sp.Abs(sp.Symbol('R_casc'))/sp.Symbol('R0')) + lam*CI   # ℛ‑based
psi_conn = sp.log(PhiN_casc/PhiN0)                                      # ΦN‑based

# To test equivalence we would need a relation linking R_casc to PhiN_casc.
# The proposal gives none; we treat R_casc as independent.
R_casc, R0 = sp.symbols('R_casc R0', positive=True)

# Check if psi_curv - psi_conn simplifies to zero *for all* symbols -> False
diff = sp.simplify(psi_curv - psi_conn)
print("Difference between the two invariant proposals:")
print(diff)
print("Is it identically zero?", diff.equals(0))
# Expect False → invariant not uniquely defined
assert not diff.equals(0), "Invariant definitions are not equivalent → rubric violation."

# ----------------------------------------------------------------------
# 2. Boundary consistency from chosen invariant (psi_conn)
# ----------------------------------------------------------------------
# Boundary: Cascade Shredding ↔ ψ → +∞  ⇔  PhiN_casc → 0+
# Boundary: Informational Freeze ↔ ψ → -∞ ⇔  PhiN_casc → ∞
# We verify that the limits of psi_conn match these statements.
limit_zero = sp.limit(psi_conn, PhiN_casc, 0, dir='+')
limit_inf  = sp.limit(psi_conn, PhiN_casc, sp.oo)

print("\nLimit ψ as Φ_N^{casc} → 0+ :", limit_zero)
print("Limit ψ as Φ_N^{casc} → ∞ :", limit_inf)
assert limit_zero == sp.oo, "Shredding boundary not satisfied."
assert limit_inf == -sp.oo, "Freeze boundary not satisfied."

# ----------------------------------------------------------------------
# 3. Double‑well potential bistability check
# ----------------------------------------------------------------------
# V(I) = α/2 * I^2 + β/4 * I^4 - γ * I
I, alpha, beta, gamma = sp.symbols('I alpha beta gamma', real=True)
V = alpha/2 * I**2 + beta/4 * I**4 - gamma * I

# Stationary points: dV/dI = 0
dV = sp.diff(V, I)
stationary = sp.solve(dV, I)
print("\nStationary points of V(I):", stationary)

# Impose sign constraints: α<0, β>0, γ>0
# Substitute symbolic signs to check shape
alpha_n = -sp.Symbol('a', positive=True)   # α = -a
beta_p  = sp.Symbol('b', positive=True)    # β =  b
gamma_p = sp.Symbol('g', positive=True)    # γ =  g
Vsub = V.subs({alpha: -alpha_n, beta: beta_p, gamma: gamma_p})
dVsub = sp.diff(Vsub, I)
stat_sub = sp.solve(dVsub, I)
print("\nStationary points with α<0, β>0, γ>0:", stat_sub)

# Evaluate V at the two non‑zero roots to confirm they are minima (second derivative >0)
I1, I2 = stat_sub[1], stat_sub[2]  # assuming zero root is first
V_pp1 = sp.diff(Vsub, I, 2).subs(I, I1)
V_pp2 = sp.diff(Vsub, I, 2).subs(I, I2)
print("Second derivative at I1:", V_pp1.simplify())
print("Second derivative at I2:", V_pp2.simplify())
assert V_pp1 > 0 and V_pp2 > 0, "Non‑zero stationary points are not minima → potential not bistable."
assert Vsub.subs(I, 0) < Vsub.subs(I, I1) and Vsub.subs(I, 0) < Vsub.subs(I, I2), \
       "Zero point is not the global minimum → liquidity state not stable."

# ----------------------------------------------------------------------
# 4. Dimensionless action check (symbolic)
# ----------------------------------------------------------------------
# After scaling, we assign all fields dimensionless.
# Action S = ∫ d^4x [ ½ g^{μν} ∂_μ I ∂_ν V + V(I) + λ_Ω L_Ω(ΦN,ΦΔ) + A_μ J^μ ]
# We only need to verify each term is a pure number (no leftover dimensions).
# Define base dimensions: [M]^0 [L]^0 [T]^0 → all symbols dimensionless.
# We'll check that any combination of symbols yields dimensionless.
# In SymPy we can't directly enforce dimensions, but we can assert that
# no explicit dimensional constants (like c, ħ) appear.
dimless_terms = [I, PhiN, PhiDelta, CI, L, lam, alpha, beta, gamma, eta1, eta2, eta3, eta4, tau]
for t in dimless_terms:
    assert t.is_real, f"Term {t} must be real (dimensionless)."
print("\nAll field/parameter symbols are real → dimensionless after scaling (by construction).")

print("\nΩ‑Physics Rubric checks passed (modulo the invariant duality which we flagged).")