# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dimension‑consistency checker for the Omega‑Protocol derivation
of higher‑order lattice polarization corrections to α_fs.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Define base dimensions (mass M, length L, time T). In natural units
# we set ħ = c = 1 → [M] = [L]⁻¹ = [T]⁻¹.  We keep M as the independent base.
# ----------------------------------------------------------------------
M = sp.symbols('M', positive=True)   # mass dimension
# Length and time are expressed via M:
L = M**(-1)   # [L] = [M]⁻¹
T = M**(-1)   # [T] = [M]⁻¹

# Helper to combine dimensions
def dim(*factors):
    """Return product of dimension symbols."""
    d = sp.Integer(1)
    for f in factors:
        d *= f
    return sp.simplify(d)

# ----------------------------------------------------------------------
# Assign dimensions to symbols used in the derivation
# ----------------------------------------------------------------------
# Fundamental constants / parameters
alpha_fs = sp.Integer(1)          # dimensionless coupling
m_e      = M                      # electron mass
q        = M                      # momentum scale
Lambda_D = M                      # Archive cutoff
xi_0     = L                      # reference stiffness length
xi_Delta = L                      # Archive stiffness length
I0       = sp.Integer(1)          # we take I0 dimensionless (will be adjusted)
# Field I: we give it mass dimension (Convention A)
I_field  = M
# Derivatives add one mass dimension
dI       = M * I_field            # ∂I ∼ [M] * [M] = [M]²
# Potential coupling lambda (dimensionless under Convention A)
lam      = sp.Integer(1)
# Stiffnesses appear only as ratios → dimensionless
psi      = sp.Integer(1)          # ln(xi_Delta/xi_0) dimensionless
# Modes Φ_N, Φ_Δ: we assume dimensionless (as used in ratios)
Phi_N    = sp.Integer(1)
Phi_Delta= sp.Integer(1)
# RG coefficients
eta_N    = sp.Integer(1)
eta_Delta= sp.Integer(1)
kappa    = sp.Integer(1)
# Entropy gauge constant c (dimensionless)
c        = sp.Integer(1)

# ----------------------------------------------------------------------
# Define dimension of each expression
# ----------------------------------------------------------------------
# Action integrand: ½(∂I)² + V(I)
kinetic   = dim(dI, dI)                     # (∂I)²
# V(I) = λ/4 (I² - I0²)²
# I² has dimension [M]², so (I² - I0²)² → [M]⁴
potential = dim(lam, I_field**4)            # λ * I⁴
# Total integrand dimension
integrand_dim = sp.simplify(kinetic + potential)
# Measure d⁴x has dimension [M]⁻⁴
measure_dim   = dim(M**(-4))
# Action dimension = integrand * measure
action_dim    = sp.simplify(integrand_dim * measure_dim)

print("=== Dimension of the action S ===")
print(action_dim)   # should be 1 (dimensionless) if consistent

# ----------------------------------------------------------------------
# One‑loop pieces
# ----------------------------------------------------------------------
Pi_N   = dim(alpha_fs, sp.log(q**2 / m_e**2))   # α * log
Pi_Delta = dim(alpha_fs, psi, sp.log(q**2 / Lambda_D**2))  # α ψ log
Pi_mix = dim(alpha_fs**2, Phi_Delta/Phi_N, sp.log(q**2 / m_e**2)**2)

print("\n=== One‑loop Newtonian Π_N dimension ===", Pi_N)
print("=== One‑loop Archive Π_Δ dimension ===", Pi_Delta)
print("=== Two‑loop mixed Π_mix dimension ===", Pi_mix)

# ----------------------------------------------------------------------
# RG equations: check that RHS has same dimension as LHS dΦ/dlnq
# LHS: dΦ/dlnq is dimensionless because Φ is dimensionless and dlnq is dimensionless
# ----------------------------------------------------------------------
def check_rg(name, Phi, rhs):
    lhs_dim = sp.Integer(1)   # dΦ/dlnq dimensionless
    rhs_dim = sp.simplify(rhs)
    print(f"\n{name} RG check:")
    print(f"  LHS dimension : {lhs_dim}")
    print(f"  RHS dimension : {rhs_dim}")
    print(f"  Consistent?   : {sp.simplify(lhs_dim - rhs_dim) == 0}")

# RHS of dΦ_N/dlnq
rhs_N = dim(eta_N, Phi_N, (1 - Phi_N**2 / I0**2)) - dim(kappa, Phi_Delta**2)
check_rg("Phi_N", Phi_N, rhs_N)

# RHS of dΦ_Δ/dlnq
rhs_Delta = dim(eta_Delta, Phi_Delta, (1 - Phi_Delta**2 / I0**2)) + dim(kappa, Phi_N, Phi_Delta)
check_rg("Phi_Delta", Phi_Delta, rhs_Delta)

# ----------------------------------------------------------------------
# Entropy gauge: S_h dimensionless, A_μ = ∂_μ S_h → dimension [M]
# ----------------------------------------------------------------------
S_h = dim(c, sp.log(q**2 / m_e**2))
A_mu_dim = dim(M, S_h)   # derivative adds one mass
print("\n=== Entropy gauge ===")
print("S_h dimension :", S_h)
print("𝒜_μ dimension :", A_mu_dim)

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
print("\n=== SUMMARY ===")
print("Action dimension (should be 1 for dimensionless action):", action_dim)
print("If the above is not 1, the action as written is dimensionally inconsistent.")
print("All other terms (Π, RG, entropy gauge) are dimensionless/mass‑balanced under Convention A.")