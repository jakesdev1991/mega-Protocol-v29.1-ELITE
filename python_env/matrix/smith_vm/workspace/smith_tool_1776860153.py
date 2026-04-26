# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validate TDIS-Ω field theory consistency.
Checks whether the action S[B] yields the proposed dynamics:
    ∂_t B = D ∇^2 B - λ (B - B_opt) + η - A
If not, the script highlights the discrepancy.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Coordinates: t, x, y, z (we keep spatial Laplacian symbolic)
t, x, y, z = sp.symbols('t x y z', real=True)
# Field B(t,x,y,z)
B = sp.Function('B')(t, x, y, z)
# Parameters
D, lam, B_opt = sp.symbols('D lam B_opt', real=True)
# Source / noise terms (treated as given functions)
eta = sp.Function('eta')(t, x, y, z)
A   = sp.Function('A')(t, x, y, z)

# ----------------------------------------------------------------------
# Metric: flat Minkowski with signature (+,-,-,-)
# sqrt(-g) = 1, g^{μν} ∂_μ B ∂_ν B = (∂_t B)^2 - (∂_x B)^2 - (∂_y B)^2 - (∂_z B)^2
# ----------------------------------------------------------------------
L_kin = 0.5 * (sp.diff(B, t)**2 - sp.diff(B, x)**2 - sp.diff(B, y)**2 - sp.diff(B, z)**2)

# Double-well potential V(B)
alpha, beta = sp.symbols('alpha beta', real=True)
V = alpha/2 * (B - B_opt)**2 + beta/4 * (B - B_opt)**4

# Lagrangian density (ignore Ω-coupling and A_μ J^μ for variation w.r.t B)
L = L_kin - V   # note: action S = ∫ L d^4x ; sign convention yields +V in E-L

# ----------------------------------------------------------------------
# Euler-Lagrange: ∂L/∂B - ∂_μ (∂L/∂(∂_μ B)) = 0
# ----------------------------------------------------------------------
# ∂L/∂B
dL_dB = sp.diff(L, B)

# ∂L/∂(∂_μ B) for each coordinate
dL_dB_t = sp.diff(L, sp.diff(B, t))
dL_dB_x = sp.diff(L, sp.diff(B, x))
dL_dB_y = sp.diff(L, sp.diff(B, y))
dL_dB_z = sp.diff(L, sp.diff(B, z))

# ∂_μ (∂L/∂(∂_μ B))
term_t = sp.diff(dL_dB_t, t)
term_x = sp.diff(dL_dB_x, x)
term_y = sp.diff(dL_dB_y, y)
term_z = sp.diff(dL_dB_z, z)

# Euler-Lagrange expression (should equal zero)
EL = dL_dB - (term_t + term_x + term_y + term_z)
# Simplify
EL_simp = sp.simplify(EL)
print("Euler-Lagrange equation (should be 0):")
sp.pprint(EL_simp)
print()

# ----------------------------------------------------------------------
# Expected dynamics from the thought (first-order in time)
# We move all terms to LHS: ∂_t B - D ∇^2 B + λ (B - B_opt) - η + A = 0
# ----------------------------------------------------------------------
laplacian_B = sp.diff(B, x, x) + sp.diff(B, y, y) + sp.diff(B, z, z)
expected = sp.diff(B, t) - D * laplacian_B + lam * (B - B_opt) - eta + A
expected_simp = sp.simplify(expected)
print("Thought-proposed dynamics (LHS = 0):")
sp.pprint(expected_simp)
print()

# ----------------------------------------------------------------------
# Compare: does EL_simp match expected_simp up to a factor?
# For the kinetic term we have □B = ∂_t^2 B - ∇^2 B.
# The EL gives: □B - V'(B) = 0  -> ∂_t^2 B - ∇^2 B - V'(B) = 0
# The thought proposes: ∂_t B - D ∇^2 B + λ (B - B_opt) - η + A = 0
# Clearly different orders; we can test by attempting to substitute
# a hypothetical relation ∂_t B = something and see if it holds.
# ----------------------------------------------------------------------
print("=== Consistency check ===")
# Try to see if EL can be rewritten as first-order by assuming ∂_t^2 B ≈ 0 (overdamped limit)
# In the overdamped limit we drop the second time derivative: ∂_t^2 B ≈ 0
EL_overdamped = sp.simplify(EL_simp.subs(sp.diff(B, t, t), 0))
print("Euler-Lagrange with ∂_t^2 B set to 0 (overdamped approximation):")
sp.pprint(EL_overdamped)
print()
# Compare to expected
diff = sp.simplify(EL_overdamped - expected)
print("Difference (overdamped EL - expected):")
sp.pprint(diff)
print()
if diff == 0:
    print("✓ Under the overdamped approximation the action reproduces the proposed dynamics.")
else:
    print("✗ Even with overdamped approximation the equations do NOT match.")
    print("  This indicates the action must be modified (e.g., add a Rayleigh dissipation function)")
    print("  or the dynamics must be changed to follow from the variational principle.")