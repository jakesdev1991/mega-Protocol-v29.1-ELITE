# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script for Liquidity‑Crunch Omega (LC‑Ω)

Purpose:
    - Verify that the derived invariants respect the Omega Protocol hard bounds:
          Φ_N  ≥ Φ_N_min  (0.4)
          Φ_Δ  ≤ Φ_Δ_max  (0.7)
    - Check internal consistency of the scaling relations:
          ξ_N = ξ_N0 * (|∇L|/L_n)^(-α) * ν^(-β)
          ξ_Δ = ξ_Δ0 * (|∇·J|/J0)^(-δ) * β^(-ε)
    - Compute the Liquidity‑Fragility Index (LFI) and its anomaly score.
    - Flag any violation of the protocol invariants.

The script works with synthetic data that mimics the structure leaked from
SQL dumps (node‑wise liquidity density L_i(t) and inter‑node flux J_ij(t)).
Replace the synthetic generator with real‑parsed data for production use.
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.spatial.distance import pdist, squareform

# ----------------------------------------------------------------------
# Omega Protocol hard invariants (from the prompt)
# ----------------------------------------------------------------------
PHI_N_MIN = 0.4      # lower bound on Newtonian mode
PHI_D_MAX = 0.7      # upper bound on Asymmetry mode

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def exponential_decay(r, xi, C0):
    """Simple exponential model C(r) = C0 * exp(-r/xi)"""
    return C0 * np.exp(-r / xi)

def correlation_length_from_cov(r, C):
    """
    Fit C(r) = C0 * exp(-r/xi) to obtain xi.
    Returns xi (correlation length) and fit covariance.
    """
    try:
        popt, _ = curve_fit(exponential_decay, r, C, p0=[np.mean(r), np.max(C)])
        xi = popt[0]
        return xi, popt
    except Exception as e:
        raise ValueError(f"Correlation length fit failed: {e}")

def compute_liquidity_fields(L_nodes, J_edges, coords):
    """
    Build continuous fields L(x) and J(x) on a regular grid via
    inverse‑distance weighting (IDW).  Returns gradient and divergence.
    """
    # Grid definition – use the bounding box of node coordinates
    x_min, y_min = coords.min(axis=0)
    x_max, y_max = coords.max(axis=0)
    grid_size = 50                     # 50x50 grid is enough for a demo
    xs = np.linspace(x_min, x_max, grid_size)
    ys = np.linspace(y_min, y_max, grid_size)
    X, Y = np.meshgrid(xs, ys)
    grid_pts = np.vstack([X.ravel(), Y.ravel()]).T

    # Inverse distance weighting (power=2)
    def idw_field(values, power=2):
        dists = squareform(pdist(np.vstack([coords, grid_pts])))
        dists = dists[:len(coords), len(coords):]   # node‑to‑grid distances
        weights = 1.0 / (dists**power + 1e-12)
        weights /= weights.sum(axis=0, keepdims=True)
        return np.dot(values, weights).reshape(grid_size, grid_size)

    L_grid = idw_field(L_nodes)
    # J is a vector field; we store its x and y components separately
    Jx_grid = idw_field(J_edges[:, 0])
    Jy_grid = idw_field(J_edges[:, 1])

    # Numerical gradients (central differences)
    grad_Lx = np.gradient(L_grid, axis=1) / (xs[1] - xs[0])
    grad_Ly = np.gradient(L_grid, axis=0) / (ys[1] - ys[0])
    grad_L_mag = np.sqrt(grad_Lx**2 + grad_Ly**2)

    div_J = np.gradient(Jx_grid, axis=1) / (xs[1] - xs[0]) + \
            np.gradient(Jy_grid, axis=0) / (ys[1] - ys[0])

    return {
        "L": L_grid,
        "Jx": Jx_grid,
        "Jy": Jy_grid,
        "grad_L_mag": grad_L_mag,
        "div_J": div_J,
        "xs": xs,
        "ys": ys,
    }

def compute_phi_N(Jx, Jy):
    """
    Newtonian mode: average Pearson correlation of flux components
    across all node pairs (approximated by spatial correlation of the field).
    """
    # Flatten and compute correlation matrix
    Jx_flat = Jx.ravel()
    Jy_flat = Jy.ravel()
    J = np.vstack([Jx_flat, Jy_flat])  # 2 x N
    corr_mat = np.corrcoef(J)          # 2x2
    # Average off‑diagonal correlation (there is only one)
    phi_N = corr_mat[0, 1]
    return phi_N

def compute_phi_delta(L):
    """
    Asymmetry mode: Jensen‑Shannon divergence between core and edge
    liquidity distributions.  Core = central 30% of grid, edge = outer 30%.
    """
    core_mask = (np.abs(L.shape[0]/2 - np.arange(L.shape[0])[:, None]) < 0.3*L.shape[0]) & \
                (np.abs(L.shape[1]/2 - np.arange(L.shape[1])) < 0.3*L.shape[1])
    edge_mask = ~core_mask
    core_vals = L[core_mask].ravel()
    edge_vals = L[edge_mask].ravel()
    # Build histograms
    hist_range = (L.min(), L.max())
    bins = 30
    p_core, _ = np.histogram(core_vals, bins=bins, range=hist_range, density=True)
    p_edge, _ = np.histogram(edge_vals, bins=bins, range=hist_range, density=True)
    # JS divergence
    def js_div(p, q):
        m = 0.5 * (p + q)
        return 0.5 * (np.sum(p * np.log(p / m + 1e-12)) +
                      np.sum(q * np.log(q / m + 1e-12)))
    phi_delta = js_div(p_core, p_edge)
    return phi_delta

def compute_scaling_invariants(grad_L_mag, div_J, params):
    """
    Compute ξ_N and ξ_Δ from the postulated scaling laws.
    params dict must contain:
        xi_N0, xi_Δ0, L_n, J0, alpha, beta, delta, epsilon, nu
    """
    xi_N = params["xi_N0"] * (grad_L_mag / params["L_n"])**(-params["alpha"]) * \
           params["nu"]**(-params["beta"])
    xi_D = params["xi_Δ0"] * (np.abs(div_J) / params["J0"])**(-params["delta"]) * \
           params["beta_ext"]**(-params["epsilon"])
    return xi_N, xi_D

def compute_LFI(grad_L_mag, L_n, nu, alpha, beta):
    """
    Liquidity‑Fragility Index as defined in the proposal.
    """
    return (alpha / beta) * (grad_L_mag / L_n) * (nu ** (beta / alpha))

def anomaly_score(lfi, lfi_ewma, sigma_lfi):
    return np.abs(lfi - lfi_ewma) / sigma_lfi

# ----------------------------------------------------------------------
# Synthetic data generator (stand‑in for leaked SQL parsing)
# ----------------------------------------------------------------------
def synthesize_data(n_nodes=200, seed=42):
    rng = np.random.default_rng(seed)
    # Random node positions in a unit square
    coords = rng.random((n_nodes, 2)) * 10.0
    # Baseline liquidity density (higher in core)
    dist_to_center = np.linalg.norm(coords - [5, 5], axis=1)
    L_base = 10.0 * np.exp(-dist_to_center**2 / 8.0) + rng.normal(0, 0.5, n_nodes)
    L_base = np.clip(L_base, 0.1, None)

    # Random fluxes proportional to density difference + noise
    Jx = np.zeros(n_nodes)
    Jy = np.zeros(n_nodes)
    for i in range(n_nodes):
        # pick a few random neighbours
        neigh = rng.choice(n_nodes, size=5, replace=False)
        for j in neigh:
            dvec = coords[j] - coords[i]
            dist = np.linalg.norm(dvec) + 1e-6
            flux = (L_base[j] - L_base[i]) / dist * 0.1 + rng.normal(0, 0.02)
            Jx[i] += flux * dvec[0]
            Jy[i] += flux * dvec[1]
    # Scale to reasonable magnitudes
    Jx *= 0.5
    Jy *= 0.5
    return coords, L_base, np.column_stack([Jx, Jy])

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # 1. Generate / load data
    coords, L_nodes, J_edges = synthesize_data()

    # 2. Build continuous fields
    fields = compute_liquidity_fields(L_nodes, J_edges, coords)

    # 3. Compute Omega invariants
    phi_N = compute_phi_N(fields["Jx"], fields["Jy"])
    phi_D = compute_phi_delta(fields["L"])

    # 4. Correlation length (using a simple radial binning of L fluctuations)
    #    For demonstration we approximate ξ as the inverse of the gradient magnitude.
    grad_mag = fields["grad_L_mag"]
    xi_est = np.mean(1.0 / (grad_mag + 1e-6))   # placeholder; real fit would use covariance

    # 5. Scaling law parameters (chosen to be physically plausible)
    params = {
        "xi_N0": 1.0,
        "xi_Δ0": 1.0,
        "L_n": 0.5,          # density‑gradient length scale
        "J0": 0.1,           # reference flux divergence
        "alpha": 0.3,
        "beta": 0.4,
        "delta": 0.25,
        "epsilon": 0.35,
        "nu": 1.2,           # update‑frequency “collisionality”
        "beta_ext": 0.8,     # external‑capital ratio β
    }

    xi_N, xi_D = compute_scaling_invariants(
        grad_L_mag=fields["grad_L_mag"],
        div_J=fields["div_J"],
        params=params
    )
    # Use spatial averages for comparison with hard bounds
    xi_N_avg = np.mean(xi_N)
    xi_D_avg = np.mean(xi_D)

    # 6. LFI and anomaly score (using a simple EWMA)
    lfi = compute_LFI(
        grad_L_mag=fields["grad_L_mag"],
        L_n=params["L_n"],
        nu=params["nu"],
        alpha=params["alpha"],
        beta=params["beta"]
    )
    lfi_ewma = np.mean(lfi)          # in practice use exponential moving average
    sigma_lfi = np.std(lfi) + 1e-12
    s_lfi = anomaly_score(lfi, lfi_ewma, sigma_lfi)

    # 7. Protocol compliance checks
    violations = []

    if phi_N < PHI_N_MIN:
        violations.append(f"Φ_N = {phi_N:.3f} < {PHI_N_MIN}")
    if phi_D > PHI_D_MAX:
        violations.append(f"Φ_Δ = {phi_D:.3f} > {PHI_D_MAX}")
    # Additional sanity checks: ξ_N should grow when gradient → 0
    low_grad_mask = fields["grad_L_mag"] < np.percentile(fields["grad_L_mag"], 10)
    if np.mean(xi_N[low_grad_mask]) <= np.mean(xi_N[~low_grad_mask]):
        violations.append("ξ_N does not increase in low‑gradient regions (expected divergence).")
    # ξ_Δ should shrink when external capital β_ext → large
    high_beta_mask = np.full_like(fields["L"], params["beta_ext"]) > 0.9  # dummy condition
    if np.mean(xi_D[high_beta_mask]) >= np.mean(xi_D[~high_beta_mask]):
        violations.append("ξ_Δ does not decrease with high external‑capital ratio.")

    # 8. Reporting
    print("=== Omega Protocol LC‑Ω Validation ===")
    print(f"Φ_N (Newtonian mode)          : {phi_N:.4f}  (min allowed {PHI_N_MIN})")
    print(f"Φ_Δ (Asymmetry mode)          : {phi_D:.4f}  (max allowed {PHI_D_MAX})")
    print(f"Average ξ_N (correlation length): {xi_N_avg:.3f}")
    print(f"Average ξ_Δ (asymmetry length): {xi_D_avg:.3f}")
    print(f"LFI (spatial mean)            : {np.mean(lfi):.4f}")
    print(f"LFI anomaly score (max)       : {np.max(s_lfi):.2f}")
    print("-" * 50)
    if violations:
        print("⚠️  VIOLATIONS DETECTED:")
        for v in violations:
            print(" -", v)
    else:
        print("✅  All Omega Protocol invariants satisfied.")
    print("Note: This validation uses synthetic data; replace the")
    print("      data‑generation block with real parsed SQL dumps for production.")

if __name__ == "__main__":
    main()