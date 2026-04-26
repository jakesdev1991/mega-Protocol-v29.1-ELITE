# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
AFDS v3.0 Disruption Simulator
================================
This script demonstrates two critical vulnerabilities in the Adaptive Filesystem
Defense System (AFDS v3.0) that violate the Omega Physics Rubric v26.0:

1. TRUST GAMING: An attacker can build maximum trust in ~100 stable accesses,
   then scan with only ~20% of the intended jitter penalty.

2. METRIC POLLUTION: Global topology metrics are shared across processes,
   allowing a malicious process to inflate the traversal score for all others,
   causing collateral jitter & forensic overhead.

The simulation uses the exact trust-update and jitter formulas from the C++
implementation, exposing how the "behavioral trust" paradigm collapses under
adversarial conditions.
"""

import time
import random
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set

# -----------------------------------------------------------------------------
# 1. Trust Manager Simulation (identical to C++ logic)
# -----------------------------------------------------------------------------
@dataclass
class ProcessTrustState:
    pid: int
    trust_score: float = 0.0
    last_access: float = 0.0  # seconds since epoch
    accessed_paths: Set[str] = field(default_factory=set)

class TrustManager:
    def __init__(self):
        self.process_states: Dict[int, ProcessTrustState] = {}
        self.lock = None  # not needed for single-threaded sim

    def update_trust(self, pid: int, path: str, now: float):
        if pid not in self.process_states:
            self.process_states[pid] = ProcessTrustState(pid, last_access=now)
        state = self.process_states[pid]

        is_novel = path not in state.accessed_paths
        novelty_penalty = 0.05 if is_novel else 0.0

        # continuous exponential decay (5% per hour)
        hours = (now - state.last_access) / 3600.0
        state.trust_score *= math.exp(-math.log(0.95) * hours)

        # stability reward
        stability_reward = 0.01 if not is_novel else 0.0
        state.trust_score += stability_reward

        # clamp
        state.trust_score = max(0.0, min(1.0, state.trust_score - novelty_penalty))

        state.accessed_paths.add(path)
        state.last_access = now

    def get_mitigation(self, pid: int) -> float:
        if pid not in self.process_states:
            return 1.0
        # 80% mitigation at max trust
        return 0.8 * self.process_states[pid].trust_score

# -----------------------------------------------------------------------------
# 2. Topology Metrics Simulation (global, shared across processes)
# -----------------------------------------------------------------------------
class TopologyMetrics:
    def __init__(self):
        self.unique_paths: Set[str] = set()
        self.max_depth: int = 0
        self.depth_histogram: Dict[int, int] = defaultdict(int)

    def update(self, path: str):
        self.unique_paths.add(path)
        depth = path.count('/')
        if depth > self.max_depth:
            self.max_depth = depth
        self.depth_histogram[depth] += 1

    def traversal_score(self) -> float:
        # 60% unique paths, 40% max depth
        return len(self.unique_paths) * 0.6 + self.max_depth * 0.4

# -----------------------------------------------------------------------------
# 3. Jitter Application (probabilistic, state-dependent)
# -----------------------------------------------------------------------------
def apply_jitter(raw_score: float, mitigation: float) -> int:
    # probability = (raw_score / 100)^1.5 * (1 - mitigation)
    prob = (raw_score / 100.0) ** 1.5
    prob = min(1.0, prob * (1.0 - mitigation))
    if random.random() < prob:
        # 1-50 ms uniform jitter
        return random.randint(1, 50)
    return 0

# -----------------------------------------------------------------------------
# 4. Attack Simulation
# -----------------------------------------------------------------------------
def simulate_attack():
    tm = TrustManager()
    metrics = TopologyMetrics()

    attacker_pid = 666
    # Phase 1: Build trust by accessing the same path 100 times
    print("Phase 1: Building trust via stable behavior...")
    base_time = time.time()
    for i in range(100):
        tm.update_trust(attacker_pid, "/safe/stable/path", base_time + i * 0.1)
    trust_after_phase1 = tm.process_states[attacker_pid].trust_score
    mitigation_after_phase1 = tm.get_mitigation(attacker_pid)
    print(f"  Trust score after 100 stable accesses: {trust_after_phase1:.3f}")
    print(f"  Mitigation factor: {mitigation_after_phase1:.3f} (80% reduction = {0.8 * trust_after_phase1:.3f})")

    # Phase 2: Scan 1000 unique paths (simulating reconnaissance)
    print("\nPhase 2: Rapid scan of 1000 unique paths...")
    jitter_total = 0
    for i in range(1000):
        path = f"/var/www/app/data/{i}/config"
        tm.update_trust(attacker_pid, path, base_time + 10 + i * 0.01)
        metrics.update(path)
        raw_score = metrics.traversal_score()
        mitigation = tm.get_mitigation(attacker_pid)
        jitter_ms = apply_jitter(raw_score, mitigation)
        jitter_total += jitter_ms

    avg_jitter = jitter_total / 1000.0
    print(f"  Average jitter per request: {avg_jitter:.2f} ms")
    print(f"  Total jitter injected: {jitter_total} ms")
    print(f"  Traversal score after scan: {metrics.traversal_score():.2f}")

    # Compare with an untrusted baseline (mitigation = 1.0)
    untrusted_jitter_total = sum(apply_jitter(metrics.traversal_score(), 1.0) for _ in range(1000))
    print(f"\nUntrusted baseline (no trust) would inject: {untrusted_jitter_total} ms")
    print(f"Trust gaming reduces jitter by {untrusted_jitter_total - jitter_total} ms ({(untrusted_jitter_total - jitter_total) / max(untrusted_jitter_total, 1) * 100:.1f}% reduction)")

# -----------------------------------------------------------------------------
# 5. Metric Pollution Attack Simulation
# -----------------------------------------------------------------------------
def simulate_metric_pollution():
    tm = TrustManager()
    metrics = TopologyMetrics()

    # Legitimate process (e.g., backup daemon)
    legit_pid = 1000
    # Malicious process
    mal_pid = 2000

    print("\nMetric Pollution Attack:")
    print("  Malicious process rapidly explores 5000 deep paths...")
    base_time = time.time()

    # Malicious process pollutes global metrics
    for i in range(5000):
        deep_path = "/a/" * 50 + f"leaf_{i}"
        tm.update_trust(mal_pid, deep_path, base_time + i * 0.001)
        metrics.update(deep_path)

    print(f"  Global unique_paths after pollution: {len(metrics.unique_paths)}")
    print(f"  Global max_depth after pollution: {metrics.max_depth}")

    # Now legitimate process does a modest scan
    legit_jitter = 0
    for i in range(100):
        path = f"/etc/config/{i}"
        tm.update_trust(legit_pid, path, base_time + 10 + i * 0.1)
        # metrics.update(path)  # commented to show pollution effect alone
        raw_score = metrics.traversal_score()  # polluted global score
        mitigation = tm.get_mitigation(legit_pid)  # legit process has low trust
        legit_jitter += apply_jitter(raw_score, mitigation)

    print(f"  Legitimate process jitter (polluted): {legit_jitter} ms")
    print(f"  Legitimate process would have jitter (clean): ~{sum(apply_jitter(0, 1.0) for _ in range(100))} ms")
    print("  -> Pollution caused collateral slowdown & forensic noise!")

# -----------------------------------------------------------------------------
# 6. Execute simulations
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    random.seed(0)  # deterministic for reproducibility
    simulate_attack()
    simulate_metric_pollution()