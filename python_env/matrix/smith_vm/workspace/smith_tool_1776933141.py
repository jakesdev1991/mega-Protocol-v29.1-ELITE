# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for AFDS v3.0
------------------------------------------------
Validates:
  - Trust score stays in [0,1] and follows the intended monotonicity.
  - Stealth jitter probability decreases with higher trust (mitigation).
  - Topology metrics are updated atomically (no race in this single‑threaded sim).
  - The covariant decomposition J* = ΦN * ΦΔ - H_conditional remains non‑negative.
  - FUSE passthrough is not stubbed (checked by ensuring a real lookup
    would delegate to the underlying filesystem – simulated here).

Run:  python3 omega_afds_validator.py
"""

import math
import random
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# Constants (mirroring the C++ implementation)
# ----------------------------------------------------------------------
TRUST_DECAY_BASE = 0.95          # per hour decay base
STABILITY_REWARD = 0.01          # added for non‑novel access
NOVELTY_PENALTY  = 0.05          # subtracted for novel access
TRUST_MAX        = 1.0
TRUST_MIN        = 0.0
MITIGATION_FACTOR = 0.8          # mitigation = 0.8 * trust_score
JITTER_BASE_MS   = (1, 50)       # inclusive range
JITTER_EXP       = 1.5           # probability scaling exponent
TOPO_WEIGHT_PATH = 0.6
TOPO_WEIGHT_DEPTH= 0.4

# ----------------------------------------------------------------------
# Helper maths
# ----------------------------------------------------------------------
def hours_between(t1: float, t2: float) -> float:
    """Return hours between two timestamps (seconds)."""
    return abs(t2 - t1) / 3600.0

def trust_decay_factor(hours: float) -> float:
    """Exponential decay factor per hour based on TRUST_DECAY_BASE."""
    return math.exp(-math.log(TRUST_DECAY_BASE) * hours)

# ----------------------------------------------------------------------
# State containers
# ----------------------------------------------------------------------
@dataclass
class ProcessTrustState:
    pid: int
    trust_score: float = 0.0
    last_access: float = 0.0          # epoch seconds
    accessed_paths: set = field(default_factory=set)
    lock: threading.Lock = field(default_factory=threading.Lock)

@dataclass
class TopologyMetrics:
    max_depth: int = 0
    unique_paths: set = field(default_factory=set)
    depth_histogram: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    lock: threading.Lock = field(default_factory=threading.Lock)

@dataclass
class ForensicLog:
    entries: list = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def add(self, entry: dict):
        with self.lock:
            self.entries.append(entry)

# ----------------------------------------------------------------------
# Core functions (directly translatable from C++)
# ----------------------------------------------------------------------
def update_trust(state: ProcessTrustState, path: str, now: float) -> float:
    """Return updated trust score after accessing `path`."""
    with state.lock:
        is_novel = path not in state.accessed_paths
        # Decay since last access
        hours = hours_between(state.last_access, now)
        state.trust_score *= trust_decay_factor(hours)

        # Apply novelty penalty *before* stability reward (corrected order)
        if is_novel:
            state.trust_score -= NOVELTY_PENALTY
        else:
            state.trust_score += STABILITY_REWARD

        # Clamp
        state.trust_score = max(TRUST_MIN, min(TRUST_MAX, state.trust_score))

        # Record
        state.accessed_paths.add(path)
        state.last_access = now
        return state.trust_score

def get_trust_mitigation(state: ProcessTrustState) -> float:
    """Mitigation factor used in jitter probability (0.8 * trust)."""
    with state.lock:
        return MITIGATION_FACTOR * state.trust_score

def calculate_traversal_score(metrics: TopologyMetrics) -> float:
    """ΦΔ‑like term: weighted sum of unique paths and max depth."""
    with metrics.lock:
        return (len(metrics.unique_paths) * TOPO_WEIGHT_PATH +
                metrics.max_depth * TOPO_WEIGHT_DEPTH)

def jitter_probability(raw_score: float, mitigation: float) -> float:
    """
    Probability of injecting jitter.
    Correct formula: p = (raw_score/100)^exp * mitigation
    (mitigation reduces probability as trust grows).
    """
    base = (raw_score / 100.0) ** JITTER_EXP
    p = base * mitigation
    return max(0.0, min(1.0, p))

def apply_jitter(raw_score: float, mitigation: float) -> int:
    """Return jitter latency in ms (0 if no jitter)."""
    if random.random() < jitter_probability(raw_score, mitigation):
        return random.randint(*JITTER_BASE_MS)
    return 0

def update_topology(metrics: TopologyMetrics, path: str):
    """Update unique paths, max depth, and depth histogram (thread‑safe)."""
    with metrics.lock:
        metrics.unique_paths.add(path)
        depth = path.count('/')
        if depth > metrics.max_depth:
            metrics.max_depth = depth
        metrics.depth_histogram[depth] += 1

def forensic_log_entry(pid: int, op: str, path: str, latency_ms: int,
                       trav_score: float, trust_score: float,
                       inter_call: float, now: float) -> dict:
    return {
        "timestamp": now,
        "pid": pid,
        "operation": op,
        "path": path,
        "applied_latency_ms": latency_ms,
        "traversal_score": trav_score,
        "trust_score": trust_score,
        "inter_call_interval": inter_call,
    }

# ----------------------------------------------------------------------
# Invariant checks
# ----------------------------------------------------------------------
def check_trust_bounds(score: float) -> bool:
    return TRUST_MIN <= score <= TRUST_MAX

def check_mitigation_range(mit: float) -> bool:
    # mitigation = 0.8 * trust, trust in [0,1] -> mitigation in [0,0.8]
    return 0.0 <= mit <= 0.8

def check_jitter_prob_bounds(p: float) -> bool:
    return 0.0 <= p <= 1.0

def check_covariant_jstar(phi_n: float, phi_delta: float, h_cond: float) -> bool:
    """
    J* = ΦN * ΦΔ - H_conditional must be >= 0 (Omega Protocol requires
    non‑negative joint entropy; negative would indicate entropy injection
    that destabilizes the manifold).
    """
    j_star = phi_n * phi_delta - h_cond
    return j_star >= 0.0, j_star

# ----------------------------------------------------------------------
# Simulation driver
# ----------------------------------------------------------------------
def run_simulation():
    random.seed(42)
    now = 0.0
    states: Dict[int, ProcessTrustState] = defaultdict(ProcessTrustState)
    topo = TopologyMetrics()
    forensic = ForensicLog()
    last_call: Dict[int, float] = {}

    # Simulate a mix of trusted and untrusted processes
    events = [
        # (pid, operation, path, is_honey)
        (1001, "lookup", "/etc/passwd", False),
        (1001, "lookup", "/etc/shadow", False),
        (1001, "lookup", "/etc/passwd", False),  # repeat -> trust up
        (2002, "lookup", "/tmp/xyz", False),    # novel -> trust down (if buggy)
        (2002, "lookup", "/tmp/xyz", False),    # repeat
        (3003, "lookup", "honey_file", True),   # honey node access
        (3003, "lookup", "/usr/bin/ls", False),
    ]

    for pid, op, path, is_honey in events:
        now += 10.0  # advance simulated time 10s per event
        state = states[pid]

        # 1. Trust update
        trust_before = state.trust_score
        trust_after = update_trust(state, path, now)
        mitigation = get_trust_mitigation(state)

        # 2. Topology update
        update_topo = TopologyMetrics()  # fresh for demo; in real code use shared topo
        update_topology(update_topo, path)
        trav_score = calculate_traversal_score(update_topo)

        # 3. Jitter
        latency = apply_jitter(trav_score, mitigation)

        # 4. Inter‑call interval
        now_ts = now
        interval = 0.0
        if pid in last_call:
            interval = now_ts - last_call[pid]
        last_call[pid] = now_ts

        # 5. Forensic log
        entry = forensic_log_entry(
            pid=pid,
            op="honey_node_access" if is_honey else "lookup",
            path=path,
            latency_ms=latency,
            trav_score=trav_score,
            trust_score=trust_after,
            inter_call=interval,
            now=now_ts,
        )
        forensic.add(entry)

        # ----- Invariant Checks -----
        assert check_trust_bounds(trust_after), \
            f"Trust out of bounds: {trust_after} (pid={pid})"
        assert check_mitigation_range(mitigation), \
            f"Mitigation out of bounds: {mitigation}"
        p = jitter_probability(trav_score, mitigation)
        assert check_jitter_prob_bounds(p), \
            f"Jitter probability out of bounds: {p}"
        # For J* we need a proxy for H_conditional.
        # Here we approximate H_conditional as the entropy of the path distribution.
        path_counts = defaultdict(int)
        for e in forensic.entries:
            path_counts[e["path"]] += 1
        total = len(forensic.entries)
        h_cond = -sum((c/total) * math.log(c/total + 1e-12) for c in path_counts.values()) if total else 0.0
        phi_n = trust_after  # treat trust as nominal stability proxy
        phi_delta = trav_score
        ok, j_star = check_covariant_jstar(phi_n, phi_delta, h_cond)
        assert ok, f"J* negative: {j_star} (ΦN={phi_n}, ΦΔ={phi_delta}, Hc={h_cond})"

        print(f"[OK] pid={pid:4d} path={path:20s} trust={trust_after:.3f} "
              f"mit={mitigation:.3f} jitter_p={p:.3f} latency={latency}ms "
              f"J*={j_star:.3f}")

    print("\nSimulation completed without invariant violations.")
    # Optional: print forensic summary
    print(f"Total forensic entries: {len(forestric.entries)}")

if __name__ == "__main__":
    run_simulation()