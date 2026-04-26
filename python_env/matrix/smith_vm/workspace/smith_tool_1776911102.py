# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Invariant Validator for AFDS v3.0 (Trust, Jitter, Topology, Φ‑density)
Run: python3 validate_afds.py
"""

import math
import random
import sys
from collections import defaultdict
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# Helper random utilities
# ----------------------------------------------------------------------
def rand_pid() -> int:
    return random.randint(100, 9999)

def rand_path() -> str:
    depth = random.randint(0, 5)
    parts = [""] + ["dir" + str(random.randint(0, 9)) for _ in range(depth)]
    return "/".join(parts)

# ----------------------------------------------------------------------
# 1. TrustManager (core equations)
# ----------------------------------------------------------------------
class TrustState:
    __slots__ = ("pid", "trust_score", "last_access", "accessed_paths",
                 "cumulative_stability")
    def __init__(self, pid: int):
        self.pid = pid
        self.trust_score = 0.0
        self.last_access = 0.0          # seconds since epoch (float)
        self.accessed_paths = set()
        self.cumulative_stability = 0.0

class TrustManager:
    def __init__(self):
        self.states: Dict[int, TrustState] = {}

    def _get_state(self, pid: int) -> TrustState:
        if pid not in self.states:
            self.states[pid] = TrustState(pid)
        return self.states[pid]

    def update_trust(self, pid: int, path: str, access_success: bool, now: float):
        state = self._get_state(pid)
        is_novel = path not in state.accessed_paths
        novelty_penalty = 0.05 if is_novel else 0.0

        # time decay (hours)
        delta_h = (now - state.last_access) / 3600.0
        state.trust_score *= math.exp(-math.log(0.95) * delta_h)
        state.trust_score = max(state.trust_score - novelty_penalty, 0.0)

        if not is_novel:
            # stability contribution
            state.cumulative_stability += math.exp(-delta_h)
            state.trust_score += 0.01 * math.exp(-0.1 * state.cumulative_stability)

        # clamp
        state.trust_score = min(max(state.trust_score, 0.0), 1.0)
        state.accessed_paths.add(path)
        state.last_access = now

    def get_trust_mitigation(self, pid: int) -> float:
        state = self.states.get(pid)
        if state is None:
            return 1.0          # no mitigation (i.e., 0 % reduction)
        return 0.8 * state.trust_score

    def newtonian_trust_baseline(self, pid: int) -> float:
        state = self.states.get(pid)
        if state is None:
            return 0.1
        stability_integral = state.cumulative_stability * math.exp(-0.1 * len(state.accessed_paths))
        noise_entropy = math.log(len(state.accessed_paths) + 1e-10)
        return math.exp(-0.01 * noise_entropy) * stability_integral

    def psi_coupling(self, pid: int) -> float:
        phi_n = self.newtonian_trust_baseline(pid)
        return math.log(max(phi_n, 1e-10))

# ----------------------------------------------------------------------
# 2. Topology Metrics
# ----------------------------------------------------------------------
class TopologyMetrics:
    def __init__(self):
        self.unique_paths = set()
        self.max_depth = 0
        self.depth_histogram = defaultdict(int)
        self.traversal_entropy = 0.0

    def update(self, path: str):
        self.unique_paths.add(path)
        depth = path.count('/')
        if depth > self.max_depth:
            self.max_depth = depth
        self.depth_histogram[depth] += 1
        self.traversal_entropy += math.log(depth + 1) * 0.01

    def traversal_score(self) -> float:
        return 0.6 * len(self.unique_paths) + 0.4 * self.max_depth

    def asymmetric_threat(self) -> float:
        b = len(self.unique_paths)
        d = self.max_depth
        return math.tanh(b * d / (b + d + 1e-10))

# ----------------------------------------------------------------------
# 3. Jitter Application
# ----------------------------------------------------------------------
def apply_adaptive_jitter(raw_score: float, mitigation: float, phi_delta: float) -> int:
    """Return jitter in ms (0 means no jitter)."""
    prob = (raw_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_delta)
    prob = max(0.0, min(1.0, prob))
    if phi_delta > 0.95:
        return 1000          # hard stop
    if random.random() < prob:
        return 1 + int(50.0 * random.random())  # [1,50] ms
    return 0

# ----------------------------------------------------------------------
# 4. Forensic Logger (impedance)
# ----------------------------------------------------------------------
class ForensicLogger:
    def __init__(self):
        self.entries = []  # list of dicts

    def log(self, entry: dict):
        self.entries.append(entry)

    def topological_impedance(self) -> float:
        imp = 0.0
        for e in self.entries:
            imp += e["trust_score"] * abs(e["phi_delta"])
        return imp * 0.01

# ----------------------------------------------------------------------
# 5. Φ‑Density (as given in the source)
# ----------------------------------------------------------------------
K_BOLTZMANN = 1.0
def phi_density(raw_gain: float = 0.85, audit_complexity: float = 2.5) -> float:
    audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
    return raw_gain - audit_entropy

TARGET_PHIDENSITY = 0.75   # claimed net Φ after audit subtraction
EPS = 1e-9

# ----------------------------------------------------------------------
# Property‑based validation
# ----------------------------------------------------------------------
def run_validation(iterations: int = 5000):
    tm = TrustManager()
    topo = TopologyMetrics()
    flog = ForensicLogger()
    now_base = 1000000.0  # arbitrary start time

    for i in range(iterations):
        pid = rand_pid()
        path = rand_path()
        now = now_base + i * 0.5  # advance time slightly each step
        success = random.random() > 0.2

        # ---- Trust update ----
        tm.update_trust(pid, path, success, now)
        state = tm.states[pid]
        # Trust bounds
        assert 0.0 <= state.trust_score <= 1.0, f"Trust OOB: {state.trust_score}"
        # Mitigation bounds
        mit = tm.get_trust_mitigation(pid)
        assert 0.0 <= mit <= 0.8, f"Mit OOB: {mit}"
        # Newtonian trust baseline non‑negative
        phi_n = tm.newtonian_trust_baseline(pid)
        assert phi_n >= 0.0, f"φ_N negative: {phi_n}"
        # Psi coupling real
        psi = tm.psi_coupling(pid)
        assert isinstance(psi, float) and not math.isnan(psi), f"ψ invalid: {psi}"

        # ---- Topology update ----
        topo.update(path)
        # metrics monotonic
        assert topo.traversal_entropy >= 0.0
        assert len(topo.unique_paths) >= 0
        assert topo.max_depth >= 0
        # traversal score non‑negative
        ts = topo.traversal_score()
        assert ts >= 0.0
        # asymmetric threat in [0,1)
        phi_d = topo.asymmetric_threat()
        assert 0.0 <= phi_d < 1.0, f"φ_Δ out of range: {phi_d}"

        # ---- Jitter ----
        jitter_ms = apply_adaptive_jitter(ts, mit, phi_d)
        if phi_d > 0.95:
            assert jitter_ms == 1000, "Hard‑stop jitter mismatch"
        else:
            assert 0 <= jitter_ms <= 50, f"Jitter OOB: {jitter_ms}"

        # ---- Forensic log ----
        entry = {
            "timestamp": now,
            "pid": pid,
            "operation": "lookup",
            "path": path,
            "applied_latency_ms": jitter_ms,
            "traversal_score": ts,
            "trust_score": mit,
            "inter_call_interval": 0.0,  # simplified
            "phi_delta": phi_d,
        }
        flog.log(entry)
        # impedance non‑negative
        assert flog.topological_impedance() >= 0.0

        # ---- Trigger condition (honey node or high score) ----
        # we simulate a honey node by marking a specific path
        if path == "/honey" or ts > 90.0:
            # just ensure logging happened; report generation is external
            pass

    # ---- Φ‑density check ----
    computed = phi_density()
    if abs(computed - TARGET_PHIDENSITY) > EPS:
        print(f"[FAIL] Φ‑density mismatch: computed={computed:.6f}, target={TARGET_PHIDENSITY:.6f}")
        sys.exit(1)
    else:
        print(f"[PASS] Φ‑density matches target: {computed:.6f}")

    print("[PASS] All invariants held over", iterations, "iterations.")

if __name__ == "__main__":
    run_validation()