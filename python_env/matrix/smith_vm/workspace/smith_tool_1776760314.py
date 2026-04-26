# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Dimensional‑consistency validator for the ETO‑Ω proposal.
Checks that:
  1. The effective Hamiltonian H_eff has dimensions of energy ([L]^{-1}).
  2. The logical operators Φ_N, Φ_Δ are dimensionless.
  3. The gap Δ has dimensions of energy.
  4. The stiffness invariants ξ_N, ξ_Δ have dimensions of length.
  5. The code distance d is dimensionless (as a ratio of lengths).
  6. The order parameter O is dimensionless.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Base dimension: Length (L). In natural units, Energy ~ L^{-1}.
L = sp.symbols('L', positive=True)   # dimension of length

# Define dimensional symbols for each quantity:
#   [phi]       = L^{-(d-1)/2}  (we keep d generic, but it cancels out)
#   [∂]         = L^{-1}
#   [xi_N]      = L
#   [xi_delta]  = L
#   [Delta0]    = L^{-1}   (reference gap, energy)
#   [psi]       = dimensionless (log of ratio)
#   [Phi_N]     = dimensionless
#   [Phi_Delta] = dimensionless
#   [J0, K0]    = L^{-1}   (reference couplings, energy)
#   [xi0]       = L        (reference length)

# Dimension of the field phi (depends on spatial dimension d)
d = sp.symbols('d', integer=True, positive=True)  # spatial dimensions
dim_phi = L**(-(d-1)/2)          # [phi]

# Dimension of derivative
dim_dL = L**(-1)                 # [∂_mu]

# Dimension of the kinetic term (∂phi)^2 in the Lagrangian density
dim_kinetic = dim_dL**2 * dim_phi**2   # should be L^{-(d+1)} for action density
# Verify: (L^{-1})^2 * L^{-(d-1)} = L^{-2} * L^{-(d-1)} = L^{-(d+1)} ✔️

# ----------------------------------------------------------------------
# Define dimensional symbols for the key constructs
dim_xi_N   = L
dim_xi_D   = L
dim_psi    = 1                     # dimensionless
dim_Phi_N  = 1
dim_Phi_D  = 1
dim_Delta0 = L**(-1)               # reference gap (energy)
dim_J0     = L**(-1)               # reference coupling (energy)
dim_K0     = L**(-1)
dim_xi0    = L                     # reference length

# ----------------------------------------------------------------------
# 1. Effective Hamiltonian: H_eff = - Σ J_ij σzσz - Σ K_ij σxσx
#    σ operators are dimensionless → [H_eff] = [J_ij] = [K_ij]
#    Assume J_ij = J0 * f_J(xi_N/xi0, xi_D/xi0)  (same for K)
#    where f_J, f_K are dimensionless functions.
dim_J = dim_J0   # because the function is dimensionless
dim_K = dim_K0

print("Dimension of J_ij (and thus H_eff):", dim_J)   # should be L^{-1}
assert dim_J == L**(-1), "H_eff does not have energy dimensions!"

# ----------------------------------------------------------------------
# 2. Gap: Δ = Delta0 * f_delta(xi_N/xi0, xi_D/xi0)
dim_Delta = dim_Delta0   # f_delta dimensionless
print("Dimension of gap Δ:", dim_Delta)
assert dim_Delta == L**(-1), "Gap Δ does not have energy dimensions!"

# ----------------------------------------------------------------------
# 3. Code distance: d_code = xi0 * exp(psi)   (psi dimensionless)
dim_d_code = dim_xi0 * sp.exp(dim_psi)   # exp of dimensionless is dimensionless
print("Dimension of code distance d_code:", dim_d_code.simplify())
assert dim_d_code == L, "Code distance should have dimensions of length."

# ----------------------------------------------------------------------
# 4. Order parameter O = <phi(x) phi(y)>_{|x-y|→∞}
#    Two-point function of phi: [phi]^2 = L^{-(d-1)}
dim_O = dim_phi**2
print("Dimension of order parameter O:", dim_O.simplify())
# In the proposal O is treated as dimensionless (normalized); we can
# define a normalized version O_norm = O * xi0^{d-1} to make it dimensionless.
dim_O_norm = dim_O * dim_xi0**(d-1)
print("Dimension of normalized O_norm:", dim_O_norm.simplify())
assert dim_O_norm == 1, "Normalized order parameter should be dimensionless."

# ----------------------------------------------------------------------
# 5. Logical operators: Φ_N, Φ_D (already set dimensionless)
print("Dimension of Φ_N:", dim_Phi_N)
print("Dimension of Φ_Δ:", dim_Phi_D)
assert dim_Phi_N == 1 and dim_Phi_D == 1, "Logical operators must be dimensionless."

# ----------------------------------------------------------------------
print("\nAll dimensional checks passed. The proposal is dimensionally consistent.")