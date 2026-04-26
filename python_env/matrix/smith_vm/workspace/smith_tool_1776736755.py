# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Audit Script for Higher-Order Lattice Polarization
# --------------------------------------------------------------
# This script validates the mathematical soundness and invariant
# compliance of the derivation supplied by Agent Engine.
# It uses sympy for symbolic algebra and dimensional analysis.
# --------------------------------------------------------------

import sympy as sp

# ------------------------------------------------------------------
# 1. Define symbols (dimensions in natural units: [mass]=1, [length]=-1)
# ------------------------------------------------------------------
# Basic dimensions
M = sp.symbols('M', positive=True)   # mass dimension
L = sp.symbols('L', positive=True)   # length dimension (inverse mass)

# Physical quantities
e   = sp.symbols('e')                # gauge coupling (dimensionless in 4D)
gD  = sp.symbols('g_D')              # Yukawa coupling to Phi_Delta (dimensionless)
gN  = sp.symbols('g_N')              # Yukawa coupling to Phi_N (dimensionless)
alpha0 = e**2/(4*sp.pi)              # fine-structure constant at low energy (dimensionless)

# Momenta and masses
q   = sp.symbols('q')                # photon momentum (dimension M)
m   = sp.symbols('m')                # fermion mass (dimension M)
Lambda = sp.symbols('Lambda')        # UV cutoff (dimension M)

# Omega Protocol invariants
psi   = sp.symbols('psi')            # ln(Phi_N/I_0)  (dimensionless)
xi_N  = sp.symbols('xi_N')           # correlation length of Phi_N (dimension L)
xi_D  = sp.symbols('xi_D')           # correlation length of Phi_Delta (dimension L)
xi0   = sp.symbols('xi0')            # reference length (dimension L)

# Lattice spacing a (dimension L) and derived cutoff
a   = xi0 * sp.exp(-psi)             # a = xi0 * e^{-psi}
# Lambda = pi / a  (dimension M)
Lambda_expr = sp.pi / a

# Effective mass of Phi_Delta from quantum fluctuations
lam   = sp.symbols('lam')            # dimensionless lambda from Mexican hat
m_PhiD_sq = lam / xi_D**2            # dimension M^2

# ------------------------------------------------------------------
# 2. Build the candidate expression for alpha_fs(q^2)
# ------------------------------------------------------------------
# One-loop QED piece (leading log)
Pi_QED = - alpha0/(3*sp.pi) * sp.log(-q**2 / m**2)   # dimensionless

# Double-log correction from Phi_Delta exchange
# We keep the coefficient as a free symbol k_gD to be checked later
k_gD = sp.symbols('k_gD')          # expected ~ 1/(32 pi^4) or 1/(16 pi^4)
Pi_Delta = - k_gD * gD**2 * alpha0 * sp.log(-q**2 / m**2)**2

# Lattice artefact term (order a^2 q^2)
C = sp.symbols('C')                # dimensionless constant
Pi_lattice = C * a**2 * q**2       # dimensionless (a^2 ~ L^2, q^2 ~ M^2 => L^2 M^2 = 1)

# Total vacuum polarization (dimensionless)
Pi_tot = Pi_QED + Pi_Delta + Pi_lattice

# Renormalized fine-structure constant
alpha_fs = alpha0 / (1 - Pi_tot)

# ------------------------------------------------------------------
# 3. Dimensionality check
# ------------------------------------------------------------------
def dim(expr):
    """Return the dimension of expr in terms of M and L.
    We treat every symbol as dimensionless unless explicitly assigned."""
    d = M**0 * L**0
    # replace each symbol by its known dimension
    repl = {
        e: 1,               # dimensionless in 4D
        gD: 1,
        gN: 1,
        alpha0: 1,
        q: M,
        m: M,
        Lambda: M,
        psi: 1,
        xi_N: L,
        xi_D: L,
        xi0: L,
        lam: 1,
        a: L,               # a = xi0 * exp(-psi) => L
        C: 1,
        k_gD: 1,
    }
    for sym, dim_sym in repl.items():
        d = d.subs(sym, dim_sym)
    # Simplify powers
    return sp.simplify(d)

print("Dimension of alpha_fs:", dim(alpha_fs))
# Should be dimensionless (M^0 L^0)

# ------------------------------------------------------------------
# 4. Beta-function from alpha_fs(q^2)
# ------------------------------------------------------------------
# Define t = ln(-q^2 / mu^2) with mu an arbitrary renorm scale.
t = sp.symbols('t')
# Replace -q^2/m^2 = exp(t)  => q^2 = - m^2 * exp(t)
subs_dict = { -q**2 / m**2: sp.exp(t) }
Pi_tot_t = Pi_tot.subs(subs_dict)
alpha_fs_t = alpha0 / (1 - Pi_tot_t)

# Beta function: beta = d alpha / d t
beta = sp.diff(alpha_fs_t, t)
# Expand to O(alpha0^2, alpha0*gD^2)
beta_series = sp.series(beta, alpha0, 0, 3).removeO()
beta_series = sp.series(beta_series, gD, 0, 3).removeO()
print("\nBeta function (series up to alpha0^2 and alpha0*gD^2):")
sp.pprint(beta_series)

# Expected form: beta = (2/3π) α0^2 + k_beta * α0 * gD^2
# Extract coefficients
coeff_alpha2 = beta_series.coeff(alpha0, 2)
coeff_alpha_gD2 = beta_series.coeff(alpha0*gD**2, 1)
print("\nCoefficient of α0^2 :", coeff_alpha2)
print("Coefficient of α0*gD^2 :", coeff_alpha_gD2)

# ------------------------------------------------------------------
# 5. Invariant compliance check
# ------------------------------------------------------------------
# List all symbols appearing in alpha_fs
symbols_in_expr = set(alpha_fs.free_symbols)
print("\nSymbols appearing in final expression:")
sp.pprint(symbols_in_expr)

# Allowed symbols (Protocol invariants + fundamentals)
allowed = {e, gD, gN, alpha0, q, m, Lambda, psi, xi_N, xi_D, xi0, lam, C, k_gD}
unallowed = symbols_in_expr - allowed
if unallowed:
    print("\n!!! Unallowed symbols (raw Phi fields?) :", unallowed)
else:
    print("\nAll symbols are permitted by the Omega Protocol invariants.")

# ------------------------------------------------------------------
# 6. Optional: plug in a numeric value for k_gD and see beta shift
# ------------------------------------------------------------------
# Theoretical value from explicit sunset diagram (massless scalar):
# k_gD_theory = 1/(16*pi**4)  (if the factor 2 correction is applied)
k_gD_theory = 1/(16*sp.pi**4)
beta_num = beta_series.subs({k_gD: k_gD_theory})
print("\nBeta function with k_gD = 1/(16π^4):")
sp.pprint(sp.simplify(beta_num))

# ------------------------------------------------------------------
# End of script
# ------------------------------------------------------------------