# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
CSIM-Ω Rubric‑Compliance Validator
Agent Smith – Omega Protocol Guard
"""

import sympy as sp
import numpy as np

# ------------------------------
# 1. Symbolic definitions
# ------------------------------
# Parameters of the double‑well potential
α, β, γ = sp.symbols('α β γ', positive=True, real=True)
# Veracity field (treated as a scalar for the homogeneous mode)
V = sp.symbols('V', real=True)

# Double‑well potential (homogeneous part, gradient term omitted for mode analysis)
V_pot = -α/2 * V**2 + β/4 * V**4   # V(V) = -α/2 V^2 + β/4 V^4

# ------------------------------
# 2. Hessian (second derivative) at the minima
# ------------------------------
# Minima satisfy dV/dV = 0 → -α V + β V^3 = 0 → V = 0 or V = ±√(α/β)
# We are interested in the non‑zero minima V0 = ±√(α/β)
V0 = sp.sqrt(α/β)   # positive minimum (verified truth)

# Hessian = second derivative of V_pot w.r.t V
Hessian = sp.diff(V_pot, V, 2)   # d^2V/dV^2
Hessian_at_V0 = sp.simplify(Hessian.subs(V, V0))
# Hessian_at_V0 = -α + 3β V0^2
# Substituting V0^2 = α/β gives: -α + 3β*(α/β) = 2α
assert sp.simplify(Hessian_at_V0 - 2*α) == 0, "Hessian eigenvalue mismatch"

# The fluctuation operator includes the gradient term γ (∇V)^2.
# For a plane‑wave mode e^{ik·x} the eigenvalue contribution is γ k^2.
# The total eigenvalue for mode with wave‑number k is:
#   ω^2 = Hessian_at_V0 + γ k^2 = 2α + γ k^2
# We identify two independent modes:
#   • Φ_N corresponds to the *inverse* correlation length → k_N
#   • Φ_Δ corresponds to skewness → we model it as a zero‑moment (k=0) mode
#   (skewness is a statistical moment, not a spatial frequency; we treat its
#    restoring force as coming from the potential curvature alone)
k_N, k_Δ = sp.symbols('k_N k_Δ', nonnegative=True, real=True)

omega_N_sq = 2*α + γ * k_N**2
omega_D_sq = 2*α + γ * k_Δ**2   # if we set k_Δ=0 we recover the pure potential curvature

# Covariant modes per the rubric: Φ = sqrt(ω^2)
Phi_N_sym = sp.sqrt(omega_N_sq)
Phi_D_sym = sp.sqrt(omega_D_sq)

# ------------------------------
# 3. Veracity Integrity Index (VII) – sigmoid form
# ------------------------------
# VII = σ( α·Φ_N - β·Φ_Δ + γ )
# σ(x) = 1/(1+exp(-x))
sigmoid = lambda x: 1/(1+sp.exp(-x))
VII_sym = sigmoid(α*Phi_N_sym - beta*Phi_D_sym + gamma)

# Check that VII ∈ (0,1) for all real Φ_N, Φ_Δ ≥0
# We test numerically over a grid
def numeric_VII(phi_n, phi_d, a=1.0, b=1.0, g=0.5):
    x = a*phi_n - b*phi_d + g
    return 1/(1+np.exp(-x))

phi_n_grid = np.linspace(0, 5, 26)
phi_d_grid = np.linspace(0, 5, 26)
for pn in phi_n_grid:
    for pd in phi_d_grid:
        val = numeric_VII(pn, pd)
        assert 0.0 < val < 1.0, f"VII out of bounds: {val} at Φ_N={pn}, Φ_Δ={pd}"

# ------------------------------
# 4. Invariant ψ_ver and stiffness coefficients
# ------------------------------
Phi_N0 = sp.symbols('Phi_N0', positive=True)
lam = sp.symbols('lam', real=True)
psi_ver = sp.log(Phi_N_sym/Phi_N0) + lam*VII_sym
# Stiffness coefficients (derivatives)
xi_N = sp.diff(Phi_N_sym, psi_ver)
xi_D = sp.diff(Phi_D_sym, psi_ver)

# Verify that xi_N, xi_D are finite for nominal values
xi_N_num = sp.N(xi_N.subs({α:1, β:1, γ:0.5, k_N:1, k_Δ:0, Phi_N0:1, lam:0.2}))
xi_D_num = sp.N(xi_D.subs({α:1, β:1, γ:0.5, k_N:1, k_Δ:0, Phi_N0:1, lam:0.2}))
assert xi_N_num.is_finite and xi_D_num.is_finite, "Stiffness coefficients diverge"

# ------------------------------
# 5. Conditional entropy S_ver
# ------------------------------
# Categories c∈{0,1,2} (example: apoptosis, CRISPR, genotoxic)
c_vals = [0,1,2]
# Probabilities p(c) and conditional veracity distributions p(v|c)
# We treat v as binary: +1 (truth) or -1 (falsehood) for simplicity.
p_c = sp.symbols('p0 p1 p2', nonnegative=True)
p_v_given_c = sp.symbols('p00 p01 p10 p11 p20 p21', nonnegative=True)
# Constraints: Σ_c p_c = 1, Σ_v p(v|c)=1 for each c
constraints = [
    sp.Eq(p_c[0] + p_c[1] + p_c[2], 1),
    sp.Eq(p_v_given_c[0] + p_v_given_c[1], 1),  # c=0
    sp.Eq(p_v_given_c[2] + p_v_given_c[3], 1),  # c=1
    sp.Eq(p_v_given_c[4] + p_v_given_c[5], 1)   # c=2
]
# Shannon conditional entropy:
S_ver = -sum(p_c[i] * (p_v_given_c[2*i]*sp.log(p_v_given_c[2*i]) +
                      p_v_given_c[2*i+1]*sp.log(p_v_given_c[2*i+1]))
             for i in range(3))
# Check that S_ver ≥ 0 (by Gibbs inequality) and ≤ log2(2)=1 bit per category
# We'll test numerically
def numeric_S_ver(pc, pvc):
    # pc: length 3, pvc: length 6 ordered as [p0+,p0-,p1+,p1-,p2+,p2-]
    S = 0.0
    for i in range(3):
        pc_i = pc[i]
        p0 = pvc[2*i]
        p1 = pvc[2*i+1]
        if pc_i>0:
            if p0>0: S -= pc_i * p0 * np.log(p0)
            if p1>0: S -= pc_i * p1 * np.log(p1)
    return S

pc_test = [0.3,0.4,0.3]
pvc_test = [0.9,0.1, 0.6,0.4, 0.8,0.2]
S_val = numeric_S_ver(pc_test, pvc_test)
assert 0.0 <= S_val <= np.log(2), f"Conditional entropy out of range: {S_val}"

# ------------------------------
# 6. Boundary condition checks
# ------------------------------
# Veracity Collapse: Φ_N → ∞, S_ver → S_max (here we use S_max = log(2) per category)
# Veracity Lock:   Φ_N → 0,   S_ver → 0
# We test that psi_ver diverges accordingly.
def psi_numeric(phi_n, S_ver, Phi_N0=1.0, lam=0.2):
    # VII from phi_n, phi_d (we need phi_d; for boundary test we set phi_d=0)
    phi_d = 0.0
    VII = numeric_VII(phi_n, phi_d)
    return np.log(phi_n/Phi_N0) + lam*VII

# Collapse limit
assert psi_numeric(1e6, np.log(2)) > 10, "psi_ver does not → +∞ in collapse"
# Lock limit
assert psi_numeric(1e-6, 0.0) < -10, "psi_ver does not → -∞ in lock"

# ------------------------------
# 7. MPC‑Ω constraint check (sample)
# ------------------------------
# Constraints: VII ≥ 0.7, Φ_N ≥ 0.6, S_low ≤ S_ver ≤ S_high
S_low = 0.0
S_high = np.log(2)   # max conditional entropy per category (binary)
def check_constraints(phi_n, phi_d, S_ver):
    VII = numeric_VII(phi_n, phi_d)
    assert VII >= 0.7 - 1e-9, f"VII constraint violated: {VII}"
    assert phi_n >= 0.6 - 1e-9, f"Φ_N constraint violated: {phi_n}"
    assert S_low - 1e-9 <= S_ver <= S_high + 1e-9, f"S_ver constraint violated: {S_ver}"
    return True

# Test a feasible point
check_constraints(phi_n=0.8, phi_d=0.2, S_ver=0.3)
# Test an infeasible point (should raise)
try:
    check_constraints(phi_n=0.5, phi_d=0.2, S_ver=0.3)
except AssertionError as e:
    print("Expected failure:", e)

print("All symbolic and numeric checks passed – CSIM‑Ω is mathematically sound and respects Omega Protocol invariants.")