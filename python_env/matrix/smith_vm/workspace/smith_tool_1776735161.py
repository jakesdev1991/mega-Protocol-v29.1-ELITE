# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith – Omega Protocol Validation Script
Checks dimensional consistency and invariant relations for the
Higher-Order Lattice Polarization derivation.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Base dimension: Time (T). In natural units ħ = c = 1.
# ----------------------------------------------------------------------
T = sp.symbols('T', positive=True)   # dimension of time
# Derived dimensions
M = 1/T      # mass dimension (since ħ = M L^2 / T = 1 and L = T)
L = T        # length = time
E = M * L**2 / T**2  # energy = M L^2 / T^2 -> simplifies to 1/T
# Verify energy dimension
assert sp.simplify(E) == 1/T, "Energy dimension mismatch"

# ----------------------------------------------------------------------
# Symbolic fields and parameters (dimensionless unless noted)
# ----------------------------------------------------------------------
I, I0 = sp.symbols('I I0', dimensionless=True)   # information field, vev
gN, gD = sp.symbols('gN gD', dimensionless=True) # Yukawa couplings
lam = sp.symbols('lam', dimension=1/T**2)        # lambda from V(I)
psi = sp.symbols('psi', dimensionless=True)     # ln(Phi_N/I0)
PhiN, PhiD = sp.symbols('PhiN PhiD', dimensionless=True) # scalar modes
xi0 = sp.symbols('xi0', dimension=L)             # base length scale
a   = sp.symbols('a', dimension=L)               # lattice spacing
Lambda = sp.symbols('Lambda', dimension=1/L)     # UV cutoff (inverse length)
mu0 = sp.symbols('mu0', dimension=1/L)           # reference scale
G   = sp.symbols('G', dimension=L**2 / M)        # Newton constant
rho = sp.symbols('rho', dimension=M / L**3)      # mass density

# ----------------------------------------------------------------------
# 1. Action & potential dimensional check
# ----------------------------------------------------------------------
# Kinetic term: (1/2)*(dI/dt)^2
dt = sp.symbols('dt', dimension=T)
dIdt = sp.diff(I, dt)  # dimension: I/T -> 1/T
kin = sp.Rational(1,2) * dIdt**2
# Potential term: lambda/4 * (I^2 - I0^2)^2
pot = lam/4 * (I**2 - I0**2)**2
# Both must share same dimension
assert sp.simplify(kin.dim) == sp.simplify(pot.dim), "Action term dimension mismatch"

# ----------------------------------------------------------------------
# 2. Scalar mass correction
# ----------------------------------------------------------------------
Delta_m2 = gN**2 * Lambda**2 / (16*sp.pi**2)  # same form for gD
assert sp.simplify(Delta_m2.dim) == (1/T)**2, "Mass‑squared dimension mismatch"

# ----------------------------------------------------------------------
# 3. Beta function & Landau pole
# ----------------------------------------------------------------------
beta_gD = gD**3 / (16*sp.pi**2)
assert beta_gD.dim == sp.S(1), "Beta function must be dimensionless"
# Landau pole: mu0 * exp(8π^2/gD^2)
expo = 8*sp.pi**2 / gD**2
assert expo.dim == sp.S(1), "Exponent must be dimensionless"
Lambda_LP = mu0 * sp.exp(expo)
assert sp.simplify(Lambda_LP.dim) == (1/L), "Landau pole dimension mismatch"

# ----------------------------------------------------------------------
# 4. Lattice spacing dependence
# ----------------------------------------------------------------------
psi_def = sp.log(PhiN / I0)
assert psi_def.dim == sp.S(1), "psi must be dimensionless"
a_calc = xi0 * sp.exp(-psi_def)
assert sp.simplify(a_calc.dim) == L, "Lattice spacing dimension mismatch"

# ----------------------------------------------------------------------
# 5. Poisson recovery
# ----------------------------------------------------------------------
laplacian_PhiN = sp.diff(PhiN, sp.symbols('x', dimension=L), 2) \
               + sp.diff(PhiN, sp.symbols('y', dimension=L), 2) \
               + sp.diff(PhiN, sp.symbols('z', dimension=L), 2)
# laplacian dimension: PhiN / L^2 -> 1/L^2
assert sp.simplify(laplacian_PhiN.dim) == 1/L**2, "Laplacian dimension mismatch"
rhs = 4*sp.pi * G * rho
assert sp.simplify(rhs.dim) == 1/L**2, "Poisson RHS dimension mismatch"

# ----------------------------------------------------------------------
# 6. Entropy‑gauge link (dimensionless check)
# ----------------------------------------------------------------------
pk = sp.symbols('pk0:5')  # probabilities, dimensionless
Sh = -sp.sum(pk * sp.log(pk) for pk in pk)  # Shannon entropy
assert Sh.dim == sp.S(1), "Entropy must be dimensionless"

print("All dimensional and invariant checks passed.")