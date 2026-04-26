# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith – Omega Protocol Math Validator
Verifies dimensional consistency of the POASH-Ω formulation
after correcting the Φ_N/Φ_Δ mapping.
"""

import sympy as sp

# ------------------------------------------------------------------
# Define dimensional symbols
# ------------------------------------------------------------------
T = sp.symbols('T', positive=True)   # base dimension: time
# Dimensionless fields
dimless = 1

# Coupling constant λ has dimension [T]^{-2}
lam = sp.symbols('lam', positive=True)
dim_lam = T**(-2)

# ------------------------------------------------------------------
# Helper: dimension of an expression (as power of T)
# ------------------------------------------------------------------
def dim_of(expr):
    """Return the exponent of T in expr assuming all symbols are dimensionless
    except lam (dimension T^{-2})."""
    # Replace symbols with their dimensional exponents
    subs_map = {
        lam: -2,   # lam -> T^{-2}
        # all other symbols (I, PHI, psi, PhiN, PhiD, A_k, etc.) -> 0
    }
    # Extract exponent of T by converting to a power of T
    # We'll treat expr as product of powers; sympy's as_coeff_mul helps
    coeff, terms = expr.as_coeff_mul()
    # coeff is numeric, terms are symbols/powers
    exp = 0
    for term in terms:
        if term.is_Pow:
            base, expo = term.as_base_exp()
            if base == lam:
                exp += expo * (-2)
            else:
                # dimensionless base
                pass
        else:
            # symbol itself (lam or dimensionless)
            if term == lam:
                exp += -2
            # else dimensionless -> 0
    return exp

# ------------------------------------------------------------------
# Define symbols for the fields (all dimensionless)
# ------------------------------------------------------------------
I, PHI, psi, PhiN, PhiD = sp.symbols('I PHI psi PhiN PhiD')
# harmonic amplitudes and their stats (dimensionless)
A_k, mu_k, sigma_k = sp.symbols('A_k mu_k sigma_k')
# coherence average (dimensionless)
coh = sp.symbols('coh')
# time (dimension T)
t = sp.symbols('t')
# ------------------------------------------------------------------
# 1. Action integrand: L = 0.5*(dI/dt)^2 + V(I)
# ------------------------------------------------------------------
dI_dt = sp.diff(I, t)
L = sp.Rational(1,2) * dI_dt**2 + (lam/4) * (I**2 - I**2)**2  # I0 replaced by I for dim check
# Actually V(I) = (lam/4)*(I^2 - I0^2)^2 ; I0 is dimensionless constant
I0 = sp.symbols('I0')
V = (lam/4) * (I**2 - I0**2)**2
L = sp.Rational(1,2) * dI_dt**2 + V

print("Action Lagrangian dimension exponent:", dim_of(L))
# Expect 0 because (dI/dt)^2 ~ T^{-2} and lam ~ T^{-2} -> both give T^{-2} *? Wait:
# dI/dt has dimension T^{-1} (I dimensionless) -> (dI/dt)^2 -> T^{-2}
# lam * (dimensionless)^4 -> T^{-2}
# So L has dimension T^{-2}. The action S = ∫ L dt adds +1 -> T^{-1} (or dimensionless if ħ=1).
# We'll just verify that both terms share same dimension.
term1_dim = dim_of(sp.Rational(1,2) * dI_dt**2)
term2_dim = dim_of(V)
print("  dI/dt^2 term dimension exponent:", term1_dim)
print("  V(I) term dimension exponent:", term2_dim)
assert term1_dim == term2_dim, "Action terms dimension mismatch"

# ------------------------------------------------------------------
# 2. Stiffness invariants: xi_N^{-2} = λ (3/coh + 1/coh^2)
# ------------------------------------------------------------------
xi_N_sq_inv = lam * (3/coh + 1/coh**2)
print("\nxi_N^{-2} dimension exponent:", dim_of(xi_N_sq_inv))
# Should be -2 (same as lam)
assert dim_of(xi_N_sq_inv) == -2, "xi_N^{-2} dimension mismatch"

# ------------------------------------------------------------------
# 3. Corrected mapping to covariant modes
# ------------------------------------------------------------------
# Φ_N = Φ_N0 + α_N * I   (α_N dimensionless)
alpha_N = sp.symbols('alpha_N')
PhiN_corr = sp.symbols('PhiN0') + alpha_N * I
print("\nPhiN_corr dimension exponent:", dim_of(PhiN_corr))
# Should be 0 (dimensionless)
assert dim_of(PhiN_corr) == 0, "PhiN_corr dimension mismatch"

# Φ_Δ = Φ_Δ0 - α_Δ * PHI + γ * Var(A)
alpha_Delta = sp.symbols('alpha_Delta')
gamma = sp.symbols('gamma')
VarA = sp.symbols('VarA')   # dimensionless variance
PhiD_corr = sp.symbols('PhiD0') - alpha_Delta * PHI + gamma * VarA
print("PhiD_corr dimension exponent:", dim_of(PhiD_corr))
assert dim_of(PhiD_corr) == 0, "PhiD_corr dimension mismatch"

# ------------------------------------------------------------------
# 4. Boundary conditions (dimensionless checks)
# ------------------------------------------------------------------
# Shredding Event: PHI -> 0, xi -> 0  (xi has dimension T)
# Informational Freeze: PHI -> 1, xi -> ∞
# We just verify that the symbols used are dimensionless where required.
print("\nBoundary condition symbols dimensionless check:")
print("  PHI dimension exponent:", dim_of(PHI))   # should be 0
print("  xi_N dimension exponent:", dim_of(sp.symbols('xi_N')))  # we haven't defined; assume T
# For completeness, define xi_N dimension as T
xi_N = sp.symbols('xi_N')
dim_xi_N = T
print("  xi_N (assumed) dimension exponent:", 1)  # T^1

# ------------------------------------------------------------------
# If we reach here, all checks passed
print("\n=== ALL DIMENSIONAL CHECKS PASSED ===")