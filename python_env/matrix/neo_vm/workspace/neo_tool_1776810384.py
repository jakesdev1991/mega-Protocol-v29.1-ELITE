# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Define momentum components (real numbers on the Brillouin zone)
p0, p1, p2, p3 = sp.symbols('p0 p1 p2 p3', real=True)

# Lattice dispersion: sin(p_mu)
sinp = [sp.sin(p0), sp.sin(p1), sp.sin(p2), sp.sin(p3)]

# Denominator of the projector: sum_i sin(p_i)^2
den = sum(s**2 for s in sinp)

# Build the isotropic (transverse) projector P_iso = delta - (sinp_i sinp_j)/den
P_iso = sp.eye(4) - sp.Matrix([[sinp[i]*sinp[j]/den for j in range(4)] for i in range(4)])

# Build the anisotropic (longitudinal) projector P_aniso = (sinp_i sinp_j)/den
P_aniso = sp.Matrix([[sinp[i]*sinp[j]/den for j in range(4)] for i in range(4)])

# Compute the product (should be zero if truly orthogonal)
product = P_iso * P_aniso

# Simplify the matrix
product_simpl = sp.simplify(product)

# Print the product matrix (symbolic)
print("P_iso * P_aniso (symbolic):")
sp.pprint(product_simpl)

# Evaluate at a concrete momentum point, e.g., (π/2, π/3, π/4, π/5)
vals = {p0: sp.pi/2, p1: sp.pi/3, p2: sp.pi/4, p3: sp.pi/5}
product_numeric = product_simpl.subs(vals)
print("\nP_iso * P_aniso at (π/2, π/3, π/4, π/5):")
sp.pprint(product_numeric)

# Compute the commutator [P_iso, P_aniso] = P_iso P_aniso - P_aniso P_iso
commutator = product_simpl - product_simpl.T  # since both are symmetric, commutator = product - product^T
commutator_simpl = sp.simplify(commutator)
print("\nCommutator [P_iso, P_aniso] (symbolic):")
sp.pprint(commutator_simpl)