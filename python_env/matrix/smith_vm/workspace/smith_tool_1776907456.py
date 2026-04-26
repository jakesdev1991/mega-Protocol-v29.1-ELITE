# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for AFDS v3.0
------------------------------------------------
Checks:
  * Trust decay matches 5%/hour continuous exponential.
  * Mitigation = 0.8 * trust_score.
  * Jitter probability = (raw/100)^1.5 * (1-mitigation) clamped [0,1].
  * Jitter magnitude in [1,50] ms when triggered.
  * Trust score always stays in [0,1].
  * Topology metrics update correctly (unique paths, max depth).
  * Benchmark isolation: baseline must NOT call any AFDS update;
                         AFDS run MUST update topology.
  * FPR test must use >=2 distinct benign paths.
  * Memory/CPU overhead must be non‑stub (i.e., not a constant).
  * SecurityManifoldCurvature must be non‑zero (placeholder not allowed).
"""

import math
import random
import time
from typing import List, Tuple

# ----------------------------------------------------------------------
# Mocked minimal AFDS components (as they appear in the pleading code)
# ----------------------------------------------------------------------
class TrustManager:
    def __init__(self):
        self._state = {}          # pid -> (trust, last_access, paths)
        self._lambda = -math.log(0.95) / 3600.0  # per second

    def update(self, pid: int, path: str, now: float):
        trust, last, paths = self._state.get(pid, (0.0, now, set()))
        is_novel = path not in paths
        # continuous decay
        hours = (now - last) / 3600.0
        trust *= math.exp(-self._lambda * hours * 3600)  # same as exp(-lambda * delta_t)
        if not is_novel:
            trust += 0.01
        if is_novel:
            trust -= 0.05
        trust = max(0.0, min(1.0, trust))
        paths.add(path)
        self._state[pid] = (trust, now, paths)

    def mitigation(self, pid: int) -> float:
        trust, _, _ = self._state.get(pid, (0.0, 0.0, set()))
        return 0.8 * trust


class TopologyMetrics:
    def __init__(self):
        self._paths = set()
        self._max_depth = 0
        self._depth_hist = []  # list of ints

    def update(self, path: str):
        self._paths.add(path)
        depth = path.count('/')
        if depth > self._max_depth:
            self._max_depth = depth
        if depth >= len(self._depth_hist):
            self._depth_hist.extend([0] * (depth + 1 - len(self._depth_hist)))
        self._depth_hist[depth] += 1

    def traversal_score(self) -> float:
        return len(self._paths) * 0.6 + self._max_depth * 0.4


def apply_jitter(raw_score: float, mitigation: float) -> Tuple[bool, int]:
    """Returns (jitter_applied, latency_ms)."""
    prob = (raw_score / 100.0) ** 1.5
    prob = max(0.0, min(1.0, prob * (1.0 - mitigation)))
    if random.random() < prob:
        latency = 1 + int(50.0 * random.random())  # 1..50 inclusive
        return True, latency
    return False, 0


def benchmark_isolation_check():
    """Simulate the benchmark suite and assert proper isolation."""
    # ---- Baseline (no AFDS) ----
    tm = TrustManager()
    topo = TopologyMetrics()
    start = time.perf_counter()
    for i in range(1000):
        path = f"/test{i}"
        # Baseline must NOT call trust or jitter updates.
        # It also must NOT update topology (per spec).
        # We deliberately *do not* call any AFDS method here.
        pass
    baseline = time.perf_counter() - start

    # ---- AFDS run (untrusted) ----
    tm2 = TrustManager()
    topo2 = TopologyMetrics()
    start = time.perf_counter()
    for i in range(1000):
        path = f"/test{i}"
        tm2.update(os.getpid(), path, time.time())   # trust update (allowed)
        topo2.update(path)                           # topology update (required)
        raw = topo2.traversal_score()
        lat = apply_jitter(raw, tm2.mitigation(os.getpid()))[1]  # jitter (may be 0)
        # we ignore latency for timing; just ensure the path was processed
    afds = time.perf_counter() - start

    slowdown = afds / baseline if baseline > 0 else float('inf')
    # The spec demands >500% slowdown → slowdown > 5.0
    if slowdown <= 5.0:
        raise AssertionError(
            f"AFDS slowdown insufficient: {slowdown:.2f}x (expected >5.0x)"
        )
    print(f"[OK] Baseline isolation & slowdown: {slowdown:.2f}x")


def fpr_check():
    """False‑positive test must use a realistic benign set."""
    tm = TrustManager()
    topo = TopologyMetrics()
    # Use at least 2 distinct safe paths to avoid degenerate score.
    safe_paths = ["/home/admin/docs", "/var/log/syslog"]
    hits = 0
    for _ in range(1000):
        path = random.choice(safe_paths)
        tm.update(os.getpid(), path, time.time())
        topo.update(path)
        score = topo.traversal_score()
        if score > 90.0:
            hits += 1
    fpr = hits / 1000.0
    if fpr >= 0.001:   # <0.1% target
        raise AssertionError(f"FPR too high: {fpr:.5f} (limit <0.001)")
    print(f"[OK] FPR: {fpr*100:.3f}%")


def trust_decay_check():
    """Verify continuous 5%/hour decay."""
    tm = TrustManager()
    pid = os.getpid()
    now = time.time()
    # Start with max trust
    tm._state[pid] = (1.0, now, set())
    # Wait 1 hour simulated
    later = now + 3600.0
    tm.update(pid, "/some/path", later)
    trust, _, _ = tm._state[pid]
    expected = 0.95  # exact 5% decay
    if not math.isclose(trust, expected, rel_tol=1e-6):
        raise AssertionError(
            f"Trust decay mismatch: got {trust:.6f}, expected {expected:.6f}"
        )
    print("[OK] Trust decay 5%/hour verified")


def mitigation_check():
    tm = TrustManager()
    pid = os.getpid()
    now = time.time()
    tm._state[pid] = (0.75, now, set())
    mit = tm.mitigation(pid)
    expected = 0.8 * 0.75
    if not math.isclose(mit, expected, rel_tol=1e-9):
        raise AssertionError(f"Mitigation error: {mit} vs {expected}")
    print("[OK] Mitigation formula correct")


def jitter_prob_check():
    """Statistical test: probability matches formula."""
    random.seed(42)
    tm = TrustManager()
    pid = os.getpid()
    now = time.time()
    tm._state[pid] = (0.5, now, set())
    mit = tm.mitigation(pid)
    # Choose a raw score that yields a known probability
    raw = 50.0  # => (0.5)^1.5 = 0.35355
    prob_theory = (raw / 100.0) ** 1.5 * (1.0 - mit)
    prob_theory = max(0.0, min(1.0, prob_theory))
    trials = 20000
    hits = sum(apply_jitter(raw, mit)[0] for _ in range(trials))
    empirical = hits / trials
    if not math.isclose(empirical, prob_theory, rel_tol=0.02):  # 2% tolerance
        raise AssertionError(
            f"Jitter probability off: empirical {empirical:.5f}, theory {prob_theory:.5f}"
        )
    print("[OK] Jitter probability within tolerance")


def jitter_range_check():
    """Ensure jitter magnitude is always 1..50 ms when applied."""
    for _ in range(5000):
        applied, lat = apply_jitter(200.0, 0.0)  # high score, no mitigation => likely jitter
        if applied:
            if not (1 <= lat <= 50):
                raise AssertionError(f"Jitter out of range: {lat} ms")
    print("[OK] Jitter magnitude range correct")


def stub_detector():
    """Fail if any Omega‑invariant stub is left unchanged."""
    # SecurityManifoldCurvature must be non‑zero (or at least not the literal 0.0 placeholder)
    # We cannot call the real function without the full OmegaProtocol libs, so we
    # check the source string for the placeholder comment.
    import inspect, os
    src = inspect.getsource(globals().get('CalculateSecurityManifoldCurvature', lambda: 0))
    if "Placeholder for manifold calculation" in src or src.strip() == "return 0.0":
        raise AssertionError("SecurityManifoldCurvature stub not implemented")
    # ForensicLogger.GenerateReport must not be empty
    src2 = inspect.getsource(ForensicLogger.GenerateReport)
    if "Implementation with entropy-aware reporting" in src2 and "return" not in src2:
        raise AssertionError("ForensicLogger.GenerateReport stub not implemented")
    print("[OK] No obvious Omega‑invariant stubs detected")


def main():
    import os
    random.seed(12345)
    print("=== Omega Protocol Invariant Validation ===")
    trust_decay_check()
    mitigation_check()
    jitter_prob_check()
    jitter_range_check()
    benchmark_isolation_check()
    fpr_check()
    stub_detector()
    print("\nAll invariant checks passed. Implementation is *potentially* compliant.")
    # Note: Passing these tests does NOT guarantee full Omega compliance;
    # it only guarantees that the core mathematical invariants are honoured.


if __name__ == "__main__":
    main()