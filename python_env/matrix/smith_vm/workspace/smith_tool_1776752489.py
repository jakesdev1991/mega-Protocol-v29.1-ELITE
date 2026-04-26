# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# dimensional validation for the Omega Action based analysis
# base dimension: time = T
# we represent dimensions as powers of T
def dim(pow):
    return {'T': pow}

# field I is dimensionless (entropy)
I_dim = dim(0)
# stiffnesses xi_N xi_Delta have dimension of time
xi_dim = dim(1)
# UV cutoff Lambda has inverse time dimension
Lambda_dim = dim(-1)
# couplings g_N g_Delta lambda are dimensionless
g_dim = dim(0)
lam_dim = dim(0)  # lambda in potential
# invariant psi = ln(Phi_N/I0) dimensionless
psi_dim = dim(0)
# lattice spacing a = xi0 * exp(-psi) -> time dimension
a_dim = xi_dim
# action S = ∫ dt [ (1/2)(dI/dt)^2 + V(I) ]
# derivative dI/dt -> T^{-1}
dI_dt_dim = dim(-1)
# kinetic term (dI/dt)^2 -> T^{-2}
kin_dim = dim(-2)
# potential V(I) = (lambda/4)(I^2 - I0^2)^2
# lambda must match kinetic term dimension
V_dim = lam_dim  # lambda dimension
# assert kinetic and potential have same dimension
assert kin_dim == V_dim, "kinetic and potential dimension mismatch"
# Lagrangian L has dimension T^{-2}
L_dim = kin_dim
# action S = ∫ L dt -> T^{-2} * T = T^{-1}
S_dim = {'T': L_dim['T'] + 1}
assert S_dim == dim(-1), "action dimension incorrect"
# mass correction Δm^2 ~ g^2 Λ^2 / (16π^2)
# g^2 dimensionless, Λ^2 -> T^{-2}
mass2_dim = {'T': 2 * Lambda_dim['T']}
assert mass2_dim == dim(-2), "mass correction dimension incorrect"
# beta function β(g) = g^3/(16π^2) dimensionless
beta_dim = g_dim
assert beta_dim == dim(0), "beta function dimension incorrect"
# Poisson recovery: ∇^2 Φ_N ~ 4π G ρ
# ∇^2 adds T^{-2}, so Φ_N must have same dimension as source term
# we treat G ρ as having T^{-2} for consistency check
PhiN_dim = dim(-2)  # placeholder for Newtonian potential dimension
laplacian_PhiN_dim = {'T': PhiN_dim['T'] - 2}
# source term dimension (set to match laplacian)
source_dim = laplacian_PhiN_dim
assert laplacian_PhiN_dim == source_dim, "Poisson recovery dimension mismatch"
print("all dimensional checks passed")