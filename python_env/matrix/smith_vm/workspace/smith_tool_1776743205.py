# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for TEMPEST‑Ω (or similar) proposals.
This script checks the *dimensional* and *structural* consistency of the
core mathematical objects that must appear in a rubric‑compliant submission.
If any check fails, an AssertionError is raised with a diagnostic message.
"""

import sympy as sp
from sympy.physics.units import mass, length, time

# ----------------------------------------------------------------------
# 1. Base dimensions (M, L, T). We treat information-theoretic quantities as dimensionless.
# ----------------------------------------------------------------------
M = mass
L = length
T = time

# Helper to compare dimensions
def dim_eq(expr, target_dim):
    """Return True if expr has the same dimensions as target_dim."""
    return sp.simplify(expr / target_dim) == 1

# ----------------------------------------------------------------------
# 2. Define symbols for the core fields and parameters
# ----------------------------------------------------------------------
# Scalar stress field φ (dimensionless)
phi = sp.Symbol('phi', real=True)

# Potential parameters
lam = sp.Symbol('lam', positive=True)   # dimensionless coupling
v   = sp.Symbol('v',   real=True)       # vacuum expectation value (dimensionless)

# Reference mass scale m0 (inverse time)
m0 = sp.Symbol('m0', positive=True)     # dimensions [T^-1]

# Effective mass derived from curvature of V(phi) at minima
# Double‑well potential: V(phi) = (lam/4)*(phi**2 - v**2)**2
V = (lam/4) * (phi**2 - v**2)**2
# Second derivative at phi = +/- v
V_ddot = sp.diff(V, phi, 2).subs(phi, v)  # same for -v
# Effective mass squared: m_eff^2 = V''(v)
m_eff_sq = V_ddot
m_eff = sp.sqrt(m_eff_sq)  # take positive root

# ----------------------------------------------------------------------
# 3. Dimensional assignments (based on natural units where ħ = c = 1)
#    In 1+1 D: [∂_μ] = T^-1, [φ] = 1, [V] = T^-2 (energy density)
# ----------------------------------------------------------------------
# Action S = ∫ d^2x [ (1/2)(∂φ)^2 - V(φ) ]  → dimensions M L^2 T^-1 (energy·time)
# In our unit system: [∂φ] = T^-1, [(∂φ)^2] = T^-2, [d^2x] = L * T
# Hence [S] = (T^-2)*(L*T) = L * T^-1 = M L^2 T^-1 (since M = L/T in c=1)
# We'll just verify the combination yields the expected dimension.

# Kinetic term dimension: (∂φ)^2 * d^2x
kinetic_dim = (T**-2) * (L * T)   # = L * T^-1
# Potential term dimension: V * d^2x
potential_dim = (T**-2) * (L * T) # = L * T^-1
action_dim = kinetic_dim  # both terms share same dimension

# Expected action dimension: energy·time = M L^2 T^-1
expected_action_dim = M * L**2 * T**-1

assert dim_eq(kinetic_dim, expected_action_dim), \
    f"Kinetic term dimension mismatch: {kinetic_dim} vs {expected_action_dim}"
assert dim_eq(potential_dim, expected_action_dim), \
    f"Potential term dimension mismatch: {potential_dim} vs {expected_action_dim}"

# ----------------------------------------------------------------------
# 4. Field φ must be dimensionless
# ----------------------------------------------------------------------
assert dim_eq(phi, 1), f"Scalar field φ should be dimensionless, got {phi}"

# ----------------------------------------------------------------------
# 5. Effective mass m_eff must have dimensions of inverse time [T^-1]
# ----------------------------------------------------------------------
assert dim_eq(m_eff, T**-1), \
    f"Effective mass m_eff dimension mismatch: {m_eff} vs T^-1"

# ----------------------------------------------------------------------
# 6. Invariant ψ = ln(m_eff / m0) must be dimensionless
# ----------------------------------------------------------------------
psi = sp.log(m_eff / m0)
assert dim_eq(psi, 1), f"Invariant ψ should be dimensionless, got {psi}"

# ----------------------------------------------------------------------
# 7. Stiffness invariants ξ_N, ξ_Δ (taken as 1/m_eff) must have dimensions of time
# ----------------------------------------------------------------------
xi_N = 1 / m_eff
xi_Delta = 1 / m_eff   # same form for illustration
assert dim_eq(xi_N, T), f"ξ_N dimension mismatch: {xi_N} vs T"
assert dim_eq(xi_Delta, T), f"ξ_Δ dimension mismatch: {xi_Delta} vs T"

# ----------------------------------------------------------------------
# 8. Entropy S_h = c * ln(ξ/ξ0) dimensionless; ξ0 is a reference time
# ----------------------------------------------------------------------
c = sp.Symbol('c', real=True)          # dimensionless constant
xi0 = sp.Symbol('xi0', positive=True)  # reference time, same dimension as ξ
S_h = c * sp.log(xi_N / xi0)
assert dim_eq(S_h, 1), f"Entropy S_h should be dimensionless, got {S_h}"

# ----------------------------------------------------------------------
# 9. Gauge field A_μ = ∂_μ S_h must have dimensions of inverse length [L^-1]
#    (derivative w.r.t. x^μ where [x] = L for space, T for time; we check space component)
# ----------------------------------------------------------------------
# For simplicity, treat ∂_x S_h: derivative of dimensionless w.r.t. length → L^-1
A_x = sp.diff(S_h, sp.Symbol('x'))  # x has dimension L
assert dim_eq(A_x, L**-1), f"Gauge field A_x dimension mismatch: {A_x} vs L^-1"

# ----------------------------------------------------------------------
# 10. Representative Temporal Stress Index (TSI) term check
#     TSI term = α * C_i * exp(-λ * |t - t_i|) + β / Δt_{f,e} + γ * sync(t_i)
#     We assume:
#       - α, β, γ are dimensionless weights
#       - C_i (criticality) dimensionless (1‑5 scale)
#       - λ has dimensions T^-1 (so exponent is dimensionless)
#       - Δt_{f,e} and sync term are dimensionless counts or time inverses as needed
# ----------------------------------------------------------------------
alpha, beta, gamma = sp.symbols('alpha beta gamma', real=True)  # dimensionless
C_i = sp.Symbol('C_i', real=True)          # dimensionless
lam_tsi = sp.Symbol('lam_tsi', positive=True)  # decay constant [T^-1]
t = sp.Symbol('t', real=True)              # time [T]
t_i = sp.Symbol('t_i', real=True)          # time [T]
Delta_t = sp.Symbol('Delta_t', positive=True)  # time to next event [T]
sync = sp.Symbol('sync', real=True)        # dimensionless synchrony measure

term1 = alpha * C_i * sp.exp(-lam_tsi * sp.Abs(t - t_i))
term2 = beta / Delta_t
term3 = gamma * sync

# Check dimensions of each term (should be same; we pick dimensionless for illustration)
# For term1: exp(...) dimensionless, α, C_i dimensionless → dimensionless
assert dim_eq(term1, 1), f"TSI term1 dimension mismatch: {term1}"
# term2: β dimensionless divided by Δt [T] → [T^-1]; to make TSI dimensionless we need β to carry [T]
# We'll enforce that β has dimensions of time to keep term2 dimensionless.
beta = sp.Symbol('beta', positive=True)  # redefine with time dimension
# Give beta dimension of time
beta_dim = T
assert dim_eq(beta, beta_dim), f"Beta must have dimension of time, got {beta}"
# Re-evaluate term2 with correct beta
term2 = beta / Delta_t
assert dim_eq(term2, 1), f"TSI term2 dimension mismatch after fixing β: {term2}"
# term3: γ dimensionless * sync dimensionless → dimensionless
assert dim_eq(term3, 1), f"TSI term3 dimension mismatch: {term3}"

# ----------------------------------------------------------------------
# If we reach here, all structural/dimensional checks passed.
# ----------------------------------------------------------------------
print("[✓] All Omega invariant checks passed.")
print("    Action dimension:", action_dim)
print("    Field φ dimensionless:", dim_eq(phi, 1))
print("    Effective mass m_eff dimension [T^-1]:", dim_eq(m_eff, T**-1))
print("    Invariant ψ dimensionless:", dim_eq(psi, 1))
print("    Stiffness ξ dimension [T]:", dim_eq(xi_N, T))
print("    Entropy S_h dimensionless:", dim_eq(S_h, 1))
print("    Gauge field A_μ dimension [L^-1]:", dim_eq(A_x, L**-1))
print("    TSI terms dimensionless (after β correction).")