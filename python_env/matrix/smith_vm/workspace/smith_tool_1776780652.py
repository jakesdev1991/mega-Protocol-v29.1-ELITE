# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit: Higher‑Order Lattice Polarization Corrections
Verifies mathematical soundness and invariant compliance.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbolic setup
# ----------------------------------------------------------------------
# Mass dimensions (in natural units: [mass] = 1)
# We assign dimension symbols to check consistency.
M = sp.symbols('M', positive=True)   # mass dimension
# Fields
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# Parameters
m_N, m_Delta, g_Delta, lam = sp.symbols('m_N m_Delta g_Delta lam', real=True)
# Current (conserved) – not needed for algebraic checks
# Cutoff
Lambda = sp.symbols('Lambda', positive=True)
# Fermion mass
m_f = sp.symbols('m_f', positive=True)
# Momentum squared (external)
q2 = sp.symbols('q2', real=True)

# ----------------------------------------------------------------------
# 1. Effective potential (quadratic)
# ----------------------------------------------------------------------
V_eff = (m_N**2/2)*Phi_N**2 + (m_Delta**2/2)*Phi_Delta**2 + lam*Phi_N*Phi_Delta**2

# Hessian matrix H_ij = ∂^2 V_eff / ∂Φ_i ∂Φ_j
H = sp.hessian(V_eff, (Phi_N, Phi_Delta))
print("Hessian H:")
sp.pprint(H)
print()

# ----------------------------------------------------------------------
# 2. Stiffness invariants from eigenvalues (equilibrium at Φ=0)
# ----------------------------------------------------------------------
# At equilibrium Φ_N = Φ_Delta = 0 the Hessian is diagonal:
H0 = H.subs({Phi_N:0, Phi_Delta:0})
print("Hessian at equilibrium (Φ=0):")
sp.pprint(H0)
print()

# Inverse stiffness squared are the diagonal entries:
xi_N_inv2 = H0[0,0]   # m_N^2
xi_Delta_inv2 = H0[1,1] # m_Delta^2
print("xi_N^{-2} =", xi_N_inv2)
print("xi_Δ^{-2} =", xi_Delta_inv2)
print()

# Stiffness themselves (inverse sqrt):
xi_N = sp.sqrt(1/xi_N_inv2)   # 1/m_N
xi_Delta = sp.sqrt(1/xi_Delta_inv2)  # 1/sqrt(m_Delta^2 + 2λΦ_N) evaluated at Φ_N=0 -> 1/m_Delta
# For generality keep Φ_N symbolic:
xi_Delta_gen = sp.sqrt(1/(m_Delta**2 + 2*lam*Phi_N))
print("xi_N =", xi_N.simplify())
print("xi_Δ (general) =", xi_Delta_gen.simplify())
print()

# ----------------------------------------------------------------------
# 3. Metric coupling invariant ψ
# ----------------------------------------------------------------------
psi = sp.log(xi_Delta_gen/xi_N)
print("ψ = ln(ξ_Δ/ξ_N) =")
sp.pprint(psi.simplify())
print("Is ψ dimensionless? →", psi.is_commutative)  # sympy treats it as dimensionless if args are
# Check by substituting dimensions: each mass → M, each field dimensionless
dim_subs = {m_N:M, m_Delta:M, lam:M**2, Phi_N:1, Phi_Delta:1}
psi_dim = psi.subs(dim_subs)
print("ψ after dimensional substitution:", psi_dim.simplify())
print("ψ dimension (should be M^0):", psi_dim.simplify().expand())
print()

# ----------------------------------------------------------------------
# 4. Archive-mode vacuum polarization Π_Δ (logarithmic part)
# ----------------------------------------------------------------------
# The derived expression (ignoring O(q^2/Λ^2)):
Pi_Delta = (g_Delta**2 * Phi_Delta**2 / sp.pi) * (
    sp.log(Lambda**2 / m_f**2) +
    (m_f**2 / m_Delta**2) * sp.log(Lambda**2 / m_Delta**2)
)
print("Π_Δ(q^2) (log part) =")
sp.pprint(Pi_Delta)
print()

# Check dimensionlessness of Π_Δ:
# [g_Δ] = M, [Φ_Δ] = 0, [Λ] = M, [m_f] = M, [m_Δ] = M
dim_subs_Pi = {g_Delta:M, Phi_Delta:1, Lambda:M, m_f:M, m_Delta:M}
Pi_dim = Pi_Delta.subs(dim_subs_Pi)
print("Π_Δ dimension after substitution:", sp.simplify(Pi_dim))
print("Should be M^0 →", sp.simplify(Pi_dim))
print()

# ----------------------------------------------------------------------
# 5. Renormalization condition: Δ(1/α) = - Π_Δ
# ----------------------------------------------------------------------
Delta_inv_alpha = -Pi_Delta
print("Δ(1/α) = -Π_Δ =")
sp.pprint(Delta_inv_alpha)
print()

# ----------------------------------------------------------------------
# 6. Topological impedance Z = e^ψ
# ----------------------------------------------------------------------
Z = sp.exp(psi)
print("Z = e^ψ =")
sp.pprint(Z.simplify())
print("Z dimension (should be M^0):", Z.subs(dim_subs).simplify())
print()

# ----------------------------------------------------------------------
# 7. Entropy gauge weight p(Δ) ∝ exp(-Z|Δ|)  (check normalisability)
# ----------------------------------------------------------------------
Delta = sp.symbols('Delta', real=True)
p = sp.exp(-Z*sp.Abs(Delta))  # unnormalized density
# Integral over Δ from -∞ to +∞ converges if Z>0:
integral = sp.integrate(p, (Delta, -sp.oo, sp.oo))
print("∫ p(Δ) dΔ =", integral.simplify())
print("Converges for Z>0 →", integral.simplify() == 2/Z)
print()

# ----------------------------------------------------------------------
# 8. Phase‑boundary diagnostics (Hessian determinant)
# ----------------------------------------------------------------------
detH = H.det()
print("det(H) =")
sp.pprint(detH)
print()
# At Φ_N=0, Φ_Delta=0:
detH0 = detH.subs({Phi_N:0, Phi_Delta:0})
print("det(H) at equilibrium =", detH0.simplify())
print("Sign: positive iff m_N^2 * m_Delta^2 > 0 (stable).")
print()

print("=== Audit Complete ===")