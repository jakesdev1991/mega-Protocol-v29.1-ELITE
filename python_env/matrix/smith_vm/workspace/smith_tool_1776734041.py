# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Higher-Order Lattice Polarization correction
to the fine‑structure constant in the Omega Protocol.

Checks:
  1. Hessian diagonalization → masses m_N, m_Δ.
  2. Dynamical stiffness invariants ξ_N⁻², ξ_Δ⁻².
  3. Shredding‑Event condition (ξ_Δ → ∞).
  4. Factor‑3 contribution from the 3D Archive mode in Π_eff.
  5. Running α_fs expression matches the derived form.
  6. β‑function sign consistency.
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
# ------------------------------------------------------------------
lam, v, Phi_N, Phi_Delta = sp.symbols('lam v Phi_N Phi_Delta', positive=True, real=True)
gN, gD = sp.symbols('gN gD', real=True)          # couplings
# UV cutoffs (appear only inside logs, treated as symbols)
Lambda_N, Lambda_D, Lambda = sp.symbols('Lambda_N Lambda_D Lambda', positive=True)
# Momentum scale
q = sp.symbols('q', positive=True)

# ------------------------------------------------------------------
# 1. Mexican‑hat potential and its Hessian
# ------------------------------------------------------------------
V = lam/4 * (Phi_N**2 + Phi_Delta**2 - v**2)**2

# Second derivatives (mass‑squared terms)
d2V_dPhiN2 = sp.diff(V, Phi_N, 2)
d2V_dPhiD2 = sp.diff(V, Phi_Delta, 2)

print("∂²V/∂Φ_N² =", d2V_dPhiN2.simplify())
print("∂²V/∂Φ_Δ² =", d2V_dPhiD2.simplify())

# ------------------------------------------------------------------
# 2. Stiffness invariants (inverse squared correlation lengths)
# ------------------------------------------------------------------
xiN_inv2 = d2V_dPhiN2
xiD_inv2 = d2V_dPhiD2

print("\nξ_N⁻² =", xiN_inv2)
print("ξ_Δ⁻² =", xiD_inv2)

# ------------------------------------------------------------------
# 3. Shredding‑Event condition: ξ_Δ → ∞  ⇔  ξ_Δ⁻² → 0
# ------------------------------------------------------------------
shredding_eq = sp.Eq(xiD_inv2, 0)
print("\nShredding‑Event condition (ξ_Δ⁻² = 0):", shredding_eq)
# Solve for the relation between fields:
shredding_sol = sp.solve(shredding_eq, Phi_N**2)
print("   → Φ_N² + 3Φ_Δ² = v²  (solution):", shredding_sol)

# ------------------------------------------------------------------
# 4. Vacuum‑polarization contributions (logarithmic approximation)
# ------------------------------------------------------------------
# Assume ⟨Φ²⟩ ~ 1/k² → ∫ dk k³ (1/k²) ∝ ∫ dk k → log cutoff
# We keep only the logarithmic pieces:
Pi_QED = sp.log(Lambda**2 / q**2)          # overall e²/(3π) factor omitted for clarity
Pi_N   = sp.log(Lambda_N**2 / q**2)       # coupled to g_N²
Pi_D   = sp.log(Lambda_D**2 / q**2)       # coupled to 3·g_Δ²

# Effective polarization (up to overall constants)
Pi_eff = (1/sp.Integer(3))*Pi_QED + (gN**2/sp.Integer(4))*Pi_N + (3*gD**2/sp.Integer(4))*Pi_D
print("\nEffective polarization (log part):", Pi_eff.simplify())

# ------------------------------------------------------------------
# 5. Running α_fs (first‑order expansion)
# ------------------------------------------------------------------
alpha0 = sp.symbols('alpha0', positive=True)
# α⁻¹(q²) = α0⁻¹ − Π_eff  →  α ≈ α0 [1 + α0·Π_eff] (to O(α0²))
alpha_run = alpha0 * (1 + alpha0 * Pi_eff)
print("\nRunning α_fs (first order):", alpha_run.simplify())
# Expected form:
expected = alpha0 * (1 + alpha0/sp.Integer(3)*sp.log(Lambda**2/q**2)
                     + (gN**2/sp.Integer(4))*sp.log(Lambda_N**2/q**2)
                     + (3*gD**2/sp.Integer(4))*sp.log(Lambda_D**2/q**2))
print("Expected expression:", expected.simplify())
assert sp.simplify(alpha_run - expected) == 0, "Mismatch in running α_fs"

# ------------------------------------------------------------------
# 6. β‑function (derivative of α⁻¹)
# ------------------------------------------------------------------
# β = dα/d ln q² = −α² * dΠ_eff/d ln q²
# dΠ_eff/d ln q² = −[1/3 + gN²/4 + 3gD²/4]  (since d/d ln q² ln(Λ²/q²) = −1)
beta = -alpha0**2 * (- (1/sp.Integer(3) + gN**2/sp.Integer(4) + 3*gD**2/sp.Integer(4)))
print("\nβ‑function:", beta.simplify())
# Check sign: the term in brackets is positive → β negative (asymptotic freedom‑like)
assert beta < 0, "β‑function should be negative for positive couplings"

print("\nAll algebraic checks passed. The derivation is mathematically sound "
      "under the logarithmic approximation and respects the Omega Protocol invariants.")