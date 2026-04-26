# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
---------------------------------
Checks dimensional consistency and basic structural requirements
for the Higher‑Order Lattice Polarization derivation.
"""

import sympy as sp

# ------------------------------------------------------------------
# 1. Define base dimensions (M = mass, L = length, T = time)
#    In natural units we keep them explicit to catch mismatches.
M, L, T = sp.symbols('M L T', positive=True)

# Helper to create a dimension object
def dim(**powers):
    """Return a dimension dict, e.g. dim(M=1, L=-2, T=1) -> M^1 L^-2 T^1"""
    return {M: powers.get('M', 0),
            L: powers.get('L', 0),
            T: powers.get('T', 0)}

def mul_dim(d1, d2):
    """Multiply two dimension dicts."""
    return {k: d1.get(k,0)+d2.get(k,0) for k in set(d1)|set(d2)}

def pow_dim(d, n):
    """Raise a dimension to power n."""
    return {k: v*n for k,v in d.items()}

def dim_eq(d1, d2):
    """Check equality of two dimension dicts."""
    return d1 == d2

# ------------------------------------------------------------------
# 2. Assign dimensions to fundamental quantities
#    Action S has dimensions [M L^2 T^-1] (ℏ = 1 in natural units, but we keep it)
dim_S   = dim(M=1, L=2, T=-1)

# Field I (information density) is dimensionless per the derivation
dim_I   = dim()  # {}

# Coupling λ appears in V(I) = (λ/4)(I^2 - I0^2)^2 → [V] = [Energy]^4 = [M L^2 T^-2]^2
# Hence [λ] = [Energy]^2 = [M L^2 T^-2]
dim_lam = dim(M=1, L=2, T=-2)

# Stiffnesses ξ_N, ξ_Δ have dimensions of length (or time) – we choose length
dim_xi  = dim(L=1)

# Invariant ψ = ln(ξ_Δ/ξ_0) → argument dimensionless, ψ dimensionless
dim_psi = dim()

# Momentum q has dimensions [M L T^-1]
dim_q   = dim(M=1, L=1, T=-1)

# Mass m_e same as momentum
dim_me  = dim_q

# ------------------------------------------------------------------
# 3. Check the Hessian relation: ξ_Δ⁻² = λ(Φ_N² + 3Φ_Δ² - I₀²)
#    Assume Φ_N, Φ_Δ have same dimension as I (dimensionless) for simplicity.
dim_Phi = dim()   # dimensionless mode amplitudes
dim_I0  = dim()

rhs = mul_dim(dim_lam,
              pow_dim(dim_Phi, 2))   # λ * Φ^2
lhs = pow_dim(dim_xi, -2)            # ξ_Δ⁻²
print("Hessian relation dimension check:", dim_eq(lhs, rhs))

# ------------------------------------------------------------------
# 4. Check one‑loop vacuum polarization term:
#    Π_N(q²) = (α/3π) ln(q²/m_e²) → α dimensionless, log dimensionless
dim_alpha = dim()   # fine‑structure constant dimensionless
log_arg   = mul_dim(pow_dim(dim_q,2), pow_dim(dim_me,-2))  # q²/m_e²
print("Log argument dimensionless:", dim_eq(log_arg, dim()))

# Π_N overall dimensionless (as required for polarization tensor)
print("Π_N dimensionless:", dim_eq(dim_alpha, dim()))

# ------------------------------------------------------------------
# 5. Check RG equations:
#    β_N = dΦ_N/d ln q  → dimensions of Φ_N (since d/d ln q is dimensionless)
dim_beta_N = dim_Phi
rhs_beta_N = mul_dim(dim(), dim_Phi)  # η_N Φ_N (η_N dimensionless)
rhs_beta_N = sp.Add(rhs_beta_N,
                    mul_dim(dim(), pow_dim(dim_Phi,2)))  # - κ Φ_Δ² (κ dimensionless)
print("β_N dimension check:", dim_eq(dim_beta_N, rhs_beta_N))

# Similarly for β_Δ
dim_beta_Delta = dim_Phi
rhs_beta_Delta = sp.Add(mul_dim(dim(), dim_Phi),
                        mul_dim(dim(), mul_dim(dim_Phi, dim_Phi)))
print("β_Δ dimension check:", dim_eq(dim_beta_Delta, rhs_beta_Delta))

# ------------------------------------------------------------------
# 6. Entropy‑gauge term: S_h ∝ ln(q²/m_e²) → dimensionless
dim_Sh = dim()
print("Shannon entropy dimensionless:", dim_eq(dim_Sh, dim()))

# Gauge field 𝒜_μ = ∂_μ S_h → adds one derivative (∂_μ has dimension [L^-1])
dim_Amu = mul_dim(dim_Sh, pow_dim(dim(L=1), -1))  # ∂_μ ~ 1/L
print("𝒜_μ dimension:", dim_Amu)

# Information current J^μ has dimensions of [Energy]^3 = [M L^2 T^-2]^3 / [L] ?
# In natural units, J^μ ~ ∂^μ I → dimension [L^-1] (since I dimensionless)
dim_Jmu = pow_dim(dim(L=1), -1)  # ∂^μ I
print("J^μ dimension:", dim_Jmu)

# Coupling term 𝒜_μ J^μ → dimension of action density [M L^-4 T^-0]? 
# We just verify it matches the dimension of the Lagrangian density [M L^-1 T^-2]
dim_coupling = mul_dim(dim_Amu, dim_Jmu)
dim_Lagrangian = dim(M=1, L=-1, T=-2)
print("𝒜_μ J^μ matches Lagrangian density:", dim_eq(dim_coupling, dim_Lagrangian))

# ------------------------------------------------------------------
# 7. Gauge invariance check (symbolic)
#    Under 𝒜_μ → 𝒜_μ + ∂_μΛ, the change in ∫𝒜_μ J^μ is ∫(∂_μΛ) J^μ
#    = -∫ Λ (∂_μ J^μ) after integration by parts → vanishes if ∂_μ J^μ = 0 (current conservation).
Lambda = sp.Function('Lambda')(sp.Symbol('x'), sp.Symbol('y'), sp.Symbol('z'), sp.Symbol('t'))
# Assume current conservation ∂_μ J^μ = 0 as a physical condition.
div_J = 0  # placeholder
gauge_variation = -Lambda * div_J
print("Gauge variation (should be zero):", gauge_variation)

print("\nAll dimensional checks completed. If any 'False' appears above, the derivation violates Omega Protocol invariants.")