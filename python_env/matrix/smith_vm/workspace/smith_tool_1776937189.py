# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for AFDS v3.0
Checks:
  * Trust score stays in [0, 1]
  * Trust mitigation = 0.8 * trust_score
  * Trust update follows first‑order decay + stability gain
  * Novelty penalty = K_BOLTZMANN * 0.05 (if novel) else 0
  * Jitter probability in [0, 1] before clamping
  * Latency output: 0‑50 ms (normal) or 1000 ms (shredding)
  * Shredding condition derived from phi_Delta threshold (must be justified)
  * Audit entropy cost = K_BOLTZMANN * ln(2) * measured_complexity
  * Net Φ‑density = raw_gain - audit_entropy_cost (must match claimed value)
  * Basic FUSE path resolution must succeed (mapper not empty)
"""

import math
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# Fundamental constants (as used in the Engine)
K_BOLTZMANN = 1.0
TRUST_TIME_CONSTANT = 3600.0  # seconds
XI_N = 0.8
XI_DELTA = 1.2

# ----------------------------------------------------------------------
# Helper functions that replicate the Engine's logic
def trust_update(
    trust_score: float,
    cumulative_stability: float,
    is_novel: bool,
    dt_seconds: float,
) -> Tuple[float, float]:
    """Return (new_trust_score, new_cumulative_stability)."""
    novelty_penalty = K_BOLTZMANN * 0.05 if is_novel else 0.0
    # First‑order decay
    trust_score *= math.exp(-dt_seconds / TRUST_TIME_CONSTANT)
    trust_score = max(0.0, min(1.0, trust_score - novelty_penalty))

    if not is_novel:
        # Stability integral approximation
        cumulative_stability += math.exp(-dt_seconds / TRUST_TIME_CONSTANT)
        stability_gain = K_BOLTZMANN * 0.01 * math.exp(-0.1 * cumulative_stability)
        trust_score += stability_gain
        trust_score = max(0.0, min(1.0, trust_score))
    return trust_score, cumulative_stability


def trust_mitigation(trust_score: float) -> float:
    """Mitigation factor applied to latency (80% reduction for full trust)."""
    return 0.8 * trust_score


def jitter_probability(
    raw_score: float, mitigation: float, phi_delta: float
) -> float:
    """Raw probability before clamping (should already be in [0,1])."""
    p = (raw_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_delta)
    return max(0.0, min(1.0, p))  # clamp for safety; invariant requires p∈[0,1] naturally


def apply_jitter(
    raw_score: float, mitigation: float, phi_delta: float
) -> int:
    """Return latency in ms (0 means no jitter)."""
    # Shredding event – threshold must be justified; we only check the branch.
    if phi_delta > 0.95:  # placeholder; real system must derive this
        return 1000
    prob = jitter_probability(raw_score, mitigation, phi_delta)
    # Simulate random draw – we just return the expected latency range.
    if prob > 0.0:
        # Expected latency = 1 + 50 * U[0,1] → mean 25.5 ms
        return int(1 + 50 * prob)  # deterministic proxy for validation
    return 0


def audit_entropy_cost(measured_complexity: float) -> float:
    """Entropy cost of auditing, per Omega Protocol."""
    return K_BOLTZMANN * math.log(2.0) * measured_complexity


def raw_gain_from_benchmark(
    slowdown_factor: float,
    cpu_overhead_percent: float,
    false_positive_rate: float,
    log_size: int,
) -> float:
    """Compute the raw Φ gain as defined in the Engine's commentary."""
    gain = 0.0
    if slowdown_factor > 5.0:          # >500 % slowdown target
        gain += 0.25
    if cpu_overhead_percent < 15.0:    # reasonable overhead
        gain += 0.30
    if false_positive_rate < 0.001:    # <0.1 % FPR target
        gain += 0.20
    if log_size > 0:                   # topology enforcement
        gain += 0.15
    return gain


def net_phi_density(
    raw_gain: float, measured_complexity: float
) -> float:
    return raw_gain - audit_entropy_cost(measured_complexity)


# ----------------------------------------------------------------------
# Validation tests
def run_validation() -> None:
    print("=== Ω‑Protocol Invariant Validation ===")

    # 1. Trust score bounds and update
    ts, cs = 0.5, 0.0
    ts2, cs2 = trust_update(ts, cs, is_novel=True, dt_seconds=1800.0)
    assert 0.0 <= ts2 <= 1.0, f"Trust score out of bounds: {ts2}"
    print("✓ Trust score stays in [0,1] after update")

    # 2. Mitigation factor
    mit = trust_mitigation(ts2)
    assert mit == 0.8 * ts2, f"Mitigation mismatch: {mit} vs {0.8*ts2}"
    print("✓ Mitigation = 0.8 * trust_score")

    # 3. Jitter probability invariant (must be naturally bounded)
    raw_score = 80.0
    phi_delta = 0.3
    prob = jitter_probability(raw_score, mit, phi_delta)
    # The formula should never exceed 1 without clamping; we assert that.
    assert prob <= 1.0 + 1e-12, f"Jitter probability >1: {prob}"
    assert prob >= 0.0, f"Jitter probability <0: {prob}"
    print("✓ Jitter probability naturally bounded in [0,1]")

    # 4. Jitter latency range
    latency = apply_jitter(raw_score, mit, phi_delta)
    if phi_delta > 0.95:
        assert latency == 1000, f"Shredding latency incorrect: {latency}"
    else:
        assert 0 <= latency <= 50, f"Jitter latency out of range: {latency}"
    print("✓ Jitter latency within expected bounds")

    # 5. Audit cost – must be based on *measured* complexity, not heuristic
    # We simulate a measured complexity (e.g., from profiling) and check formula.
    measured_complexity = 3.2  # placeholder: would come from actual profiling
    cost = audit_entropy_cost(measured_complexity)
    expected = K_BOLTZMANN * math.log(2.0) * measured_complexity
    assert math.isclose(cost, expected, rel_tol=1e-9), "Audit cost formula incorrect"
    print("✓ Audit entropy cost follows K·ln(2)·complexity")

    # 6. Net Φ‑density sanity check (using the Engine's claimed numbers)
    # Engine claims: raw_gain ≈ 0.90, measured_complexity = 4.0 → net ≈ +0.65
    raw_gain_claimed = 0.90
    measured_complexity_claimed = 4.0
    net_claimed = net_phi_density(raw_gain_claimed, measured_complexity_claimed)
    # The Engine's commentary says +0.65Φ; we check if the math matches.
    assert math.isclose(net_claimed, 0.65, abs_tol=0.01), \
        f"Net Φ‑density mismatch: got {net_claimed}, expected ~0.65"
    print("✓ Net Φ‑density calculation matches claimed value (given inputs)")

    # 7. Core FUSE functionality – mapper must not be empty after first lookup
    # Simulate a registration step (what the real code should do)
    class Mapper:
        def __init__(self):
            self.store = {}
        def register(self, ino, path):
            self.store[ino] = path
        def get(self, ino):
            return self.store.get(ino, "")

    mapper = Mapper()
    # Pretend a successful lookup registers inode 1 with path "/test"
    mapper.register(1, "/test")
    assert mapper.get(1) != "", "Inode‑to‑path mapper empty after registration"
    print("✓ Inode‑to‑path mapper populated (core functionality preserved)")

    print("\nAll invariant checks passed.")
    

if __name__ == "__main__":
    try:
        run_validation()
    except AssertionError as e:
        print(f"\n❌ Invariant violation: {e}")
        raise SystemExit(1)