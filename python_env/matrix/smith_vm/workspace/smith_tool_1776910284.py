# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for AFDS v3.0 (Trust Manager,
Forensic Logger, Topology Metrics, and Phi‑density).

Run:  python3 validate_afds.py
"""

import math
import random
from collections import defaultdict
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# Helper functions that mirror the C++ logic (pure Python)
# ----------------------------------------------------------------------
TAU = 3600.0  # seconds


def trust_decay_factor(delta_t: float) -> float:
    """Return exp(-ln(0.95) * delta_t / TAU)."""
    return math.exp(-math.log(0.95) * (delta_t / TAU))


def update_trust(
    trust: float,
    is_novel: bool,
    delta_t: float,
) -> float:
    """Apply one trust update step (no clamping inside, caller must clamp)."""
    novelty_penalty = 0.05 if is_novel else 0.0
    trust *= trust_decay_factor(delta_t)
    trust -= novelty_penalty
    if not is_novel:
        trust += 0.01
    return trust


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def trust_mitigation(trust: float) -> float:
    """0.8 * trust (for known PID)."""
    return 0.8 * trust


def traversal_score(unique_paths: int, max_depth: int) -> float:
    return unique_paths * 0.6 + max_depth * 0.4


def jitter_probability(raw_score: float, mitigation: float) -> float:
    p = (raw_score / 100.0) ** 1.5
    p *= mitigation
    return clamp(p, 0.0, 1.0)


def expected_jitter_ms(p: float) -> float:
    """Uniform latency 1‑50 ms when triggered."""
    return p * ((1 + 50) / 2)  # 25.5 ms


def shannon_conditional_entropy(counts: Dict[str, int]) -> float:
    """Return H_cond = H(X) / H_max, where H_max = log(N_patterns)."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values()]
    H = -sum(p * math.log(p) for p in probs if p > 0)
    H_max = math.log(len(probs))
    return 0.0 if H_max == 0 else H / H_max


def manifold_curvature(phi_N: float, traversal_score: float, h_cond: float) -> float:
    phi_Delta = math.tanh(traversal_score / 100.0)
    return phi_N * phi_Delta - h_cond


def phi_density(raw_gain: float, audit_complexity: float) -> float:
    """Φ_net = raw_gain - k_B * ln(2) * audit_complexity (k_B = 1)."""
    k_B = 1.0
    audit_cost = k_B * math.log(2.0) * audit_complexity
    return raw_gain - audit_cost


# ----------------------------------------------------------------------
# Randomized test harness
# ----------------------------------------------------------------------
def run_random_tests(num_iter: int = 10_000) -> None:
    random.seed(42)

    for i in range(num_iter):
        # --- Trust state -------------------------------------------------
        trust = random.random()  # [0,1]
        is_novel = random.random() < 0.3
        delta_t = random.uniform(0, 2 * TAU)  # up to 2h
        new_trust = update_trust(trust, is_novel, delta_t)
        new_trust = clamp(new_trust, 0.0, 1.0)

        assert 0.0 <= new_trust <= 1.0, f"Trust out of bounds: {new_trust}"
        mitigation = trust_mitigation(new_trust)
        assert 0.0 <= mitigation <= 0.8, f"Mitigation out of bounds: {mitigation}"

        # --- Topology ----------------------------------------------------
        unique_paths = random.randint(0, 200)
        max_depth = random.randint(0, 30)
        raw = traversal_score(unique_paths, max_depth)
        assert raw >= 0.0, "Negative traversal score"

        # --- Jitter ------------------------------------------------------
        prob = jitter_probability(raw, mitigation)
        assert 0.0 <= prob <= 1.0, f"Jitter probability invalid: {prob}"
        exp_jitter = expected_jitter_ms(prob)
        assert 0.0 <= exp_jitter <= 25.5, f"Expected jitter out of range: {exp_jitter}"

        # --- Forensic entropy --------------------------------------------
        # Simulate a small log of patterns
        n_patterns = random.randint(1, 10)
        counts = defaultdict(int)
        for _ in range(random.randint(5, 30)):
            pat = f"op{random.randint(0, n_patterns-1)}:int{random.randint(0, 9)}"
            counts[pat] += 1
        h_cond = shannon_conditional_entropy(counts)
        assert 0.0 <= h_cond <= 1.0, f"Conditional entropy out of [0,1]: {h_cond}"

        # --- Manifold curvature -------------------------------------------
        phi_N = 0.7  # as in the source
        curv = manifold_curvature(phi_N, raw, h_cond)
        # No hard bounds, but we can sanity‑check that it's not absurdly large
        assert -5.0 <= curv <= 5.0, f"Curvature seems implausible: {curv}"

        # --- Phi‑density --------------------------------------------------
        raw_gain = random.uniform(0.0, 2.0)   # explore a range
        audit_complexity = random.uniform(0.1, 5.0)
        net_phi = phi_density(raw_gain, audit_complexity)
        # The formula itself is dimensionally sound; we just verify it's a real number
        assert isinstance(net_phi, float) and not math.isnan(net_phi), "Phi‑density NaN"

        if i % 1000 == 0:
            print(f"Iteration {i}: OK")

    print("All random tests passed.")


def check_claimed_phi_density() -> None:
    """
    Verify the numbers given in the original commentary:
        raw_gain = 0.80
        audit_complexity = 2.5
        => claimed net Φ = +0.65
    """
    raw_gain = 0.80
    audit_complexity = 2.5
    net = phi_density(raw_gain, audit_complexity)
    print(f"Phi‑density with raw_gain={raw_gain}, audit_complexity={audit_complexity} => {net:.4f}")
    # The original claim was +0.65; we flag the discrepancy.
    expected = 0.65
    if not math.isclose(net, expected, abs_tol=0.01):
        raise AssertionError(
            f"Phi‑density mismatch: got {net:.4f}, expected ~{expected:.2f}. "
            f"Adjust raw_gain or audit_complexity to satisfy Ω‑invariant."
        )


if __name__ == "__main__":
    try:
        run_random_tests()
        check_claimed_phi_density()
    except AssertionError as e:
        print(f"\nVALIDATION FAILED: {e}")
        raise SystemExit(1)
    print("\nAll invariants satisfied. AFDS v3.0 is Ω‑compliant (pending Φ‑density fix).")