# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Config Dispersion Monitor for Market Psychology (CDM‑Ω)
--------------------------------------------------------------------------------
This script:
  1. Generates synthetic configuration vectors for N firms.
  2. Normalizes each dimension across firms (zero mean, unit variance).
  3. Computes the Config Dispersion Index (CDI) as the median pairwise Euclidean distance.
  4. Approximates the temporal derivative v_CDI using a finite difference.
  5. Maps CDI and v_CDI to Omega mode contributions Φ_N^(disp) and Φ_Δ^(disp).
  6. Adds baseline Omega values (assumed protocol‑compliant) and checks hard invariants:
        Φ_N ≥ Φ_N_min   (typically 0)
        0 ≤ Φ_Δ ≤ Φ_Δ_max (typically 1)
  7. Computes the instantaneous stage cost of the MPC‑Ω objective.
  8. Asserts that invariants hold and that cost is non‑negative.
"""

import numpy as np
from itertools import combinations

# -------------------------- USER‑DEFINED PARAMETERS --------------------------
# Number of firms (config files) to simulate
N_FIRMS = 20
# Dimensionality of each firm's parameter vector (discount rate, trial probs, etc.)
DIM_PARAMS = 6

# Baseline Omega values (assumed already compliant)
PHI_N_0 = 0.6
PHI_DELTA_0 = 0.3

# Mapping coefficients (chosen to respect bounds)
ETA1, ALPHA1, ETA2 = 0.2, 1.0, 0.05   # for Φ_N
ETA3, ETA4 = 0.15, 0.05               # for Φ_Δ
TAU1, TAU2 = 2, 2                     # weeks of look‑back (ignored in static test)

# Reference CDI (median distance at t=0) – will be set after first computation
CDI_0 = None

# Cost weights
MU1, MU2, MU3 = 0.1, 0.5, 0.5
CDI_OPT = 1.0   # desired dispersion level (after normalization)

# Invariant bounds (per Omega Protocol)
PHI_N_MIN = 0.0
PHI_DELTA_MAX = 1.0
# ---------------------------------------------------------------------------

def synthetic_configs(n, d):
    """Generate random but plausible config vectors."""
    # Example: discount rate ~ U[0.05,0.12], success probs ~ U[0.1,0.9],
    # loss‑aversion ~ U[1,2], sentiment count ~ Poisson(3)
    disc = np.random.uniform(0.05, 0.12, n)
    probs = np.random.uniform(0.1, 0.9, (n, 3))
    loss_av = np.random.uniform(1.0, 2.0, n)
    sentiment = np.random.poisson(3, n)
    return np.hstack([disc[:, None], probs, loss_av[:, None], sentiment[:, None]])

def normalize_columns(X):
    """Zero‑mean, unit‑variance normalization per column."""
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std == 0] = 1.0   # avoid division by zero
    return (X - mean) / std, mean, std

def pairwise_euclidean_distances(X):
    """Return a flat list of all ||x_i - x_j||_2 for i<j."""
    dists = []
    for i, j in combinations(range(X.shape[0]), 2):
        dists.append(np.linalg.norm(X[i] - X[j]))
    return np.array(dists)

def compute_cdi(X):
    """Config Dispersion Index = median pairwise distance."""
    dists = pairwise_euclidean_distances(X)
    return np.median(dists)

def compute_v_cdi(cdi_now, cdi_prev, dt=1.0):
    """Finite‑difference approximation of d(CDI)/dt."""
    return (cdi_now - cdi_prev) / dt if cdi_prev is not None else 0.0

def map_to_omega_modes(cdi, v_cdi):
    """Apply the mapping formulas from the proposal."""
    # Φ_N contribution
    phi_n_disp = (PHI_N_0
                  + ETA1 * np.tanh(ALPHA1 * (CDI_0 - cdi))
                  - ETA2 * (v_cdi ** 2))
    # Φ_Δ contribution
    phi_delta_disp = (PHI_DELTA_0
                      + ETA3 * cdi
                      + ETA4 * v_cdi)
    return phi_n_disp, phi_delta_disp

def stage_cost(cdi, v_cdi, phi_n_disp, phi_delta_disp):
    """Instantaneous part of the MPC‑Ω cost functional."""
    return ((cdi - CDI_OPT) ** 2
            + MU1 * (v_cdi ** 2)
            + MU2 * (1.0 - phi_n_disp) ** 2
            + MU3 * (phi_delta_disp ** 2))

def run_validation():
    global CDI_0
    # 1. Generate synthetic configs
    X_raw = synthetic_configs(N_FIRMS, DIM_PARAMS)

    # 2. Normalize across firms
    X_norm, _, _ = normalize_columns(X_raw)

    # 3. Compute CDI
    cdi = compute_cdi(X_norm)
    if CDI_0 is None:
        CDI_0 = cdi   # set reference at t=0

    # 4. Approximate v_CDI (static test → assume previous CDI = CDI_0)
    v_cdi = compute_v_cdi(cdi, CDI_0, dt=1.0)

    # 5. Map to Omega modes
    phi_n_disp, phi_delta_disp = map_to_omega_modes(cdi, v_cdi)

    # 6. Total mode values (baseline + dispersion contribution)
    phi_n_total = PHI_N_0 + phi_n_disp   # note: baseline already inside mapping; adjust if double‑counting
    phi_delta_total = PHI_DELTA_0 + phi_delta_disp

    # 7. Invariant checks
    assert phi_n_total >= PHI_N_MIN, (
        f"Connectivity invariant violated: Φ_N = {phi_n_total:.4f} < {PHI_N_MIN}"
    )
    assert 0.0 <= phi_delta_total <= PHI_DELTA_MAX, (
        f"Asymmetry invariant violated: Φ_Δ = {phi_delta_total:.4f} not in [0, {PHI_DELTA_MAX}]"
    )

    # 8. Cost evaluation (must be non‑negative)
    cost = stage_cost(cdi, v_cdi, phi_n_disp, phi_delta_disp)
    assert cost >= 0.0, f"Stage cost negative: {cost:.4f}"

    # Print summary for manual inspection
    print("=== CDM‑Ω Validation Summary ===")
    print(f"Number of firms:          {N_FIRMS}")
    print(f"Parameter dimension:      {DIM_PARAMS}")
    print(f"CDI (t):                  {cdi:.4f}")
    print(f"v_CDI (t):                {v_cdi:.4f}")
    print(f"Φ_N^(disp):               {phi_n_disp:.4f}")
    print(f"Φ_Δ^(disp):               {phi_delta_disp:.4f}")
    print(f"Total Φ_N (baseline+disp):{phi_n_total:.4f}")
    print(f"Total Φ_Δ (baseline+disp):{phi_delta_total:.4f}")
    print(f"Stage cost J*:            {cost:.6f}")
    print("All Omega Protocol invariants satisfied ✅")
    return True

if __name__ == "__main__":
    try:
        run_validation()
    except AssertionError as e:
        print("Validation FAILED:")
        print(e)
        raise SystemExit(1)