# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Dimensional consistency validation for the higher‑order lattice polarization derivation
import sympy as sp

# Define base dimensions: [M] mass, [L] length, [T] time
# In natural units ħ = c = 1, we have [M] = [L]^{-1} = [T]^{-1}
# We'll use symbols for dimensions and verify that each expression is dimensionless or has the expected dimension.
M, L, T = sp.symbols('M L T')
# Define dimension of basic quantities
dim = {}
# Action S has dimension of [M][L]^2/[T] -> in natural units [T]^{-1}
dim['S'] = 1/T
# Information field I is dimensionless (entropy)
dim['I'] = 1
# Self‑coupling λ in V(I) = λ/4 (I^2 - I0^2)^2 must give [S] dimension
# Since I is dimensionless, λ must have same dimension as S
dim['λ'] = dim['S']
# Yukawa couplings g_N, g_Δ are dimensionless
dim['g_N'] = 1
dim['g_Δ'] = 1
# UV cutoff Λ has dimension of mass (inverse length/time)
dim['Λ'] = 1/L  # same as 1/T
# Field Φ_N, Φ_Δ have dimension of sqrt(λ)?? Actually from V(I) they are like fluctuations of I, dimensionless
# We treat them as dimensionless for the purpose of checking mass corrections
dim['Φ_N'] = 1
dim['Φ_Δ'] = 1
# Lattice spacing a has dimension of length
dim['a'] = L
# ξ_0 is a fundamental length scale
dim['ξ_0'] = L
# ψ = ln(Φ_N/I_0) is dimensionless (argument of log must be dimensionless)
dim['ψ'] = 1
# Stiffnesses ξ_N, ξ_Δ have dimension of length
dim['ξ_N'] = L
dim['ξ_Δ'] = L
# Fine‑structure constant α is dimensionless
dim['α'] = 1
# Mass squared dimension
dim['m2'] = 1/L**2

# Check key expressions
# 1. Quadratic mass correction: Δm^2 ~ g^2 Λ^2 / (16π^2)
expr1 = dim['g_N']**2 * dim['Λ']**2
print("Δm^2 dimension:", expr1, "expected:", dim['m2'], "match?", sp.simplify(expr1 - dim['m2']) == 0)

# 2. Landau pole exponent: Λ_LP = μ0 * exp(8π^2 / g_Δ^2)
# exponent must be dimensionless
exp_arg = 8*sp.pi**2 / dim['g_Δ']**2
print("Exponent dimension:", exp_arg, "dimensionless?", exp_arg == 1)
# Λ_LP inherits dimension of μ0 (cutoff)
dim['μ0'] = dim['Λ']
dim['Λ_LP'] = dim['μ0'] * sp.exp(exp_arg)  # exp of dimensionless is dimensionless
print("Λ_LP dimension:", dim['Λ_LP'], "expected:", dim['Λ'], "match?", sp.simplify(dim['Λ_LP'] - dim['Λ']) == 0)

# 3. Lattice spacing relation a = ξ_0 * exp(-ψ)
expr_a = dim['ξ_0'] * sp.exp(-dim['ψ'])
print("a dimension from relation:", expr_a, "expected:", dim['a'], "match?", sp.simplify(expr_a - dim['a']) == 0)

# 4. Action dimension check: S = ∫ dt [1/2 (dI/dt)^2 + V(I)]
# dI/dt has dimension of 1/T (since I dimensionless)
dim_dIdt = 1/T
kinetic = dim_dIdt**2 * T  # integrate dt adds T
potential = dim['λ']  # V(I) ~ λ * I^4, I dimensionless
print("Kinetic term dimension:", kinetic, "potential term dimension:", potential, "action dimension expected:", dim['S'])
print("Kinetic matches S?", sp.simplify(kinetic - dim['S']) == 0)
print("Potential matches S?", sp.simplify(potential - dim['S']) == 0)

# 5. Jerk invariant J* = d^3 I/dt^3 (dimension 1/T^3) – should remain unchanged
dim_J = 1/T**3
print("Jerk dimension:", dim_J)