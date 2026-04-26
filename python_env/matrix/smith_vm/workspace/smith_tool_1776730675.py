# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for OPSI-Ω

Validates:
  - Non‑negative OPSI
  - Phi_N and Phi_Delta remain in [0,1]
  - MPC-Omega hard constraints:
        OPSI <= 3.0
        Phi_N >= 0.75
        Phi_Delta <= 0.65
  - Weight vector lies in the probability simplex (non‑negative, sum <= w_max)
"""

import numpy as np
from typing import List, Tuple

# -------------------------- Configuration --------------------------
# Default bounds (can be overridden via arguments)
PHI_N0 = 0.9      # baseline process connectivity
PHI_D0 = 0.2      # baseline information asymmetry
ETA1   = 0.3      # influence strength on Phi_N
ETA2   = 0.25     # influence strength on Phi_Delta
TAU1   = 4.0      # weeks -> converted to same time unit as OPSI (days)
TAU2   = 6.0
W_MAX  = 1.0      # maximum allowed sum of weights (simplex)
OPSI_MAX = 3.0
PHI_N_MIN = 0.75
PHI_DELTA_MAX = 0.65
# ------------------------------------------------------------------

def sigmoid(x: float) -> float:
    """Standard logistic sigmoid, output in (0,1)."""
    return 1.0 / (1.0 + np.exp(-x))

def compute_opsii(
    r_P: np.ndarray,
    A: np.ndarray,
    V: np.ndarray,
    L: np.ndarray,
    weights: Tuple[float, float, float, float]
) -> float:
    """
    Compute OPSI for a set of documents.
    Parameters
    ----------
    r_P, A, V, L : 1‑D np.ndarray of equal length N (per‑document metrics)
    weights : (alpha, beta, gamma, delta) – assumed non‑negative
    Returns
    -------
    OPSI scalar (sum over documents)
    """
    alpha, beta, gamma, delta = weights
    # Guard against negative weights
    if any(w < 0 for w in weights):
        raise ValueError("Weight components must be non‑negative.")
    # Termwise contributions
    term = alpha * r_P + beta * (1.0 - A) + gamma * V + delta * np.exp(-L)
    return float(np.sum(term))

def map_to_phi(
    ops_i: float,
    ops_i_past: float,
    avg_A: float,
    phi_n0: float = PHI_N0,
    phi_d0: float = PHI_D0,
    eta1: float = ETA1,
    eta2: float = ETA2,
    tau1: float = TAU1,
    tau2: float = TAU2
) -> Tuple[float, float]:
    """
    Map OPSI (current and lagged) and avg asymmetry to Omega invariants.
    Uses a simple lag: ops_i_past = OPSI(t - tau).
    """
    phi_n = phi_n0 - eta1 * sigmoid(ops_i_past)
    phi_d = phi_d0 + eta2 * (1.0 - avg_A)
    # Clip to [0,1] for safety (should already hold if inputs are sane)
    phi_n = np.clip(phi_n, 0.0, 1.0)
    phi_d = np.clip(phi_d, 0.0, 1.0)
    return phi_n, phi_d

def validate_state(
    ops_i: float,
    phi_n: float,
    phi_d: float,
    weights: Tuple[float, float, float, float]
) -> None:
    """
    Raise ValueError if any Omega invariant or MPC constraint is violated.
    """
    # 1. Weight simplex check
    if any(w < 0 for w in weights):
        raise ValueError(f"Invalid weight vector {weights}: negative component.")
    if sum(weights) > W_MAX + 1e-9:
        raise ValueError(f"Weight sum {sum(weights):.4f} exceeds W_MAX={W_MAX}.")

    # 2. OPSI non‑negative (by construction with non‑negative weights and non‑negative features)
    if ops_i < -1e-9:
        raise ValueError(f"OPSI negative: {ops_i}")

    # 3. Phi invariants
    if not (0.0 <= phi_n <= 1.0):
        raise ValueError(f"Phi_N out of bounds [0,1]: {phi_n}")
    if not (0.0 <= phi_d <= 1.0):
        raise ValueError(f"Phi_Delta out of bounds [0,1]: {phi_d}")

    # 4. MPC-Omega hard constraints
    if ops_i > OPSI_MAX + 1e-9:
        raise ValueError(f"OPSI exceeds maximum {OPSI_MAX}: {ops_i}")
    if phi_n < PHI_N_MIN - 1e-9:
        raise ValueError(f"Phi_N below minimum {PHI_N_MIN}: {phi_n}")
    if phi_d > PHI_DELTA_MAX + 1e-9:
        raise ValueError(f"Phi_Delta exceeds maximum {PHI_DELTA_MAX}: {phi_d}")

    # If we reach here, all checks passed
    return True

# -------------------------- Example / Unit Test --------------------------
def _synthetic_test():
    """Generate fake data and run the validator."""
    np.random.seed(42)
    N = 5  # number of documents
    # Simulate non‑negative raw metrics
    r_P = np.abs(np.random.randn(N)) * 0.5          # changes/day
    A   = np.random.rand(N)                         # entropy normalised [0,1]
    V   = np.abs(np.random.randn(N)) * 0.2          # volatility
    L   = np.abs(np.random.randn(N)) * 10.0         # latency in days

    # Example weight vector (learned, but must be non‑negative and sum <= W_MAX)
    weights = (0.4, 0.3, 0.2, 0.1)  # sum = 1.0

    # Current OPSI
    ops_i = compute_opsii(r_P, A, V, L, weights)
    # Lagged OPSI (simulate using same data for simplicity)
    ops_i_past = ops_i * 0.9
    # Average asymmetry across documents
    avg_A = np.mean(A)

    phi_n, phi_d = map_to_phi(ops_i, ops_i_past, avg_A)

    print(f"Synthetic OPSI: {ops_i:.4f}")
    print(f"Phi_N (ops):   {phi_n:.4f}")
    print(f"Phi_Delta (ops):{phi_d:.4f}")

    try:
        validate_state(ops_i, phi_n, phi_d, weights)
        print("✅ All Omega invariants and MPC constraints satisfied.")
    except ValueError as e:
        print(f"❌ Validation failed: {e}")

if __name__ == "__main__":
    _synthetic_test()