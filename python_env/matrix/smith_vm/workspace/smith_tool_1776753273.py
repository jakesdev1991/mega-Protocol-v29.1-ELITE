# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Dimensional consistency audit for the POASH‑Ω / Omega Protocol embedding.
We assign base dimensions: [M] mass, [L] length, [T] time, [Θ] temperature,
[I] electric current, [J] luminous intensity, [N] amount of substance.
Only [T] is relevant here; we treat all other dimensions as 0.
A dimensionless quantity has zero exponent for all bases.
"""

import sympy as sp

# Base dimensions
M, L, T, Theta, I, J, N = sp.symbols('M L T Theta I J N')
def dim(*exps):
    """Return a dimension tuple (M,L,T,Theta,I,J,N)."""
    return tuple(exps)

# Helper to compare dimensions
def same_dim(d1, d2):
    return d1 == d2

# Assign dimensions to symbols used in the proposal
# Fundamental constants (set to dimensionless for simplicity)
hbar = dim(0,0,0,0,0,0,0)   # ħ = 1 in natural units
# Dimensions of time
t_dim = dim(0,0,1,0,0,0,0)  # [T]

# Field I(t) = - Σ p_k log p_k  (Shannon entropy) -> dimensionless
I_dim = dim(0,0,0,0,0,0,0)

# Time derivative of I
Idot_dim = div(I_dim, t_dim)   # [T]^{-1}
def div(d1, d2):
    return tuple(a-b for a,b in zip(d1,d2))

# Kinetic term: 1/2 (dI/dt)^2
kin_dim = mul(Idot_dim, Idot_dim)   # [T]^{-2}
def mul(d1,d2):
    return tuple(a+b for a,b in zip(d1,d2))

# Potential V(I) = λ/4 (I^2 - I0^2)^2
# I is dimensionless, so (I^2 - I0^2)^2 is dimensionless
# λ is claimed to have [T]^{-2}
lam_dim = dim(0,0,-2,0,0,0,0)
V_dim = mul(lam_dim, dim(0,0,0,0,0,0,0))   # [T]^{-2}

# Lagrangian L = kinetic + V
L_dim = add(kin_dim, V_dim)   # should be same as each term
def add(d1,d2):
    if d1 != d2:
        raise ValueError(f"Dimension mismatch: {d1} vs {d2}")
    return d1

print("Kinetic term dimension:", kin_dim)
print("Potential term dimension:", V_dim)
print("Lagrangian dimension (should be uniform):", L_dim)

# Action S = ∫ L dt -> add one power of T
S_dim = mul(L_dim, t_dim)
print("Action dimension:", S_dim)   # Expect dimensionless if L had [T]^{-1}

# ---- Stiffness invariants ----
# Average coherence <coh> is dimensionless
coh_dim = dim(0,0,0,0,0,0,0)

# λ_N = λ (3 <coh>^{-1} + <coh>^{-2})
# Since <coh> is dimensionless, its powers are dimensionless
lamN_dim = lam_dim   # same as λ
lamD_dim = lam_dim

# ξ_N^{-2} = λ_N  => ξ_N has dimension [T]
xiN2_dim = lamN_dim   # [T]^{-2}
# take sqrt to get ξ_N dimension: [T]
# sqrt of [T]^{-2} is [T]^{-1}? Wait: (ξ_N)^{-2} has [T]^{-2} => ξ_N has [T]
# Let's compute: if ξ_N^2 has [T]^{-2}, then ξ_N has [T]^{-1}. 
# Actually we defined ξ_N^{-2} = λ_N, so ξ_N^2 = 1/λ_N.
# Since λ_N has [T]^{-2}, 1/λ_N has [T]^{2}, thus ξ_N has [T].
# We'll check by inverting.
def invert_dim(d):
    return tuple(-x for x in d)

xiN_sq_dim = invert_dim(lamN_dim)   # [T]^{2}
# ξ_N dimension is sqrt of that: half the exponents
xiN_dim = tuple(x/2 for x in xiN_sq_dim)
print("ξ_N dimension (derived):", xiN_dim)   # Expect [T]

# Same for ξ_Δ
xiD_sq_dim = invert_dim(lamD_dim)
xiD_dim = tuple(x/2 for x in xiD_sq_dim)
print("ξ_Δ dimension (derived):", xiD_dim)   # Expect [T]

# ψ = ln(ξ/ξ0) -> argument of log must be dimensionless
# Therefore ξ must be dimensionless *if* we treat log as taking dimensionless argument.
# In natural physics, log of a dimensional quantity is defined via a reference,
# making the argument dimensionless. We'll treat ψ as dimensionless regardless.
psi_dim = dim(0,0,0,0,0,0,0)

# Covariant modes: claimed dimensionless
PhiN_dim = dim(0,0,0,0,0,0,0)
PhiD_dim = dim(0,0,0,0,0,0,0)

# Check relations ξ_N = ∂Φ_N/∂ψ, ξ_Δ = ∂Φ_Δ/∂psi
# Derivative w.r.t. a dimensionless variable does not change dimension
# So RHS dimensions are those of Φ_N, Φ_D
print("∂Φ_N/∂ψ dimension:", PhiN_dim)
print("∂Φ_Δ/∂ψ dimension:", PhiD_dim)
print("ξ_N dimension:", xiN_dim)
print("ξ_Δ dimension:", xiD_dim)
print("Are they equal?", same_dim(xiN_dim, PhiN_dim), same_dim(xiD_dim, PhiD_dim))

# ---- Mapping from PHI to I via chain rule ----
# PHI is dimensionless (health index)
PHI_dim = dim(0,0,0,0,0,0,0)
# p_k = |A_k|^2 / Σ|A_j|^2  -> dimensionless (ratio)
p_dim = dim(0,0,0,0,0,0,0)
# I = - Σ p_k log p_k  -> dimensionless
I_dim2 = dim(0,0,0,0,0,0,0)
# dI/dt = (Σ p_k log p_k) dPHI/dt
# The factor (Σ p_k log p_k) is dimensionless (since p_k dimensionless)
# dPHI/dt has dimension [T]^{-1}
dPHI_dt_dim = div(PHI_dim, t_dim)   # [T]^{-1}
dI_dt_dim = mul(dim(0,0,0,0,0,0,0), dPHI_dt_dim)   # [T]^{-1}
print("dI/dt dimension from chain rule:", dI_dt_dim)
print("Actual dI/dt dimension (from I definition):", Idot_dim)
print("Match?", same_dim(dI_dt_dim, Idot_dim))

# ---- Variance term in Φ_Δ ----
# Var(A) = ⟨A^2⟩ - ⟨A⟩^2  -> dimension of A^2
# Let A have dimension a_dim (unknown). We'll keep it symbolic.
a_dim = sp.symbols('a_dim')
# Assume a_dim has some dimension; we represent as (0,0,exp,0,0,0,0) where exp is exponent of T
# For simplicity, treat A as having dimension [T]^0 (i.e., dimensionless) – common for normalized amplitudes.
# If A is dimensionless, Var(A) is dimensionless.
VarA_dim = dim(0,0,0,0,0,0,0)
# γ = ∂^2 I / ∂A^2  -> I dimensionless, A dimensionless => γ dimensionless
gamma_dim = dim(0,0,0,0,0,0,0)
term_dim = mul(gamma_dim, VarA_dim)   # dimensionless
print("γ Var(A) dimension:", term_dim)
print("Φ_Δ dimension claimed:", PhiD_dim)
print("Match?", same_dim(term_dim, PhiD_dim))

# ---- MPC cost function terms ----
# (1-PHI)^2 dimensionless
cost1_dim = dim(0,0,0,0,0,0,0)
# λ1 (Φ_Δ)^2 : λ1 dimensionless? Assume λ1 dimensionless for now
lam1_dim = dim(0,0,0,0,0,0,0)
cost2_dim = mul(lam1_dim, mul(PhiD_dim, PhiD_dim))
print("Cost term (Φ_Δ)^2 dimension:", cost2_dim)
# λ2 ||∇A||^2 : ∇A has dimension of A per unit time (if derivative w.r.t time)
# If A dimensionless, ∇A has [T]^{-1}, squared gives [T]^{-2}
# λ2 must then have [T]^{2} to make term dimensionless.
lam2_dim = div(dim(0,0,2,0,0,0,0), dim(0,0,0,0,0,0,0))  # [T]^{2}
gradA_dim = div(a_dim, t_dim)   # [T]^{-1} if a_dim dimensionless
gradA2_dim = mul(gradA_dim, gradA_dim)   # [T]^{-2}
cost3_dim = mul(lam2_dim, gradA2_dim)
print("Cost term ||∇A||^2 dimension:", cost3_dim)
print("Is cost3 dimensionless?", same_dim(cost3_dim, dim(0,0,0,0,0,0,0)))

# Constraint dimensions: PHI ≥ 0.4 etc. are dimensionless checks – OK.

print("\n--- Summary of mismatches ---")
issues = []
if not same_dim(kin_dim, V_dim):
    issues.append("Kinetic and potential terms have different dimensions.")
if not same_dim(S_dim, dim(0,0,0,0,0,0,0)):
    issues.append("Action is not dimensionless (check Lagrangian scaling).")
if not same_dim(xiN_dim, PhiN_dim):
    issues.append("ξ_N dimension does not match Φ_N dimension (violates ∂Φ_N/∂ψ relation).")
if not same_dim(xiD_dim, PhiD_dim):
    issues.append("ξ_Δ dimension does not match Φ_Δ dimension.")
if not same_dim(dI_dt_dim, Idot_dim):
    issues.append("Chain‑rule expression for dI/dt is dimensionally inconsistent.")
if not same_dim(term_dim, PhiD_dim):
    issues.append("γ Var(A) term dimension does not match Φ_Δ.")
if not same_dim(cost3_dim, dim(0,0,0,0,0,0,0)):
    issues.append("MPC gradient penalty term is not dimensionless (missing scale).")

if issues:
    for i, msg in enumerate(issues, 1):
        print(f"{i}: {msg}")
else:
    print("All checked equations are dimensionally homogeneous.")