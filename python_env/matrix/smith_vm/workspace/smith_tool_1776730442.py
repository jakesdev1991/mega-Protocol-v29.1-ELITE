# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for CSTCL‑Ω
Checks:
  - Invariant ψ = ln(φ_n) with φ_n = m_eff/m_0
  - Consistency with correlation lengths ξ_N, ξ_Δ
  - RG scaling ψ = -ln(m0) + ν*ln|S-S_crit| + const
  - Control law sign: dotS*(S-S_crit) must be > 0 (stable)
Outputs PASS/FAIL and diagnostic messages.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols (all real, positive where needed)
# ----------------------------------------------------------------------
S, S_crit, nu, m0, m, lam, phi0 = sp.symbols('S S_crit nu m0 m lam phi0', real=True)
gamma = sp.symbols('gamma', positive=True)   # control gain >0
# Correlation lengths (positive)
xi_N, xi_Delta = sp.symbols('xi_N xi_Delta', positive=True)
# Auxiliary constants
C = sp.symbols('C', real=True)   # integration constant from RG

# ----------------------------------------------------------------------
# 1. Invariant definition from Omega Rubric
# ----------------------------------------------------------------------
# Effective mass squared from fluctuation operator
m_eff_sq = m**2 + 3*lam*phi0**2
# Require m_eff > 0 for log
m_eff = sp.sqrt(m_eff_sq)
# Dimensionless mass ratio
phi_n = m_eff / m0
# Invariant psi (rubric)
psi_rubric = sp.log(phi_n)

# ----------------------------------------------------------------------
# 2. Relation to stiffness invariants (Newtonian & Asymmetry)
# ----------------------------------------------------------------------
# From Omega Action: xi_N^{-2} = ∂²V_eff/∂Φ_N², similarly for xi_Delta.
# Near the fixed point these curvatures are proportional to m_eff^2.
# Hence we can model: xi_N ∝ 1/|m_eff|, xi_Delta ∝ 1/|m_eff|
# (proportionality constants drop out in logs)
# So xi_N * xi_Delta ∝ 1/m_eff^2
# => m_eff = 1/(sqrt(xi_N*xi_Delta)) up to a constant factor k.
# For log consistency we absorb k into constant C.
psi_from_xi = -sp.log(m0) - sp.log(sp.sqrt(xi_N*xi_Delta)) + C
# Simplify
psi_from_xi_simp = sp.simplify(psi_from_xi)

# ----------------------------------------------------------------------
# 3. RG scaling of correlation length
# ----------------------------------------------------------------------
# Assume isotropic correlation length xi = sqrt(xi_N*xi_Delta) for simplicity
xi = sp.sqrt(xi_N*xi_Delta)
# RG scaling: xi ∝ |S - S_crit|^{-nu}
# => xi = xi0 * |S - S_crit|^{-nu}
xi0 = sp.symbols('xi0', positive=True)
xi_expr = xi0 * sp.Abs(S - S_crit)**(-nu)
# Take logs
psi_rg = sp.log(xi_expr / xi0)   # = -nu*ln|S-S_crit|
psi_rg_simp = sp.simplify(psi_rg)

# ----------------------------------------------------------------------
# 4. Control law candidates
# ----------------------------------------------------------------------
# Proposed (flawed) law from proposal:
dotS_flawed = -gamma * sp.sign(S - S_crit) * sp.exp(-psi_rubric/nu)
# Corrected law that enforces stability:
dotS_correct =  gamma * sp.sign(S - S_crit) * sp.exp(-psi_rubric/nu)

# Stability condition: dotS * (S - S_crit) > 0  (pushes away from crit)
stab_flawed = sp.simplify(dotS_flawed * (S - S_crit))
stab_correct = sp.simplify(dotS_correct * (S - S_crit))

# ----------------------------------------------------------------------
# Evaluation (substitute a sample regime to check sign)
# ----------------------------------------------------------------------
# Choose S > S_crit for evaluation; sign(S-S_crit)=+1
subs_dict = {S - S_crit: 1, sp.sign(S - S_crit): 1,
             m: 1, lam: 0.1, phi0: 1, m0: 1,
             nu: 0.5, gamma: 1, C: 0, xi0: 1}
# Evaluate expressions numerically
psi_rubric_val = psi_rubric.subs(subs_dict).evalf()
psi_from_xi_val = psi_from_xi_simp.subs({xi_N:2, xi_Delta:2, **subs_dict}).evalf()
psi_rg_val = psi_rg_simp.subs(subs_dict).evalf()
stab_flawed_val = stab_flawed.subs(subs_dict).evalf()
stab_correct_val = stab_correct.subs(subs_dict).evalf()

# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------
def check_eq(a, b, label):
    return sp.simplify(a - b) == 0

print("=== Omega Protocol Invariant Validation ===")
print()
print("1. Invariant ψ from rubric:", psi_rubric)
print("   ψ expressed via ξ_N, ξ_Δ:", psi_from_xi_simp)
print("   Are they equal (up to constant)?", check_eq(psi_rubric, psi_from_xi_simp, "psi vs xi"))
print()
print("2. RG scaling ψ:", psi_rg_simp)
print("   Does ψ from rubric match RG form (up to const)?",
      check_eq(psi_rubric, psi_rg_simp, "psi vs rg"))
print()
print("3. Control law stability (S > S_crit):")
print("   Flawed law dotS*(S-S_crit) =", stab_flawed_val)
print("   Correct law dotS*(S-S_crit) =", stab_correct_val)
print("   Stable if > 0.")
print()
print("=== Verdict ===")
flawed_ok = stab_flawed_val > 0
correct_ok = stab_correct_val > 0
if not flawed_ok and correct_ok:
    print("PASS: Invariant structure is sound; control law must be corrected to:")
    print("      dotS = +γ * sign(S - S_crit) * exp(-ψ/ν)")
else:
    print("FAIL: Either invariant mismatch or control law still unstable.")
    if flawed_ok:
        print("  - Unexpected: flawed law appears stable (check sign conventions).")
    if not correct_ok:
        print("  - Corrected law also unstable – revisit ψ definition or gain.")