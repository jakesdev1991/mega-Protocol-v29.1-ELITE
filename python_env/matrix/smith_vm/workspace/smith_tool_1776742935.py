# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the Omega‑Rubric‑compliant tokamak proposal.
Checks:
  1. Mexican‑hat potential V = (Φ_N^2 + Φ_Δ^2 - ψ0^2)^2
  2. Second derivatives ∂²V/∂Φ_N^2 and ∂²V/∂Φ_Δ^2
  3. Correlation lengths ξ_N, ξ_Δ = (∂²V/∂Φ^2)^(-1/2)
  4. Instability condition: ξ → ∞  <=>  ∂²V/∂Φ^2 → 0
  5. Proposed (incorrect) condition: ξ → 0  <=>  ∂²V/∂Φ^2 → ∞
"""

import sympy as sp
import numpy as np

# Symbols
ΦN, ΦΔ, ψ0 = sp.symbols('ΦN ΦΔ ψ0', real=True, nonnegative=True)

# Mexican‑hat potential
V = (ΦN**2 + ΦΔ**2 - ψ0**2)**2

# Second derivatives
dV_dΦN2 = sp.diff(V, ΦN, 2)
dV_dΦΔ2 = sp.diff(V, ΦΔ, 2)

print("Second derivatives:")
print("∂²V/∂ΦN² =", dV_dΦN2.simplify())
print("∂²V/∂ΦΔ² =", dV_dΦΔ2.simplify())
print()

# Correlation lengths (inverse sqrt of second derivative)
xi_N = sp.simplify(1/sp.sqrt(dV_dΦN2))
xi_Δ = sp.simplify(1/sp.sqrt(dV_dΦΔ2))

print("Correlation lengths:")
print("ξ_N =", xi_N)
print("ξ_Δ =", xi_Δ)
print()

# Instability when second derivative → 0  => ξ → ∞
instability_cond_N = sp.solve(dV_dΦN2, ΦN**2 + ΦΔ**2)
instability_cond_Δ = sp.solve(dV_dΦΔ2, ΦN**2 + ΦΔ**2)

print("Instability (second derivative = 0) conditions:")
print("For ΦN: ΦN² + ΦΔ² =", instability_cond_N)
print("For ΦΔ: ΦN² + ΦΔ² =", instability_cond_Δ)
print()

# What the proposal incorrectly states: ξ → 0  <=>  ΦN² + 3ΦΔ² → ψ0²
# Let's test that claim:
claim_lhs = ΦN**2 + 3*ΦΔ**2
claim_rhs = ψ0**2
print("Proposed claim: ΦN² + 3ΦΔ² → ψ0²  (=> ξ_Δ → 0)")
print("Evaluating ξ_Δ under that claim:")
xi_Δ_claim = xi_Δ.subs({ΦN**2 + 3*ΦΔ**2: ψ0**2})
print("ξ_Δ (substituted) =", sp.simplify(xi_Δ_claim))
print("Is ξ_Δ zero? ->", sp.simplify(xi_Δ_claim) == 0)
print()

# Correct instability for ΦΔ: set ∂²V/∂ΦΔ² = 0
correct_cond_Δ = sp.solve(dV_dΦΔ2, ΦN**2 + 3*ΦΔ**2)
print("Correct instability condition for ΦΔ (∂²V/∂ΦΔ² = 0):")
print("ΦN² + 3ΦΔ² =", correct_cond_Δ)
print("Under this condition ξ_Δ →", sp.limit(xi_Δ, dV_dΦΔ2, 0, dir='+'))
print()

# Numerical example to illustrate divergence vs. zero
ψ0_val = 1.0
# Choose parameters approaching the instability from below
vals = np.linspace(0.0, 0.99, 5) * ψ0_val**2  # ΦN²+3ΦΔ² values
for target in vals:
    # solve for ΦN,ΦΔ satisfying ΦN²+3ΦΔ² = target (pick ΦN=0 for simplicity)
    ΦΔ_sq = target / 3.0
    ΦN_sq = 0.0
    ΦN_num = np.sqrt(ΦN_sq)
    ΦΔ_num = np.sqrt(ΦΔ_sq)
    # compute ξ_Δ numerically
    dV = 4.0 * (ΦN_num**2 + 3*ΦΔ_num**2 - ψ0_val**2)  # from derivative expression
    xi = 1.0/np.sqrt(np.abs(dV)) if dV != 0 else np.inf
    print(f"Target ΦN²+3ΦΔ²={target:.3f} => ξ_Δ ≈ {xi:.3f} (dV={dV:.3f})")
    if np.isinf(xi):
        print("  → ξ diverges (instability approached)")
print()

# Summary
print("\n--- SUMMARY ---")
print("The proposal’s boundary condition (ξ → 0) is mathematically incorrect.")
print("Correct instability occurs when the second derivative of V → 0,")
print("which makes ξ → ∞.  The MPC‑Ω constraints and anomaly‑detection")
print("thresholds must be revised accordingly.")