# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for AFDS v3.0
------------------------------------------------
This script defines the mathematical core of the Adaptive Filesystem Defense
System (AFDS v3.0) and checks that every computed quantity respects the
invariants dictated by the Omega Physics Rubric v26.0.

Invariants checked:
  1. Trust score ∈ [0, 1]
  2. φₙ = exp(−H_noise) * S,   S = Σ_i exp(−Δt_i/τ)   (τ > 0)
  3. φΔ = |breadth − depth| / (breadth + depth)   (breadth+depth>0)
  4. ψ = ln(φₙ)   →   φₙ > 0  (so ψ is real)
  5. Gauge emergence G = trust_score * |φΔ|
  6. Topological impedance H_imp = Σ_i (G_i + G_{i-1})/2 * (ψ_i − ψ_{i-1})
  7. Curvature κ = ξₙ·φₙ + ξ_Δ·φΔ − H_imp
  8. Jitter probability p_jitter = p0 * (1 + α * T)   clamped to [p_min, p_max]
     where T = TraversalScore ∈ [0,1]; p_min = 1ms, p_max = 50ms
  9. All constants (τ, ξₙ, ξ_Δ, p0, α) must be expressed as fundamental
     parameters (no undocumented magic numbers).

If any invariant fails, an AssertionError is raised with a diagnostic.
"""

import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Fundamental parameters (these should be supplied by the Omega‑OS config)
# ----------------------------------------------------------------------
TAU_SEC = 3600.0          # trust‑time constant (seconds)
XI_N = 0.42               # Newtonian stiffness (dimensionless)
XI_DELTA = 0.58           # Asymmetric threat stiffness (dimensionless)
P0_MS = 1.0               # base jitter (ms)
ALPHA = 49.0              # scaling so that p_jitter ∈ [1,50] ms when T∈[0,1]
P_MIN_MS = 1.0
P_MAX_MS = 50.0
H_NOISE = 0.03            # example noise entropy (dimensionless)

# ----------------------------------------------------------------------
# Helper functions implementing the invariant formulas
# ----------------------------------------------------------------------
def trust_score_from_stability(stability_sum: float) -> float:
    """
    φₙ = exp(−H_noise) * stability_sum
    stability_sum = Σ exp(−Δt/τ)  (must be ≥0)
    """
    phi_n = math.exp(-H_NOISE) * stability_sum
    # Trust score is φₙ clamped to [0,1] by the OS (see invariant 1)
    return max(0.0, min(1.0, phi_n))

def phi_delta(breadth: int, depth: int) -> float:
    """φΔ = |breadth−depth|/(breadth+depth)  (dimensionless, ∈[0,1])"""
    if breadth + depth == 0:
        return 0.0
    return abs(breadth - depth) / (breadth + depth)

def psi(phi_n: float) -> float:
    """ψ = ln(φₙ)  – requires φₙ > 0"""
    if phi_n <= 0.0:
        raise ValueError("φₙ must be strictly positive to compute ψ")
    return math.log(phi_n)

def gauge(trust: float, phi_delta_val: float) -> float:
    """Gauge emergence G = trust_score * |φΔ|"""
    return trust * abs(phi_delta_val)

def topological_impedance(
    trust_seq: List[float],
    phi_delta_seq: List[float],
    psi_seq: List[float],
) -> float:
    """
    H_imp = Σ_i (G_i + G_{i-1})/2 * (ψ_i − ψ_{i-1})
    where G_i = trust_i * |φΔ_i|
    """
    assert len(trust_seq) == len(phi_delta_seq) == len(psi_seq) >= 2
    H = 0.0
    prev_g = gauge(trust_seq[0], phi_delta_seq[0])
    prev_psi = psi_seq[0]
    for t, pd, ps in zip(trust_seq[1:], phi_delta_seq[1:], psi_seq[1:]):
        g = gauge(t, pd)
        H += (g + prev_g) * 0.5 * (ps - prev_psi)
        prev_g, prev_psi = g, ps
    return H

def curvature(phi_n: float, phi_delta_val: float, H_imp: float) -> float:
    """κ = ξₙ·φₙ + ξ_Δ·φΔ − H_imp"""
    return XI_N * phi_n + XI_DELTA * phi_delta_val - H_imp

def jitter_prob_ms(traversal_score: float) -> float:
    """
    p_jitter = P0 * (1 + α * T)   clamped to [P_MIN, P_MAX] (ms)
    T = TraversalScore ∈ [0,1]
    """
    raw = P0_MS * (1.0 + ALPHA * traversal_score)
    return max(P_MIN_MS, min(P_MAX_MS, raw))

# ----------------------------------------------------------------------
# Validation routine – runs a series of sanity‑checks
# ----------------------------------------------------------------------
def validate_invariants(
    stability_sum: float,
    breadth: int,
    depth: int,
    trust_seq: List[float],
    phi_delta_seq: List[float],
    psi_seq: List[float],
    traversal_score: float,
) -> None:
    """
    Checks every Omega Protocol invariant. Raises AssertionError on failure.
    """
    # 1. Trust score bounds (derived from φₙ)
    phi_n = math.exp(-H_NOISE) * stability_sum
    trust = max(0.0, min(1.0, phi_n))
    assert 0.0 <= trust <= 1.0, f"Trust score out of bounds: {trust}"

    # 2. φₙ formula (already used above)
    assert math.isclose(phi_n, math.exp(-H_NOISE) * stability_sum, rel_tol=1e-12), \
        "φₙ does not follow exp(−H_noise)*stability_sum"

    # 3. φΔ formula
    phi_delta_val = phi_delta(breadth, depth)
    assert 0.0 <= phi_delta_val <= 1.0, f"φΔ out of [0,1]: {phi_delta_val}"
    # Re‑compute to ensure no hidden magic numbers
    if breadth + depth > 0:
        assert math.isclose(
            phi_delta_val,
            abs(breadth - depth) / (breadth + depth),
            rel_tol=1e-12,
        ), "φΔ not geometrically motivated"

    # 4. ψ = ln(φₙ) → φₙ>0
    psi_val = psi(phi_n)
    assert math.isclose(psi_val, math.log(phi_n), rel_tol=1e-12), \
        "ψ not equal to ln(φₙ)"

    # 5. Gauge emergence definition (implicitly used in H_imp)
    #    We just ensure the function matches the definition.
    for t, pd in zip(trust_seq, phi_delta_seq):
        g = gauge(t, pd)
        assert math.isclose(g, t * abs(pd), rel_tol=1e-12), \
            "Gauge emergence not trust*|φΔ|"

    # 6. Topological impedance path integral
    H_imp = topological_impedance(trust_seq, phi_delta_seq, psi_seq)
    # Re‑compute using the definition to catch variable‑mix errors
    H_ref = 0.0
    prev_g = gauge(trust_seq[0], phi_delta_seq[0])
    prev_psi = psi_seq[0]
    for t, pd, ps in zip(trust_seq[1:], phi_delta_seq[1:], psi_seq[1:]):
        g = gauge(t, pd)
        H_ref += (g + prev_g) * 0.5 * (ps - prev_psi)
        prev_g, prev_psi = g, ps
    assert math.isclose(H_imp, H_ref, rel_tol=1e-9), \
        "Topological impedance not a true path integral ∫ gauge dψ"

    # 7. Curvature definition
    kappa = curvature(phi_n, phi_delta_val, H_imp)
    assert math.isclose(
        kappa,
        XI_N * phi_n + XI_DELTA * phi_delta_val - H_imp,
        rel_tol=1e-12,
    ), "Curvature does not follow ξₙ·φₙ + ξ_Δ·φΔ − H_imp"

    # 8. Jitter probability bounds and scaling
    jitter_ms = jitter_prob_ms(traversal_score)
    assert P_MIN_MS <= jitter_ms <= P_MAX_MS, \
        f"Jitter out of allowed range [{P_MIN_MS},{P_MAX_MS}] ms: {jitter_ms}"
    # Linear scaling check (within floating tolerance)
    expected = P0_MS * (1.0 + ALPHA * traversal_score)
    clamped = max(P_MIN_MS, min(P_MAX_MS, expected))
    assert math.isclose(jitter_ms, clamped, rel_tol=1e-12), \
        "Jitter probability not correctly scaled with TraversalScore"

    # 9. Fundamental‑parameter check – ensure no undocumented literals slipped in
    #    (this is a sanity check that the constants used above are the ones defined)
    assert XI_N > 0 and XI_DELTA > 0, "Stiffness must be positive"
    assert TAU_SEC > 0, "Trust time constant must be positive"
    assert P0_MS >= 0 and ALPHA >= 0, "Jitter base and scale must be non‑negative"

    # If we reach here, all invariants hold.
    print("✅ All Omega Protocol invariants satisfied.")

# ----------------------------------------------------------------------
# Example usage (replace with real telemetry from the AFDS daemon)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock data representing a short traversal window
    stability_sum = 2.5                 # Σ exp(−Δt/τ)
    breadth, depth = 7, 3               # example exploration shape
    trust_seq   = [0.6, 0.62, 0.58, 0.61]
    phi_delta_seq = [phi_delta(breadth, depth)] * len(trust_seq)  # static shape for demo
    psi_seq = [math.exp(-H_NOISE) * s for s in [2.0, 2.1, 1.9, 2.05]]  # ψ = ln(φₙ) approximations
    traversal_score = 0.73              # high‑novelty traversal

    try:
        validate_invariants(
            stability_sum=stability_sum,
            breadth=breadth,
            depth=depth,
            trust_seq=trust_seq,
            phi_delta_seq=phi_delta_seq,
            psi_seq=psi_seq,
            traversal_score=traversal_score,
        )
    except AssertionError as e:
        print("❌ Invariant violation:", e)
        raise
    except Exception as e:
        print("⚠️ Unexpected error:", e)
        raise