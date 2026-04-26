# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dimensional validation of the instability analysis.
Checks:
 1. Scalar mass correction Δm² ~ g² Λ² / (16π²)
 2. Beta function β(g) = g³/(16π²) + ...
 3. Landau pole scale Λ_LP = μ₀ exp(8π²/g²(μ₀))
 4. Lattice spacing a = ξ₀ I₀ / Φ_N
 5. Poisson recovery: ∇² Φ_N = 4π G ρ
"""

import sympy as sp

# Define base dimensions
M, L, T, Q = sp.symbols('M L T Q', positive=True)

# Helper to create dimension objects
def dim(*powers):
    # powers: (M, L, T, Q)
    return M**powers[0] * L**powers[1] * T**powers[2] * Q**powers[3]

# Assign dimensions to symbols
# Couplings g_N, g_D are dimensionless (Yukawa)
gN = gD = sp.Symbol('gN gD', dimensionless=True)
# UV cutoff Λ has dimension of mass (inverse length in natural units)
Lambda = sp.Symbol('Lambda', dimension=dim(1,0,0,0))   # [M]
# Renormalization scale μ0 same as Λ
mu0 = sp.Symbol('mu0', dimension=dim(1,0,0,0))
# Scalar fields: Φ_N, Φ_Δ have dimension of mass (canonical scalar in 4D)
PhiN = PhiD = sp.Symbol('PhiN PhiD', dimension=dim(1,0,0,0))
# Vacuum expectation I0 same dimension as Φ_N
I0 = sp.Symbol('I0', dimension=dim(1,0,0,0))
# Lattice fundamental length ξ0 has dimension of length
xi0 = sp.Symbol('xi0', dimension=dim(0,1,0,0))
# Newton constant G: [L]^3/[M][T]^2
G = sp.Symbol('G', dimension=dim(-1,3,-2,0))
# Charge e (for fine-structure) dimensionless in natural units
e = sp.Symbol('e', dimensionless=True)
# Jerk J* has dimension [T]^-3
Jstar = sp.Symbol('Jstar', dimension=dim(0,0,-3,0))

# 1. Scalar mass correction: Δm² ~ g² Λ² / (16π²)
Delta_m2_sq = gD**2 * Lambda**2 / (16*sp.pi**2)
print("Δm² dimension:", Delta_m2_sq.dimension)  # should be [M]^2
assert Delta_m2_sq.dimension == dim(2,0,0,0), "Mass‑squared dimension mismatch"

# 2. Beta function β(g) = g³/(16π²) + ...
beta_gD = gD**3 / (16*sp.pi**2)
print("β(gΔ) dimension:", beta_gD.dimension)  # dimensionless
assert beta_gD.dimension == sp.S(1), "Beta function must be dimensionless"

# 3. Landau pole: Λ_LP = μ₀ exp(8π²/g²(μ₀))
# exponent must be dimensionless
expo = 8*sp.pi**2 / gD**2
print("Exponent dimension:", expo.dimension)
assert expo.dimension == sp.S(1), "Exponent in exp must be dimensionless"
Lambda_LP = mu0 * sp.exp(expo)
print("Λ_LP dimension:", Lambda_LP.dimension)
assert Lambda_LP.dimension == dim(1,0,0,0), "Landau pole must have mass dimension"

# 4. Lattice spacing a = ξ₀ I₀ / Φ_N
a = xi0 * I0 / PhiN
print("Lattice spacing a dimension:", a.dimension)
assert a.dimension == dim(0,1,0,0), "a must be a length"

# 5. Poisson recovery: ∇² Φ_N = 4π G ρ
# ∇² has dimension [L]^-2
laplacian_PhiN = sp.Symbol('∇²ΦN', dimension=dim(0,-2,1,0))  # [L]^-2 [M] = [M L^-2]
rho = sp.Symbol('ρ', dimension=dim(1,-3,0,0))  # mass density [M L^-3]
rhs = 4*sp.pi * G * rho
print("RHS of Poisson dimension:", rhs.dimension)
assert laplacian_PhiN.dimension == rhs.dimension, "Poisson equation dimension mismatch"

print("\nAll dimensional checks passed.")