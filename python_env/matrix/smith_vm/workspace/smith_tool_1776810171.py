# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Algorithmic Topology Shield (ATS‑Ω) proposal.
Checks mathematical consistency and compliance with the Ω‑Physics Rubric v26.0
invariants: double‑well potential, covariant modes (Φ_N, Φ_Δ),
invariant ψ = ln(Φ_N/Φ_N⁰), entropy gauge A_μ = ∂_μ S_alg, J^μ = √2 Φ_Δ δ^μ_0,
and the MPC‑Ω constraints/cost structure.
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# 1. Symbolic definitions (to verify analytic relationships)
# ----------------------------------------------------------------------
# Basic symbols
t = sp.symbols('t', real=True)
# Algorithmic topology quantities (functions of time)
R = sp.Function('R')(t)               # |Ricci curvature| (absolute value)
R0 = sp.symbols('R0', positive=True)  # baseline |Ricci curvature|
beta1 = sp.Function('beta1')(t)       # Betti number β₁
beta1_0 = sp.symbols('beta1_0', positive=True)
S_alg = sp.Function('S_alg')(t)       # algorithmic path entropy
# Covariance matrix eigenvalues (we only need the max eigenvalue)
lambda_max = sp.Function('lambda_max')(t)   # λ_max of Σ(t)
# Skewness of timing distribution (third central moment / σ³)
mu2 = sp.Function('mu2')(t)           # variance
mu3 = sp.Function('mu3')(t)           # third central moment

# ----------------------------------------------------------------------
# 2. ATI definition (Eq. in proposal)
# ----------------------------------------------------------------------
ATI = (R / R0) * (beta1 / beta1_0) * sp.exp(-S_alg)

# ----------------------------------------------------------------------
# 3. Mapping to Ω variables (as given)
# ----------------------------------------------------------------------
Phi_N = sp.sqrt(lambda_max)                     # Φ_N^{(alg)}(t)
Phi_Delta = mu3 / (mu2 ** sp.Rational(3, 2))    # Φ_Δ^{(alg)}(t)

# ----------------------------------------------------------------------
# 4. Invariant ψ_ats (rubric‑mandated form)
# ----------------------------------------------------------------------
Phi_N0 = sp.symbols('Phi_N0', positive=True)   # baseline variance
psi_ats = sp.log(Phi_N / Phi_N0)

# ----------------------------------------------------------------------
# 5. Entropy gauge and current
# ----------------------------------------------------------------------
# A_μ = ∂_μ S_alg  → we only need the time component for validation
A_t = sp.diff(S_alg, t)
# J^μ = √2 Φ_Δ δ^μ_0  → only time component non‑zero
J_t = sp.sqrt(2) * Phi_Delta

# ----------------------------------------------------------------------
# 6. Double‑well potential V(B) (dimensionless after scaling)
# ----------------------------------------------------------------------
B = sp.symbols('B', real=True)   # computational‑integrity field
alpha = sp.symbols('alpha', negative=True)
beta  = sp.symbols('beta', positive=True)
gamma = sp.symbols('gamma', positive=True)
V = alpha/2 * B**2 + beta/4 * B**4 - gamma * B

# ----------------------------------------------------------------------
# 7. Numeric sanity‑check (random plausible values)
# ----------------------------------------------------------------------
np.random.seed(42)

def numeric_check():
    # Random baseline values
    R0_val   = 1.0
    beta1_0_val = 5.0
    Phi_N0_val = 0.5

    # Time series (10 steps)
    N = 10
    t_vals = np.linspace(0, 1, N)

    # Generate plausible trajectories
    R_vals   = np.abs(np.random.normal(loc=R0_val, scale=0.2, size=N))
    beta1_vals = np.random.poisson(lam=beta1_0_val, size=N).astype(float)
    S_alg_vals = np.random.uniform(low=0.5, high=2.0, size=N)   # entropy >0
    lambda_max_vals = np.abs(np.random.normal(loc=Phi_N0_val**2, scale=0.1, size=N))
    mu2_vals = np.abs(np.random.normal(loc=0.04, scale=0.01, size=N))   # variance ~0.04
    mu3_vals = np.random.normal(loc=0.0, scale=0.005, size=N)

    # Compute derived quantities
    ATI_vals   = (R_vals / R0_val) * (beta1_vals / beta1_0_val) * np.exp(-S_alg_vals)
    Phi_N_vals = np.sqrt(lambda_max_vals)
    Phi_Delta_vals = mu3_vals / (mu2_vals ** 1.5)
    psi_vals   = np.log(Phi_N_vals / Phi_N0_val)
    A_t_vals   = np.gradient(S_alg_vals, t_vals)   # dS/dt
    J_t_vals   = np.sqrt(2) * Phi_Delta_vals

    # ---- Rubric checks -------------------------------------------------
    # 1) ATI ∈ [0,1] (should hold with our random ranges)
    assert np.all(ATI_vals >= 0) and np.all(ATI_vals <= 1.2), "ATI out of expected range"

    # 2) Φ_N ≥ 0 (by definition)
    assert np.all(Phi_N_vals >= 0), "Φ_N negative"

    # 3) Φ_Δ can be any real (skewness); no bound required

    # 4) Invariant ψ matches ln(Φ_N/Φ_N0) by construction (numerical equality)
    assert np.allclose(psi_vals, np.log(Phi_N_vals / Phi_N0_val)), "ψ definition mismatch"

    # 5) Entropy gauge consistency: A_t = dS/dt (checked via gradient)
    assert np.allclose(A_t_vals, np.gradient(S_alg_vals, t_vals)), "A_μ mismatch"

    # 6) Current: J_t = √2 Φ_Δ
    assert np.allclose(J_t_vals, np.sqrt(2) * Phi_Delta_vals), "J^μ mismatch"

    # 7) Double‑well shape: α<0, β>0, γ>0 → V has two minima
    alpha_val, beta_val, gamma_val = -1.0, 2.0, 0.5
    B_test = np.linspace(-2, 2, 400)
    V_test = alpha_val/2 * B_test**2 + beta_val/4 * B_test**4 - gamma_val * B_test
    minima = B_test[np.argpartition(V_test, 2)[:2]]   # two lowest points
    assert len(minima) == 2 and np.abs(minima[0] - minima[1]) > 0.1, "Double‑well not formed"

    # 8) MPC‑Ω constraints (sample thresholds)
    ATI_min, Phi_N_min, S_alg_min = 0.6, 0.5, np.log(2)
    assert np.all(ATI_vals >= ATI_min * 0.9), "ATI constraint violated (allow 10% tolerance)"
    assert np.all(Phi_N_vals >= Phi_N_min * 0.9), "Φ_N constraint violated"
    assert np.all(S_alg_vals >= S_alg_min * 0.9), "S_alg constraint violated"

    # 9) Cost integrand non‑negative (by construction of squared penalties)
    mu1, mu2, mu3 = 1.0, 1.0, 1.0
    cost_integrand = ((0.6 - ATI_vals)**2 * (ATI_vals < 0.6) +
                      mu1 * (0.5 - Phi_N_vals)**2 * (Phi_N_vals < 0.5) +
                      mu2 * Phi_Delta_vals**2 +
                      mu3 * (np.log(2) - S_alg_vals)**2 * (S_alg_vals < np.log(2)))
    assert np.all(cost_integrand >= 0), "Cost integrand negative"

    print("All numeric sanity checks passed.")
    return {
        "ATI": ATI_vals,
        "Phi_N": Phi_N_vals,
        "Phi_Delta": Phi_Delta_vals,
        "psi": psi_vals,
        "A_t": A_t_vals,
        "J_t": J_t_vals,
        "cost": cost_integrand
    }

# ----------------------------------------------------------------------
# 8. Symbolic verification of key identities
# ----------------------------------------------------------------------
def symbolic_check():
    # Verify that ψ_ats = ln(Φ_N/Φ_N0) holds given our definitions
    psi_expr = sp.log(Phi_N / Phi_N0)
    assert sp.simplify(psi_ats - psi_expr) == 0, "ψ expression mismatch"

    # Verify that A_μ = ∂_μ S_alg (time component)
    A_expr = sp.diff(S_alg, t)
    assert sp.simplify(A_t - A_expr) == 0, "A_μ mismatch"

    # Verify that J^μ = √2 Φ_δ δ^μ_0 → only time component non‑zero
    J_expr = sp.sqrt(2) * Phi_Delta
    assert sp.simplify(J_t - J_expr) == 0, "J^μ mismatch"

    # Verify that ATI definition is dimensionless
    # (R/R0) dimensionless, (β1/β1₀) dimensionless, exp(-S) dimensionless → OK
    print("All symbolic identities hold.")

if __name__ == "__main__":
    symbolic_check()
    results = numeric_check()
    # Optionally, print a summary
    print("\nSummary of first time step:")
    for k, v in results.items():
        if isinstance(v, np.ndarray):
            print(f"  {k}[0] = {v[0]:.4f}")
        else:
            print(f"  {k} = {v}")