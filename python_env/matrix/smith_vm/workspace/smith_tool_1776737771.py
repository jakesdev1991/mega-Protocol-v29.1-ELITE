# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Audit of the "Higher-Order Lattice Polarization" derivation for α_fs.
We verify:
 1. The one-loop QED vacuum polarization (log term).
 2. The two-loop scalar‑exchange contribution (double‑log term).
 3. Consistency of the resulting β‑function with the derivative of α(q²).
 4. Dimensional consistency of the lattice term expressed via Ω‑invariants.
All calculations are done symbolically (sympy) and spot‑checked numerically.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbols (all dimensionless unless noted)
# ----------------------------------------------------------------------
e, m, q2, Lambda, gDelta, xi0, psi, C = sp.symbols(
    'e m q2 Lambda gDelta xi0 psi C', positive=True, real=True
)
pi = sp.pi
alpha0 = e**2 / (4*sp.pi)  # fine‑structure constant at low energy (ħ=c=1)

# ----------------------------------------------------------------------
# 1. One‑loop QED vacuum polarization (known result)
#    Pi_QED(q²) = - (α0/(3π)) * ln(-q²/m²)   for -q² >> m²
# ----------------------------------------------------------------------
Pi_QED = - alpha0/(3*pi) * sp.log(-q2/m**2)

# ----------------------------------------------------------------------
# 2. Two‑loop scalar‑exchange contribution (approximate double‑log)
#    ΔPi ≈ - (gΔ² e²)/(32 π⁴) * ln²(-q²/m²)
# ----------------------------------------------------------------------
DeltaPi = - (gDelta**2 * e**2) / (32 * pi**4) * sp.log(-q2/m**2)**2

# ----------------------------------------------------------------------
# 3. Total polarization and running α(q²)
#    α(q²) = α0 / (1 - Π_total)
# ----------------------------------------------------------------------
Pi_tot = Pi_QED + DeltaPi
alpha_q2 = alpha0 / (1 - Pi_tot)

# ----------------------------------------------------------------------
# 4. β‑function from definition:
#    β(α) = μ ∂α/∂μ = - α² * dΠ/d ln(-q²)   (with μ² = -q²)
# ----------------------------------------------------------------------
lnL = sp.log(-q2/m**2)  # = ln(μ²/m²)
dPi_dln = sp.diff(Pi_tot, lnL)
beta_from_Pi = - alpha_q2**2 * dPi_dln

# Simplify beta expression
beta_simplified = sp.simplify(beta_from_Pi)
# Expected beta from the derivation:
beta_expected = (2*alpha_q2**2)/(3*pi) + (alpha_q2 * gDelta**2)/(8*pi**3)

# ----------------------------------------------------------------------
# 5. Lattice term expressed via Ω‑invariants
#    a = xi0 * exp(-psi)   →   Λ = π/a = (π/xi0) * exp(psi)
#    Lattice correction: C * a² * q² = C * xi0⁻² * exp(2ψ) * q²
# ----------------------------------------------------------------------
a = xi0 * sp.exp(-psi)
LatticeTerm = C * a**2 * q2  # = C * xi0⁻² * exp(2ψ) * q²

# ----------------------------------------------------------------------
# 6. Numerical spot‑check (choose sample values)
# ----------------------------------------------------------------------
sample = {
    e: 0.302822123,          # ≈ sqrt(4π * 1/137)
    m: 0.511e-3,             # electron mass in GeV
    q2: -100.0,              # spacelike momentum squared (GeV²)
    Lambda: 10.0,            # UV cutoff (GeV)
    gDelta: 0.05,
    xi0: 1.0e-3,             # reference length (GeV⁻¹)
    psi: 0.2,
    C: 0.01
}

def sub_num(expr):
    return float(expr.subs(sample))

print("=== Numerical Spot‑Check ===")
print(f"α0 = {sub_num(alpha0):.6e}")
print(f"Π_QED = {sub_num(Pi_QED):.6e}")
print(f"ΔΠ (scalar) = {sub_num(DeltaPi):.6e}")
print(f"Π_total = {sub_num(Pi_tot):.6e}")
print(f"α(q²) = {sub_num(alpha_q2):.6e}")
print(f"β from Π = {sub_num(beta_simplified):.6e}")
print(f"β expected = {sub_num(beta_expected):.6e}")
print(f"Difference β = {sub_num(beta_simplified - beta_expected):.6e}")
print(f"Lattice term C a² q² = {sub_num(LatticeTerm):.6e}")

# ----------------------------------------------------------------------
# 7. Symbolic consistency checks
# ----------------------------------------------------------------------
print("\n=== Symbolic Consistency ===")
# Check that β from Π matches expected up to O(α², gΔ²)
beta_diff = sp.simplify(beta_simplified - beta_expected)
print(f"β difference (symbolic) = {beta_diff}")
# Ideally zero; if not, we inspect leading terms.
if beta_diff != 0:
    # Expand in small gDelta to see mismatch order
    beta_diff_series = sp.series(beta_diff, gDelta, 0, 3).removeO()
    print(f"β difference expanded in gΔ: {beta_diff_series}")

# Dimensional check: LatticeTerm should be dimensionless
# In natural units [q²] = mass², [xi0] = mass⁻¹ → xi0⁻² q² is dimensionless.
dim_check = sp.simplify(LatticeTerm / (C * xi0**(-2) * sp.exp(2*psi) * q2))
print(f"Lattice term dimensional consistency factor = {dim_check} (should be 1)")

# ----------------------------------------------------------------------
# 8. Verdict
# ----------------------------------------------------------------------
tolerance = 1e-4
beta_ok = abs(sub_num(beta_simplified - beta_expected)) < tolerance
dim_ok = abs(sub_num(dim_check - 1.0)) < tolerance

print("\n=== Audit Result ===")
print(f"β‑function match: {'PASS' if beta_ok else 'FAIL'}")
print(f"Lattice term dimensionality: {'PASS' if dim_ok else 'FAIL'}")
if beta_ok and dim_ok:
    print("Derivation is mathematically sound (within tested approximations) and respects Ω‑invariants.")
else:
    print("Derivation shows discrepancies; review the scalar‑exchange integral or lattice mapping.")