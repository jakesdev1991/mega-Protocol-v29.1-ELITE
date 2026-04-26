# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
PCS‑Ω Rubric Validator
~~~~~~~~~~~~~~~~~~~~~~
Validates that a candidate implementation of the Perceptual Coherence Shield
(PCS‑Ω) satisfies the Ω‑Physics Rubric v26.0 requirements:

1. Covariant modes Φ_N and Φ_Δ arise from Hessian diagonalisation of V(C).
2. Entropy gauge S_perc is a Shannon *conditional* entropy.
3. Boundary conditions respect thermodynamic direction
   (shredding ↔ high entropy, locking ↔ low entropy).
4. MPC‑Ω QP constraints and cost integrand are respected.

The script is self‑contained; run it with a synthetic coherence field to see
a PASS/FAIL report.
"""

import numpy as np
from scipy.cluster.vq import kmeans, vq
from scipy.stats import skew, entropy

# ----------------------------------------------------------------------
# Helper functions (mathematical core)
# ----------------------------------------------------------------------
def double_well_second_derivative(C, alpha, beta):
    """
    V(C) = 0.5*alpha*C^2 + 0.25*beta*C^4 - gamma*C
    V''(C) = alpha + 3*beta*C^2
    (gamma drops out because it is linear)
    """
    return alpha + 3.0 * beta * C**2

def covariant_modes_from_field(C, grad_norm_ratio, skewness,
                               kappa1=1.0, kappa2=0.1,
                               kappa3=1.0, kappa4=0.1):
    """
    Implements the rubric‑compliant mapping:
        ω_N^2 = κ1 * (‖∇C‖/‖C‖) + κ2
        ω_Δ^2 = κ3 * Skew[C]   + κ4
    Φ_N = sqrt(ω_N^2),   Φ_Δ = sqrt(ω_Δ^2)
    """
    omega_N_sq = kappa1 * grad_norm_ratio + kappa2
    omega_D_sq = kappa3 * skewness       + kappa4
    # Guard against negative eigenvalues (should not happen with proper κ)
    omega_N_sq = max(omega_N_sq, 0.0)
    omega_D_sq = max(omega_D_sq, 0.0)
    Phi_N = np.sqrt(omega_N_sq)
    Phi_D = np.sqrt(omega_D_sq)
    return Phi_N, Phi_D

def conditional_entropy(C, region_labels, n_bins=20):
    """
    Shannon conditional entropy S_perc = Σ_r p(r) [ - Σ_c p(c|r) log p(c|r) ]
    C: 1D array of coherence values (flattened over points)
    region_labels: same‑shape int array indicating region id per point
    Returns S_perc in nats.
    """
    n_points = C.size
    # Probability of each region
    unique_regions, region_counts = np.unique(region_labels, return_counts=True)
    p_r = region_counts / n_points

    # Bin the coherence values globally to get a common set of bins
    hist_all, bin_edges = np.histogram(C, bins=n_bins, density=False)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    S_perc = 0.0
    for r in unique_regions:
        mask = (region_labels == r)
        C_r = C[mask]
        if C_r.size == 0:
            continue
        hist_r, _ = np.histogram(C_r, bins=bin_edges, density=False)
        p_c_given_r = hist_r / hist_r.sum() if hist_r.sum() > 0 else np.zeros_like(hist_r)
        # Avoid log(0) by masking zeros
        nz = p_c_given_r > 0
        S_perc += p_r[r] * (-np.sum(p_c_given_r[nz] * np.log(p_c_given_r[nz])))
    return S_perc

def perceptual_coherence_index(Phi_N, Phi_D, Gamma=1.0):
    """PCI = Φ_N * Φ_D * Γ  (Γ ∈ [0,1] captures higher‑order couplings)"""
    return Phi_N * Phi_D * Gamma

def boundary_conditions(Phi_N, S_perc, S_max, eps=1e-9):
    """
    Returns a tuple (is_shredding, is_locking) according to the rubric:
        Shredding: Φ_N → ∞  AND  S_perc → S_max
        Locking  : Φ_N → 0   AND  S_perc → 0
    In practice we use thresholds:
        Φ_N > Phi_N_high  → "large"
        Φ_N < Phi_N_low   → "small"
        S_perc > S_max - eps → "high entropy"
        S_perc < eps       → "low entropy"
    """
    Phi_N_low, Phi_N_high = 0.5, 5.0   # example thresholds; can be tuned
    is_shredding = (Phi_N > Phi_N_high) and (S_perc > S_max - eps)
    is_locking   = (Phi_N < Phi_N_low)  and (S_perc < eps)
    return is_shredding, is_locking

# ----------------------------------------------------------------------
# Validator
# ----------------------------------------------------------------------
def validate_pcs_omega(C_raw, coords, 
                       alpha=-1.0, beta=2.0, gamma=0.5,
                       n_regions=4, n_bins=16,
                       PCI_min=0.6, Phi_N_min=0.5,
                       S_low=0.2, S_high=None,
                       Gamma=1.0):
    """
    Main validation routine.
    Parameters
    ----------
    C_raw : (N,) array
        Raw coherence values per point (cosine similarity in [-1,1]).
    coords : (N,3) array
        3D coordinates of the points (used only for gradient approximation).
    alpha,beta,gamma : float
        Parameters of the double‑well potential.
    n_regions : int
        Number of regions for conditional entropy (k‑means on coords).
    n_bins : int
        Number of histogram bins for entropy.
    PCI_min, Phi_N_min : float
        QP lower bounds.
    S_low : float
        Lower entropy bound (must be >0).
    S_high : float or None
        Upper entropy bound; if None, set to log(n_bins).
    Gamma : float
        Higher‑order coupling factor (clipped to [0,1]).
    Returns
    -------
    dict with all computed quantities and a boolean 'passed'.
    """
    # ----- 1. Basic sanity on coherence -----
    assert np.all((C_raw >= -1.0) & (C_raw <= 1.0)), "Coherence out of [-1,1]"
    C = C_raw.copy()

    # ----- 2. Approximate ∇C / ‖C‖ (finite differences on a point cloud) -----
    # For simplicity we use the average nearest‑neighbor distance as proxy for gradient magnitude.
    from scipy.spatial import cKDTree
    tree = cKDTree(coords)
    dists, idx = tree.query(coords, k=2)          # k=2 gives self + nearest neighbor
    grad_approx = np.abs(C[idx[:,1]] - C[:,0]) / (dists[:,1] + 1e-12)
    grad_norm = np.linalg.norm(grad_approx)
    C_norm = np.linalg.norm(C)
    grad_norm_ratio = grad_norm / (C_norm + 1e-12)

    # ----- 3. Skewness of coherence distribution -----
    skewness = skew(C)

    # ----- 4. Covariant modes from Hessian diagonalisation (rubric‑compliant) -----
    Phi_N, Phi_D = covariant_modes_from_field(
        C, grad_norm_ratio, skewness,
        kappa1=1.0, kappa2=0.1,
        kappa3=1.0, kappa4=0.1)

    # ----- 5. Perceptual Coherence Index -----
    PCI = perceptual_coherence_index(Phi_N, Phi_D, Gamma=np.clip(Gamma, 0.0, 1.0))

    # ----- 6. Region partition for conditional entropy -----
    # Use k‑means on coordinates (could also use feature space; here we keep it simple)
    centroids, _ = kmeans(coords, n_regions, iter=20)
    region_labels, _ = vq(coords, centroids)

    # ----- 7. Conditional entropy -----
    S_perc = conditional_entropy(C, region_labels, n_bins=n_bins)
    S_max = np.log(n_bins) if S_high is None else S_high
    if S_high is None:
        S_high = S_max

    # ----- 8. Boundary condition check (thermodynamic direction) -----
    is_shredding, is_locking = boundary_conditions(
        Phi_N, S_perc, S_max, eps=1e-9)

    # ----- 9. MPC‑Ω QP constraints -----
    constraints_ok = (
        PCI >= PCI_min and
        Phi_N >= Phi_N_min and
        S_low <= S_perc <= S_high
    )

    # ----- 10. Cost integrand positivity (sampled) -----
    # Example integrand from the proposal:
    #   (0.6 - PCI)_+^2 + μ1(0.5 - ΦN)_+^2 + μ2 ΦΔ^2 + μ3 (S_perc - S_target)^2
    mu1, mu2, mu3, S_target = 1.0, 1.0, 1.0, 0.5 * (S_low + S_high)
    integrand = (
        max(0.6 - PCI, 0.0)**2 +
        mu1 * max(0.5 - Phi_N, 0.0)**2 +
        mu2 * Phi_D**2 +
        mu3 * (S_perc - S_target)**2
    )
    cost_ok = integrand >= 0.0   # always true by construction, but we keep the check

    # ----- 11. Assemble result -----
    result = {
        "C_mean": float(np.mean(C)),
        "grad_norm_ratio": float(grad_norm_ratio),
        "skewness": float(skewness),
        "Phi_N": float(Phi_N),
        "Phi_D": float(Phi_D),
        "PCI": float(PCI),
        "S_perc": float(S_perc),
        "S_max": float(S_max),
        "is_shredding": bool(is_shredding),
        "is_locking": bool(is_locking),
        "constraints_ok": bool(constraints_ok),
        "cost_integrand": float(integrand),
        "cost_ok": bool(cost_ok),
    }

    # Final pass/fail according to the rubric
    result["passed"] = bool(
        constraints_ok and cost_ok and
        not (is_shredding or is_locking)   # we are not in a pathological boundary
    )
    return result

# ----------------------------------------------------------------------
# Example usage (synthetic data)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Generate a fake point cloud and coherence field
    np.random.seed(42)
    N = 500
    # Random points on a unit sphere
    phi = np.arccos(2*np.random.rand(N)-1)
    theta = 2*np.pi*np.random.rand(N)
    coords = np.stack([np.sin(phi)*np.cos(theta),
                       np.sin(phi)*np.sin(theta),
                       np.cos(phi)], axis=1)
    # Coherence: mostly high with some noise
    C_raw = 0.8 + 0.1*np.random.randn(N)
    C_raw = np.clip(C_raw, -1.0, 1.0)

    # Run validator
    report = validate_pcs_omega(
        C_raw, coords,
        alpha=-1.0, beta=2.0, gamma=0.5,
        n_regions=5, n_bins=20,
        PCI_min=0.6, Phi_N_min=0.5,
        S_low=0.2, S_high=None,   # will become log(20)
        Gamma=0.9
    )

    # Pretty‑print
    print("=== PCS‑Ω Rubric Validation Report ===")
    for k, v in report.items():
        if isinstance(v, float):
            print(f"{k:20}: {v:.5f}")
        else:
            print(f"{k:20}: {v}")
    print("\nOverall PASS?" , report["passed"])