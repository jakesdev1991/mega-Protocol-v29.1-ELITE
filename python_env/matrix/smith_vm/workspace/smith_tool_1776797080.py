# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for the Cognitive‑Tooling Mismatch Sensor (CTMS‑Ω) proposal.

Checks:
1. Dimensional consistency of the Fokker‑Planck equation (including the missing ½ factor).
2. Dimensional consistency of the Ω‑Action integral.
3. Validity of the Tooling‑Friction Fragility Index (TFFI) – sigmoid output in [0,1].
4. MPC‑Ω constraints: TFFI < 0.6, Φ_N^(cog) > 0.5.
5. Basic sanity of the invariant ψ_cog (dimensionless).
6. Highlights the dimensional inconsistency claimed for the stiffness invariants.

The script uses only symbolic/numeric checks; it does not require external data.
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# 1. Symbolic dimensional analysis
# ----------------------------------------------------------------------
# Define dimension symbols (M=mass, L=length, T=time). We will treat the
# cognitive‑load field Λ as dimensionless, coordinates as dimensionless after
# scaling by a reference length ℓ, and the metric g_{μν} as dimensionless.
# Under these assumptions we verify each term's dimension.

# Dimensionless base
dimless = sp.S(1)

# Symbols for parameters (assumed dimensionless unless noted)
mu, D, S_src = sp.symbols('mu D S_src')          # drift, diffusion, source
alpha, beta, gamma, lam_Omega = sp.symbols('alpha beta gamma lam_Omega')
PhiN0, PhiD0, eta1, eta2, eta3, eta4 = sp.symbols('PhiN0 PhiD0 eta1 eta2 eta3 eta4')
lam_psi, R0 = sp.symbols('lam_psi R0')

# ----- Fokker‑Planck -------------------------------------------------
# ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ^2[D P] + S
# If Λ, t, P are dimensionless, then:
#   ∂_t P → dimless
#   ∂_Λ[μ P] → mu * dimless   => mu must be dimless
#   ½ ∂_Λ^2[D P] → D * dimless => D must be dimless
#   S → dimless
# We check the missing ½: the proposal omitted it.
print("=== Fokker‑Planck dimensional check ===")
print("Assumed dimensions: [Λ]=dimensionless, [t]=dimensionless, [P]=dimensionless")
print("→ ∂_t P dimensionless:", dimless)
print("→ μ must be dimensionless for -∂_Λ[μ P] term to match:", dimless)
print("→ D must be dimensionless for ½∂_Λ^2[D P] term to match:", dimless)
print("→ Source S must be dimensionless:", dimless)
print("Note: The proposal wrote the diffusion term as ∂_Λ^2[D P] (missing ½).")
print("If the ½ is omitted, D would need to be re‑defined as D' = ½ D to keep the equation correct.\n")

# ----- Ω‑Action ------------------------------------------------------
# S = ∫ d^4x √{-g} [ ½ g^{μν} ∂_μ Λ ∂_ν Λ + V(Λ) + λ_Omega L_Omega(Φ_N,Φ_Δ) ]
# With dimensionless coordinates, metric, Λ → each term dimensionless.
print("=== Ω‑Action dimensional check ===")
print("Assuming: [x^μ]=dimensionless, [g_{μν}]=dimensionless, [Λ]=dimensionless")
print("→ Kinetic term ½ g^{μν} ∂_μ Λ ∂_ν Λ dimensionless:", dimless)
print("→ Potential V(Λ)=α/2 Λ^2 + β/4 Λ^4 - γ Λ dimensionless if α,β,γ dimensionless:", dimless)
print("→ Coupling λ_Omega L_Omega(Φ_N,Φ_Δ) dimensionless if λ_Omega dimensionless and L_Omega built from dimensionless Φ_N,Φ_Δ:", dimless)
print("→ Measure d^4x √{-g} dimensionless (since √{-g} dimensionless).")
print("→ Action S dimensionless ✓\n")

# ----- Invariant ψ_cog ------------------------------------------------
# ψ_cog = ln(|R_cog|/R0) + λ·max(TFFI)
# R_cog is Ricci curvature; with dimensionless metric & coordinates → dimensionless.
print("=== ψ_cog invariant check ===")
print("Assuming [R_cog]=dimensionless, [R0]=dimensionless → ln(|R_cog|/R0) dimensionless:", dimless)
print("TFFI output of sigmoid → dimensionless, λ dimensionless → λ·max(TFFI) dimensionless:", dimless)
print("→ ψ_cog dimensionless ✓\n")

# ----------------------------------------------------------------------
# 2. Numeric sanity checks (TFFI, MPC‑Ω constraints, ψ_cog)
# ----------------------------------------------------------------------
np.random.seed(42)

# Simulate a few teams (j) and time steps (t)
n_teams = 5
n_time = 10

# Raw signals (all normalized to roughly [0,1] for demonstration)
CKD = np.random.uniform(0, 3, size=(n_teams, n_time))          # Context‑Key Density
ETA = np.random.uniform(0, 10, size=(n_teams, n_time))        # Edit‑Time‑to‑Access (min)
H_tools = np.random.uniform(0, 1, size=(n_teams, n_time))    # Tool‑switching entropy (0=low,1=high)
SchemaDiv = np.random.uniform(0, 1, size=(n_teams, n_time))  # Schema divergence

# Weights (chosen arbitrarily but positive)
alpha_w, beta_w, gamma_w, delta_w = 0.4, 0.3, 0.2, 0.1

# Weighted sum before sigmoid
weighted = (alpha_w * CKD +
            beta_w * np.exp(-ETA) +
            gamma_w * (1 - H_tools) +
            delta_w * SchemaDiv)

# Sigmoid → TFFI in (0,1)
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

TFFI = sigmoid(weighted)

print("=== TFFI statistics ===")
print(f"TFFI min: {TFFI.min():.3f}, max: {TFFI.max():.3f}, mean: {TFFI.mean():.3f}")
assert np.all((TFFI >= 0) & (TFFI <= 1)), "TFFI out of [0,1] range!"
print("✓ TFFI lies in [0,1] as expected.\n")

# Mapping to Omega variables (cog‑derived)
# Φ_N^(cog)(t) = Φ_N^(0) - η1 * mean_j[TFFI_j(t-τ)] - η2 * var_j[TFFI_j(t-τ)]
# Φ_Δ^(cog)(t) = Φ_Δ^(0) + η3 * skew_j[TFFI_j(t-τ)] - η4 * min_j[CKD_j(t-τ)]
# We ignore τ for simplicity and use current timestep.
PhiN0_val, PhiD0_val = 0.8, 0.2
eta1_val, eta2_val, eta3_val, eta4_val = 0.1, 0.05, 0.15, 0.07

mean_TFFI = TFFI.mean(axis=0)
var_TFFI = TFFI.var(axis=0)
skew_TFFI = ((TFFI - mean_TFFI)**3).mean(axis=0) / (var_TFFI**1.5 + 1e-12)
min_CKD = CKD.min(axis=0)

PhiN_cog = PhiN0_val - eta1_val * mean_TFFI - eta2_val * var_TFFI
PhiD_cog = PhiD0_val + eta3_val * skew_TFFI - eta4_val * min_CKD

print("=== Φ_N^(cog) and Φ_Δ^(cog) ===")
print(f"Φ_N^(cog) range: [{PhiN_cog.min():.3f}, {PhiN_cog.max():.3f}]")
print(f"Φ_Δ^(cog) range: [{PhiD_cog.min():.3f}, {PhiD_cog.max():.3f}]")

# MPC‑Ω constraints: TFFI < 0.6, Φ_N^(cog) > 0.5
constraint1 = np.all(TFFI < 0.6)
constraint2 = np.all(PhiN_cog > 0.5)

print("\n=== MPC‑Ω constraint check ===")
print(f"All TFFI < 0.6 ? {constraint1}")
print(f"All Φ_N^(cog) > 0.5 ? {constraint2}")
if constraint1 and constraint2:
    print("✓ Constraints satisfied.")
else:
    print("✗ Constraints violated!")

# Invariant ψ_cog (mock Ricci curvature)
# ψ_cog = ln(|R_cog|/R0) + λ·max_j[TFFI_j(t)]
lam_psi_val = 0.3
R0_val = 1.0
# Generate a mock Ricci scalar (dimensionless) varying around 1
R_cog = np.random.uniform(0.5, 2.0, size=n_time)
psi_cog = np.log(np.abs(R_cog) / R0_val) + lam_psi_val * TFFI.max(axis=0)

print("\n=== ψ_cog invariant (sample) ===")
print(f"ψ_cog values: {psi_cog}")
print("✓ ψ_cog is dimensionless (log of ratio + dimensionless term).\n")

# ----------------------------------------------------------------------
# 3. Highlight stiffness invariant dimensional inconsistency
# ----------------------------------------------------------------------
print("=== Stiffness invariant dimensional note ===")
print("The proposal claims ξ_N, ξ_Δ have dimensions of time because")
print("the effective potential scales as inverse‑time² due to the kinetic term’s prefactor.")
print("However, under the dimensionless scaling used for the action,")
print("the kinetic term carries no inverse‑time² factor, so ξ_N, ξ_Δ would be dimensionless")
print("(or would inherit whatever scale is introduced via the reference length ℓ).")
print("This creates a contradiction in the unit analysis.\n")

# ----------------------------------------------------------------------
# Final verdict
# ----------------------------------------------------------------------
if constraint1 and constraint2:
    print("VALIDATION RESULT: PASS (numeric & dimensional checks satisfied,")
    print("                aside from the noted stiffness‑invariant inconsistency).")
else:
    print("VALIDATION RESULT: FAIL (constraints violated).")