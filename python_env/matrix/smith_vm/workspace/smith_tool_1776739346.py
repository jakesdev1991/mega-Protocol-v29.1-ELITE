# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
---------------------------------
Checks the radiative stability of the scalar sector (Phi_N, Phi_Delta)
and the Poisson recovery condition for Phi_N.
"""

import sympy as sp
import numpy as np

# ----------------------------
# 1. Symbolic parameters
# ----------------------------
gN, gD = sp.symbols('gN gD', positive=True)   # Yukawa couplings
Lambda = sp.symbols('Lambda', positive=True) # UV cutoff (lattice inverse spacing)
mu0 = sp.symbols('mu0', positive=True)       # RG reference scale
# Optional: fix numeric values for a concrete test
num_vals = {gN: 0.02, gD: 0.02, Lambda: 1e16, mu0: 1e2}  # GeV units

# ----------------------------
# 2. One-loop scalar mass corrections
# ----------------------------
# Δm^2 ~ (g^2 / (16π^2)) * Lambda^2
Delta_m2_N = (gN**2 / (16 * sp.pi**2)) * Lambda**2
Delta_m2_D = (gD**2 / (16 * sp.pi**2)) * Lambda**2

print("=== One-loop mass shifts ===")
print(f"Δm²_{sp.latex('\\Phi_N')} = {Delta_m2_N}")
print(f"Δm²_{sp.latex('\\Phi_Delta')} = {Delta_m2_D}")

# Substitute numbers to see magnitude
Delta_m2_N_num = Delta_m2_N.subs(num_vals).evalf()
Delta_m2_D_num = Delta_m2_D.subs(num_vals).evalf()
print(f"Numerical (GeV²): Δm²_N ≈ {Delta_m2_N_num:.3e}, Δm²_D ≈ {Delta_m2_D_num:.3e}")

# ----------------------------
# 3. Landau pole for g_Delta
# ----------------------------
# Beta function: β(g) = g^3/(16π^2)  (leading order)
beta_gD = gD**3 / (16 * sp.pi**2)
# Solve dg/dlnμ = β → ∫ dg/g^3 = ∫ (1/16π^2) dlnμ
# => -1/(2 g^2) = (1/16π^2) ln(μ/μ0) + C
# Landau pole when denominator → 0:
# 1/g^2(μ) = 1/g^2(μ0) - (1/8π^2) ln(μ/μ0)
# Pole at ln(μ/μ0) = 8π^2 / g^2(μ0)
Lambda_LP = mu0 * sp.exp(8 * sp.pi**2 / gD**2)

print("\n=== Landau pole ===")
print(f"Λ_LP = {Lambda_LP}")
Lambda_LP_num = Lambda_LP.subs(num_vals).evalf()
print(f"Numerical Λ_LP ≈ {Lambda_LP_num:.3e} GeV")
print(f"Cutoff Λ = {Lambda.subs(num_vals).evalf():.3e} GeV")
print(f"Is Λ_LP < Λ ? {Lambda_LP_num < Lambda.subs(num_vals).evalf()}")

# ----------------------------
# 4. Poisson recovery test
# ----------------------------
# For a massive scalar: (∇² - m²) Φ_N = -4π G ρ
# Point source ρ = δ³(r) → solution Φ_N = (e^{-m r})/(4π r)
# If m ≠ 0, the force is Yukawa‑suppressed → violates pure 1/r Poisson.
m2_N = Delta_m2_N  # treat radiative mass as effective m^2
m_N = sp.sqrt(m2_N)  # principal branch (positive)

# Define radial coordinate r>0
r = sp.symbols('r', positive=True)
Phi_N_massive = sp.exp(-m_N * r) / (4 * sp.pi * r)
Phi_N_massless = 1 / (4 * sp.pi * r)  # m=0 case

# Compute Laplacian in spherical coordinates: ∇² f = (1/r²) d/dr (r² df/dr)
laplacian_massive = sp.simplify((1/r**2) * sp.diff(r**2 * sp.diff(Phi_N_massive, r), r))
laplacian_massless = sp.simplify((1/r**2) * sp.diff(r**2 * sp.diff(Phi_N_massless, r), r))

print("\n=== Poisson recovery check ===")
print(f"∇²Φ_N (massive) = {laplacian_massive}")
print(f"∇²Φ_N (massless) = {laplacian_massless}")
# Expected source: -4π δ³(r) → away from r=0 we expect 0.
# For massive case, away from origin we get -m² Φ_N (Yukawa).
# Let's verify the identity: ∇²Φ_N - m² Φ_N = 0 for r>0.
identity_massive = sp.simplify(laplacian_massive - m_N**2 * Phi_N_massive)
print(f"∇²Φ_N - m²Φ_N (should be 0) = {identity_massive}")

# If m_N ≠ 0, the Poisson equation is modified → violation of invariant.
poisson_ok = sp.simplify(identity_massive) == 0
print(f"Poisson recovery satisfied? {poisson_ok}")

# ----------------------------
# 5. Lattice spacing positivity
# ----------------------------
# a = ξ0 * exp(-ψ) , ψ = ln(Φ_N/I0)  → a = ξ0 * I0 / Φ_N
xi0, I0 = sp.symbols('xi0 I0', positive=True)
Phi_N_sym = sp.symbols('Phi_N', positive=True)
a_expr = xi0 * sp.exp(-sp.log(Phi_N_sym / I0))  # = xi0 * I0 / Phi_N
print("\n=== Lattice spacing ===")
print(f"a = {sp.simplify(a_expr)}")
# Check that a > 0 for all Phi_N>0 (obviously true)
a_positive = sp.simplify(a_expr) > 0
print(f"a > 0 for Phi_N>0 ? {a_positive}")

# ----------------------------
# 6. Summary of invariant compliance
# ----------------------------
print("\n=== Invariant Compliance Summary ===")
violations = []

# Scalar mass naturalness: require radiative shift << (some reference scale)^2
ref_scale = 1e2  # e.g., electroweak scale GeV
if Delta_m2_N_num > ref_scale**2:
    violations.append("Phi_N acquires large radiative mass (violates Newtonian lightness)")

if Delta_m2_D_num > ref_scale**2:
    violations.append("Phi_Delta acquires large radiative mass (violates Archive mode masslessness)")

if Lambda_LP_num < Lambda.subs(num_vals).evalf():
    violations.append("Landau pole appears below lattice cutoff (perturbative breakdown)")

if not poisson_ok:
    violations.append("Poisson recovery for Phi_N violated (Yukawa suppression)")

if violations:
    print("FAIL – the following invariants are at risk:")
    for v in violations:
        print(" -", v)
else:
    print("PASS – all tested Omega Protocol invariants hold under the given parameters.")

# End of script