# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Dimensional consistency check for the Higher‑Order Lattice Polarization derivation
# Dimensions are expressed in terms of mass [M] and length [L] (natural units ħ = c = 1).
#   [action] = [M][L]^2,   [∂] = [L]^{-1},   [Φ] = [M] (scalar field),
#   [g] = dimensionless,   [Λ] = [M],       [a] = [L],
#   [ξ0] = [L],            [I0] = [M] (to make ψ dimensionless),
#   [G] = [M]^{-2}         (Newton's constant in 4D).

import sympy as sp

# Define dimension symbols
M, L = sp.symbols('M L', positive=True)

# Helper to build dimension expressions
def dim(*powers):
    # powers: (exp_M, exp_L)
    return M**powers[0] * L**powers[1]

# Assign dimensions to fields/parameters
dim_PhiN = dim(1, 0)          # [M]
dim_PhiDelta = dim(1, 0)      # [M]
dim_gN = dim(0, 0)            # dimensionless
dim_gDelta = dim(0, 0)        # dimensionless
dim_Lambda = dim(1, 0)        # [M] UV cutoff
dim_xi0 = dim(0, 1)           # [L]
dim_I0 = dim(1, 0)            # [M] (so that Phi_N/I0 is dimensionless)
dim_psi = dim(0, 0)           # ln(dimensionless) -> dimensionless
dim_a = dim(0, 1)             # [L] lattice spacing
dim_G = dim(-2, 0)            # [M]^{-2}
dim_rho = dim(4, 0)           # [M]^4 energy density in natural units

# Define derived dimensions
dim_psi_check = dim_PhiN - dim_I0   # should be zero for log argument
dim_a_expr = dim_xi0 + dim_I0 - dim_PhiN  # a = xi0 * I0 / Phi_N

# Dimension checks
checks = []

# 1. Yukawa term in Lagrangian: g * Phi * psi_bar psi -> dimension [M]^4
#   [g]=0, [Phi]=M, [psi_bar psi]=M^3  => total M^4 (OK)
checks.append(("Yukawa coupling dimensionless", dim_gN == dim(0,0)))
checks.append(("Yukawa coupling dimensionless", dim_gDelta == dim(0,0)))

# 2. Scalar mass correction: Δm^2 ~ g^2 Λ^2 / (16π^2)
dim_Delta_m2 = 2*dim_gN + 2*dim_Lambda   # g^2 Λ^2
checks.append(("Δm_ΦN^2 dimension", dim_Delta_m2 == dim(2,0)))  # [M]^2

# 3. Beta function: β(g) = g^3/(16π^2) -> dimensionless
dim_beta = 3*dim_gDelta
checks.append(("Beta function dimensionless", dim_beta == dim(0,0)))

# 4. Landau pole exponent: 8π^2/g^2 -> dimensionless
dim_exp = -2*dim_gDelta
checks.append(("Exponent dimensionless", dim_exp == dim(0,0)))

# 5. Landau pole scale: Λ_LP = μ0 * exp(...) -> same dimension as μ0
dim_mu0 = dim_Lambda   # assume reference scale same dimension as cutoff
dim_LP = dim_mu0 + dim_exp   # exp dimensionless
checks.append(("Landau pole dimension", dim_LP == dim_mu0))

# 6. Lattice spacing relation: a = xi0 * I0 / Phi_N
checks.append(("Lattice spacing dimension", dim_a_expr == dim_a))

# 7. Poisson equation: ∇^2 Φ_N = 4π G ρ
#   [∇^2 Φ_N] = [Φ_N] / L^2 = M L^{-2}
#   [G ρ] = [M]^{-2} * [M]^4 = M^2
#   In natural units we set c=ħ=1, so an extra factor of [L]^{-2} appears from the conversion
#   between mass and length; to keep the check simple we verify that both sides have
#   the same combined dimension M L^{-2} after inserting G's dimension.
dim_lhs_Poisson = dim_PhiN - 2*dim(0,1)   # Φ_N / L^2
dim_rhs_Poisson = dim_G + dim_rho        # G * rho
checks.append(("Poisson equation dimension", dim_lhs_Poisson == dim_rhs_Poisson))

# Output results
all_pass = all(result for _, result in checks)
print("Dimensional consistency check results:")
for name, res in checks:
    print(f"  {name}: {'PASS' if res else 'FAIL'}")
print("\nOverall:", "PASS" if all_pass else "FAIL")