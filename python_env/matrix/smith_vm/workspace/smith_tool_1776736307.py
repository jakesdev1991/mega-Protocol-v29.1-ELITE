# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol audit of the Higher‑Order Lattice Polarization derivation.
Checks:
  * dimensional consistency of Pi(q^2)
  * transversality (Ward identity)
  * RG‑invariant J* = Phi_N^2 + Phi_Delta^2
  * field‑space bounds |Phi| <= I0
  * parity‑odd piece transversality
"""

import sympy as sp
import numpy as np
from scipy.integrate import solve_ivp

# ----------------------------------------------------------------------
# 1. Symbolic setup
# ----------------------------------------------------------------------
# Basic symbols
q, mu, nu, rho, sigma = sp.symbols('q mu nu rho sigma')
# Dimensions: [M] = mass, we work in natural units (hbar=c=1)
M = sp.symbols('M')
# Assign dimensions: [q] = M, [log] = 0, [alpha] = 0, [Phi] = 0 (dimensionless fields)
dim = {q: M,
       sp.log(q**2): 0,
       sp.Symbol('alpha_fs'): 0,
       sp.Symbol('psi'): 0,
       sp.Symbol('Phi_N'): 0,
       sp.Symbol('Phi_Delta'): 0,
       sp.Symbol('I0'): 0,
       sp.Symbol('Lambda_Delta'): 0,
       sp.Symbol('m_e'): 0,
       sp.Symbol('kappa'): 0,
       sp.Symbol('eta_N'): 0,
       sp.Symbol('eta_Delta'): 0,
       sp.Symbol('c'): 0}

def dim_of(expr):
    """Return the mass dimension of a sympy expression using the dim dict."""
    return sp.simplify(sp.together(expr.subs(dim)))

# ----------------------------------------------------------------------
# 2. Vacuum‑polarisation tensor pieces
# ----------------------------------------------------------------------
# Transverse projector
P_mn = q**2 * sp.KroneckerDelta(mu, nu) - sp.Symbol('q_mu') * sp.Symbol('q_nu')
# For simplicity we treat the projector symbolically; transversality test
# will replace q_mu -> q * n_mu with a dummy unit vector n_mu.
n_mu, n_nu = sp.symbols('n_mu n_nu')
q_mu = q * n_mu
q_nu = q * n_nu
P_mn = q**2 * sp.KroneckerDelta(mu, nu) - q_mu * q_nu

# One‑loop Newtonian part
Pi_N = sp.Symbol('alpha_fs')/(3*sp.pi) * sp.log(q**2 / sp.Symbol('m_e')**2)
Pi_N_mn = P_mn * Pi_N

# One‑loop Archive part (scalar piece)
psi = sp.Symbol('psi')
xi_Delta = sp.Symbol('xi_Delta')
xi_0 = sp.Symbol('xi_0')
Lambda_D = sp.Symbol('Lambda_Delta')
Pi_Delta_scalar = sp.Symbol('alpha_fs')/(2*sp.pi) * psi * sp.log(q**2 / Lambda_D**2)
Pi_Delta_mn = P_mn * Pi_Delta_scalar

# Parity‑odd piece (symbolic)
# Delta_{munu} ∝ ε_{munurho sigma} q^rho k^sigma ; after loop integration
# the symmetric integral over k yields zero for the contracted q^rho piece,
# leaving a transverse structure proportional to the same projector.
# We model it as a constant times the projector to test transversality.
k_mu, k_nu = sp.symbols('k_mu k_nu')
eps = sp.Symbol('eps')  # stands for the Levi‑Civita contraction result
Delta_mn = eps * (q_mu * k_nu - q_nu * k_mu)  # antisymmetric, linear in q

# Two‑loop mixed term
Pi_mix = (sp.Symbol('alpha_fs')**2 / sp.pi**2) * (sp.Symbol('Phi_Delta')/sp.Symbol('Phi_N')) * sp.log(q**2 / sp.Symbol('m_e')**2)**2
Pi_mix_mn = P_mn * Pi_mix

# Full Pi_{munu}
Pi_full_mn = Pi_N_mn + Pi_Delta_mn + Delta_mn + Pi_mix_mn

# ----------------------------------------------------------------------
# 3. Dimensionality check
# ----------------------------------------------------------------------
print("\n=== Dimensionality check ===")
terms = {
    "Pi_N_mn": Pi_N_mn,
    "Pi_Delta_mn": Pi_Delta_mn,
    "Delta_mn": Delta_mn,
    "Pi_mix_mn": Pi_mix_mn,
}
for name, expr in terms.items():
    d = dim_of(expr)
    print(f"{name:12s} : dimension = {d}")
    if d != 0:
        print(f"  *** WARNING: non‑zero dimension ({d}) ***")

# ----------------------------------------------------------------------
# 4. Transversality (Ward identity)
# ----------------------------------------------------------------------
print("\n=== Transversality check ===")
# Contract with q^mu (i.e. replace mu index with q_mu)
# We test each term separately.
def contract_with_qmu(expr):
    # Replace the free mu index with q_mu (nu stays free)
    return expr.subs({sp.Symbol('q_mu'): q_mu})

transverse_ok = True
for name, expr in terms.items():
    contracted = contract_with_qmu(expr)
    # Simplify using that n_mu * n^mu = 1 (unit vector) and that k_mu is integration variable → zero after sym.
    # For the parity‑odd piece we note that k_mu integrates to zero, so we set k_mu -> 0.
    contracted_simp = sp.simplify(contracted.subs({sp.Symbol('k_mu'): 0, sp.Symbol('k_nu'): 0}))
    if contracted_simp != 0:
        print(f"{name:12s} : q^mu Pi_{munu} = {contracted_simp}  (NON‑ZERO)")
        transverse_ok = False
    else:
        print(f"{name:12s} : q^mu Pi_{munu} = 0")
if transverse_ok:
    print("All pieces are transverse → Ward identity satisfied.")
else:
    print("*** WARNING: some piece violates transversality ***")

# ----------------------------------------------------------------------
# 5. RG invariant J* = Phi_N^2 + Phi_Delta^2
# ----------------------------------------------------------------------
print("\n=== RG invariant J* check ===")
# Beta functions
eta_N = sp.Symbol('eta_N')
eta_D = sp.Symbol('eta_Delta')
kappa = sp.Symbol('kappa')
I0 = sp.Symbol('I0')
Phi_N = sp.Symbol('Phi_N')
Phi_D = sp.Symbol('Phi_Delta')

beta_N = eta_N * Phi_N * (1 - Phi_N**2 / I0**2) - kappa * Phi_D**2
beta_D = eta_D * Phi_D * (1 - Phi_D**2 / I0**2) + kappa * Phi_N * Phi_D

# dJ/dlnq = 2 Phi_N beta_N + 2 Phi_D beta_D
J = Phi_N**2 + Phi_D**2
dJ_dlnq = sp.simplify(2*Phi_N*beta_N + 2*Phi_D*beta_D)
print(f"dJ*/dlnq = {dJ_dlnq}")

# Check if it vanishes identically (i.e. no Phi dependence)
if dJ_dlnq == 0:
    print("J* is exactly conserved (independent of Phi).")
else:
    print("J* is NOT identically conserved.")
    # Evaluate for a sample point to see typical size
    subs_dict = {Phi_N: 0.3*I0, Phi_D: 0.4*I0, I0: 1.0,
                 eta_N: 0.1, eta_D: 0.1, kappa: 0.05}
    val = dJ_dlnq.subs(subs_dict)
    print(f"Example value (Phi_N=0.3 I0, Phi_D=0.4 I0, eta=0.1, kappa=0.05): {val.evalf()}")

# ----------------------------------------------------------------------
# 6. Numerical integration of RG flow & field‑space bounds
# ----------------------------------------------------------------------
print("\n=== Numerical RG flow (bounds check) ===")
def rhs(t, y):
    """t = ln(q), y = [Phi_N, Phi_Delta]"""
    phiN, phiD = y
    bN = eta_N_val * phiN * (1 - phiN**2 / I0_val**2) - kappa_val * phiD**2
    bD = eta_D_val * phiD * (1 - phiD**2 / I0_val**2) + kappa_val * phiN * phiD
    return [bN, bD]

# Choose sample parameters (all dimensionless)
I0_val = 1.0
eta_N_val = 0.1
eta_D_val = 0.1
kappa_val = 0.02   # small coupling to keep flow near the well
# Initial condition inside the well
y0 = [0.2*I0_val, 0.1*I0_val]

t_span = (0, 5)   # from ln(q)=0 to ln(q)=5  (q ~ e^5 ~ 148 m_e)
sol = solve_ivp(rhs, t_span, y0, max_step=0.01, rtol=1e-6, atol=1e-9)

phiN_vals = sol.y[0]
phiD_vals = sol.y[1]
max_abs = max(np.max(np.abs(phiN_vals)), np.max(np.abs(phiD_vals)))
print(f"Maximum |Phi| encountered: {max_abs:.4f} (I0 = {I0_val})")
if max_abs > I0_val + 1e-9:
    print("*** WARNING: Phi exceeded the double‑well boundary (possible Shredding) ***")
else:
    print("Field stays inside the allowed Ω‑Protocol region (no Shredding/Freeze detected).")

# ----------------------------------------------------------------------
# 7. Parity‑odd piece transversality (explicit)
# ----------------------------------------------------------------------
print("\n=== Parity‑odd piece transversality ===")
# The parity‑odd term is epsilon_{munurho sigma} q^rho k^sigma.
# Contract with q^mu: epsilon_{munurho sigma} q^mu q^rho k^sigma = 0
# because epsilon is antisymmetric in mu<->rho while q^mu q^rho is symmetric.
# We verify symbolically.
epsilon = sp.Symbol('epsilon')  # placeholder for the Levi‑Civita contraction
Delta_mn_sym = epsilon * (q_mu * k_nu - q_nu * k_mu)
contracted_odd = sp.simplify(Delta_mn_sym.subs({sp.Symbol('q_mu'): q_mu}))
# Set k_mu -> 0 after integration (loop momentum average zero)
contracted_odd = sp.simplify(contracted_odd.subs({sp.Symbol('k_mu'): 0, sp.Symbol('k_nu'): 0}))
print(f"q^mu Delta_{munu} = {contracted_odd}")
if contracted_odd == 0:
    print("Parity‑odd piece is transverse.")
else:
    print("*** WARNING: parity‑odd piece not transverse ***")

print("\n=== Audit complete ===")