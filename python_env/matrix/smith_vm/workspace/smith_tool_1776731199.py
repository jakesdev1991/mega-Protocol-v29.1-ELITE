# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for HPCLM‑Ω
-----------------------------------------------
Validates the mathematical soundness of the High‑Performance Computing Leakage Monitor
(HPCLM‑Ω) proposal against the Omega Protocol invariants:
    Φ_N  (market connectivity)
    Φ_Δ  (information asymmetry)
    J*   (cost/objective)

The script is deliberately minimal – it can be dropped into the isolated VM and run
to obtain a pass/fail verdict.
"""

import math
from typing import List, Tuple, NamedTuple

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
class Leak(NamedTuple):
    gpu: int                # number of GPUs in the leaked cluster (>0)
    delay: float            # days between leak date and planned deployment
                               # negative => leak precedes deployment
    conf: int               # confidentiality level 1 (low) – 3 (high)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def compute_hli(leaks: List[Leak],
                alpha: float, beta: float, gamma: float, delta: float) -> float:
    """HLI(t) = Σ[α·log(GPU) + β·exp(-γ·delay) + δ·conf]"""
    total = 0.0
    for l in leaks:
        if l.gpu <= 0:
            raise ValueError("GPU count must be > 0 for log.")
        total += (alpha * math.log(l.gpu) +
                  beta * math.exp(-gamma * l.delay) +
                  delta * l.conf)
    return total

def map_phi_n(hli: float,
              phi_n0: float, eta1: float, tau1: float,
              hli_lag: float) -> float:
    """Φ_N^{(hpc)} = Φ_N^{(0)} + η₁·sigmoid(HLI(t‑τ₁))"""
    # In this validator we simply pass the lagged HLI as an argument.
    return phi_n0 + eta1 * sigmoid(hli_lag - tau1)

def map_phi_delta(hli: float,
                  phi_delta0: float, eta2: float, tau2: float,
                  hli_lag: float) -> float:
    """Φ_Δ^{(hpc)} = Φ_Δ^{(0)} + η₂·HLI(t‑τ₂)"""
    return phi_delta0 + eta2 * (hli_lag - tau2)

def correlation_length(hli: float, eps: float = 1e-9) -> float:
    """ξ ∝ 1/HLI (guard against division by zero)"""
    return 1.0 / max(hli, eps)

def cost_function(hli: float,
                  s_hli: float,
                  lam: float) -> float:
    """J = HLI + λ·s_HLI"""
    return hli + lam * s_hli

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_omega_invariants(leaks: List[Leak],
                              # HLI parameters
                              alpha: float, beta: float, gamma: float, delta: float,
                              # Φ_N mapping
                              phi_n0: float, eta1: float, tau1: float,
                              # Φ_Δ mapping
                              phi_delta0: float, eta2: float, tau2: float,
                              # Anomaly score (s_HLI) – supplied externally
                              s_hli: float,
                              # Cost weight
                              lam: float,
                              # Safety bounds (Omega Protocol invariants)
                              max_hli: float = 5.0,
                              max_phi_n: float = 0.9,
                              max_phi_delta: float = 0.7,
                              # Small epsilon to avoid div‑by‑zero in ξ
                              eps: float = 1e-9) -> Tuple[bool, dict]:
    """
    Returns (is_valid, diagnostics_dict)
    """
    # 1. Compute HLI
    hli = compute_hli(leaks, alpha, beta, gamma, delta)

    # 2. Lagged HLI for Φ mappings (here we use the same HLI as a placeholder;
    #    in production you would shift the time series by τ₁, τ₂).
    hli_lag = hli   # simplistic; replace with actual lagged series if available

    # 3. Map to Ω‑state variables
    phi_n = map_phi_n(hli, phi_n0, eta1, tau1, hli_lag)
    phi_delta = map_phi_delta(hli, phi_delta0, eta2, tau2, hli_lag)

    # 4. Correlation lengths
    xi_n = correlation_length(hli, eps)
    xi_delta = correlation_length(hli, eps)

    # 5. Cost
    J = cost_function(hli, s_hli, lam)

    # 6. Invariant checks
    checks = {
        "HLI ≤ max_hli": hli <= max_hli + eps,
        "Φ_N ≤ max_phi_n": phi_n <= max_phi_n + eps,
        "Φ_Δ ≤ max_phi_delta": phi_delta <= max_phi_delta + eps,
        "ξ_N > 0": xi_n > 0,
        "ξ_Δ > 0": xi_delta > 0,
        "J finite": math.isfinite(J),
    }

    all_ok = all(checks.values())
    diagnostics = {
        "HLI": hli,
        "Φ_N": phi_n,
        "Φ_Δ": phi_delta,
        "ξ_N": xi_n,
        "ξ_Δ": xi_delta,
        "Cost J": J,
        "checks": checks,
    }
    return all_ok, diagnostics

# ----------------------------------------------------------------------
# Example usage (synthetic data)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Synthetic leak list for a quarter (feel free to replace with real data)
    example_leaks = [
        Leak(gpu=256, delay=-30, conf=3),   # leaked 30 days before deployment, highly confidential
        Leak(gpu=512, delay=10, conf=2),    # leaked after deployment date
        Leak(gpu=128, delay=-60, conf=1),
    ]

    # Hyper‑parameters (these would be learned in practice; here we pick values
    # that comfortably satisfy the invariants)
    hp = {
        "alpha": 0.4,
        "beta": 0.3,
        "gamma": 0.02,
        "delta": 0.5,
        "phi_n0": 0.2,
        "eta1": 0.5,
        "tau1": 2.0,      # months → treat as same unit as HLI lag for demo
        "phi_delta0": 0.1,
        "eta2": 0.15,
        "tau2": 3.0,
        "s_hli": 1.2,     # example anomaly score
        "lam": 0.8,
    }

    valid, diag = validate_omega_invariants(
        leaks=example_leaks,
        alpha=hp["alpha"], beta=hp["beta"], gamma=hp["gamma"], delta=hp["delta"],
        phi_n0=hp["phi_n0"], eta1=hp["eta1"], tau1=hp["tau1"],
        phi_delta0=hp["phi_delta0"], eta2=hp["eta2"], tau2=hp["tau2"],
        s_hli=hp["s_hli"],
        lam=hp["lam"],
    )

    print("=== Omega Protocol Validation Result ===")
    print(f"Valid: {valid}")
    for k, v in diag.items():
        if k != "checks":
            print(f"{k}: {v:.4f}")
    print("\nConstraint checks:")
    for c, ok in diag["checks"].items():
        print(f"  {c}: {'PASS' if ok else 'FAIL'}")

    if not valid:
        raise AssertionError("One or more Omega Protocol invariants violated.")