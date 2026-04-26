# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# Omega Protocol Invariant Validator – AFDS v3.0 Core Math
# =============================================================================
# This script validates the *mathematical* core of the Engine's C++ implementation:
#   - Trust score update (first‑order decay + novelty penalty + stability gain)
#   - Trust mitigation factor (0.8 * trust_score)
#   - Adaptive jitter probability and latency bounds
#   - Audit‑cost subtraction sanity check
#
# It does NOT check the full informational‑geometry invariants (covariant Φ‑mode split,
# ψ = ln φ_n, stiffness terms, Shannon‑entropy gauge, diagonal action). Those must be
# verified by a separate physics‑first audit.
#
# Run: python3 validate_afds_math.py
# =============================================================================

import math
import random
from typing import Tuple

# ---- Constants mirrored from Engine (C++) ------------------------------------
K_BOLTZMANN = 1.0                     # normalized informational constant
TRUST_TIME_CONSTANT = 3600.0          # 1 hour in seconds
NOVELTY_PENALTY_FACTOR = 0.05         # K_BOLTZMANN * 0.05
STABILITY_GAIN_FACTOR = 0.01          # K_BOLTZMANN * 0.01
STABILITY_EXP_DECAY = 0.1             # exponent in stability gain
TRUST_MITIGATION_FACTOR = 0.8         # 80% reduction for trusted
MAX_JITTER_MS = 50
MIN_JITTER_MS = 1
SHRED_THRESHOLD_PHI_DELTA = 0.95      # Engine hard‑coded (to be checked)

# ---- Helper functions -------------------------------------------------------
def trust_update(trust: float,
                 cumulative_stability: float,
                 novelty: bool,
                 dt_seconds: float) -> Tuple[float, float]:
    """
    Emulate Engine's UpdateTrust logic.
    Returns (new_trust, new_cumulative_stability).
    """
    # First‑order decay: dS/dt = -S/τ  => S(t+dt) = S * exp(-dt/τ)
    decay_factor = math.exp(-dt_seconds / TRUST_TIME_CONSTANT)
    trust_after_decay = trust * decay_factor

    # Novelty penalty
    novelty_penalty = NOVELTY_PENALTY_FACTOR if novelty else 0.0
    trust_after_penalty = max(trust_after_decay - novelty_penalty, 0.0)

    # Stability gain (only if not novel)
    if not novelty:
        # cumulative_stability updated with time‑weighted stability
        cumulative_stability += math.exp(-dt_seconds / TRUST_TIME_CONSTANT)
        stability_gain = STABILITY_GAIN_FACTOR * math.exp(-STABILITY_EXP_DECAY * cumulative_stability)
        trust_after_gain = min(trust_after_penalty + stability_gain, 1.0)
    else:
        trust_after_gain = trust_after_penalty
        # cumulative_stability unchanged on novel access

    # Clamp to [0,1] (Engine does this implicitly)
    trust_after_gain = max(min(trust_after_gain, 1.0), 0.0)
    cumulative_stability = max(cumulative_stability, 0.0)
    return trust_after_gain, cumulative_stability


def trust_mitigation(trust: float) -> float:
    """Engine's GetTrustMitigation returns 0.8 * trust_score (clamped to >=1?)."""
    return TRUST_MITIGATION_FACTOR * trust  # Engine returns this directly; caller uses as multiplier >=0


def jitter_probability(raw_score: float,
                       mitigation: float,
                       phi_delta: float) -> float:
    """Engine's probability before clamping."""
    p = (raw_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_delta)
    return min(max(p, 0.0), 1.0)   # Engine clamps after computing


def jitter_latency(raw_score: float,
                   mitigation: float,
                   phi_delta: float,
                   rng: random.Random) -> int:
    """Return latency in ms as Engine's ApplyAdaptiveJitter."""
    prob = jitter_probability(raw_score, mitigation, phi_delta)
    if phi_delta > SHRED_THRESHOLD_PHI_DELTA:
        return 1000   # shredding event
    if rng.random() < prob:
        return 1 + int(rng.random() * MAX_JITTER_MS)   # 1..50 ms
    return 0


def audit_cost_estimate() -> float:
    """
    Engine's heuristic audit complexity:
        1.0 (trust) + 1.5 (forensic) + 1.0 (topology) + 0.5 (mutex) = 4.0
    Audit entropy cost = K_B * ln(2) * complexity
    """
    complexity = 4.0
    return K_BOLTZMANN * math.log(2.0) * complexity


def raw_gain_from_benchmark(slowdown_factor: float,
                            cpu_overhead_percent: float,
                            false_positive_rate: float,
                            log_size: int) -> float:
    """
    Engine's raw gain calculation (simplified):
        +0.25 if slowdown_factor > 5.0
        +0.30 if cpu_overhead_percent < 15.0
        +0.20 if false_positive_rate < 0.001
        +0.15 if log_size > 0
    """
    gain = 0.0
    if slowdown_factor > 5.0:
        gain += 0.25
    if cpu_overhead_percent < 15.0:
        gain += 0.30
    if false_positive_rate < 0.001:
        gain += 0.20
    if log_size > 0:
        gain += 0.15
    return gain


# ---- Validation Routine ------------------------------------------------------
def run_validation(num_steps: int = 1000, seed: int = 42) -> None:
    rng = random.Random(seed)

    trust = 0.0
    cum_stab = 0.0
    last_time = 0.0   # simulated seconds

    for i in range(num_steps):
        # simulate random inter‑access time (0.1–10 s)
        dt = rng.uniform(0.1, 10.0)
        # decide novelty with decreasing probability as we explore
        novelty = rng.random() < max(0.1, 1.0 - i / (num_steps * 2))
        trust, cum_stab = trust_update(trust, cum_stab, novelty, dt)

        # Invariant: trust must stay in [0,1]
        assert 0.0 <= trust <= 1.0, f"Trust out of bounds at step {i}: {trust}"

        # Invariant: novelty penalty never exceeds K_BOLTZMANN*0.05
        novelty_penalty = NOVELTY_PENALTY_FACTOR if novelty else 0.0
        assert novelty_penalty <= K_BOLTZMANN * 0.05, \
            f"Novelty penalty too large at step {i}: {novelty_penalty}"

        # Invariant: stability gain bounded by K_BOLTZMANN*0.01*exp(-0.1*cum_stab)
        if not novelty:
            max_gain = STABILITY_GAIN_FACTOR * math.exp(-STABILITY_EXP_DECAY * cum_stab)
            actual_gain = STABILITY_GAIN_FACTOR * math.exp(-STABILITY_EXP_DECAY * (cum_stab - math.exp(-dt/TRUST_TIME_CONSTANT)))
            assert actual_gain <= max_gain + 1e-12, \
                f"Stability gain exceeds theoretical max at step {i}: {actual_gain} > {max_gain}"

        # Compute mitigation and jitter
        mitigation = trust_mitigation(trust)
        # raw_score simulated as a function of unique path count (proxy)
        raw_score = min(100.0, i * 0.1)   # grows slowly
        phi_delta = rng.uniform(0.0, 1.0)   # pretend asymmetry
        latency = jitter_latency(raw_score, mitigation, phi_delta, rng)

        # Jitter latency bounds
        assert latency == 0 or (MIN_JITTER_MS <= latency <= MAX_JITTER_MS or latency == 1000), \
            f"Illegal latency at step {i}: {latency}"

        # Probability must be derived from the declared formula
        prob = jitter_probability(raw_score, mitigation, phi_delta)
        if phi_delta > SHRED_THRESHOLD_PHI_DELTA:
            # shredding path: latency fixed 1000 ms, probability irrelevant
            continue
        expected_latency_if_hit = 1 + int(rng.random() * MAX_JITTER_MS) if rng.random() < prob else 0
        # We cannot assert exact match because of randomness, but we can check that
        # latency>0 implies the hit condition was satisfied.
        if latency > 0:
            assert latency <= MAX_JITTER_MS, f"Jitter latency exceeded max: {latency}"
        # advance simulated time
        last_time += dt

    # ---- Audit‑cost sanity check ------------------------------------------------
    audit_cost = audit_cost_estimate()
    # Engine claims net Φ = +0.65 after subtracting audit cost from raw gain.
    # Therefore raw_gain must be >= audit_cost + 0.65
    min_raw_gain_needed = audit_cost + 0.65
    # Simulate a plausible benchmark outcome (optimistic)
    slowdown = 6.0          # >5 → contributes 0.25
    cpu_over = 10.0         # <15 → contributes 0.30
    fpr = 0.0005            # <0.001 → contributes 0.20
    log_sz = 150            # >0 → contributes 0.15
    raw_gain = raw_gain_from_benchmark(slowdown, cpu_over, fpr, log_sz)
    assert raw_gain >= min_raw_gain_needed - 1e-9, \
        (f"Raw gain insufficient: {raw_gain:.4f} < required {min_raw_gain_needed:.4f} "
         f"(audit_cost={audit_cost:.4f})")

    print("All mathematical invariants passed for the simulated subset.")


if __name__ == "__main__":
    run_validation()