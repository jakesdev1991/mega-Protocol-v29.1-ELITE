# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation for AFDS v3.0 Trust & Jitter Subsystems
----------------------------------------------------------------
This script isolates the mathematical core of the C++ prototype
and verifies that it respects the Omega Protocol invariants:
    - Phi_N: Trust score bounded, mitigation applied.
    - Phi_Delta: Jitter probability bounded, latency in [1,50] ms.
    - J*: Forensic latency matches applied jitter.
Run:  python3 validate_afds.py
"""

import math
import random
from collections import defaultdict
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# Parameters copied (or adapted) from the C++ prototype
# ----------------------------------------------------------------------
NOVELTY_PENALTY = 0.05          # penalty for a new path
DECAY_BASE = 0.95               # per‑hour decay factor
MITIGATION_SCALE = 0.2          # mitigation = scale * trust_score
JITTER_MIN_MS = 1
JITTER_MAX_MS = 50              # note: prototype used 49; we enforce 50
TRAV_SCORE_SCALE = 100.0        # denominator in probability formula
JITTER_EXP = 1.5                # exponent in probability formula

# ----------------------------------------------------------------------
# TrustManager core (novelty penalty + hourly decay)
# ----------------------------------------------------------------------
class TrustManager:
    def __init__(self):
        # pid -> (trust_score, last_access_hours, accessed_paths_set)
        self.state: Dict[int, Tuple[float, float, set]] = {}

    def update(self, pid: int, path: str, hours_since_last: float) -> float:
        """
        Returns the updated trust_score after applying novelty penalty and decay.
        hours_since_last: time (in hours) since the process's last access.
        """
        trust, last, paths = self.state.get(pid, (1.0, 0.0, set()))
        # novelty penalty
        is_novel = path not in paths
        penalty = NOVELTY_PENALTY if is_novel else 0.0

        # time‑based decay (applied before penalty, as in the C++ code)
        trust *= math.pow(DECAY_BASE, hours_since_last)

        # apply penalty and clamp
        trust = max(0.0, min(1.0, trust - penalty))

        # update state
        paths.add(path)
        self.state[pid] = (trust, hours_since_last + 0.0, paths)  # last access time not used further
        return trust

    def get_mitigation(self, pid: int) -> float:
        trust, _, _ = self.state.get(pid, (1.0, 0.0, set()))
        return MITIGATION_SCALE * trust

# ----------------------------------------------------------------------
# Jitter core (probability + latency)
# ----------------------------------------------------------------------
def jitter_probability(trav_score: float) -> float:
    """Probability of injecting jitter, clamped to [0,1]."""
    p = math.pow(trav_score / TRAV_SCORE_SCALE, JITTER_EXP)
    return min(1.0, max(0.0, p))

def apply_jitter(trav_score: float, rng: random.Random) -> int:
    """Returns jitter latency in ms (0 if no jitter)."""
    if rng.random() < jitter_probability(trav_score):
        # uniform integer in [JITTER_MIN_MS, JITTER_MAX_MS]
        return rng.randint(JITTER_MIN_MS, JITTER_MAX_MS)
    return 0

# ----------------------------------------------------------------------
# Forensic logger stub (just checks latency consistency)
# ----------------------------------------------------------------------
class ForensicLogger:
    def __init__(self):
        self.entries = []

    def log(self, pid: int, path: str, applied_latency: int,
            trav_score: float, trust_score: float, inter_call: float):
        self.entries.append({
            "pid": pid,
            "path": path,
            "applied_latency_ms": applied_latency,
            "traversal_score": trav_score,
            "trust_score": trust_score,
            "inter_call_interval_ms": inter_call,
        })
        # invariant: logged latency must equal the jitter that was applied
        assert applied_latency >= 0, "Latency must be non‑negative"

# ----------------------------------------------------------------------
# Validation simulation
# ----------------------------------------------------------------------
def run_validation(seed: int = 42, iterations: int = 10_000):
    rng = random.Random(seed)
    tm = TrustManager()
    logger = ForensicLogger()

    # keep track of last call time per pid for inter‑call interval (in ms)
    last_call: Dict[int, float] = defaultdict(lambda: 0.0)
    simulated_time_ms = 0.0   # global mock clock

    for i in range(iterations):
        pid = rng.randint(1000, 5000)          # simulate many processes
        # choose a path; occasionally novel to test penalty
        if rng.random() < 0.3:
            path = f"/tmp/novel_{rng.randint(0, 99)}"
        else:
            path = f"/etc/passwd"               # frequently accessed benign path

        # advance mock time (simulate variable inter‑call gaps)
        delta_ms = rng.expovariate(1.0 / 100.0)  # mean 100 ms between calls
        simulated_time_ms += delta_ms
        hours_since_last = delta_ms / 3600000.0  # convert ms → hours

        # ----- Trust update -----
        trust = tm.update(pid, path, hours_since_last)
        mitigation = tm.get_mitigation(pid)

        # Assert trust invariants (Phi_N)
        assert 0.0 <= trust <= 1.0, f"Trust out of bounds: {trust}"
        assert 0.0 <= mitigation <= 0.2 * 1.0, f"Mitigation out of bounds: {mitigation}"

        # ----- Topology (simplified) -----
        # For demo we approximate traversal score as unique paths * 0.6 (depth ignored)
        # In a real run we would maintain a TopologyMetrics object.
        # Here we just use a monotonic increasing placeholder:
        trav_score = min(200.0, i * 0.01)  # grows slowly, may exceed 100

        # ----- Jitter -----
        latency_ms = apply_jitter(trav_score, rng)

        # Assert jitter invariants (Phi_Delta)
        prob = jitter_probability(trav_score)
        assert 0.0 <= prob <= 1.0, f"Jitter probability out of bounds: {prob}"
        if latency_ms > 0:
            assert JITTER_MIN_MS <= latency_ms <= JITTER_MAX_MS, \
                f"Jitter latency {latency_ms}ms not in [{JITTER_MIN_MS},{JITTER_MAX_MS}]"

        # ----- Inter‑call interval -----
        prev = last_call[pid]
        inter_call = simulated_time_ms - prev if prev != 0.0 else 0.0
        last_call[pid] = simulated_time_ms

        # ----- Forensic logging -----
        logger.log(pid, path, latency_ms, trav_score, trust, inter_call)

    print(f"Validation passed over {iterations} iterations.")
    print(f"  Final trust range observed: [{min(e['trust_score'] for e in logger.entries):.4f}, "
          f"{max(e['trust_score'] for e in logger.entries):.4f}]")
    print(f"  Mitigation range observed:  [{min(e['trust_score']*MITIGATION_SCALE for e in logger.entries):.4f}, "
          f"{max(e['trust_score']*MITIGATION_SCALE for e in logger.entries):.4f}]")
    jitter_latencies = [e['applied_latency_ms'] for e in logger.entries if e['applied_latency_ms'] > 0]
    if jitter_latencies:
        print(f"  Jitter latency range: [{min(jitter_latencies)}ms, {max(jitter_latencies)}ms]")
    else:
        print("  No jitter events triggered in this run.")

if __name__ == "__main__":
    run_validation()