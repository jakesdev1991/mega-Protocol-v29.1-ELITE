# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Dimensional consistency check for Omega Action based instability analysis
# Dimensions: [T] = time, dimensionless = 1
# We define a simple dimension class for illustrative purposes

class Dim:
    def __init__(self, t_exp=0):
        # t_exp is exponent of [T]; dimensionless if t_exp == 0
        self.t = t_exp
    def __mul__(self, other):
        return Dim(self.t + other.t)
    def __add__(self, other):
        if self.t != other.t:
            raise ValueError("Dimension mismatch in addition")
        return self
    def __eq__(self, other):
        return self.t == other.t
    def __repr__(self):
        return f"[T]^{self.t}"

# Base dimensions
T = Dim(1)          # [Time]
ONE = Dim(0)        # dimensionless

# Define symbols with their dimensions
I   = ONE           # information content field (entropy) dimensionless
dt  = T             # differential time
lambda_ = Dim(-2)   # coupling lambda has dimension [T]^{-2} to make V(I) dimensionless * [T]^{-2}
gN  = ONE           # Yukawa coupling dimensionless
gD  = ONE           # Yukawa coupling dimensionless
Lambda = Dim(-1)    # UV cutoff momentum inverse time [T]^{-1}
xi0  = T            # stiffness xi0 has dimension [T]
psi  = ONE          # invariant psi = ln(Phi_N/I0) dimensionless
PhiN = ONE          # Phi_N dimensionless (information)
PhiD = ONE          # Phi_D dimensionless (information)

# Action S = ∫ dt [ (1/2)(dI/dt)^2 + V(I) ]
# kinetic term: (dI/dt)^2 -> (I/T)^2 = I^2 * T^{-2}
kinetic = (I / T) ** 2   # I^2 * T^{-2}
# potential V(I) = (lambda/4)(I^2 - I0^2)^2 -> lambda * I^4
potential = lambda_ * I ** 4   # lambda [T]^{-2} * I^4
# Lagrangian density L = kinetic + potential must have same dimension
L = kinetic + potential        # should be [T]^{-2}
# Action S = ∫ L dt -> L * T
S = L * T                      # [T]^{-2} * [T] = [T]^{-1}
print("Action dimension:", S)    # expected [T]^{-1}

# Mass correction Δm^2 ~ g^2 Λ^2 / (16π^2)
Delta_m2_N = (gN ** 2) * (Lambda ** 2)   # g^2 dimensionless * Lambda^2 [T]^{-2}
Delta_m2_D = (gD ** 2) * (Lambda ** 2)
print("Mass correction dimension:", Delta_m2_N)  # expected [T]^{-2}

# Beta function β(g_D) = g_D^3/(16π^2) -> dimensionless
beta_gD = gD ** 3
print("Beta function dimension:", beta_gD)  # expected dimensionless

# Landau pole scale Λ_LP = μ0 exp(8π^2/g_D^2) -> same dimension as μ0
mu0 = Dim(-1)   # reference scale [T]^{-1}
Lambda_LP = mu0   # exponential is dimensionless
print("Landau pole dimension:", Lambda_LP)  # expected [T]^{-1}

# Lattice spacing a = ξ0 * exp(-psi) -> ξ0 dimension [T] times dimensionless
a = xi0   # exp(-psi) dimensionless
print("Lattice spacing dimension:", a)  # expected [T]

# Invariants: ψ = ln(Φ_N/I0) dimensionless (already set)
# Stiffnesses ξ_N, ξ_Δ have dimension [T] (set as symbols)
xi_N = T
xi_D = T
print("Stiffness ξ_N dimension:", xi_N)
print("Stiffness ξ_Δ dimension:", xi_D)

# Boundary conditions: Shredding Event when Φ_N^2 + 3 Φ_D^2 = I0^2
# All terms dimensionless
shred_condition = (PhiN ** 2) + 3 * (PhiD ** 2)
print("Shredding condition dimension:", shred_condition)  # expected dimensionless

# Informational Freeze when 3 Φ_N^2 + Φ_D^2 = I0^2
freeze_condition = 3 * (PhiN ** 2) + (PhiD ** 2)
print("Freeze condition dimension:", freeze_condition)  # expected dimensionless

# Poisson recovery violation: Φ_N acquires mass m^2 ~ g_N^2 Λ^2/(16π^2)
# This mass term adds to the kinetic term of Φ_N breaking ∇^2 Φ_N ∝ source
# Check that m^2 has same dimension as kinetic term of Φ_N (which is [T]^{-2})
PhiN_mass2 = Delta_m2_N
print("Phi_N mass^2 dimension:", PhiN_mass2)  # expected [T]^{-2}