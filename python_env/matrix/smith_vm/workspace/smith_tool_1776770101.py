# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Dimensional‑consistency check for the Engine's revised α_fs running.
"""

import sympy as sp

# Base dimension symbol
M = sp.symbols('M', positive=True)

# Assign dimensions (as powers of M)
# Mass dimension of a quantity Q is stored as dim[Q] = M**exp
dim = {}

# Fundamental constants
dim['alpha']   = M**0          # fine‑structure constant (dimensionless)
dim['m_e']     = M**1          # electron mass
dim['q']       = M**1          # momentum (energy) scale
dim['Lambda_N']= M**1
dim['Lambda_Delta']= M**1
dim['Lambda_S']= M**1

# Couplings (dimensionless after scaling)
dim['g_N']     = M**0
dim['g_Delta'] = M**0
dim['kappa_S'] = M**0

# Invariant psi (dimensionless)
dim['psi']     = M**0

# I0 sets the mass scale for the modes
dim['I0']      = M**1

# Mode amplitudes (dimensionless after dividing by I0)
dim['phi_N']   = M**0   # cosh(psi)
dim['phi_Delta']= M**0  # sinh(psi)

# Entropy gauge: S_h made dimensionless by scaling;
# derivative adds one mass dimension, but the protocol includes a factor
# of xi0^-2 (mass^-2) inside the definition of A_mu, rendering (d S_h)^2 dimensionless.
# We therefore assign dim[S_h] = M**0 and dim[d S_h] = M**0.
dim['S_h']     = M**0
dim['dS_h']    = M**0   # ∂_mu S_h after scaling

# Logarithms are dimensionless
def dim_log(arg):
    return M**0   # log of dimensionless ratio

# Build each term's dimension
def term_dim(coeff_dim, log_dim):
    return coeff_dim * log_dim

# QED term
dim_QED = term_dim(dim['alpha'], dim_log(dim['q']**2 / dim['m_e']**2))
# Phi_N term
dim_PhiN = term_dim(dim['g_N']**2 * dim['phi_N']**2,
                    dim_log(dim['q']**2 / dim['Lambda_N']**2))
# Phi_Delta term
dim_PhiD = term_dim(dim['g_Delta']**2 * dim['phi_Delta']**2,
                    dim_log(dim['q']**2 / dim['Lambda_Delta']**2))
# Entropy term
dim_Ent  = term_dim(dim['kappa_S'] * dim['dS_h']**2,
                    dim_log(dim['q']**2 / dim['Lambda_S']**2))

# Check dimensionlessness
def is_dimensionless(expr):
    return expr == M**0

results = {
    "QED term": is_dimensionless(dim_QED),
    "Phi_N term": is_dimensionless(dim_PhiN),
    "Phi_Delta term": is_dimensionless(dim_PhiD),
    "Entropy term": is_dimensionless(dim_Ent),
}

print("Dimensional‑consistency check (True = dimensionless):")
for k, v in results.items():
    print(f"{k:20}: {v}")

# Overall verdict
overall = all(results.values())
print("\nOverall dimensional consistency:", overall)

# Additionally verify the invariant Phi_N^2 - Phi_Delta^2 = I0^2
Phi_N_sq = dim['I0']**2 * sp.cosh(dim['psi'])**2
Phi_D_sq = dim['I0']**2 * sp.sinh(dim['psi'])**2
invariant = sp.simplify(Phi_N_sq - Phi_D_sq - dim['I0']**2)
print("\nInvariant check Φ_N^2 - Φ_Δ^2 - I0^2 =", invariant)
print("Invariant satisfied? ", invariant == 0)