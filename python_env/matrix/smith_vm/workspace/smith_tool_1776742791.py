# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Dimensional consistency check for the POASH‑Ω Omega‑Protocol embedding.
Base dimensions:
    [T]  : time
    [I]  : information (dimensionless in the proposal, but we keep it symbolic)
    [A]  : amplitude of a sensor metric (arbitrary)
    [S]  : power spectral density (amplitude^2 / frequency)
"""

import sympy as sp

# ----------------------------------------------------------------------
# Define dimensional symbols
# ----------------------------------------------------------------------
T = sp.symbols('T')          # time dimension
I = sp.symbols('I')          # information (Shannon entropy) dimension
A = sp.symbols('A')          # amplitude dimension
S = sp.symbols('S')          # PSD dimension = A^2 * T   (since PSD = |X|^2 / Δf)

# Derived dimensions
dim_dt   = T                     # dt
dim_dI   = I / T                 # dI/dt
dim_dI2  = dim_dI**2             # (dI/dt)^2
dim_lam  = sp.symbols('lam')     # λ (to be solved for)
dim_V    = dim_lam * I**4        # V(I) ~ λ * I^4 (I dimensionless → I^4 still I^4)
dim_Sint = dim_dI2 + dim_V       # integrand of action
dim_S    = dim_Sint * T          # S = ∫ integrand dt

print("Action dimensions:")
print("  integrand :", dim_sint)
print("  S[I]      :", dim_s)
print()

# ----------------------------------------------------------------------
# Stiffness invariants: ξ_N^{-2} = λ (3⟨coh⟩^{-1} + ⟨coh⟩^{-2})
# Assume coherence is dimensionless (standard definition)
# ----------------------------------------------------------------------
dim_coh = sp.symbols('coh')   # dimensionless
dim_xiN2 = dim_lam * (3/ dim_coh + 1/ dim_coh**2)   # λ * (coherent combination)
dim_xiN  = sp.sqrt(1/ dim_xiN2)   # ξ_N = (ξ_N^{-2})^{-1/2}

print("Stiffness invariants:")
print("  ξ_N^{-2}  :", dim_xiN2)
print("  ξ_N       :", dim_xiN)
print()

# ----------------------------------------------------------------------
# Mapping Φ_N = Φ_N0 + α * d(PHI)/dt   (α = ∂I/∂PHI)
# Assume Φ_N, Φ_N0 dimensionless, PHI dimensionless
# ----------------------------------------------------------------------
dim_PHI = I   # PHI taken as dimensionless information
dim_alpha = I / dim_PHI   # ∂I/∂PHI → dimensionless if I and PHI same dim
dim_dPHI_dt = dim_PHI / T
dim_term = dim_alpha * dim_dPHI_dt
print("Φ_N mapping:")
print("  α          :", dim_alpha)
print("  dPHI/dt    :", dim_dPHI_dt)
print("  α·dPHI/dt  :", dim_term)
print("  Expected   : dimensionless")
print()

# ----------------------------------------------------------------------
# Coherence definition from proposal:
# ⟨coh(k)⟩ = (1/N) Σ (1/k) ∫_0^T S_k(k) dk
# S_k(k) has dimensions of PSD * frequency? We'll treat S as PSD.
# ----------------------------------------------------------------------
# Integral ∫ S_k(k) dk over k (frequency) yields: PSD * (1/T) * T = PSD
# Actually ∫ S(k) dk over frequency gives power (A^2)
dim_integral = S * (1/T) * T   # S * (dk) where dk has 1/T
dim_term_inside = (1/ dim_coh) * dim_integral   # 1/k factor (k has 1/T) → T
dim_coh_prop = dim_term_inside   # after sum/avg (dimensionless factor)
print("Proposed coherence dimensions:")
print("  ⟨coh⟩ (as written):", dim_coh_prop)
print("  Expected dimensionless:", sp.simplify(dim_coh_prop))
print()

# ----------------------------------------------------------------------
# Check if we can assign dimensions to make everything consistent
# ----------------------------------------------------------------------
# We'll solve for dimensions of λ, I, A, S such that:
#   1. Action S[I] is dimensionless (natural units)
#   2. ξ_N has dimension of time
#   3. Φ_N mapping term is dimensionless
#   4. Coherence is dimensionless
# ----------------------------------------------------------------------
lam_dim, I_dim, A_dim, S_dim = sp.symbols('lam_dim I_dim A_dim S_dim')
# Build equations
eq1 = sp.Eq(dim_sint * T, 1)                     # S[I] dimensionless
eq2 = sp.Eq(dim_xiN, T)                          # ξ_N has time dimension
eq3 = sp.Eq(dim_term, 1)                         # α·dPHI/dt dimensionless
eq4 = sp.Eq(dim_coh_prop, 1)                     # coherence dimensionless

sol = sp.solve([eq1, eq2, eq3, eq4],
               [lam_dim, I_dim, A_dim, S_dim],
               dict=True)
print("Dimensional solution (if any):")
if sol:
    for s in sol:
        print(s)
else:
    print("No solution – the set of equations is inconsistent.")
print()

# ----------------------------------------------------------------------
# Additional check: V(I) dimensions must match kinetic term
# ----------------------------------------------------------------------
print("Kinetic term dimension:", dim_dI2)
print("Potential term dimension:", dim_V)
print("Are they equal?", sp.simplify(dim_dI2 - dim_V) == 0)