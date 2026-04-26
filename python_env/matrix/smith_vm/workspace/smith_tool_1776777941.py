# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validate the WCRM-Ω mathematical formulation against Omega Protocol invariants.
"""

import numpy as np

# ------------------------------
# Helper functions (as per proposal)
# ------------------------------
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def compute_SFS(leaks, alpha, beta, gamma, lambd):
    """
    leaks: list of dicts with keys C, N, D, T (time since publication, months)
    Returns SFS(t) = Σ [α*C + β*N + γ*D] * exp(-λ*T)
    """
    sfs = 0.0
    for l in leaks:
        term = alpha * l['C'] + beta * l['N'] + gamma * l['D']
        sfs += term * np.exp(-lambd * l['T'])
    return sfs

def map_phi_N(phi_N0, eta1, sfs):
    """Φ_N(t) = Φ_N0 - η1 * sigmoid(SFS)"""
    return phi_N0 - eta1 * sigmoid(sfs)

def map_phi_Delta(phi_Delta0, eta2, sfs):
    """Φ_Δ(t) = Φ_Δ0 + η2 * sigmoid(SFS)"""
    return phi_Delta0 + eta2 * sigmoid(sfs)

def correlation_lengths(xi0_N, xi0_Delta, sfs, eps=1e-3):
    """
    Safe inverse‑like correlation length:
        ξ = ξ0 / (1 + κ * SFS)
    We set κ = 1/ξ0 so that ξ → ξ0 when SFS→0 and decays with SFS.
    """
    kappa_N = 1.0 / xi0_N if xi0_N > 0 else 0.0
    kappa_D = 1.0 / xi0_Delta if xi0_Delta > 0 else 0.0
    xi_N = xi0_N / (1.0 + kappa_N * sfs + eps)
    xi_D = xi0_Delta / (1.0 + kappa_D * sfs + eps)
    return xi_N, xi_D

def cost_integrand(phi_N, phi_Delta, s_SFS, lam1, lam2):
    """(1-Φ_N)^2 + λ1 Φ_Δ^2 + λ2 s_SFS^2"""
    return (1.0 - phi_N)**2 + lam1 * phi_Delta**2 + lam2 * s_SFS**2

# ------------------------------
# Parameter sanity checks
# ------------------------------
def test_random_scenario(num_trials=1000):
    np.random.seed(42)

    # Baseline Omega values (must be in [0,1])
    phi_N0 = np.random.uniform(0.4, 0.9)   # strategic connectivity
    phi_Delta0 = np.random.uniform(0.1, 0.5)  # information asymmetry

    # Mapping coefficients – must keep results in [0,1]
    eta1 = np.random.uniform(0.0, phi_N0)          # ensures Φ_N≥0
    eta2 = np.random.uniform(0.0, 1.0 - phi_Delta0)  # ensures Φ_Δ≤1

    # Correlation length base values (arbitrary positive)
    xi0_N = np.random.uniform(0.5, 5.0)
    xi0_Delta = np.random.uniform(0.5, 5.0)

    # SFS weighting parameters (non‑negative)
    alpha = np.random.uniform(0.0, 2.0)
    beta  = np.random.uniform(0.0, 2.0)
    gamma = np.random.uniform(0.0, 2.0)
    lambd = np.random.uniform(0.01, 0.5)   # decay per month

    # Cost weights
    lam1 = np.random.uniform(0.0, 2.0)
    lam2 = np.random.uniform(0.0, 2.0)

    for _ in range(num_trials):
        # ---- generate a random leak set ----
        n_leaks = np.random.randint(1, 6)
        leaks = []
        for __ in range(n_leaks):
            leaks.append({
                'C': np.random.randint(1, 6),   # criticality 1‑5
                'N': np.random.randint(1, 6),   # negligence 1‑5
                'D': np.random.uniform(0.0, 10.0), # dissemination scale
                'T': np.random.uniform(0.0, 24.0)  # months since pub
            })

        # ---- compute SFS ----
        sfs = compute_SFS(leaks, alpha, beta, gamma, lambd)
        assert sfs >= 0.0, f"SFS negative: {sfs}"

        # ---- map to Omega variables ----
        phi_N = map_phi_N(phi_N0, eta1, sfs)
        phi_Delta = map_phi_Delta(phi_Delta0, eta2, sfs)

        assert 0.0 <= phi_N <= 1.0, f"Φ_N out of bounds: {phi_N}"
        assert 0.0 <= phi_Delta <= 1.0, f"Φ_Δ out of bounds: {phi_Delta}"

        # ---- correlation lengths (safe form) ----
        xi_N, xi_D = correlation_lengths(xi0_N, xi0_Delta, sfs)
        assert xi_N > 0.0 and xi_D > 0.0, "Correlation length non‑positive"

        # ---- cost integrand non‑negative ----
        # For anomaly score we use a simple proxy: s_SFS = |SFS - mean|/std
        # Here we just set s_SFS = sfs (non‑negative) to test sign.
        s_SFS = sfs
        integrand = cost_integrand(phi_N, phi_Delta, s_SFS, lam1, lam2)
        assert integrand >= 0.0, f"Cost integrand negative: {integrand}"

        # ---- QP constraints from proposal ----
        assert sfs <= 10.0 + 1e-9, f"SFS exceeds bound: {sfs}"
        assert phi_N >= 0.3 - 1e-9, f"Φ_N below minimum: {phi_N}"
        assert phi_Delta <= 0.8 + 1e-9, f"Φ_Δ above maximum: {phi_Delta}"

    print(f"All {num_trials} random scenarios passed validation.")
    return True

# ------------------------------
# Run the test
# ------------------------------
if __name__ == "__main__":
    test_random_scenario()