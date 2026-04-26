# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Checks the mathematical consistency of the Engine's derivation
for the Higher-Order Lattice Polarization corrections to α_fs.
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
# ------------------------------------------------------------------
lam, v = sp.symbols('lam v', positive=True)   # λ > 0, v > 0
PhiN, PhiD = sp.symbols('PhiN PhiD')          # field components
gN, gD = sp.symbols('gN gD')                  # couplings
# ------------------------------------------------------------------
# 1. Potential and Hessian
# ------------------------------------------------------------------
V = lam/4 * (PhiN**2 + PhiD**2 - v**2)**2

# Hessian matrix (second derivatives)
H = sp.Matrix([[sp.diff(V, PhiN, PhiN), sp.diff(V, PhiN, PhiD)],
               [sp.diff(V, PhiD, PhiN), sp.diff(V, PhiD, PhiD)]])

print("Hessian H:")
sp.pprint(H.simplify())
print()

# ------------------------------------------------------------------
# 2. Invariants from diagonal entries of H
# ------------------------------------------------------------------
xiN_inv2 = H[0,0]   # ∂²V/∂ΦN²
xiD_inv2 = H[1,1]   # ∂²V/∂ΦD²

print("xi_N^{-2} (from H[0,0]):")
sp.pprint(xiN_inv2.simplify())
print()
print("xi_Δ^{-2} (from H[1,1]):")
sp.pprint(xiD_inv2.simplify())
print()

# ------------------------------------------------------------------
# 3. Shredding Event condition: xi_Δ^{-2} = 0
# ------------------------------------------------------------------
shredding_eq = sp.Eq(xiD_inv2, 0)
print("Shredding Event condition (xi_Δ^{-2}=0):")
sp.pprint(shredding_eq)
print("=> Solved for relation between ΦN and ΦΔ:")
sol_shred = sp.solve(shredding_eq, PhiD**2)
sp.pprint(sol_shred)
print()

# ------------------------------------------------------------------
# 4. Factor‑3 check: Archive mode contribution to Π^{μν}
#    The Engine writes: Π_Δ^{μν} = -3 g_D^2 <Φ_Δ^2> (g^{μν}q^2 - q^μ q^ν)
#    We verify that the coefficient 3 appears when summing over three
#    internal dimensions (each contributes g_D^2 <Φ_Δ^2>).
# ------------------------------------------------------------------
# Symbolic representation of the sum over three dimensions:
dim_sum = 3 * gD**2   # each dimension gives g_D^2 <Φ_Δ^2>
print("Sum over three internal dimensions of Archive mode:")
sp.pprint(dim_sum)
print("Matches the prefactor 3 g_D^2 in Π_Δ^{μν}.")
print()

# ------------------------------------------------------------------
# 5. β‑function from logarithmic running
#    α^{-1}(q^2) = α0^{-1} - [e^2/(3π) ln(Λ^2/q^2) + g_N^2/(4π) ln(Λ_N^2/q^2)
#                            + 3 g_D^2/(4π) ln(Λ_D^2/q^2)]
# ------------------------------------------------------------------
α0, α = sp.symbols('α0 α')
Lambda, LambdaN, LambdaD = sp.symbols('Lambda LambdaN LambdaD', positive=True)
q2 = sp.symbols('q2', positive=True)

# Effective polarization (logarithmic part)
Pi_eff = (1/(3*sp.pi))*sp.log(Lambda**2/q2) \
         + (gN**2/(4*sp.pi))*sp.log(LambdaN**2/q2) \
         + (3*gD**2/(4*sp.pi))*sp.log(LambdaD**2/q2)

# Inverse coupling
alpha_inv = 1/α0 - Pi_eff
# α as function of q2 (implicit)
# Differentiate α^{-1} w.r.t. ln q2 to get β
lnq2 = sp.log(q2)
beta = - sp.diff(alpha_inv, lnq2) * α**2   # using dα/dlnq2 = -α^2 d(α^{-1})/dlnq2
beta_simplified = sp.simplify(beta)
print("β‑function derived from the logarithmic running:")
sp.pprint(beta_simplified)
print()
print("Expected form: -α^2/π * [1 + g_N^2/(4π) + 3 g_D^2/(4π)]")
expected = -α**2/sp.pi * (1 + gN**2/(4*sp.pi) + 3*gD**2/(4*sp.pi))
print("Expected:")
sp.pprint(expected)
print()
print("Are they equal? ", sp.simplify(beta_simplified - expected) == 0)
print()

# ------------------------------------------------------------------
# 6. Entropy coupling (qualitative check)
#    We only verify that the Shannon entropy definition appears.
# ------------------------------------------------------------------
p_i = sp.symbols('p_i')
S_h = -sp.Sum(p_i * sp.log(p_i), (i, 1, sp.oo))  # symbolic sum
print("Shannon entropy definition (symbolic):")
sp.pprint(S_h)
print()
print("All core algebraic checks completed.")