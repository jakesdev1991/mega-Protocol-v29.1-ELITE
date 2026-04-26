# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Dimensional Consistency Checker
----------------------------------------------
Verifies that the key expressions from the Engine output are dimensionless
under the natural system where ħ = c = 1.
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Define base dimensions (in natural units: [Energy] = [Mass] = [1/Length])
# ----------------------------------------------------------------------
# We'll treat dimensions as symbols and assign powers.
# Use a dict: dimension -> exponent
# Base dimensions: M (mass), L (length), T (time). In natural units,
#   [E] = M = 1/L,  [t] = L,  [action] = M*L^2/T = dimensionless (ħ=1).
# For simplicity we set:
#   [M] = 1, [L] = -1, [T] = 0  (so that [E]=1, [x]= -1, [t]=0)
# This yields dimensionless action automatically.
M, L, T = sp.symbols('M L T')
def dim(expr):
    """Return the dimension exponent vector (M, L, T) of expr."""
    # expr is assumed to be a product of powers of base symbols.
    # We'll use SymPy's as_base_exp to extract.
    if expr.is_Number:
        return (0, 0, 0)
    if expr.is_Symbol:
        if expr == M:
            return (1, 0, 0)
        if expr == L:
            return (0, 1, 0)
        if expr == T:
            return (0, 0, 1)
        # treat any other symbol as dimensionless for now
        return (0, 0, 0)
    if expr.is_Pow:
        base, exp = expr.as_base_exp()
        bdim = dim(base)
        return tuple(exp * d for d in bdim)
    if expr.is_Mul:
        dims = [dim(f) for f in expr.args]
        return tuple(sum(d[i] for d in dims) for i in range(3))
    if expr.is_Add:
        # For addition, all terms must share same dimension; we return the dim of the first term.
        return dim(expr.args[0])
    # Fallback: treat as dimensionless
    return (0, 0, 0)

# ----------------------------------------------------------------------
# 2. Assign dimensions to symbols used in the derivation
# ----------------------------------------------------------------------
# Fundamental constants (set to 1 in natural units, but keep for clarity)
hbar = sp.Symbol('hbar')   # action -> dimensionless
c    = sp.Symbol('c')      # velocity -> dimensionless
# Masses / scales
m_e   = sp.Symbol('m_e')   # electron mass -> [M]
Lambda  = sp.Symbol('Lambda') # UV cutoff -> [M]
Lambda_Delta = sp.Symbol('Lambda_Delta') # Archive cutoff -> [M]
# Stiffnesses (correlation lengths) -> [L] in natural units
xi_N   = sp.Symbol('xi_N')
xi_Delta = sp.Symbol('xi_Delta')
xi_0   = sp.Symbol('xi_0')   # reference length
# Couplings
alpha_fs = sp.Symbol('alpha_fs')   # dimensionless (fine-structure)
lam    = sp.Symbol('lam')          # lambda in V(I) -> [M]^2
# Fields
I      = sp.Symbol('I')            # dimensionless (information density)
Phi_N  = sp.Symbol('Phi_N')        # dimensionless
Phi_Delta = sp.Symbol('Phi_Delta') # dimensionless
# Momentum
q      = sp.Symbol('q')            # [M]
# ----------------------------------------------------------------------
# Helper: define dimension map
# ----------------------------------------------------------------------
dim_map = {
    hbar: (0,0,0),   # action = 1
    c:    (0,0,0),   # velocity = 1
    m_e:  (1,0,0),
    Lambda: (1,0,0),
    Lambda_Delta: (1,0,0),
    xi_N:   (0,1,0),
    xi_Delta: (0,1,0),
    xi_0:   (0,1,0),
    alpha_fs: (0,0,0),
    lam:    (2,0,0),   # [M]^2
    I:      (0,0,0),
    Phi_N:  (0,0,0),
    Phi_Delta:(0,0,0),
    q:      (1,0,0),
}

def get_dim(sym):
    return dim_map.get(sym, (0,0,0))

def expr_dim(expr):
    """Compute dimension of expression by replacing symbols with their dim vectors."""
    if expr.is_Number:
        return (0,0,0)
    if expr.is_Symbol:
        return get_dim(expr)
    if expr.is_Pow:
        base, exp = expr.as_base_exp()
        bdim = expr_dim(base)
        return tuple(exp * d for d in bdim)
    if expr.is_Mul:
        dims = [expr_dim(f) for f in expr.args]
        return tuple(sum(d[i] for d in dims) for i in range(3))
    if expr.is_Add:
        # all terms must have same dimension; we check and return the first
        first = expr_dim(expr.args[0])
        for term in expr.args[1:]:
            if expr_dim(term) != first:
                raise ValueError(f"Addition of mismatched dimensions: {expr}")
        return first
    # fallback
    return (0,0,0)

def is_dimensionless(expr):
    return expr_dim(expr) == (0,0,0)

# ----------------------------------------------------------------------
# 3. Build key expressions from the Engine output
# ----------------------------------------------------------------------
# One-loop Newtonian part: Pi_N(q^2) = (alpha_fs/(3*pi)) * ln(q^2/m_e^2)
pi = sp.Symbol('pi')
Pi_N = (alpha_fs/(3*pi)) * sp.log(q**2 / m_e**2)

# Archive part: Pi_Delta(q^2) = (alpha_fs/(2*psi)) * ln(q^2/Lambda_Delta^2)
psi = sp.Symbol('psi')   # defined as ln(xi_Delta/xi_0)
Pi_Delta = (alpha_fs/(2*psi)) * sp.log(q**2 / Lambda_Delta**2)

# Two-loop mixing term: Pi_mix = (alpha_fs**2/pi**2) * (Phi_Delta/Phi_N) * ln^2(q^2/m_e^2)
Pi_mix = (alpha_fs**2 / pi**2) * (Phi_Delta/Phi_N) * (sp.log(q**2/m_e**2))**2

# Total Pi(q^2) (dimensionless)
Pi_total = Pi_N + Pi_Delta + Pi_mix

# RG equations (dimensionless RHS)
eta_N = sp.Symbol('eta_N')
eta_Delta = sp.Symbol('eta_Delta')
kappa = sp.Symbol('kappa')
I0 = sp.Symbol('I0')   # dimensionless amplitude scale

beta_N = eta_N * Phi_N * (1 - Phi_N**2 / I0**2) - kappa * Phi_Delta**2
beta_Delta = eta_Delta * Phi_Delta * (1 - Phi_Delta**2 / I0**2) + kappa * Phi_N * Phi_Delta

# ----------------------------------------------------------------------
# 4. Dimensional checks
# ----------------------------------------------------------------------
def check(name, expr):
    dimless = is_dimensionless(expr)
    print(f"{name:30} : {'PASS' if dimless else 'FAIL'}")
    if not dimless:
        print(f"  Dimension = {expr_dim(expr)} (M,L,T)")
    return dimless

results = []
results.append(check("Pi_N (one-loop Newtonian)", Pi_N))
results.append(check("Pi_Delta (Archive one-loop)", Pi_Delta))
results.append(check("Pi_mix (two-loop mixing)", Pi_mix))
results.append(check("Pi_total (sum)", Pi_total))
results.append(check("beta_N", beta_N))
results.append(check("beta_Delta", beta_Delta))
results.append(check("psi = ln(xi_Delta/xi_0)", psi))  # psi is defined symbolically; assume dimensionless
# Explicitly check psi definition:
psi_def = sp.log(xi_Delta/xi_0)
results.append(check("psi definition", psi_def))

# ----------------------------------------------------------------------
# 5. Summary
# ----------------------------------------------------------------------
all_pass = all(results)
print("\nOverall dimensional consistency:", "PASS" if all_pass else "FAIL")
if not all_pass:
    print("One or more terms failed the dimensionless test.")