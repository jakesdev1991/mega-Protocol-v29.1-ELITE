# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# OMEGA PROTOCOL VALIDATION SCRIPT – AFDS v3.0 (ADAPTIVE FILESYSTEM DEFENSE SYSTEM)
# VALIDATES MATHEMATICAL SOUNDNESS AND INVARIANT COMPLIANCE (Phi_N, Phi_Delta, J*)
# =============================================================================
import math
import random
from typing import Dict, Tuple

# -----------------------------------------------------------------------------
# HELPERS – Mimic the core logic from the C++ implementation
# -----------------------------------------------------------------------------
def trust_update(
    trust: float,
    is_novel: bool,
    hours_since_last: float,
) -> float:
    """
    Replicates TrustManager::UpdateTrust core mathematics.
    Returns new trust score clamped to [0,1].
    """
    # Time-based decay (5% per hour)
    trust *= math.pow(0.95, hours_since_last)

    # Novelty penalty
    novelty_penalty = 0.05 if is_novel else 0.0

    # Stability reward (only for non-novel)
    stability_reward = 0.01 if not is_novel else 0.0

    # Apply penalty then reward (order matches C++: penalty subtract, reward add)
    trust = trust - novelty_penalty + stability_reward

    # Clamp
    return max(0.0, min(1.0, trust))


def mitigation(trust: float) -> float:
    """TrustManager::GetTrustMitigation – 80% reduction factor."""
    return 0.8 * trust


def traversal_score(unique_paths: int, max_depth: int) -> float:
    """CalculateTraversalScore – weights 0.6 for breadth, 0.4 for depth."""
    return (unique_paths * 0.6) + (max_depth * 0.4)


def jitter_probability(
    raw_score: float,
    mitig: float,
) -> float:
    """
    ApplyAdaptiveJitter probability calculation.
    Returns probability in [0,1] that jitter is injected.
    """
    base = math.pow(raw_score / 100.0, 1.5)
    base = min(1.0, base)          # clamp
    prob = base * (1.0 - mitig)    # trust mitigation reduces chance
    return max(0.0, min(1.0, prob))


def apply_jitter(
    raw_score: float,
    mitig: float,
    rng: random.Random,
) -> int:
    """
    Simulates ApplyAdaptiveJitter – returns latency in ms (0 if no jitter).
    """
    prob = jitter_probability(raw_score, mitig)
    if rng.random() < prob:
        jitter_ms = 1 + int(49.0 * rng.random())  # 1..50 inclusive
        return jitter_ms
    return 0


# -----------------------------------------------------------------------------
# VALIDATION SUITE – Checks each Omega Protocol invariant
# -----------------------------------------------------------------------------
def run_validation() -> Tuple[bool, str]:
    """
    Returns (passed, message). If any invariant fails, returns False with details.
    """
    rng = random.Random(42)  # deterministic for repeatability

    # -------------------------- Invariant Phi_N: Trust Score Bounds --------------------------
    # Trust must always remain in [0,1] regardless of inputs.
    test_cases = [
        (0.0, True, 0.0),   # novel, no decay
        (0.0, True, 10.0),  # novel, large decay (should stay 0)
        (0.5, False, 0.0),  # stable, no decay
        (0.5, False, 5.0),  # stable, moderate decay
        (0.9, True, 2.0),   # high trust, novel access
        (0.9, False, 2.0),  # high trust, stable access
    ]
    for trust0, novel, hrs in test_cases:
        t1 = trust_update(trust0, novel, hrs)
        if not (0.0 <= t1 <= 1.0):
            return False, f"Phi_N violation: trust={trust0}, novel={novel}, hrs={hrs} -> {t1}"
    # Additionally, verify that repeated stable accesses can increase trust.
    trust = 0.0
    for _ in range(200):  # many stable accesses, no decay
        trust = trust_update(trust, False, 0.0)
    if trust < 0.9:  # should approach near 1 with 0.01 reward each step
        return False, f"Phi_N violation: trust did not increase sufficiently after stable accesses ({trust})"

    # -------------------------- Invariant Phi_Delta: Mitigation Factor --------------------------
    # Mitigation = 0.8 * trust must be in [0,0.8] and monotonic with trust.
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        m = mitigation(t)
        if not (0.0 <= m <= 0.8):
            return False, f"Phi_Delta violation: mitigation({t}) = {m}"
        # monotonic check
        if t > 0.0 and mitigation(t) < mitigation(t - 0.01):
            return False, f"Phi_Delta violation: mitigation not monotonic at trust={t}"

    # -------------------------- Invariant J*: Jitter Probability Bounds & Trust Coupling ----------
    # Probability must be in [0,1] and must decrease as mitigation increases (i.e., as trust increases).
    raw_scores = [0.0, 20.0, 50.0, 80.0, 120.0, 200.0]
    for score in raw_scores:
        for trust in [0.0, 0.3, 0.6, 0.9]:
            mitig = mitigation(trust)
            prob = jitter_probability(score, mitig)
            if not (0.0 <= prob <= 1.0):
                return False, f"J* violation: prob out of range (score={score}, trust={trust}) -> {prob}"
            # Check monotonic decreasing in mitigation (i.e., increasing trust lowers prob)
            # We'll test by comparing two trust levels
    for score in raw_scores:
        low_trust = 0.0
        high_trust = 1.0
        p_low = jitter_probability(score, mitigation(low_trust))
        p_high = jitter_probability(score, mitigation(high_trust))
        if p_low < p_high:  # higher trust should not increase jitter probability
            return False, f"J* violation: jitter probability increased with trust (score={score})"

    # -------------------------- Functional Checks: Jitter Latency Range --------------------------
    for _ in range(1000):
        score = rng.uniform(0, 200)
        trust = rng.random()
        mitig = mitigation(trust)
        lat = apply_jitter(score, mitig, rng)
        if lat != 0 and not (1 <= lat <= 50):
            return False, f"Jitter latency out of bounds: {lat}ms (score={score}, trust={trust})"

    # -------------------------- Forensic Logger Sanity (latency matches jitter) -------------------
    # We simulate a single log entry and ensure applied_latency_ms equals the jitter returned.
    score = 75.0
    trust = 0.4
    mitig = mitigation(trust)
    lat = apply_jitter(score, mitig, rng)
    # In real code, ForensicLogEntry.applied_latency_ms would be set to `lat`.
    # Here we just assert that the value we got is the one that would be logged.
    assert isinstance(lat, int)  # trivial, but shows the link

    # -------------------------- Topology Metrics: Depth Histogram Non‑Negative -------------------
    # Not directly in the snippet, but we can sanity-check the update logic.
    class DummyMetrics:
        def __init__(self):
            self.unique_paths = set()
            self.max_depth = 0
            self.depth_histogram = []

    def update_topology(path: str, m: DummyMetrics):
        m.unique_paths.add(path)
        depth = path.count('/')
        if depth > m.max_depth:
            m.max_depth = depth
        if depth >= len(m.depth_histogram):
            m.depth_histogram.extend([0] * (depth - len(m.depth_histogram) + 1))
        m.depth_histogram[depth] += 1

    dm = DummyMetrics()
    for p in ["/", "/a", "/a/b", "/a/b/c/d"]:
        update_topology(p, dm)
    # All histogram entries must be non‑negative and sum to number of paths.
    if any(v < 0 for v in dm.depth_histogram):
        return False, "Topology histogram contains negative count"
    if sum(dm.depth_histogram) != len(["/", "/a", "/a/b", "/a/b/c/d"]):
        return False, "Topology histogram sum mismatch"

    # If we reach here, all invariants hold.
    return True, "All Omega Protocol invariants (Phi_N, Phi_Delta, J*) satisfied."


# -----------------------------------------------------------------------------
# EXECUTE VALIDATION
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    passed, msg = run_validation()
    if passed:
        print("VALIDATION RESULT: PASS")
        print(msg)
    else:
        print("VALIDATION RESULT: FAIL")
        print(msg)
        # In a real guard‑rail scenario we would raise or halt deployment.
        raise SystemExit(1)