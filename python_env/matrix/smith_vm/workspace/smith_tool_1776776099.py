# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPCLM‑Ω Mathematical & Invariant Validator
-----------------------------------------
This script checks that the formulas proposed for HPCLM‑Ω respect the
Omega Protocol invariants (Phi_N, Phi_Delta, J*) and the explicit
MPC‑Ω constraints:
    HLI   <= 5.0
    Phi_N <= 0.9
    Phi_Delta <= 0.7
All violations raise AssertionError with a descriptive message.
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL  # pip install statsmodels

# ----------------------------------------------------------------------
# 1. Core functions (as described in the proposal)
# ----------------------------------------------------------------------
def compute_hli(gpu_counts, delays, conf_scores, alpha, beta, gamma, delta):
    """
    HLI(t) = Σ [ α·log(GPU) + β·exp(−γ·delay) + δ·conf ]
    Parameters
    ----------
    gpu_counts : array-like, >=1
    delays     : array-like, days (leak_date - planned_deploy_date)
                 Negative => leak before deployment.
    conf_scores: array-like, 1..3 (confidentiality level)
    alpha,beta,gamma,delta : non‑negative scalars
    """
    assert np.all(np.array(gpu_counts) >= 1), "GPU count must be >=1"
    assert np.all((np.array(conf_scores) >= 1) & (np.array(conf_scores) <= 3)), "conf score in [1,3]"
    assert alpha >= 0 and beta >= 0 and delta >= 0, "weights must be non‑negative"
    # Guard against exploding exp for large negative delays:
    # Clip delay to a realistic window [-180, +365] days (≈ -6 to +12 months)
    delay_clipped = np.clip(np.array(delays), -180, 365)
    term1 = alpha * np.log(np.array(gpu_counts))
    term2 = beta * np.exp(-gamma * delay_clipped)
    term3 = delta * np.array(conf_scores)
    return np.sum(term1 + term2 + term3)


def phi_n(hli, phi_n0, eta1, tau1):
    """Φ_N = Φ_N0 + η₁·sigmoid(HLI(t‑τ₁))"""
    # shift HLI by lead time (simple approximation: use same HLI)
    shifted = hli  # in a real pipeline we would lag the series
    sig = 1.0 / (1.0 + np.exp(-shifted))  # standard sigmoid
    return phi_n0 + eta1 * sig


def phi_delta(hli, phi_d0, eta2, tau2):
    """Φ_Δ = Φ_Δ0 + η₂·HLI(t‑τ₂)"""
    shifted = hli
    return phi_d0 + eta2 * shifted


def stl_anomaly_score(hli_series, period=13):
    """
    STL decomposition → residual → z‑score.
    Returns anomaly score s_HLI = |residual| / σ_residual.
    """
    series = pd.Series(hli_series)
    stl = STL(series, period=period, robust=True)
    res = stl.fit()
    residual = res.resid
    sigma = np.std(residual)
    if sigma == 0:
        sigma = 1e-12  # avoid division by zero
    return np.abs(residual) / sigma


# ----------------------------------------------------------------------
# 2. Parameter values (chosen to satisfy constraints; in practice they'd be learned)
# ----------------------------------------------------------------------
PHI_N0   = 0.4   # baseline market connectivity
PHI_D0   = 0.2   # baseline information asymmetry
ETA1     = 0.4   # ensures Φ_N ≤ 0.9 when sigmoid≈1
ETA2     = 0.1   # ensures Φ_Δ ≤ 0.7 for HLI≤5
TAU1     = 0     # lead‑time handling omitted for static test
TAU2     = 0
ALPHA    = 0.3
BETA     = 0.5
GAMMA    = 0.01  # small γ keeps exp term moderate
DELTA    = 0.2

# ----------------------------------------------------------------------
# 3. Synthetic leak data generator
# ----------------------------------------------------------------------
def synthetic_leaks(n=10):
    """Return lists of GPU counts, delays, conf scores for n leaks."""
    rng = np.random.default_rng(seed=42)
    gpu = rng.integers(low=1, high=256, size=n)          # 1–256 GPUs per leak
    delay = rng.integers(low=-180, high=365, size=n)    # -6 to +12 months
    conf = rng.integers(low=1, high=4, size=n)          # 1–3
    return gpu, delay, conf


# ----------------------------------------------------------------------
# 4. Validation routine
# ----------------------------------------------------------------------
def validate():
    gpu, delay, conf = synthetic_leaks(n=20)
    hli = compute_hli(gpu, delay, conf, ALPHA, BETA, GAMMA, DELTA)

    # ---- Invariant checks ------------------------------------------------
    # HLI non‑negative
    assert np.all(hli >= 0), f"HLI contains negative values: {hli[hli<0]}"

    # HLI upper bound (MPC‑Ω constraint)
    assert np.all(hli <= 5.0), f"HLI exceeds 5.0: max={np.max(hli)}"

    # Phi_N bounds
    phi_n_vals = phi_n(hli, PHI_N0, ETA1, TAU1)
    assert np.all((phi_n_vals >= 0) & (phi_n_vals <= 0.9)), \
        f"Phi_N out of [0,0.9]: min={np.min(phi_n_vals)}, max={np.max(phi_n_vals)}"

    # Phi_Delta bounds
    phi_d_vals = phi_delta(hli, PHI_D0, ETA2, TAU2)
    assert np.all((phi_d_vals >= 0) & (phi_d_vals <= 0.7)), \
        f"Phi_Delta out of [0,0.7]: min={np.min(phi_d_vals)}, max={np.max(phi_d_vals)}"

    # ---- Anomaly score sanity -------------------------------------------
    # Need a time‑series; we fabricate a simple trend + noise
    trend = np.linspace(0, 4, len(hli))
    noise = np.random.normal(0, 0.2, size=len(hli))
    hli_ts = hli + trend + noise
    anomaly = stl_anomaly_score(hli_ts, period=5)
    assert np.all(anomaly >= 0), "Anomaly score contains negative values"
    # No explicit upper bound, but we can flag extreme values for inspection
    extreme = anomaly > 5.0
    if np.any(extreme):
        print(f"Warning: {np.sum(extreme)} extreme anomaly scores >5.0")

    # ---- MPC‑Ω QP feasibility (simple linear feasibility check) ---------
    # We verify that there exists at least one HLI in [0,5] that yields
    # Phi_N ≤0.9 and Phi_Delta ≤0.7 simultaneously.
    test_hli = np.linspace(0, 5, 501)
    feasible = np.all([
        np.all(phi_n(test_hli, PHI_N0, ETA1, TAU1) <= 0.9),
        np.all(phi_delta(test_hli, PHI_D0, ETA2, TAU2) <= 0.7)
    ])
    assert feasible, "No HLI in [0,5] satisfies both Phi_N≤0.9 and Phi_Delta≤0.7"

    print("✅ All Omega Protocol invariants and MPC‑Ω constraints satisfied.")
    print(f"   Sample HLI range: [{np.min(hli):.3f}, {np.max(hli):.3f}]")
    print(f"   Phi_N range:      [{np.min(phi_n_vals):.3f}, {np.max(phi_n_vals):.3f}]")
    print(f"   Phi_Delta range:  [{np.min(phi_d_vals):.3f}, {np.max(phi_d_vals):.3f}]")
    print(f"   Max anomaly score:{np.max(anomaly):.3f}")


if __name__ == "__main__":
    validate()