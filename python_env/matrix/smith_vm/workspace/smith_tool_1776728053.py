# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Higher-Order Lattice Polarization correction
for the fine-structure constant within the Omega Protocol.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols (all dimensionless unless noted)
# ----------------------------------------------------------------------
# Fundamental couplings
e   = sp.symbols('e', real=True, positive=True)          # electric charge
gD  = sp.symbols('gD', real=True, positive=True)        # Yukawa coupling Phi_Delta-fermion
# Masses
m   = sp.symbols('m', real=True, positive=True)         # fermion mass
mPhi= sp.symbols('mPhi', real=True, positive=True)      # generated mass of Phi_Delta (IR regulator)
# Momenta
q   = sp.symbols('q', real=True)                        # photon momentum (|q| has dimension 1/length)
# Omega Protocol invariants
psi = sp.symbols('psi', real=True)                      # ln(Phi_N/I0)
xi0 = sp.symbols('xi0', real=True, positive=True)      # reference length (sets lattice spacing)
xiD = sp.symbols('xiD', real=True, positive=True)      # Archive correlation length (dimensionless ratio)
# Constants
pi  = sp.pi
C   = sp.symbols('C', real=True)                        # lattice coefficient (dimensionless)

# ----------------------------------------------------------------------
# Helper: dimension checking
# ----------------------------------------------------------------------
# In natural units (hbar=c=1): [e] = 0, [gD] = 0, [m] = 1/L, [q] = 1/L,
# [xi0] = L, [psi] = 0, [C] = 0.
def dim(expr):
    """Return the dimension of expr as a power of length (L)."""
    # Replace each symbol by its dimension exponent
    dims = {
        e: 0,
        gD: 0,
        m: -1,      # mass ~ 1/L
        q: -1,
        xi0: +1,    # length
        psi: 0,
        xiD: 0,
        C: 0,
        pi: 0,
    }
    # Use sympy to replace powers
    expr_subs = expr.subs(dims)
    # Simplify assuming only powers of L remain
    return sp.simplify(expr_subs)

# ----------------------------------------------------------------------
# 1. Proposed alpha_fs(q^2) expression (as given in the answer)
# ----------------------------------------------------------------------
alpha0 = e**2/(4*pi)                     # dimensionless
L      = sp.log(-q**2/m**2)              # log argument dimensionless

# QED one-loop term
term_QED = alpha0/(3*pi) * L

# Scalar-exchange double-log term (as written)
term_scalar = gD**2 * alpha0/(32*pi**4) * L**2

# Lattice term (as written in the answer)
term_lattice_wrong = C * xi0**(-2) * sp.exp(2*psi) * q**2

# Corrected lattice term using a = xi0 * exp(-psi)
a = xi0 * sp.exp(-psi)
term_lattice_correct = C * a**2 * q**2   # = C * xi0**2 * exp(-2*psi) * q**2

alpha_proposed = alpha0 * (1 + term_QED + term_scalar + term_lattice_wrong)
alpha_correct  = alpha0 * (1 + term_QED + term_scalar + term_lattice_correct)

# ----------------------------------------------------------------------
# 2. Dimension check
# ----------------------------------------------------------------------
print("=== Dimension analysis (should be 0 for dimensionless) ===")
print("alpha0 dimension:", dim(alpha0))
print("term_QED dimension:", dim(term_QED))
print("term_scalar dimension:", dim(term_scalar))
print("term_lattice_wrong dimension:", dim(term_lattice_wrong))
print("term_lattice_correct dimension:", dim(term_lattice_correct))
print("alpha_proposed dimension:", dim(alpha_proposed))
print("alpha_correct dimension:", dim(alpha_correct))
print()

# ----------------------------------------------------------------------
# 3. Beta function from the proposed expression
# ----------------------------------------------------------------------
# beta = d alpha / d ln(q^2)  (since d/d ln(q^2) = (q^2/2) d/d(q^2))
def beta_from_alpha(alpha_expr):
    # derivative wrt ln(q^2) = derivative wrt L because L = ln(-q^2/m^2)
    dalpha_dL = sp.diff(alpha_expr, L)
    # dL/d ln(q^2) = 1
    return sp.simplify(dalpha_dL)

beta_proposed = beta_from_alpha(alpha_proposed)
beta_correct  = beta_from_alpha(alpha_correct)

print("=== Beta functions ===")
print("beta_proposed =", sp.simplify(beta_proposed))
print("beta_correct  =", sp.simplify(beta_correct))
print()

# ----------------------------------------------------------------------
# 4. Expected scalar-induced beta piece (from literature)
# ----------------------------------------------------------------------
# One-loop scalar-fermion loop contributes to photon self-energy:
#   Pi_scalar ~ (gD^2 e^2)/(16 pi^2) * L   (single log)
# This yields a contribution to beta(alpha) = (gD^2 alpha^2)/(16 pi^4) * L
expected_scalar_beta = gD**2 * alpha0**2/(16*pi**4) * L
print("Expected scalar-induced beta piece:", expected_scalar_beta)
print("Difference (proposed - expected):", sp.simplify(beta_proposed - expected_scalar_beta))
print("Difference (correct - expected):", sp.simplify(beta_correct - expected_scalar_beta))
print()

# ----------------------------------------------------------------------
# 5. Omega Protocol invariant checks
# ----------------------------------------------------------------------
# psi must appear only through exp(+/- psi) (dimensionless)
# xi0 must appear with positive power when combined with q^2 to give a^2 q^2
def check_invariant(expr, name):
    # Replace exp(psi) and exp(-psi) by a dummy to see if any other psi remains
    expr_sub = expr.subs({sp.exp(psi): sp.symbols('Epsi'), sp.exp(-psi): sp.symbols('Empsi')})
    # If psi still appears explicitly, flag
    if expr_sub.has(psi):
        print(f"[{name}] WARNING: explicit psi dependence found.")
    else:
        print(f"[{name}] OK: psi only via exp(+/- psi).")
    # Check xi0 power: we expect xi0^2 * exp(-2psi) * q^2
    # Extract powers of xi0 and q
    pow_xi0 = sp.Poly(expr, xi0).degree() if expr.has(xi0) else 0
    pow_q   = sp.Poly(expr, q).degree()   if expr.has(q)   else 0
    print(f"[{name}] xi0 power: {pow_xi0}, q power: {pow_q}")
    # For a^2 q^2 term we need xi0^2 * q^2
    if pow_xi0 == 2 and pow_q == 2:
        print(f"[{name}] xi0 and q powers match a^2 q^2 expectation.")
    else:
        print(f"[{name}] xi0/q powers DO NOT match a^2 q^2 expectation.")
    print()

print("=== Invariant checks ===")
check_invariant(term_lattice_wrong, "lattice_wrong")
check_invariant(term_lattice_correct, "lattice_correct")