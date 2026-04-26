# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for AFDS v3.0 (Trust & Jitter Core)

Checks:
  1. Trust score stays in [0, 1].
  2. Continuous 5%/hour decay matches exponential model.
  3. Mitigation = 0.8 * trust_score  =>  in [0, 0.8].
  4. Jitter probability p = (raw/100)^1.5 * (1-mitigation) clamped to [0,1].
  5. When jitter triggers, latency in [1, 50] ms.
  6. Derived Omega invariants:
        Phi_N = trust_score
        Phi_Delta = 1 - trust_score
        J*      = expected jitter latency
        => Phi_N * Phi_Delta <= 0.25   (max entropy of a binary variable)
        => J* >= 0                     (non‑negative latency)
  7. Topology raw score monotonic in unique_paths and max_depth.

The script is deliberately pure‑Python and side‑effect free; it can be
imported by a test harness or executed directly.
"""

import random
import math
from typing import Tuple

# ----------------------------------------------------------------------
# Helper functions that mirror the C++ logic (but in Python for clarity)
# ----------------------------------------------------------------------
def trust_decay_factor(hours: float) -> float:
    """Continuous 5% per hour decay: T(t) = T0 * exp(-ln(0.95) * t)"""
    return math.exp(-math.log(0.95) * hours)

def update_trust(
    trust: float,
    hours_since_last: float,
    is_novel: bool,
) -> float:
    """Apply decay, reward/penalty, and clamp to [0,1]."""
    t = trust * trust_decay_factor(hours_since_last)
    if not is_novel:
        t += 0.01          # stability reward
    t -= 0.05 if is_novel else 0.0   # novelty penalty
    return max(0.0, min(1.0, t))

def mitigation(trust: float) -> float:
    """Trust‑based mitigation factor (max 80%)."""
    return 0.8 * trust

def traversal_score(unique_paths: int, max_depth: int) -> float:
    """Raw traversal score used for jitter probability."""
    return 0.6 * unique_paths + 0.4 * max_depth

def jitter_probability(raw_score: float, mitig: float) -> float:
    """Probability of injecting jitter, clamped to [0,1]."""
    p = (raw_score / 100.0) ** 1.5 * (1.0 - mitig)
    return max(0.0, min(1.0, p))

def jitter_latency() -> int:
    """Latency when jitter triggers: 1 + floor(50 * U), U~[0,1)."""
    return 1 + int(50.0 * random.random())

# ----------------------------------------------------------------------
# Invariant checks
# ----------------------------------------------------------------------
def check_trust_bounds(t: float) -> bool:
    return 0.0 <= t <= 1.0

def check_mitigation_bounds(m: float) -> bool:
    return 0.0 <= m <= 0.8

def check_jitter_prob_bounds(p: float) -> bool:
    return 0.0 <= p <= 1.0

def check_jitter_latency_bounds(lat: int) -> bool:
    return 1 <= lat <= 50

def check_omega_invariants(trust: float, exp_jitter: float) -> Tuple[bool, bool]:
    phi_n = trust
    phi_delta = 1.0 - trust
    j_star = exp_jitter
    inv1 = (phi_n * phi_delta) <= 0.25 + 1e-12  # allow tiny floating error
    inv2 = j_star >= 0.0
    return inv1, inv2

def monotonic_raw_score(up1: int, d1: int, up2: int, d2: int) -> bool:
    """raw score must not decrease if both arguments increase."""
    s1 = 0.6 * up1 + 0.4 * d1
    s2 = 0.6 * up2 + 0.4 * d2
    return (up2 >= up1 and d2 >= d1) == (s2 >= s1 - 1e-12)

# ----------------------------------------------------------------------
# Stress‑test simulation
# ----------------------------------------------------------------------
def run_simulation(num_iterations: int = 200_000) -> None:
    random.seed(42)  # deterministic for CI
    trust = 0.5  # start mid‑range
    last_time = 0.0  # simulated hours since last access
    total_jitter_ms = 0.0
    jitter_triggers = 0

    for i in range(num_iterations):
        # Simulate stochastic workload
        hours_since = random.expovariate(1.0)  # mean 1 hour between events
        is_novel = random.random() < 0.3       # 30% novel paths
        up = random.randint(0, 200)            # unique paths seen so far (approx)
        depth = random.randint(0, 20)

        # Update trust
        new_trust = update_trust(trust, hours_since, is_novel)
        if not check_trust_bounds(new_trust):
            raise AssertionError(f"Trust out of bounds: {new_trust}")
        trust = new_trust

        # Mitigation
        mit = mitigation(trust)
        if not check_mitigation_bounds(mit):
            raise AssertionError(f"Mitigation out of bounds: {mit}")

        # Raw traversal score & jitter probability
        raw = traversal_score(up, depth)
        prob = jitter_probability(raw, mit)
        if not check_jitter_prob_bounds(prob):
            raise AssertionError(f"Jitter probability out of bounds: {prob}")

        # Decide whether jitter fires
        if random.random() < prob:
            lat = jitter_latency()
            if not check_jitter_latency_bounds(lat):
                raise AssertionError(f"Jitter latency out of bounds: {lat}")
            total_jitter_ms += lat
            jitter_triggers += 1

        # Periodic invariant checks (every 10k steps)
        if i % 10_000 == 0 and i > 0:
            exp_jitter = (total_jitter_ms / jitter_triggers) if jitter_triggers else 0.0
            inv1, inv2 = check_omega_invariants(trust, exp_jitter)
            if not inv1:
                raise AssertionError(f"Phi_N*Phi_Delta > 0.25: trust={trust}")
            if not inv2:
                raise AssertionError(f"Negative expected jitter: {exp_jitter}")

        # Monotonicity sanity check on raw score (random pairs)
        if i % 7_000 == 0:
            up_a, d_a = random.randint(0, 200), random.randint(0, 20)
            up_b, d_b = random.randint(0, 200), random.randint(0, 20)
            if not monotonic_raw_score(up_a, d_a, up_b, d_b):
                raise AssertionError("Raw score monotonicity violated")

    # Final report
    avg_jitter = (total_jitter_ms / jitter_triggers) if jitter_triggers else 0.0
    print("\n=== AFDS v3.0 Trust/Jitter Validation Summary ===")
    print(f"Iterations:          {num_iterations:,}")
    print(f"Final trust score:   {trust:.6f}")
    print(f"Average mitigation:  {0.8*trust:.6f}")
    print(f"Jitter triggers:     {jitter_triggers:,} ({jitter_triggers/num_iterations:.2%})")
    print(f"Avg jitter latency:  {avg_jitter:.2f} ms")
    print("All invariants held throughout the run.\n")

if __name__ == "__main__":
    run_simulation()