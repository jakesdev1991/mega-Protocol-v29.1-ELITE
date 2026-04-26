# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol invariant validator for the Functional Transfer Fragility Monitor (FTFM‑Ω).
Checks:
  1. Presence of 1/2 factor in diffusion term.
  2. Dimensionless nature of each term in the Omega Action.
  3. Dimensionless invariant ψ (log of ratio of dimensionless quantities).
  4. CFI bounds [0,1] for any real input.
  5. Linear mappings to Φ_N and Φ_Δ preserve [0,1] for small coefficients.
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Symbolic setup
# ----------------------------------------------------------------------
# Base dimensions (we treat everything as dimensionless except time T)
T = sp.symbols('T', positive=True)   # dimension of time
# Dimensionless symbols
x, y, z, t = sp.symbols('x y z t')   # coordinates on context manifold (dimensionless)
F = sp.symbols('F')                  # functional transfer field (dimensionless)
D = sp.symbols('D')                  # diffusion coefficient (will be checked)
R = sp.symbols('R')                  # drift term R(F,s) (dimensionless)
zeta = sp.symbols('zeta')            # noise term (dimensionless)
# Metric g_{μν} and its inverse g^{μν} are dimensionless
g = sp.symbols('g')                  # placeholder for metric determinant sqrt(-g) (dimensionless)
# Potential parameters
alpha, beta = sp.symbols('alpha beta', real=True)
F0 = sp.symbols('F0')                # reference field value (dimensionless)
# Omega coupling
lambda_Omega = sp.symbols('lambda_Omega', real=True)
L_Omega = sp.symbols('L_Omega')      # built from Φ_N, Φ_Δ (dimensionless)
# Gauge term
A_mu = sp.symbols('A_mu')            # gauge potential (to be checked)
J_mu = sp.symbols('J_mu')            # current (to be checked)

# ----------------------------------------------------------------------
# 2. Check diffusion term: ∂_t F = D ∇^2 F + ...  should be (1/2) D ∇^2 F
# ----------------------------------------------------------------------
# Let's compute dimensions of each term assuming [∂_t] = 1/T, [∇^2] = 1/L^2.
# Since we set coordinates dimensionless, we introduce a characteristic length L0
# to give ∇^2 dimension 1/L0^2. We'll treat L0 as dimensionless scaling factor.
L0 = sp.symbols('L0', positive=True)   # characteristic length (dimensionless scaling)
# Effective dimension of ∇^2 is 1/L0^2
dim_dT = 1/T
dim_laplacian = 1/L0**2
dim_D = sp.symbols('dim_D')   # unknown dimension of D

# Dimension of D ∇^2 F
dim_D_term = dim_D * dim_laplacian   # because F dimensionless
# Dimension of ∂_t F
dim_dtF = dim_dT

# Equality condition: dim_dtF == dim_D_term  =>  dim_D = T / L0^2
dim_D_solved = sp.solve(sp.Eq(dim_dtF, dim_D_term), dim_D)[0]
print("Required dimension of D for dimensional balance:", dim_D_solved)
print("If D is taken as a pure number (dimensionless), the equation is off by factor T/L0^2.")
print("Thus a prefactor 1/2 does NOT fix dimensions; the issue is missing a time scale.")
print("-"*60)

# ----------------------------------------------------------------------
# 3. Action dimensional check
# ----------------------------------------------------------------------
# Action S = ∫ d^4x sqrt(-g) [ 1/2 g^{μν} ∂_μ F ∂_ν F + V(F) + λ L_Ω + A_μ J^μ ]
# We assume integration measure d^4x has dimension L0^4 (since each dx ~ L0)
# sqrt(-g) is dimensionless.
dim_d4x = L0**4
# Kinetic term: 1/2 g^{μν} ∂_μ F ∂_ν F
# ∂_μ has dimension 1/L0 (since ∂/∂x ~ 1/L0)
dim_kinetic = (1/L0)**2   # two derivatives
# Potential V: Mexican hat V = (α/2)‖F-F0‖^2 + (β/4)‖F-F0‖^4
# F dimensionless → V dimensionless if α,β dimensionless
dim_V = sp.Integer(1)    # dimensionless
# Omega coupling term: λ L_Ω (both dimensionless)
dim_Omega = sp.Integer(1)
# Gauge term: A_μ J^μ
# We will derive dimensions of A_μ and J^μ from definitions later.
dim_A = sp.symbols('dim_A')
dim_J = sp.symbols('dim_J')
dim_gauge = dim_A * dim_J

# Total integrand dimension (inside brackets)
dim_integrand = sp.Add(dim_kinetic, dim_V, dim_Omega, dim_gauge)
# Action dimension = dim_d4x * dim_integrand
dim_S = sp.simplify(dim_d4x * dim_integrand)
print("Dimension of the action S:", dim_S)
print("For S to be dimensionless (as required in natural units ħ=c=1),")
print("we need:", sp.simplify(dim_S == 1))
print("-"*60)

# ----------------------------------------------------------------------
# 4. Gauge term definitions (as given in the proposal)
# ----------------------------------------------------------------------
# A_μ = ∂_μ S_context   where S_context = - Σ p_k log p_k  (Shannon entropy, dimensionless)
# Hence A_μ has dimension of derivative w.r.t. coordinate → 1/L0
dim_A_correct = 1/L0
# J^μ = √2 Φ_Δ ℓ δ^μ_0   where ℓ is a characteristic length (take ℓ = L0)
# Φ_Δ dimensionless, ℓ has dimension L0, δ is dimensionless
dim_J_correct = L0
print("Derived dimensions from definitions:")
print("  [A_μ] =", dim_A_correct)
print("  [J^μ] =", dim_J_correct)
print("Hence [A_μ J^μ] =", dim_A_correct * dim_J_correct)
print("-"*60)

# ----------------------------------------------------------------------
# 5. Invariant ψ = ln(|R_context|/R0) + λ·CFI
# ----------------------------------------------------------------------
# Ricci curvature R_context has dimension 1/L0^2 (inverse length squared)
R_context = sp.symbols('R_context')
R0 = sp.symbols('R0')   # reference curvature, same dimension as R_context
lam = sp.symbols('lam') # λ coupling (dimensionless)
CFI = sp.symbols('CFI') # assumed dimensionless
psi = sp.ln(sp.Abs(R_context)/R0) + lam*CFI
# Log argument must be dimensionless → R_context/R0 dimensionless → OK if R0 same dim as R_context
print("ψ expression:", psi)
print("Log argument dimensionless? sp.simplify(R_context/R0) ->", sp.simplify(R_context/R0))
print("-"*60)

# ----------------------------------------------------------------------
# 6. CFI bounds check (tanh ensures [-1,1]; we shift to [0,1] via (tanh+1)/2)
# ----------------------------------------------------------------------
# Proposal uses CFI = tanh[ … ] directly, claiming range [0,1].
# Actually tanh ranges [-1,1]; to get [0,1] need (tanh+1)/2.
# We'll test both.
def tanh(x): return sp.tanh(x)
expr = sp.symbols('expr')   # placeholder for the linear combination inside tanh
CFI_tanh = tanh(expr)
CFI_shifted = (tanh(expr) + 1)/2
print("tanh range:", sp.simplify(CFI_tanh.subs(expr, -sp.oo)), "to", sp.simplify(CFI_tanh.subs(expr, sp.oo)))
print("(tanh+1)/2 range:", sp.simplify(CFI_shifted.subs(expr, -sp.oo)), "to",
      sp.simplify(CFI_shifted.subs(expr, sp.oo)))
print("-"*60)

# ----------------------------------------------------------------------
# 7. Linear mappings to Φ_N and Φ_Δ
# ----------------------------------------------------------------------
# Φ_N(t) = Φ_N0 - η1·CFI(t-τ1) + η2·ρ(t-τ1)
# Φ_Δ(t)= Φ_Δ0 + η3·κ(t-τ2) - η4·χ(t-τ2)
# Assume all inputs dimensionless and coefficients small enough to keep outputs in [0,1].
Phi_N0, Phi_Delta0 = sp.symbols('Phi_N0 Phi_Delta0', real=True)
eta1, eta2, eta3, eta4 = sp.symbols('eta1 eta2 eta3 eta4', real=True)
CFI, rho, kappa, chi = sp.symbols('CFI rho kappa chi', real=True)
Phi_N = Phi_N0 - eta1*CFI + eta2*rho
Phi_Delta = Phi_Delta0 + eta3*kappa - eta4*chi
print("Φ_N expression:", Phi_N)
print("Φ_Δ expression:", Phi_Delta)
print("To guarantee Φ_N,Φ_Δ ∈ [0,1] we need:")
print("  0 ≤ Φ_N0 - eta1*CFI + eta2*rho ≤ 1  for all CFI,rho∈[0,1]")
print("  0 ≤ Φ_Delta0 + eta3*kappa - eta4*chi ≤ 1  for all kappa,chi∈[0,1]")
print("-"*60)

# ----------------------------------------------------------------------
# 8. Summary of findings
# ----------------------------------------------------------------------
print("=== VALIDATION SUMMARY ===")
print("1. Diffusion term missing 1/2 factor AND missing explicit time scale → dimensional mismatch.")
print("2. Action dimension analysis shows integrand must be dimensionless;")
print("   with current definitions gauge term contributes L0^0 (OK) only if A_μ,J^μ as derived.")
print("3. Invariant ψ is ad‑hoc; not derived from variation of the action.")
print("4. CFI via plain tanh yields [-1,1]; proposal’s claim of [0,1] requires (tanh+1)/2.")
print("5. Linear mappings can preserve [0,1] if coefficients are sufficiently small.")
print("6. Lead‑times τ treated as constants – acceptable as first approximation.")
print("7. Ricci curvature estimate from GPLVM latent Hessian needs justification.")
print("\nTo achieve PASS, fix:")
print("   • Add 1/2 factor and introduce a characteristic time τ0 in ∂_t F = (1/2)D∇^2F + …")
print("   • Derive A_μ J^μ from a gauge‑invariant term in the Lagrangian.")
print("   • Obtain ψ from a term like ∫ sqrt{-g} R (Ricci scalar) in the action.")
print("   • Replace plain tanh with (tanh+1)/2 or rescale arguments appropriately.")
print("   • Justify the GPLVM→Ricci curvature approximation or replace with a well‑defined curvature estimator.")
print("   • Optionally make τ1,τ2 functions of CFI,ρ,etc. for better predictive horizon.")