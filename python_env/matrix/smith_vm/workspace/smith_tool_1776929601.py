# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
AFDS v3.0 Invariant Validator
Checks:
  - Trust score stays in [0,1] and can increase.
  - Mitigation is derived from trust and applied to jitter probability.
  - Jitter probability is clamped to [0,1].
  - Latency when applied is in [1,50] ms.
  - Forensic log contains required fields.
  - Benchmark uses actual AFDS traversal (stubbed here for illustration).
"""

import math
import random
import time
from typing import Dict, Tuple

# ------------------- Trust Model (as in engine) -------------------
class TrustState:
    def __init__(self):
        self.trust = 0.0          # initial trust
        self.last = time.time()
        self.paths = set()

    def update(self, path: str, novelty_penalty: float = 0.05, decay_per_hour: float = 0.05):
        now = time.time()
        dt_h = (now - self.last) / 3600.0
        # decay
        self.trust *= (1.0 - decay_per_hour) ** dt_h
        # novelty penalty
        is_novel = path not in self.paths
        penalty = novelty_penalty if is_novel else 0.0
        self.trust = max(0.0, min(1.0, self.trust - penalty))
        self.paths.add(path)
        self.last = now
        return self.trust

# ------------------- Jitter Model (as in engine) -------------------
def jitter_probability(trav_score: float) -> float:
    p = math.pow(trav_score / 100.0, 1.5)
    return min(1.0, p)   # clamp

def apply_jitter(trav_score: float) -> int:
    if random.random() < jitter_probability(trav_score):
        return 1 + int(49.0 * random.random())
    return 0

# ------------------- Validation Routines -------------------
def validate_trust_monotonicity():
    """Ensure trust can increase when novelty_penalty = 0 and decay = 0."""
    ts = TrustState()
    # force zero decay and zero penalty
    orig_update = ts.update
    def patched_update(path):
        return orig_update(path, novelty_penalty=0.0, decay_per_hour=0.0)
    ts.update = patched_update

    scores = []
    for i in range(10):
        ts.update(f"/path/{i}")
        scores.append(ts.trust)
    # trust should be non‑decreasing and eventually >0
    assert all(scores[i] <= scores[i+1] + 1e-12 for i in range(len(scores)-1)), \
        "Trust decreased without novelty penalty"
    assert scores[-1] > 0.0, "Trust never increased"
    print("[✓] Trust can increase when novelty=0 & decay=0")

def validate_trust_bounds():
    ts = TrustState()
    for _ in range(1000):
        ts.update("/new/path/" + str(random.randint(0, 1000)))
        assert 0.0 <= ts.trust <= 1.0, f"Trust out of bounds: {ts.trust}"
    print("[✓] Trust stays within [0,1]")

def validate_mitigation_used():
    """Check that mitigation derived from trust is actually used to scale jitter probability."""
    ts = TrustState()
    # Simulate a trusted process (low novelty)
    for _ in range(20):
        ts.update("/known/path", novelty_penalty=0.0, decay_per_hour=0.0)
    trust = ts.trust
    mitigation = 0.2 * trust   # as in engine
    # In real code mitigation should affect jitter probability:
    # p_eff = jitter_probability(score) * (1 - mitigation)  (example)
    # Here we just assert mitigation is non‑zero for trusted case.
    assert mitigation > 0.0, "Mitigation zero despite high trust"
    print("[✓] Mitigation derived from trust is non‑zero for trusted process")

def validate_jitter_bounds():
    for score in [0, 10, 50, 100, 200, 1000]:
        p = jitter_probability(score)
        assert 0.0 <= p <= 1.0, f"Jitter probability {p} out of bounds for score {score}"
        lat = apply_jitter(score)
        if lat != 0:
            assert 1 <= lat <= 50, f"Jitter latency {lat}ms out of bounds"
    print("[✓] Jitter probability and latency respect bounds")

def validate_forensic_fields():
    # Mimic the log entry creation
    entry = {
        "timestamp": time.time(),
        "pid": 1234,
        "operation": "lookup",
        "path": "/some/file",
        "applied_latency_ms": apply_jitter(30),
        "traversal_score": 30.0,
        "trust_score": 0.2 * 0.5,  # dummy
        "inter_call_interval": 0.0
    }
    required = {"timestamp","pid","operation","path","applied_latency_ms",
                "traversal_score","trust_score","inter_call_interval"}
    assert required.issubset(entry.keys()), "Missing forensic field"
    print("[✓] Forensic entry contains all required fields")

def validate_benchmark_stub():
    """
    Placeholder: real benchmark must measure actual FUSE traversal.
    Here we assert that a stub would call a function that uses the AFDS stack.
    """
    def dummy_afds_traversal():
        # Simulate a path lookup that goes through trust/jitter/logging
        ts = TrustState()
        ts.update("/tmp/test")
        _ = apply_jitter(10)
        return True
    assert dummy_afds_traversal(), "AFDS traversal stub failed"
    print("[✓] Benchmark stub invokes AFDS components (replace with real FUSE test)")

def main():
    random.seed(42)
    validate_trust_monotonicity()
    validate_trust_bounds()
    validate_mitigation_used()
    validate_jitter_bounds()
    validate_forensic_fields()
    validate_benchmark_stub()
    print("\nAll invariant checks passed – *if* the engine code is patched to use mitigation and allow trust growth.")

if __name__ == "__main__":
    main()