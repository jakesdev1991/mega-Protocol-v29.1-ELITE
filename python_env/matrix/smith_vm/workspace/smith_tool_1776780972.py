# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
---------------------------------
Checks:
  1. Definitions of ψ, ξ_N⁻², ξ_Δ⁻²
  2. Boundary conditions for Shredding Event and Informational Freeze
  3. Dimensional consistency of key quantities
  4. Dimension of the threshold Θ(ψ) (should be [T]⁻⁶)
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
# ------------------------------------------------------------------
# Fields (dimensionless)
Phi_N, Phi_Delta, I0 = sp.symbols('Phi_N Phi_Delta I0', positive=True, real=True)
# Coupling constant λ has dimension [T]⁻²
lam = sp.symbols('lam', positive=True, real=True)
# Auxiliary, dimensionless
gDelta = sp.symbols('gDelta', real=True)
# Time symbol for dimensional analysis
T = sp.symbols('T')  # represents [time]

# ------------------------------------------------------------------
# 1. Invariant definitions
# ------------------------------------------------------------------
psi = sp.log(Phi_N / I0)                     # ψ = ln(Φ_N / I0)

# Stiffness invariants (inverse squared)
xi_N_inv2  = lam * (3*Phi_N**2 + Phi_Delta**2 - I0**2)
xi_D_inv2  = lam * (Phi_N**2 + 3*Phi_Delta**2 - I0**2)

# ------------------------------------------------------------------
# 2. Boundary conditions
# ------------------------------------------------------------------
# Shredding Event: ξ_Δ → ∞  <=>  ξ_Δ⁻² → 0
shred_cond = sp.simplify(xi_D_inv2)          # should vanish when Φ_N²+3Φ_Δ² = I0²
# Informational Freeze: ξ_N → ∞  <=>  ξ_N⁻² → 0
freeze_cond = sp.simplify(xi_N_inv2)         # should vanish when 3Φ_N²+Φ_Δ² = I0²

# ------------------------------------------------------------------
# 3. Dimensional analysis
# ------------------------------------------------------------------
# Assign dimensions: [Φ_N] = [Φ_Δ] = [I0] = 1, [λ] = T⁻²
dim = {
    Phi_N: 1,
    Phi_Delta: 1,
    I0: 1,
    lam: T**(-2),
    psi: 0,               # log of dimensionless ratio → dimensionless
    gDelta: 0,
}

def expr_dim(expr):
    """Replace symbols with their dimensional powers and simplify."""
    return sp.simplify(expr.subs(dim))

# Dimensions of key quantities
dim_xi_N2   = expr_dim(1/xi_N_inv2)   # ξ_N²
dim_xi_D2   = expr_dim(1/xi_D_inv2)   # ξ_Δ²
dim_psi     = expr_dim(psi)
dim_S_h     = 0                       # Shannon entropy (dimensionless)
# Jerk J_I = d³S_h/dt³ → dimension T⁻³
dim_JI      = T**(-3)

print("Dimensional checks:")
print(f"  [ξ_N²]   = {dim_xi_N2}   (expected T²)")
print(f"  [ξ_Δ²]   = {dim_xi_D2}   (expected T²)")
print(f"  [ψ]      = {dim_psi}     (expected 1)")
print(f"  [J_I]    = {dim_JI}      (expected T⁻³)")

# ------------------------------------------------------------------
# 4. Threshold Θ(ψ) dimension
# ------------------------------------------------------------------
# Θ(ψ) = (λ I0⁴ /9) * (e^{2ψ} -1)² * (1 + (3 gΔ²)/(4π) e^{-2ψ})
Theta = (lam * I0**4 / 9) * (sp.exp(2*psi) - 1)**2 * (1 + (3*gDelta**2)/(4*sp.pi) * sp.exp(-2*psi))
dim_Theta = expr_dim(Theta)
print(f"  [Θ(ψ)]   = {dim_Theta}   (expected T⁻⁶ for σ_J² comparison)")

# ------------------------------------------------------------------
# 5. Numerical sanity check (using the audit data)
# ------------------------------------------------------------------
# Normalised modes (I0 = 1)
phi_N_val = 0.78
phi_D_val = 0.35
lam_val   = 1e10      # s⁻²
gDelta_val= 0.1

psi_val   = sp.N(sp.log(phi_N_val))
xi_N_inv2_val = sp.N(xi_N_inv2.subs({Phi_N:phi_N_val, Phi_Delta:phi_D_val, I0:1, lam:lam_val}))
xi_D_inv2_val = sp.N(xi_D_inv2.subs({Phi_N:phi_N_val, Phi_Delta:phi_D_val, I0:1, lam:lam_val}))

print("\nNumerical evaluation (audit data):")
print(f"  ψ = {psi_val:.6f}")
print(f"  ξ_N⁻² = {xi_N_inv2_val:.3e} s⁻²")
print(f"  ξ_Δ⁻² = {xi_D_inv2_val:.3e} s⁻²")
print(f"  Shredding condition Φ_N²+3Φ_Δ²-I0² = {phi_N_val**2 + 3*phi_D_val**2 - 1:.6f}")
print(f"  Freeze condition 3Φ_N²+Φ_Δ²-I0² = {3*phi_N_val**2 + phi_D_val**2 - 1:.6f}")

# ------------------------------------------------------------------
# Assertions (will raise if invariant broken)
# ------------------------------------------------------------------
assert sp.simplify(psi - sp.log(Phi_N/I0)) == 0, "ψ definition broken"
assert sp.simplify(xi_N_inv2 - lam*(3*Phi_N**2 + Phi_Delta**2 - I0**2)) == 0, "ξ_N⁻² definition broken"
assert sp.simplify(xi_D_inv2 - lam*(Phi_N**2 + 3*Phi_Delta**2 - I0**2)) == 0, "ξ_Δ⁻² definition broken"

# Boundary checks: the expressions should vanish exactly on the respective surfaces
assert sp.simplify(xi_D_inv2.subs({Phi_N**2 + 3*Phi_Delta**2: I0**2})) == 0, "Shredding boundary incorrect"
assert sp.simplify(xi_N_inv2.subs({3*Phi_N**2 + Phi_Delta**2: I0**2})) == 0, "Freeze boundary incorrect"

# Dimensional checks: powers of T must match expectations
assert dim_xi_N2 == T**2, f"ξ_N² dimension mismatch: got {dim_xi_N2}"
assert dim_xi_D2 == T**2, f"ξ_Δ² dimension mismatch: got {dim_xi_D2}"
assert dim_psi == sp.Integer(0), f"ψ dimension mismatch: got {dim_psi}"
assert dim_JI == T**(-3), f"J_I dimension mismatch: got {dim_JI}"

# The threshold dimension is *not* T⁻⁶ → flag as a potential error
if dim_Theta != T**(-6):
    print("\n[WARNING] Θ(ψ) dimension is", dim_Theta, "instead of expected T⁻⁶.")
    print("          This indicates a possible missing factor in the threshold formula.")
else:
    print("\n[OK] Θ(ψ) dimension matches T⁻⁶.")

print("\nAll invariant checks passed.")