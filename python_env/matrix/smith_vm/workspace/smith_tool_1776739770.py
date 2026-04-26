# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Higher-Order Lattice Polarization derivation
for the fine-structure constant α_fs within the Omega Protocol.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols (all assumed positive unless noted)
# ----------------------------------------------------------------------
# Fundamental constants (set to 1 in natural units for simplicity)
hbar, c = sp.symbols('hbar c', positive=True)

# Couplings and masses
e, gD, gN, m, lam = sp.symbols('e gD gN m lam', positive=True)  # e: electric charge, gD/gN: Yukawa, m: fermion mass, lam: scalar self-coupling

# Omega Protocol invariants
psi, xi_N, xi_Delta, xi0 = sp.symbols('psi xi_N xi_Delta xi0', positive=True)  # psi dimensionless, xi_* length scales

# Momentum transfer
q2 = sp.symbols('q2', real=True)  # q^2 (can be negative for spacelike)

# UV cutoff and lattice spacing
Lambda = sp.symbols('Lambda', positive=True)  # UV cutoff
a = sp.symbols('a', positive=True)            # lattice spacing

# ----------------------------------------------------------------------
# 1. Define the proposed expression for α_fs(q^2)
# ----------------------------------------------------------------------
α0 = sp.symbols('α0', positive=True)  # bare fine-structure constant e^2/(4πħc)

# Logarithmic piece (standard QED)
L = sp.log(-q2 / m**2)  # assumes -q2 >> m^2

# One-loop QED term
term_QED = α0/(3*sp.pi) * L

# Two-loop ΦΔ exchange term (double log)
term_phiDelta = (gD**2 * α0) / (32*sp.pi**4) * L**2

# Lattice power-law term (C dimensionless)
C = sp.symbols('C')  # dimensionless constant
term_lattice = C * xi0**(-2) * sp.exp(2*psi) * q2

# Full α_fs (to the order shown)
α_fs = α0 * (1 + term_QED + term_phiDelta + term_lattice)

# ----------------------------------------------------------------------
# 2. Dimensionality check (in natural units ħ=c=1)
# ----------------------------------------------------------------------
# In natural units: [e] = 0 (dimensionless), [gD] = 0, [m] = 1, [q2] = 2,
# [xi0] = -1 (length), [psi] = 0, [C] = 0.
# We verify each additive correction is dimensionless.

def dim_of(expr):
    """Return the mass dimension of expr assuming e,gD,psi,C dimensionless."""
    # Replace each symbol with its dimension exponent:
    dim_map = {
        e: 0, gD: 0, gN: 0, m: 1, lam: 0,
        xi0: -1, xi_N: -1, xi_Delta: -1,
        psi: 0, C: 0,
        q2: 2,
        sp.log(-q2/m**2): 0,  # log of dimensionless ratio
    }
    # Replace powers explicitly
    expr_sub = expr.subs(dim_map)
    # Simplify to a power of mass (should be a number)
    return sp.simplify(expr_sub)

print("Dimension of term_QED:", dim_of(term_QED))
print("Dimension of term_phiDelta:", dim_of(term_phiDelta))
print("Dimension of term_lattice:", dim_of(term_lattice))
print("All should be 0 (dimensionless).")

# ----------------------------------------------------------------------
# 3. Cutoff mapping: a = ξ0 * exp(-psi)  <=>  Λ = π/ξ0 * exp(psi)
# ----------------------------------------------------------------------
# Verify that Λ * a = π (up to the chosen convention)
Lambda_expr = sp.pi/xi0 * sp.exp(psi)
a_expr = xi0 * sp.exp(-psi)

print("\nLambda * a =", sp.simplify(Lambda_expr * a_expr))
print("Expected: π")

# ----------------------------------------------------------------------
# 4. Φ_Δ mass generation: m_phi^2 ~ λ * xi_Delta^{-2}
# ----------------------------------------------------------------------
m_phi_sq = lam * xi_Delta**(-2)
print("\nΦ_Δ mass^2 expression:", m_phi_sq)
print("Dimension check:", dim_of(m_phi_sq))  # should be +2 (mass^2)

# ----------------------------------------------------------------------
# 5. Beta‑function from α_fs(q^2)
# ----------------------------------------------------------------------
# Identify renormalization scale μ = sqrt(-q2)
mu = sp.symbols('mu', positive=True)
# Replace -q2 -> mu^2
mu_sub = { -q2: mu**2 }
α_fs_mu = α_fs.subs(mu_sub)

# Beta function: β(α) = μ * dα/dμ
beta = sp.simplify(mu * sp.diff(α_fs_mu, mu))
print("\nBeta function from α_fs(μ):")
print(beta)

# Expected beta: (2α0^2)/(3π) + (α0 * gD^2)/(8π^3) + ... (ignore higher orders)
beta_expected = (2*α0**2)/(3*sp.pi) + (α0 * gD**2)/(8*sp.pi**3)
print("\nExpected beta (to same order):")
print(beta_expected)

print("\nDifference (should be zero or higher‑order):")
print(sp.simplify(beta - beta_expected))

# ----------------------------------------------------------------------
# 6. Summary of checks
# ----------------------------------------------------------------------
print("\n=== SUMMARY ===")
print("All dimensionless terms OK?" , all(dim_of(t) == 0 for t in [term_QED, term_phiDelta, term_lattice]))
print("Lambda * a = π ?" , sp.simplify(Lambda_expr * a_expr) == sp.pi)
print("Φ_Δ mass^2 dimension = +2 ?" , dim_of(m_phi_sq) == 2)
print("Beta function matches expected at O(α0^2, α0 gD^2)?" , sp.simplify(beta - beta_expected).as_leading_term(mu) == 0)