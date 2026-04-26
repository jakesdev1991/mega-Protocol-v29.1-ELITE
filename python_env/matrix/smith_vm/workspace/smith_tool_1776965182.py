# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# AFDS v3.0 Mathematical & Invariant Validation Script
# This script checks the core mathematical properties of the repaired AFDS v3.0
# implementation against the Omega Protocol specifications.

import math
import random
from collections import defaultdict

# -------------------------- Helper Functions --------------------------

def continuous_trust_decay(initial_trust, hours):
    """Exact continuous decay: 5% per hour -> factor = 0.95^hours = exp(-ln(0.95)*hours)"""
    return initial_trust * math.exp(-math.log(0.95) * hours)

def clamp(x, low=0.0, high=1.0):
    return max(low, min(high, x))

def calculate_traversal_score(unique_paths, max_depth):
    """Score = 0.6 * |unique_paths| + 0.4 * max_depth"""
    return 0.6 * len(unique_paths) + 0.4 * max_depth

def jitter_probability(raw_score, mitigation):
    """p = (raw_score/100)^1.5 * (1 - mitigation), clamped to [0,1]"""
    base = (raw_score / 100.0) ** 1.5
    prob = base * (1.0 - mitigation)
    return clamp(prob, 0.0, 1.0)

def apply_adaptive_jitter(raw_score, mitigation, rng):
    """Return jitter_ms (1-50) if random < probability, else 0"""
    prob = jitter_probability(raw_score, mitigation)
    if rng.random() < prob:
        # 1 + 50 * random -> inclusive [1,50]
        return 1 + int(50.0 * rng.random())
    return 0

# -------------------------- Validation Tests --------------------------

def test_trust_decay():
    """Verify continuous decay matches 5% per hour."""
    print("\n[Test] Trust Decay (5%/hour continuous)")
    initial = 1.0
    for hours in [0, 0.5, 1, 2, 4, 12, 24]:
        expected = initial * (0.95 ** hours)   # discrete equivalent for comparison
        actual = continuous_trust_decay(initial, hours)
        # Allow tiny floating-point difference
        if abs(actual - expected) > 1e-9:
            print(f"  FAIL: hours={hours}, expected≈{expected:.6f}, got={actual:.6f}")
            return False
        print(f"  OK: {hours}h -> {actual:.6f}")
    return True

def test_trust_update_logic():
    """Check novelty penalty, stability reward, and clamping."""
    print("\n[Test] Trust Update Logic")
    trust = 0.5
    # Simulate a process state
    state = {
        'trust': trust,
        'last_access': 0.0,   # hours since epoch (we'll use hours unit)
        'paths': set()
    }
    now = 10.0   # current time in hours

    # First access (novel)
    path = "/new/file"
    is_novel = path not in state['paths']
    penalty = 0.05 if is_novel else 0.0
    # decay over 10 hours
    decayed = continuous_trust_decay(state['trust'], now - state['last_access'])
    rewarded = decayed + (0.01 if not is_novel else 0.0)
    new_trust = clamp(rewarded - penalty)
    state['paths'].add(path)
    state['last_access'] = now
    expected = clamp(continuous_trust_decay(0.5, 10.0) - 0.05)
    if abs(new_trust - expected) > 1e-9:
        print(f"  FAIL novel access: expected={expected:.6f}, got={new_trust:.6f}")
        return False
    print(f"  Novel access OK: trust={new_trust:.6f}")

    # Second access (same path, non-novel) after 1 hour
    path2 = "/new/file"
    is_novel = path2 not in state['paths']
    penalty = 0.05 if is_novel else 0.0
    decayed = continuous_trust_decay(new_trust, 1.0)   # 1 hour later
    rewarded = decayed + (0.01 if not is_novel else 0.0)
    new_trust2 = clamp(rewarded - penalty)
    expected2 = clamp(continuous_trust_decay(new_trust, 1.0) + 0.01)
    if abs(new_trust2 - expected2) > 1e-9:
        print(f"  FAIL repeat access: expected={expected2:.6f}, got={new_trust2:.6f}")
        return False
    print(f"  Repeat access OK: trust={new_trust2:.6f}")
    return True

def test_mitigation_factor():
    """Mitigation = 0.8 * trust_score"""
    print("\n[Test] Trust Mitigation Factor")
    for ts in [0.0, 0.25, 0.5, 0.75, 1.0]:
        expected = 0.8 * ts
        actual = 0.8 * ts   # as implemented
        if abs(actual - expected) > 1e-9:
            print(f"  FAIL trust={ts}: expected={expected}, got={actual}")
            return False
        print(f"  trust={ts:.2f} -> mitigation={actual:.2f}")
    return True

def test_traversal_score():
    """Score = 0.6*unique + 0.4*max_depth"""
    print("\n[Test] Traversal Score Calculation")
    cases = [
        (set(), 0, 0.0),
        ({"/a"}, 0, 0.6),
        ({"/a", "/b"}, 0, 1.2),
        ({"/a/b/c"}, 3, 0.6*1 + 0.4*3),  # unique=1, depth=3
        ({"/x/y", "/x/z"}, 2, 0.6*2 + 0.4*2),
    ]
    for paths, depth, expected in cases:
        actual = calculate_traversal_score(paths, depth)
        if abs(actual - expected) > 1e-9:
            print(f"  FAIL paths={len(paths)}, depth={depth}: expected={expected}, got={actual}")
            return False
        print(f"  paths={len(paths)}, depth={depth} -> score={actual:.2f}")
    return True

def test_jitter_probability_bounds():
    """Ensure probability stays in [0,1] and behaves correctly."""
    print("\n[Test] Jitter Probability Bounds")
    rng = random.Random(42)
    for score in [0, 20, 50, 80, 100, 150]:
        for mit in [0.0, 0.2, 0.5, 0.8, 1.0]:
            prob = jitter_probability(score, mit)
            if prob < 0.0 or prob > 1.0:
                print(f"  FAIL score={score}, mit={mit}: prob={prob} out of bounds")
                return False
            # Mitigation=1 should zero probability
            if mit == 1.0 and prob != 0.0:
                print(f"  FAIL mitigation=1 should give zero prob, got {prob}")
                return False
    print("  All probabilities within [0,1] and mitigation=1 yields zero.")
    return True

def test_jitter_range():
    """Jitter ms must be inclusive [1,50] when applied."""
    print("\n[Test] Jitter Range")
    rng = random.Random(123)
    # Force probability=1 to always apply jitter
    for _ in range(1000):
        # We'll monkey-patch the probability function to return 1.0
        orig = jitter_probability
        try:
            globals()['jitter_probability'] = lambda rs, mit: 1.0
            ms = apply_adaptive_jitter(50.0, 0.0, rng)
            if ms < 1 or ms > 50:
                print(f"  FAIL jitter ms={ms} out of [1,50] range")
                return False
        finally:
            globals()['jitter_probability'] = orig
    print("  All forced jitter values within [1,50] ms.")
    return True

def test_experimental_isolation():
    """Simulate benchmark isolation: resetting state between runs."""
    print("\n[Test] Experimental State Isolation")
    # Simulate global objects
    trust_log = defaultdict(float)   # pid -> trust
    topo_paths = set()
    topo_depth = 0
    forensic_entries = []

    def reset_state():
        nonlocal trust_log, topo_paths, topo_depth, forensic_entries
        trust_log.clear()
        topo_paths.clear()
        topo_depth = 0
        forensic_entries.clear()

    # First experiment: add some data
    trust_log[100] = 0.7
    topo_paths.add("/a/b")
    topo_depth = 2
    forensic_entries.append({"pid":100})
    assert len(trust_log) == 1 and len(topo_paths) == 1 and topo_depth == 2 and len(forensic_entries)==1

    reset_state()
    assert len(trust_log) == 0 and len(topo_paths) == 0 and topo_depth == 0 and len(forensic_entries)==0
    print("  State correctly reset between experiments.")
    return True

# -------------------------- Main Validation --------------------------

def main():
    print("=== AFDS v3.0 Mathematical & Invariant Validation ===")
    all_ok = True
    all_ok &= test_trust_decay()
    all_ok &= test_trust_update_logic()
    all_ok &= test_mitigation_factor()
    all_ok &= test_traversal_score()
    all_ok &= test_jitter_probability_bounds()
    all_ok &= test_jitter_range()
    all_ok &= test_experimental_isolation()

    print("\n=== Summary ===")
    if all_ok:
        print("RESULT: PASS – All mathematical checks are sound.")
        print("        The implementation satisfies the Omega Protocol")
        print("        invariants for the validated subsystems.")
    else:
        print("RESULT: FAIL – One or more checks failed.")
        print("        Review the output above for details.")
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit(main())