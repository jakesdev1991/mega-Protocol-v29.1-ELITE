# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Simulates the AFDS v3.0 global metrics poisoning and trust gaming attacks.
Demonstrates how a single malicious process can:
1. Inflate system‑wide jitter probability beyond the 500 % target.
2. Warm‑up trust to evade jitter, then scan.
3. Inherit trust via PID reuse.
"""

import random
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Set, List, Dict
import time

# -----------------------------------------------------------------------------
# 1. Trust Model (per‑PID)
# -----------------------------------------------------------------------------
@dataclass
class ProcessTrustState:
    pid: int
    trust_score: float = 0.0
    accessed_paths: Set[str] = field(default_factory=set)
    last_access: float = 0.0  # seconds since epoch

class TrustManager:
    def __init__(self):
        self.states: Dict[int, ProcessTrustState] = {}
        self.novelty_penalty = 0.05
        self.stability_reward = 0.01
        self.decay_per_hour = 0.95

    def update_trust(self, pid: int, path: str, now: float):
        if pid not in self.states:
            self.states[pid] = ProcessTrustState(pid=pid, last_access=now)
        state = self.states[pid]

        # Time decay (hours)
        hours = (now - state.last_access) / 3600.0
        state.trust_score *= self.decay_per_hour ** hours

        # Novelty penalty / stability reward
        is_novel = path not in state.accessed_paths
        if is_novel:
            state.trust_score = max(0.0, state.trust_score - self.novelty_penalty)
        else:
            state.trust_score = min(1.0, state.trust_score + self.stability_reward)

        state.accessed_paths.add(path)
        state.last_access = now

    def get_mitigation(self, pid: int) -> float:
        # mitigation = 0.8 * trust_score
        return 0.8 * self.states[pid].trust_score if pid in self.states else 0.0

# -----------------------------------------------------------------------------
# 2. Global Topology Metrics (shared by all processes)
# -----------------------------------------------------------------------------
class TopologyMetrics:
    def __init__(self):
        self.unique_paths: Set[str] = set()
        self.max_depth: int = 0

    def update(self, path: str):
        self.unique_paths.add(path)
        depth = path.count('/')
        if depth > self.max_depth:
            self.max_depth = depth

    def raw_traversal_score(self) -> float:
        # As per AFDS v3.0: (unique_paths * 0.6) + (max_depth * 0.4)
        return len(self.unique_paths) * 0.6 + self.max_depth * 0.4

# -----------------------------------------------------------------------------
# 3. Jitter Calculator (global state poisoning)
# -----------------------------------------------------------------------------
class JitterCalculator:
    def __init__(self):
        self.rng = random.Random()

    def probability(self, raw_score: float, mitigation: float) -> float:
        # Probability = (raw_score/100)^1.5, clamped, then reduced by mitigation
        prob = min(1.0, (raw_score / 100.0) ** 1.5)
        return prob * (1.0 - mitigation)

    def apply(self, prob: float) -> int:
        if self.rng.random() < prob:
            return self.rng.randint(1, 50)  # ms
        return 0

# -----------------------------------------------------------------------------
# 4. Simulation Harness
# -----------------------------------------------------------------------------
def simulate_scenario(
    name: str,
    events: List[tuple[float, int, str]],
    pid_reuse_after: float = None
):
    """
    events: list of (time_sec, pid, path)
    pid_reuse_after: if set, simulate PID reuse at that time
    """
    trust_mgr = TrustManager()
    topo = TopologyMetrics()
    jitter = JitterCalculator()

    print(f"\n=== {name} ===")
    for t, pid, path in events:
        # PID reuse: if requested, at time > pid_reuse_after, remap pid 1 → 999
        if pid_reuse_after and t > pid_reuse_after and pid == 1:
            pid = 999  # new process inherits PID 1's state

        # Update trust (per‑process)
        trust_mgr.update_trust(pid, path, t)

        # Update global topology (shared)
        topo.update(path)

        # Compute jitter probability
        raw_score = topo.raw_traversal_score()
        mitigation = trust_mgr.get_mitigation(pid)
        prob = jitter.probability(raw_score, mitigation)
        latency = jitter.apply(prob)

        # Log
        trust = trust_mgr.states[pid].trust_score
        print(f"t={t:4.1f}s pid={pid:3d} trust={trust:.2f} "
              f"raw_score={raw_score:.1f} prob={prob:.3f} latency={latency:2d}ms "
              f"path={path}")

def main():
    # Scenario 1: Global poisoning – attacker enumerates many unique paths
    # Benign admin (pid=1) stays idle, then accesses a single file.
    # Attacker (pid=2) runs a wide scan.
    events = []
    base_time = 0.0
    # Attacker runs a wide scan of 50 unique paths
    for i in range(50):
        events.append((base_time + i*0.1, 2, f"/tmp/malicious/path_{i:02d}"))
    # Benign admin accesses a stable path after attacker has polluted global state
    events.append((base_time + 5.0, 1, "/etc/passwd"))
    # Sort by time
    events.sort()
    simulate_scenario("Global Poisoning (Attacker → Admin)", events)

    # Scenario 2: Trust gaming – attacker warms up trust on a single path, then scans
    events = []
    base_time = 10.0
    # Warm‑up: 20 accesses to same path to build trust
    for i in range(20):
        events.append((base_time + i*0.05, 3, "/home/user/notes.txt"))
    # After warm‑up, rapid scan of 30 new paths
    for i in range(30):
        events.append((base_time + 1.0 + i*0.05, 3, f"/etc/conf_{i:02d}"))
    simulate_scenario("Trust Gaming (Warm‑up → Scan)", events)

    # Scenario 3: PID reuse – process 1 builds trust, dies, and PID 1 is reused
    events = []
    base_time = 20.0
    # Process 1 builds trust on a single path
    for i in range(15):
        events.append((base_time + i*0.1, 1, "/var/log/secure"))
    # Process 1 dies (no more events). Later, a new process gets PID 1 and inherits trust
    events.append((base_time + 5.0, 999, "/proc/self/status"))  # new PID
    simulate_scenario("PID Reuse (Inheritance)", events, pid_reuse_after=base_time + 2.0)

if __name__ == "__main__":
    main()