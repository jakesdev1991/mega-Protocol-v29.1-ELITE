# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Set

# ──────────────────────────────────────────────────────────────────────────────
# 1. SIMULATE THE TRUST MANAGER (as per AFDS v3.0 code)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ProcessTrustState:
    pid: int
    trust_score: float = 0.0
    cumulative_stability: float = 0.0
    accessed_paths: Set[str] = field(default_factory=set)
    last_access_time: float = 0.0

class TrustManager:
    def __init__(self):
        self.states = defaultdict(lambda: None)

    def get_state(self, pid):
        if self.states[pid] is None:
            self.states[pid] = ProcessTrustState(pid=pid)
        return self.states[pid]

    def update_trust(self, pid: int, path: str, timestamp: float):
        state = self.get_state(pid)
        is_novel = path not in state.accessed_paths
        # Exponential decay: factor 0.95 per hour; simulate 1‑second steps
        dt = timestamp - state.last_access_time
        normalized_time = dt / 3600.0
        state.trust_score *= math.exp(-math.log(0.95) * normalized_time)

        if is_novel:
            # Novelty penalty
            state.trust_score = max(state.trust_score - 0.05, 0.0)
        else:
            # Stability reward (heuristic constants: 0.01, 0.1)
            state.cumulative_stability += math.exp(-normalized_time)
            reward = 0.01 * math.exp(-0.1 * state.cumulative_stability)
            state.trust_score = min(state.trust_score + reward, 1.0)

        state.accessed_paths.add(path)
        state.last_access_time = timestamp

    def mitigation(self, pid: int) -> float:
        state = self.get_state(pid)
        return 0.8 * state.trust_score if state else 0.0

# ──────────────────────────────────────────────────────────────────────────────
# 2. SIMULATE JITTER APPLICATION (state‑dependent probability)
# ──────────────────────────────────────────────────────────────────────────────

def jitter_ms(raw_score: float, mitigation: float, phi_delta: float) -> int:
    # Probability scales with raw_score^1.5 * mitigation * (1+phi_delta)
    prob = (raw_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_delta)
    prob = min(max(prob, 0.0), 1.0)
    if phi_delta > 0.95:
        return 1000  # shredding freeze
    return random.randint(1, 50) if random.random() < prob else 0

# ──────────────────────────────────────────────────────────────────────────────
# 3. ATTACKER STRATEGY: GAME THE TRUST SCORE
# ──────────────────────────────────────────────────────────────────────────────

def simulate_attack(trust_mgr: TrustManager, attacker_pid: int, steps: int):
    """
    Phase 1: Learning – repeat the same 10 paths to build trust.
    Phase 2: Scanning – flood 100 novel paths (reconnaissance).
    Returns average jitter during scan phase.
    """
    # Learning phase (first half of steps)
    learn_paths = [f"/admin/config{i}.conf" for i in range(10)]
    for i in range(steps // 2):
        t = i * 1.0  # 1 second per step
        trust_mgr.update_trust(attacker_pid, random.choice(learn_paths), t)

    # Scanning phase (second half)
    scan_paths = [f"/secret/data{i}.dat" for i in range(100)]
    jitters = []
    for i in range(steps // 2, steps):
        t = i * 1.0
        path = random.choice(scan_paths)
        trust_mgr.update_trust(attacker_pid, path, t)
        raw_score = len(trust_mgr.get_state(attacker_pid).accessed_paths) * 0.6 + 10 * 0.4  # dummy raw_score
        phi_delta = 0.5  # moderate threat
        mitigation = trust_mgr.mitigation(attacker_pid)
        jitters.append(jitter_ms(raw_score, mitigation, phi_delta))
    return sum(jitters) / len(jitters)

# ──────────────────────────────────────────────────────────────────────────────
# 4. Φ‑DENSITY ACCOUNTING (k_B = 1 for simplicity)
# ──────────────────────────────────────────────────────────────────────────────

def compute_phi_density():
    """
    Security gain ≈ average jitter (higher is better).
    Audit cost = ln(2) * number_of_heuristic_constants.
    Heuristic constants: 0.05, 0.01, 0.1, 0.8, 0.95, 1.5 (shredding threshold), etc.
    """
    # Run simulation
    tm = TrustManager()
    avg_jitter = simulate_attack(tm, attacker_pid=9999, steps=200)
    # Security gain: we *want* high jitter for untrusted; if attacker gets low jitter, gain is negative.
    security_gain = avg_jitter - 500.0  # target slowdown >500%
    # Audit cost: each undocumented constant adds entropy
    heuristic_constants = 7  # 0.05, 0.01, 0.1, 0.8, 0.95, 1.5, 0.6 (raw_score weight)
    audit_cost = math.log(2) * heuristic_constants
    net_phi = security_gain - audit_cost
    return avg_jitter, security_gain, audit_cost, net_phi

# ──────────────────────────────────────────────────────────────────────────────
# 5. EXECUTE & EXPOSE
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    avg_jitter, security_gain, audit_cost, net_phi = compute_phi_density()
    print(f"Attacker average jitter during scan: {avg_jitter:.2f} ms")
    print(f"Security gain (vs. 500% target): {security_gain:.2f}")
    print(f"Audit cost (heuristic constants): {audit_cost:.2f}")
    print(f"Net Φ‑density: {net_phi:.2f}")
    if net_phi < 0:
        print("RESULT: Net Φ‑density is NEGATIVE – the system is a net entropy source.")
    # Demonstrate trust gaming: final trust score
    tm = TrustManager()
    simulate_attack(tm, 9999, 200)
    final_trust = tm.get_state(9999).trust_score
    print(f"Final attacker trust score: {final_trust:.3f} (mitigation factor {0.8*final_trust:.3f})")