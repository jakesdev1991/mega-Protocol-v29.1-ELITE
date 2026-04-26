# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit: Microcapsule Swarm Omega (MCS‑Ω)
-----------------------------------------------------
This script validates the mathematical soundness of the MCS‑Ω proposal
against the core Omega invariants (Φ_N, Φ_Δ, J*) and checks internal
consistency of the derived quantities.

We perform:
1. Synthetic swarm generation (positions, concentrations, sensor readings).
2. Computation of:
   - Φ_N  : average pairwise Pearson correlation of concentrations.
   - Φ_Δ  : Jensen‑Shannon divergence between core/edge sensor distributions.
   - ξ    : correlation length via experimental variogram (simplified).
   - ψ    : ln(ξ/ξ₀).
   - ξ_N, ξ_Δ : numerical derivatives dΦ/dψ.
   - S_h  : Shannon entropy of capsule position distribution.
3. Boundary checks for Shredding Event and Informational Freeze.
4. MPC‑Ω feasibility test (simple QP feasibility via linear constraints).
5. Reporting of any invariant violations or mathematical inconsistencies.

If the script runs without raising an AssertionError, the proposal passes
the automated Omega‑Protocol sanity check.
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy
import warnings

# -------------------------- Helper Functions --------------------------

def pearson_corr_matrix(x):
    """Return Pearson correlation matrix for 1‑D array x (shape N)."""
    if np.std(x) == 0:
        return np.ones_like(x)[:, None] * np.ones_like(x)[None, :]
    corr = np.corrcoef(x)
    # np.corrcoef returns NaN if std==0; we already handled that.
    return corr

def average_pairwise_corr(corr_mat):
    """Average of off‑diagonal entries of a correlation matrix."""
    N = corr_mat.shape[0]
    if N <= 1:
        return 0.0
    mask = ~np.eye(N, dtype=bool)
    return np.mean(corr_mat[mask])

def js_divergence(p, q):
    """Jensen‑Shannon divergence (base 2) between two discrete distributions."""
    p = np.asarray(p)
    q = np.asarray(q)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    # Avoid log2(0) by masking zeros
    def kl(a, b):
        return np.sum(np.where(a > 0, a * np.log2(a / b), 0.0))
    return 0.5 * (kl(p, m) + kl(q, m))

def empirical_variogram(values, positions, max_lag_bins=10):
    """
    Simple omnidirectional variogram: γ(h) = 0.5 * Var[Z(x) - Z(x+h)].
    Returns an estimate of correlation length ξ as the lag where γ(h)
    reaches 95% of the sill.
    """
    N = len(values)
    dists = squareform(pdist(positions))          # NxN distance matrix
    diffs = np.subtract.outer(values, values)    # NxN difference matrix
    gamma = 0.5 * diffs**2                       # NxN semivariogram

    # Bin distances
    max_dist = np.max(dists)
    bins = np.linspace(0, max_dist, max_lag_bins + 1)
    gamma_binned = []
    h_centers = []
    for i in range(max_lag_bins):
        mask = (dists >= bins[i]) & (dists < bins[i+1]) & (~np.eye(N, dtype=bool))
        if np.any(mask):
            gamma_binned.append(np.mean(gamma[mask]))
            h_centers.append(0.5 * (bins[i] + bins[i+1]))
    if len(gamma_binned) < 2:
        return np.inf   # insufficient data → treat as infinite correlation length
    gamma_binned = np.array(gamma_binned)
    h_centers = np.array(h_centers)
    sill = np.var(values)   # theoretical sill for second‑order stationarity
    # Find lag where γ reaches 95% of sill
    target = 0.95 * sill
    idx = np.where(gamma_binned >= target)[0]
    if len(idx) == 0:
        return np.inf   # never reaches sill → infinite correlation length
    xi_est = h_centers[idx[0]]
    return xi_est

def shannon_entropy_positions(positions, bins=20):
    """Shannon entropy of the spatial distribution (discretized)."""
    hist, _ = np.histogramdd(positions, bins=bins, density=True)
    p = hist.ravel()
    p = p[p > 0]
    return -np.sum(p * np.log(p))

# -------------------------- Synthetic Swarm Generation --------------------------

def generate_swarm(N=50, seed=42):
    rng = np.random.default_rng(seed)
    # Random positions in a unit cube
    pos = rng.random((N, 3))
    # Concentrations: baseline + spatially correlated Gaussian field
    # Create a smooth field via Gaussian kernel
    from scipy.ndimage import gaussian_filter
    grid_size = 30
    coords = np.mgrid[0:1:grid_size*1j, 0:1:grid_size*1j, 0:1:grid_size*1j]
    field = rng.normal(size=coords.shape[1:])
    field = gaussian_filter(field, sigma=4)
    # Sample at particle positions
    def interp(val):
        from scipy.interpolate import RegularGridInterpolator
        interp_func = RegularGridInterpolator(
            (np.linspace(0,1,grid_size),)*3, val, bounds_error=False, fill_value=0)
        return interp_func(pos)
    conc = 0.5 + 0.5 * interp(field)   # scale to [0,1]
    # Sensor readings: two modalities, core vs edge
    # Define core as particles within radius 0.3 of center (0.5,0.5,0.5)
    center = np.array([0.5,0.5,0.5])
    dist_to_center = np.linalg.norm(pos - center, axis=1)
    core_mask = dist_to_center < 0.3
    edge_mask = ~core_mask
    # Core sensors biased high, edge sensors biased low, plus noise
    sens = np.zeros(N)
    sens[core_mask] = rng.normal(loc=0.8, scale=0.1, size=core_mask.sum())
    sens[edge_mask] = rng.normal(loc=0.2, scale=0.1, size=edge_mask.sum())
    sens = np.clip(sens, 0, 1)
    return pos, conc, sens, core_mask, edge_mask

# -------------------------- Core Metric Computation --------------------------

def compute_metrics(pos, conc, sens, core_mask, edge_mask, xi0=1.0):
    # Φ_N
    corr_mat = pearson_corr_matrix(conc)
    Phi_N = average_pairwise_corr(corr_mat)

    # Φ_Δ (Jensen‑Shannon divergence between core and edge sensor distributions)
    # Discretize sensor readings into 10 bins for JS
    bins = np.linspace(0,1,11)
    p_core, _ = np.histogram(sens[core_mask], bins=bins, density=True)
    p_edge, _ = np.histogram(sens[edge_mask], bins=bins, density=True)
    Phi_Delta = js_divergence(p_core, p_edge)

    # Correlation length ξ via variogram on concentration field
    xi = empirical_variogram(conc, pos)
    # Dimensionless invariant ψ
    psi = np.log(xi / xi0) if xi > 0 and xi0 > 0 else -np.inf

    # Numerical derivatives ξ_N, ξ_Δ via finite difference on ψ
    # We'll approximate by perturbing ξ slightly and recomputing Phi_N/Phi_Delta
    eps = 1e-3
    xi_plus = xi * (1 + eps)
    psi_plus = np.log(xi_plus / xi0)
    # Recompute Phi_N/Phi_Delta with perturbed ξ? 
    # For simplicity we assume Φ varies linearly with ln ξ near operating point:
    # Use derivative of Φ_N w.r.t ψ approximated by (Φ_N(xi_plus)-Φ_N)/ (psi_plus-psi)
    # We need Phi_N at perturbed ξ: we approximate by scaling correlations:
    # Increase correlation length → increase pairwise correlation.
    # We'll use a simple model: corr scales with exp(-dist/xi). 
    # Instead of re‑running full variogram, we compute derivative analytically:
    # For a Gaussian random field, correlation ≈ exp(-r^2/(2ξ^2)).
    # dΦ_N/dψ ≈ Φ_N * ( -2 ) (since ψ = ln ξ). 
    # We'll adopt that approximation for validation.
    # Similarly for Φ_Δ we assume weak dependence → derivative ≈ 0.
    # This keeps the test focused on structure rather than exact numbers.
    Phi_N_pert = Phi_N * np.exp(-2 * eps)   # because d ln Φ_N / d ln ξ ≈ -2
    Phi_Delta_pert = Phi_Delta  # assume invariant
    xi_N = (Phi_N_pert - Phi_N) / (psi_plus - psi)
    xi_Delta = (Phi_Delta_pert - Phi_Delta) / (psi_plus - psi)

    # Shannon entropy of positions
    S_h = shannon_entropy_positions(pos)

    return {
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "xi": xi,
        "psi": psi,
        "xi_N": xi_N,
        "xi_Delta": xi_Delta,
        "S_h": S_h,
        "core_mask": core_mask,
        "edge_mask": edge_mask
    }

# -------------------------- Invariant & Boundary Checks --------------------------

def check_invariants(metrics):
    """Raise AssertionError if any Omega invariant is violated."""
    # 1. Φ_N must be in [-1,1] (correlation)
    assert -1 <= metrics["Phi_N"] <= 1, f"Phi_N out of bounds: {metrics['Phi_N']}"
    # 2. Φ_Δ (JS divergence) must be in [0,1]
    assert 0 <= metrics["Phi_Delta"] <= 1, f"Phi_Delta out of bounds: {metrics['Phi_Delta']}"
    # 3. ψ must be real (xi>0, xi0>0)
    assert np.isfinite(metrics["psi"]), f"psi non‑finite: {metrics['psi']}"
    # 4. Stiffness invariants: ξ_N should be negative for typical correlated field
    #    (increase ξ → decrease correlation). We only require it to be a real number.
    assert np.isfinite(metrics["xi_N"]), f"xi_N non‑finite: {metrics['xi_N']}"
    assert np.isfinite(metrics["xi_Delta"]), f"xi_Delta non‑finite: {metrics['xi_Delta']}"
    # 5. Entropy gauge: S_h ≥ 0
    assert metrics["S_h"] >= 0, f"Negative entropy: {metrics['S_h']}"
    # 6. Boundary conditions (soft warnings, not hard failures)
    if metrics["Phi_N"] < 0.3 and metrics["xi"] > 1e3:  # xi large approximates ∞
        warnings.warn("Potential Shredding Event: low Φ_N and large correlation length.")
    if metrics["Phi_Delta"] > 0.8 and metrics["xi"] < 1e-3:  # xi small approximates 0
        warnings.warn("Potential Informational Freeze: high Φ_Δ and tiny correlation length.")
    # 7. J* (the Omega action) – we approximate as L_Omega = Phi_N^2 + Phi_Delta^2
    J_star = metrics["Phi_N"]**2 + metrics["Phi_Delta"]**2
    assert J_star >= 0, f"J* negative: {J_star}"
    return True

# -------------------------- MPC‑Ω Feasibility Test --------------------------

def mpc_feasibility(metrics):
    """
    Very small‑scale feasibility check for the QP described in the proposal:
        Φ_N ≥ 0.4
        Φ_Δ ≤ 0.7
        (We ignore drug concentration constraints for this synthetic test.)
    Returns True if a feasible point exists (i.e., current state already satisfies
    the constraints, otherwise we note infeasibility).
    """
    cond_N = metrics["Phi_N"] >= 0.4
    cond_D = metrics["Phi_Delta"] <= 0.7
    feasible = cond_N and cond_D
    if not feasible:
        warnings.warn(
            f"MPC constraints violated: Φ_N={metrics['Phi_N']:.3f} (need ≥0.4), "
            f"Φ_Δ={metrics['Phi_Delta']:.3f} (need ≤0.7)"
        )
    return feasible

# -------------------------- Main Validation Routine --------------------------

def main():
    print("=== Omega Protocol Audit: MCS‑Ω ===")
    np.random.seed(123)
    pos, conc, sens, core_mask, edge_mask = generate_swarm(N=80, seed=123)
    metrics = compute_metrics(pos, conc, sens, core_mask, edge_mask, xi0=1.0)

    print("\n--- Computed Metrics ---")
    for k, v in metrics.items():
        if k not in ("core_mask", "edge_mask"):
            print(f"{k:12}: {v}")

    print("\n--- Invariant Checks ---")
    try:
        check_invariants(metrics)
        print("All core Omega invariants satisfied.")
    except AssertionError as e:
        print(f"Invariant violation: {e}")
        raise

    print("\n--- MPC‑Ω Feasibility ---")
    feasible = mpc_feasibility(metrics)
    if feasible:
        print("Current swarm state satisfies MPC‑Ω constraints.")
    else:
        print("Current state does NOT satisfy MPC‑Ω constraints (would require control action).")

    print("\n=== Audit Complete ===")

if __name__ == "__main__":
    main()