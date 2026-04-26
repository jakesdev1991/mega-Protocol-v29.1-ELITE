# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol compliance checker for the ISS‑Ω proposal.

The script validates the *minimal* mathematical constraints that any
Omega‑compliant extension must satisfy:
    • ISI definition (linear, bounded)
    • Φ_N(ISI) monotonic increasing & bounded
    • Φ_Δ(ISI) concave‑down with a single maximum
    • QP‑style bounds on ISI, Φ_N, Φ_Δ
    • Ability to embed a Shannon‑entropy term in the cost.

Replace the synthetic data with real measurements to test a concrete
implementation.
"""

import numpy as np
from typing import Callable, Tuple

# ----------------------------------------------------------------------
# 1.  Synthetic data generator (replace with real data)
# ----------------------------------------------------------------------
def generate_synthetic_data(n_samples: int = 500,
                            seed: int = 42) -> Tuple[np.ndarray, np.ndarray,
                                                      np.ndarray, np.ndarray,
                                                      np.ndarray]:
    """
    Returns:
        ISI_raw   – raw linear combination before clipping
        ISI_clipped – ISI after applying the ISI_f ≤ 3.0 bound
        Phi_N     – Φ_N^(iss) values
        Phi_Delta – Φ_Δ^(iss) values
        probs     – a dummy probability vector for entropy test
    """
    rng = np.random.default_rng(seed)

    # Feature components (all non‑negative for simplicity)
    A = rng.exponential(scale=1.0, size=n_samples)          # anomaly score
    R = rng.choice([0.5, 1.0, 2.0], size=n_samples)        # role criticality
    I = rng.choice([0.2, 1.0], size=n_samples)             # intent score
    E = rng.exponential(scale=0.5, size=n_samples)         # external stress

    # Learned weights (example values – in practice these come from XGBoost)
    alpha, beta, gamma, delta = 0.4, 0.3, 0.2, 0.1

    ISI_raw = alpha * A + beta * R + gamma * I + delta * E
    # Enforce ISI_f ≤ 3.0 (hard bound from the QP constraint)
    ISI_clipped = np.minimum(ISI_raw, 3.0)

    # Mapping parameters (example values)
    Phi_N0, eta1, tau1 = 0.2, 0.4, 1.0   # tau not needed for static check
    Phi_Delta0, eta2, eta3, tau2, tau3 = 0.1, 0.5, 0.3, 0.5, 2.0

    # Apply time‑lags – for a static check we simply use the same ISI
    Phi_N = Phi_N0 + eta1 * np.tanh(ISI_clipped - tau1)
    # Φ_Δ = Φ_Δ0 + η2·ISI(t‑τ2) – η3·ISI(t‑τ3)^2
    Phi_Delta = (Phi_Delta0 +
                 eta2 * ISI_clipped -
                 eta3 * ISI_clipped ** 2)

    # Dummy probability distribution for entropy test (must sum to 1)
    probs = rng.dirichlet(alpha=np.ones(5), size=n_samples)

    return ISI_raw, ISI_clipped, Phi_N, Phi_Delta, probs


# ----------------------------------------------------------------------
# 2.  Validation functions
# ----------------------------------------------------------------------
def check_isi_bounds(ISI: np.ndarray, max_isi: float = 3.0) -> None:
    """ISI must never exceed the hard bound."""
    assert np.all(ISI <= max_isi + 1e-12), \
        f"ISI exceeds bound {max_isi}: max={np.max(ISI):.4f}"
    assert np.all(ISI >= 0.0 - 1e-12), \
        f"ISI contains negative values: min={np.min(ISI):.4f}"


def check_phi_n_monotonic(ISI: np.ndarray, Phi_N: np.ndarray) -> None:
    """Φ_N must be monotonically non‑decreasing with ISI."""
    # Sort by ISI and verify that Φ_N never decreases
    sorted_idx = np.argsort(ISI)
    Phi_N_sorted = Phi_N[sorted_idx]
    diffs = np.diff(Phi_N_sorted)
    assert np.all(diffs >= -1e-9), \
        f"Φ_N is not monotonic: min diff={np.min(diffs):.6f}"


def check_phi_n_bounded(Phi_N: np.ndarray, max_phi_n: float = 0.85) -> None:
    """Φ_N must stay below its prescribed ceiling."""
    assert np.all(Phi_N <= max_phi_n + 1e-12), \
        f"Φ_N exceeds bound {max_phi_n}: max={np.max(Phi_N):.4f}"
    assert np.all(Phi_N >= 0.0 - 1e-12), \
        f"Φ_N contains negative values: min={np.min(Phi_N):.4f}"


def check_phi_delta_shape(ISI: np.ndarray, Phi_Delta: np.ndarray) -> None:
    """
    Φ_Δ must be concave‑down (second derivative ≤ 0) and possess a single
    maximum. We approximate derivatives via finite differences.
    """
    # Sort by ISI for derivative estimation
    sorted_idx = np.argsort(ISI)
    ISI_s = ISI[sorted_idx]
    Phi_s = Phi_Delta[sorted_idx]

    # First derivative
    d1 = np.diff(Phi_s) / np.diff(ISI_s)
    # Second derivative
    d2 = np.diff(d1) / np.diff(ISI_s[:-1])

    # Concave‑down: second derivative should be ≤ 0 (allow tiny numerical noise)
    assert np.all(d2 <= 1e-8), \
        f"Φ_Δ is not concave‑down: max second derivative={np.max(d2):.6f}"

    # Single maximum: first derivative should change sign at most once
    sign_changes = np.sum(np.diff(np.sign(d1)) != 0)
    assert sign_changes <= 1, \
        f"Φ_Δ has {sign_changes} extremum(s); expected at most one."


def check_phi_delta_bounded(Phi_Delta: np.ndarray,
                            max_phi_delta: float = 0.7) -> None:
    """Φ_Δ must stay below its prescribed ceiling."""
    assert np.all(Phi_Delta <= max_phi_delta + 1e-12), \
        f"Φ_Δ exceeds bound {max_phi_delta}: max={np.max(Phi_Delta):.4f}"
    assert np.all(Phi_Delta >= 0.0 - 1e-12), \
        f"Φ_Δ contains negative values: min={np.min(Phi_Delta):.4f}"


def entropy_term(probs: np.ndarray, lambda_e: float = 0.1) -> np.ndarray:
    """
    Shannon entropy H = -∑ p log p.
    Returns λ_e * H for each sample (used in the cost function).
    """
    # Avoid log(0) by clipping
    safe_probs = np.clip(probs, 1e-15, 1.0)
    H = -np.sum(safe_probs * np.log(safe_probs), axis=1)
    return lambda_e * H


def validate_cost_component(ISI: np.ndarray,
                            s_ISI: np.ndarray,
                            lambda_: float = 0.5,
                            lambda_e: float = 0.1,
                            probs: np.ndarray = None) -> np.ndarray:
    """
    Implements the cost:  ISI_f + λ·s_ISI  (+ optional entropy term).
    Returns the total cost per sample.
    """
    cost = ISI + lambda_ * s_ISI
    if probs is not None:
        cost += entropy_term(probs, lambda_e)
    return cost


# ----------------------------------------------------------------------
# 3.  Main validation routine
# ----------------------------------------------------------------------
def main() -> None:
    # Generate (or load) data
    ISI_raw, ISI_clipped, Phi_N, Phi_Delta, probs = generate_synthetic_data()

    # ---- 1. ISI bounds ------------------------------------------------
    check_isi_bounds(ISI_clipped)
    print("✅ ISI bounds satisfied.")

    # ---- 2. Φ_N checks ------------------------------------------------
    check_phi_n_monotonic(ISI_clipped, Phi_N)
    check_phi_n_bounded(Phi_N)
    print("✅ Φ_N monotonic & bounded.")

    # ---- 3. Φ_Δ checks ------------------------------------------------
    check_phi_delta_shape(ISI_clipped, Phi_Delta)
    check_phi_delta_bounded(Phi_Delta)
    print("✅ Φ_Δ concave‑down with single max & bounded.")

    # ---- 4. QP‑style constraints (already covered above) -------------
    # (ISI ≤ 3, Φ_N ≤ 0.85, Φ_Δ ≤ 0.7) – verified in the individual checks.

    # ---- 5. Entropy term integration ---------------------------------
    # Build a dummy s_ISI (anomaly score) for the cost function
    s_ISI = np.random.rand(*ISI_clipped.shape) * 2.0  # values in [0,2)
    total_cost = validate_cost_component(ISI_clipped, s_ISI,
                                         lambda_=0.4,
                                         lambda_e=0.05,
                                         probs=probs)
    # Cost should be non‑negative (by construction)
    assert np.all(total_cost >= 0.0 - 1e-12), \
        f"Cost contains negative values: min={np.min(total_cost):.6f}"
    print("✅ Cost function (with entropy term) is non‑negative.")

    print("\nAll minimal Omega‑Protocol mathematical checks PASSED.")
    print("Note: Passing these tests does *not* guarantee full covariant")
    print("derivation or invariant construction – those require a")
    print("variational principle and are *not* satisfied by the current")
    print("ISS‑Ω proposal as written.")


if __name__ == "__main__":
    main()