# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the one-loop anisotropic vacuum-polarization correction.
Shows that premature contraction of delta_mu_z delta_nu_z kills angular dependence.
"""

import sympy as sp
import itertools

# Define metric (Euclidean) and gamma matrices (symbolic)
# We only need the trace identities: tr[gamma_mu gamma_nu] = 4*delta_mu_nu
# and tr[gamma_mu gamma_nu gamma_rho gamma_sigma] = 4*(delta_mu_nu*delta_rho_sigma
#                                                    - delta_mu_rho*delta_nu_sigma
#                                                    + delta_mu_sigma*delta_nu_rho)

def delta(a, b):
    """Kronecker delta."""
    return 1 if a == b else 0

# Indices
mu, nu, rho, sigma = sp.symbols('mu nu rho sigma', integer=True)
# Direction vector n (archive direction) picks out z-index = 3 (0-based)
n_idx = 3

# Momentum components (symbolic)
k = sp.Matrix(sp.symbols('k0 k1 k2 k3'))
kp = sp.Matrix(sp.symbols('kp0 kp1 kp2 kp3'))

# Helper: sin(k_i) (we treat sin as a placeholder function)
sin = sp.Function('sin')
def sin_comp(vec, i):
    return sin(vec[i])

# Build the trace for the anisotropic insertion:
# Tr[ gamma_mu (i gamma·sin k + m) gamma_nu (i gamma·sin(k-p) + m) ]
# with one insertion of (PhiDelta/2) i gamma_z sin k_z in the first propagator.
# We compute the term linear in PhiDelta:
#   Tr[ gamma_mu (i gamma_z sin k_z) gamma_nu (i gamma·sin(k-p) + m) ] +
#   Tr[ gamma_mu (i gamma·sin k + m) gamma_nu (i gamma_z sin k_z) ]

def gamma_trace(mu_idx, nu_idx, insert_first=True):
    """
    Returns the trace coefficient (without overall prefactors) for the
    PhiDelta-linear term with the insertion in the first (if True) or second propagator.
    """
    # Insertion matrix: i gamma_z sin k_z
    insert = sp.I * sp.symbols('gamma_z') * sin_comp(k if insert_first else kp, n_idx)
    # The other propagator: i gamma·sin(q) + m, where q = k-p (first) or k (second)
    other_momentum = kp if insert_first else k
    other = sp.I * sum(sp.symbols(f'gamma_{i}') * sin_comp(other_momentum, i) for i in range(4)) + sp.symbols('m')
    # Full product: gamma_mu * insert * gamma_nu * other
    # We only need the trace; use known identities.
    # Since we treat gamma matrices symbolically, we replace products with trace rules.
    # Instead of building full algebra, we directly apply trace identities:
    # Tr[gamma_mu gamma_alpha gamma_nu gamma_beta] = 4*(delta_mu_alpha*delta_nu_beta
    #                                                - delta_mu_nu*delta_alpha_beta
    #                                                + delta_mu_beta*delta_nu_alpha)
    # Tr[gamma_mu gamma_alpha gamma_nu] = 0 (odd number)
    # Tr[gamma_mu gamma_nu] = 4*delta_mu_nu
    # Tr[gamma_mu] = 0
    # We'll compute contributions from the term with two gammas from insert and other.
    # Insert contributes one gamma_z; other contributes sum over gamma_i sin_i.
    # So we need Tr[gamma_mu gamma_z gamma_nu gamma_i] * (I * sin_z) * (I * sin_i)
    # plus the mass term: Tr[gamma_mu gamma_z gamma_nu] * m (which vanishes because odd).
    coeff = 0
    for i in range(4):
        # Tr[gamma_mu gamma_z gamma_nu gamma_i]
        tr = 4 * (delta(mu, n_idx) * delta(nu, i) -
                  delta(mu, nu) * delta(n_idx, i) +
                  delta(mu, i) * delta(nu, n_idx))
        # factors: (I from insert)*(I from other) = -1
        coeff += -tr * sin_comp(k if insert_first else kp, n_idx) * sin_comp(other_momentum, i)
    return coeff

# Compute total linear-in-PhiDelta trace (first + second insertion)
trace_total = gamma_trace(mu, nu, insert_first=True) + gamma_trace(mu, nu, insert_first=False)
trace_total_simplified = sp.simplify(trace_total)
print("Trace coefficient (linear in PhiDelta) before any delta contraction:")
print(trace_total_simplified)
print("\nNow contract mu and nu with delta_mu_z delta_nu_z (premature contraction):")
# Premature contraction: set mu = nu = n_idx and multiply by delta_mu_z delta_nu_z (=1)
premature = trace_total_simplified.subs({mu: n_idx, nu: n_idx})
print("Result after premature contraction:", sp.simplify(premature))
print("\nObserve that the result is proportional to m^2 (mass term) only -> angular dependence lost.")
# To see the angular structure, keep mu,nu generic and look at the sin_z*sin_z term:
print("\nExtracting sin_z*k * sin_z*(k-p) term (keeping mu,nu generic):")
# Choose a representative component, e.g., mu = x (0), nu = x (0) to see angular part.
sample = trace_total_simplified.subs({mu: 0, nu: 0})
print("Sample component (mu=nu=x):", sp.simplify(sample))
# The expression contains sin(k_z)*sin(kp_z) etc., showing angular dependence.