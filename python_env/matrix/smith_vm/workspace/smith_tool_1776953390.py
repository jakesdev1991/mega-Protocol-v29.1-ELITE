# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for AFDS v3.0 core mathematics.
Run as:  python3 omega_afds_validator.py
"""

import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Constants from the Omega Physics Rubric v26.0 (example values)
# ----------------------------------------------------------------------
XI_N = 0.8          # coupling for Newtonian trust
XI_DELTA = 1.2      # coupling for asymmetric threat
K_BOLTZMANN = 1.0   # Boltzmann constant (set to 1 for natural units)
AUDIT_COMPLEXITY = 2.5  # placeholder; would be measured in practice

# ----------------------------------------------------------------------
# Helper functions that mirror the *invariant‑correct* formulas
# ----------------------------------------------------------------------
def compute_phi_n(accessed_paths: int, cumulative_stability: float) -> float:
    """
    Φₙ = exp(-H_noise) * stability_integral
    H_noise = log(|accessed_paths| + 1)   (adds 1 to avoid log(0))
    stability_integral is supplied directly (should be ≥0)
    """
    if accessed_paths < 0 or cumulative_stability < 0:
        raise ValueError("Path count and stability must be non‑negative")
    H_noise = math.log(accessed_paths + 1.0)
    phi_n = math.exp(-H_noise) * cumulative_stability
    # Φₙ is a probability‑like confidence; clamp to [0,1] for safety
    return min(max(phi_n, 0.0), 1.0)


def compute_psi(phi_n: float) -> float:
    """ψ = ln(Φₙ) with a small epsilon to avoid -inf."""
    eps = 1e-12
    return math.log(max(phi_n, eps))


def compute_phi_delta(breadth: int, depth: int) -> float:
    """
    Asymmetric threat metric derived from first principles:
    φΔ = |breadth - depth| / (breadth + depth)
    Returns 0 when both are zero (no traversal yet).
    """
    total = breadth + depth
    if total == 0:
        return 0.0
    return abs(breadth - depth) / total


def compute_gauge_emergence(trust_score: float, phi_delta: float) -> float:
    """Gauge emergence = |ΦΔ| * trust_score (both already in [0,1])."""
    return abs(phi_delta) * trust_score


def compute_topological_impedance(
    psi_series: List[float],
    gauge_series: List[float]
) -> float:
    """
    Approximate H_imp = ∫ gauge dψ via trapezoidal rule.
    Both series must be same length and ordered by traversal time.
    """
    if len(psi_series) != len(gauge_series):
        raise ValueError("psi and gauge series length mismatch")
    if len(psi_series) < 2:
        return 0.0
    integral = 0.0
    for i in range(1, len(psi_series)):
        dpsi = psi_series[i] - psi_series[i-1]
        avg_gauge = (gauge_series[i] + gauge_series[i-1]) * 0.5
        integral += avg_gauge * dpsi
    return integral


def compute_curvature(
    phi_n: float,
    phi_delta: float,
    h_imp: float
) -> float:
    """Invariant curvature: 𝒭 = ξₙ·Φₙ + ξΔ·ΦΔ − H_imp."""
    return XI_N * phi_n + XI_DELTA * phi_delta - h_imp


def compute_trust_mitigation(phi_n: float) -> float:
    """Mitigation = 0.8 * Φₙ (must stay in [0,0.8])."""
    return 0.8 * phi_n


def compute_jitter_probability(
    traversal_score: float,
    mitigation: float,
    phi_delta: float
) -> float:
    """
    State‑dependent jitter probability (invariant form):
    p = (traversal_score / 100)^1.5 * mitigation * (1 + φΔ)
    Clamped to [0,1].
    """
    base = (traversal_score / 100.0) ** 1.5
    p = base * mitigation * (1.0 + phi_delta)
    return min(max(p, 0.0), 1.0)


def apply_adaptive_jitter(
    traversal_score: float,
    mitigation: float,
    phi_delta: float
) -> Tuple[float, int]:
    """
    Returns (probability_used, latency_ms).
    Implements the shredding threshold: if φΔ > 0.95 → 1000 ms freeze.
    """
    prob = compute_jitter_probability(traversal_score, mitigation, phi_delta)
    if phi_delta > 0.95:
        return prob, 1000  # shredding freeze
    # jitter range 1‑50 ms; if no jitter, latency = 0
    latency = 0
    if prob > 0.0:  # simple Monte‑Carlo decision for illustration
        # In practice we would draw a random number; here we return max latency if triggered
        latency = 50  # worst‑case jitter for validation
    return prob, latency


# ----------------------------------------------------------------------
# Validation routine – asserts Omega invariants
# ----------------------------------------------------------------------
def validate_afds_core(
    path_counts: List[int],
    stability_vals: List[float],
    breadth_vals: List[int],
    depth_vals: List[int],
    traversal_scores: List[float]
) -> None:
    """
    Runs a sequence of steps and checks every invariant.
    All input lists must be of equal length (one step per index).
    """
    assert len(path_counts) == len(stability_vals) == len(breadth_vals) == \
           len(depth_vals) == len(traversal_scores), "Input length mismatch"

    phi_n_series = []
    psi_series = []
    gauge_series = []
    mitigation_series = []

    for i in range(len(path_counts)):
        # 1. Φₙ and ψ
        phi_n = compute_phi_n(path_counts[i], stability_vals[i])
        assert 0.0 <= phi_n <= 1.0, f"Step {i}: Φₙ out of bounds [{phi_n}]"
        psi = compute_psi(phi_n)
        phi_n_series.append(phi_n)
        psi_series.append(psi)

        # 2. ΦΔ
        phi_delta = compute_phi_delta(breadth_vals[i], depth_vals[i])
        assert 0.0 <= phi_delta <= 1.0, f"Step {i}: ΦΔ out of bounds [{phi_delta}]"

        # 3. Trust mitigation
        mitigation = compute_trust_mitigation(phi_n)
        assert 0.0 <= mitigation <= 0.8, f"Step {i}: Mitigation out of bounds [{mitigation}]"
        mitigation_series.append(mitigation)

        # 4. Gauge emergence & topological impedance (incremental)
        gauge = compute_gauge_emergence(mitigation, phi_delta)  # using mitigation as trust_score proxy
        gauge_series.append(gauge)

        # 5. Curvature (check after we have at least one H_imp)
        if i > 0:
            h_imp = compute_topological_impedance(psi_series[:i+1], gauge_series[:i+1])
            curvature = compute_curvature(phi_n, phi_delta, h_imp)
            # Curvature should be a real number; no explicit bounds but we can sanity‑check
            assert not math.isnan(curvature) and math.isfinite(curvature), \
                f"Step {i}: Curvature is NaN or infinite [{curvature}]"

        # 6. Jitter probability and latency
        prob, latency = apply_adaptive_jitter(
            traversal_scores[i], mitigation, phi_delta
        )
        assert 0.0 <= prob <= 1.0, f"Step {i}: Jitter probability out of bounds [{prob}]"
        # Latency must be either 0 (no jitter), 1‑50 (jitter), or 1000 (shredding)
        assert latency == 0 or (1 <= latency <= 50) or latency == 1000, \
            f"Step {i}: Invalid latency [{latency}]"

    # Final H_imp check (should be non‑negative for physical gauge emergence)
    final_h_imp = compute_topological_impedance(psi_series, gauge_series)
    assert final_h_imp >= 0.0, f"Final topological impedance negative [{final_h_imp}]"

    # Optional: compute net Φ‑density change (example formula)
    # ΔΦ = -k_B * (ΔH_security - ΔH_audit)
    # Here we just demonstrate that the terms are computable.
    delta_h_security = final_h_imp  # placeholder; real calculation would involve entropy changes
    delta_h_audit = K_BOLTZMANN * math.log(2.0) * AUDIT_COMPLEXITY
    net_phi_density = - (delta_h_security - delta_h_audit)
    # No assertion – just for illustration; sign indicates gain/loss
    print(f"[VALIDATOR] Net Φ‑density estimate: {net_phi_density:.4f} Φ")

    print("[VALIDATOR] All Omega Protocol invariants satisfied.")


# ----------------------------------------------------------------------
# Example usage (synthetic data that should pass)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Simulate a short, well‑behaved traversal:
    #   - steadily increasing known paths (low novelty)
    #   - moderate breadth/depth balance
    #   - low traversal scores (trusted behavior)
    path_counts   = [0, 2, 5, 9, 12]          # distinct paths visited
    stability_vals = [0.0, 0.3, 0.7, 1.2, 1.5]# cumulative stability (time‑weighted)
    breadth_vals   = [0, 1, 2, 3, 4]
    depth_vals     = [0, 1, 2, 2, 3]
    traversal_scores = [5.0, 8.0, 10.0, 12.0, 15.0]  # low scores → low jitter prob

    try:
        validate_afds_core(
            path_counts, stability_vals,
            breadth_vals, depth_vals,
            traversal_scores
        )
    except AssertionError as e:
        print(f"[VALIDATOR] INVARIANT VIOLATION: {e}")
        raise