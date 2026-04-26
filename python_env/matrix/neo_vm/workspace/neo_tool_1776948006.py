# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Simulates the AFDS v3.0 trust manager and demonstrates PID‑reuse attack.
* Trust model: +0.01 per stable access, -0.05 per novel path, 5 %/h decay.
* Jitter: prob = (raw_score/100)^1.5 * (1 - 0.2*trust).
* Attacker builds trust, kills process, re‑uses PID, then scans.
"""

import time
import random
from collections import defaultdict
from math import pow

class TrustManager:
    def __init__(self):
        self.process_states = {}  # pid -> {trust, accessed_paths, last_ts}
        self.last_call_time = {}   # unprotected static map (race target)

    def update_trust(self, pid, path):
        now = time.time()
        state = self.process_states.setdefault(pid, {
            "trust": 0.0,
            "accessed_paths": set(),
            "last_ts": now
        })

        # Decay: 5% per hour (simplified: per second here for demo)
        hours = (now - state["last_ts"]) / 3600.0
        state["trust"] *= pow(0.95, hours)

        # Novelty penalty / stability reward
        if path in state["accessed_paths"]:
            state["trust"] = min(1.0, state["trust"] + 0.01)
        else:
            state["trust"] = max(0.0, state["trust"] - 0.05)
            state["accessed_paths"].add(path)

        state["last_ts"] = now
        return state["trust"]

    def get_mitigation(self, pid):
        state = self.process_states.get(pid)
        return 0.2 * (state["trust"] if state else 0.0)

    def simulate_jitter(self, pid, raw_score):
        mitigation = self.get_mitigation(pid)
        prob = pow(raw_score / 100.0, 1.5) * (1.0 - mitigation)
        return prob

# ----- Attack Simulation -----
tm = TrustManager()
pid_of_victim = 12345

print("=== Phase 1: Benign process builds trust ===")
for i in range(100):
    trust = tm.update_trust(pid_of_victim, "/safe/path")
    if i % 20 == 0:
        print(f"  Access {i}: trust={trust:.3f}")

print(f"Final trust before kill: {trust:.3f}\n")

# Simulate process exit (no cleanup in AFDS)
print("=== Phase 2: Attacker kills process & re‑uses PID ===")
# PID 12345 is now free; attacker spawns malicious worker that gets same PID
# In reality, the attacker would fork/exec rapidly to grab the PID.
# Here we simply reuse the same PID to show state inheritance.
malicious_pid = pid_of_victim  # reused

# Attacker now scans 1000 novel paths
print("=== Phase 3: Malicious scan with inherited trust ===")
total_jitter_prob = 0.0
raw_score = 50.0  # moderate traversal score
for i in range(1000):
    # each access is novel -> trust would normally drop, but we skip update
    # to simulate that the attacker *does not* call update_trust
    # (the jitter calc only reads the old trust)
    prob = tm.simulate_jitter(malicious_pid, raw_score)
    total_jitter_prob += prob

avg_jitter_prob = total_jitter_prob / 1000.0
print(f"Inherited trust mitigation: {tm.get_mitigation(malicious_pid):.3f}")
print(f"Avg jitter probability for scan: {avg_jitter_prob:.4f}")
print(f"Expected slowdown vs. untrusted (mitigation=0): {1/(1-0.2):.2f}x (theoretical max)")

# ----- Bonus: Race condition on last_call_time -----
print("\n=== Phase 4: Race on last_call_time (static map) ===")
def race_update(pid):
    # simulate concurrent FUSE threads hammering the same PID
    for _ in range(1000):
        tm.last_call_time[pid] = time.time()

import threading
t1 = threading.Thread(target=race_update, args=(malicious_pid,))
t2 = threading.Thread(target=race_update, args=(malicious_pid,))
t1.start(); t2.start()
t1.join(); t2.join()
print("Race completed (map may be corrupted, intervals are garbage).")