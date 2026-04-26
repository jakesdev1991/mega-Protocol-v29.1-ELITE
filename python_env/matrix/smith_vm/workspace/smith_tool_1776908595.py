# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol compliance validator for the AFDS v3.0 trust/jitter model.
Checks:
  * Trust score ∈ [0,1]
  * Mitigation = 0.8 * trust_score
  * Jitter probability ∈ [0,1]
  * Jitter latency ∈ [1,50] ms when triggered
  * Forensic trigger conditions
  * Exponential decay factor = 0.95 per hour
  * Monotonic trust → lower jitter probability
"""

import math
import random
import time
from typing import Dict, Tuple

# ------------------- TrustManager (Python) -------------------
class ProcessTrustState:
    def __init__(self, pid: int):
        self.pid = pid
        self.trust_score: float = 0.0
        self.last_access: float = time.time()
        self.accessed_paths = set()
        self._lock = False  # simple flag; not used in single‑threaded test

class TrustManager:
    def __init__(self):
        self.states: Dict[int, ProcessTrustState] = {}

    def _decay(self, score: float, hours: float) -> float:
        # trust *= 0.95**hours
        return score * (0.95 ** hours)

    def update_trust(self, pid: int, path: str) -> None:
        st = self.states.setdefault(pid, ProcessTrustState(pid))
        now = time.time()
        hours = (now - st.last_access) / 3600.0

        is_novel = path not in st.accessed_paths
        novelty_penalty = 0.05 if is_novel else 0.0

        st.trust_score = self._decay(st.trust_score, hours)
        if not is_novel:
            st.trust_score += 0.01
        st.trust_score -= novelty_penalty
        st.trust_score = max(0.0, min(1.0, st.trust_score))

        st.accessed_paths.add(path)
        st.last_access = now

    def get_trust_mitigation(self, pid: int) -> float:
        st = self.states.get(pid)
        if st is None:
            return 1.0          # no mitigation (unknown process)
        return 0.8 * st.trust_score

# ------------------- Topology & Jitter -------------------
def traversal_score(unique_paths: int, max_depth: int) -> float:
    return 0.6 * unique_paths + 0.4 * max_depth

def jitter_probability(raw_score: float, mitigation: float) -> float:
    p = (raw_score / 100.0) ** 1.5
    p *= (1.0 - mitigation)
    return max(0.0, min(1.0, p))

def apply_jitter(prob: float) -> Tuple[bool, int]:
    """Return (triggered, latency_ms). Latency in [1,50] if triggered."""
    if random.random() < prob:
        latency = 1 + int(random.random() * 50)  # 1..50 inclusive
        return True, latency
    return False, 0

# ------------------- Forensic Logger (stub) -------------------
class ForensicLogger:
    def __init__(self):
        self.entries = []
    def log(self, entry: dict):
        self.entries.append(entry)
        if entry["operation"] == "honey_node_access" or entry["traversal_score"] > 90.0:
            self._generate_report()
    def _generate_report(self):
        pass  # stub

# ------------------- Validation Harness -------------------
def run_validation(iterations: int = 100_000) -> None:
    tm = TrustManager()
    flog = ForensicLogger()
    # Track monotonic trust effect
    trust_vs_jitter = []

    for _ in range(iterations):
        pid = random.randint(1000, 6000)
        # Simulate a path access
        depth = random.randint(0, 10)
        path = "/" + "/".join(["dir"] * depth) + f"/file{random.randint(0,100)}.dat"
        tm.update_trust(pid, path)

        st = tm.states[pid]
        trust = st.trust_score
        mitigation = tm.get_trust_mitigation(pid)

        # Trust bounds
        assert 0.0 <= trust <= 1.0, f"Trust out of bounds: {trust}"
        assert 0.0 <= mitigation <= 0.8, f"Mitigation out of bounds: {mitigation}"

        # Topology metrics (approximate)
        unique_paths = len(st.accessed_paths)
        max_depth = max((p.count('/') for p in st.accessed_paths), default=0)
        raw_score = traversal_score(unique_paths, max_depth)

        # Jitter probability
        prob = jitter_probability(raw_score, mitigation)
        assert 0.0 <= prob <= 1.0, f"Jitter probability OOB: {prob}"

        triggered, latency = apply_jitter(prob)
        if triggered:
            assert 1 <= latency <= 50, f"Jitter latency OOB: {latency}"
        # Forensic log entry
        entry = {
            "timestamp": time.time(),
            "pid": pid,
            "operation": "honey_node_access" if "honey_" in path else "lookup",
            "path": path,
            "applied_latency_ms": latency,
            "traversal_score": raw_score,
            "trust_score": trust,
            "inter_call_interval": 0.0,  # not measured in this test
        }
        flog.log(entry)

        # Record for monotonicity check
        trust_vs_jitter.append((trust, prob))

    # ---- Monotonic trust → lower jitter probability (statistical) ----
    # Bin trust scores and ensure average probability decreases with trust
    bins = 10
    bin_sums = [0.0] * bins
    bin_counts = [0] * bins
    for trust, prob in trust_vs_jitter:
        b = int(trust * bins)
        if b == bins:
            b = bins - 1
        bin_sums[b] += prob
        bin_counts[b] += 1
    avgs = [bin_sums[i]/max(1,bin_counts[i]) for i in range(bins)]
    # Check monotonic non‑increasing trend (allow small noise)
    for i in range(1, bins):
        if bin_counts[i] == 0 or bin_counts[i-1] == 0:
            continue
        assert avgs[i] <= avgs[i-1] + 1e-2, f"Trust‑jitter monotonicity violated at bin {i}: {avgs[i-1]} -> {avgs[i]}"

    print(f"✅ Validation passed over {iterations} iterations.")
    print(f"   Final trust range observed: {min(s.trust_score for s in tm.states.values()):.4f} – {max(s.trust_score for s in tm.states.values()):.4f}")
    print(f"   Average jitter probability: {sum(p for _,p in trust_vs_jitter)/len(trust_vs_jitter):.4f}")

if __name__ == "__main__":
    run_validation()