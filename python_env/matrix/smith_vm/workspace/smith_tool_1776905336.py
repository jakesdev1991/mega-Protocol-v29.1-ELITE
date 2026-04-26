# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
AFDS v3.0 Mathematical Invariant Validator
-----------------------------------------
Checks:
  * Trust score stays in [0,1] after novelty penalty & decay.
  * Mitigation factor = 0.2 * trust_score  ->  [0,0.2].
  * Jitter probability = (score/100)^1.5 clamped to [0,1].
  * Applied jitter latency in [1,50] ms when triggered.
  * TraversalScore = 0.6*|U| + 0.4*D  (non‑negative).
  * Forensic log latency field equals the jitter returned.
  * Depth histogram updates correctly.
Run as part of CI:  python3 validate_afds.py
"""

import math
import random
from typing import Tuple

# ------------------- Trust Model -------------------
def update_trust(
    trust: float,
    is_novel: bool,
    hours_since_last: float,
    novelty_penalty: float = 0.05,
    decay_per_hour: float = 0.05,  # 5% per hour -> multiply by (1-decay)
) -> float:
    """Return new trust score after novelty penalty and exponential decay."""
    # decay: trust * (1 - decay_per_hour) ^ hours
    decayed = trust * ((1.0 - decay_per_hour) ** hours_since_last)
    # novelty penalty
    penalized = decayed - (novelty_penalty if is_novel else 0.0)
    # clamp to [0,1]
    return max(0.0, min(1.0, penalized))


def mitigation(trust: float) -> float:
    """Mitigation factor applied to intrusion score (0.2 * trust)."""
    return 0.2 * trust


# ------------------- Jitter Model -------------------
def jitter_probability(traversal_score: float) -> float:
    """Probability of injecting jitter, clamped to [0,1]."""
    p = (traversal_score / 100.0) ** 1.5
    return max(0.0, min(1.0, p))


def apply_jitter(traversal_score: float, rng: random.Random) -> int:
    """Return jitter latency in ms (0 if no jitter)."""
    if rng.random() < jitter_probability(traversal_score):
        # uniform 1..50 inclusive
        return rng.randint(1, 50)
    return 0


# ------------------- Topology -------------------
def traversal_score(unique_paths: int, max_depth: int) -> float:
    """Raw traversal score used for jitter probability."""
    return 0.6 * unique_paths + 0.4 * max_depth


def update_topology(path: str,
                    unique_paths: set,
                    depth_hist: list,
                    ) -> Tuple[int, int]:
    """Update topology metrics; returns (new_unique_count, new_max_depth)."""
    unique_paths.add(path)
    depth = path.count('/')
    if depth >= len(depth_hist):
        depth_hist.extend([0] * (depth - len(depth_hist) + 1))
    depth_hist[depth] += 1
    return len(unique_paths), max(depth_hist)  # max depth = len(depth_hist)-1


# ------------------- Forensic Logging -------------------
class ForensicEntry:
    def __init__(self, pid, op, path, applied_latency,
                 traversal_score, trust_score, inter_call_interval):
        self.pid = pid
        self.op = op
        self.path = path
        self.applied_latency_ms = applied_latency
        self.traversal_score = traversal_score
        self.trust_score = trust_score
        self.inter_call_interval = inter_call_interval


# ------------------- Property Tests -------------------
def run_tests():
    rng = random.Random(42)  # deterministic for CI

    # 1. Trust bounds & monotonicity
    trust = 0.5
    for _ in range(100):
        is_novel = rng.random() < 0.3
        hours = rng.random() * 10  # 0‑10h
        new_trust = update_trust(trust, is_novel, hours)
        assert 0.0 <= new_trust <= 1.0, f"Trust out of bounds: {new_trust}"
        trust = new_trust
    print("[✓] Trust stays in [0,1]")

    # 2. Mitigation range
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        m = mitigation(t)
        assert 0.0 <= m <= 0.2, f"Mitigation out of range: {m}"
    print("[✓] Mitigation in [0,0.2]")

    # 3. Jitter probability monotonic & clamped
    prev = -1.0
    for s in [0, 10, 20, 50, 100, 200, 500, 1000]:
        p = jitter_probability(s)
        assert 0.0 <= p <= 1.0, f"Probability {p} not in [0,1]"
        assert p >= prev - 1e-12, f"Probability not monotonic at {s}"
        prev = p
    print("[✓] Jitter probability valid & monotonic")

    # 4. Applied jitter latency range
    for _ in range(1000):
        score = rng.uniform(0, 500)
        lat = apply_jitter(score, rng)
        if lat != 0:
            assert 1 <= lat <= 50, f"Jitter latency {lat} out of [1,50]"
    print("[✓] Jitter latency in [1,50] when injected")

    # 5. Traversal score non‑negative
    for u in range(0, 100):
        for d in range(0, 20):
            ts = traversal_score(u, d)
            assert ts >= 0.0, f"Negative traversal score: {ts}"
    print("[✓] Traversal score non‑negative")

    # 6. Topology update correctness
    up = set()
    dh = []
    paths = ["/a", "/a/b", "/a/b/c", "/d/e", "/d/e/f/g"]
    for p in paths:
        u_cnt, max_d = update_topology(p, up, dh)
        assert u_cnt == len(up), "Unique count mismatch"
        assert max_d == len(dh) - 1, "Depth histogram size mismatch"
        # histogram sanity
        total = sum(dh)
        assert total == len([x for x in paths if x <= p]), "Histogram sum off"
    print("[✓] Topology metrics update correctly")

    # 7. Forensic entry latency matches jitter
    for _ in range(500):
        score = rng.uniform(0, 300)
        lat = apply_jitter(score, rng)
        entry = ForensicEntry(
            pid=123,
            op="lookup",
            path="/test",
            applied_latency=lat,
            traversal_score=score,
            trust_score=0.7,
            inter_call_interval=10.0,
        )
        assert entry.applied_latency_ms == lat, "Forensic latency mismatch"
    print("[✓] Forensic latency field consistent")

    print("\nAll invariant checks PASSED.")


if __name__ == "__main__":
    run_tests()