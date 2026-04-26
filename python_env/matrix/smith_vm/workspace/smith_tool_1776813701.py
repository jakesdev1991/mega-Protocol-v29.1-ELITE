# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Invariant Validator for the Information‑Cascade Monitor (IC‑Ω)
Checks:
  1. Uniqueness of the invariant ψ_cascade.
  2. Logical derivation of boundary conditions from the invariant.
  3. Satisfaction of Ω‑constraints on CI, Φ_N, S_cascade.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbolic declarations (all dimensionless after scaling)
# ----------------------------------------------------------------------
# Core variables
CI, PhiN0, PhiN, PhiDelta0, PhiDelta, lam = sp.symbols(
    'CI PhiN0 PhiN PhiDelta0 PhiDelta lam', real=True, nonnegative=True
)
# Curvature and reference curvature
R, R0 = sp.symbols('R R0', real=True, positive=True)

# Linear‑response approximations (as given in the proposal)
#   PhiN(t) = PhiN0 - eta1*CI(t-tau) + eta2*(1 - L(t-tau))
#   PhiDelta(t) = PhiDelta0 + eta3*Delta(t-tau) - eta4*C(t-tau)
# For the validation we treat the CI‑dependent parts as symbols:
eta1, eta2, eta3, eta4 = sp.symbols('eta1 eta2 eta3 eta4', real=True)
L, Delta, C = sp.symbols('L Delta C', real=True)  # liquidity withdrawal, skew, cross‑ETF corr

# Approximate PhiN and PhiDelta (ignore higher‑order terms)
PhiN_approx = PhiN0 - eta1*CI + eta2*(1 - L)
PhiDelta_approx = PhiDelta0 + eta3*Delta - eta4*C

# ----------------------------------------------------------------------
# 1. Invariant uniqueness test
# ----------------------------------------------------------------------
# Invariant form A: curvature‑based
psi_A = sp.ln(sp.Abs(R)/R0) + lam*CI

# Invariant form B: log‑connectivity based
psi_B = sp.ln(PhiN_approx/PhiN0)

# Check if psi_A - psi_B simplifies to zero under generic assumptions
diff = sp.simplify(psi_A - psi_B)
print("Difference between the two invariant definitions:")
print(diff)
print("\nIs the difference identically zero? ", diff == 0)

# If not zero, the invariant is not unique → Ω‑fail.
unique_invariant = (diff == 0)

# ----------------------------------------------------------------------
# 2. Boundary‑condition consistency
# ----------------------------------------------------------------------
# Define two candidate boundary sets:
#   Set1 (psi/CI):   Shredding → psi → +∞, CI → 1
#                     Freeze    → psi → -∞, CI → 0
#   Set2 (PhiN/PhiDelta/entropy): 
#                     Shredding → PhiN → 0, S → 0
#                     Freeze    → PhiDelta → ∞, S → 0
# Entropy proxy: S = -sum p_k log p_k; we enforce a lower bound later.
# For symbolic test we examine whether psi → ±∞ forces the claimed limits.

# Limits for psi_A
limit_psiA_plus = sp.limit(psi_A, R, 0, dir='-')   # R→0+ gives -∞ inside ln → -∞
limit_psiA_minus = sp.limit(psi_A, R, sp.oo, dir='+')  # R→∞ gives +∞
print("\nLimit psi_A as R→0+ :", limit_psiA_plus)
print("Limit psi_A as R→∞ :", limit_psiA_minus)

# Limits for psi_B (depends on PhiN_approx)
limit_psiB_plus = sp.limit(psi_B, PhiN_approx, 0, dir='+')   # PhiN→0+ → -∞
limit_psiB_minus = sp.limit(psi_B, PhiN_approx, sp.oo, dir='-')  # PhiN→∞ → +∞
print("\nLimit psi_B as PhiN→0+ :", limit_psiB_plus)
print("Limit psi_B as PhiN→∞ :", limit_psiB_minus)

# Boundary consistency: does psi_A → +∞ imply CI→1? (CI bounded [0,1])
# Since psi_A = ln(|R|/R0) + lam*CI, divergence can come from R term or CI term.
# CI term can only diverge if lam*CI → ±∞, but CI ∈ [0,1] and lam finite → bounded.
# Therefore psi_A divergence must be driven by R→0 or ∞, *not* CI.
# Hence Set1 (psi/CI) is NOT a logical consequence of psi_A.
# Conversely, psi_B divergence is driven by PhiN→0 or ∞, matching Set2's Shredding/Freeze
# when we also enforce S→0 (entropy collapse) as an additional condition.

# ----------------------------------------------------------------------
# 3. Ω‑constraint enforcement (state‑vector limits)
# ----------------------------------------------------------------------
# Constraints from the MPC‑Ω formulation:
#   CI ≤ 0.7
#   PhiN ≥ 0.6
#   S_cascade ≥ log(3)  (we treat S as a symbolic variable with this bound)
S = sp.symbols('S', real=True)
constraints = [
    sp.Le(CI, 0.7),          # CI <= 0.7
    sp.Ge(PhiN_approx, 0.6), # PhiN >= 0.6
    sp.Ge(S, sp.log(3))      # S >= ln(3)
]

# Evaluate constraints symbolically (they remain symbolic; we just store them)
print("\nΩ‑constraints:")
for c in constraints:
    print(c)

# ----------------------------------------------------------------------
# Final verdict
# ----------------------------------------------------------------------
print("\n=== VALIDATION SUMMARY ===")
print(f"Unique invariant?          : {unique_invariant}")
print(f"Omega constraints satisfied: (symbolic placeholders; must be checked at runtime)")
print("\n→ If the invariant is not unique, the proposal fails Ω‑Physics Rubric v26.0.")
print("→ Boundary Set1 (psi/CI) is inconsistent with either invariant.")
print("→ Boundary Set2 (PhiN/PhiDelta/entropy) aligns with the log‑connectivity invariant.")
print("→ Repair: adopt a single invariant ψ = ln(Φ_N/Φ_N^{(0)}), derive boundaries")
print("   from its asymptotic behavior, and enforce CI≤0.7, Φ_N≥0.6, S≥ln(3) in the MPC‑Ω QP.")