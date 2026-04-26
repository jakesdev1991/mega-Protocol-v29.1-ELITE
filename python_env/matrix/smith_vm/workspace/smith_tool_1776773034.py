# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for NETT-Ω mathematical soundness and Omega Protocol compliance.
Assumes normalized invariants Φ_N, Φ_Δ ∈ [0, 1] and NES ∈ [0, 1].
"""

import numpy as np
from typing import List, Tuple

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))

def validate_narrative_features(features: dict) -> bool:
    """
    Each narrative feature should be a non‑negative real; we expect them already
    normalized to [0,1] for simplicity.
    """
    for name, val in features.items():
        if not (0.0 <= val <= 1.0):
            print(f"Feature '{name}' out of bounds: {val}")
            return False
    return True

def compute_NES(feature_vec: np.ndarray, model_weights: np.ndarray, bias: float) -> float:
    """
    Linear surrogate of the gradient‑boosted classifier followed by Platt scaling.
    In practice replace with the actual GBT + Platt; here we just enforce bounds.
    """
    raw = np.dot(feature_vec, model_weights) + bias
    # Platt scaling: probability = 1 / (1 + exp(A*raw + B))
    A, B = 1.0, 0.0   # placeholder; real values would be learned
    prob = 1.0 / (1.0 + np.exp(A * raw + B))
    if not (0.0 <= prob <= 1.0):
        raise ValueError(f"NES probability out of range: {prob}")
    return prob

def update_phi_n(phi_n0: float, avg_nes: float, eta1: float) -> float:
    """Φ_N update per the proposal."""
    return phi_n0 + eta1 * sigmoid(avg_nes)

def update_phi_delta(phi_delta0: float, std_nes: float, eta2: float) -> float:
    """Φ_Δ update per the proposal."""
    return phi_delta0 - eta2 * std_nes

def validate_omega_invariants(phi_n: float, phi_delta: float,
                              phi_n_bounds: Tuple[float,float] = (0.0,1.0),
                              phi_delta_bounds: Tuple[float,float] = (0.0,1.0)) -> bool:
    """Check that invariants stay inside their allowed intervals."""
    lo_n, hi_n = phi_n_bounds
    lo_d, hi_d = phi_delta_bounds
    if not (lo_n <= phi_n <= hi_n):
        print(f"Φ_N out of bounds: {phi_n}")
        return False
    if not (lo_d <= phi_delta <= hi_d):
        print(f"Φ_Δ out of bounds: {phi_delta}")
        return False
    return True

def validate_mpc_constraints(avg_nes: float, phi_n: float, phi_delta: float) -> bool:
    """MPC‑Ω constraints from the proposal."""
    if avg_nes < 0.6:
        print(f"MPC constraint violated: average NES = {avg_nes} < 0.6")
        return False
    if phi_n < 0.8:
        print(f"MPC constraint violated: Φ_N = {phi_n} < 0.8")
        return False
    if phi_delta > 0.5:
        print(f"MPC constraint violated: Φ_Δ = {phi_delta} > 0.5")
        return False
    return True

def singularity_prediction(residual: float, sigma_res: float,
                           phi_delta_nar: float) -> bool:
    """Return True if breakthrough is flagged."""
    if sigma_res <= 0:
        raise ValueError("Sigma residual must be > 0 for anomaly score.")
    s_nes = abs(residual) / sigma_res
    return s_nes > 2.5 and phi_delta_nar < 0.4

def run_validation_snapshot():
    """Create a toy dataset and run all checks."""
    # --- 1. Synthetic feature vectors for 3 tokamak projects ---
    np.random.seed(42)
    n_projects = 3
    n_features = 6  # clarity, persuasiveness, risk_framing, visual, confidence, story
    # Features already normalized to [0,1]
    feature_matrix = np.random.rand(n_projects, n_features)

    # --- 2. Dummy model (weights + bias) ---
    model_weights = np.random.randn(n_features) * 0.1
    bias = 0.0

    # --- 3. Compute NES for each project ---
    nes_list = []
    for i in range(n_projects):
        feats = feature_matrix[i]
        if not validate_narrative_features({f"f{j}":feats[j] for j in range(n_features)}):
            return False
        nes = compute_NES(feats, model_weights, bias)
        nes_list.append(nes)
        print(f"Project {i}: NES = {nes:.3f}")

    avg_nes = np.mean(nes_list)
    std_nes = np.std(nes_list, ddof=0)
    print(f"\nAggregate NES: mean = {avg_nes:.3f}, std = {std_nes:.3f}")

    # --- 4. Omega invariant updates ---
    phi_n0, phi_delta0 = 0.5, 0.5   # baseline values
    eta1, eta2 = 0.3, 0.2          # chosen to keep updates in [0,1]

    phi_n = update_phi_n(phi_n0, avg_nes, eta1)
    phi_delta = update_phi_delta(phi_delta0, std_nes, eta2)

    print(f"Updated Φ_N = {phi_n:.3f} (baseline {phi_n0})")
    print(f"Updated Φ_Δ = {phi_delta:.3f} (baseline {phi_delta0})")

    if not validate_omega_invariants(phi_n, phi_delta):
        return False

    # --- 5. MPC‑Ω constraints ---
    if not validate_mpc_constraints(avg_nes, phi_n, phi_delta):
        return False

    # --- 6. Singularity prediction (dummy residual) ---
    residual = 0.8   # example deviation from trend
    sigma_res = 0.3  # must be >0
    flagged = singularity_prediction(residual, sigma_res, phi_delta)
    print(f"\nSingularity flagged? {flagged} (s_NES = {abs(residual)/sigma_res:.2f})")

    # --- 7. Additional sanity checks ---
    # Ensure sigmoid argument is average NES (already in [0,1])
    assert 0.0 <= avg_nes <= 1.0, "Average NES out of [0,1]"
    # Ensure std non‑negative
    assert std_nes >= 0.0, "Standard deviation negative"

    print("\nAll validation checks passed.")
    return True

if __name__ == "__main__":
    success = run_validation_snapshot()
    exit(0 if success else 1)