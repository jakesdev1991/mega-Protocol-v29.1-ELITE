# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# base dimensions: M (mass), L (length), T (time)
# in natural units ħ = 1 => action dimensionless
# c = 1 => L = T
M, L, T = sp.symbols('M L T')
# define derived dimensions
action_dim = 1  # dimensionless
# fields
# I (information content) dimensionless per solution
I_dim = 1
# phi_N, phi_Delta assumed same dimension as I
phi_dim = I_dim
# I0 same as I
I0_dim = I_dim
# lambda from potential V(I) = (lambda/4)*(I^2 - I0^2)^2
# V(I) must have dimensions of energy = 1/T (since action = ∫ L dt, L = energy)
energy_dim = 1/T
# solve for lambda dimension: lambda * I^4 ~ energy
lambda_dim = energy_dim / I_dim**4
# kinetic term (1/2)*(dI/dt)^2
# dI/dt has dimension I/T
kinetic_dim = (I_dim / T)**2
# total Lagrangian dimension should be energy
Lagrangian_dim = kinetic_dim + lambda_dim * I_dim**4
print("Lagrangian dimension:", Lagrangian_dim.simplify())
print("Should equal energy dimension (1/T):", energy_dim)
print("Match?", sp.simplify(Lagrangian_dim - energy_dim) == 0)

# invariants
psi = sp.log(phi_dim / I0_dim)  # dimensionless
print("\nPsi dimension (should be 1):", psi)

# stiffnesses: xi_N^{-2} = lambda*(3 phi_N^2 + phi_Delta^2 - I0^2)
# xi_N has dimension of length (L)
xi_dim = L
xi_inv2_dim = 1 / xi_dim**2
rhs_stiff_dim = lambda_dim * phi_dim**2
print("\nXi^{-2} dimension:", xi_inv2_dim.simplify())
print("RHS stiffness dimension:", rhs_stiff_dim.simplify())
print("Match?", sp.simplify(xi_inv2_dim - rhs_stiff_dim) == 0)

# lattice spacing a = xi_0 * exp(-psi)
# xi_0 same dimension as xi
xi0_dim = xi_dim
a_dim = xi0_dim  # exp(-psi) dimensionless
print("\nLattice spacing a dimension:", a_dim.simplify())
print("Should be length:", xi_dim)
print("Match?", sp.simplify(a_dim - xi_dim) == 0)

# Yukawa coupling g_Delta dimensionless (as assumed)
g_dim = 1
# beta function beta(g) = g^3/(16 pi^2) -> dimensionless
beta_dim = g_dim**3
print("\nBeta(g) dimension:", beta_dim)
print("Should be dimensionless:", 1)
print("Match?", sp.simplify(beta_dim - 1) == 0)

# Landau pole scale: Lambda_LP = mu0 * exp(8 pi^2 / g^2)
# exponent dimensionless, mu0 has dimension of mass (or 1/T)
mu0_dim = 1/T  # energy scale
Lambda_dim = mu0_dim
print("\nLandau pole dimension:", Lambda_dim.simplify())
print("Should be 1/T:", mu0_dim)
print("Match?", sp.simplify(Lambda_dim - mu0_dim) == 0)

# Poisson recovery: Laplacian phi_N ~ source
# Laplacian adds 1/L^2
laplacian_phi_dim = phi_dim / L**2
# source term: 4 pi G rho, G has dimension L^3/(M T^2), rho = M/L^3
G_dim = L**3/(M*T**2)
rho_dim = M/L**3
source_dim = G_dim * rho_dim
print("\nLaplacian phi_N dimension:", laplacian_phi_dim.simplify())
print("Source dimension:", source_dim.simplify())
print("Match?", sp.simplify(laplacian_phi_dim - source_dim) == 0)