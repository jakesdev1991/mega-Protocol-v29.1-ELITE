# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the refined BRS-Omega proposal.
Checks dimensional consistency and basic Omega‑Protocol invariants.
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Symbolic definitions with dimensions
# ----------------------------------------------------------------------
# Base dimensions: [M] mass, [L] length, [T] time, [I] information (dimensionless)
# We treat information-theoretic quantities as dimensionless.
# Time dimension: T
T = sp.symbols('T', positive=True)   # time dimension

# Dimensionless counts / fractions
t, m, delta = sp.symbols('t m delta', nonnegative=True, integer=False)  # t: corrupt workers, m: total workers
s, s_min, s_max = sp.symbols('s s_min s_max', nonnegative=True)        # sparsity fraction
ell, ell_max = sp.symbols('ell ell_max', positive=True)                # latency, max allowed latency
# Noise and latency induced error are made dimensionless by normalisation:
eta = sp.symbols('eta', nonnegative=True)   # residual corruption noise (dimensionless)
zeta = sp.symbols('zeta', nonnegative=True) # latency‑induced error (dimensionless)

# Coefficients (dimensionless)
alpha1, alpha2, beta1, beta2 = sp.symbols('alpha1 alpha2 beta1 beta2', positive=True)
Phi_N0, Phi_Delta0 = sp.symbols('Phi_N0 Phi_Delta0', real=True)

# ----------------------------------------------------------------------
# 2. Expressions for the covariant modes (streaming)
# ----------------------------------------------------------------------
Phi_N_stream = Phi_N0 - alpha1*eta - alpha2*zeta
Phi_Delta_stream = Phi_Delta0 + beta1*eta - beta2*zeta

print("Phi_N_stream expression:", Phi_N_stream)
print("Phi_Delta_stream expression:", Phi_Delta_stream)

# ----------------------------------------------------------------------
# 3. Dimensionality check
# ----------------------------------------------------------------------
# Define a dimension function: returns the exponent of T in a sympy expression
def time_dimension(expr):
    # Replace every symbol with its T exponent; dimensionless symbols -> 0
    subs_dict = {
        t: 0, m: 0, delta: 0,
        s: 0, s_min: 0, s_max: 0,
        ell: 1, ell_max: 1,   # latency has dimension T
        eta: 0, zeta: 0,      # already normalised -> dimensionless
        alpha1:0, alpha2:0, beta1:0, beta2:0,
        Phi_N0:0, Phi_Delta0:0
    }
    dim_expr = expr.subs(subs_dict)
    # If the result is a number, its dimension is 0 (dimensionless)
    return sp.simplify(dim_expr)

print("\nTime dimension of Phi_N_stream :", time_dimension(Phi_N_stream))
print("Time dimension of Phi_Delta_stream :", time_dimension(Phi_Delta_stream))

# Both should be 0 → dimensionless
assert time_dimension(Phi_N_stream) == 0, "Phi_N_stream not dimensionless!"
assert time_dimension(Phi_Delta_stream) == 0, "Phi_Delta_stream not dimensionless!"

# ----------------------------------------------------------------------
# 4. Entropy‑based threat level
# ----------------------------------------------------------------------
# Gradient magnitudes g_i are assumed dimensionless after normalisation.
# Shannon entropy: H = - sum p_i log p_i, p_i dimensionless → H dimensionless.
p = sp.symbols('p0:%d' % 5)   # example with 5 workers; keep generic
H = -sp.Sum(p[i]*sp.log(p[i]), (i, 0, len(p)-1)).doit()
H_max = sp.log(len(p))        # max entropy when uniform
theta = 1 - H/H_max

print("\nEntropy H:", H)
print("Max entropy H_max:", H_max)
print("Threat level theta:", theta)

# Check dimensionless
def is_dimensionless(expr):
    return time_dimension(expr) == 0

assert is_dimensionless(theta), "Theta not dimensionless!"

# ----------------------------------------------------------------------
# 5. Cost function J (dimensionless)
# ----------------------------------------------------------------------
lam1, lam2 = sp.symbols('lam1 lam2', positive=True)
# Assume sum over tau replaced by a generic term; each term must be dimensionless.
J_term = (1 - Phi_N_stream)**2 + Phi_Delta_stream**2 + lam1*(theta - t/m)**2 + lam2*(ell/ell_max)**2
print("\nCost function term J_term:", J_term)
assert is_dimensionless(J_term), "Cost function term not dimensionless!"

# ----------------------------------------------------------------------
# 6. Boundary conditions (Shredding Event / Informational Freeze)
# ----------------------------------------------------------------------
# Define characteristic invariants xi_N, xi_Delta with dimension T
xi_N, xi_Delta = sp.symbols('xi_N xi_Delta', positive=True)
# Their inverses squared are modelled as linear functions (dimension 1/T^2)
lam = sp.symbols('lam', positive=True)   # coupling constant with dimension 1/T^2
gamma0, gamma1, gamma2 = sp.symbols('gamma0 gamma1 gamma2', real=True)
delta0, delta1, delta2 = sp.symbols('delta0 delta1 delta2', real=True)

xi_N_inv2 = lam*(gamma0 + gamma1*t + gamma2*ell/ell_max)   # note ell/ell_max dimensionless
xi_Delta_inv2 = lam*(delta0 - delta1*t + delta2*ell/ell_max)

print("\nxi_N^-2:", xi_N_inv2)
print("xi_Delta^-2:", xi_Delta_inv2)

# Dimensions: lam has 1/T^2, bracket dimensionless → overall 1/T^2 → correct for 1/xi^2
assert time_dimension(xi_N_inv2) == -2, "xi_N^-2 wrong dimension"
assert time_dimension(xi_Delta_inv2) == -2, "xi_Delta^-2 wrong dimension"

# Shredding Event: xi_Delta -> ∞  <=> xi_Delta^-2 <= 0
shredding_cond = xi_Delta_inv2 <= 0
print("\nShredding Event condition (xi_Delta^-2 <= 0):", shredding_cond)

# Informational Freeze: xi_N -> ∞  <=> xi_N^-2 <= 0
freeze_cond = xi_N_inv2 <= 0
print("Informational Freeze condition (xi_N^-2 <= 0):", freeze_cond)

# ----------------------------------------------------------------------
# 7. (Optional) Numeric MPC-Omega QP solve & KKT check
# ----------------------------------------------------------------------
import numpy as np
import cvxopt   # pip install cvxopt

def solve_mpc_omega(num_workers=5, t_max=None):
    if t_max is None:
        t_max = (num_workers-1)//2
    # Parameters (chosen arbitrarily for demo)
    ell0 = 0.2   # ms
    alpha = 0.5
    beta = 0.3
    ell_max_val = 1.0   # ms
    # Decision variables: t (continuous relaxation), s
    # Build QP: minimize 0.5*x^T P x + q^T x  s.t. Gx <= h, Ax = b
    # x = [t, s]
    P = 2*np.array([[1.0, 0.0],
                    [0.0, 1.0]])   # identity weighting
    q = np.zeros(2)
    # Inequality constraints:
    # 1) ell(t,s) <= ell_max  -> ell0 + alpha*t/m - beta*s <= ell_max
    G1 = np.array([alpha/num_workers, -beta])
    h1 = ell_max_val - ell0
    # 2) 0 <= t <= t_max
    G2 = np.array([1.0, 0.0])
    h2 = float(t_max)
    G3 = np.array([-1.0, 0.0])
    h3 = 0.0
    # 3) s_min <= s <= s_max
    s_min_val, s_max_val = 0.1, 0.9
    G4 = np.array([0.0, 1.0])
    h4 = s_max_val
    G5 = np.array([0.0, -1.0])
    h5 = -s_min_val
    # 4) Phi_N >= 0.6, Phi_Delta <= 0.7 (linearised)
    # Using nominal values: Phi_N0=0.8, Phi_Delta0=0.4, alpha1=alpha2=beta1=beta2=0.1
    Phi_N0_val, Phi_Delta0_val = 0.8, 0.4
    a1=a2=b1=b2=0.1
    # Phi_N = Phi_N0 - a1*eta - a2*zeta ; we treat eta,zeta as functions of t,s:
    # eta = t/m (worst case), zeta = ell/ell_max (latency induced)
    # => Phi_N >= 0.6  -> -a1*t/m - a2*(ell0+alpha*t/m - beta*s)/ell_max <= 0.6 - Phi_N0
    G6 = np.array([-a1/num_workers - a2*alpha/(num_workers*ell_max_val),
                   a2*beta/ell_max_val])
    h6 = 0.6 - Phi_N0_val + a2*ell0/ell_max_val
    # Phi_Delta <= 0.7  -> b1*t/m + b2*(ell0+alpha*t/m - beta*s)/ell_max <= 0.7 - Phi_Delta0
    G7 = np.array([ b1/num_workers + b2*alpha/(num_workers*ell_max_val),
                   -b2*beta/ell_max_val])
    h7 = 0.7 - Phi_Delta0_val - b2*ell0/ell_max_val

    G = np.vstack([G1, G2, G3, G4, G5, G6, G7])
    h = np.hstack([h1, h2, h3, h4, h5, h6, h7])

    # Solve QP
    from cvxopt import matrix, solvers
    solvers.options['show_progress'] = False
    P_cvx = matrix(P)
    q_cvx = matrix(q)
    G_cvx = matrix(G)
    h_cvx = matrix(h)
    sol = solvers.qp(P_cvx, q_cvx, G_cvx, h_cvx)
    t_opt, s_opt = sol['x']
    print("\nMPC-Omega solution: t = {:.3f}, s = {:.3f}".format(t_opt, s_opt))
    # Check constraints
    ell_val = ell0 + alpha*t_opt/num_workers - beta*s_opt
    print("Resulting latency ell = {:.3f} ms (limit {:.3f})".format(ell_val, ell_max_val))
    assert ell_val <= ell_max_val + 1e-6, "Latency constraint violated"
    assert 0 <= t_opt <= t_max + 1e-6, "t out of bounds"
    assert s_min_val <= s_opt <= s_max_val + 1e-6, "s out of bounds"
    # KKT residual (primal feasibility already checked)
    # Dual variables:
    lam = sol['z']
    # Stationarity: P*x + q + G^T * lam = 0
    stationarity = np.dot(P, np.array([t_opt, s_opt])) + q + np.dot(G.T, lam)
    print("KKT stationarity residual norm:", np.linalg.norm(stationarity))
    assert np.linalg.norm(stationarity) < 1e-4, "KKT stationarity not satisfied"
    return t_opt, s_opt

# Run a quick numeric check
try:
    solve_mpc_omega()
    print("\nNumeric MPC-Omega QP solved successfully and KKT conditions satisfied.")
except Exception as e:
    print("\nNumeric check failed:", e)

print("\nAll symbolic dimensional checks passed.")