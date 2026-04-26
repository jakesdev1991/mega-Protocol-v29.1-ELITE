# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import time, random, math
from collections import defaultdict

# ──────────────────────────────────────────────────────────────────────────────
# 1. Simulated AFDS Trust Model (flawed hourly decay)
# ──────────────────────────────────────────────────────────────────────────────
class ProcessTrustState:
    def __init__(self, pid):
        self.pid = pid
        self.trust_score = 0.0
        self.accessed_paths = set()
        self.last_access = time.time()

class TrustManager:
    def __init__(self):
        self.states = {}

    def update(self, pid, path):
        if pid not in self.states:
            self.states[pid] = ProcessTrustState(pid)
        s = self.states[pid]

        # Flaw: decay only per *full hour*
        now = time.time()
        hours = int((now - s.last_access) // 3600)
        s.trust_score *= (0.95 ** hours)

        # Reward stability, penalize novelty
        novelty = 0.05 if path not in s.accessed_paths else 0.0
        if not novelty:
            s.trust_score += 0.01
        s.trust_score = max(0.0, min(1.0, s.trust_score - novelty))

        s.accessed_paths.add(path)
        s.last_access = now

    def mitigation(self, pid):
        return 0.8 * self.states[pid].trust_score if pid in self.states else 1.0

# ──────────────────────────────────────────────────────────────────────────────
# 2. Simulate attacker farming trust on a single file
# ──────────────────────────────────────────────────────────────────────────────
tm = TrustManager()
attacker_pid = 666

print("=== Trust Farming Demo (same path, 100 accesses) ===")
for i in range(100):
    tm.update(attacker_pid, "/etc/passwd")
    if i % 10 == 0:
        print(f"Access #{i}: trust={tm.states[attacker_pid].trust_score:.3f}, "
              f"mitigation={tm.mitigation(attacker_pid):.3f}")

# Now attacker scans honey nodes with 80 % less jitter
raw_score = 50  # moderate traversal score
jitter_prob = (raw_score / 100) ** 1.5 * (1 - tm.mitigation(attacker_pid))
print(f"\nHoney‑node scan: raw_score={raw_score}, effective jitter prob={jitter_prob:.3%} "
      f"(vs 100% for untrusted)")

# ──────────────────────────────────────────────────────────────────────────────
# 3. Benchmark Contamination Demo
# ──────────────────────────────────────────────────────────────────────────────
class TopologyMetrics:
    def __init__(self):
        self.unique_paths = set()
        self.max_depth = 0

def run_contaminated_benchmark():
    tm = TrustManager()
    metrics = TopologyMetrics()

    # Baseline phase: populate 1000 unique paths
    for i in range(1000):
        p = f"/test{i}"
        metrics.unique_paths.add(p)
        metrics.max_depth = max(metrics.max_depth, p.count('/'))

    # AFDS phase: re‑use the same (now bloated) metrics
    total_jitter_ms = 0
    for i in range(1000):
        p = f"/test{i}"
        raw = (len(metrics.unique_paths) * 0.6) + (metrics.max_depth * 0.4)
        # untrusted mitigation = 1.0
        prob = min(1.0, (raw / 100) ** 1.5)
        if random.random() < prob:
            total_jitter_ms += random.randint(1, 50)

    return total_jitter_ms

contaminated_latency = run_contaminated_benchmark()
print(f"\n=== Benchmark Contamination ===")
print(f"Measured jitter latency: {contaminated_latency} ms "
      f"(artifact of polluted state, not real AFDS overhead)")

# ──────────────────────────────────────────────────────────────────────────────
# 4. PID Reuse Trust Inheritance (conceptual)
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== PID Reuse Exploit ===")
# Process 1234 builds trust, then exits
tm.update(1234, "/foo")
tm.update(1234, "/foo")
print(f"Process 1234 trust before exit: {tm.states[1234].trust_score:.3f}")
# PID 1234 is reused by a new process
# New process inherits the same trust state (no exit cleanup)
print(f"New process reusing PID 1234 inherits trust: {tm.states[1234].trust_score:.3f}")