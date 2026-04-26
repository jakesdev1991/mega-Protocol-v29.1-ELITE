# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for the Higher‑Order Lattice Polarization
derivation (Phi_N, Phi_Delta) -> effective fine‑structure constant.

The script checks:
  1. Tensor structure of the vacuum polarisation on an anisotropic lattice.
  2. Ward–Takahashi (gauge) identity.
  3. One‑loop beta‑function consistency.
  4. Dimensionless nature of the effective coupling.

If any check fails, the script exits with a non‑zero status and a
diagnostic message – exactly what the Omega Protocol requires for
a FAIL verdict.
"""

import sys
import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Momentum components
p0, p1, p2, p3 = sp.symbols('p0 p1 p2 p3', real=True)
# Lattice spacing (set to 1 for simplicity – appears only in logs)
a = sp.symbols('a', positive=True)
# Coupling
e = sp.symbols('e', positive=True)
# Phi_N and Phi_Delta (dimensionless)
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# Mass (set to 0 for massless QED UV behaviour)
m = sp.symbols('m', real=True, nonnegative=True)
# External momentum squared
p2_sq = p0**2 + p1**2 + p2**2 + p3**2

# ----------------------------------------------------------------------
# 1. Most general vacuum polarisation tensor allowed by the metric
#    g = diag(1,1,1,1+Phi_Delta)  (Euclidean signature)
# ----------------------------------------------------------------------
# Basis tensors that are symmetric in mu,nu and built from p_mu, p_nu,
# and the preferred direction n_mu = (0,0,0,1) (archive axis).
n = sp.Matrix([0, 0, 0, 1])   # unit vector along archive direction

# Independent scalar structures (parity‑even, Lorentz‑broken to O(4) -> O(3)xZ2)
# We follow the decomposition:
#   Π_μν = A(p^2, p·n) * (δ_μν p^2 - p_μ p_ν)
#        + B(p^2, p·n) * (n_μ n_ν p^2 - (p·n)(n_μ p_ν + n_ν p_μ))
#        + C(p^2, p·n) * (p_μ p_ν - (p·n)^2/(n·n) * n_μ n_ν)
# where A, B, C are scalar functions.
# For an isotropic lattice (Phi_Delta=0) we must have B=C=0 and A=Π(p^2).
# We keep them symbolic to test the Engine's assumption B=C=0.

A, B, C = sp.symbols('A B C', cls=sp.Function)

# Build the tensor
delta = sp.eye(4)  # Kronecker delta in Euclidean indices
Pi_tensor = sp.zeros(4, 4)
for mu in range(4):
    for nu in range(4):
        term1 = A(p2_sq, p0*n[0]+p1*n[1]+p2*n[2]+p3*n[3]) * (delta[mu,nu]*p2_sq - p[mu]*p[nu])
        term2 = B(p2_sq, p0*n[0]+p1*n[1]+p2*n[2]+p3*n[3]) * (
                    n[mu]*n[nu]*p2_sq - (p0*n[0]+p1*n[1]+p2*n[2]+p3*n[3])*(n[mu]*p[nu]+n[nu]*p[mu])
                )
        term3 = C(p2_sq, p0*n[0]+p1*n[1]+p2*n[2]+p3*n[3]) * (
                    p[mu]*p[nu] - (p0*n[0]+p1*n[1]+p2*n[2]+p3*n[3])**2/(n.dot(n)) * n[mu]*n[nu]
                )
        Pi_tensor[mu, nu] = sp.simplify(term1 + term2 + term3)

# Helper: momentum vector as sympy Matrix
p = sp.Matrix([p0, p1, p2, p3])

# ----------------------------------------------------------------------
# Engine's ansatz: assumes B = C = 0 and A = Pi0 + Phi_Delta * PiDelta * (p_z^2/p^2)
# ----------------------------------------------------------------------
# Define the Engine's scalar piece
Pi0 = sp.symbols('Pi0', cls=sp.Function)   # function of p^2 and Phi_N
PiDelta = sp.symbols('PiDelta', cls=sp.Function)  # function of p^2 only

# Engine's effective scalar (isotropic + anisotropic piece)
Pi_engine = Pi0(p2_sq, Phi_N) + Phi_Delta * PiDelta(p2_sq) * (p[2]**2 / p2_sq)  # p_z = p[2]

# Build Engine's tensor using only the transverse structure
Pi_engine_tensor = sp.zeros(4,4)
for mu in range(4):
    for nu in range(4):
        Pi_engine_tensor[mu,nu] = Pi_engine * (delta[mu,nu]*p2_sq - p[mu]*p[nu])

# ----------------------------------------------------------------------
# 2. Ward–Takahashi identity: p_mu Π_μν = 0 (must hold for gauge invariance)
# ----------------------------------------------------------------------
def ward_violation(tensor):
    """Return p_mu * Π_μν as a vector; should be zero."""
    vec = sp.zeros(4,1)
    for nu in range(4):
        comp = 0
        for mu in range(4):
            comp += p[mu] * tensor[mu, nu]
        vec[nu] = sp.simplify(comp)
    return vec

ward_full = ward_violation(Pi_tensor)
ward_engine = ward_violation(Pi_engine_tensor)

# ----------------------------------------------------------------------
# 3. One‑loop beta‑function from Pi0 (isotropic part)
#    In continuum QED: Π_0(p^2) ≈ (e^2/(12π^2)) * log(Λ^2/p^2)  → β(e) = e^3/(12π^2)
#    On the lattice we allow an additive constant proportional to Phi_N.
# ----------------------------------------------------------------------
# Define a simple one‑loop model for Pi0 and PiDelta (just to test structure)
# Pi0 = (e^2/(12π^2))*log(a^{-2}/p^2) + (e^2/π^2)*Phi_N
# PiDelta = (e^2/π^2)*I_Delta(p^2)   (we treat I_Delta as a positive constant for the test)
pi = sp.pi
Log = sp.log
Pi0_model = (e**2/(12*pi**2))*Log(1/(a**2*p2_sq)) + (e**2/pi**2)*Phi_N
# For the test we set I_Delta = 1 (dimensionless O(1) number)
PiDelta_model = (e**2/pi**2) * 1

# Insert into Engine's scalar piece
Pi_engine_model = sp.simplify(Pi0_model + Phi_Delta * PiDelta_model * (p[2]**2 / p2_sq))

# The renormalised coupling: α_eff = α0 / (1 + Π_engine)
alpha0 = sp.symbols('alpha0', positive=True)
alpha_eff_engine = alpha0 / (1 + Pi_engine_model)

# Compute the logarithmic derivative w.r.t. p^2 → gives the beta function
# β(e) = - (e/2) * d ln α_eff / d ln μ^2   (with μ^2 ~ -p^2 in Euclidean)
# For massless QED we expect β(e) = e^3/(12π^2) + O(e^5, Phi_Delta)
beta_engine = sp.simplify(-e/2 * sp.diff(sp.log(alpha_eff_engine), sp.log(p2_sq)))
beta_expected = e**3/(12*pi**2)   # continuum one‑loop result

# ----------------------------------------------------------------------
# 4. Dimensionless check: α_eff must be pure number (no leftover momentum dimension)
# ----------------------------------------------------------------------
dim_check = sp.simplify(alpha_eff_engine / alpha0)  # should be dimensionless
# If any explicit p^2 remains inside a log or similar, it's still dimensionless
# because log of dimensionless ratio; we just verify that there is no leftover
# dimensional factor like p^2 * (something with dimension -2).
# We'll check that the expression contains no positive powers of p^2 outside a log.
def has_dimensionful_pow(expr):
    """Return True if expr contains p^2 raised to a positive power not inside a Log."""
    if expr.is_Atom:
        return False
    if expr.func is sp.Pow:
        base, exp = expr.as_base_exp()
        if base == p2_sq and exp.is_number and exp > 0:
            # check if the whole Pow is inside a Log
            # simple heuristic: if parent is Log, ignore
            parent = expr.parent
            return parent is None or not parent.func is sp.Log
    # recurse
    return any(has_dimensionful_pow(arg) for arg in expr.args)

dim_fail = has_dimensionful_pow(alpha_eff_engine)

# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------
def report(name, condition, details=None):
    if condition:
        print(f"[PASS] {name}")
        return True
    else:
        print(f"[FAIL] {name}")
        if details:
            print(f"    Details: {details}")
        return False

all_pass = True

# Tensor structure: Engine assumes B=C=0 → check if the full tensor allows non‑zero B,C
# We test by substituting random numeric values and seeing if the difference
# between full and Engine tensors can be non‑zero.
all_pass &= report(
    "Tensor structure completeness",
    sp.simplify(Pi_tensor - Pi_engine_tensor).equals(0),
    "Engine's ansatz forces B=C=0; general anisotropic lattice permits B,C ≠ 0."
)

# Ward identity
all_pass &= report(
    "Ward–Takahashi identity (full tensor)",
    ward_full.equals(sp.zeros(4,1)),
    f"Violation vector: {ward_full}"
)
all_pass &= report(
    "Ward–Takahashi identity (Engine ansatz)",
    ward_engine.equals(sp.zeros(4,1)),
    f"Violation vector: {ward_engine}"
)

# Beta‑function
all_pass &= report(
    "One‑loop beta‑function matches continuum QED",
    sp.simplify(beta_engine - beta_expected).equals(0),
    f"Engine beta = {beta_engine}, expected = {beta_expected}"
)

# Dimensionless check
all_pass &= report(
    "Effective coupling dimensionless",
    not dim_fail,
    "Expression contains uncanceled powers of p^2 outside a log."
)

if all_pass:
    print("\n=== OMEGA PROTOCOL VALIDATION: PASS ===")
    sys.exit(0)
else:
    print("\n=== OMEGA PROTOCOL VALIDATION: FAIL ===")
    sys.exit(1)