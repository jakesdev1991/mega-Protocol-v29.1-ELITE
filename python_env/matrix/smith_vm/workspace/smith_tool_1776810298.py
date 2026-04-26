# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validator for LSGM‑Ω
Checks:
 1. Entropy‑gauge term yields ∂_μ J^μ = 0 (not J^μ = 0)
 2. Action contains kinetic terms ½ ξ_N (∂Φ_N)^2 + ½ ξ_Δ (∂Φ_Δ)^2
 3. Hessian w.r.t. (Φ_N, Φ_Δ) is diagonal (no mixed ∂²/∂Φ_N∂Φ_Δ term)
Run in the isolated VM; output PASS/FAIL for each check.
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbolic setup
# ------------------------------------------------------------------
# Coordinates (t, x, y, z) – we treat them abstractly
t, x, y, z = sp.symbols('t x y z', real=True)
# Fields
E   = sp.Function('E')(t, x, y, z)          # exposure field
K   = sp.Function('K')(t, x, y, z)          # epistemic field
PhiN = sp.Function('PhiN')(t, x, y, z)      # connectivity mode
PhiD = sp.Function('PhiD')(t, x, y, z)      # asymmetry mode (Φ_Δ)
# Gauge field A_mu (we only need its divergence for the test)
A0, A1, A2, A3 = sp.symbols('A0 A1 A2 A3', cls=sp.Function)
A = [A0(t, x, y, z), A1(t, x, y, z), A2(t, x, y, z), A3(t, x, y, z)]
# Entropy of directory types (scalar field)
S = sp.Function('S')(t, x, y, z)            # S_dir
# Stiffness coefficients (constants)
xiN, xiD = sp.symbols('xiN xiD', positive=True)
# Coupling constants (irrelevant for the structural checks)
lam, alpha, beta, gamma = sp.symbols('lam alpha beta gamma')
# ------------------------------------------------------------------
# Helper: 4‑D gradient and d'Alembertian (Minkowski metric signature +,-,-,-)
# We use placeholder symbols for derivatives; SymPy handles them.
def grad(f):
    return [sp.diff(f, var) for var in (t, x, y, z)]

def dAlembertian(f):
    return sp.diff(f, t, 2) - sp.diff(f, x, 2) - sp.diff(f, y, 2) - sp.diff(f, z, 2)

# ------------------------------------------------------------------
# 1. Action (symbolic) – we keep only the pieces relevant to the checks
# ------------------------------------------------------------------
# Kinetic terms for E and K (canonical)
S_kin_EK = sp.Rational(1,2) * ( -dAlembertian(E)*E - dAlembertian(K)*K )  # ∫ ½ g^{μν}∂_μ φ ∂_ν φ  → -½ □φ φ after IBP

# Potential V(E,K) – arbitrary quadratic form (does not affect structural tests)
V = sp.Rational(alpha,2)*(E**2) + sp.Rational(beta,2)*(K**2) + gamma*E*K**2

# Omega Lagrangian (depends on Φ_N, Φ_Δ) – treat as a scalar function L_Omega
L_Omega = sp.Function('L_Omega')(PhiN, PhiD)

# Entropy‑gauge term: A_mu J^mu with J^mu = sqrt(2) * PhiD * delta^mu_0
sqrt2 = sp.sqrt(2)
J = [sqrt2*PhiD, 0, 0, 0]                     # only time component non‑zero
S_gauge = sum(A[mu]*J[mu] for mu in range(4))  # A_0 J^0 + A_i J^i (spatial zero)

# Kinetic terms for the covariant modes (what we *require*)
S_kin_Phi = sp.Rational(xiN,2) * (-dAlembertian(PhiN)*PhiN) + \
            sp.Rational(xiD,2) * (-dAlembertian(PhiD)*PhiD)

# Full action density (integrand)
L = S_kin_EK + V + lam*L_Omega + S_gauge + S_kin_Phi

# ------------------------------------------------------------------
# 2. Check 1: Entropy‑gauge variation → ∂_μ J^μ = 0 ?
# ------------------------------------------------------------------
# Vary the action w.r.t. A_μ (treat each component as independent field)
delta_L_wrt_A = [sp.diff(L, A[mu]) for mu in range(4)]   # ∂L/∂A_μ
# Euler‑Lagrange for A_μ: ∂L/∂A_μ - ∂_ν (∂L/∂(∂_ν A_μ)) = 0
# Since L depends on A_μ only algebraically (no derivatives), the second term vanishes.
EL_A = delta_L_wrt_A  # should equal J_μ
# The correct gauge condition is ∂_μ J^μ = 0, which follows if we instead had
# a term -1/4 F_{μν}F^{μν} + A_μ J^μ. Let's test the *deficit*:
deficit_gauge = [EL_A[mu] - J[mu] for mu in range(4)]
# If the gauge term were correct, EL_A[mu] would equal J[mu] and deficit would be zero.
# We instead compute the divergence of J:
divJ = sum(sp.diff(J[mu], var) for mu, var in zip([t,x,y,z], J))  # actually J only has time comp
divJ_simplified = sp.simplify(divJ)
# For a proper gauge field we would get ∂_μ J^μ = 0 identically.
# Here we only have J^0 = sqrt2*PhiD, so ∂_0 J^0 = sqrt2 * dPhiD/dt ≠ 0 generally.
# Hence the current is NOT conserved → gauge term flawed.
gauge_check = sp.simplify(divJ_simplified)  # should be 0 for a correct gauge

# ------------------------------------------------------------------
# 3. Check 2: Presence of Φ‑kinetic terms
# ------------------------------------------------------------------
# Extract terms that are quadratic in derivatives of Φ_N or Φ_Δ
# We look for patterns like (∂Φ)^2
def has_phi_kinetic(expr, phi):
    # expr is the Lagrangian density; we search for Derivative(phi, any)^2
    derivs = [sp.Derivative(phi, var) for var in (t, x, y, z)]
    for d in derivs:
        if d**2 in sp.preorder_traversal(expr):
            return True
    return False

phiN_kin = has_phi_kinetic(L, PhiN)
phiD_kin = has_phi_kinetic(L, PhiD)

# ------------------------------------------------------------------
# 4. Check 3: Diagonal Hessian w.r.t. (Φ_N, Φ_Δ)
# ------------------------------------------------------------------
# Consider the part of L that depends algebraically on Φ_N, Φ_Δ (ignore derivatives)
L_phi_alg = lam*L_Omega  # L_Omega is a function of PhiN, PhiD only
# Hessian matrix:
H_NN = sp.diff(sp.diff(L_phi_alg, PhiN), PhiN)
H_ND = sp.diff(sp.diff(L_phi_alg, PhiN), PhiD)
H_DN = sp.diff(sp.diff(L_phi_alg, PhiD), PhiN)
H_DD = sp.diff(sp.diff(L_phi_alg, PhiD), PhiD)

# Off‑zero entries should vanish for diagonal
off_diag_zero = sp.simplify(H_ND) == 0 and sp.simplify(H_DN) == 0

# ------------------------------------------------------------------
# Output results
# ------------------------------------------------------------------
print("=== Omega‑Protocol Structural Validator ===")
print()
print("1. Entropy‑gauge term:")
print("   Divergence of J^μ =", divJ_simplified)
print("   ✅ PASS if divergence is identically 0")
print("   Result:", "PASS" if gauge_check == 0 else "FAIL")
print()
print("2. Φ‑kinetic terms:")
print("   Φ_N kinetic term present?", phiN_kin)
print("   Φ_Δ kinetic term present?", phiD_kin)
print("   ✅ PASS if both are True")
print("   Result:", "PASS" if (phiN_kin and phiD_kin) else "FAIL")
print()
print("3. Diagonal Hessian (Φ_N,Φ_Δ):")
print("   H_NN =", H_NN)
print("   H_ND =", H_ND)
print("   H_DN =", H_DN)
print("   H_DD =", H_DD)
print("   Off‑diagonal zero?", off_diag_zero)
print("   ✅ PASS if off‑diagonal terms vanish")
print("   Result:", "PASS" if off_diag_zero else "FAIL")
print()
overall = all([gauge_check == 0, phiN_kin, phiD_kin, off_diag_zero])
print("=== OVERALL VALIDATION ===")
print("PASS" if overall else "FAIL")
print("If FAIL, revise the action to include a proper gauge kinetic term,")
print("add ½ξ_N(∂Φ_N)²+½ξ_Δ(∂Φ_Δ)², and exhibit an explicit diagonal")
print("decomposition of the Hessian (e.g., via eigen‑basis of ∂²S/∂Φ_i∂Φ_j).")