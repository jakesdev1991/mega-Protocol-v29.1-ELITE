# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for OPSI-Ω
---------------------------------------------
Checks that the mathematical formulation of the Operational Permissions
Stress Index (OPSI-Ω) and its mapping to Phi_N, Phi_Delta, correlation
lengths, and the implicit cost function respect the Omega Protocol
invariants.

Run:  python3 validate_opsI.py
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (mirroring the proposal)
# ----------------------------------------------------------------------
def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))

def compute_OPSI(r_P: np.ndarray,
                 A_d: np.ndarray,
                 V_d: np.ndarray,
                 L_d: np.ndarray,
                 alpha: float,
                 beta: float,
                 gamma: float,
                 delta: float) -> np.ndarray:
    """
    OPSI_b(t) = Σ [ α·r_P + β·(1‑A_d) + γ·V_d + δ·exp(-L_d) ]
    All inputs are 1‑D arrays of equal length (per document).
    """
    term = alpha * r_P + beta * (1.0 - A_d) + gamma * V_d + delta * np.exp(-L_d)
    return np.sum(term)

def compute_Phi_N(Phi_N0: float,
                  OPSI: float,
                  eta1: float,
                  tau1: float,
                  t: float) -> float:
    """Phi_N(t) = Phi_N0 - eta1 * sigmoid(OPSI(t - tau1))"""
    # For validation we ignore the time shift; assume OPSI already lagged.
    return Phi_N0 - eta1 * sigmoid(OPSI)

def compute_Phi_Delta(Phi_Delta0: float,
                      A_bar: float,
                      eta2: float,
                      tau2: float,
                      t: float) -> float:
    """Phi_Delta(t) = Phi_Delta0 + eta2 * (1 - A_bar(t - tau2))"""
    return Phi_Delta0 + eta2 * (1.0 - A_bar)

def correlation_lengths(V_d: float,
                        r_P: float,
                        eps: float = 1e-9) -> tuple:
    """xi_N ∝ 1/V_d , xi_Delta ∝ 1/r_p"""
    xi_N = 1.0 / max(V_d, eps)
    xi_D = 1.0 / max(r_P, eps)
    return xi_N, xi_D

def compute_J(OPSI: float,
              s_OPSI: float,
              mu: float) -> float:
    """Implicit cost: J = OPSI + mu * s_OPSI"""
    return OPSI + mu * s_OPSI

# ----------------------------------------------------------------------
# Synthetic data generator (for illustration)
# ----------------------------------------------------------------------
def synthetic_data(n_docs: int = 5):
    np.random.seed(42)
    r_P   = np.abs(np.random.normal(loc=0.5, scale=0.2, size=n_docs))   # changes/day
    A_d   = np.random.uniform(0.0, 1.0, size=n_docs)                  # access asymmetry (entropy norm)
    V_d   = np.abs(np.random.normal(loc=0.1, scale=0.05, size=n_docs)) # volatility
    L_d   = np.abs(np.random.normal(loc=1.0, scale=0.5, size=n_docs)) # latency (days)
    return r_P, A_d, V_d, L_d

# ----------------------------------------------------------------------
# Invariant checks
# ----------------------------------------------------------------------
def validate():
    # ---- Parameters (must respect Omega bounds) ----
    alpha, beta, gamma, delta = 0.25, 0.25, 0.25, 0.25   # non‑negative, sum=1
    assert all(p >= 0 for p in (alpha, beta, gamma, delta)), "Weights must be non‑negative"

    Phi_N0   = 0.8   # baseline process connectivity
    Phi_D0   = 0.3   # baseline information asymmetry
    eta1     = 0.4   # must satisfy eta1 <= Phi_N0
    eta2     = 0.5   # must satisfy eta2 <= 1 - Phi_D0
    mu       = 0.3   # non‑negative

    assert 0.0 <= eta1 <= Phi_N0, f"eta1 ({eta1}) must be in [0, Phi_N0={Phi_N0}]"
    assert 0.0 <= eta2 <= (1.0 - Phi_D0), f"eta2 ({eta2}) must be in [0, 1-Phi_D0={1-Phi_D0}]"
    assert mu >= 0.0, "mu must be non‑negative"

    # ---- Generate data ----
    r_P, A_d, V_d, L_d = synthetic_data(n_docs=10)

    # ---- Compute core quantities ----
    OPSI = compute_OPSI(r_P, A_d, V_d, L_d, alpha, beta, gamma, delta)
    A_bar = np.mean(A_d)                     # simple proxy for department‑averaged asymmetry
    Phi_N = compute_Phi_N(Phi_N0, OPSI, eta1, tau1=0.0, t=0.0)
    Phi_D = compute_Phi_Delta(Phi_D0, A_bar, eta2, tau2=0.0, t=0.0)
    xi_N, xi_D = correlation_lengths(np.mean(V_d), np.mean(r_P))
    s_OPSI = np.abs(OPSI - np.mean([OPSI])) / (np.std([OPSI]) + 1e-9)  # dummy anomaly score
    J = compute_J(OPSI, s_OPSI, mu)

    # ---- Invariant assertions ----
    # 1. OPSI non‑negative
    assert OPSI >= 0.0, f"OPSI must be ≥0, got {OPSI}"
    # 2. Phi_N, Phi_Delta in [0,1]
    assert 0.0 <= Phi_N <= 1.0, f"Phi_N out of bounds: {Phi_N}"
    assert 0.0 <= Phi_D <= 1.0, f"Phi_D out of bounds: {Phi_D}"
    # 3. Correlation lengths positive
    assert xi_N > 0.0, f"xi_N must be >0, got {xi_N}"
    assert xi_D > 0.0, f"xi_D must be >0, got {xi_D}"
    # 4. Cost non‑negative
    assert J >= 0.0, f"Cost J must be ≥0, got {J}"
    # 5. Optional: weights sum to 1 (not strictly required but recommended)
    assert np.isclose(alpha+beta+gamma+delta, 1.0), "Weights should sum to 1 for interpretability"

    print("✅ All Omega Protocol invariants satisfied.")
    print(f"OPSI      = {OPSI:.4f}")
    print(f"Phi_N     = {Phi_N:.4f}")
    print(f"Phi_Delta = {Phi_D:.4f}")
    print(f"xi_N      = {xi_N:.4f}")
    print(f"xi_Delta  = {xi_D:.4f}")
    print(f"J (cost)  = {J:.4f}")

if __name__ == "__main__":
    try:
        validate()
    except AssertionError as e:
        print("❌ Invariant violation:", e)
        raise SystemExit(1)