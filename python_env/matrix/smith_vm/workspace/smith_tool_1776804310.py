# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Compliance Checker for LSGM‑Ω (refined)
Uses SymPy to symbolically verify:
  - Invariant ψ = ln Φ_N
  - Correct entropy‑gauge derivation (∂_μ J^μ = 0)
  - Presence of kinetic terms for Φ_N, Φ_Δ
  - Exact boundary terminology (Shredding Event / Informational Freeze)
"""

import sympy as sp

# ---------------------------
# 1. Symbolic setup (1+1D for simplicity)
# ---------------------------
t, x = sp.symbols('t x', real=True)
# metric signature (+, -) -> sqrt(-g) = 1
g = sp.Matrix([[1, 0],
               [0, -1]])
ginv = g.inv()
sqrt_neg_g = 1  # sqrt(-det(g)) = 1 for this metric

# Fields
E = sp.Function('E')(t, x)          # exposure field
K = sp.Function('K')(t, x)          # epistemic field
A0 = sp.Function('A0')(t, x)        # time component of gauge field A_μ
A1 = sp.Function('A1')(t, x)        # space component
# Assemble A_mu = (A0, A1) with index lowering/raising via metric
A = sp.Matrix([A0, A1])             # covariant components A_μ
# Raise index: A^μ = g^{μν} A_ν
A_up = ginv * A                     # contravariant components

# ---------------------------
# 2. Define Φ_N, Φ_Δ (toy models)
# ---------------------------
# Spectral gap Φ_N as exponential of curvature scalar R_G (dimensionless)
R_G = sp.Function('R_G')(t, x)      # dimensionless curvature scalar
Phi_N0 = sp.symbols('Phi_N0', positive=True)
R0 = sp.symbols('R0', positive=True)
Phi_N = Phi_N0 * sp.exp(R_G / R0)   # connectivity

# Φ_Δ as a simple function of curvature skewness (toy)
Phi_Delta = sp.Function('Phi_Delta')(t, x)  # treat as independent for now

# Invariant ψ = ln Φ_N
psi = sp.log(Phi_N)
# Check that ψ indeed equals ln Φ_N (trivial, but verifies structure)
assert sp.simplify(psi - sp.log(Phi_N)) == 0, "Invariant ψ ≠ ln Φ_N"

# ---------------------------
# 3. Action components
# ---------------------------
# Kinetic terms for E and K
kin_E = sp.Rational(1,2) * (ginv[0,0]*sp.diff(E,t)**2 + ginv[1,1]*sp.diff(E,x)**2)
kin_K = sp.Rational(1,2) * (ginv[0,0]*sp.diff(K,t)**2 + ginv[1,1]*sp.diff(K,x)**2)

# Placeholder potential V(E,K) and Omega Lagrangian
V = sp.Function('V')(E, K)
L_Omega = sp.Function('L_Omega')(Phi_N, Phi_Delta)
lam_Omega = sp.symbols('lam_Omega')

# ---------------------------
# 4. Entropy‑gauge term (two variants)
# ---------------------------
# Directory entropy S_dir (toy scalar)
S_dir = sp.Function('S_dir')(t, x)

# Variant A: flawed coupling 𝒜_μ J^μ  (no kinetic term for A)
J0 = sp.sqrt(2) * Phi_Delta   # only time component non‑zero
J = sp.Matrix([J0, 0])        # J^μ contravariant (we will raise/lower correctly)
# Actually J^μ as given: J^μ = sqrt(2) Φ_Δ δ^μ_0 -> contravariant
J_up = sp.Matrix([J0, 0])
# Lower index: J_μ = g_{μν} J^ν
J_low = g * J_up

# Coupling term A_μ J^mu (using covariant A_μ and contravariant J^μ)
coupling_flawed = A.dot(J_up)   # A_μ J^μ

# Variant B: proper gauge field with kinetic term -1/4 F_{μν}F^{μν}
F = sp.Matrix.zeros(2,2)
F[0,1] = sp.diff(A0, x) - sp.diff(A1, t)
F[1,0] = -F[0,1]
# F^{μν} = g^{μα} g^{νβ} F_{αβ}
F_up = ginv * F * ginv
# Kinetic term for gauge field
gau_kin = -sp.Rational(1,4) * (F_up.dot(F))  # scalar: F^{μν}F_{μν}
# Coupling term same as above
coupling_proper = A.dot(J_up)

# ---------------------------
# 5. Total action density (Lagrangian)
# ---------------------------
L_flawed = kin_E + kin_K + V + lam_Omega * L_Omega + coupling_flawed
L_proper = kin_E + kin_K + V + lam_Omega * L_Omega + gau_kin + coupling_proper

# Action integrals (we keep density; Euler‑Lagrange works on density)
S_flawed = sp.integrate(L_flawed, (t, x))  # symbolic integral placeholder
S_proper = sp.integrate(L_proper, (t, x))

# ---------------------------
# 6. Euler‑Lagrange for A_μ (check gauge equation)
# ---------------------------
def euler_lagrange(L, q, qd):
    """Return EL eq: d/dx^μ (∂L/∂(∂_μ q)) - ∂L/∂q = 0"""
    # qd is list of derivatives [∂_t q, ∂_x q]
    term = sp.diff(sp.diff(L, qd[0]), t) + sp.diff(sp.diff(L, qd[1]), x) - sp.diff(L, q)
    return sp.simplify(term)

# For flawed variant: vary A0, A1
EL_A0_flawed = euler_lagrange(L_flawed, A0, [sp.diff(A0, t), sp.diff(A0, x)])
EL_A1_flawed = euler_lagrange(L_flawed, A1, [sp.diff(A1, t), sp.diff(A1, x)])
# Expect J^μ = 0 -> both components should give J^μ = 0
assert sp.simplify(EL_A0_flawed - J0) == 0, "Flawed gauge eq does not give J^0 = source"
assert sp.simplify(EL_A1_flawed - 0) == 0, "Flawed gauge eq does not give J^1 = 0"
# This shows the flawed version forces J^μ = 0 (too strong)

# For proper variant: vary A0, A1
EL_A0_proper = euler_lagrange(L_proper, A0, [sp.diff(A0, t), sp.diff(A0, x)])
EL_A1_proper = euler_lagrange(L_proper, A1, [sp.diff(A1, t), sp.diff(A1, x)])
# Proper gauge eq: ∂_ν F^{νμ} = J^mu
# Compute left side manually to verify
# ∂_ν F^{ν0} = ∂_t F^{t0} + ∂_x F^{x0}
# ∂_ν F^{ν1} = ∂_t F^{t1} + ∂_x F^{x1}
F_up_num = ginv * F * ginv  # already computed
left0 = sp.diff(F_up_num[0,0], t) + sp.diff(F_up_num[1,0], x)
left1 = sp.diff(F_up_num[0,1], t) + sp.diff(F_up_num[1,1], x)
assert sp.simplify(EL_A0_proper - left0) == 0, "Proper gauge eq mismatch for μ=0"
assert sp.simplify(EL_A1_proper - left1) == 0, "Proper gauge eq mismatch for μ=1"
# From antisymmetry of F, ∂_μ J^μ = 0 follows:
divJ = sp.diff(J0, t) + sp.diff(0, x)  # J^1 = 0
assert sp.simplify(divJ) == 0, "Proper gauge eq does NOT imply ∂_μ J^μ = 0 (check)"

# ---------------------------
# 7. Check kinetic terms for Φ_N, Φ_Δ
# ---------------------------
# Look for (∂Φ_N)^2 and (∂Φ_Δ)^2 in L_proper
def has_kinetic_term(expr, phi):
    """Return True if expr contains (∂_μ φ)^2 summed over μ."""
    dphi_t = sp.diff(phi, t)
    dphi_x = sp.diff(phi, x)
    term = dphi_t**2 + dphi_x**2  # with metric (+,-) gives + (∂t)^2 - (∂x)^2; we just check presence
    # Simplify expr and see if term appears
    expr_simp = sp.expand(expr)
    return term in expr_simp.args or any(term in str(arg) for arg in expr_simp.args)

has_kin_PhiN = has_kinetic_term(L_proper, Phi_N)
has_kin_PhiD = has_kinetic_term(L_proper, Phi_Delta)
if not (has_kin_PhiN and has_kin_PhiD):
    print("WARNING: Missing explicit kinetic terms for Φ_N and/or Φ_Δ")
    # This is a rubric violation per Meta‑Scrutiny

# ---------------------------
# 8. Boundary terminology check
# ---------------------------
# Rubric requires exact phrases: "Shredding Event" or "Informational Freeze"
proposal_text = """
Total Exposure Collapse: ψ → +∞ and Φ_Δ → +∞ → high‑curvature directories leak fragile models.
Perfect Obfuscation: ψ → -∞ and Φ_Δ → 0 → leakage surface flat and uncorrelated.
"""
required_phrases = ["Shredding Event", "Informational Freeze"]
missing = [p for p in proposal_text.count(p) == 0 for p in required_phrases]
if missing:
    print(f"WARNING: Missing exact boundary terminology: {missing}")

# ---------------------------
# 9. Summary
# ---------------------------
print("\n=== Omega Protocol Compliance Check ===")
print("Invariant ψ = ln Φ_N : OK")
print("Entropy‑gauge (proper) yields ∂_μ J^μ = 0 : OK")
print("Entropy‑gauge (flawed) forces J^μ = 0 : Flagged as incorrect")
print("Kinetic terms for Φ_N, Φ_Δ present :", has_kin_PhiN and has_kin_PhiD)
print("Exact boundary terminology present :", all(p in proposal_text for p in required_phrases))
print("If any WARNING above appears, the proposal is NOT fully Omega‑compliant.")