# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for the Narrative Coherence Index for Micro‑Cap Resilience (NCMR‑Ω)
Checks:
    - Φ_N ≥ 0, Φ_Δ ≥ 0, J* ≥ 0   (Omega Protocol invariants)
    - NCI ∈ [0,1]
    - MPC constraints: NCI ≥ 0.4, Φ_N ≥ 0.7, Φ_Δ ≤ 0.6
    - Cost functional non‑negative
"""

import numpy as np

# ------------------------------
# Helper functions (as per proposal)
# ------------------------------
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def compute_nci(consistency, alignment, rigidity, debt, alpha, beta, gamma, delta):
    """
    NCI = α*Consistency + β*Alignment - γ*Rigidity - δ*Debt
    All sub‑metrics ∈ [0,1]; weights should satisfy α+β+γ+δ ≤ 1 to keep NCI in [0,1].
    """
    return alpha * consistency + beta * alignment - gamma * rigidity - delta * debt

def map_to_phi_n(nci, phi_n0, eta1, tau1, t):
    """
    Φ_N^{(narr)}(t) = Φ_N^{(0)} + η1 * sigmoid( NCI(t - τ1) )
    We approximate NCI(t-τ1) by the current nci for simplicity in validation.
    """
    return phi_n0 + eta1 * sigmoid(nci)

def map_to_phi_delta(nci, rigidity, phi_delta0, eta2, eta3, tau2, t):
    """
    Φ_Δ^{(narr)}(t) = Φ_Δ^{(0)} - η2 * NCI(t-τ2) + η3 * Rigidity(t-τ2)
    Again we use current values for validation.
    """
    return phi_delta0 - eta2 * nci + eta3 * rigidity

def anomaly_score(residual, sigma_res):
    """Standardized residual."""
    return np.abs(residual) / sigma_res if sigma_res > 0 else 0.0

def cost_function(nci, s_nci, phi_delta_narr, lam1=1.0, lam2=1.0):
    """
    J = ∫[ (1-NCI)^2 + λ1 * s_NCI^2 + λ2 * Φ_Δ^{(narr)} ] dt
    For a single time‑step we drop the integral and just compute the integrand.
    """
    return (1.0 - nci)**2 + lam1 * s_nci**2 + lam2 * phi_delta_narr

# ------------------------------
# Validation routine
# ------------------------------
def validate_random_sample(num_samples=10000):
    np.random.seed(42)  # reproducibility

    for i in range(num_samples):
        # --- Random but plausible inputs ---
        consistency = np.random.uniform(0, 1)
        alignment   = np.random.uniform(0, 1)
        rigidity    = np.random.uniform(0, 1)
        debt        = np.random.uniform(0, 1)

        # Weights: enforce α+β+γ+δ ≤ 1
        raw = np.random.dirichlet([1,1,1,1]) * np.random.uniform(0.5, 1.0)  # sum in [0.5,1.0]
        alpha, beta, gamma, delta = raw

        # Baseline Φ values (must be in [0,1])
        phi_n0   = np.random.uniform(0, 1)
        phi_d0   = np.random.uniform(0, 1)

        # η coefficients: keep resulting Φ in [0,1] (conservative bounds)
        eta1 = np.random.uniform(0, 0.5)   # upward push for Φ_N
        eta2 = np.random.uniform(0, 0.5)   # downward push for Φ_Δ via NCI
        eta3 = np.random.uniform(0, 0.5)   # upward push for Φ_Δ via rigidity

        # Time delays (months) – not needed for pointwise validation
        tau1, tau2 = 3, 6   # typical values from proposal

        # --- Core computations ---
        nci = compute_nci(consistency, alignment, rigidity, debt,
                          alpha, beta, gamma, delta)

        phi_n_narr = map_to_phi_n(nci, phi_n0, eta1, tau1, t=0)
        phi_d_narr = map_to_phi_delta(nci, rigidity,
                                      phi_d0, eta2, eta3, tau2, t=0)

        # Simulate a residual for anomaly score
        # Assume NCI follows a smooth trend with small noise
        trend = nci  # placeholder: in reality trend from STL
        noise = np.random.normal(0, 0.05)
        residual = nci - (trend + noise)
        sigma_res = np.std([residual]) if np.std([residual]) > 0 else 1e-6
        s_nci = anomaly_score(residual, sigma_res)

        # Cost (single‑step integrand)
        J = cost_function(nci, s_nci, phi_d_narr, lam1=1.0, lam2=1.0)

        # ------------------------------
        # Invariant & Constraint Checks
        # ------------------------------
        # 1. Omega Protocol invariants
        assert phi_n_narr >= -1e-9, f"Φ_N negative: {phi_n_narr}"
        assert phi_d_narr >= -1e-9, f"Φ_Δ negative: {phi_d_narr}"
        assert J >= -1e-9, f"Cost J* negative: {J}"

        # 2. NCI bounded
        assert 0 - 1e-9 <= nci <= 1 + 1e-9, f"NCI out of [0,1]: {nci}"

        # 3. MPC‑Ω hard constraints (as stipulated in the proposal)
        assert nci >= 0.4 - 1e-9, f"NCI < 0.4: {nci}"
        assert phi_n_narr >= 0.7 - 1e-9, f"Φ_N < 0.7: {phi_n_narr}"
        assert phi_d_narr <= 0.6 + 1e-9, f"Φ_Δ > 0.6: {phi_d_narr}"

        # If we reach here, sample passed
        if (i+1) % 2000 == 0:
            print(f"Passed {i+1}/{num_samples} samples...")

    print(f"All {num_samples} random samples satisfied the invariants and constraints.")

# ------------------------------
# Run validation
# ------------------------------
if __name__ == "__main__":
    validate_random_sample(num_samples=5000)