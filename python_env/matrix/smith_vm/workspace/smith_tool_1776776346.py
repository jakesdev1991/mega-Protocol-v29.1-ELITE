# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for TPM‑Ω (Topological Persistence Monitor)
-------------------------------------------------------------------
This script checks that the refined TPM‑Ω integration respects the
core Omega invariants:
    • Φ_N  > 0
    • 0 ≤ Φ_Δ ≤ 1
    • ψ    = ln(φ_n/φ_n0) is finite
    • Entropy gauge A_μ = ∂_μ E₁ holds numerically
It uses synthetic backup data so that the test is deterministic.
"""

import numpy as np
from gudhi import RipsComplex   # pip install gudhi
import warnings

# ----------------------------------------------------------------------
# Helper functions (field‑theoretic formulas)
# ----------------------------------------------------------------------
def effective_mass(m0, lam, phi_bar):
    """m_eff^2 = m0^2 + 3 λ φ̄^2"""
    return np.sqrt(m0**2 + 3 * lam * phi_bar**2)

def stiffness_from_persistence(P1, E1, c_N=1.0, c_D=1.0):
    """
    Map persistence observables to stiffness lengths.
    We enforce: ξ_N = c_N * sqrt(P1) , ξ_Δ = c_D * sqrt(P1)
    (the product ξ_N ξ_Δ ∝ P1 as required).
    """
    xi_N = c_N * np.sqrt(np.maximum(P1, 0))
    xi_D = c_D * np.sqrt(np.maximum(P1, 0))
    return xi_N, xi_D

def Phi_N(xi_N, xi_D, eta1=0.5, eta2=0.3, PhiN0=1.0):
    """Φ_N^(topo) = Φ_N0 + η1 * (P1/P0) - η2 * (E1/E0)"""
    # Here we use the proxy P1/P0 ≈ ξ_N*ξ_D / (ξ_N0*ξ_D0)
    # and E1/E0 ≈ E1 (since we normalise E0=1 for the synthetic test)
    P_ratio = (xi_N * xi_D)  # assuming unit reference product
    E_ratio = E1             # E0 set to 1
    return PhiN0 + eta1 * P_ratio - eta2 * E_ratio

def Phi_Delta(xi_N, xi_D, eta3=0.4, eta4=0.2, PhiD0=0.2):
    """Φ_Δ^(topo) = Φ_Δ0 + η3|P1/P0-1| + η4|E1/E0-1|"""
    P_ratio = xi_N * xi_D
    E_ratio = E1
    return PhiD0 + eta3 * np.abs(P_ratio - 1.0) + eta4 * np.abs(E_ratio - 1.0)

def psi_from_stiffness(xi_N, xi_D, m_eff, m0=1.0):
    """ψ = ln( φ_n / φ_n0 ) with φ_n = m_eff/(m0*sqrt(ξ_N ξ_Δ))"""
    phi_n = m_eff / (m0 * np.sqrt(np.maximum(xi_N * xi_D, 1e-12)))
    phi_n0 = 1.0   # reference value (healthy state)
    return np.log(np.maximum(phi_n, 1e-12) / phi_n0)

def entropy_gauge(E1_series, dt=1.0):
    """Finite‑difference approximation of A_t = ∂_t E₁"""
    return np.gradient(E1_series, dt)

# ----------------------------------------------------------------------
# Synthetic backup point‑cloud generator
# ----------------------------------------------------------------------
def generate_backup_cloud(n_points=200, dim=5, corr_len=1.0, seed=42):
    """Generate a Gaussian cloud whose covariance encodes a correlation length."""
    rng = np.random.default_rng(seed)
    # Create a covariance matrix with off‑decay exp(-|i-j|/corr_len)
    cov = np.exp(-np.abs(np.subtract.outer(np.arange(dim), np.arange(dim))) / corr_len)
    points = rng.multivariate_normal(mean=np.zeros(dim), cov=cov, size=n_points)
    return points

# ----------------------------------------------------------------------
# Persistent homology → P₁, E₁
# ----------------------------------------------------------------------
def persistence_features(points, max_edge_length=2.0):
    """Return total persistence P₁ and persistence entropy E₁ for H₁."""
    rips = RipsComplex(points=points, max_edge_length=max_edge_length)
    st = rips.create_simplex_tree(max_dimension=2)
    st.compute_persistence()
    # Extract persistence pairs for H₁
    dgm = st.persistence_intervals_in_dimension(1)
    if len(dgm) == 0:
        return 0.0, 0.0
    lifespans = dgm[:, 1] - dgm[:, 0]          # d - b
    P1 = np.sum(lifespans)
    # Persistence entropy
    p = lifespans / P1
    # Avoid log(0)
    p = p[p > 0]
    E1 = -np.sum(p * np.log(p))
    return P1, E1

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_tpo():
    warnings.filterwarnings("ignore", category=UserWarning)

    # Synthetic backup sequence (sliding window of W=5 backups)
    W = 5
    P1_hist = []
    E1_hist = []
    PhiN_hist = []
    PhiD_hist = []
    psi_hist  = []
    A_hist    = []

    for w in range(W):
        # Vary correlation length to simulate approaching a Shredding Event
        corr_len = 1.0 - 0.15 * w   # decreasing connectivity
        cloud = generate_backup_cloud(corr_len=corr_len)
        P1, E1 = persistence_features(cloud)
        P1_hist.append(P1)
        E1_hist.append(E1)

        # Field quantities (use a fixed background field for the test)
        m0 = 1.0
        lam = 0.2
        phi_bar = 0.0   # spatial average of the synthetic cloud (zero‑mean)
        m_eff = effective_mass(m0, lam, phi_bar)

        xi_N, xi_D = stiffness_from_persistence(P1, E1)
        PhiN = Phi_N(xi_N, xi_D)
        PhiD = Phi_Delta(xi_N, xi_D)
        psi  = psi_from_stiffness(xi_N, xi_D, m_eff, m0)

        PhiN_hist.append(PhiN)
        PhiD_hist.append(PhiD)
        psi_hist.append(psi)

    # Entropy gauge (finite difference)
    A_hist = entropy_gauge(np.array(E1_hist), dt=1.0)

    # ------------------------------------------------------------------
    # Invariant checks
    # ------------------------------------------------------------------
    violations = []

    for i, (PhiN, PhiD, psi) in enumerate(zip(PhiN_hist, PhiD_hist, psi_hist)):
        if not (PhiN > 0):
            violations.append(f"Step {i}: Φ_N = {PhiN:.3f} ≤ 0")
        if not (0.0 <= PhiD <= 1.0):
            violations.append(f"Step {i}: Φ_Δ = {PhiD:.3f} outside [0,1]")
        if not np.isfinite(psi):
            violations.append(f"Step {i}: ψ = {psi} is non‑finite")
        # Optional: bound ψ to avoid extreme values (field theory expects |ψ|<~5)
        if abs(psi) > 5.0:
            violations.append(f"Step {i}: |ψ| = {abs(psi):.2f} unusually large")

    # Entropy gauge consistency: compare finite‑difference with analytic derivative
    # For our synthetic data we expect A_t ≈ (E1[t]-E1[t-1])/Δt
    for i in range(1, len(E1_hist)):
        analytic = (E1_hist[i] - E1_hist[i-1]) / 1.0
        numeric  = A_hist[i]
        if not np.isclose(analytic, numeric, rtol=1e-5, atol=1e-8):
            violations.append(f"Entropy gauge mismatch at step {i}: "
                              f"analytic={analytic:.6f}, numeric={numeric:.6f}")

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    if violations:
        raise AssertionError("\n".join(violations))
    else:
        print("✅ All Omega Protocol invariants satisfied for the synthetic test.")
        print(f"   Final Φ_N  = {PhiN_hist[-1]:.3f}")
        print(f"   Final Φ_Δ  = {PhiD_hist[-1]:.3f}")
        print(f"   Final ψ    = {psi_hist[-1]:.3f}")
        print(f"   Final A_t  = {A_hist[-1]:.6f}")

if __name__ == "__main__":
    validate_tpo()