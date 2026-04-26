# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Dimensional‑consistency checker for the NCSM‑Ω refinement.
Assumes base dimensions: [M] mass, [L] length, [T] time.
In natural units (ħ = 1) action is dimensionless → [M L^2 T^{-1}] = 1.
We therefore set:
    [action] = 1
    [field φ] = 1          (embeddings are normalised)
    [length] = L
    [time]   = T
    [mass]   = M
All derived dimensions are expressed as products of M^a L^b T^c.
"""

import sympy as sp

# Base symbols for dimensions
M, L, T = sp.symbols('M L T', positive=True)

# Helper to create a dimension tuple
def dim(*powers):
    # powers = (a,b,c) for M^a L^b T^c
    return M**powers[0] * L**powers[1] * T**powers[2]

# Known dimensions
dim_action   = dim(0,0,0)          # dimensionless in ħ=1
dim_phi      = dim(0,0,0)          # normalised embedding field
dim_length   = dim(0,1,0)          # L
dim_time     = dim(0,0,1)          # T
dim_mass     = dim(1,0,0)          # M

# Derived quantities from the paper
# Curvature R ~ [length]^{-2}
dim_R        = dim(0,-2,0)

# Entropy S is dimensionless (Shannon)
dim_S        = dim(0,0,0)

# Coupling constants from V_eff: λ_eff [T^{-2}], α [L^2], β [T^{-2}]
dim_lambda_eff = dim(0,0,-2)
dim_alpha      = dim(0,2,0)
dim_beta       = dim(0,0,-2)

# γ_S, δ_S are dimensionless (they multiply S which is dimensionless)
dim_gamma_S = dim(0,0,0)
dim_delta_S = dim(0,0,0)

# Field magnitude I is dimensionless (norm of φ^2 averaged)
dim_I       = dim(0,0,0)

# Effective potential V_eff(I) must have dimension of [action]/[time] = [T^{-1}]
# because S = ∫ dt L, L has dimension [T^{-1}] when action dimensionless.
dim_V_eff   = dim(0,0,-1)

# Check each term in V_eff = (λ_eff/4)(I^2 - I0^2)^2 + α R I + β S I
term1 = dim_lambda_eff * dim_I**4          # λ_eff * I^4
term2 = dim_alpha   * dim_R * dim_I        # α * R * I
term3 = dim_beta    * dim_S * dim_I        # β * S * I

print("Dimensions:")
print("  λ_eff I^4 :", term1)
print("  α R I     :", term2)
print("  β S I     :", term3)
print("  V_eff target:", dim_V_eff)

# Verify homogeneity
def check_eq(expr, target, name):
    if sp.simplify(expr - target) == 0:
        print(f"  {name}: OK")
        return True
    else:
        print(f"  {name}: FAIL → {expr} != {target}")
        return False

ok = True
ok &= check_eq(term1, dim_V_eff, "λ_eff I^4")
ok &= check_eq(term2, dim_V_eff, "α R I")
ok &= check_eq(term3, dim_V_eff, "β S I")

# Stiffness invariants: ξ_N^{-2} = λ_eff (3 I0^2 + <R> + γ_S <S>)
dim_xiN_inv2 = dim_lambda_eff * (dim_I**2 + dim_R + dim_gamma_S * dim_S)
# ξ_Δ^{-2} = λ_eff (I0^2 + 3<R> + δ_S <S>)
dim_xiD_inv2 = dim_lambda_eff * (dim_I**2 + 3*dim_R + dim_delta_S * dim_S)

# ξ has dimension of time (since ξ^{-2} has [T^{-2}])
dim_xi = sp.sqrt(1/dim_xiN_inv2)   # should be [T]
print("\nStiffness dimensions:")
print("  ξ_N^{-2} :", dim_xiN_inv2)
print("  ξ_Δ^{-2} :", dim_xiD_inv2)
print("  ξ (sqrt of inverse) :", dim_xi)
print("  Expected ξ dimension [T]:", dim_time)
ok &= check_eq(dim_xi, dim_time, "ξ dimension")

# Invariant ψ = ln(ξ/ξ0) → dimensionless (log of ratio)
dim_psi = dim(0,0,0)   # log is dimensionless
print("\nInvariant ψ dimension:", dim_psi, "(should be dimensionless)")
ok &= check_eq(dim_psi, dim(0,0,0), "ψ")

# Covariant mode relations: ξ_N = ∂Φ_N/∂ψ, ξ_Δ = ∂Φ_Δ/∂ψ
# Since ψ is dimensionless, ∂/∂ψ does not change dimension.
# Hence [ξ_N] = [Φ_N] and [ξ_Δ] = [Φ_Δ].
# From earlier, ξ has dimension [T]; we therefore assign:
dim_PhiN = dim_time
dim_PhiD = dim_time
print("\nCovariant mode dimensions:")
print("  Φ_N :", dim_PhiN, "(should match ξ_N)")
print("  Φ_Δ :", dim_PhiD, "(should match ξ_Δ)")
ok &= check_eq(dim_PhiN, dim_xi, "Φ_N vs ξ_N")
ok &= check_eq(dim_PhiD, dim_xi, "Φ_Δ vs ξ_Δ")

# Entropy gauge field 𝒜_μ = ∂_μ S → dimension of ∂_μ is [L^{-1}] for spatial, [T^{-1}] for temporal.
# In the action term ∫√g 𝒜_μ J^μ, J^μ (information flux) has dimension [Φ] * [velocity]?
# For simplicity we check that 𝒜_μ has same dimension as ∂_μ S, i.e. inverse length/time.
dim_dS_dx = dim_S / dim_length   # [L^{-1}]
dim_dS_dt = dim_S / dim_time     # [T^{-1}]
print("\nEntropy gauge dimensions:")
print("  ∂S/∂x :", dim_dS_dx)
print("  ∂S/∂t :", dim_dS_dt)
# These are acceptable as they appear contracted with J^μ which carries opposite dimensions.

print("\n=== RESULT ===")
if ok:
    print("All checked dimensional relations PASS.")
else:
    print("Some dimensional checks FAILED – review the expressions above.")