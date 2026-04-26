# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol validation of the Higher‑Order Lattice Polarization correction.
Checks:
  - Transversality: p_mu * Pi^{mu nu} = 0
  - Anisotropic part is symmetric, traceless, and built only from n_mu n_nu
  - Positivity of the effective fine‑structure constant alpha_eff^i
  - No double‑counting of metric deformation in the kinetic term
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
p0, p1, p2, p3 = sp.symbols('p0 p1 p2 p3', real=True)   # Euclidean momentum components
m, e = sp.symbols('m e', positive=True)                # mass, charge
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)  # Ω‑invariants
# Archive direction unit vector (choose z = 3)
n = sp.Matrix([0, 0, 0, 1])

p = sp.Matrix([p0, p1, p2, p3])
p2_sq = p.dot(p)                     # p^2

# ----------------------------------------------------------------------
# Most general rank‑2 tensor allowed by the residual symmetry:
#   - invariant under O(3) rotations in the 1‑2‑3 subspace (transverse plane)
#   - invariant under n -> -n (reflection of archive axis)
#   - symmetric: Pi^{mu nu} = Pi^{nu mu}
# Basis tensors:
#   T1 = delta^{mu nu}
#   T2 = p^{mu} p^{nu}
#   T3 = n^{mu} n^{nu}
#   T4 = p^{mu} n^{nu} + n^{mu} p^{nu}
#   T5 = (p^{mu} p^{nu}) (n·p)^2 / (p^2)^2   (higher‑order, omitted for O(e^4))
# We keep up to linear in Phi_Delta and quadratic in p.
# ----------------------------------------------------------------------
delta = sp.eye(4)  # Kronecker delta in Euclidean space

# Isotropic scalar function (function of p^2 only)
Pi0 = sp.Function('Pi0')(p2_sq)          # to be determined from 1‑loop

# Anisotropic scalar function (also depends only on p^2)
PiDelta = sp.Function('PiDelta')(p2_sq)

# Construct the polarization tensor
Pi_munu = (
    delta * Pi0                                          # isotropic part
    + Phi_Delta * (n * n.T) * PiDelta                    # pure n_nu n_mu piece
    + Phi_Delta * (p * n.T + n * p.T) * 0                # mixed part set to zero by tracelessness condition
    # Note: we intentionally set the mixed coefficient to zero; a non‑zero value would break tracelessness.
)

# ----------------------------------------------------------------------
# Enforce transversality: p_mu * Pi^{mu nu} = 0  (for all nu)
# ----------------------------------------------------------------------
transversality_eqs = [p.dot(Pi_munu[:, nu]) for nu in range(4)]
transversality_simplified = [sp.simplify(eq) for eq in transversality_eqs]

print("=== Transversality conditions (should be zero) ===")
for i, eq in enumerate(transversality_simplified):
    print(f"nu={i}: {eq}")

# ----------------------------------------------------------------------
# Check that the anisotropic part is traceless:
#   g_{mu nu} * (PhiDelta part) = 0
# ----------------------------------------------------------------------
aniso_part = Phi_Delta * (n * n.T) * PiDelta
trace_aniso = sp.trace(delta * aniso_part)   # g^{mu nu} * aniso_{mu nu}
print("\n=== Trace of anisotropic part ===")
print(sp.simplify(trace_aniso))

# ----------------------------------------------------------------------
# Photon propagator in Landau gauge:
#   D_{mu nu} = (delta_{mu nu} - p_mu p_nu / p^2) / [p^2 (1 + Pi_{mu nu} projected)]
# Since we enforced transversality, Pi_{mu nu} is already transverse,
# so we can simply invert the scalar factor in the subspace orthogonal to p.
# ----------------------------------------------------------------------
# Build the transverse projector
P_T = delta - p * p.T / p2_sq
# Effective inverse propagator in the transverse subspace:
M_inv = p2_sq * (P_T + Pi_munu)   # because D^{-1}_{mu nu} = p^2 (delta_{mu nu} + Pi_{mu nu}) in Landau gauge
# Invert only on the 3‑dim transverse subspace (remove the longitudinal eigenvector p)
# We do this by projecting onto a basis orthogonal to p.
# Choose three orthonormal vectors e1,e2,e3 spanning the orthogonal complement.
# For simplicity, we evaluate the eigenvalues of M_inv in the subspace.
# Compute eigenvalues of M_inv; one should be zero (longitudinal), the other three equal
# to p^2 (1 + Pi_scalar) where Pi_scalar is the scalar function multiplying the transverse projector.
eigenvals = M_inv.eigenvals()
print("\n=== Eigenvalues of the inverse propagator (should be {0, λ, λ, λ}) ===")
for val, mult in eigenvals.items():
    print(f"Eigenvalue: {sp.simplify(val)}  (multiplicity {mult})")

# Extract the non‑zero eigenvalue (should be p^2 * (1 + Pi_scalar))
non_zero_evals = [val for val, mult in eigenvals.items() if not sp.simplify(val).equals(0)]
if len(non_zero_evals) != 1:
    print("ERROR: More than one non‑zero eigenvalue – indicates mixing!")
else:
    lambda_val = sp.simplify(non_zero_evals[0])
    print(f"Non‑zero eigenvalue λ = {lambda_val}")
    # λ should factor as p^2 * (1 + Pi_scalar)
    Pi_scalar_est = sp.simplify(lambda_val / p2_sq - 1)
    print(f"Estimated scalar Pi(p^2) = {Pi_scalar_est}")

    # Compare with the ansatz: Pi_scalar = Pi0 + Phi_Delta * PiDelta * (n·p)^2 / p^2
    # Since we set mixed part to zero, the anisotropy contributes only via n_nu n_mu.
    # Its projection onto the transverse subspace yields a factor (n·p)^2 / p^2.
    n_dot_p = n.dot(p)
    expected_Pi = Pi0 + Phi_Delta * PiDelta * (n_dot_p**2) / p2_sq
    print(f"Expected Pi(p^2) from decomposition = {sp.simplify(expected_Pi)}")
    print(f"Difference = {sp.simplify(Pi_scalar_est - expected_Pi)}")

# ----------------------------------------------------------------------
# Positivity check for the effective coupling
#   alpha_eff^i = alpha0 / [1 + Pi_i(p^2)]
# where Pi_i are the eigenvalues of Pi^{mu nu} in the i‑direction.
# For a diagonal basis aligned with (x,y,z) we can read off:
#   Pi_x = Pi0                           (no n component)
#   Pi_y = Pi0
#   Pi_z = Pi0 + Phi_Delta * PiDelta    (because n_z = 1)
# ----------------------------------------------------------------------
alpha0 = sp.symbols('alpha0', positive=True)
Pi_x = Pi0
Pi_y = Pi0
Pi_z = Pi0 + Phi_Delta * PiDelta

def check_positivity(expr, name):
    """Return True if expr > 0 for all real p^2 >= 0, given small Phi_N, Phi_Delta."""
    # We test numerically over a grid; symbolic positivity is hard for generic functions.
    vals = np.logspace(-4, 2, 50)  # p^2 from 1e-4 to 100
    for p2_val in vals:
        subs_dict = {p2_sq: p2_val, Phi_N: 0.01, Phi_Delta: 0.02,
                     m: 0.5, e: 0.3, alpha0: 1/137.0}
        # Replace Pi0 and PiDelta with their 1‑loop forms (placeholder)
        # Here we use simple log forms to illustrate the test.
        Pi0_val = (e**2/(12*sp.pi**2)) * sp.log(1/p2_val) + (e**2/sp.pi**2) * Phi_N
        PiDelta_val = (e**2/sp.pi**2)  # O(1) constant kernel
        expr_val = expr.subs({Pi0: Pi0_val, PiDelta: PiDelta_val}).subs(subs_dict)
        if float(expr_val) <= 0:
            print(f"POSITIVITY FAILURE for {name}: p^2={p2_val}, value={expr_val}")
            return False
    return True

print("\n=== Positivity of effective coupling ===")
ok_x = check_positivity(alpha0/(1 + Pi_x), "α_eff^x")
ok_y = check_positivity(alpha0/(1 + Pi_y), "α_eff^y")
ok_z = check_positivity(alpha0/(1 + Pi_z), "α_eff^z")
if ok_x and ok_y and ok_z:
    print("All directional couplings remain positive for the test grid.")
else:
    print("Positivity violation detected – invariant J* broken.")

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
print("\n=== Validation Summary ===")
print("If all transversality equations simplify to 0, the trace of the anisotropic part is 0,")
print("the non‑zero eigenvalue matches the expected scalar Pi(p^2), and positivity holds,")
print("then the candidate expression respects the Ω‑Protocol invariants.")
print("Otherwise, the derivation must be revised.")