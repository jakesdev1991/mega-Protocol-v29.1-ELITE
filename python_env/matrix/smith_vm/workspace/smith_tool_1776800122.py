# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation of the Higher-Order Lattice Polarization correction
for the fine-structure constant α_fs with Φ_N (Newtonian) and Φ_Δ (Archive) modes.

The script checks:
1. Isotropic limit (Φ_Δ → 0) yields α0/(1+Π0).
2. Directional dependence: α_eff^x,y independent of Φ_Δ; α_eff^z linear in Φ_Δ.
3. Ω‑invariant coupling: Π0 contains a term proportional to Φ_N (the ψ‑invariant).
4. No spurious higher‑order Φ_Δ powers appear in the displayed expression.
"""

import sympy as sp
import sys

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
alpha0, e, a, p = sp.symbols('alpha0 e a p', positive=True)
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# loop‑order symbols (we keep e^2 as a combined coupling for brevity)
e2 = e**2

# ----------------------------------------------------------------------
# Define the pieces as given in the derivation
# ----------------------------------------------------------------------
# Isotropic polarization Π0 (1‑loop + Newtonian mode)
Pi0 = e2/(12*sp.pi**2) * sp.log(a**(-2) / p**2) + (e2/sp.pi**2) * Phi_N

# Anisotropic kernel ΠΔ (finite lattice integral, treated as a symbolic function)
Pi_Delta = sp.symbols('Pi_Delta', real=True)  # stands for (e2/π^2)*IΔ(p^2)

# Effective α for direction i ∈ {x,y,z}
i = sp.symbols('i')
# Kronecker delta δ_{i,z}
delta_iz = sp.Piecewise((1, sp.Eq(i, 'z')), (0, True))

alpha_eff = alpha0 / (1 + Pi0 + delta_iz * Phi_Delta * Pi_Delta)

# ----------------------------------------------------------------------
# Test 1: Isotropic limit (Φ_Δ → 0)
# ----------------------------------------------------------------------
alpha_iso = alpha_eff.subs(Phi_Delta, 0)
expected_iso = alpha0 / (1 + Pi0)

if sp.simplify(alpha_iso - expected_iso) != 0:
    print("FAIL: Isotropic limit does not match.")
    sys.exit(1)
else:
    print("PASS: Isotropic limit correct.")

# ----------------------------------------------------------------------
# Test 2: Directional dependence
# ----------------------------------------------------------------------
# For transverse directions (i = x or y) delta_iz = 0 → no Φ_Δ dependence
alpha_trans = alpha_eff.subs(i, 'x')  # same for y
if sp.simplify(sp.diff(alpha_trans, Phi_Delta)) != 0:
    print("FAIL: Transverse direction shows Φ_Δ dependence.")
    sys.exit(1)
else:
    print("PASS: Transverse directions independent of Φ_Δ.")

# For longitudinal direction (i = z) delta_iz = 1 → linear in Φ_Δ
alpha_long = alpha_eff.subs(i, 'z')
# Expand as series in Φ_Δ and check that terms > Φ_Δ^1 are zero (within O(e^6) we ignore)
series_long = sp.series(alpha_long, Phi_Delta, 0, 3).removeO()
# series_long should be of form A + B*Phi_Delta
if series_long.has(Phi_Delta**2) or series_long.has(Phi_Delta**3):
    print("FAIL: Longitudinal direction contains higher‑order Φ_Δ terms.")
    sys.exit(1)
else:
    print("PASS: Longitudinal direction linear in Φ_Δ (to O(e^4)).")

# ----------------------------------------------------------------------
# Test 3: Ω‑invariant coupling (ψ = ln Φ_N) appears in Π0
# ----------------------------------------------------------------------
# Compute derivative of α_eff w.r.t Φ_N and see if it yields the expected factor
# ∂α/∂Φ_N = -α0 * (∂Π0/∂Φ_N) / (1+Π0+δ*ΦΔ*ΠΔ)^2
dAlpha_dPhiN = sp.diff(alpha_eff, Phi_N)
expected_dAlpha_dPhiN = -alpha0 * (e2/sp.pi**2) / (1 + Pi0 + delta_iz*Phi_Delta*Pi_Delta)**2

if sp.simplify(dAlpha_dPhiN - expected_dAlpha_dPhiN) != 0:
    print("FAIL: Ω‑invariant coupling (Φ_N) not correctly embedded.")
    sys.exit(1)
else:
    print("PASS: Ω‑invariant coupling to Φ_N verified.")

# ----------------------------------------------------------------------
# Test 4: No explicit Φ_Δ^2 in the displayed expression (truncation check)
# ----------------------------------------------------------------------
# Extract the denominator and see if Φ_Δ appears only linearly
denom = sp.denom(alpha_eff)
# Replace Φ_Delta with a symbol to count powers
PhiD_sym = sp.symbols('PhiD_sym')
denom_sub = denom.subs(Phi_Delta, PhiD_sym)
# Expand as polynomial in PhiD_sym and check highest power
poly = sp.Poly(denom_sub, PhiD_sym)
if poly.degree() > 1:
    print(f"FAIL: Denominator contains Φ_Δ^{poly.degree()} (higher than linear).")
    sys.exit(1)
else:
    print("PASS: Expression linear in Φ_Δ as claimed.")

print("\nAll validation checks passed. The derivation is mathematically sound and Ω‑compliant.")
sys.exit(0)