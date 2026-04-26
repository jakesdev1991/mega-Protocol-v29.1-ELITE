# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation Script – Agent Smith
# --------------------------------------------------------------
# Purpose:  Verify that the Higher-Order Lattice Polarization
#           derivation respects:
#           (a) correct angular structure at O(e^2, Phi_Delta)
#           (b) presence of Omega invariants psi, xi_N, xi_Delta
# --------------------------------------------------------------

import sympy as sp
import numpy as np

# ------------------------------------------------------------------
# 1. Symbols and basic definitions
# ------------------------------------------------------------------
# lattice momenta
k0, k1, k2, k3 = sp.symbols('k0 k1 k2 k3', real=True)
p0, p1, p2, p3 = sp.symbols('p0 p1 p2 p3', real=True)
# archive direction n_mu = (0,0,0,1)
n = sp.Matrix([0, 0, 0, 1])

# metric deformation (only enters via Phi_Delta in propagator)
Phi_Delta = sp.symbols('Phi_Delta', real=True)
# fermion mass
m = sp.symbols('m', real=True, positive=True)
# coupling
e = sp.symbols('e', real=True, positive=True)

# Euclidean gamma matrices (we only need trace identities)
# Use sympy's Pauli-like representation for trace:
#   Tr[gamma_mu gamma_nu] = 4*delta_mu_nu
#   Tr[gamma_mu gamma_nu gamma_rho gamma_sigma] = 4*(delta_mu_nu*delta_rho_sigma
#                                                    -delta_mu_rho*delta_nu_sigma
#                                                    +delta_mu_sigma*delta_nu_rho)
def delta(a,b):
    return 1 if a==b else 0

# ------------------------------------------------------------------
# 2. One-loop vacuum polarization tensor (isotropic part)
# ------------------------------------------------------------------
# Define sine lattice momenta
sin = lambda idx: sp.sin(idx)  # placeholder; actual integration later
# For the trace we keep the full structure:
#   Tr[gamma_mu (i gamma·sin k + m) gamma_nu (i gamma·sin(k-p) + m)]
# Using trace identities:
def trace_one_loop(mu, nu):
    # i gamma·sin k -> i * sum_rho gamma_rho * sin k_rho
    # We'll compute the trace analytically:
    term = (
        4 * (sp.KroneckerDelta(mu, nu) * (
                sum(sp.sin(k[r]) * sp.sin((k[r] - p[r])) for r in range(4)) - m**2)
             - sp.sin(k[mu]) * sp.sin((k[nu] - p[nu]))
             - sp.sin((k[mu] - p[mu])) * sp.sin(k[nu])
    )
    return sp.simplify(term)

# ------------------------------------------------------------------
# 3. Anisotropic correction from Phi_Delta (linear order)
# ------------------------------------------------------------------
# The correction to the propagator is:
#   delta S_F = - S_F * (i Phi_Delta/2 gamma_z sin k_z) * S_F
# This inserts an extra factor (i Phi_Delta/2) gamma_z sin k_z between
# the two fermion lines in the loop.
# The resulting trace (still to be integrated) is:
def anisotropic_trace(mu, nu):
    # Start from the isotropic trace and insert the extra gamma_z sin k_z
    # between the two propagators. Using trace cyclic property we get:
    # Tr[gamma_mu S_F gamma_nu S_F (i Phi_Delta/2) gamma_z sin k_z]
    # = (i Phi_Delta/2) * Tr[gamma_mu (i gamma·sin k + m) gamma_nu
    #                         (i gamma·sin(k-p) + m) gamma_z] * sin k_z
    # We evaluate the trace with an extra gamma_z at the end.
    term = (
        4 * (
            sp.KroneckerDelta(mu, nu) * (
                sum(sp.sin(k[r]) * sp.sin((k[r] - p[r])) for r in range(4)) * sp.sin(k[2])  # gamma_z index=2
                - m**2 * sp.sin(k[2])
            )
            - sp.sin(k[mu]) * sp.sin((k[nu] - p[nu])) * sp.sin(k[2])
            - sp.sin((k[mu] - p[mu])) * sp.sin(k[nu]) * sp.sin(k[2])
            + sp.sin(k[mu]) * sp.sin(k[nu]) * sp.sin((k[2] - p[2]))  # from moving gamma_z inside
            - sp.sin((k[mu] - p[mu])) * sp.sin((k[nu] - p[nu])) * sp.sin(k[2])
        )
    )
    return sp.simplify(term * sp.I * Phi_Delta / 2)

# ------------------------------------------------------------------
# 4. Check angular dependence after Brillouin‑zone integration
# ------------------------------------------------------------------
# We cannot perform the full BZ integral symbolically, but we can
# inspect the integrand's dependence on the external angle.
# Define external momentum direction:
#   p = |p| (sinθ cosφ, sinθ sinφ, cosθ)  (we only need θ dependence)
# For simplicity, set p0 = p1 = p2 = 0, p3 = |p| (along archive)
# and later rotate to see theta dependence.
# Here we set p = (0,0,0,|p|) and later contract with a test vector
# orthogonal to n to generate sin^2θ terms.
p_mag = sp.symbols('p_mag', real=True, positive=True)
p_vec = sp.Matrix([0,0,0,p_mag])

# Choose a polarisation vector epsilon orthogonal to n, e.g. epsilon = (1,0,0,0)
eps = sp.Matrix([1,0,0,0])

# Build the contraction epsilon_mu epsilon_nu * anisotropic_trace
contract = 0
for mu in range(4):
    for nu in range(4):
        contract += eps[mu] * eps[nu] * anisotropic_trace(mu, nu)

# Simplify and see if we get a term proportional to (1 - 3 cos^2θ)
# For p along z, cosθ = p_z/|p| = 1, sinθ = 0.
# To expose angular dependence we replace p_mag by p_mag * sp.sin(theta)
# and p_z by p_mag * sp.cos(theta) and keep theta symbolic.
theta = sp.symbols('theta', real=True)
p_vec_theta = sp.Matrix([0,0,0,p_mag*sp.cos(theta)])  # only z component varies
# Recompute contract with this p_vec (need to replace p in anisotropic_trace)
# For brevity we substitute p[3] = p_mag*sp.cos(theta) in the expression:
contract_theta = contract.subs({p[3]: p_mag*sp.cos(theta)})

# Expand in powers of sin(theta) and cos(theta)
expr = sp.simplify(sp.expand(contract_theta))
print("Anisotropic trace contraction (symbolic):")
print(expr)
print("\n--- Checking for Legendre P2(cosθ) structure ---")
# P2(cosθ) = (3*cos^2θ - 1)/2
P2 = (3*sp.cos(theta)**2 - 1)/2
# See if expr can be written as A * P2 + B (where B is isotropic part)
coeff_P2 = sp.Poly(expr, sp.cos(theta)).coeff_monomial(sp.cos(theta)**2)
coeff_const = sp.Poly(expr, sp.cos(theta)).coeff_monomial(1)
print(f"Coefficient of cos^2θ : {coeff_P2}")
print(f"Constant term        : {coeff_const}")
# If coeff_P2 != 0 we have angular dependence.
has_angular = sp.simplify(coeff_P2) != 0
print(f"Angular dependence present? {has_angular}")

# ------------------------------------------------------------------
# 5. Effective coupling formula – check for Omega invariants
# ------------------------------------------------------------------
# The claimed formula:
#   alpha_eff^i = alpha0 / (1 + Pi_T + delta_{i,z} Phi_Delta [Pi_L + 2 Pi_M] + O(e^6))
# We will construct a symbolic expression and search for psi, xi_N, xi_Delta.
alpha0, Pi_T, Pi_L, Pi_M = sp.symbols('alpha0 Pi_T Pi_L Pi_M', real=True)
i, z = sp.symbols('i z', integer=True)
delta_i_z = sp.KroneckerDelta(i, z)  # 1 if i==z else 0
alpha_eff = alpha0 / (1 + Pi_T + delta_i_z * Phi_Delta * (Pi_L + 2*Pi_M) + sp.O(e**6))

# Define Omega invariants
psi   = sp.symbols('psi', real=True)
xi_N  = sp.symbols('xi_N', real=True)
xi_D  = sp.symbols('xi_Delta', real=True)

# Look for their presence in the expression (they should appear via
# Pi_T, Pi_L, Pi_M if the derivation is Omega‑compliant).
expr_str = str(alpha_eff)
has_psi   = 'psi'   in expr_str
has_xiN   = 'xi_N'  in expr_str
has_xiD   = 'xi_Delta' in expr_str

print("\n--- Omega invariant check ---")
print(f"Expression contains psi?   {has_psi}")
print(f"Expression contains xi_N?  {has_xiN}")
print(f"Expression contains xi_Delta? {has_xiD}")

# ------------------------------------------------------------------
# 6. Verdict
# ------------------------------------------------------------------
print("\n=== VALIDATION RESULT ===")
if not has_angular:
    print("FAIL: One-loop anisotropic kernel lost angular dependence.")
elif not (has_psi and has_xiN and has_xiD):
    print("FAIL: Missing Omega Protocol invariants (psi, xi_N, xi_Delta).")
else:
    print("PASS: Angular structure present and Omega invariants detected.")
    print("Note: Two-loop prefactor still needs explicit derivation.")
# --------------------------------------------------------------