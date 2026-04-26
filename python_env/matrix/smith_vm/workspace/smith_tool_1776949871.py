# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for AFDS v3.0 Core Mathematics
----------------------------------------------------------------
This script checks the internal consistency of the formulas used in the
Engine's pleading output (trust decay, mitigation, jitter probability,
traversal score, and benchmark calculations).  It does **not** assess
the higher‑level Omega Physics invariants (covariant modes, entropy,
etc.) – those require a full manifold analysis and are left to the
Omega Physics Rubric v26.0.

If any assertion fails, the script raises an AssertionError with a
descriptive message, indicating a mathematical or logical violation.
"""

import math
import random
from typing import Tuple

# ----------------------------------------------------------------------
# 1. Trust Model Mathematics
# ----------------------------------------------------------------------
def trust_decay_factor(hours: float) -> float:
    """
    Continuous 5% per hour decay.
    After 1 hour: factor = 0.95
    """
    return math.exp(-math.log(0.95) * hours)   # = 0.95 ** hours

def update_trust(
    trust: float,
    is_novel: bool,
    hours_since_last: float,
    stability_reward: float = 0.01,
    novelty_penalty: float = 0.05,
) -> float:
    """
    Mimics the Engine's UpdateTrust logic:
        trust *= decay
        if not novel: trust += stability_reward
        trust -= novelty_penalty if novel else 0.0
        clamp to [0,1]
    """
    trust *= trust_decay_factor(hours_since_last)
    if not is_novel:
        trust += stability_reward
    if is_novel:
        trust -= novelty_penalty
    return max(0.0, min(1.0, trust))

def trust_mitigation(trust: float) -> float:
    """
    Engine returns 0.8 * trust (80% mitigation when trust=1).
    """
    return 0.8 * trust

# ----------------------------------------------------------------------
# 2. Jitter Mathematics
# ----------------------------------------------------------------------
def jitter_probability(raw_score: float, mitigation: float) -> float:
    """
    Engine: probability = (raw_score/100)^1.5 * (1 - mitigation)
    Clamped to [0,1].
    """
    base = (raw_score / 100.0) ** 1.5
    prob = base * (1.0 - mitigation)
    return max(0.0, min(1.0, prob))

def apply_jitter(probability: float) -> int:
    """
    Engine: if rand < probability: jitter_ms = 1 + int(50 * rand)
    Returns jitter in ms (0 if no jitter).
    """
    if random.random() < probability:
        jitter = 1 + int(50.0 * random.random())   # 1..50 inclusive
        return jitter
    return 0

# ----------------------------------------------------------------------
# 3. Topology / Traversal Score
# ----------------------------------------------------------------------
def traversal_score(unique_paths: int, max_depth: int) -> float:
    """
    Engine: score = unique_paths*0.6 + max_depth*0.4
    """
    return unique_paths * 0.6 + max_depth * 0.4

# ----------------------------------------------------------------------
# 4. Benchmark Math (simplified)
# ----------------------------------------------------------------------
def benchmark_slowdown(baseline_us: float, afds_us: float) -> float:
    """
    Engine: slowdown = afds_time / baseline_time
    """
    if baseline_us == 0:
        raise ZeroDivisionError("Baseline time cannot be zero.")
    return afds_us / baseline_us

def false_positive_rate(false_pos: int, total: int) -> float:
    return false_pos / total if total else 0.0

# ----------------------------------------------------------------------
# Validation Suite
# ----------------------------------------------------------------------
def run_validation() -> None:
    random.seed(42)   # deterministic for CI

    # ---- Trust Decay ----
    assert math.isclose(trust_decay_factor(1.0), 0.95, rel_tol=1e-12), "Decay factor wrong for 1h"
    assert math.isclose(trust_decay_factor(2.0), 0.95**2, rel_tol=1e-12), "Decay factor wrong for 2h"
    assert math.isclose(trust_decay_factor(0.5), 0.95**0.5, rel_tol=1e-12), "Decay factor wrong for 0.5h"

    # ---- Trust Update Bounds ----
    for _ in range(1000):
        t = random.random() * 2.0          # trust in [0,2) to test clamping
        novel = random.choice([True, False])
        hrs = random.random() * 5.0        # 0‑5 hours
        new_t = update_trust(t, novel, hrs)
        assert 0.0 <= new_t <= 1.0, f"Trust out of bounds: {new_t}"
        # Mitigation must be in [0,0.8]
        mit = trust_mitigation(new_t)
        assert 0.0 <= mit <= 0.8, f"Mitigation out of bounds: {mit}"

    # ---- Jitter Probability Bounds ----
    for _ in range(1000):
        raw = random.uniform(0, 200)       # allow scores >100 to test clamping
        mit = random.uniform(0, 0.8)
        prob = jitter_probability(raw, mit)
        assert 0.0 <= prob <= 1.0, f"Jitter probability out of bounds: {prob}"
        # When mitigation=1 (trust=1) probability should be 0
        assert math.isclose(jitter_probability(raw, 0.8), 0.0, abs_tol=1e-12), \
            "Probability not zero at max mitigation"
        # When raw=0 probability should be 0
        assert math.isclose(jitter_probability(0.0, mit), 0.0, abs_tol=1e-12), \
            "Probability not zero at raw score 0"

    # ---- Jitter Application Range ----
    for _ in range(5000):
        prob = random.random()
        jit = apply_jitter(prob)
        if jit == 0:
            continue   # no jitter injected
        assert 1 <= jit <= 50, f"Jitter ms out of spec: {jit}"

    # ---- Traversal Score Non‑negative ----
    for _ in range(1000):
        up = random.randint(0, 1000)
        md = random.randint(0, 100)
        sc = traversal_score(up, md)
        assert sc >= 0.0, f"Negative traversal score: {sc}"
        # Upper bound sanity (not required by spec, but helpful)
        assert sc <= up * 0.6 + md * 0.4, "Traversal score formula mismatch"

    # ---- Benchmark Math ----
    base = 1000.0   # µs
    afds = 6000.0   # µs (6× slowdown)
    slow = benchmark_slowdown(base, afds)
    assert math.isclose(slow, 6.0, rel_tol=1e-12), "Slowdown calculation wrong"
    # Edge cases
    assert benchmark_slowdown(1.0, 1.0) == 1.0, "Identity slowdown failed"
    try:
        benchmark_slowdown(0.0, 1.0)
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        pass

    # ---- FPR Calculation ----
    assert false_positive_rate(0, 1000) == 0.0
    assert false_positive_rate(1, 1000) == 0.001
    assert false_positive_rate(500, 1000) == 0.5

    print("[Ω] All mathematical invariants validated successfully.")

if __name__ == "__main__":
    run_validation()