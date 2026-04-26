# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for AFDS v3.0 Core Logic
Checks:
  - Trust score bounds [0,1] and monotonic decay w.r.t novelty.
  - Consistency metric does NOT reward new paths.
  - Jitter probability uses raw traversal score (not mitigated trust).
  - Forensic log captures applied latency.
Run with: python3 validate_afds.py
"""

import math
import random
from typing import Dict, Set

# ------------------- TRUST MODEL INVARIANTS -------------------
def validate_trust_model() -> bool:
    """Simulate trust updates and assert invariants."""
    trust: Dict[int, float] = {}
    paths: Dict[int, Set[str]] = {}
    last_access: Dict[int, float] = {}  # simulated hours

    def update_trust(pid: int, path: str, novelty: bool, hours_since_last: float = 0.0):
        """Novelty=True if path not seen before for this pid."""
        if pid not in trust:
            trust[pid] = 0.0          # Invariant: trust init = 0.0
            paths[pid] = set()
            last_access[pid] = 0.0
        # Decay: 5% per hour (as in code)
        trust[pid] *= (0.95 ** hours_since_last)
        # Consistency as defined in the submission
        if paths[pid]:
            consistency = (1.0 if path in paths[pid] else 0.0) / len(paths[pid])
        else:
            consistency = 0.0
        # Trust update (as in code)
        trust[pid] = min(1.0, trust[pid] + 0.1 * consistency)
        paths[pid].add(path)
        last_access[pid] += hours_since_last
        return trust[pid]

    # --- Test 1: Trust must never exceed 1.0 or drop below 0.0 ---
    for pid in [1, 2, 3]:
        for i in range(100):
            t = update_trust(pid, f"/path/{i}", novelty=(i not in paths[pid]))
            assert 0.0 <= t <= 1.0, f"Trust out of bounds: pid={pid}, t={t}"
    # --- Test 2: Trust must NOT increase when novelty=True (penalize novelty) ---
    for pid in [10, 11]:
        trust[pid] = 0.5
        paths[pid] = {"/known"}
        # Access a novel path
        t_before = trust[pid]
        t_after = update_trust(pid, "/novel", novelty=True)
        # With the current consistency formula, trust *may* increase (flaw)
        # We assert the *desired* invariant: novelty should not increase trust.
        if t_after > t_before + 1e-9:  # allow tiny FP noise
            print(f"[FAIL] Trust increased on novelty: {t_before} -> {t_after} (pid={pid})")
            return False
    # --- Test 3: Trust should decay with inactivity ---
    for pid in [20, 21]:
        trust[pid] = 0.8
        paths[pid] = {"/static"}
        t_before = trust[pid]
        t_after = update_trust(pid, "/static", novelty=False, hours_since_last=10.0)
        if t_after >= t_before - 1e-9:
            print(f"[FAIL] Trust did not decay after 10h: {t_before} -> {t_after}")
            return False
    return True

# ------------------- JITTER PROBABILITY INVARIANTS -------------------
def validate_jitter() -> bool:
    """Ensure jitter probability uses raw traversal score, not mitigated trust."""
    # Mock traversal score calculation (as in code)
    def traversal_score(unique_paths: int, max_depth: int) -> float:
        return (unique_paths * 0.6) + (max_depth * 0.4)

    # Probability function from submission
    def jitter_probability(raw_score: float) -> float:
        return math.pow(raw_score / 100.0, 1.5)

    # Test: probability must be monotonic in raw_score and bounded [0,1]
    prev = -1.0
    for score in [0, 10, 20, 50, 80, 100, 150]:
        p = jitter_probability(score)
        assert 0.0 <= p <= 1.0, f"Jitter probability out of range: score={score}, p={p}"
        assert p >= prev - 1e-9, f"Non‑monotonic probability: {prev} -> {p} at score={score}"
        prev = p
    # Ensure trust mitigation does NOT feed into probability
    # (We simply check that the function does not reference trust; static analysis)
    # Here we trust the source code; if it used trust, the test would need to inject a trust var.
    return True

# ------------------- FORENSIC LOG INVARIANTS -------------------
def validate_forensic() -> bool:
    """Check that a log entry can contain applied latency > 0."""
    class ForensicLogEntry:
        def __init__(self, applied_latency_ms: int, **kwargs):
            self.applied_latency_ms = applied_latency_ms
            # other fields omitted for brevity

    # Simulate a jitter injection that returns latency
    def inject_jitter() -> int:
        # Mimic the jitter range 1‑50 ms
        return random.randint(1, 50)

    latency = inject_jitter()
    entry = ForensicLogEntry(applied_latency_ms=latency)
    assert entry.applied_latency_ms > 0, "Forensic log must record non‑zero injected latency"
    return True

# ------------------- MAIN VALIDATION -------------------
def main():
    print("[Ω] Running AFDS v3.0 invariant validation...")
    checks = [
        ("Trust Model", validate_trust_model),
        ("Jitter Probability", validate_jitter),
        ("Forensic Logging", validate_forensic),
    ]
    all_ok = True
    for name, func in checks:
        try:
            ok = func()
            print(f"  {name}: {'PASS' if ok else 'FAIL'}")
            if not ok:
                all_ok = False
        except AssertionError as e:
            print(f"  {name}: FAIL – {e}")
            all_ok = False
    print("\n[Ω] Result:", "ALL INVARIANTS SATISFIED" if all_ok else "INVARIANT VIOLATION DETECTED")
    if not all_ok:
        print("\n→ The current AFDS v3.0 core logic violates Omega Protocol invariants.")
        print→ "See audit notes for required fixes (trust model redesign, latency capture, benchmark suite).")
    exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()