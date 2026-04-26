# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol – AFDS v3.0 Mathematical Validation
-------------------------------------------------
This script independently reproduces the core mathematical formulas used in the
C++ prototype and asserts that they satisfy the specifications:

1. Trust decay – continuous 5 % per hour exponential decay.
2. Trust mitigation – 80 % reduction when trust = 1.0.
3. TraversalScore – 0.6·|unique_paths| + 0.4·max_depth.
4. Jitter probability – p = (raw_score/100)^1.5 · (1‑mitigation), clamped [0,1].
5. Jitter latency – uniform integer in [1, 50] ms when triggered.
6. Benchmark slowdown ratio – (AFDS_time)/(baseline_time).

If any assertion fails, the script raises an AssertionError with a descriptive
message, signalling a violation of the Omega Protocol invariants.
"""

import math
import random
import time
from typing import Tuple

# ----------------------------------------------------------------------
# 1. Trust Model helpers (mirroring the C++ implementation)
# ----------------------------------------------------------------------
def continuous_decay(initial: float, hours: float) -> float:
    """
    Exact continuous decay for a 5 % per hour loss:
        score(t) = score0 * exp(-ln(0.95) * t)
    """
    return initial * math.exp(-math.log(0.95) * hours)

def update_trust(
    trust: float,
    is_novel: bool,
    hours_since_last: float,
    stability_reward: float = 0.01,
    novelty_penalty: float = 0.05,
) -> float:
    """
    Replicates the logic inside TrustManager::UpdateTrust:
        1. Apply continuous decay.
        2. Add stability_reward if not novel.
        3. Subtract novelty_penalty if novel.
        4. Clamp to [0,1].
    """
    # 1. decay
    trust = trust * math.exp(-math.log(0.95) * hours_since_last)

    # 2. reward
    if not is_novel:
        trust += stability_reward

    # 3. penalty
    if is_novel:
        trust -= novelty_penalty

    # 4. clamp
    return max(0.0, min(1.0, trust))

def trust_mitigation(trust: float) -> float:
    """
    Mitigation factor returned by TrustManager::GetTrustMitigation:
        mitigation = 0.8 * trust   (i.e., up to 80 % reduction)
    """
    return 0.8 * trust

# ----------------------------------------------------------------------
# 2. Topology & TraversalScore
# ----------------------------------------------------------------------
def traversal_score(unique_paths: int, max_depth: int) -> float:
    """
    CalculateTraversalScore:
        score = 0.6 * unique_paths + 0.4 * max_depth
    """
    return 0.6 * unique_paths + 0.4 * max_depth

# ----------------------------------------------------------------------
# 3. Jitter Probability & Latency
# ----------------------------------------------------------------------
def jitter_probability(raw_score: float, mitigation: float) -> float:
    """
    Implements the probability calculation from ApplyAdaptiveJitter:
        p = (raw_score/100)^1.5 * (1 - mitigation)
    clamped to [0,1].
    """
    base = (raw_score / 100.0) ** 1.5
    p = base * (1.0 - mitigation)
    return max(0.0, min(1.0, p))

def apply_jitter(raw_score: float, mitigation: float, rng: random.Random) -> int:
    """
    Returns the jitter latency in milliseconds (0 if no jitter injected).
    Mirrors the logic in ApplyAdaptiveJitter:
        - draw uniform [0,1)
        - if < probability → sleep 1..50 ms (uniform integer)
    """
    prob = jitter_probability(raw_score, mitigation)
    if rng.random() < prob:
        # uniform integer in [1,50]
        return rng.randint(1, 50)
    return 0

# ----------------------------------------------------------------------
# 4. Benchmark helpers
# ----------------------------------------------------------------------
def benchmark_slowdown(baseline_us: float, afds_us: float) -> float:
    """
    Computes the slowdown ratio used in BenchmarkSuite::RunExperiments:
        slowdown = afds_time / baseline_time
    """
    if baseline_us == 0:
        raise ZeroDivisionError("Baseline time must be >0")
    return afds_us / baseline_us

# ----------------------------------------------------------------------
# 5. Property‑based validation
# ----------------------------------------------------------------------
def run_validation() -> None:
    rng = random.Random(42)   # deterministic for CI

    # ---- Trust decay ----------------------------------------------------
    # After 1 hour, trust should be exactly 0.95 of the original.
    assert math.isclose(continuous_decay(1.0, 1.0), 0.95, rel_tol=1e-12)
    # After 2 hours, trust = 0.95^2
    assert math.isclose(continuous_decay(1.0, 2.0), 0.95 ** 2, rel_tol=1e-12)
    # Decay is monotonic
    for h in [0, 0.5, 1, 2, 4, 8]:
        assert continuous_decay(1.0, h) >= continuous_decay(1.0, h + 0.1)

    # ---- Trust update (reward/penalty) ----------------------------------
    # Start neutral, no time elapsed, non‑novel → reward only
    t = update_trust(0.5, False, 0.0)
    assert math.isclose(t, 0.5 + 0.01, abs_tol=1e-12)
    # Novel access → penalty only
    t = update_trust(0.5, True, 0.0)
    assert math.isclose(t, 0.5 - 0.05, abs_tol=1e-12)
    # Combined decay + reward + penalty, clamped
    t = update_trust(0.2, True, 1.0)   # decay to 0.2*0.95 = 0.19, then -0.05
    assert math.isclose(t, max(0.0, 0.19 - 0.05), abs_tol=1e-12)
    t = update_trust(0.9, False, 1.0)  # decay to 0.9*0.95=0.855, +0.01
    assert math.isclose(t, min(1.0, 0.855 + 0.01), abs_tol=1e-12)

    # ---- Mitigation ------------------------------------------------------
    assert trust_mitigation(0.0) == 0.0
    assert trust_mitification(1.0) == 0.8
    assert trust_mitification(0.5) == 0.4

    # ---- TraversalScore --------------------------------------------------
    assert traversal_score(0, 0) == 0.0
    assert traversal_score(10, 0) == 6.0      # 0.6*10
    assert traversal_score(0, 10) == 4.0      # 0.4*10
    assert traversal_score(5, 5) == 5.0       # 0.6*5 + 0.4*5

    # ---- Jitter probability -----------------------------------------------
    # No mitigation, low score → low probability
    assert jitter_probability(10.0, 0.0) < 0.001
    # No mitigation, max score (100) → probability = 1^1.5 = 1
    assert math.isclose(jitter_probability(100.0, 0.0), 1.0, rel_tol=1e-12)
    # Full mitigation → probability zero regardless of score
    assert jitter_probability(100.0, 1.0) == 0.0
    # Mid values
    p = jitter_probability(50.0, 0.5)
    expected = ((50.0/100.0)**1.5) * 0.5
    assert math.isclose(p, expected, rel_tol=1e-12)

    # ---- Jitter latency (sampling test) ----------------------------------
    # When probability is 0, latency must be 0
    assert apply_jitter(0.0, 0.0, rng) == 0
    assert apply_jitter(100.0, 1.0, rng) == 0
    # When probability is 1, latency must be in [1,50]
    for _ in range(1000):
        lat = apply_jitter(100.0, 0.0, rng)
        assert 1 <= lat <= 50

    # ---- Benchmark slowdown sanity check ----------------------------------
    # If AFDS adds no overhead, slowdown ≈ 1
    assert math.isclose(benchmark_slowdown(1000.0, 1000.0), 1.0, rel_tol=1e-9)
    # If AFDS doubles the time, slowdown = 2
    assert math.isclose(benchmark_slowdown(1000.0, 2000.0), 2.0, rel_tol=1e-9)
    # Extreme slowdown >5 (i.e., >500 %)
    assert benchmark_slowdown(1000.0, 6000.0) > 5.0

    print("✅ All Omega Protocol mathematical invariants hold.")

if __name__ == "__main__":
    run_validation()