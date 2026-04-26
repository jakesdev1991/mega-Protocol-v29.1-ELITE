# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith – Omega Protocol Invariant Validator
# This script checks the mathematical soundness of the AFDS v3.0 design
# against the stated Omega Protocol invariants (Phi_N, Phi_Delta, J*).
# Any deviation is reported as a violation.

import math
import random
from typing import Tuple

# ----------------------------------------------------------------------
# Fundamental constants (as defined in the C++ code)
# ----------------------------------------------------------------------
K_BOLTZMANN = 1.0                     # Normalized informational constant
TRUST_TIME_CONSTANT = 3600.0          # 1 hour in seconds
XI_N = 0.8                            # Trust stiffness
XI_DELTA = 1.2                        # Deformation stiffness

# ----------------------------------------------------------------------
# Helper functions that mirror the C++ logic (simplified for validation)
# ----------------------------------------------------------------------
def update_trust(trust_score: float,
                 is_novel: bool,
                 cumulative_stability: float,
                 normalized_time: float) -> Tuple[float, float]:
    """Return (new_trust_score, new_cumulative_stability) per TrustManager.UpdateTrust."""
    novelty_penalty = K_BOLTZMANN * 0.05 if is_novel else 0.0
    # First‑order decay invariant
    trust_score *= math.exp(-normalized_time)
    trust_score = max(0.0, min(1.0, trust_score - novelty_penalty))

    if not is_novel:
        # Stability integral approximation
        cumulative_stability += math.exp(-normalized_time)
        stability_gain = K_BOLTZMANN * 0.01 * math.exp(-0.1 * cumulative_stability)
        trust_score += stability_gain
        trust_score = max(0.0, min(1.0, trust_score))
    return trust_score, cumulative_stability

def trust_mitigation(trust_score: float) -> float:
    """80% reduction when trust == 1.0."""
    return 0.8 * trust_score

def adaptive_jitter_probability(raw_score: float,
                                mitigation: float,
                                phi_delta: float) -> float:
    """Probability of jitter injection (should be in [0,1])."""
    prob = (raw_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_delta)
    return max(0.0, min(1.0, prob))

def apply_adaptive_jitter(raw_score: float,
                          mitigation: float,
                          phi_delta: float) -> int:
    """Return latency in ms (0 means no jitter)."""
    if phi_delta > 0.95:          # shredding event boundary condition
        return 1000
    prob = adaptive_jitter_probability(raw_score, mitigation, phi_delta)
    return (1 + int(50.0 * random.random())) if random.random() < prob else 0

def asymmetric_threat(breadth: int, depth: int) -> float:
    """Phi_Delta = |breadth - depth| / (breadth + depth)  ∈ [0,1]."""
    if breadth + depth == 0:
        return 0.0
    return abs(breadth - depth) / (breadth + depth)

def security_manifold_curvature(phi_N: float,
                                phi_delta: float,
                                h_imp: float) -> float:
    """XI_N * phi_N + XI_DELTA * phi_Delta - h_imp."""
    return XI_N * phi_N + XI_DELTA * phi_delta - h_imp

def phi_density_from_benchmark(slowdown_factor: float,
                               cpu_overhead_percent: float,
                               false_positive_rate: float,
                               log_size: int) -> float:
    """Compute raw gain, subtract audit entropy cost, return net Phi density."""
    # Raw gain contributions (as per the code)
    raw_gain = 0.0
    if slowdown_factor > 5.0:          # >500% slowdown target
        raw_gain += 0.25
    if cpu_overhead_percent < 15.0:    # Reasonable overhead
        raw_gain += 0.30
    if false_positive_rate < 0.001:    # <0.1% FPR target
        raw_gain += 0.20
    if log_size > 0:
        raw_gain += 0.15

    # Audit complexity (hard‑coded in the implementation)
    audit_complexity = 1.0 + 1.5 + 1.0 + 0.5   # = 4.0
    audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity

    return raw_gain - audit_entropy_cost

# ----------------------------------------------------------------------
# Validation Routine
# ----------------------------------------------------------------------
def run_validation() -> None:
    violations = []

    # 1. Trust score bounds and invariants
    ts, cs = 0.5, 0.0
    for i in range(10):
        ts, cs = update_trust(ts,
                              is_novel=(i % 3 == 0),   # occasional novelty
                              cumulative_stability=cs,
                              normalized_time=0.1)     # 0.1 * TRUST_TIME_CONSTANT sec
        if not (0.0 <= ts <= 1.0):
            violations.append(f"Trust score out of bounds: {ts}")
    # Mitigation check
    if abs(trust_mitigation(1.0) - 0.8) > 1e-9:
        violations.append(f"Trust mitigation for trust=1.0 should be 0.8, got {trust_mitigation(1.0)}")

    # 2. Jitter probability bounds
    for raw in [0, 25, 50, 75, 100]:
        for mit in [0.0, 0.4, 0.8, 1.0]:
            for phi in [0.0, 0.3, 0.6, 0.9]:
                prob = adaptive_jitter_probability(raw, mit, phi)
                if not (0.0 <= prob <= 1.0):
                    violations.append(f"Jitter probability out of bounds: raw={raw}, mit={mit}, phi={phi} => {prob}")

    # 3. Asymmetric threat (Phi_Delta) bounds
    for b in range(0, 6):
        for d in range(0, 6):
            phi = asymmetric_threat(b, d)
            if not (0.0 <= phi <= 1.0):
                violations.append(f"Asymmetric threat out of bounds: breadth={b}, depth={d} => {phi}")

    # 4. Security manifold curvature uses correct constants
    # (just a sanity check that the formula matches the definition)
    test_curv = security_manifold_curvature(0.5, 0.3, 0.2)
    expected = XI_N * 0.5 + XI_DELTA * 0.3 - 0.2
    if abs(test_curv - expected) > 1e-9:
        violations.append(f"Curvature formula mismatch: got {test_curv}, expected {expected}")

    # 5. Phi density calculation – compare to claimed net +0.65Φ
    # Use benchmark numbers that would satisfy the design goals:
    #   slowdown_factor = 6.0   (>5 => +0.25)
    #   cpu_overhead    = 10.0  (<15 => +0.30)
    #   false_positive  = 0.0005 (<0.001 => +0.20)
    #   log_size        = 1     (>0 => +0.15)
    net_phi = phi_density_from_benchmark(
        slowdown_factor=6.0,
        cpu_overhead_percent=10.0,
        false_positive_rate=0.0005,
        log_size=1
    )
    claimed = 0.65
    if abs(net_phi - claimed) > 1e-3:
        violations.append(
            f"Phi density mismatch: computed {net_phi:.5f}, claimed {claimed:.5f} "
            f"(raw_gain={0.25+0.30+0.20+0.15:.2f}, audit_cost={math.log(2)*4:.5f})"
        )

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    if violations:
        print("Ω-PROTOCOL VIOLATIONS DETECTED:")
        for v in violations:
            print(f" - {v}")
        print("\nVALIDATION FAILED – design must be revised.")
    else:
        print("ALL INVARIANT CHECKS PASSED.")
        print(f"Net Φ‑density (based on benchmark) = {net_phi:.5f}")

if __name__ == "__main__":
    run_validation()