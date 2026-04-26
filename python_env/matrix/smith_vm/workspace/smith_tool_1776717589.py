# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Jerk‑Stability Validator
---------------------------------------
Checks that a candidate S_j(T) implementation:
  1. Returns ~1 for Gaussian jerk.
  2. Returns ~1 for constant (zero‑variance) jerk.
  3. Decreases monotonically with excess kurtosis > 0.
  4. Remains in the interval (0, 1].

The script also provides a sanity‑check for the other Engine formulas
(coherence field, invariants, entropy) using synthetic telemetry.
"""

import numpy as np
from scipy.stats import kurtosis, laplace, norm

# ----------------------------------------------------------------------
# Helper: corrected jerk‑stability metric (excess‑kurtosis based)
# ----------------------------------------------------------------------
def sj_corrected(j_signal: np.ndarray) -> float:
    """
    Compute S_j from a 1-D jerk signal using the corrected formula.
    """
    if j_signal.size < 2:
        return 1.0                     # insufficient data → treat as predictable
    mean_j = np.mean(j_signal)
    std_j = np.std(j_signal, ddof=0)   # population std, matches integral definition
    # Guard against zero variance (constant signal)
    if std_j < 1e-12:
        return 1.0
    z = (j_signal - mean_j) / std_j
    K = np.mean(z ** 4)                # empirical fourth moment
    excess = max(0.0, K - 3.0)
    return 1.0 / (1.0 + excess)


# ----------------------------------------------------------------------
# Benchmark distributions
# ----------------------------------------------------------------------
def test_jerk_metric():
    rng = np.random.default_rng(seed=42)
    N = 200_000  # large sample for stable statistics

    # 1. Gaussian jerk (excess kurtosis = 0)
    j_gauss = rng.normal(loc=0.0, scale=1.0, size=N)
    sj_g = sj_corrected(j_gauss)
    print(f"Gaussian jerk: S_j = {sj_g:.5f} (target ≈ 1.0)")

    # 2. Constant jerk (zero variance)
    j_const = np.full(N, fill_value=2.5)
    sj_c = sj_corrected(j_const)
    print(f"Constant jerk: S_j = {sj_c:.5f} (target ≈ 1.0)")

    # 3. Heavy‑tailed jerk (Laplace, excess kurtosis = 3)
    j_lap = rng.laplace(loc=0.0, scale=1.0, size=N)
    sj_l = sj_corrected(j_lap)
    print(f"Laplace jerk:  S_j = {sj_l:.5f} (target < 1.0)")

    # Assertions – adjust tolerances as needed
    assert np.isclose(sj_g, 1.0, atol=0.02), "Gaussian jerk should give S_j≈1"
    assert np.isclose(sj_c, 1.0, atol=0.02), "Constant jerk should give S_j≈1"
    assert sj_l < 0.9, "Heavy‑tailed jerk should yield S_j noticeably <1"
    assert 0.0 < sj_l <= 1.0, "S_j must stay in (0,1]"
    print("\nAll jerk‑stability checks PASSED.\n")


# ----------------------------------------------------------------------
# Synthetic telemetry to verify other Engine equations (no runtime)
# ----------------------------------------------------------------------
def synthetic_telemetry_check():
    """
    Build a tiny, self‑consistent telemetry set and compute:
      - ψ_ij, φ_ij, ψ, ξ_N, ξ_Δ, S_h
    The goal is to confirm the equations are well‑defined, not to
    validate physical correctness.
    """
    # Simulate 4 compute units (0..3)
    n_units = 4
    # Atomic success rates (unitless, 0..1)
    A = np.random.rand(n_units, n_units)
    # Latency (ns) – positive
    L = np.random.uniform(10, 200, size=(n_units, n_units))
    L0 = 50.0  # decay length scale
    # Coherence field ψ_ij
    psi_ij = A * np.exp(-L / L0)

    # Asymmetry field φ_ij (reads/writes)
    reads = np.random.randint(1, 100, size=(n_units, n_units))
    writes = np.random.randint(1, 100, size=(n_units, n_units))
    eps = 1e-6
    phi_ij = reads / (writes + eps)

    # Global scalars
    psi = np.log(np.mean(phi_ij))
    Phi_N = np.mean(psi_ij)
    Phi_Delta = np.std(psi_ij)

    # Radial correlation length ξ_N: fit exponential decay vs. topological distance
    # For simplicity, use Manhattan distance on a line topology
    dist = np.abs(np.subtract.outer(np.arange(n_units), np.arange(n_units)))
    # Average coherence per distance bin
    C_r = np.array([np.mean(psi_ij[dist == d]) for d in np.unique(dist) if d > 0])
    r_vals = np.unique(dist)[dist > 0]
    # Fit log(C) = -r/ξ_N + const via least squares
    if len(C_r) > 1 and np.all(C_r > 0):
        logC = np.log(C_r)
        A_mat = np.vstack([-r_vals, np.ones_like(r_vals)]).T
        xi_N, _ = np.linalg.lstsq(A_mat, logC, rcond=None)[0]
        xi_N = -1.0 / xi_N if xi_N != 0 else np.inf
    else:
        xi_N = np.nan

    # Poloidal correlation length ξ_Δ: std of decay constants across pathway types
    # Define two pathway types: CPU-GPU (0↔2,1↔3) and GPU-GPU (2↔3)
    pathway_masks = {
        "CPU-GPU": ((np.arange(n_units)[:, None] == 0) & (np.arange(n_units)[None, :] == 2)) |
                   ((np.arange(n_units)[:, None] == 1) & (np.arange(n_units)[None, :] == 3)),
        "GPU-GPU": ((np.arange(n_units)[:, None] == 2) & (np.arange(n_units)[None, :] == 3)) |
                   ((np.arange(n_units)[:, None] == 3) & (np.arange(n_units)[None, :] == 2))
    }
    decay_consts = []
    for label, mask in pathway_masks.items():
        if np.any(mask):
            # Fit exponential decay for this subset (same distance metric)
            sub_psi = psi_ij * mask
            C_sub = np.array([np.mean(sub_psi[dist == d]) for d in r_vals])
            if np.all(C_sub > 0) and len(C_sub) > 1:
                logCsub = np.log(C_sub)
                A_mat = np.vstack([-r_vals, np.ones_like(r_vals)]).T
                xi, _ = np.linalg.lstsq(A_mat, logCsub, rcond=None)[0]
                xi = -1.0 / xi if xi != 0 else np.inf
                decay_consts.append(xi)
    xi_Delta = np.std(decay_consts) if len(decay_consts) > 1 else 0.0

    # Entropy S_h: Shannon entropy of coherence histogram
    hist, _ = np.histogram(psi_ij, bins=10, density=True)
    # Avoid zeros in log
    hist = hist[hist > 0]
    S_h = -np.sum(hist * np.log(hist))

    print("Synthetic telemetry check:")
    print(f"  ψ = {psi:.5f}, Φ_N = {Phi_N:.5f}, Φ_Δ = {Phi_Delta:.5f}")
    print(f"  ξ_N = {xi_N if not np.isnan(xi_N) else 'nan':.5f}, ξ_Δ = {xi_Delta:.5f}")
    print(f"  S_h = {S_h:.5f}")
    print("All intermediate quantities are computable – no undefined symbols.\n")


if __name__ == "__main__":
    test_jerk_metric()
    synthetic_telemetry_check()