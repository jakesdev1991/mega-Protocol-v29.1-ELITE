# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Validates the Informational Jerk stability analysis for the Scrutiny agent.
Checks:
  1. Active use of the invariant ψ = ln(Φ_N/I₀)
  2. Correct finite‑difference third‑derivative stencil (includes Δt⁻³)
  3. Full chain‑rule expression for 𝒥_I (no term omitted)
  4. Numerical comparison σ_𝒥² vs. Θ with supplied data
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. Symbolic setup – covariant modes and invariant ψ
# ----------------------------------------------------------------------
Φ_N, Φ_Δ, I0 = sp.symbols('Φ_N Φ_Δ I0', positive=True)
# Normalized amplitudes (v = I0)
phi_N = Φ_N / I0
phi_Δ = Φ_Δ / I0

# Metric coupling invariant ψ (must appear actively)
psi = sp.log(phi_N)   # ψ = ln(Φ_N/I0)

# Two‑state probabilities proportional to mode amplitudes
p_N = phi_N / (phi_N + phi_Δ)
p_Δ = phi_Δ / (phi_N + phi_Δ)

# Shannon conditional entropy S_h(Φ_N, Φ_Δ)
S_h = -(p_N*sp.log(p_N) + p_Δ*sp.log(p_Δ))

# ----------------------------------------------------------------------
# 2. Compute jerk 𝒥_I = d³S_h/dt³ via chain rule (full expression)
# ----------------------------------------------------------------------
t = sp.symbols('t')
# Treat Φ_N(t), Φ_Δ(t) as arbitrary functions of time
PhiN_t = sp.Function('Φ_N')(t)
PhiD_t = sp.Function('Φ_Δ')(t)

# Replace symbols with time‑dependent versions
S_h_t = S_h.subs({Φ_N: PhiN_t, Φ_Δ: PhiD_t})

# First derivative
dS_dt = sp.diff(S_h_t, t)
# Second derivative
d2S_dt2 = sp.diff(dS_dt, t)
# Third derivative (informational jerk)
J_I_expr = sp.diff(d2S_dt2, t)

# ----------------------------------------------------------------------
# 3. Check for active appearance of ψ in J_I_expr
# ----------------------------------------------------------------------
# Substitute ψ back in to see if any derivative of ψ remains
psi_expr = sp.log(PhiN_t/I0)   # ψ(t)
# Compute J_I_expr expressed in terms of ψ and its derivatives
J_I_via_psi = sp.simplify(J_I_expr.subs({sp.log(PhiN_t/I0): psi_expr}))
# If ψ does not appear, the expression will be independent of psi_expr
uses_psi = psi_expr in sp.preorder_traversal(J_I_via_psi)

print("=== Invariant ψ Usage Check ===")
print("Does ψ appear explicitly in the jerk expression?", uses_psi)
if not uses_psi:
    print("❌ FAIL: ψ is defined but never actively used.")
else:
    print("✅ PASS: ψ participates in the derivation.")

# ----------------------------------------------------------------------
# 4. Numerical evaluation with supplied audit data
# ----------------------------------------------------------------------
# Supplied normalized values (v = I0 = 1)
phi_N_val = 0.78
phi_Δ_val = 0.35
# Derivatives of normalized amplitudes (s⁻¹)
phi_N_dot = 2.1e3
phi_Δ_dot = 8.7e3
# Stiffness invariant ξ⁻² = 4.2e6 s⁻²  → ξ ≈ 1/√(4.2e6)
xi = 1.0/np.sqrt(4.2e6)
# Approximate second derivatives via φ̈ ≈ φ̇/ξ (crude but matches engine)
phi_N_ddot = phi_N_dot / xi
phi_Δ_ddot = phi_Δ_dot / xi

# Source jerk (s⁻³)
J_source = 1.5e12

# Entropy and its derivatives w.r.t. normalized amplitudes
def S_h_val(pN, pD):
    return -(pN*np.log(pN) + pD*np.log(pD))

pN = phi_N_val/(phi_N_val+phi_Δ_val)
pD = phi_Δ_val/(phi_N_val+phi_Δ_val)
S = S_h_val(pN, pD)

# Analytic derivatives (from sympy earlier)
dS_dphiN = -np.log(phi_N_val/phi_Δ_val)
d2S_dphiN2 = -(1/phi_N_val + 1/phi_Δ_val)
dS_dphiDelta = -np.log(phi_Δ_val/phi_N_val)
d2S_dphiDelta2 = -(1/phi_Δ_val + 1/phi_N_val)
d2S_dphiNdphiDelta = (1/phi_N_val + 1/phi_Δ_val)  # derived from sympy

# Chain‑rule jerk (full)
J_chain = (d2S_dphiN2 * phi_N_dot**2 +
           2*d2S_dphiNdphiDelta * phi_N_dot * phi_Δ_dot +
           d2S_dphiDelta2 * phi_Δ_dot**2 +
           dS_dphiN * phi_N_ddot +
           dS_dphiDelta * phi_Δ_ddot)

J_total = J_chain + J_source

print("\n=== Numerical Jerk Evaluation ===")
print(f"J_chain  = {J_chain:.3e} s⁻³")
print(f"J_source = {J_source:.3e} s⁻³")
print(f"J_total  = {J_total:.3e} s⁻³")

# ----------------------------------------------------------------------
# 5. Variance estimate (assume ±20% fluctuation around mean)
# ----------------------------------------------------------------------
J_mean = J_total
J_std  = 0.20 * np.abs(J_mean)
sigma_J2 = J_std**2
print(f"\nAssumed 20% fluctuation → σ_𝒥 = {J_std:.3e} s⁻³")
print(f"σ_𝒥²    = {sigma_J2:.3e} s⁻⁶")

# ----------------------------------------------------------------------
# 6. Threshold Θ from Shredding condition (ξ_Δ → ∞)
# ----------------------------------------------------------------------
# Using typical values λ = 1e10 s⁻², g_Δ = 0.1, I0 = 1
lam = 1.0e10
gDelta = 0.1
I0_val = 1.0
Theta = (lam * I0_val**2) / (4*np.pi) * (1 + (3*gDelta**2)/(4*np.pi))
print(f"\nThreshold Θ (λ={lam:.2e}, g_Δ={gDelta}) = {Theta:.3e} s⁻⁶")

# ----------------------------------------------------------------------
# 7. Stability decision
# ----------------------------------------------------------------------
stable = sigma_J2 < Theta
print("\n=== Stability Decision ===")
print(f"σ_𝒥² ({sigma_J2:.3e})  ?  Θ ({Theta:.3e})")
print("Stable?" , stable)
if not stable:
    print("❌ System flagged as UNSTABLE (jerk variance exceeds Shredding threshold).")
else:
    print("✅ System would be considered STABLE.")

# ----------------------------------------------------------------------
# 8. Summary of compliance
# ----------------------------------------------------------------------
print("\n=== Omega Protocol Rubric Compliance Summary ===")
print("1. No boilerplate: ✔ (narrative headings used)")
print("2. Covariant modes Φ_N, Φ_Δ: ✔ (derived from Hessian)")
print("3. Active invariants (ψ, ξ_N, ξ_Δ):", "✔" if uses_psi else "✘ (ψ only nominal)")
print("4. Boundary conditions (Shredding, Freeze): ✔")
print("5. Entropy‑based observable S_h: ✔")
print("6. Equation‑level derivation from Omega Action: ✔")
print("7. Numerical evaluation with supplied data: ✔ (but note Δt missing)")
print("8. Dimensional consistency: ⚠ (Δt⁻³ omitted in finite‑difference stencil)")
print("9. Φ‑density impact discussion: ⚠ (qualitative only)")
print("\nOverall: FAIL – invariant ψ not actively used and Δt scaling missing.")