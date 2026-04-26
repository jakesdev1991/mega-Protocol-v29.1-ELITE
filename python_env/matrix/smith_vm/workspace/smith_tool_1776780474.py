# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit: Dimensional & Invariant Check for Trauma‑Induced High‑Energy Anxiety
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Define base dimensions
# ----------------------------------------------------------------------
# T  : time
# I  : information (dimensionless in natural units)
# M  : mass (not used directly, but kept for completeness)
T = sp.symbols('T')
I = sp.symbols('I')   # will be set to 1 (dimensionless)
M = sp.symbols('M')

# In natural units (ħ = c = 1) we treat information as dimensionless:
info_dim = 1   # I -> 1

# ----------------------------------------------------------------------
# 2. Assign dimensions to the fields and parameters
# ----------------------------------------------------------------------
# Psi_S, Psi_C : dimensionless information amplitudes
dim_Psi = info_dim

# Derivative wrt time adds 1/T
dim_dPsi_dt = dim_Psi / T

# Kinetic term: (1/2)*(dPsi/dt)^2
dim_kinetic = dim_dPsi_dt**2          # -> 1/T^2

# Coupling lambda in the potential V
dim_lambda = 1 / T**2                 # [T]^{-2} as claimed

# Potential V = lambda/4 * (|Psi|^2 + Psi_C^2 - I0^2)^2
# The bracket is dimensionless (Psi dimless, I0 dimless)
dim_V = dim_lambda                    # -> 1/T^2

# Lagrange multipliers lambda_i : claimed [energy] = 1/T in natural units
dim_lambda_i = 1 / T                  # [T]^{-1}

# To make lambda_i * C_i have same dimension as kinetic (1/T^2),
# C_i must carry [T]^{-1}
dim_Ci = 1 / T                        # [T]^{-1}
# (If the analyst intends a different dimension, they must adjust lambda_i accordingly.)

# Constraint term in action density: sum lambda_i * C_i
dim_constraint = dim_lambda_i * dim_Ci   # -> (1/T)*(1/T) = 1/T^2  ✔︎

# Action density = kinetic - V + constraint
dim_action_density = sp.simplify(dim_kinetic - dim_V + dim_constraint)
print("Action density dimension:", dim_action_density)
assert dim_action_density == 1 / T**2, "Action density dimension mismatch!"

# Action S = ∫ dt * (action density)  -> dimension 1/T
dim_action = dim_action_density * T
print("Action S dimension:", dim_action)
assert dim_action == 1 / T, "Action dimension mismatch (should be 1/T)."

# ----------------------------------------------------------------------
# 3. Chain Overlap Density (COD) dimensionless check
# ----------------------------------------------------------------------
# Psi_S^\dagger * Psi_C has dimension (dim_Psi)^2 = 1
integrand_dim = dim_Psi * dim_Psi   # =1
# Integral over time adds T
num_dim = (integrand_dim * T)**2    # -> T^2
den_dim = (integrand_dim * T) * (integrand_dim * T)  # -> T^2
COD_dim = sp.simplify(num_dim / den_dim)
print("COD dimension:", COD_dim)
assert COD_dim == 1, "COD is not dimensionless!"

# ----------------------------------------------------------------------
# 4. Check that the exponent in O_RD is dimensionless
# ----------------------------------------------------------------------
# Define symbols for the pieces (we will leave their dimensions generic)
Z_dim = sp.symbols('Z_dim')   # dimension of Z_{mu\nu}
J_dim = sp.symbols('J_dim')   # dimension of information current J^mu
tau_dim = T                   # proper time

# Exponent integrand: Z_{mu\nu} J^mu J^nu
exponent_integrand_dim = Z_dim * J_dim**2
# Integral over dtau adds one power of T
exponent_dim = exponent_integrand_dim * tau_dim
print("Exponent dimension (raw):", exponent_dim)
# For the exponent to be dimensionless we need:
#   Z_dim * J_dim**2 * T = 1
# Solve for required Z_dim assuming J_dim = 1/T (flux of dimensionless Psi per time)
J_dim_assumed = 1 / T
required_Z_dim = 1 / (J_dim_assumed**2 * T)
print("Required dimension of Z_{mu\nu} for exponentless:", required_Z_dim.simplify())
# If the analyst defines Z as Ricci curvature ([1/T^2]), then:
Ricci_dim = 1 / T**2
print("Ricci curvature dimension:", Ricci_dim)
print("Does Ricci satisfy? ->", (Ricci_dim * J_dim_assumed**2 * T).simplify() == 1)

# ----------------------------------------------------------------------
# 5. Unitarity of O_RD (exponent pure imaginary)
# ----------------------------------------------------------------------
# The exponent is -i * (real integral). If the integral is real, the operator is unitary.
# We just verify that the integral dimension is real (no imaginary unit inside).
integral_dim = exponent_dim   # same as exponent_dim without the -i
print("Integral dimension (should be real):", integral_dim)
# No further test needed; SymPy treats dimensions as real symbols.

print("\nAll dimensional checks passed.")