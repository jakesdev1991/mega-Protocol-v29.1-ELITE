# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Conference Network Embedding for Micro‑Cap Resilience (CNEM‑Ω) proposal.
Checks mathematical soundness and compliance with the Omega Protocol invariants:
    • Φ_N  (strategic connectivity) must be non‑decreasing with NRS.
    • Φ_Δ  (information asymmetry) must be non‑increasing with NRS and non‑decreasing with clustering.
    • J*   (the MPC‑Ω cost) must be ≥ 0 for all feasible states.
    • Hard constraints: NRS ≥ 0.35, Φ_N ≥ 0.7, Φ_Δ ≤ 0.6.
"""

import numpy as np
from scipy.special import expit  # logistic sigmoid

# ----------------------------------------------------------------------
# Helper functions (directly taken from the proposal)
# ----------------------------------------------------------------------
def zscore_4q(series: np.ndarray) -> np.ndarray:
    """4‑quarter rolling z‑score (std over window of 4). Edge handling: use global std for simplicity."""
    mu = np.mean(series)
    sigma = np.std(series) + 1e-12
    return (series - mu) / sigma

def compute_NRS(k, b, ev, cc, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1):
    """
    NRS_i(q) = α·Z(k) + β·b + γ·ev − δ·Z(cc)
    All inputs are raw centrality measures for a single micro‑cap at a single quarter.
    """
    Zk = zscore_4q(np.array([k]))[0]   # pretend we have a history; here just scale
    Zcc = zscore_4q(np.array([cc]))[0]
    return alpha * Zk + beta * b + gamma * ev - delta * Zcc

def map_to_PhiN(NRS, PhiN0=0.5, eta1=0.3, tau1=3, mu_NRS=0.0, sigma_NRS=1.0):
    """
    Φ_N^(net)(t) = Φ_N^(0) + η1 * sigmoid( (NRS(t‑τ1)‑μ_NRS)/σ_NRS )
    """
    return PhiN0 + eta1 * expit((NRS - mu_NRS) / sigma_NRS)

def map_to_PhiDelta(NRS, cc, PhiDelta0=0.5, eta2=0.25, eta3=0.15,
                    tau2=2, tau3=4, mu_NRS=0.0, sigma_NRS=1.0):
    """
    Φ_Δ^(net)(t) = Φ_Δ^(0) − η2·NRS(t‑τ2) + η3·cc(t‑τ3)
    """
    return PhiDelta0 - eta2 * NRS + eta3 * cc

def anomaly_score(NRS_series):
    """STL‑like decomposition approximated by detrending with linear fit; residual std used."""
    t = np.arange(len(NRS_series))
    coeffs = np.polyfit(t, NRS_series, 1)
    trend = np.polyval(coeffs, t)
    residual = NRS_series - trend
    sigma_res = np.std(residual) + 1e-12
    return np.abs(residual) / sigma_res

def mpc_cost(NRS, s_NRS, PhiDelta, lambda1=1.0, lambda2=1.0):
    """
    J = ∫[ (1−NRS)^2 + λ1·s_NRS^2 + λ2·max(0, Φ_Δ−0.6) ] dt
    For validation we evaluate the integrand at a point.
    """
    term1 = (1.0 - NRS) ** 2
    term2 = lambda1 * s_NRS ** 2
    term3 = lambda2 * max(0.0, PhiDelta - 0.6)
    return term1 + term2 + term3

def check_constraints(NRS, PhiN, PhiDelta):
    """Hard constraints from the MPC‑Ω formulation."""
    return (NRS >= 0.35) and (PhiN >= 0.7) and (PhiDelta <= 0.6)

# ----------------------------------------------------------------------
# Validation suite
# ----------------------------------------------------------------------
def run_validation():
    np.random.seed(42)
    n_samples = 1000

    # Generate plausible raw centrality values (bounded for realism)
    k_raw   = np.random.uniform(0, 30, n_samples)   # degree
    b_raw   = np.random.uniform(0, 1, n_samples)    # betweenness (norm)
    ev_raw  = np.random.uniform(0, 1, n_samples)    # eigenvector
    cc_raw  = np.random.uniform(0, 1, n_samples)    # clustering

    # Compute NRS
    NRS = compute_NRS(k_raw, b_raw, ev_raw, cc_raw)

    # Map to Omega vars (using a single time‑step; lag ignored for static check)
    PhiN  = map_to_PhiN(NRS)
    PhiD  = map_to_PhiDelta(NRS, cc_raw)

    # Anomaly score (need a series – we reuse NRS as a pseudo‑time series)
    sNRS = anomaly_score(NRS)

    # Cost
    J = mpc_cost(NRS, sNRS, PhiD)

    # ------------------------------------------------------------------
    # 1. Mathematical soundness checks
    # ------------------------------------------------------------------
    # NRS should be a real number (no NaNs)
    assert np.all(np.isfinite(NRS)), "NRS contains non‑finite values"

    # Sigmoid output in (0,1) → PhiN in [PhiN0, PhiN0+eta1]
    assert np.all((PhiN >= 0.5) & (PhiN <= 0.5 + 0.3)), "PhiN mapping out of expected range"

    # PhiDelta should stay within reasonable bounds given coefficients
    # Worst case: NRS=1, cc=1 → PhiD = 0.5 -0.25*1 +0.15*1 = 0.4
    # Best case: NRS=0, cc=0   → PhiD = 0.5
    assert np.all((PhiD >= 0.4) & (PhiD <= 0.5)), "PhiDelta mapping out of expected range"

    # Anomaly score non‑negative
    assert np.all(sNRS >= 0), "Anomaly score negative"

    # Cost non‑negative (by construction)
    assert np.all(J >= 0), "MPC cost negative"

    # ------------------------------------------------------------------
    # 2. Monotonicity w.r.t. Omega invariants
    # ------------------------------------------------------------------
    # PhiN should increase with NRS (check via Spearman correlation)
    from scipy.stats import spearmanr
    rho_N, p_N = spearmanr(NRS, PhiN)
    assert rho_N > 0.9, f"PhiN not monotonic with NRS (ρ={rho_N:.3f})"

    # PhiDelta should decrease with NRS and increase with cc
    rho_D_N, p_D_N = spearmanr(NRS, PhiD)
    assert rho_D_N < -0.9, f"PhiDelta not decreasing with NRS (ρ={rho_D_N:.3f})"
    rho_D_cc, p_D_cc = spearmanr(cc_raw, PhiD)
    assert rho_D_cc > 0.4, f"PhiDelta not increasing with clustering (ρ={rho_D_cc:.3f})"

    # ------------------------------------------------------------------
    # 3. Constraint satisfaction for a feasible subset
    # ------------------------------------------------------------------
    feasible = check_constraints(NRS, PhiN, PhiD)
    feas_count = np.sum(feasible)
    # Expect at least some feasible points given the ranges we chose
    assert feas_count > 0, "No sample satisfies the hard constraints"
    print(f"Feasible samples: {feas_count}/{n_samples}")

    # ------------------------------------------------------------------
    # 4. Cost behavior on feasible vs infeasible region
    # ------------------------------------------------------------------
    cost_feas = J[feasible]
    cost_infeas = J[~feasible]
    # On average, infeasible points should have higher cost due to penalty term
    assert np.mean(cost_infeas) >= np.mean(cost_feas), "Cost does not penalize infeasibility"

    print("All validation checks passed.")
    return {
        "NRS_mean": np.mean(NRS),
        "PhiN_mean": np.mean(PhiN),
        "PhiD_mean": np.mean(PhiD),
        "feasible_ratio": feas_count / n_samples,
        "avg_cost_feas": np.mean(cost_feas),
        "avg_cost_infeas": np.mean(cost_infeas)
    }

if __name__ == "__main__":
    stats = run_validation()
    print("\nSummary statistics:")
    for k, v in stats.items():
        print(f"{k}: {v:.4f}")