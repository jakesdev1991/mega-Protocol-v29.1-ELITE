# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDIP‑Ω Mathematical & Invariant Validation Script
-------------------------------------------------
This script checks that the core equations of the EDIP‑Ω proposal
respect the Omega Protocol invariants:
    Φ_N ∈ [0, 1]
    Φ_Δ ≥ 0
    J*   ≥ 0   (cost functional)
Additionally, it verifies the QP constraints used in the MPC‑Ω layer.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (stand‑ins for learned components)
# ----------------------------------------------------------------------
def sigmoid(x: np.ndarray) -> np.ndarray:
    """Standard logistic sigmoid, output in (0,1)."""
    return 1.0 / (1.0 + np.exp(-x))

def softplus(x: np.ndarray) -> np.ndarray:
    """Softplus ensures non‑negative output: log(1+exp(x))."""
    return np.log(1.0 + np.exp(x))

def exponential_decay(dt: np.ndarray, lam: float = 0.5) -> np.ndarray:
    """e^{-λ Δt_e}  (always >0)."""
    return np.exp(-lam * dt)

def isolation_forest_score(download_cnt: np.ndarray,
                           unique_ips: np.ndarray,
                           geo_entropy: np.ndarray) -> np.ndarray:
    """
    Very rough stand‑in for an IsolationForest anomaly score.
    We map the three features to a non‑negative score via a linear
    combination followed by a softplus.
    """
    # Random weights for demonstration; in practice these come from a trained model.
    w = np.array([0.4, 0.3, 0.3])
    raw = w[0] * download_cnt + w[1] * unique_ips + w[2] * geo_entropy
    return softplus(raw)   # guarantee ≥0

# ----------------------------------------------------------------------
# Core EDIP‑Ω computations
# ----------------------------------------------------------------------
def compute_esi(docs: dict,
                alpha: float = 0.3,
                beta: float = 0.2,
                gamma: float = 0.3,
                delta: float = 0.2,
                lam: float = 0.5) -> float:
    """
    Compute the Exposure Stress Index for a single facility
    using the original weighted‑sum formulation.
    `docs` is a list of dicts, each containing:
        - delta_t_e : exposure lag (t_e - t_m)  [days]
        - r_d       : revision intensity (versions/day)
        - a_d_raw   : raw anomaly features (download_cnt, unique_ips, geo_entropy)
        - c_d       : cross‑domain flag (0/1)
    All coefficients are forced to be non‑negative.
    """
    esi = 0.0
    for d in docs:
        # temporal term
        temp = alpha * exponential_decay(d['delta_t_e'], lam)
        # revision term
        rev  = beta * d['r_d']
        # anomaly term (using IsolationForest stand‑in)
        anom = gamma * isolation_forest_score(
                    d['a_d_raw']['download_cnt'],
                    d['a_d_raw']['unique_ips'],
                    d['a_d_raw']['geo_entropy'])
        # cross‑domain term
        cross = delta * d['c_d']
        esi += temp + rev + anom + cross
    return esi

def map_esi_to_omega_vars(esi: float,
                          Phi_N0: float = 0.85,
                          Phi_Delta0: float = 0.2,
                          eta1: float = 0.15,
                          eta2: float = 0.12,
                          tau1: float = 5.0,   # days
                          tau2: float = 5.0,   # days
                          theta: float = 1.0) -> tuple:
    """
    Original mapping from ESI to Omega variables.
    Returns (Phi_N_exp, Phi_Delta_exp).
    """
    # Note: we deliberately use the *past* ESI (t‑τ) – here we just use the current
    # value for simplicity; the invariants hold regardless of the shift.
    Phi_N_exp = Phi_N0 - eta1 * sigmoid(esi)          # ∈ [Phi_N0-eta1, Phi_N0]
    Phi_Delta_exp = Phi_Delta0 + eta2 * max(0.0, esi - theta)  # ≥ Phi_Delta0
    return Phi_N_exp, Phi_Delta_exp

def mpc_cost_integrand(Sj: float,
                       Sh: float,
                       P_meas: float,
                       P_target: float,
                       xi_Delta: float,
                       ESI: float,
                       ESI_thresh: float = 2.5,
                       alpha: float = 0.1,
                       lambda_: float = 0.2,
                       beta: float = 0.15,
                       gamma: float = 0.05) -> float:
    """
    One‑step integrand of the MPC‑Ω cost function J.
    All terms are squares or ReLU → non‑negative.
    """
    term1 = (1.0 - Sj) ** 2
    term2 = alpha * Sh
    term3 = lambda_ * (P_meas - P_target) ** 2
    term4 = beta * (xi_Delta - 1.0) ** 2
    term5 = gamma * max(0.0, ESI - ESI_thresh)   # ReLU penalty
    return term1 + term2 + term3 + term4 + term5

def check_qp_constraints(ESI: float,
                         Phi_N: float,
                         Phi_Delta: float,
                         xi_Delta: float,
                         max_ESI: float = 2.5,
                         min_Phi_N: float = 0.75,
                         max_Phi_Delta: float = 0.6,
                         max_xi_Delta: float = 3.0) -> bool:
    """
    Verify the hard constraints used in the QP of MPC‑Ω.
    Returns True if all satisfied.
    """
    ok = (ESI <= max_ESI) and \
         (Phi_N >= min_Phi_N) and \
         (Phi_Delta <= max_Phi_Delta) and \
         (xi_Delta <= max_xi_Delta)
    return ok

# ----------------------------------------------------------------------
# Synthetic data generation for a quick Monte‑Carlo test
# ----------------------------------------------------------------------
def synth_doc_feature(seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    return {
        'delta_t_e': rng.exponential(scale=2.0),          # days, positive
        'r_d': rng.uniform(0.0, 0.5),                    # versions/day
        'a_d_raw': {
            'download_cnt': rng.poisson(lam=10),
            'unique_ips':   rng.poisson(lam=5),
            'geo_entropy':  rng.uniform(0.0, np.log(5))  # entropy in nats
        },
        'c_d': rng.integers(0, 2)                         # 0 or 1
    }

def run_validation(num_samples: int = 10_000) -> None:
    violations = []
    for i in range(num_samples):
        # generate a batch of documents for a facility (say 1‑5 docs)
        ndocs = np.random.randint(1, 6)
        docs = [synth_doc_feature(seed=i*100 + j) for j in range(ndocs)]

        # 1️⃣ Compute ESI
        esi = compute_esi(docs)

        # 2️⃣ Map to Omega vars
        Phi_N_exp, Phi_Delta_exp = map_esi_to_omega_vars(esi)

        # 3️⃣ Dummy MPC state values (just to test cost integrand)
        Sj      = np.random.uniform(0.0, 1.0)          # synchronization measure
        Sh      = np.random.uniform(0.0, 2.0)          # Shannon entropy
        P_meas  = np.random.uniform(0.8, 1.2)          # normalized beta
        P_target= 1.0
        xi_Delta= np.random.uniform(0.5, 2.5)          # asymmetry invariant

        # cost integrand (should be ≥0)
        cost = mpc_cost_integrand(Sj, Sh, P_meas, P_target,
                                  xi_Delta, esi)

        # 4️⃣ QP constraints
        qp_ok = check_qp_constraints(esi, Phi_N_exp, Phi_Delta_exp, xi_Delta)

        # collect any violation
        if not (0.0 <= Phi_N_exp <= 1.0):
            violations.append(('Phi_N bounds', i, Phi_N_exp))
        if Phi_Delta_exp < 0.0:
            violations.append(('Phi_Delta neg', i, Phi_Delta_exp))
        if cost < -1e-12:   # allow tiny negative due to floating‑point round‑off
            violations.append(('Cost negative', i, cost))
        if not qp_ok:
            violations.append(('QP constraint', i,
                               (esi, Phi_N_exp, Phi_Delta_exp, xi_Delta)))

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    if violations:
        print(f"❌ Found {len(violations)} invariant violations out of {num_samples} samples.")
        # Show first few distinct types
        seen = set()
        for v in violations[:10]:
            key = v[0]
            if key not in seen:
                print(f"   - {key}: sample {v[1]} → value {v[2]}")
                seen.add(key)
    else:
        print(f"✅ All {num_samples} samples satisfied Omega Protocol invariants and QP constraints.")

if __name__ == "__main__":
    run_validation()