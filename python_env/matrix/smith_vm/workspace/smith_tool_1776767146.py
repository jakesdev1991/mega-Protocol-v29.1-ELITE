# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validator for Thermal‑Spatial Fragility Monitor (TSFM‑Ω)

This script checks that the core mathematical objects defined in the refined
TSFM‑Ω proposal satisfy the Omega Protocol invariants:

    • Φ_N   – Newtonian (uniform) mode  →  a₀(t)
    • Φ_Δ   – Archive   (dipole) mode   →  a₁(t)
    • J*    – Implicit in the action‑based cost functional (we verify
              that the Lagrangian density is non‑negative and that the
              constraints used in the MPC‑Ω QP are respected).

The validator works on synthetic time‑series data but can be swapped for
real sensor streams.

Invariants enforced (as stated in the proposal & MPC‑Ω section):

    1) Φ_N  ≥ 0.6
    2) Φ_Δ  ≤ 0.7
    3) TSFI ≤ 1.5
    4) ξ_N  ≥ ξ_N^min   (stiffness from Φ_N, Φ_Δ)
    5) ξ_Δ  ≥ ξ_Δ^min
    6) max_i T_i ≤ T_redline
    7) ξ_N⁻² = α(3Φ_N² + Φ_Δ² – T₀²)  > 0
    8) ξ_Δ⁻² = α(Φ_N² + 3Φ_Δ² – T₀²)  > 0
    9) ψ = ln〈κ〉/κ₀ + λ·TSFI   (no hard bound, but we flag if ψ > 0
       during a predicted anomaly – indicates inconsistency with
       “flattening manifold → negative ψ” expectation).

If any invariant is violated, the script raises a ValidationError with
details.

Author: Agent Smith (Matrix Guardian)
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List

# ----------------------------------------------------------------------
# Configuration (tuned to typical H100 cluster numbers – adjust as needed)
# ----------------------------------------------------------------------
@dataclass
class PhysParams:
    D: float = 1.0e-4          # thermal diffusivity [m²/s] (placeholder)
    alpha: float = 2.0         # double‑well strength
    T0: float = 85.0           # nominal operating temperature [°C]
    k: float = 150.0           # thermal conductivity [W/(m·K)]
    rho: float = 1.2           # air density [kg/m³]
    cp: float = 1005.0         # specific heat [J/(kg·K)]
    lambda_: float = 0.5       # weight of TSFI in ψ
    xi0: float = 0.1           # reference correlation length [m]
    xi_N_min: float = 0.05     # minimal allowed ξ_N [s]
    xi_Delta_min: float = 0.05 # minimal allowed ξ_Δ [s]
    T_redline: float = 110.0   # max allowable sensor temperature [°C]
    S_target: float = 2.0      # target entropy (nats) for gauge term

PARAMS = PhysParams()

# ----------------------------------------------------------------------
# Helper functions – core mathematics from the proposal
# ----------------------------------------------------------------------
def compute_modes(T_field: np.ndarray, psi_basis: np.ndarray) -> Tuple[float, float]:
    """
    Project the 3‑D temperature field onto the Laplace eigenbasis.
    Returns a0 (uniform) and a1 (dipole) coefficients.
    """
    # Assuming psi_basis[:,0] = uniform mode, psi_basis[:,1] = dipole mode
    a0 = np.tensordot(T_field, psi_basis[:, 0], axes=([0,1,2], [0]))
    a1 = np.tensordot(T_field, psi_basis[:, 1], axes=([0,1,2], [0]))
    return float(a0), float(a1)

def correlation_length_from_field(T_field: np.ndarray,
                                  sensor_coords: np.ndarray) -> float:
    """
    Estimate ξ via exponential fit to the spatial correlation function.
    Simple implementation: compute pairwise correlations, fit log(C) vs r.
    """
    N = T_field.shape[0]
    # Flatten spatial dimensions, keep time axis last (assume shape (nx,ny,nz,nt))
    T_flat = T_field.reshape(-1, T_field.shape[-1])
    # Remove temporal mean
    T_anom = T_flat - np.mean(T_flat, axis=1, keepdims=True)
    # Correlation matrix (space × space)
    C = np.corrcoef(T_anom)  # shape (Nsp, Nsp)
    # Distance matrix
    diff = sensor_coords[:, np.newaxis, :] - sensor_coords[np.newaxis, :, :]
    dist = np.sqrt(np.sum(diff**2, axis=-1))
    # Upper triangle (excluding diagonal)
    iu = np.triu_indices(Nsp, k=1)
    r_vals = dist[iu]
    c_vals = C[iu]
    # Bin distances and average correlation
    nbins = 20
    bins = np.linspace(r_vals.min(), r_vals.max(), nbins+1)
    bin_centers = 0.5*(bins[:-1]+bins[1:])
    binned_corr = np.full(nbins, np.nan)
    for b in range(nbins):
        mask = (r_vals >= bins[b]) & (r_vals < bins[b+1])
        if np.any(mask):
            binned_corr[b] = np.mean(c_vals[mask])
    # Fit log(C) = -r/ξ  =>  ξ = -r / log(C)
    valid = ~np.isnan(binned_corr) & (binned_corr > 0)
    if np.sum(valid) < 2:
        return np.inf  # insufficient data → treat as large correlation length
    logc = np.log(binned_corr[valid])
    rfit = bin_centers[valid]
    # Linear fit: logc = -r/ξ  => slope = -1/ξ
    A = np.vstack([rfit, np.ones_like(rfit)]).T
    slope, _ = np.linalg.lstsq(A, logc, rcond=None)[0]
    xi = -1.0 / slope if slope < 0 else np.inf
    return float(xi)

def heat_flux_divergence(T_field: np.ndarray,
                         v_field: np.ndarray) -> float:
    """
    Compute ∇·q = ∇·(-k∇T + ρ c_p v T) using finite differences.
    Returns volume‑averaged |∇·q|.
    """
    # Gradient of T
    gradT = np.gradient(T_field, axis=(0,1,2))  # list of three arrays
    # Conductive part: -k ∇T
    q_cond = -PARAMS.k * np.stack(gradT, axis=-1)
    # Advective part: ρ c_p v T
    q_adv = PARAMS.rho * PARAMS.cp * v_field * T_field[..., np.newaxis]
    q = q_cond + q_adv
    # Divergence
    div_q = np.gradient(q[...,0], axis=0) + \
            np.gradient(q[...,1], axis=1) + \
            np.gradient(q[...,2], axis=2)
    return float(np.mean(np.abs(div_q)))

def entropy_gauge(T_field: np.ndarray,
                  window: int = 10) -> float:
    """
    Shannon entropy of temperature fluctuations per sensor,
    averaged over space and then over a temporal window.
    Returns scalar ȆS(t).
    """
    # Flatten space, keep time
    T_flat = T_field.reshape(-1, T_field.shape[-1])
    # Detrend (remove running mean)
    kernel = np.ones(window)/window
    T_mean = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='same'),
                                 axis=1, arr=T_flat)
    T_fluct = T_flat - T_mean
    # Histogram per sensor
    n_bins = 20
    hists = np.apply_along_axis(
        lambda x: np.histogram(x, bins=n_bins, density=True)[0],
        axis=1, arr=T_fluct)
    # Avoid zeros in log
    hists = np.clip(hists, 1e-12, None)
    S_per_sensor = -np.sum(hists * np.log(hists), axis=1)
    # Spatial average
    S_spatial = np.mean(S_per_sensor)
    # Temporal smoothing (already done via window)
    return float(S_spatial)

def compute_tsfi(xi: float,
                 div_q: float,
                 S_bar: float) -> float:
    """
    TSFI = (ξ/ξ₀) * exp[∫|∇·q| dV] * exp[-S̄]
    We approximate the volume integral by the pointwise mean multiplied by V.
    For unit volume V=1, the exponent is just div_q.
    """
    term1 = xi / PARAMS.xi0
    term2 = np.exp(div_q)          # ∫|∇·q| dV ≈ ⟨|∇·q|⟩·V, V=1
    term3 = np.exp(-S_bar)
    return float(term1 * term2 * term3)

def stiffness_inverses(Phi_N: float, Phi_Delta: float) -> Tuple[float, float]:
    """
    ξ_N⁻² = α(3Φ_N² + Φ_Δ² – T₀²)
    ξ_Δ⁻² = α(Φ_N² + 3Φ_Δ² – T₀²)
    """
    xi_N_inv2 = PARAMS.alpha * (3*Phi_N**2 + Phi_Delta**2 - PARAMS.T0**2)
    xi_Delta_inv2 = PARAMS.alpha * (Phi_N**2 + 3*Phi_Delta**2 - PARAMS.T0**2)
    return float(xi_N_inv2), float(xi_Delta_inv2)

def olivier_ricci_curvature(sensor_coords: np.ndarray,
                            temps: np.ndarray) -> float:
    """
    Very simplified Ollivier‑Ricci proxy:
        κ_ij = 1 - W₁(μ_i, μ_j) / d_ij
    We approximate the 1‑D Wasserstein distance between two Gaussians
    fitted to each sensor's temperature distribution (mean, std).
    """
    N = sensor_coords.shape[0]
    means = np.mean(temps, axis=-1)
    stds  = np.std(temps, axis=-1, ddof=1)
    # Pairwise distances
    diff = sensor_coords[:, np.newaxis, :] - sensor_coords[np.newaxis, :, :]
    d = np.sqrt(np.sum(diff**2, axis=-1))
    # 1‑D Wasserstein between Gaussians: |μ_i-μ_j| + |σ_i-σ_j|
    w1 = np.abs(means[:, np.newaxis] - means[np.newaxis, :]) + \
         np.abs(stds[:, np.newaxis] - stds[np.newaxis, :])
    kappa = 1.0 - w1 / (d + 1e-9)
    np.fill_diagonal(kappa, 0.0)   # ignore self‑pairs
    return float(np.mean(kappa[iu])) if (iu:=np.triu_indices(N, k=1))[0].size else 0.0

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
class ValidationError(RuntimeError):
    pass

def validate_step(t_idx: int,
                  T_field: np.ndarray,
                  v_field: np.ndarray,
                  sensor_coords: np.ndarray,
                  psi_basis: np.ndarray) -> None:
    """
    Perform all invariant checks for a single time slice.
    """
    # 1) Modal coefficients → Φ_N, Φ_Δ
    a0, a1 = compute_modes(T_field, psi_basis)
    Phi_N = a0
    Phi_Delta = a1

    # 2) Correlation length ξ
    xi = correlation_length_from_field(T_field, sensor_coords)

    # 3) Heat‑flux divergence and entropy gauge
    div_q = heat_flux_divergence(T_field, v_field)
    S_bar = entropy_gauge(T_field)

    # 4) TSFI
    TSFI = compute_tsfi(xi, div_q, S_bar)

    # 5) Stiffness inverses → ξ_N, ξ_Δ
    xi_N_inv2, xi_Delta_inv2 = stiffness_inverses(Phi_N, Phi_Delta)
    if xi_N_inv2 <= 0 or xi_Delta_inv2 <= 0:
        raise ValidationError(
            f"Stiffness non‑positive at t={t_idx}: "
            f"ξ_N⁻²={xi_N_inv2:.3e}, ξ_Δ⁻²={xi_Delta_inv2:.3e}"
        )
    xi_N = 1.0 / np.sqrt(xi_N_inv2)
    xi_Delta = 1.0 / np.sqrt(xi_Delta_inv2)

    # 6) Ollivier‑Ricci curvature → ψ
    kappa_mean = olivier_ricci_curvature(sensor_coords, T_field)
    psi = np.log(kappa_mean / 1e-3) + PARAMS.lambda_ * TSFI  # κ₀ set to 1e-3 for scaling

    # ------------------------------------------------------------------
    # Invariant checks (Omega Protocol)
    # ------------------------------------------------------------------
    if Phi_N < 0.6:
        raise ValidationError(f"Φ_N ({Phi_N:.3f}) < 0.6 at t={t_idx}")
    if Phi_Delta > 0.7:
        raise ValidationError(f"Φ_Δ ({Phi_Delta:.3f}) > 0.7 at t={t_idx}")
    if TSFI > 1.5:
        raise ValidationError(f"TSFI ({TSFI:.3f}) > 1.5 at t={t_idx}")
    if xi_N < PARAMS.xi_N_min:
        raise ValidationError(f"ξ_N ({xi_N:.3f}) < ξ_N^min ({PARAMS.xi_N_min}) at t={t_idx}")
    if xi_Delta < PARAMS.xi_Delta_min:
        raise ValidationError(f"ξ_Δ ({xi_Delta:.3f}) < ξ_Δ^min ({PARAMS.xi_Delta_min}) at t={t_idx}")
    # Temperature redline
    T_max = np.max(T_field)
    if T_max > PARAMS.T_redline:
        raise ValidationError(f"Max temperature {T_max:.1f}°C > T_redline ({PARAMS.T_redline}) at t={t_idx}")
    # ψ should be negative during anomalous growth (manifold flattening)
    # We only warn, not fail, because ψ can be positive in nominal regime.
    if psi > 0 and TSFI > 1.2:  # heuristic: high TSFI + positive ψ → inconsistency
        raise ValidationError(
            f"ψ ({psi:.3f}) > 0 while TSFI high ({TSFI:.3f}) at t={t_idx} "
            f"(expected negative ψ indicating manifold flattening)."
        )

    # If we reach here, all invariants hold for this slice.
    return None

# ----------------------------------------------------------------------
# Example usage with synthetic data (replace with real streams)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Synthetic grid: 8×8×4 rack, 50 time steps
    nx, ny, nz, nt = 8, 8, 4, 50
    # Coordinates of sensor nodes (uniform grid)
    xs = np.linspace(0, 1, nx)
    ys = np.linspace(0, 1, ny)
    zs = np.linspace(0, 1, nz)
    xv, yv, zv = np.meshgrid(xs, ys, zs, indexing='ij')
    sensor_coords = np.stack([xv.ravel(), yv.ravel(), zv.ravel()], axis=-1)  # (N,3)
    Nsensor = sensor_coords.shape[0]

    # Random temperature field around nominal T0 with occasional hotspot
    np.random.seed(42)
    base = PARAMS.T0 + 2.0 * np.random.randn(nx, ny, nz, nt)
    # Inject a slowly growing hotspot in the centre
    hotspot = np.zeros_like(base)
    cx, cy, cz = nx//2, ny//2, nz//2
    for t in range(nt):
        amp = 0.5 * t / (nt-1) * 15.0  # grow up to +15°C
        hotspot[cx, cy, cz, t] = amp
    T_field = base + hotspot

    # Dummy velocity field (uniform upward flow)
    v_field = np.zeros((nx, ny, nz, nt, 3))
    v_field[..., 2] = 0.1  # m/s upward in z

    # Laplace eigenbasis for a rectangular box with Neumann BC:
    # ψ_{lmn}(x,y,z) = cos(lπx/Lx) cos(mπy/Ly) cos(nπz/Lz)
    # We'll generate the first two modes: (0,0,0) uniform and (1,0,0) dipole in x.
    Lx, Ly, Lz = 1.0, 1.0, 1.0  # normalized domain size
    psi_basis = np.zeros((nx, ny, nz, 2))
    # mode 0: uniform
    psi_basis[..., 0] = 1.0
    # mode 1: cos(π x / Lx)
    psi_basis[..., 1] = np.cos(np.pi * xv / Lx)[..., np.newaxis]

    # Validate each time step
    try:
        for t in range(nt):
            validate_step(
                t_idx=t,
                T_field=T_field[..., t],
                v_field=v_field[..., t, :],
                sensor_coords=sensor_coords,
                psi_basis=psi_basis
            )
        print("✅ All Omega‑Protocol invariants satisfied for the synthetic test.")
    except ValidationError as e:
        print(f"❌ Invariant violation: {e}")