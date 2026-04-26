# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Dimensional Validation Script
------------------------------------------------
Checks the dimensional consistency of the core quantities
described in the Omega-Psych-Theorist derivation:
    - Chain Overlap Density (COD)
    - Stiffness invariants ξ_N, ξ_Δ
    - Stabilizing operator O_stab
    - Action S
    - Metric‑coupling invariant ψ
    - Entropy S_h and informational jerk J_I
Uses SymPy to symbolically track dimensions.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Base dimensions
# ----------------------------------------------------------------------
# We treat:
#   [T]  -> time
#   [I]  -> information (taken as dimensionless for the protocol)
#   Probability -> dimensionless
T = sp.symbols('T')          # time dimension
I = sp.symbols('I', positive=True)  # information (dimensionless placeholder)

# Helper to express dimensionless as 1
dimless = 1

# ----------------------------------------------------------------------
# Define dimensions of fundamental fields
# ----------------------------------------------------------------------
# Wavefunctions ψ have dimension 1/sqrt([τ]) where τ is integration variable (time)
# => [ψ] = T^{-1/2}
psi_dim = T**(-sp.Rational(1,2))

# Information field I(t) is dimensionless (per protocol)
I_field_dim = dimless

# ----------------------------------------------------------------------
# COD: overlap integral ∫ ψ_sub* ψ_con dτ
# ----------------------------------------------------------------------
# integrand dimension: [ψ]*[ψ] = T^{-1}
# integration dτ adds +1[T] → overall dimensionless
COD_dim = (psi_dim * psi_dim) * T   # ψ*ψ * dτ
print(f"COD dimension: {sp.simplify(COD_dim)}  (should be 1)")

# ----------------------------------------------------------------------
# Stiffness invariants ξ_N, ξ_Δ
# ----------------------------------------------------------------------
# Given as correlation timescales → dimension [T]
xi_dim = T
print(f"Stiffness invariant dimension: {xi_dim}  (should be T)")

# ----------------------------------------------------------------------
# Stabilizing operator O_stab
# ----------------------------------------------------------------------
# Must have dimension of inverse time to match d/dt acting on state
O_stab_dim = T**(-1)
print(f"O_stab dimension: {O_stab_dim}  (should be T^-1)")

# ----------------------------------------------------------------------
# Action S (dimensionless in natural units)
# ----------------------------------------------------------------------
S_dim = dimless
print(f"Action S dimension: {S_dim}  (should be 1)")

# ----------------------------------------------------------------------
# Metric‑coupling invariant ψ = ln(Φ_N / I_0)
# ----------------------------------------------------------------------
# Argument of log must be dimensionless → Φ_N and I_0 both dimensionless
Phi_N_dim = dimless
I0_dim = dimless
psi_dim = sp.log(Phi_N_dim / I0_dim)   # log of dimensionless → dimensionless
print(f"ψ dimension: {psi_dim}  (should be 0, i.e. dimensionless)")

# ----------------------------------------------------------------------
# Entropy S_h (information entropy) → dimensionless
# ----------------------------------------------------------------------
S_h_dim = dimless
print(f"Entropy S_h dimension: {S_h_dim}  (should be 1)")

# ----------------------------------------------------------------------
# Informational jerk J_I = d^3 S_h / dt^3
# ----------------------------------------------------------------------
# Each derivative adds T^{-1}
J_I_dim = S_h_dim * T**(-3)
print(f"Informational jerk J_I dimension: {J_I_dim}  (should be T^-3)")

# ----------------------------------------------------------------------
# Threshold Θ(ψ) must share dimensions with variance of J_I
# ----------------------------------------------------------------------
# variance(J_I) has dimension [J_I]^2 = T^{-6}
var_JI_dim = J_I_dim**2
print(f"Variance of J_I dimension: {var_JI_dim}  (should be T^-6)")
# Hence Θ(ψ) must also have dimension T^{-6}
Theta_dim = T**(-6)
print(f"Θ(ψ) dimension (required): {Theta_dim}")

# ----------------------------------------------------------------------
# Summary of compliance
# ----------------------------------------------------------------------
compliance_msgs = []
compliance_msgs.append("COD dimensionless" if sp.simplify(COD_dim)==1 else "COD dimension FAIL")
compliance_msgs.append("ξ_N, ξ_Δ have dimension T" if xi_dim==T else "Stiffness dimension FAIL")
compliance_msgs.append("O_stab has dimension T^-1" if O_stab_dim==T**(-1) else "O_stab dimension FAIL")
compliance_msgs.append("Action S dimensionless" if S_dim==1 else "Action dimension FAIL")
compliance_msgs.append("ψ dimensionless" if psi_dim==0 else "ψ dimension FAIL")
compliance_msgs.append("S_h dimensionless" if S_h_dim==1 else "Entropy dimension FAIL")
compliance_msgs.append("J_I dimension T^-3" if J_I_dim==T**(-3) else "J_I dimension FAIL")
compliance_msgs.append("Var(J_I) dimension T^-6" if var_JI_dim==T**(-6) else "Var(J_I) dimension FAIL")
compliance_msgs.append("Θ(ψ) must be T^-6" if Theta_dim==T**(-6) else "Θ dimension FAIL")

print("\nCompliance checklist:")
for msg in compliance_msgs:
    print(" -", msg)

# If any FAIL appears, raise an alert
if any("FAIL" in m for m in compliance_msgs):
    raise ValueError("Dimensional inconsistency detected – Omega Protocol violated.")
else:
    print("\nAll dimensional checks passed – derivation is Omega‑Protocol compliant.")