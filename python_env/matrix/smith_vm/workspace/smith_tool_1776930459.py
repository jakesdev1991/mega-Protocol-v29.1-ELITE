# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFDS v3.0 Mathematical Validation Harness
-----------------------------------------
Checks the core trust‑model, jitter coupling, and forensic‑logging formulas
against the invariants stated in the Omega Protocol specification.
"""

import math
import random
from typing import Tuple

# ----------------------------------------------------------------------
# Helper functions that mirror the C++ logic (fixed‑point where needed)
# ----------------------------------------------------------------------
def update_trust(
    trust: float,
    is_novel: bool,
    elapsed_hours: float,
) -> Tuple[float, float, float]:
    """
    Apply novelty penalty, hourly decay, and stability reward.
    Returns (new_trust, penalty_applied, reward_applied).
    """
    # 1) Novelty penalty
    penalty = 0.05 if is_novel else 0.0
    trust_after_penalty = max(0.0, min(1.0, trust - penalty))

    # 2) Hourly decay (continuous)
    decay_factor = 0.95 ** elapsed_hours   # 5% per hour
    trust_after_decay = trust_after_penalty * decay_factor

    # 3) Stability reward (only for non‑novel accesses)
    reward = 0.01 if not is_novel else 0.0
    new_trust = max(0.0, min(1.0, trust_after_decay + reward))

    return new_trust, penalty, reward


def trust_mitigation(trust: float) -> float:
    """Mitigation factor used by the jitter subsystem."""
    return 0.8 * trust   # yields [0, 0.8]


def jitter_probability(raw_score: float, mitigation: float) -> float:
    """
    Probability of injecting jitter.
    Formula from Engine: p = min(1, (raw/100)^1.5) * (1 - mitigation)
    """
    base = (raw_score / 100.0) ** 1.5
    base = min(1.0, base)          # clamp to [0,1]
    prob = base * (1.0 - mitigation)
    return max(0.0, min(1.0, prob))


def apply_jitter(raw_score: float, mitigation: float, rng: random.Random) -> int:
    """
    Return jitter latency in ms (0 if no jitter).
    Latency range: 1‑50 ms inclusive.
    """
    prob = jitter_probability(raw_score, mitigation)
    if rng.random() < prob:
        # uniform real in [0,1) → map to [1,50]
        jitter_ms = 1 + int(49.0 * rng.random())
        # Ensure we never exceed 50 due to rounding edge‑case
        return min(50, jitter_ms)
    return 0


# ----------------------------------------------------------------------
# Validation suite
# ----------------------------------------------------------------------
def test_trust_bounds():
    """Trust must stay in [0,1] under all combinations."""
    rng = random.Random(42)
    for trust in [0.0, 0.2, 0.5, 0.8, 1.0]:
        for is_novel in (True, False):
            for hrs in [0.0, 0.5, 1.0, 2.5, 12.0]:
                new_trust, _, _ = update_trust(trust, is_novel, hrs)
                assert 0.0 <= new_trust <= 1.0, (
                    f"Trust out of bounds: {trust} -> {new_trust}"
                )
    print("✓ Trust bounds invariant holds.")


def test_mitigation_range():
    """Mitigation = 0.8 * trust must be in [0,0.8]."""
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        m = trust_mitigation(t)
        assert 0.0 <= m <= 0.8, f"Mitigation out of range: {m}"
    print("✓ Mitigation range invariant holds.")


def test_jitter_probability_bounds():
    """Probability must stay in [0,1] for any raw score and mitigation."""
    for raw in [0.0, 10.0, 50.0, 100.0, 200.0, 500.0]:
        for mit in [0.0, 0.2, 0.5, 0.8]:
            p = jitter_probability(raw, mit)
            assert 0.0 <= p <= 1.0, f"Jitter prob OOB: raw={raw}, mit={mit}, p={p}"
    print("✓ Jitter probability bounds invariant holds.")


def test_jitter_latency_range():
    """When jitter fires, latency must be 1‑50 ms."""
    rng = random.Random(12345)
    for _ in range(10_000):
        raw = rng.uniform(0, 300)
        mit = rng.uniform(0, 0.8)
        lat = apply_jitter(raw, mit, rng)
        if lat != 0:
            assert 1 <= lat <= 50, f"Jitter latency out of range: {lat} ms"
    print("✓ Jitter latency range invariant holds.")


def test_novelty_and_reward_logic():
    """Check that penalty/reward are applied exactly as specified."""
    # Novel access → penalty 0.05, reward 0
    t, pen, rew = update_trust(0.5, is_novel=True, elapsed_hours=0.0)
    assert math.isclose(pen, 0.05, rel_tol=1e-9)
    assert math.isclose(rew, 0.0, rel_tol=1e-9)
    assert math.isclose(t, 0.45, rel_tol=1e-9)   # 0.5 - 0.05

    # Non‑novel access → penalty 0, reward 0.01
    t, pen, rew = update_trust(0.5, is_novel=False, elapsed_hours=0.0)
    assert math.isclose(pen, 0.0, rel_tol=1e-9)
    assert math.isclose(rew, 0.01, rel_tol=1e-9)
    assert math.isclose(t, 0.51, rel_tol=1e-9)   # 0.5 + 0.01

    print("✓ Novelty / reward logic invariant holds.")


def test_hourly_decay():
    """Decay must follow 5% per hour continuously."""
    trust_initial = 1.0
    # After 1 hour: 1.0 * 0.95
    t1, _, _ = update_trust(trust_initial, is_novel=False, elapsed_hours=1.0)
    assert math.isclose(t1, 0.95, rel_tol=1e-9)

    # After 2 hours: 1.0 * 0.95^2
    t2, _, _ = update_trust(trust_initial, is_novel=False, elapsed_hours=2.0)
    assert math.isclose(t2, 0.9025, rel_tol=1e-9)

    # Fractional hour: 0.5h → sqrt(0.95)
    t_half, _, _ = update_trust(trust_initial, is_novel=False, elapsed_hours=0.5)
    assert math.isclose(t_half, math.sqrt(0.95), rel_tol=1e-9)

    print("✓ Hourly decay invariant holds.")


def run_all_tests():
    test_trust_bounds()
    test_mitigation_range()
    test_jitter_probability_bounds()
    test_jitter_latency_range()
    test_novelty_and_reward_logic()
    test_hourly_decay()
    print("\nAll mathematical invariants validated ✅")


if __name__ == "__main__":
    run_all_tests()