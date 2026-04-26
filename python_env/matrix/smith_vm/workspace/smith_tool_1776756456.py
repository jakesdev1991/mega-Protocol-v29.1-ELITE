# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Dimensional and algebraic sanity‑check for the Engine's
Higher‑Order Lattice Polarization derivation.
Uses Sympy to treat dimensions as symbols.
"""

import sympy as sp

# ------------------------------------------------------------------
# 1. Define dimension symbols (in natural units: [E] = energy, [L] = length = 1/[E])
# ------------------------------------------------------------------
E   = sp.Symbol('E', positive=True)   # energy dimension
L   = sp.Symbol('L', positive=True)   # length dimension
# In natural units: [L] = [E]^{-1}
# We'll keep both for clarity, but enforce L = E^{-1} later.

# ------------------------------------------------------------------
# 2. Fundamental quantities and their dimensions
# ------------------------------------------------------------------
# Action S: [E]·[T] = [E]·[L] (since [T]=[L] in c=1)
S_dim = E * L

# Field I: dimensionless (as per Engine)
I_dim = 1

# Coupling λ: from V = λ/4 (I^2 - I0^2)^2 → [V] = [E]^4 (energy density)
# Since I is dimensionless, λ must have [E]^4
lam_dim = E**4

# Vacuum expectation I0: dimensionless
I0_dim = 1

# Stiffness correlation lengths ξ_N, ξ_Δ: Engine says [length] or [time] → [L]
xi_dim = L

# Invariant ψ = ln(ξΔ/ξ0): argument of log must be dimensionless → ξ0 has same dim as ξΔ
xi0_dim = xi_dim   # thus ψ dimensionless

# Fine‑structure constant α_fs: dimensionless
alpha_dim = 1

# Electron mass m_e: [E]
m_dim = E

# Momentum q: [E]
q_dim = E

# Archive cutoff Λ_Δ: [E]
Lambda_dim = E

# Ratio ΦΔ/ΦN: both Φ's have same dimension as I (fluctuation of I) → dimensionless
Phi_dim = 1

# ------------------------------------------------------------------
# 3. Helper to check dimensionlessness
# ------------------------------------------------------------------
def is_dimensionless(expr_dim):
    """Return True if expr_dim simplifies to 1 under L = E^{-1}."""
    # substitute L = E^{-1}
    dim_sub = expr_dim.subs(L, 1/E)
    # simplify powers of E
    simplified = sp.simplify(dim_sub)
    return simplified == 1

# ------------------------------------------------------------------
# 4. Check invariant definition
# ------------------------------------------------------------------
# ξΔ^{-2} = λ (Φ_N^2 + 3 Φ_Δ^2 - I0^2)
xi_inv2_dim = lam_dim * (Phi_dim**2 + 3*Phi_dim**2 - I0_dim**2)   # λ * (dimensionless)
# Since Φ_dim = I0_dim = 1, this is just λ
print("ξΔ^{-2} dimension:", xi_inv2_dim)
print("  -> is dimensionless? (should be [E]^2 because ξΔ has [L])")
print("  Expected [E]^2 because ξΔ^{-2} ~ 1/[L]^2 = [E]^2")
print("  Check:", is_dimensionless(xi_inv2_dim * L**2))  # multiply by L^2 to cancel [L]^{-2}
# Actually we want ξΔ^{-2} to have dimension [E]^2:
print("  ξΔ^{-2} has dimension [E]^2?", is_dimensionless(xi_inv2_dim * L**2))

# ψ dimensionless check
psi_dim = sp.log(xi_dim / xi0_dim)   # log of ratio → dimensionless if args same dim
print("\nψ dimensionless?", is_dimensionless(psi_dim))

# ------------------------------------------------------------------
# 5. Vacuum polarization terms
# ------------------------------------------------------------------
# Π_N = (α/3π) ln(q^2/m_e^2)
PiN_dim = alpha_dim * sp.log(q_dim**2 / m_dim**2)
print("\nΠ_N dimensionless?", is_dimensionless(PiN_dim))

# Π_Δ = (α/2π) ψ ln(q^2/Λ_Δ^2)
PiDelta_dim = alpha_dim * psi_dim * sp.log(q_dim**2 / Lambda_dim**2)
print("Π_Δ dimensionless?", is_dimensionless(PiDelta_dim))

# Π_mix = (α^2/π^2) (ΦΔ/ΦN) ln^2(q^2/m_e^2)
PiMix_dim = alpha_dim**2 * (Phi_dim/Phi_dim) * sp.log(q_dim**2 / m_dim**2)**2
print("Π_mix dimensionless?", is_dimensionless(PiMix_dim))

# Total Π dimensionless?
Pi_total_dim = PiN_dim + PiDelta_dim + PiMix_dim
print("Total Π dimensionless?", is_dimensionless(Pi_total_dim))

# ------------------------------------------------------------------
# 6. RG equations dimensional check
# ------------------------------------------------------------------
# β_N = dΦ_N/d ln q  → same dimension as Φ_N (since d/d ln q is dimensionless)
betaN_dim = eta_N_dim * Phi_dim * (1 - Phi_dim**2 / I0_dim**2) - kappa_dim * Phi_dim**2
# We'll assign dimensions to eta_N, eta_Δ, κ as dimensionless (as Engine claims)
eta_N_dim = eta_Delta_dim = kappa_dim = 1
betaN_dim = eta_N_dim * Phi_dim * (1 - Phi_dim**2 / I0_dim**2) - kappa_dim * Phi_dim**2
print("\nβ_N dimension (should be same as Φ):", betaN_dim)
print("  Φ dimension:", Phi_dim)
print("  Match?", betaN_dim == Phi_dim)

# β_Δ analogous
betaDelta_dim = eta_Delta_dim * Phi_dim * (1 - Phi_dim**2 / I0_dim**2) + kappa_dim * Phi_dim * Phi_dim
print("β_Δ dimension (should be same as Φ):", betaDelta_dim)
print("  Match?", betaDelta_dim == Phi_dim)

# ------------------------------------------------------------------
# 7. Entropy gauge term: S_h = c ln(q^2/m_e^2) → dimensionless
#    𝒜_μ = ∂_μ S_h → [𝒜] = [∂] = [E] (since ∂/∂x has dimension of momentum)
#    J^μ (Noether current of information density) → Engine says [E]^3
#    Coupling term ∫ d^4x 𝒜_μ J^μ → [d^4x] = [L]^4 = [E]^{-4}
#    So total dimension: [E]^{-4} * [E] * [E]^3 = [E]^0 → dimensionless (as action should be)
S_h_dim = sp.log(q_dim**2 / m_dim**2)   # dimensionless
A_dim = 1 / L   # derivative w.r.t. x adds [E]
J_dim = E**3
coupling_dim = (L**4) * A_dim * J_dim   # d^4x * A * J
print("\nEntropy gauge coupling dimension:")
print("  d^4x:", L**4)
print("  𝒜_μ:", A_dim)
print("  J^μ:", J_dim)
print("  Product:", coupling_dim)
print("  Dimensionless?", is_dimensionless(coupling_dim))

# ------------------------------------------------------------------
# 8. Summary
# ------------------------------------------------------------------
print("\n=== SUMMARY ===")
print("All checked terms are dimensionless as required." if all([
    is_dimensionless(Pi_total_dim),
    is_dimensionless(psi_dim),
    betaN_dim == Phi_dim,
    betaDelta_dim == Phi_dim,
    is_dimensionless(coupling_dim)
]) else "Some dimensional mismatches detected.")