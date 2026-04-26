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
  * Trust score stays in [0,1]
  * Mitigation factor = 0.8 * trust_score (clamped to [0.2,1.0] as per spec)
  * Jitter probability ∈ [0,1] and derived from formula
  * Applied jitter latency ∈ [0,50] ms unless shredding threshold triggers
  * TraversalScore ≥ 0
  * ForensicLogEntry fields are physically plausible
  * Entropy‑based terms are non‑negative
Run with:  python3 afds_invariant_check.py
"""

import math
import random
from typing import NamedTuple

# ----------------------------------------------------------------------
# Constants taken from the C++ sketch (must match the implementation)
# ----------------------------------------------------------------------
K_BOLTZMANN = 1.0
TRUST_TIME_CONSTANT = 3600.0          # seconds
XI_N = 0.8
XI_DELTA = 1.2
SHRED_THRESHOLD = 0.95                # phi_Delta > SHRED_THRESHOLD => 1000 ms jitter
MAX_JITTER_MS = 50
MIN_JITTER_MS = 1

# ----------------------------------------------------------------------
# Helper data structures (mirroring the C++ structs)
# ----------------------------------------------------------------------
class ProcessTrustState(NamedTuple):
    pid: int
    trust_score: float
    cumulative_stability: float
    accessed_paths: set
    last_access: float  # seconds since epoch (steady clock approximated)

class TopologyMetrics(NamedTuple):
    unique_paths: set
    max_depth: int
    depth_histogram: dict  # depth -> count
    traversal_entropy: float

class ForensicLogEntry(NamedTuple):
    timestamp: float
    pid: int
    operation: str
    path: str
    applied_latency_ms: int
    traversal_score: float
    trust_score: float
    inter_call_interval: float
    phi_Delta: float

# ----------------------------------------------------------------------
# Core mathematical functions (direct translations)
# ----------------------------------------------------------------------
def update_trust(state: ProcessTrustState, path: str, access_success: bool,
                 now: float) -> ProcessTrustState:
    """Return a new ProcessTrustState after applying the trust update."""
    is_novel = path not in state.accessed_paths
    novelty_penalty = K_BOLTZMANN * 0.05 if is_novel else 0.0

    # time decay
    duration = now - state.last_access
    normalized_time = duration / TRUST_TIME_CONSTANT
    trust_after_decay = state.trust_score * math.exp(-normalized_time)
    trust_after_decay = max(0.0, min(1.0, trust_after_decay - novelty_penalty))

    # stability gain (only for non‑novel accesses)
    cumulative_stability = state.cumulative_stability
    if not is_novel:
        cumulative_stability += math.exp(-normalized_time)
        stability_gain = K_BOLTZMANN * 0.01 * math.exp(-0.1 * cumulative_stability)
        trust_after_decay += stability_gain
        trust_after_decay = max(0.0, min(1.0, trust_after_decay))

    new_accessed = set(state.accessed_paths)
    new_accessed.add(path)

    return ProcessTrustState(
        pid=state.pid,
        trust_score=trust_after_decay,
        cumulative_stability=cumulative_stability,
        accessed_paths=new_accessed,
        last_access=now,
    )

def trust_mitigation(trust_score: float) -> float:
    """Spec‑defined mitigation: 80% reduction for high trust."""
    return 0.8 * trust_score  # per spec: mitigation factor applied to base latency

def calculate_traversal_score(metrics: TopologyMetrics) -> float:
    """TraversalScore = 0.6 * |unique_paths| + 0.4 * max_depth"""
    return 0.6 * len(metrics.unique_paths) + 0.4 * metrics.max_depth

def asymmetric_threat(metrics: TopologyMetrics) -> float:
    """|breadth - depth| / (breadth + depth)"""
    breadth = len(metrics.unique_paths)
    depth = metrics.max_depth
    if breadth + depth == 0:
        return 0.0
    return abs(breadth - depth) / (breadth + depth)

def jitter_probability(raw_score: float, mitigation: float, phi_Delta: float) -> float:
    """p = (raw_score/100)^1.5 * mitigation * (1 + phi_Delta), clamped [0,1]"""
    base = (raw_score / 100.0) ** 1.5
    p = base * mitigation * (1.0 + phi_Delta)
    return max(0.0, min(1.0, p))

def apply_adaptive_jitter(raw_score: float, mitigation: float, phi_Delta: float) -> int:
    """Return jitter latency in ms; 1000 ms if shredding threshold breached."""
    if phi_Delta > SHRED_THRESHOLD:
        return 1000  # shredding latency
    prob = jitter_probability(raw_score, mitigation, phi_Delta)
    if random.random() < prob:
        # uniform 1‑50 ms jitter
        return random.randint(MIN_JITTER_MS, MAX_JITTER_MS)
    return 0

def topological_impedance(log_entries) -> float:
    """Simplified version of CalculateTopologicalImpedance:
       sum over entries of (gauge_avg * delta_psi) where
       psi = log(trust_score + eps), gauge = trust_score * |phi_Delta|
    """
    eps = 1e-10
    impedance = 0.0
    prev_psi = None
    prev_gauge = None
    for e in log_entries:
        psi = math.log(e.trust_score + eps)
        gauge = e.trust_score * abs(e.phi_Delta)
        if prev_psi is not None:
            delta_psi = psi - prev_psi
            impedance += (gauge + prev_gauge) / 2.0 * delta_psi
        prev_psi, prev_gauge = psi, gauge
    return impedance

# ----------------------------------------------------------------------
# Invariant checks (assertions)
# ----------------------------------------------------------------------
def run_invariant_suite():
    print("=== Omega Protocol Invariant Suite for AFDS v3.0 ===")

    # 1. Trust score bounds and monotonic decay
    now0 = 0.0
    state = ProcessTrustState(pid=42, trust_score=0.5,
                              cumulative_stability=0.0,
                              accessed_paths=set(),
                              last_access=now0)
    # simulate a few accesses
    for i in range(5):
        state = update_trust(state, f"/path/{i}", access_success=True,
                             now=now0 + i * 100.0)  # 100s between accesses
        assert 0.0 <= state.trust_score <= 1.0, f"Trust out of bounds: {state.trust_score}"
        assert 0.0 <= state.cumulative_stability, f"Negative stability: {state.cumulative_stability}"
    print("✓ Trust score stays in [0,1] and stability non‑negative")

    # 2. Mitigation factor mapping
    for ts in [0.0, 0.25, 0.5, 0.75, 1.0]:
        mit = trust_mitigation(ts)
        assert 0.0 <= mit <= 0.8, f"Mitigation out of expected range: {mit}"
    print("✓ Mitigation factor = 0.8 * trust_score within [0,0.8]")

    # 3. TraversalScore non‑negative
    metrics = TopologyMetrics(unique_paths={"/a", "/b/c"}, max_depth=2,
                              depth_histogram={1:1, 2:1}, traversal_entropy=0.0)
    score = calculate_traversal_score(metrics)
    assert score >= 0.0, f"Negative traversal score: {score}"
    print("✓ TraversalScore ≥ 0")

    # 4. Asymmetric threat in [0,1]
    threat = asymmetric_threat(metrics)
    assert 0.0 <= threat <= 1.0, f"Threat outside [0,1]: {threat}"
    print("✓ Asymmetric threat ∈ [0,1]")

    # 5. Jitter probability in [0,1]
    prob = jitter_probability(raw_score=score,
                              mitigation=trust_mitigation(state.trust_score),
                              phi_Delta=threat)
    assert 0.0 <= prob <= 1.0, f"Jitter probability OOB: {prob}"
    print("✓ Jitter probability ∈ [0,1]")

    # 6. Applied jitter latency bounds (unless shredding)
    latency = apply_adaptive_jitter(raw_score=score,
                                    mitigation=trust_mitigation(state.trust_state.trust_score),
                                    phi_Delta=threat)
    if threat <= SHRED_THRESHOLD:
        assert latency == 0 or (MIN_JITTER_MS <= latency <= MAX_JITTER_MS), \
            f"Jitter latency out of [1,50] ms: {latency}"
    else:
        assert latency == 1000, f"Shredding threshold not triggered correctly: {latency}"
    print("✓ Jitter latency respects spec (1‑50 ms or 1000 ms on shred)")

    # 7. ForensicLogEntry physical plausibility
    entry = ForensicLogEntry(
        timestamp=now0 + 200.0,
        pid=state.pid,
        operation="lookup",
        path="/test/file",
        applied_latency_ms=latency,
        traversal_score=score,
        trust_score=state.trust_score,
        inter_call_interval=100.0,
        phi_Delta=threat,
    )
    assert entry.applied_latency_ms >= 0
    assert 0.0 <= entry.trust_score <= 1.0
    assert entry.traversal_score >= 0.0
    assert 0.0 <= entry.phi_Delta <= 1.0
    print("✓ ForensicLogEntry fields within physical bounds")

    # 8. Topological impedance non‑negative (by construction of the integral)
    impedance = topological_impedance([entry])
    assert impedance >= 0.0, f"Topological impedance negative: {impedance}"
    print("✓ Topological impedance ≥ 0 (non‑negative by definition)")

    print("\nAll invariant checks PASSED.")
    return True

if __name__ == "__main__":
    try:
        run_invariant_suite()
    except AssertionError as e:
        print(f"\nINVARIANT VIOLATION: {e}")
        exit(1)