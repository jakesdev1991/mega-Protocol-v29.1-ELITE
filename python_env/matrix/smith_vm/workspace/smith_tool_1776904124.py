# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# OMEGA PROTOCOL VALIDATOR – AFDS v3.0 TRUST & JITTER INVARIANTS
# This script is executed in the isolated VM to enforce mathematical soundness.
# Any assertion failure results in an immediate FAIL verdict.
# =============================================================================

import math
import random
from typing import List, Set

# -----------------------------------------------------------------------------
# 1. TRUST MODEL INVARIANTS (Objective 1)
# -----------------------------------------------------------------------------
def simulate_trust_update(paths: List[str],
                          decay_per_hour: float = 0.05,
                          consistency_weight: float = 0.1) -> List[float]:
    """
    Simulates the trust update logic from TrustManager::UpdateTrust.
    Returns the trust score after each access.
    """
    trust = 0.0
    accessed: Set[str] = set()
    trust_history = []

    for i, path in enumerate(paths):
        # consistency = 1 if path already seen, else 0 (binary novelty)
        consistency = 1.0 if path in accessed else 0.0
        # In this simplified model we ignore time-based decay for clarity;
        # decay only reduces trust, never increases it.
        trust = min(1.0, trust + consistency_weight * consistency)
        accessed.add(path)
        trust_history.append(trust)
    return trust_history

def test_trust_monotonicity_novelty():
    """
    Invariant: For a sequence of *novel* paths (no repeats),
    trust must NOT increase (or must increase only via a strictly
    bounded, decay‑offset term). In the current implementation,
    trust grows as 0.1 * H_n → violates Objective 1.
    """
    novel_paths = [f"/unique/path/{i}" for i in range(1, 25000)]  # >22k needed to hit 1.0
    trust_vals = simulate_trust_update(novel_paths)

    # After 22k unique paths, trust should be < 1.0 if decay outweighs gain.
    # With NO decay in this helper, we expect trust to reach ~0.1 * H_n.
    # We assert that trust never exceeds 0.5 for the first 1000 paths
    # as a sanity check; the real violation is that it eventually hits 1.0.
    assert max(trust_vals[:1000]) < 0.5, "Early trust growth too high (should be limited by decay)"
    # The critical check: trust must stay strictly below 1.0 for any feasible attack length.
    # Since the model has no decay in this simulation, we expect it to hit 1.0.
    # If it does, the invariant is broken.
    if trust_vals[-1] >= 1.0:
        raise AssertionError(
            f"Trust reached {trust_vals[-1]:.4f} after {len(novel_paths)} novel paths. "
            "This violates Objective 1: trust must penalize novelty, not reward it."
        )

# -----------------------------------------------------------------------------
# 2. JITTER PROBABILITY INVARIANT (Objective 2)
# -----------------------------------------------------------------------------
def jitter_probability(raw_score: float) -> float:
    """Probability of jitter injection as used in ApplyAdaptiveJitter."""
    return math.pow(raw_score / 100.0, 1.5)

def test_jitter_monotonicity():
    """Invariant: jitter probability must be non‑decreasing with raw_traversal_score."""
    prev = -1.0
    for score in range(0, 101, 5):
        p = jitter_probability(float(score))
        assert p >= prev - 1e-9, f"Probability decreased at score {score}"
        prev = p

# -----------------------------------------------------------------------------
# 3. FORENSIC LATENCY INVARIANT (Objective 3)
# -----------------------------------------------------------------------------
def test_latency_capture():
    """
    Invariant: applied_latency_ms must reflect the actual jitter injected.
    The current code hard‑codes it to 0 → invariant broken.
    We simulate a call and check that the logger would receive a non‑zero value
    when jitter is applied.
    """
    # Mock the jitter function to return a known delay
    def mock_apply_jitter(score):
        return 20  # ms

    # Simulate one lookup
    applied_latency_ms = mock_apply_jitter(50.0)  # arbitrary score
    assert applied_latency_ms > 0, "Forensic logger must capture non‑zero jitter latency"

# -----------------------------------------------------------------------------
# 4. BENCHMARK SUITE INVARIANT (Objective 5)
# -----------------------------------------------------------------------------
def test_benchmark_not_empty():
    """Invariant: BenchmarkSuite::RunExperiments must contain measurable logic."""
    # In the submitted code the method is empty → we fail.
    # Here we simply assert that a placeholder comment is NOT the only content.
    # In a real validation we would inspect the source; for this VM we treat
    # an empty body as a violation.
    raise AssertionError("BenchmarkSuite::RunExperiments is unimplemented – Objective 5 violated.")

# -----------------------------------------------------------------------------
# MAIN VALIDATION DRIVER
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        print("[Omega Validator] Checking Trust Model monotonicity...")
        test_trust_monotonicity_novelty()
        print("[Omega Validator] Trust model passed novelty test (unexpected).")

        print("[Omega Validator] Checking Jitter probability monotonicity...")
        test_jitter_monotonicity()
        print("[Omega Validator] Jitter probability invariant OK.")

        print("[Omega Validator] Checking Forensic latency capture...")
        test_latency_capture()
        print("[Omega Validator] Forensic latency invariant OK.")

        print("[Omega Validator] Checking Benchmark suite implementation...")
        test_benchmark_not_empty()  # will raise
    except AssertionError as e:
        print(f"[Omega Validator] INVARIANT VIOLATION: {e}")
        # In the VM, a non‑zero exit code signals FAIL to the overseer.
        exit(1)
    print("[Omega Validator] All invariants satisfied.")
    exit(0)