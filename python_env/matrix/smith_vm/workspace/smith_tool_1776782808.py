# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCS‑Ω Invariant Validator
-------------------------
Given a set of microcapsule states, compute the Omega‑protocol invariants
and enforce the hard constraints:
    Φ_N >= 0.4
    Φ_Δ <= 0.7
Optionally also check stiffness signs.

The script is self‑contained and uses only numpy & scipy.
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy
from scipy.optimize import minimize

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def pearson_corr_matrix(x):
    """Return Pearson correlation matrix of 1‑D array x."""
    # Center and scale
    x_centered = x - np.mean(x)
    x_std = np.std(x)
    if x_std == 0:
        return np.ones_like(x)[:, None] * np.ones_like(x)[None, :]  # all ones
    z = x_centered / x_std
    return np.dot(z[:, None], z[None, :])

def average_pairwise_corr(corr_mat):
    """Average of off‑diagonal entries."""
    N = corr_mat.shape[0]
    if N < 2:
        return np.nan
    return (np.sum(corr_mat) - np.trace(corr_mat)) / (N * (N - 1))

def jensen_shannon_divergence(p, q):
    """JSD between two discrete distributions (already normalized)."""
    p = np.asarray(p)
    q = np.asarray(q)
    # Avoid zeros
    eps = 1e-12
    p = p + eps
    q = q + eps
    p /= p.sum()
    q /= q.sum()
    m = 0.5 * (p + q)
    return 0.5 * (entropy(p, m) + entropy(q, m))

def variogram_concentration(pos, c, max_lag=None, n_bins=10):
    """
    Experimental isotropic variogram of concentration field.
    Returns bin centers and variogram values.
    """
    # Pairwise distances
    dists = squareform(pdist(pos))
    # Pairwise absolute differences in concentration
    diff = np.abs(np.subtract.outer(c, c))
    # Extract upper triangle (excluding diagonal)
    triu_idx = np.triu_indices_from(dists, k=1)
    dists_vec = dists[triu_idx]
    diff_vec = diff[triu_idx]

    if max_lag is None:
        max_lag = np.max(dists_vec)

    bins = np.linspace(0, max_lag, n_bins + 1)
    which_bin = np.digitize(dists_vec, bins) - 1
    # Bin 0 corresponds to [0, first_edge); we ignore empty bins
    gamma = []
    bin_centers = []
    for b in range(n_bins):
        mask = which_bin == b
        if np.any(mask):
            gamma.append(np.mean(diff_vec[mask]))
            bin_centers.append(0.5 * (bins[b] + bins[b + 1]))
        else:
            gamma.append(np.nan)
            bin_centers.append(0.5 * (bins[b] + bins[b + 1]))
    return np.array(bin_centers), np.array(gamma)

def fit_variogram_model(bin_centers, gamma, model='linear'):
    """
    Very simple variogram model fitting to extract a correlation length.
    For demonstration we fit an exponential model:
        γ(h) = c0 + c1 * (1 - exp(-h / a))
    where a is the correlation length (range).
    Returns a (correlation length) and nugget c0.
    """
    from scipy.optimize import curve_fit
    def exp_model(h, c0, c1, a):
        return c0 + c1 * (1 - np.exp(-h / a))
    # Initial guess: nugget ~ small, sill ~ variance, a ~ median distance
    p0 = [np.nanmin(gamma), np.nanmax(gamma)-np.nanmin(gamma), np.median(bin_centers)]
    try:
        popt, _ = curve_fit(exp_model, bin_centers, gamma, p0=p0, maxfev=5000)
        c0, c1, a = popt
        return max(a, 1e-6)   # ensure positive
    except Exception:
        # fallback: use distance at which gamma reaches 95% of max
        sill = np.nanmax(gamma) - np.nanmin(gamma)
        target = np.nanmin(gamma) + 0.95 * sill
        idx = np.where(gamma >= target)[0]
        if len(idx) > 0:
            return bin_centers[idx[0]]
        else:
            return bin_centers[-1]

def position_entropy(pos, voxel_size=1.0):
    """Shannon entropy of capsule positions discretized into voxels."""
    # Determine grid bounds with a small margin
    mins = np.min(pos, axis=0) - voxel_size
    maxs = np.max(pos, axis=0) + voxel_size
    # Create bins
    bins = [np.arange(mins[i], maxs[i] + voxel_size, voxel_size) for i in range(3)]
    hist, _ = np.histogramdd(pos, bins=bins)
    p = hist.ravel()
    p = p[p > 0]
    p /= p.sum()
    return entropy(p, base=2)  # bits

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_mcs_omega(c, pos, sensor,
                       phi_n_min=0.4,
                       phi_d_max=0.7,
                       xi_n_min=0.0,
                       xi_d_tol=0.5,
                       voxel_size=1.0,
                       n_bootstrap=20):
    """
    Compute Omega invariants and test constraints.
    Returns:
        ok (bool): True if all hard constraints satisfied.
        stats (dict): All computed quantities.
    """
    N = len(c)
    if N < 2:
        raise ValueError("Need at least two capsules to compute correlations.")

    # ----- Φ_N : average pairwise correlation of concentrations -----
    corr_mat = pearson_corr_matrix(c)
    phi_n = average_pairwise_corr(corr_mat)

    # ----- Φ_Δ : JSD between core and edge sensor distributions -----
    # Define core vs edge by distance from swarm centroid
    centroid = np.mean(pos, axis=0)
    dist_to_cent = np.linalg.norm(pos - centroid, axis=1)
    median_dist = np.median(dist_to_cent)
    core_mask = dist_to_cent <= median_dist
    edge_mask = dist_to_cent > median_dist

    # For each sensor type, build a histogram, then average JSD across types
    M = sensor.shape[1]
    jsd_vals = []
    for m in range(M):
        # Build normalized histograms (10 bins)
        hist_core, _ = np.histogram(sensor[core_mask, m], bins=10, density=True)
        hist_edge, _ = np.histogram(sensor[edge_mask, m], bins=10, density=True)
        # Ensure same bin edges (use global min/max)
        global_min = np.min(sensor[:, m])
        global_max = np.max(sensor[:, m])
        bins = np.linspace(global_min, global_max, 11)
        hist_core, _ = np.histogram(sensor[core_mask, m], bins=bins, density=True)
        hist_edge, _ = np.histogram(sensor[edge_mask, m], bins=bins, density=True)
        jsd_vals.append(jensen_shannon_divergence(hist_core, hist_edge))
    phi_d = np.mean(jsd_vals)

    # ----- Correlation length ψ and its derivatives -----
    # Experimental variogram of concentration field
    bin_centers, gamma = variogram_concentration(pos, c, n_bins=12)
    xi = fit_variogram_model(bin_centers, gamma)   # correlation length
    # Reference length: median nearest‑neighbor distance
    nn_dists = np.min(squareform(pdist(pos)) + np.eye(N)*np.inf, axis=1)
    xi0 = np.median(nn_dists)
    psi = np.log(xi / xi0)

    # To get derivatives we bootstrap subsets and recompute (phi_n, phi_d, psi)
    phi_n_boot = []
    phi_d_boot = []
    psi_boot = []
    rng = np.random.default_rng(seed=42)
    for _ in range(n_bootstrap):
        idx = rng.choice(N, size=max(2, N//2), replace=False)
        c_b = c[idx]
        pos_b = pos[idx]
        sensor_b = sensor[idx]

        # Φ_N
        corr_b = pearson_corr_matrix(c_b)
        phi_n_b = average_pairwise_corr(corr_b)
        phi_n_boot.append(phi_n_b)

        # Φ_Δ (reuse same core/edge split based on bootstrap centroid)
        cent_b = np.mean(pos_b, axis=0)
        dist_b = np.linalg.norm(pos_b - cent_b, axis=1)
        med_b = np.median(dist_b)
        core_b = dist_b <= med_b
        edge_b = dist_b > med_b
        jsd_b = []
        for m in range(sensor_b.shape[1]):
            global_min = np.min(sensor_b[:, m])
            global_max = np.max(sensor_b[:, m])
            bins = np.linspace(global_min, global_max, 11)
            hc, _ = np.histogram(sensor_b[core_b, m], bins=bins, density=True)
            he, _ = np.histogram(sensor_b[edge_b, m], bins=bins, density=True)
            jsd_b.append(jensen_shannon_divergence(hc, he))
        phi_d_boot.append(np.mean(jsd_b))

        # ψ
        bin_c, gam_c = variogram_concentration(pos_b, c_b, n_bins=12)
        xi_b = fit_variogram_model(bin_c, gam_c)
        nn_b = np.min(squareform(pdist(pos_b)) + np.eye(len(c_b))*np.inf, axis=1)
        xi0_b = np.median(nn_b)
        psi_b = np.log(xi_b / xi0_b)
        psi_boot.append(psi_b)

    phi_n_boot = np.array(phi_n_boot)
    phi_d_boot = np.array(phi_d_boot)
    psi_boot = np.array(psi_boot)

    # Sort by psi to compute derivative via finite differences
    order = np.argsort(psi_boot)
    psi_sorted = psi_boot[order]
    phi_n_sorted = phi_n_boot[order]
    phi_d_sorted = phi_d_boot[order]

    # Central differences for interior points, forward/backward at edges
    dphi_n_dpsi = np.gradient(phi_n_sorted, psi_sorted)
    dphi_d_dpsi = np.gradient(phi_d_sorted, psi_sorted)
    # Use median derivative as robust estimate
    xi_n = np.median(dphi_n_dpsi)
    xi_d = np.median(dphi_d_dpsi)

    # ----- Entropy gauge S_h -----
    s_h = position_entropy(pos, voxel_size=voxel_size)

    # ----- Constraint checks -----
    ok = True
    violations = []

    if phi_n < phi_n_min:
        ok = False
        violations.append(f"Φ_N={phi_n:.3f} < min {phi_n_min}")
    if phi_d > phi_d_max:
        ok = False
        violations.append(f"Φ_Δ={phi_d:.3f} > max {phi_d_max}")
    if xi_n < xi_n_min:
        ok = False
        violations.append(f"ξ_N={xi_n:.3f} < min {xi_n_min}")
    if np.abs(xi_d) > xi_d_tol:
        ok = False
        violations.append(f"|ξ_D|={np.abs(xi_d):.3f} > tol {xi_d_tol}")

    stats = {
        "Φ_N": phi_n,
        "Φ_Δ": phi_d,
        "ψ": psi,
        "ξ_N": xi_n,
        "ξ_Δ": xi_d,
        "S_h": s_h,
        "correlation length ξ": xi,
        "reference ξ0": xi0,
        "violations": violations
    }
    return ok, stats

# ----------------------------------------------------------------------
# Example usage with synthetic data (you can replace this with real data)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(123)
    N = 50  # number of capsules
    # Random positions in a cube [0,30]^3
    pos = np.random.uniform(0, 30, size=(N, 3))
    # Concentrations: higher in a spherical tumor region at (15,15,15) radius 5
    tumor_center = np.array([15., 15., 15.])
    tumor_radius = 5.0
    dist_to_tumor = np.linalg.norm(pos - tumor_center, axis=1)
    base_conc = 0.1
    tumor_boost = 0.9 * np.exp(-dist_to_tumor**2 / (2 * tumor_radius**2))
    c = base_conc + tumor_boost + 0.05 * np.random.randn(N)  # add noise
    c = np.clip(c, 0, None)  # non-negative

    # Two dummy sensor types: pH (lower in tumor) and temperature (slightly higher)
    sensor = np.zeros((N, 2))
    sensor[:, 0] = 7.4 - 0.5 * tumor_boost / 0.9 + 0.1 * np.random.randn(N)  # pH
    sensor[:, 1] = 37.0 + 0.3 * tumor_boost / 0.9 + 0.1 * np.random.randn(N)  # Temp

    ok, stats = validate_mcs_omega(c, pos, sensor)
    print("=== MCS‑Ω Invariant Validation ===")
    for k, v in stats.items():
        if k != "violations":
            print(f"{k:12}: {v}")
    print("\nViolations:", stats["violations"])
    print("\nOverall PASS (Ω constraints satisfied):", ok)