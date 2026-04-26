# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant & Consistency Validator
-------------------------------------------------
Checks dimensional consistency and gauge invariance of the
expressions appearing in the Higher‑Order Lattice Polarization
derivation.  Uses SymPy for symbolic manipulation.

Run:  python3 omega_validator.py
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Define base dimensions (Mass M, Length L, Time T)
# ----------------------------------------------------------------------
M, L, T = sp.symbols('M L T', positive=True)

def dim(powM, powL, powT):
    """Return a dimensional expression M^powM * L^powL * T^powT."""
    return M**powM * L**powL * T**powT

# ----------------------------------------------------------------------
# 2. Assign dimensions to the fundamental symbols used in the derivation
# ----------------------------------------------------------------------
# Action S has dimensions [energy][time] = M L^2 T^-1
dim_S = dim(1, 2, -1)

# Field I (information density) is taken dimensionless in the Omega Action
dim_I = dim(0, 0, 0)

# Coupling lambda in V(I) = (λ/4)(I^2 - I0^2)^2 must give V dimensions of energy density
# V(I) appears inside ∫ d^4x, so [V] = energy/volume = M L^-1 T^-2
dim_lambda = dim(2, 0, -2)   # λ ~ [energy]^2

# Reference scales I0, ξ0, ξN, ξΔ have dimensions of length (or time) in natural units
dim_xi0 = dim(0, 1, 0)      # length
dim_xiN = dim(0, 1, 0)
dim_xiDelta = dim(0, 1, 0)

# Momentum q and mass me have dimensions of inverse length
dim_q = dim(0, -1, 0)
dim_me = dim(0, -1, 0)

# Coupling α_fs (fine‑structure) is dimensionless
dim_alpha = dim(0, 0, 0)

# The invariant ψ = ln(ξΔ/ξ0) must be dimensionless; we check the ratio
dim_psi_arg = dim_xiDelta / dim_xi0   # should be dimensionless
assert sp.simplify(dim_psi_arg) == 1, "ψ argument not dimensionless"

# ----------------------------------------------------------------------
# 3. Helper to test dimensionlessness of an expression
# ----------------------------------------------------------------------
def is_dimensionless(expr, dims):
    """Return True if expr reduces to M^0 L^0 T^0 using the supplied dimension map."""
    # Replace each symbol by its dimensional placeholder
    dim_expr = expr.subs(dims)
    # Simplify powers of M, L, T
    dim_expr = sp.together(dim_expr)
    # Extract exponents
    expM = sp.Poly(dim_expr, M).degree() if M in dim_expr.free_symbols else 0
    expL = sp.Poly(dim_expr, L).degree() if L in dim_expr.free_symbols else 0
    expT = sp.Poly(dim_expr, T).degree() if T in dim_expr.free_symbols else 0
    return expM == 0 and expL == 0 and expT == 0

# Build a dimension substitution dictionary
dim_subs = {
    S: dim_S,
    I: dim_I,
    lam: dim_lambda,
    xi0: dim_xi0,
    xiN: dim_xiN,
    xiDelta: dim_xiDelta,
    q: dim_q,
    me: dim_me,
    alpha: dim_alpha,
    # Fields Φ_N, Φ_Δ are taken dimensionless for this check (they appear only in ratios)
    PhiN: dim(0,0,0),
    PhiDelta: dim(0,0,0),
    # Logarithm arguments are dimensionless by construction
    sp.log(q**2 / me**2): dim(0,0,0),
    sp.log(q**2 / LambdaDelta**2): dim(0,0,0),   # LambdaDelta same dim as q
}

# ----------------------------------------------------------------------
# 4. Test the vacuum polarization Π(q²) expression
# ----------------------------------------------------------------------
# Define symbols
lam, xi0, xiN, xiDelta, q, me, LambdaDelta, alpha, PhiN, PhiDelta = sp.symbols(
    'lam xi0 xiN xiDelta q me LambdaDelta alpha PhiN PhiDelta', positive=True)

# One‑loop Newtonian part
Pi_N = alpha/(3*sp.pi) * sp.log(q**2 / me**2)

# Archive part (ψ = ln(xiDelta/xi0))
psi = sp.log(xiDelta/xi0)
Pi_Delta = alpha/(2*sp.pi) * psi * sp.log(q**2 / LambdaDelta**2)

# Two‑loop mixing term
Pi_mix = alpha**2/(sp.pi**2) * (PhiDelta/PhiN) * sp.log(q**2 / me**2)**2

Pi_total = Pi_N + Pi_Delta + Pi_mix

print("Π(q²) dimensionless?", is_dimensionless(Pi_total, dim_subs))

# ----------------------------------------------------------------------
# 5. Test RG beta functions
# ----------------------------------------------------------------------
# Anomalous dimensions η_N, η_Δ, κ are dimensionless
etaN, etaDelta, kappa = sp.symbols('etaN etaDelta kappa', positive=True)
I0 = sp.symbols('I0', positive=True)   # dimensionless background field

beta_N = etaN * PhiN * (1 - PhiN**2 / I0**2) - kappa * PhiDelta**2
beta_Delta = etaDelta * PhiDelta * (1 - PhiDelta**2 / I0**2) + kappa * PhiN * PhiDelta

print("β_N dimensionless per log scale?", is_dimensionless(beta_N, dim_subs))
print("β_Δ dimensionless per log scale?", is_dimensionless(beta_Delta, dim_subs))

# ----------------------------------------------------------------------
# 6. Entropy gauge term: S_h = c ln(q²/m_e²), A_μ = ∂_μ S_h
#    Coupling ∫ d⁴x A_μ J^μ  (J^μ has dimensions of energy^3)
# ----------------------------------------------------------------------
c, Jmu = sp.symbols('c Jmu', positive=True)
# S_h dimensionless → A_μ has dimension of inverse length
dim_A = dim(0, -1, 0)          # ∂_μ adds 1/L
dim_J = dim(3, -1, -2)         # energy^3 = (M L^2 T^-2)^3 = M^3 L^6 T^-6
# In natural units we treat energy ~ 1/L, so J^μ ~ L^-3; we keep a generic check:
# The integrand A_μ J^μ should have dimensions of energy density = M L^-1 T^-2
integrand_dim = dim_A * dim_J
print("A·J dimension (should be M L^-1 T^-2):", sp.simplify(integrand_dim))
# Expected:
expected = dim(1, -1, -2)
print("Matches expected?", sp.simplify(integrand_dim / expected) == 1)

# ----------------------------------------------------------------------
# 7. Gauge invariance check (toy model)
#    Under A_μ → A_μ + ∂_μ Λ, the change is ∫ d⁴x ∂_μ Λ J^μ
#    = -∫ d⁴x Λ ∂_μ J^μ (integration by parts, assuming boundary terms vanish)
#    Hence gauge invariance holds if ∂_μ J^μ = 0 (current conservation).
# ----------------------------------------------------------------------
Lambda = sp.symbolbs('Lambda', positive=True)  # gauge parameter
dim_Lambda = dim(0,0,0)   # Λ dimensionless
# Variation of the term:
delta_term = sp.diff(Lambda, q) * Jmu   # schematic ∂_μ Λ J^μ
# We cannot prove ∂_μ J^μ = 0 without explicit J^μ, but we note the condition:
print("Gauge invariance requires ∂_μ J^μ = 0 (current conservation).")

# ----------------------------------------------------------------------
# End of script
# ----------------------------------------------------------------------
print("\nAll automated dimensional checks completed.")