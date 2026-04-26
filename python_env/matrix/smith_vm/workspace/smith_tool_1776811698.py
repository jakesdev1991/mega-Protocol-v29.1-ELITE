# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the Registration Topology Shield (RTS-Ω) mathematics.
Requires: sympy
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Symbols
# ----------------------------------------------------------------------
# Spacetime/internal coordinates (x^0 = t, x^1, x^2, x^3)
x0, x1, x2, x3 = sp.symbols('x0 x1 x2 x3', real=True)
# Field C and its derivatives
C = sp.Function('C')(x0, x1, x2, x3)
dC = [sp.diff(C, coord) for coord in (x0, x1, x2, x3)]

# Parameters of the potential
alpha, beta, gamma = sp.symbols('alpha beta gamma', positive=True, real=True)
# Omega coupling
lam_Omega = sp.symbols('lam_Omega', real=True)
# Placeholder for Omega Lagrangian L_Omega(Phi_N, Phi_Delta)
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True, nonnegative=True)
L_Omega = sp.Function('L_Omega')(Phi_N, Phi_Delta)

# Metric: assume Minkowski for validation (signature + - - -)
# sqrt(-g) = 1
sqrt_neg_g = 1

# ----------------------------------------------------------------------
# 2. Action density Lagrangian
# ----------------------------------------------------------------------
# Kinetic term: (1/(2*l0^2)) * g^{mu nu} partial_mu C partial_nu C
l0 = sp.symbols('l0', positive=True)
g_inv = sp.diag(1, -1, -1, -1)  # Minkowski inverse metric
kinetic = (1/(2*l0**2)) * sum(g_inv[i,i] * dC[i]*dC[i] for i in range(4))

# Potential
U = (alpha/2)*C**2 + (beta/4)*C**4 - gamma*C

# Gauge term: -1/4 F_{mu nu} F^{mu nu} + A_mu J^mu
# For validation we treat F=0 (background) and keep only A_mu J^mu
# A_mu = ∂_mu S_reg, J^mu = sqrt(2)*l0^3*Phi_Delta * delta^mu_0
S_reg = sp.Function('S_reg')(x0, x1, x2, x3)   # placeholder
A = [sp.diff(S_reg, coord) for coord in (x0, x1, x2, x3)]
J = [sp.sqrt(2)*l0**3 * Phi_Delta if i==0 else 0 for i in range(4)]
gauge_term = sum(A[i]*J[i] for i in range(4))   # -1/4 F^2 omitted (set to 0)

# Full Lagrangian density
L = kinetic + U + lam_Omega*L_Omega + gauge_term

# ----------------------------------------------------------------------
# 3. Euler-Lagrange equation for C
# ----------------------------------------------------------------------
# d/dx^mu (∂L/∂(∂_mu C)) - ∂L/∂C = 0
EL_terms = []
for mu in range(4):
    dL_d_dC = sp.diff(L, dC[mu])
    d_dx = sp.diff(dL_d_dC, (x0, x1, x2, x3)[mu])
    EL_terms.append(d_dx)
EL = sum(EL_terms) - sp.diff(L, C)
# Simplify (assuming L_Omega does not depend on C)
EL_simplified = sp.simplify(EL)
print("Euler‑Lagrange equation for C:")
print(sp.simplify(EL_simplified))
print("\n---\n")

# ----------------------------------------------------------------------
# 4. Invariant ψ_reg = ln(Φ_N/Φ_N0)
# ----------------------------------------------------------------------
Phi_N0 = sp.symbols('Phi_N0', positive=True)
psi_reg = sp.log(Phi_N/Phi_N0)
print("Invariant ψ_reg =", psi_reg)
print("Dimensionless? ->", psi_reg.free_symbols)  # should be only Phi_N, Phi_N0
print("Baseline (Phi_N=Phi_N0) gives ψ_reg =", psi_reg.subs(Phi_N, Phi_N0))
print("\n---\n")

# ----------------------------------------------------------------------
# 5. Gauge term verification
# ----------------------------------------------------------------------
print("Gauge term A_mu J^mu =", gauge_term)
print("Expected: sqrt(2)*l0^3*Phi_Delta * ∂_0 S_reg")
print("Match? ->", sp.simplify(gauge_term - sp.sqrt(2)*l0**3*Phi_Delta*sp.diff(S_reg, x0)) == 0)
print("\n---\n")

# ----------------------------------------------------------------------
# 6. Double-well potential extrema & bistability condition
# ----------------------------------------------------------------------
dU_dC = sp.diff(U, C)
crit_points = sp.solve(dU_dC, C)
print("Critical points of U(C):", crit_points)
# Second derivative to classify
d2U_dC2 = sp.diff(U, C, 2)
for cp in crit_points:
    val = d2U_dC2.subs(C, cp)
    print(f"  C = {cp}: U'' = {val}")
# Bistability condition: discriminant of cubic alpha*C + beta*C**3 - gamma = 0
# i.e., 4*alpha**3 > 27*beta*gamma**2
cond = sp.simplify(4*alpha**3 - 27*beta**2*gamma**2)
print("\nBistability condition (4α³ - 27β²γ²) > 0 ?")
print("Expression:", cond)
print("Assuming α,β,γ>0, sign depends on parameters.\n")
print("---\n")

# ----------------------------------------------------------------------
# 7. Convexity of MPC‑Ω constraint penalties (quadratic approximation)
# ----------------------------------------------------------------------
# Constraints: psi_reg <= psi_thresh, Phi_N >= Phi_N_min, S_reg >= ln(4)
psi_thresh = sp.symbols('psi_thresh', real=True)
Phi_N_min = sp.symbols('Phi_N_min', positive=True)
S_min = sp.log(4)

# Penalty terms (positive part squared)
pen_psi = sp.Max(0, psi_reg - psi_thresh)**2
pen_Phi = sp.Max(0, Phi_N_min - Phi_N)**2
pen_S = sp.Max(0, S_min - S_reg)**2

# For convexity check we examine the Hessian of the *unclipped* quadratic
# (i.e., assume arguments positive so Max drops)
quad_psi = (psi_reg - psi_thresh)**2
quad_Phi = (Phi_N_min - Phi_N)**2
quad_S = (S_min - S_reg)**2

# Variables of interest: treat Phi_N, Phi_Delta, S_reg as independent
vars_mpc = [Phi_N, Phi_Delta, S_reg]
H_psi = sp.hessian(quad_psi, vars_mpc)
H_Phi = sp.hessian(quad_Phi, vars_mpc)
H_S   = sp.hessian(quad_S,   vars_mpc)

print("Hessian of (ψ_reg - ψ_thresh)²:")
print(H_psi)
print("\nHessian of (Φ_N^min - Φ_N)²:")
print(H_Phi)
print("\nHessian of (ln4 - S_reg)²:")
print(H_S)
# Check positive semidefiniteness (all principal minors >=0)
def is_psd(M):
    return all(M[:i,:i].det() >= 0 for i in range(1, M.shape[0]+1))
print("\nPSD checks:")
print("ψ term PSD?", is_psd(H_psi))
print("Φ term PSD?", is_psd(H_Phi))
print("S term PSD?", is_psd(H_S))
print("\n---\n")

print("Validation complete.")