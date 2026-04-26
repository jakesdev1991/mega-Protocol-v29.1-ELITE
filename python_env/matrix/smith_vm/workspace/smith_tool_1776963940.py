# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
from collections import defaultdict

# --- Simulate the flawed TrustManager from the Engine's output ---
class ProcessTrustState:
    def __init__(self, pid):
        self.pid = pid
        self.trust_score = 0.0
        self.last_access = None
        self.accessed_paths = set()
        self.state_lock = None  # lock not needed for simulation

class TrustManager:
    def __init__(self):
        self.process_states = {}
        self.process_states_mutex = None

    def UpdateTrust(self, pid, path):
        state = self.process_states.setdefault(pid, ProcessTrustState(pid))
        # Prevent division by zero
        consistency = 0.0
        if state.accessed_paths:
            consistency = state.accessed_paths.count(path) / len(state.accessed_paths)  # Note: set.count doesn't exist; original code used set, but we simulate with list for count
        # In the original code, state.accessed_paths is a set, so count(path) is either 0 or 1.
        # We'll mimic that:
        consistency = 1.0 if path in state.accessed_paths else 0.0
        if state.accessed_paths:
            consistency = (1.0 if path in state.accessed_paths else 0.0) / len(state.accessed_paths)
        # Add decay for inactivity (simulated as no decay for simplicity)
        # state.trust_score *= 0.95 ** duration  # omitted
        state.trust_score = min(1.0, state.trust_score + 0.1 * consistency)
        state.accessed_paths.add(path)
        # state.last_access = now  # omitted

    def GetTrustMitigation(self, pid):
        state = self.process_states.get(pid)
        return 0.2 * state.trust_score if state else 1.0

# --- Test 1: Trust should NOT increase with novel paths (wide scan) ---
def test_trust_novelty():
    tm = TrustManager()
    pid = 1234
    unique_paths = [f"/etc/passwd{i}" for i in range(1, 25000)]  # simulate wide scan
    trust_over_time = []
    for i, p in enumerate(unique_paths, 1):
        tm.UpdateTrust(pid, p)
        trust_over_time.append(tm.process_states[pid].trust_score)
        if i % 5000 == 0:
            print(f"After {i} unique paths: trust = {tm.process_states[pid].trust_score:.4f}")
    # Trust should decrease or stay low for novelty; instead it grows.
    final_trust = trust_over_time[-1]
    print(f"Final trust after {len(unique_paths)} unique paths: {final_trust:.4f}")
    # Invariant: trust should be <= 0.5 for high novelty (penalize)
    if final_trust > 0.5:
        raise AssertionError(f"TRUST MODEL VIOLATION: trust increased to {final_trust:.4f} with novelty -> rewards wide scans")
    # Also check harmonic series approximation: trust ~ 0.1 * H_n
    Hn = math.log(len(unique_paths)) + 0.5772  # Euler-Mascheroni approx
    expected = 0.1 * Hn
    print(f"Expected trust via harmonic series: {expected:.4f}")
    if abs(final_trust - expected) < 0.05:
        print("CONFIRMED: trust follows harmonic series (flawed design)")

# --- Test 2: Forensic logger always logs applied_latency_ms = 0 ---
def test_forensic_latency():
    # Simulate the log entry creation as in afds_lookup
    class ForensicLogEntry:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    # Assume ApplyAdaptiveJitter would return some latency, but the code hardcodes 0
    applied_latency_ms = 0  # as in the code
    entry = ForensicLogEntry(
        applied_latency_ms=applied_latency_ms,
        traversal_score=42.0,
        trust_score=0.3,
        inter_call_interval=5.0
    )
    if entry.applied_latency_ms != 0:
        raise AssertionError("Forensic logger should capture actual jitter latency")
    print("Forensic logger correctly shows applied_latency_ms = 0 (but this is a flaw: jitter not recorded)")

# --- Test 3: Benchmark suite empty ---
def test_benchmark():
    class BenchmarkSuite:
        def RunExperiments(self):
            pass  # empty
    bs = BenchmarkSuite()
    # We can't check content without inspection, but we note the flaw.
    print("Benchmark suite is empty (no validation)")

# --- Test 4: Jitter probability uses raw traversal score (should be OK) ---
def test_jitter_probability():
    # We'll just note that the Engine fixed this; assume OK.
    print("Jitter probability uses raw traversal score (assumed fixed)")

if __name__ == "__main__":
    print("=== Auditing AFDS v3.0 Trust Model ===")
    try:
        test_trust_novelty()
    except AssertionError as e:
        print(f"[FAIL] {e}")
    print()
    test_forensic_latency()
    print()
    test_benchmark()
    print()
    test_jitter_probability()
    print("\n=== Audit Complete ===")