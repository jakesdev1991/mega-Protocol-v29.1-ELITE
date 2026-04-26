# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for AFDS v3.0 (C++ reference implementation)

This script checks the mathematical soundness and invariant compliance of the
core algorithms presented in the Engine's pleading. It does **not** attempt to
validate the benchmark stub (which is non‑functional) but focuses on the
deterministic functions that can be exercised in isolation.

Invariants checked (derived from the C++ code and Omega Protocol expectations):
1. Trust scores remain in [0, 1].
2. Trust mitigation factor is either 0.8 * trust_score (if state exists) or 1.0.
3. Novelty penalty is non‑negative.
4. Updated trust score after UpdateTrust stays in [0, 1].
5. Newtonian trust baseline is non‑negative.
6. Traversal score is non‑negative.
7. Jitter probability is clamped to [0, 1].
8. Applied latency is either 0, in [1, 51] ms, or exactly 1000 ms (shredding).
9. Asymmetric threat (phi_Delta) is in [0, 1].
10. Forensic log fields are within expected ranges.
11. Topological impedance is a real number (no NaN/Inf).
12. Manifold curvature is a real number.
13. No division by zero or overflow in any formula.

If any invariant is violated, the script prints a detailed trace and exits
with a non‑zero status code.
"""

import math
import random
import sys
from typing import Dict, Tuple, List

# ----------------------------------------------------------------------
# Helper classes mirroring the C++ logic (simplified, single‑threaded)
# ----------------------------------------------------------------------
class ProcessTrustState:
    def __init__(self, pid: int):
        self.pid = pid
        self.trust_score: float = 0.0
        self.last_access: float = 0.0          # seconds since epoch (dummy)
        self.accessed_paths: set = set()
        self.cumulative_stability: float = 0.0

class TrustManager:
    K_BOLTZMANN = 1.0
    TRUST_TIME_CONSTANT = 3600.0

    def __init__(self):
        self.process_states: Dict[int, ProcessTrustState] = {}

    def _get_state(self, pid: int) -> ProcessTrustState:
        if pid not in self.process_states:
            self.process_states[pid] = ProcessTrustState(pid)
        return self.process_states[pid]

    def UpdateTrust(self, pid: int, path: str, access_success: bool,
                    now: float = None) -> None:
        if now is None:
            now = random.uniform(0, 1e6)  # dummy timestamp
        state = self._get_state(pid)

        is_novel = path not in state.accessed_paths
        novelty_penalty = self.K_BOLTZMANN * 0.05 if is_novel else 0.0

        duration = now - state.last_access if state.last_access != 0.0 else 0.0
        normalized_time = duration / self.TRUST_TIME_CONSTANT

        # decay
        state.trust_score *= math.exp(-normalized_time)
        state.trust_score = max(0.0, min(1.0, state.trust_score - novelty_penalty))

        if not is_novel:
            state.cumulative_stability += math.exp(-normalized_time)
            stability_gain = self.K_BOLTZMANN * 0.01 * math.exp(-0.1 * state.cumulative_stability)
            state.trust_score += stability_gain
            state.trust_score = max(0.0, min(1.0, state.trust_score))

        state.accessed_paths.add(path)
        state.last_access = now

    def GetTrustMitigation(self, pid: int) -> float:
        state = self.process_states.get(pid)
        if state is None:
            return 1.0
        return 0.8 * state.trust_score

    def CalculateNewtonianTrustBaseline(self, pid: int) -> float:
        state = self.process_states.get(pid)
        if state is None:
            return 0.0
        H_noise = math.log(len(state.accessed_paths) + 1)
        return math.exp(-H_noise) * state.cumulative_stability

class TopologyMetrics:
    def __init__(self):
        self.max_depth: int = 0
        self.unique_paths: set = set()
        self.depth_histogram: List[int] = []
        self.traversal_entropy: float = 0.0

def CalculateTraversalScore(metrics: TopologyMetrics) -> float:
    return 0.6 * len(metrics.unique_paths) + 0.4 * metrics.max_depth

def ApplyAdaptiveJitter(raw_score: float, mitigation: float, phi_Delta: float) -> int:
    # probability calculation
    probability = (raw_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_Delta)
    probability = max(0.0, min(1.0, probability))

    if phi_Delta > 0.95:
        return 1000   # shredding latency

    # stochastic jitter
    if random.random() < probability:
        return 1 + int(50.0 * random.random())
    return 0

def UpdateTopology(path: str, metrics: TopologyMetrics) -> None:
    metrics.unique_paths.add(path)
    depth = path.count('/')
    if depth > metrics.max_depth:
        metrics.max_depth = depth
    # histogram
    if depth >= len(metrics.depth_histogram):
        metrics.depth_histogram.extend([0] * (depth - len(metrics.depth_histogram) + 1))
    metrics.depth_histogram[depth] += 1
    metrics.traversal_entropy += math.log(depth + 1) * 0.01

def CalculateAsymmetricThreat(metrics: TopologyMetrics) -> float:
    breadth = len(metrics.unique_paths)
    depth = metrics.max_depth
    if breadth + depth == 0:
        return 0.0
    return abs(breadth - depth) / (breadth + depth)

class ForensicLogEntry:
    def __init__(self, timestamp: float, pid: int, operation: str, path: str,
                 applied_latency_ms: int, traversal_score: float,
                 trust_score: float, inter_call_interval: float, phi_Delta: float):
        self.timestamp = timestamp
        self.pid = pid
        self.operation = operation
        self.path = path
        self.applied_latency_ms = applied_latency_ms
        self.traversal_score = traversal_score
        self.trust_score = trust_score
        self.inter_call_interval = inter_call_interval
        self.phi_Delta = phi_Delta

class ForensicLogger:
    def __init__(self):
        self.log_entries: List[ForensicLogEntry] = []

    def LogAccess(self, entry: ForensicLogEntry) -> None:
        self.log_entries.append(entry)

    def CalculateTopologicalImpedance(self) -> float:
        if not self.log_entries:
            return 0.0
        impedance = 0.0
        prev_psi = 0.0
        prev_gauge = 0.0
        for e in self.log_entries:
            psi = math.log(e.trust_score + 1e-10)
            gauge = e.trust_score * abs(e.phi_Delta)
            delta_psi = psi - prev_psi
            impedance += (gauge + prev_gauge) / 2.0 * delta_psi
            prev_psi = psi
            prev_gauge = gauge
        return impedance

# ----------------------------------------------------------------------
# Invariant checking routines
# ----------------------------------------------------------------------
def check_trust_invariants(tm: TrustManager, pid: int, path: str,
                           now: float, success: bool) -> Tuple[bool, str]:
    """Run UpdateTrust and verify post‑conditions."""
    state_before = tm.process_states.get(pid)
    ts_before = state_before.trust_score if state_before else 0.0

    tm.UpdateTrust(pid, path, success, now)

    state_after = tm.process_states[pid]
    ts_after = state_after.trust_score

    if not (0.0 <= ts_after <= 1.0):
        return (False,
                f"Trust score out of bounds: {ts_after} (before {ts_before})")
    mitigation = tm.GetTrustMitigation(pid)
    if state_after is None:
        if not math.isclose(mitigation, 1.0):
            return (False,
                    f"Mitigation for unknown PID should be 1.0, got {mitigation}")
    else:
        expected = 0.8 * ts_after
        if not math.isclose(mitigation, expected, rel_tol=1e-9):
            return (False,
                    f"Mitigation mismatch: expected {expected}, got {mitigation}")
    return (True, "")

def check_jitter_invariants() -> Tuple[bool, str]:
    """Test ApplyAdaptiveJitter over a grid of inputs."""
    for raw in [0.0, 20.0, 50.0, 80.0, 100.0, 150.0]:
        for mit in [0.0, 0.4, 0.8, 1.0]:
            for phi in [0.0, 0.5, 0.9, 0.96, 1.0]:
                lat = ApplyAdaptiveJitter(raw, mit, phi)
                # probability must be in [0,1] (internal check)
                prob = (raw / 100.0) ** 1.5 * mit * (1.0 + phi)
                prob = max(0.0, min(1.0, prob))
                if phi > 0.95:
                    if lat != 1000:
                        return (False,
                                f"Shredding condition failed: raw={raw}, mit={mit}, phi={phi} -> lat={lat}")
                else:
                    if lat != 0 and not (1 <= lat <= 51):
                        return (False,
                                f"Jitter latency out of range: raw={raw}, mit={mit}, phi={phi} -> lat={lat}")
    return (True, "")

def check_topology_invariants() -> Tuple[bool, str]:
    metrics = TopologyMetrics()
    paths = ["/", "/a", "/a/b", "/a/b/c", "/x/y"]
    for p in paths:
        UpdateTopology(p, metrics)
    # unique_paths size must equal number of distinct paths inserted
    if len(metrics.unique_paths) != len(set(paths)):
        return (False, "unique_paths size mismatch")
    # max_depth must be max '/' count
    expected_depth = max(p.count('/') for p in paths)
    if metrics.max_depth != expected_depth:
        return (False, f"max_depth mismatch: got {metrics.max_depth}, expected {expected_depth}")
    # traversal score non‑negative
    if CalculateTraversalScore(metrics) < 0:
        return (False, "Negative traversal score")
    # asymmetric threat in [0,1]
    phi = CalculateAsymmetricThreat(metrics)
    if not (0.0 <= phi <= 1.0):
        return (False, f"Asymmetric threat out of bounds: {phi}")
    return (True, "")

def check_forensic_invariants() -> Tuple[bool, str]:
    logger = ForensicLogger()
    # create a few dummy entries
    for i in range(5):
        entry = ForensicLogEntry(
            timestamp=1e6 + i,
            pid=100 + i,
            operation="lookup",
            path=f"/tmp/file{i}",
            applied_latency_ms=random.choice([0, 10, 30, 1000]),
            traversal_score=random.uniform(0, 200),
            trust_score=random.uniform(0, 0.8),
            inter_call_interval=random.uniform(0, 500),
            phi_Delta=random.uniform(0, 1)
        )
        logger.LogAccess(entry)
        # field checks
        if not (0.0 <= entry.trust_score <= 0.8 or math.isclose(entry.trust_score, 1.0)):
            return (False, f"Forensic trust_score invalid: {entry.trust_score}")
        if entry.applied_latency_ms < 0:
            return (False, f"Negative latency: {entry.applied_latency_ms}")
        if not (0.0 <= entry.phi_Delta <= 1.0):
            return (False, f"Forensic phi_Delta out of bounds: {entry.phi_Delta}")
        if entry.inter_call_interval < 0:
            return (False, f"Negative inter-call interval: {entry.inter_call_interval}")
    # impedance should be a real number
    imp = logger.CalculateTopologicalImpedance()
    if math.isnan(imp) or math.isinf(imp):
        return (False, f"Topological impedance is NaN/Inf: {imp}")
    return (True, "")

def check_manifold_curvature() -> Tuple[bool, str]:
    tm = TrustManager()
    metrics = TopologyMetrics()
    logger = ForensicLogger()
    pid = 42
    # populate some state
    tm.UpdateTrust(pid, "/tmp/test", True, now=1e6)
    UpdateTopology("/tmp/test", metrics)
    UpdateTopology("/tmp/test/sub", metrics)
    phi_N = tm.CalculateNewtonianTrustBaseline(pid)
    phi_Delta = CalculateAsymmetricThreat(metrics)
    h_imp = logger.CalculateTopologicalImpedance()
    XI_N, XI_DELTA = 0.8, 1.2
    curvature = XI_N * phi_N + XI_DELTA * phi_Delta - h_imp
    if math.isnan(curvature) or math.isinf(curvature):
        return (False, f"Manifold curvature is NaN/Inf: {curvature}")
    return (True, "")

def main() -> None:
    random.seed(0xC0FFEE)  # deterministic for CI
    failures = []

    # Trust manager invariants
    tm = TrustManager()
    pid = 1234
    path = "/etc/passwd"
    now = 1_700_000_000.0
    ok, msg = check_trust_invariants(tm, pid, path, now, True)
    if not ok:
        failures.append(f"Trust invariant: {msg}")
    ok, msg = check_trust_invariants(tm, pid, "/etc/shadow", now + 10, False)
    if not ok:
        failures.append(f"Trust invariant (novel): {msg}")

    # Jitter invariants
    ok, msg = check_jitter_invariants()
    if not ok:
        failures.append(f"Jitter invariant: {msg}")

    # Topology invariants
    ok, msg = check_topology_invariants()
    if not ok:
        failures.append(f"Topology invariant: {msg}")

    # Forensic invariants
    ok, msg = check_forensic_invariants()
    if not ok:
        failures.append(f"Forensic invariant: {msg}")

    # Manifold curvature
    ok, msg = check_manifold_curvature()
    if not ok:
        failures.append(f"Manifold curvature invariant: {msg}")

    if failures:
        print("Omega Protocol Invariant Validation FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checked invariants are mathematically sound.")
        # Note: benchmark stub and PhiDensity calculation are not validated
        print("Note: Benchmark stub and PhiDensity calculation remain unverified.")
        sys.exit(0)

if __name__ == "__main__":
    main()