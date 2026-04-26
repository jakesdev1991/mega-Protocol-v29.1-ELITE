# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Audit: Validate the mathematical core of the tokamak jerk‑stability proposal.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. Symbolic jerk derivation from 1‑D diffusion equation
# ----------------------------------------------------------------------
r, t = sp.symbols('r t', real=True)
D, S = sp.symbols('D S', real=True)          # diffusivity, source term (may depend on r,t)
J = sp.Function('J')(r, t)                   # current density

# Diffusion equation for poloidal flux -> current density (simplified form)
# ∂J/∂t = D * ∂²J/∂r² + S
diff_eq = sp.Eq(sp.diff(J, t), D * sp.diff(J, r, r) + S)

# Compute the third time‑derivative (plasma current jerk proportional to ∂³J/∂t³)
J_t   = sp.diff(J, t)
J_tt  = sp.diff(J_t, t)
J_ttt = sp.diff(J_tt, t)

# Substitute using the diffusion equation repeatedly to express J_ttt in terms of spatial derivatives
# First derivative
J_t_sub   = diff_eq.rhs
# Second derivative
J_tt_sub  = sp.diff(J_t_sub, t)
# Replace ∂J/∂t again inside J_tt_sub
J_tt_sub  = J_tt_sub.subs(sp.diff(J, t), diff_eq.rhs)
# Third derivative
J_ttt_sub = sp.diff(J_tt_sub, t)
J_ttt_sub = J_ttt_sub.subs(sp.diff(J, t), diff_eq.rhs)
J_ttt_sub = J_ttt_sub.subs(sp.diff(J, t, t), sp.diff(diff_eq.rhs, t))

# Simplify assuming S varies slowly: ∂³S/∂t³ ≈ 0
# We explicitly drop terms containing diff(S, t, t, t)
J_ttt_simplified = sp.simplify(J_ttt_sub.subs(sp.diff(S, t, t, t), 0))
print("Jerk expression (∂³J/∂t³) after dropping ∂³S/∂t³:")
sp.pprint(J_ttt_simplified)
print("\n---\n")

# ----------------------------------------------------------------------
# 2. Invariant definitions from Mexican‑hat potential
# ----------------------------------------------------------------------
Phi_N, Phi_Delta, psi0, lam_N, lam_Delta = sp.symbols('Phi_N Phi_Delta psi0 lam_N lam_Delta', real=True, nonnegative=True)
V = (Phi_N**2 + Phi_Delta**2 - psi0**2)**2

# Second derivatives
V_PhiN_PhiN = sp.diff(V, Phi_N, 2)
V_PhiD_PhiD = sp.diff(V, Phi_Delta, 2)

xi_N_expr = 1/sp.sqrt(V_PhiN_PhiN)
xi_Delta_expr = 1/sp.sqrt(V_PhiD_PhiD)

print("Second derivatives of V:")
sp.pprint(V_PhiN_PhiN)
sp.pprint(V_PhiD_PhiD)
print("\nInvariant ξ_N = 1/√(∂²V/∂Φ_N²):")
sp.pprint(xi_N_expr)
print("\nInvariant ξ_Δ = 1/√(∂²V/∂Φ_Δ²):")
sp.pprint(xi_Delta_expr)
print("\n---\n")

# ----------------------------------------------------------------------
# 3. Positivity check for invariants given proposal bounds
# ----------------------------------------------------------------------
# Proposal: ξ_N ≥ 0.5, ξ_Δ ≥ 0.05  --> enforce denominators ≤ (1/0.5)² = 4 and ≤ (1/0.05)² = 400
# Since ξ = 1/√(second derivative), the condition ξ ≥ ε  <=>  second derivative ≤ 1/ε²
eps_N = 0.5
eps_D = 0.05

cond_N = sp.simplify(V_PhiN_PhiN - 1/eps_N**2)   # should be ≤ 0
cond_D = sp.simplify(V_PhiD_PhiD - 1/eps_D**2)   # should be ≤ 0

print("Condition for ξ_N ≥ 0.5  (second derivative ≤ 4):")
sp.pprint(cond_N)
print("\nCondition for ξ_Δ ≥ 0.05 (second derivative ≤ 400):")
sp.pprint(cond_D)
print("\n---\n")

# ----------------------------------------------------------------------
# 4. Boundary conditions: shredding event & informational freeze
# ----------------------------------------------------------------------
# Shredding: ξ_Δ → 0  <=> denominator → ∞  <=> V_PhiD_PhiD → 0
shredding_cond = sp.simplify(V_PhiD_PhiD)
print("Shredding condition (V_PhiD_PhiD = 0):")
sp.pprint(shredding_cond)
# Solve for Phi_N, Phi_Delta
sol_shred = sp.solve(shredding_cond, Phi_N)
print("\nSolutions for Φ_N giving shredding:")
sp.pprint(sol_shred)

# Informational freeze: I_p → 0  => ψ = ln(I_p/I_p0) → -∞
# No further algebra needed; just note that ψ diverges.
print("\nInformational freeze: ψ = ln(I_p/I_p0) → -∞ as I_p → 0 (by definition).")
print("\n---\n")

# ----------------------------------------------------------------------
# 5. Quick numerical sanity check (optional)
# ----------------------------------------------------------------------
np.random.seed(42)
# Sample some plausible values
psi0_val = 1.0
lam_N_val = 0.8
lam_Delta_val = 0.6

# Choose Phi_N, Phi_Delta that satisfy positivity
PhiN_samp = 0.9
PhiD_samp = 0.2

V_val = (PhiN_samp**2 + PhiD_samp**2 - psi0_val**2)**2
V_PhiN_PhiN_val = 2*lam_N_val*(3*PhiN_samp**2 + PhiD_samp**2 - psi0_val**2)  # from analytic derivative
V_PhiD_PhiD_val = 2*lam_Delta_val*(PhiN_samp**2 + 3*PhiD_samp**2 - psi0_val**2)

xi_N_num = 1/np.sqrt(V_PhiN_PhiN_val)
xi_Delta_num = 1/np.sqrt(V_PhiD_PhiD_val)

print("Numeric example:")
print(f"  Φ_N = {PhiN_samp}, Φ_Δ = {PhiD_samp}")
print(f"  V = {V_val:.4f}")
print(f"  ∂²V/∂Φ_N² = {V_PhiN_PhiN_val:.4f}  => ξ_N = {xi_N_num:.4f}")
print(f"  ∂²V/∂Φ_Δ² = {V_PhiD_PhiD_val:.4f}  => ξ_Δ = {xi_Delta_num:.4f}")
print(f"  ξ_N ≥ 0.5? {xi_N_num >= 0.5}")
print(f"  ξ_Δ ≥ 0.05? {xi_Delta_num >= 0.05}")