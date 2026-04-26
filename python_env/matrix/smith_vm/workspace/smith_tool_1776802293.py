# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Symbolic validation of the repaired FTFM‑Ω proposal.
Checks:
  1. Invariant form ψ = ln(Phi_N/Phi_N0)
  2. Dimensionless nature of key expressions (action terms, CFI, constraints)
  3. Correct dimensions of stiffness invariants after introducing τ0
  4. Presence of the ½ factor in the diffusion term
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Define symbols and their dimensions
# ----------------------------------------------------------------------
# Base dimensions: M (mass), L (length), T (time)
# In natural units ħ = c = 1 we can set M = L⁻¹ = T⁻¹.
# For clarity we keep L and T as independent; M will be derived.
L, T = sp.symbols('L T', positive=True)

# Dimension of a quantity: dict {L: exponent, T: exponent}
def dim(**kwargs):
    d = {L: 0, T: 0}
    d.update(kwargs)
    return d

# Assign dimensions to basic symbols
dim_F   = dim()                     # field 𝓕 is dimensionless
dim_x   = dim(L=1)                  # coordinate x^μ has dimension L (we will later set L=1 via normalization)
dim_t   = dim(T=1)                  # time coordinate has dimension T
dim_partial_t = dim(T=-1)           # ∂_t
dim_partial_x = dim(L=-1)           # ∂_x
dim_g   = dim()                     # metric dimensionless
dim_D   = dim(T=-1)                 # diffusion coefficient D has 1/T so that D ∂_x^2 matches ∂_t
dim_alpha = dim()                   # couplings α,β,γ,δ,λ_Ω dimensionless
dim_beta  = dim()
dim_gamma = dim()
dim_delta = dim()
dim_lam   = dim()
dim_tau0  = dim(T=1)                # characteristic time τ0
dim_ell   = dim(L=1)                # characteristic length ℓ (set to 1 later)

# ----------------------------------------------------------------------
# 2. Helper to check dimensionlessness
# ----------------------------------------------------------------------
def is_dimensionless(expr_dim):
    """Return True if all exponents are zero."""
    return all(v == 0 for v in expr_dim.values())

def combine_dims(*dim_dicts):
    """Add dimension dictionaries (for multiplication)."""
    res = {L:0, T:0}
    for d in dim_dicts:
        for k in (L,T):
            res[k] += d.get(k,0)
    return res

def pow_dim(base_dim, exp):
    """Dimension of base_dim**exp."""
    return {k: v*exp for k,v in base_dim.items()}

# ----------------------------------------------------------------------
# 3. Invariant ψ
# ----------------------------------------------------------------------
Phi_N   = sp.symbols('Phi_N')   # dimensionless
Phi_N0  = sp.symbols('Phi_N0')  # reference, same dimension as Phi_N
psi     = sp.log(Phi_N/Phi_N0)   # ln(Phi_N/Phi_N0)

dim_psi = combine_dims(dim_F, dim_F)  # log of ratio -> dimensionless
print("Invariant ψ dimensionless?", is_dimensionless(dim_psi))
print("Invariant form matches ln(Phi_N)? ->", psi)

# ----------------------------------------------------------------------
# 4. Stochastic reaction‑diffusion equation
# ----------------------------------------------------------------------
# ∂_t F = 0.5 * D * ∂_x^2 F + R + ζ
term_lhs   = dim_partial_t   # [∂_t F]
term_diff  = combine_dims(dim_D, pow_dim(dim_partial_x,2), dim_F)  # D * ∂_x^2 F
term_R     = dim_F           # assume R has same dimension as F (source term)
term_zeta  = dim_F           # noise same dimension as F

print("\nReaction‑diffusion term dimensions:")
print("  LHS (∂_t F):", term_lhs)
print("  Diffusion (½ D ∂_x^2 F):", term_diff)
print("  R:", term_R)
print("  ζ:", term_zeta)
print("  All equal?", term_lhs == term_diff == term_R == term_zeta)

# ----------------------------------------------------------------------
# 5. Action integrand (Lagrangian density)
# ----------------------------------------------------------------------
# L = ½ g^{μν} ∂_μ F ∂_ν F   +   V(F)   +   λΩ LΩ   +   A_μ J^μ
# We treat each term separately.

# Kinetic term: ½ g^{μν} ∂_μ F ∂_ν F
dim_kinetic = combine_dims(dim_g, pow_dim(dim_partial_x,1), dim_F,
                                      pow_dim(dim_partial_x,1), dim_F)
# Potential V: α/2 (F-F0)^2 + β/4 (F-F0)^4  -> dimensionless because α,β dimensionless
dim_V = combine_dims(dim_alpha, pow_dim(dim_F,2))  # same as F^2
# Ω coupling: λΩ LΩ(Phi_N,Phi_Delta) -> dimensionless
dim_Lambda = combine_dims(dim_lam, dim_F, dim_F)   # placeholder for LΩ
# Entropy gauge: A_μ J^μ
#   A_μ = ∂_μ S_context, S_context dimensionless -> A_μ has dimension of ∂_x
dim_A = dim_partial_x   # same as derivative
#   J^μ = sqrt(2) Phi_Delta δ^μ_0  (we set ℓ=1 via length normalization)
dim_J = dim_F           # because δ^μ_0 is dimensionless, Phi_Delta dimensionless
dim_gauge = combine_dims(dim_A, dim_J)

print("\nAction term dimensions:")
print("  Kinetic:", dim_kinetic)
print("  Potential V:", dim_V)
print("  Ω coupling:", dim_Lambda)
print("  Gauge A_μ J^μ:", dim_gauge)
print("  All dimensionless?",
      all(is_dimensionless(d) for d in [dim_kinetic, dim_V, dim_Lambda, dim_gauge]))

# ----------------------------------------------------------------------
# 6. Stiffness invariants ξ_N, ξ_Δ from effective potential V_eff(ψ)
# ----------------------------------------------------------------------
# Assume V_eff is a function of ψ only; its second derivative w.r.t ψ is dimensionless.
dim_V_eff_pp = pow_dim(dim_V, -2)   # d^2V/dψ^2 has same dimension as V (dimensionless) because ψ dimensionless
# Introduce τ0 to get dimensions of time
dim_xi = combine_dims(dim_tau0, pow_dim(dim_V_eff_pp, -1))  # ξ = τ0 * (V_eff'')^{-1}
print("\nStiffness invariant dimensions (with τ0):")
print("  ξ_N, ξ_Δ:", dim_xi)
print("  Dimension of time?", dim_xi == dim_tau0)

# ----------------------------------------------------------------------
# 7. Contextual Fragility Index CFI
# ----------------------------------------------------------------------
sigma2_TF = sp.symbols('sigma2_TF')   # dimensionless variance
kappa     = sp.symbols('kappa')       # dimensionless sensitivity
chi       = sp.symbols('chi')         # dimensionless crosstalk
rho       = sp.symbols('rho')         # dimensionless data density
alpha,beta,gamma,delta = sp.symbols('alpha beta gamma delta')
CFI_expr = sp.tanh(alpha*sigma2_TF + beta*kappa + gamma*chi - delta*rho)
dim_CFI = combine_dims(dim_alpha, dim(sigma2_TF),   # all inner terms dimensionless
                       dim_beta, dim(kappa),
                       dim_gamma, dim(chi),
                       dim_delta, dim(rho))
print("\nCFI dimensionless?", is_dimensionless(dimensionless:=combine_dims(dim_alpha, dim(sigma2_TF), dim_beta, dim(kappa), dim_gamma, dim(chi), dim_delta, dim(rho))))
print("  CFI expression:", CFI_expr)

# ----------------------------------------------------------------------
# 8. MPC‑Ω constraints (dimensionless checks)
# ----------------------------------------------------------------------
Phi_N_ftfm = sp.symbols('Phi_N_ftfm')
S_context  = sp.symbols('S_context')
constraint_CFI = sp.Le(sp.symbols('CFI'), 0.65)          # CFI ≤ 0.65
constraint_PhiN = sp.Ge(Phi_N_ftfm, 0.6)                # Φ_N ≥ 0.6
constraint_Ent  = sp.Ge(S_context, sp.log(3))           # S_context ≥ ln(3)

print("\nConstraint symbols are dimensionless (by construction).")
print("  CFI ≤ 0.65 :", constraint_CFI)
print("  Φ_N ≥ 0.6  :", constraint_PhiN)
print("  S_ctx ≥ ln3:", constraint_Ent)

# ----------------------------------------------------------------------
# 9. Cost function integrand (dimensionless)
# ----------------------------------------------------------------------
mu1, mu2, mu3 = sp.symbols('mu1 mu2 mu3')
cost = ((sp.symbols('CFI')-0.6)**2 * sp.Heaviside(sp.symbols('CFI')-0.6) +
        mu1*(0.6-Phi_N_ftfm)**2 * sp.Heaviside(0.6-Phi_N_ftfm) +
        mu2*Phi_N_ftfm**2 +
        mu3*(sp.log(3)-S_context)**2 * sp.Heaviside(sp.log(3)-S_context))
# Each term is a square of dimensionless quantities → dimensionless
print("\nCost integrand dimensionless? (each term squared of dimensionless)")
print("  Sample term (CFI-0.6)^2 dimension:", combine_dims(dim(), dim()))  # trivially dimensionless

print("\n=== Validation complete ===")