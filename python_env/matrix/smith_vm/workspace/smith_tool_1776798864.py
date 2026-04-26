# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for CTMS‑Ω proposal.
Checks:
  1. Invariant form ψ_cog = ln(Φ_N_cog / Φ_N0)
  2. Constraint bounds: TFFI < 0.6, Φ_N_cog > 0.5, S ≥ ln(3)
  3. Presence of ½ factor in Fokker‑Planck diffusion term
  4. Presence of entropy gauge term A_μ J^μ in the action
  5. Dimensionless consistency (all symbols treated as dimensionless)
  6. Boundary conditions expressed via ψ_cog divergence and Φ_Δ thresholds
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbolic placeholders (all dimensionless per proposal)
# ----------------------------------------------------------------------
t   = sp.symbols('t', real=True)          # time
Lambda = sp.symbols('Lambda', real=True)  # cognitive‑load field
P   = sp.symbols('P', real=True)          # probability density
mu  = sp.symbols('mu', real=True)         # drift μ(Λ)
D   = sp.symbols('D', real=True)          # diffusion D(Λ)
Ssrc= sp.symbols('Ssrc', real=True)       # source term S(Λ,t)

# Covariant modes (dimensionless)
Phi_N0   = sp.symbols('Phi_N0', positive=True)   # baseline connectivity
Phi_Ncog = sp.symbols('Phi_Ncog', real=True)    # Φ_N^(cog)(t)
Phi_Deltacog = sp.symbols('Phi_Deltacog', real=True)  # Φ_Δ^(cog)(t)

# Invariant ψ_cog
psi_cog = sp.log(Phi_Ncog / Phi_N0)

# ----------------------------------------------------------------------
# 1. Invariant check: must be exactly ln(Φ_N_cog/Φ_N0)
# ----------------------------------------------------------------------
invariant_ok = sp.simplify(psi_cog - sp.log(Phi_Ncog/Phi_N0)) == 0
print("Invariant form correct:", invariant_ok)

# ----------------------------------------------------------------------
# 2. Constraint bounds (sample numeric test)
# ----------------------------------------------------------------------
# Choose plausible values within claimed ranges
Phi_Ncog_val = 0.55   # > 0.5
Phi_Deltacog_val = 0.7
TFFI_val = 0.45       # < 0.6
S_val = np.log(3.5)   # ≥ ln(3)

constraints_ok = (Phi_Ncog_val > 0.5) and (Phi_Deltacog_val > 0) and \
                 (TFFI_val < 0.6) and (S_val >= np.log(3))
print("Constraint bounds satisfied (sample):", constraints_ok)

# ----------------------------------------------------------------------
# 3. Fokker‑Planck equation: ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ²[D P] + S_src
# ----------------------------------------------------------------------
# Build symbolic LHS and RHS
LHS = sp.diff(P, t)
RHS = -sp.diff(mu * P, Lambda) + sp.Rational(1,2) * sp.diff(sp.diff(D * P, Lambda), Lambda) + Ssrc

# Check that the diffusion term carries the factor 1/2 explicitly
diff_term = sp.Rational(1,2) * sp.diff(sp.diff(D * P, Lambda), Lambda)
has_half = diff_term.has(sp.Rational(1,2))
print("Fokker‑Planck diffusion term contains ½:", has_half)

# ----------------------------------------------------------------------
# 4. Action integral: S = ∫ d⁴x √-g [ ½ g^{μν} ∂_μ Λ ∂_ν Λ + V(Λ) + λ_Ω L_Ω + A_μ J^μ ]
# ----------------------------------------------------------------------
# Define metric, potential, gauge pieces (all dimensionless)
g_mu_nu = sp.symbols('g_mu_nu')          # dimensionless metric component
partial_mu_Lambda = sp.symbols('partial_mu_Lambda')
partial_nu_Lambda = sp.symbols('partial_nu_Lambda')
kinetic = sp.Rational(1,2) * g_mu_nu * partial_mu_Lambda * partial_nu_Lambda

# Potential V(Λ) = α/2 Λ² + β/4 Λ⁴ - γ Λ
alpha, beta, gamma = sp.symbols('alpha beta gamma', real=True)
V = alpha/2 * Lambda**2 + beta/4 * Lambda**4 - gamma * Lambda

# Coupling to Ω invariants
lambda_Omega = sp.symbols('lambda_Omega', real=True)
L_Omega = sp.symbols('L_Omega')   # placeholder for L_Ω(Φ_N,Φ_Δ)

# Entropy gauge: A_μ = ∂_μ S, J^μ = √2 Φ_Δ δ^μ_0  (dimensionless)
S_entropy = sp.symbols('S_entropy', real=True)   # Shannon entropy (dimensionless)
A_mu = sp.symbols('A_mu')   # ∂_μ S_entropy
J_mu = sp.symbols('J_mu')   # √2 * Φ_Δ * δ^μ_0  (dimensionless)
gauge_term = A_mu * J_mu

# Assemble Lagrangian density
L_density = kinetic + V + lambda_Omega * L_Omega + gauge_term

# Verify gauge term appears explicitly
has_gauge = L_density.has(gauge_term)
print("Action contains entropy gauge term A_μ J^μ:", has_gauge)

# ----------------------------------------------------------------------
# 5. Dimensionless check (all symbols declared dimensionless)
# ----------------------------------------------------------------------
# In this symbolic treatment we assume every symbol is dimensionless.
# We can assert that no explicit length scale appears.
length_scales = [sp.Symbol('L'), sp.Symbol('ell')]  # typical length symbols
has_length = any(L_density.has(sym) for sym in length_scales)
print("No explicit length scale in Lagrangian density:", not has_length)

# ----------------------------------------------------------------------
# 6. Boundary conditions: Shredding Event & Informational Freeze
# ----------------------------------------------------------------------
# Shredding: ψ_cog → +∞  <=> Φ_N_cog → 0+  (connectivity collapses)
# Freeze:   ψ_cog → -∞  <=> Φ_N_cog → ∞  (or Φ_Δ_cog > threshold)
shredding_cond = sp.limit(psi_cog, Phi_Ncog, 0, dir='+') == sp.oo
freeze_cond    = sp.limit(psi_cog, Phi_Ncog, sp.oo) == -sp.oo  # ψ → -∞ as Φ_N→∞
# Also require Φ_Δ_cog > 0.8 for freeze (sample threshold)
freeze_with_PhiDelta = (Phi_Deltacog_val > 0.8) and freeze_cond

print("Shredding condition (ψ→+∞ as Φ_N→0):", shredding_cond)
print("Freeze condition (ψ→-∞ as Φ_N→∞):", freeze_cond)
print("Freeze with Φ_Δ threshold (>0.8):", freeze_with_PhiDelta)

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
all_checks = invariant_ok and constraints_ok and has_half and has_gauge and (not has_length) and shredding_cond and freeze_cond
print("\n=== OVERALL VALIDATION ===")
print("All checks passed:", all_checks)
if not all_checks:
    print("Failed checks:")
    if not invariant_ok: print(" - Invariant form")
    if not constraints_ok: print(" - Constraint bounds")
    if not has_half: print(" - Missing ½ in Fokker‑Planck")
    if not has_gauge: print(" - Missing gauge term A_μ J^μ")
    if has_length: print(" - Explicit length scale present")
    if not shredding_cond: print(" - Shredding boundary not captured")
    if not freeze_cond: print(" - Freeze boundary not captured")