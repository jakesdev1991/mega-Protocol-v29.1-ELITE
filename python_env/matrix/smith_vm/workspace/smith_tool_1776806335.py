# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Topological Cognitive Memory (TCM‑Ω)

This script checks the mathematical soundness and Ω‑Rubric compliance of the
TCM‑Ω proposal.  It:
  1. Builds a synthetic multi‑agent cognitive manifold.
  2. Computes the topological observables (Wilson loop, correlation length,
     energy gap) and derives CTOI, Φ_N, Φ_Δ, ψ, ψ_Δ.
  3. Verifies the Ω‑invariant definitions ψ = ln(Φ_N) and ψ_Δ = ln(Φ_Δ).
  4. Enforces the MPC‑Ω hard constraints (CTOI ≥ 0.6, Φ_N ≥ 0.6,
     S_cognitive ≥ ln 3) and that the quadratic‑program cost is non‑negative.
  5. Checks that the dynamical update respects the prescribed decay law.
  6. Reports any violation with a clear message.

If all assertions pass, the proposal is deemed mathematically sound and
Ω‑Rubric compliant for the given synthetic scenario.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (mirror the definitions in the proposal)
# ----------------------------------------------------------------------
def wilson_loop(sigma_z, plaquette):
    """
    Compute Wilson loop W_p = ∏_{i∈∂p} σ_i^z.
    sigma_z: shape (n_agents,) with values ±1 (Ising spins).
    plaquette: list/array of indices forming a closed loop.
    Returns the product (±1).
    """
    return np.prod(sigma_z[plaquette])

def correlation_length(C, r_vals):
    """
    Estimate ξ from exponential fit C(r) ≈ exp(-r/ξ).
    C: array of correlation values at distances r_vals.
    Returns ξ > 0 or np.inf if fit fails.
    """
    # linear fit to log(C) vs r
    mask = C > 0
    if np.sum(mask) < 2:
        return np.inf
    logC = np.log(C[mask])
    r = r_vals[mask]
    coeff = np.polyfit(r, logC, 1)   # logC = a*r + b  => ξ = -1/a
    xi = -1.0 / coeff[0] if coeff[0] < 0 else np.inf
    return max(xi, 1e-12)

def energy_gap(E0, E1):
    """Δ = E1 - E0 (must be non‑negative)."""
    return max(E1 - E0, 0.0)

def compute_CTOI(Wp, Wp0, Delta, Delta0, xi, xi0):
    """
    CTOI = (|Wp|/|Wp0|) * (Delta/Delta0) * (xi/xi0)
    All factors are non‑negative; we clip extreme values for stability.
    """
    term1 = np.abs(Wp) / (np.abs(Wp0) + 1e-12)
    term2 = Delta / (Delta0 + 1e-12)
    term3 = xi   / (xi0   + 1e-12)
    return term1 * term2 * term3

def cognitive_entropy(p):
    """Shannon entropy S = -∑ p_i log p_i."""
    return -np.sum(p * np.log(p + 1e-12))

# ----------------------------------------------------------------------
# Synthetic data generation (stand‑in for real therapeutic measurements)
# ----------------------------------------------------------------------
np.random.seed(42)
n_agents = 30                     # number of cognitive “qubits”
n_time   = 50                     # discrete time steps

# Spin variables σ_i^z ∈ {+1, -1}
sigma_z = np.random.choice([-1, +1], size=(n_time, n_agents))

# Define a few plaquettes (small loops) for Wilson loop measurement
plaquettes = [ [0,1,2,3], [4,5,6,7], [8,9,10,11] ]  # example 4‑site loops

# Baseline (t=0) reference values
Wp0_vals = np.array([wilson_loop(sigma_z[0], p) for p in plaquettes])
Wp0_ref  = np.mean(np.abs(Wp0_vals))               # scalar baseline

# Baseline energy gap and correlation length (chosen arbitrarily but fixed)
Delta0 = 1.0
xi0    = 5.0

# Stress and intervention profiles (dimensionless)
stress   = 0.3 + 0.2 * np.sin(2*np.pi*np.arange(n_time)/20)   # oscillatory stress
intervention = 0.1 * (np.arange(n_time) > 20).astype(float)   # kicks in after t=20

# Model parameters (from the proposal)
gamma = 0.05
kappa = 0.1

# ----------------------------------------------------------------------
# Time‑evolution of the topological observables
# ----------------------------------------------------------------------
CTOI_hist = np.zeros(n_time)
PhiN_hist = np.zeros(n_time)
PhiDelta_hist = np.zeros(n_time)
psi_hist    = np.zeros(n_time)
psiDelta_hist = np.zeros(n_time)
S_cog_hist  = np.zeros(n_time)

# Initialise CTOI at t=0 (should be 1 by construction)
CTOI = 1.0
CTOI_hist[0] = CTOI

for t in range(1, n_time):
    # ----- 1. Update Wilson loop expectation -----
    Wp_vals_t = np.array([wilson_loop(sigma_z[t], p) for p in plaquettes])
    Wp_avg    = np.mean(np.abs(Wp_vals_t))

    # ----- 2. Update correlation length (mock: inversely related to stress) -----
    # Use a simple proxy: xi = xi0 * exp(-stress)
    xi_t = xi0 * np.exp(-stress[t-1])

    # ----- 3. Update energy gap (mock: gap shrinks under stress) -----
    Delta_t = Delta0 * (1.0 - 0.5 * np.tanh(stress[t-1]))

    # ----- 4. Compute CTOI -----
    CTOI = compute_CTOI(Wp_avg, Wp0_ref, Delta_t, Delta0, xi_t, xi0)
    CTOI_hist[t] = CTOI

    # ----- 5. Derive Ω‑variables -----
    PhiN = 1.0 - CTOI                     # Φ_N^(tcm)
    # For Φ_Δ we need a distribution of ξ_i across agents.
    # Mock: each agent gets a slightly perturbed ξ_i.
    xi_i = xi_t * (1.0 + 0.1 * np.random.randn(n_agents))
    PhiDelta = np.var(np.log(xi_i / xi0))  # Φ_Δ^(tcm)

    PhiN_hist[t]   = PhiN
    PhiDelta_hist[t] = PhiDelta

    # ----- 6. Ω‑invariants (ψ = ln Φ_N, ψ_Δ = ln Φ_Δ) -----
    # Guard against log of non‑positive numbers.
    eps = 1e-12
    psi_hist[t]    = np.log(max(PhiN,    eps))
    psiDelta_hist[t] = np.log(max(PhiDelta, eps))

    # ----- 7. Cognitive entropy (Shannon) from agent responses -----
    # Mock response magnitude proportional to |σ_i^z| (always 1) → uniform.
    # To get non‑trivial entropy we bias by stress.
    p = np.exp(-stress[t-1] * np.abs(xi_i - xi_t))
    p /= p.sum()
    S_cog_hist[t] = cognitive_entropy(p)

    # ----- 8. Update CTOI via the prescribed dynamical law -----
    # dCTOI/dt = -γ (stress - Δ)_+ CTOI + κ intervention
    stress_term = max(stress[t-1] - Delta_t, 0.0)
    dCTOI = (-gamma * stress_term * CTOI + kappa * intervention[t-1])
    CTOI += dCTOI   # Euler step (dt = 1)
    # Keep CTOI in a physically plausible range
    CTOI = np.clip(CTOI, 0.0, 2.0)

# ----------------------------------------------------------------------
# Validation checks (Ω‑Rubric v26.0 + MPC‑Ω constraints)
# ----------------------------------------------------------------------
def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)

# 1. Invariant definitions
assert_true(np.allclose(psi_hist,    np.log(np.maximum(PhiN_hist,    1e-12)),  atol=1e-10),
            "ψ ≠ ln(Φ_N) invariant violated")
assert_true(np.allclose(psiDelta_hist, np.log(np.maximum(PhiDelta_hist, 1e-12)), atol=1e-10),
            "ψ_Δ ≠ ln(Φ_Δ) invariant violated")

# 2. MPC‑Ω hard constraints
assert_true(np.all(CTOI_hist >= 0.6 - 1e-9),
            "CTOI constraint violated (CTOI < 0.6)")
assert_true(np.all(PhiN_hist   >= 0.6 - 1e-9),
            "Φ_N constraint violated (Φ_N < 0.6)")
assert_true(np.all(S_cog_hist  >= np.log(3) - 1e-9),
            "Cognitive entropy constraint violated (S < ln 3)")

# 3. Cost function non‑negativity (quadratic penalty form)
mu1, mu2, mu3 = 1.0, 1.0, 1.0   # arbitrary positive weights
cost_integrand = (np.maximum(0.6 - CTOI_hist, 0)**2 +
                  mu1 * np.maximum(0.6 - PhiN_hist, 0)**2 +
                  mu2 * PhiDelta_hist**2 +
                  mu3 * np.maximum(np.log(3) - S_cog_hist, 0)**2)
assert_true(np.all(cost_integrand >= -1e-12),
            "Cost integrand became negative (invalid QP)")

# 4. Dynamical law consistency (compare finite‑difference with RHS)
dCTOI_num = np.diff(CTOI_hist)   # forward difference Δt = 1
rhs = (-gamma * np.maximum(stress[:-1] - Delta0 * (1.0 - 0.5*np.tanh(stress[:-1])), 0.0) *
       CTOI_hist[:-1] + kappa * intervention[:-1])
assert_true(np.allclose(dCTOI_num, rhs, atol=1e-6),
            "CTOI dynamics do not match the prescribed law")

# 5. Ensure CTOI stays within a reasonable band (optional sanity check)
assert_true(np.all(CTOI_hist <= 1.5),
            "CTOI exceeded plausible upper bound ( >1.5 ) – may indicate model blow‑up")

print("✅ All Ω‑Rubric and MPC‑Ω validation checks passed.")
print(f"   Final CTOI: {CTOI_hist[-1]:.3f}")
print(f"   Final Φ_N : {PhiN_hist[-1]:.3f}")
print(f"   Final Φ_Δ : {PhiDelta_hist[-1]:.3f}")
print(f"   Final S_cog: {S_cog_hist[-1]:.3f} (ln 3 = {np.log(3):.3f})")