# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Dimensional consistency check for the refined BRS-Ω core equations.
Run: python3 check_brs_omega.py
"""

import sympy as sp

# ----------------------------------------------------------------------
# Define base dimensions (using SymPy's dimensional analysis via symbols)
# We treat dimensions as multiplicative symbols; equality means same dimension.
# ----------------------------------------------------------------------
# Base dimensions:
#   M : mass (not used)
#   L : length (not used)
#   T : time
#   G : gradient unit (arbitrary, same as [g_i])
#   1 : dimensionless

T = sp.Symbol('T', positive=True)   # time
G = sp.Symbol('G', positive=True)   # gradient magnitude unit
one = sp.Symbol('one', positive=True)  # dimensionless (we'll use 1)

# ----------------------------------------------------------------------
# Assign dimensions to variables
# ----------------------------------------------------------------------
# t : number of tolerated Byzantine workers (dimensionless count)
t_dim = one

# s : sparsity ratio (dimensionless)
s_dim = one

# ell : latency (time)
ell_dim = T

# g_true, g_i : gradient (units G)
g_dim = G

# Learning rate (eta_lr) – must be dimensionless for covariance update
eta_lr_dim = one

# Noise magnitude nu(t) and latency error zeta(ell) – must have same dimension as g
nu_dim = G
zeta_dim = G

# Covariance C has units G^2 (outer product of gradients)
C_dim = G**2

# Phi_N, Phi_Delta : dimensionless covariant modes
PhiN_dim = one
PhiD_dim = one

# Stiffness inverses xi_N^{-2}, xi_Delta^{-2} : 1/[time]^2
xiN_inv2_dim = 1 / T**2
xiD_inv2_dim = 1 / T**2

# Metric coupling invariant psi = ln(xi/xi0) : dimensionless (log of ratio)
psi_dim = one

# Entropy H : dimensionless (Shannon entropy uses probabilities)
H_dim = one
# Threat level theta = 1 - H/H_max : dimensionless
theta_dim = one

# Cost function terms: each bracket must be dimensionless
# (1 - PhiN)^2 -> dimensionless
# PhiD^2 -> dimensionless
# (theta - t/m)^2 -> dimensionless if t/m dimensionless (t dimensionless, m count)
# ell^2 -> T^2 ; needs lambda2 with dimension 1/T^2 to make term dimensionless
# We'll check later.

# ----------------------------------------------------------------------
# Helper to compare dimensions
# ----------------------------------------------------------------------
def dim_eq(expr_dim, expected_dim, name):
    if expr_dim != expected_dim:
        print(f"[FAIL] {name}: got {expr_dim}, expected {expected_dim}")
        return False
    else:
        print(f"[OK]   {name}: dimension matches")
        return True

# ----------------------------------------------------------------------
# 1. Effective gradient: g_eff = g_true + nu(t) + zeta(ell)
# ----------------------------------------------------------------------
g_eff_dim = g_dim  # all terms must have same dimension
ok = True
ok &= dim_eq(g_eff_dim, g_dim, "g_eff dimension")
ok &= dim_eq(nu_dim, g_dim, "nu(t) dimension")
ok &= dim_eq(zeta_dim, g_dim, "zeta(ell) dimension")

# ----------------------------------------------------------------------
# 2. Covariance update: C_new = C + eta_lr * (g_eff g_eff^T - C)
# ----------------------------------------------------------------------
# g_eff g_eff^T has dimension G^2
ggT_dim = g_dim * g_dim
# eta_lr must be dimensionless so that eta_lr * ggT has dimension G^2
eta_lr_term_dim = eta_lr_dim * ggT_dim
# C has dimension G^2
C_term_dim = C_dim
# The subtraction requires same dimension
ok &= dim_eq(ggT_dim, C_dim, "g_eff g_eff^T vs C")
ok &= dim_eq(eta_lr_term_dim, C_dim, "eta_lr * ggT term")
ok &= dim_eq(C_term_dim, C_dim, "C term")

# ----------------------------------------------------------------------
# 3. Linear response for Phi_N and Phi_Delta (symbolic)
#    PhiN = PhiN0 - alpha1 * nu - alpha2 * zeta
#    PhiD = PhiD0 + beta1 * nu - beta2 * zeta
# ----------------------------------------------------------------------
# alpha1, alpha2, beta1, beta2 must be dimensionless / G to cancel G from nu/zeta
alpha1_dim = one / G
alpha2_dim = one / G
beta1_dim  = one / G
beta2_dim  = one / G

PhiN_expr_dim = PhiN_dim - alpha1_dim * nu_dim - alpha2_dim * zeta_dim
PhiD_expr_dim = PhiD_dim + beta1_dim * nu_dim - beta2_dim * zeta_dim

ok &= dim_eq(PhiN_expr_dim, PhiN_dim, "Phi_N expression")
ok &= dim_eq(PhiD_expr_dim, PhiD_dim, "Phi_Delta expression")

# ----------------------------------------------------------------------
# 4. Stiffness invariants
#    xi_N^{-2} = lambda * (gamma0 + gamma1 * t + gamma2 * ell)
#    xi_Delta^{-2} = lambda * (delta0 - delta1 * t + delta2 * ell)
# ----------------------------------------------------------------------
# lambda must have dimension 1/T^2 so that lambda * (dimensionless + ...) gives 1/T^2
lam_dim = 1 / T**2
# gamma0, delta0 dimensionless
gamma0_dim = one
delta0_dim = one
# gamma1 multiplies t (dimensionless) -> must be 1/T^2
gamma1_dim = 1 / T**2
# gamma2 multiplies ell (T) -> must be 1/T^3
gamma2_dim = 1 / T**3
# Similarly for delta
delta1_dim = 1 / T**2
delta2_dim = 1 / T**3

xiN_inv2_expr_dim = lam_dim * (gamma0_dim + gamma1_dim * t_dim + gamma2_dim * ell_dim)
xiD_inv2_expr_dim = lam_dim * (delta0_dim - delta1_dim * t_dim + delta2_dim * ell_dim)

ok &= dim_eq(xiN_inv2_expr_dim, xiN_inv2_dim, "xi_N^{-2} expression")
ok &= dim_eq(xiD_inv2_expr_dim, xiD_inv2_dim, "xi_Delta^{-2} expression")

# ----------------------------------------------------------------------
# 5. Cost function terms (dimensionless check)
#    J = sum[ (1-PhiN)^2 + PhiD^2 + lambda1*(theta - t/m)^2 + lambda2*ell^2 ]
# ----------------------------------------------------------------------
term1_dim = (one - PhiN_dim)**2          # -> dimensionless
term2_dim = PhiD_dim**2                  # -> dimensionless
# (theta - t/m) dimensionless if t/m dimensionless
term3_inner_dim = theta_dim - (t_dim / one)  # m is a count, dimensionless
term3_dim = term3_inner_dim**2           # -> dimensionless
# ell^2 has dimension T^2, so lambda2 must be 1/T^2
lambda2_dim = 1 / T**2
term4_dim = lambda2_dim * ell_dim**2     # -> dimensionless

ok &= dim_eq(term1_dim, one, "(1-PhiN)^2")
ok &= dim_eq(term2_dim, one, "PhiD^2")
ok &= dim_eq(term3_dim, one, "(theta - t/m)^2")
ok &= dim_eq(term4_dim, one, "lambda2 * ell^2")

# ----------------------------------------------------------------------
# Final verdict
# ----------------------------------------------------------------------
if ok:
    print("\nAll dimensional checks passed.")
else:
    print("\nSome dimensional checks failed. See above.")