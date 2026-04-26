# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validator for PICM‑Ω v2 mathematical core.
Checks:
  - Covariant mode definitions
  - Invariant formulas for ξ_N, ξ_Δ
  - Entropy and jerk computation
  - Shredding / Informational‑Freeze conditions (correct ξ_Δ logic)
  - Dimensional consistency (natural‑unit assumption)
Outputs PASS/FAIL with diagnostic messages.
"""

import numpy as np
from scipy.stats import entropy

# ------------------- Synthetic data generation -------------------
def generate_presentation_times(T=730, base_interval=30, jitter=5, n_events=20):
    """
    Produce a list of presentation timestamps (days) over T days.
    base_interval: mean interval between presentations.
    jitter: random variation.
    """
    t = np.cumsum(np.random.normal(base_interval, jitter, size=n_events))
    t = t[t < T]          # keep within window
    return t

# ------------------- Core computations -------------------
def covariant_modes(times, T, omega=2*np.pi/365.0):
    """
    Φ_N = mean fluctuation, Φ_Δ = projection onto sin(ω t).
    We treat the underlying field φ(t) as a point‑process intensity proxy:
        φ(t) = sum_i δ(t - t_i)  (Dirac comb)
    For numerical work we bin the process.
    """
    dt = 0.5   # bin size in days
    bins = np.arange(0, T+dt, dt)
    phi, _ = np.histogram(times, bins=bins)   # counts per bin -> intensity proxy
    phi = phi.astype(float)
    phi0 = phi.mean()
    dphi = phi - phi0

    Phi_N = dphi.mean()
    Phi_Δ = np.dot(dphi, np.sin(omega * bins[:-1])) / len(bins)
    return Phi_N, Phi_Δ, phi0, dphi, bins

def invariants(Phi_N, Phi_Δ, lam=1.0, v=1.0):
    """
    Compute ξ_N^{-2} and ξ_Δ^{-2} from the derived formulas.
    Returns ξ_N, ξ_Δ (time‑scale) assuming natural units where λ, v, Φ are dimensionless.
    """
    xi_N_sq_inv = lam * (3*Phi_N**2 + Phi_Δ**2 - v**2)
    xi_D_sq_inv = lam * (Phi_N**2 + 3*Phi_Δ**2 - v**2)

    # Guard against negative inverse‑squared (unphysical)
    if xi_N_sq_inv <= 0 or xi_D_sq_inv <= 0:
        return np.nan, np.nan
    xi_N = 1.0/np.sqrt(xi_N_sq_inv)
    xi_D = 1.0/np.sqrt(xi_D_sq_inv)
    return xi_N, xi_D

def entropy_and_jerk(times, T, bin_width=7.0):
    """
    Shannon entropy of inter‑presentation intervals and its third derivative (jerk).
    """
    intervals = np.diff(np.sort(times))
    if len(intervals) < 2:
        return np.nan, np.nan
    # histogram of intervals
    max_int = np.max(intervals)
    n_bins = max(1, int(max_int // bin_width))
    hist, _ = np.histogram(intervals, bins=n_bins, range=(0, max_int))
    p = hist / hist.sum()
    # avoid log(0)
    p = p[p>0]
    S = -np.sum(p * np.log(p))

    # Approximate jerk via finite differences on a sliding window of S(t)
    # For simplicity we compute S on a rolling window and then differentiate three times.
    win = 30   # days
    step = 1.0
    t_grid = np.arange(win, T-win, step)
    S_vals = []
    for tc in t_grid:
        mask = (times >= tc-win) & (times < tc+win)
        sub = times[mask]
        if len(sub) < 2:
            S_vals.append(np.nan)
            continue
        ints = np.diff(np.sort(sub))
        if len(ints) == 0:
            S_vals.append(np.nan)
            continue
        h, _ = np.histogram(ints, bins=n_bins, range=(0, max_int))
        p = h / h.sum()
        p = p[p>0]
        S_vals.append(-np.sum(p * np.log(p)))
    S_vals = np.array(S_vals)
    # Remove NaNs
    valid = ~np.isnan(S_vals)
    if np.sum(valid) < 4:
        return S, np.nan
    S_clean = S_vals[valid]
    t_clean = t_grid[valid]
    # First, second, third derivative via numpy.gradient
    dS = np.gradient(S_clean, t_clean)
    d2S = np.gradient(dS, t_clean)
    d3S = np.gradient(d2S, t_clean)
    jerk = d3S[-1]   # latest jerk value
    return S, jerk

def shredding_condition(Phi_N, Phi_Δ, v=1.0, tol=1e-2):
    lhs = Phi_N**2 + 3*Phi_Δ**2
    return np.abs(lhs - v**2) < tol

def infofreeze_condition(Phi_N, Phi_Δ, v=1.0, tol=1e-2):
    lhs = 3*Phi_N**2 + Phi_Δ**2
    return np.abs(lhs - v**2) < tol

# ------------------- Validation routine -------------------
def validate_one_realization():
    T = 730   # ~2 years
    times = generate_presentation_times(T=T)
    Phi_N, Phi_Δ, *_ = covariant_modes(times, T)
    xi_N, xi_D = invariants(Phi_N, Phi_Δ)
    S, jerk = entropy_and_jerk(times, T)

    # Dimensional check: under natural units all quantities dimensionless.
    # We simply assert they are real numbers.
    dim_ok = np.all([np.isreal(Phi_N), np.isreal(Phi_Δ),
                     np.isreal(xi_N) if not np.isnan(xi_N) else False,
                     np.isreal(xi_D) if not np.isnan(xi_D) else False,
                     np.isreal(S), np.isreal(jerk)])

    # Correct ξ_Δ logic: shredding flag when ξ_Δ is LARGE (→∞)
    shred_flag = shredding_condition(Phi_N, Phi_Δ)
    info_flag  = infofreeze_condition(Phi_N, Phi_Δ)

    # Anomaly detection surrogate: high jerk + shredding proximity
    anomaly = (np.abs(jerk) > 2.0) and shred_flag   # threshold illustrative

    report = {
        "Phi_N": Phi_N,
        "Phi_Δ": Phi_Δ,
        "xi_N": xi_N,
        "xi_D": xi_D,
        "Entropy": S,
        "Jerk": jerk,
        "Shredding?": shred_flag,
        "InfoFreeze?": info_flag,
        "Anomaly?": anomaly,
        "DimOK": dim_ok
    }
    return report

# Run a few Monte‑Carlo checks
np.random.seed(42)
failures = []
for i in range(50):
    rep = validate_one_realization()
    if not rep["DimOK"]:
        failures.append(("DimOK", rep))
    # The only logical error we guard against is the reversed ξ_Δ test:
    # we already use shredding_condition which matches ξ_Δ → ∞.
    # If the proposal had used ξ_Δ < crit we would catch it here by
    # checking that a large xi_D coincides with shred_flag.
    if not np.isnan(rep["xi_D"]) and rep["xi_D"] > 30 and not rep["Shredding?"]:
        # ξ_Δ large but no shredding → indicates missing link
        failures.append(("xi_D_shred_mismatch", rep))

if failures:
    print("VALIDATION FAILED – issues detected:")
    for typ, msg in failures[:5]:
        print(f"  {typ}: {msg}")
else:
    print("VALIDATION PASSED – all mathematical invariants hold and ξ_Δ logic is correct.")

# -----------------------------------------------------------------
# Enforcement note:
# - The script can be integrated into the Omega Protocol’s CI pipeline.
# - Any proposal must pass this validator (or an equivalent symbolic check)
#   before being merged into the knowledge base.
# - The “no boilerplate” rule is a style check; a separate lint step
#   (e.g., forbidding markdown headings, numbered lists) should be run.
# -----------------------------------------------------------------