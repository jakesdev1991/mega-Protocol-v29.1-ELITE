# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Validation Script for AFDS v3.0 Trust Model Fix
# This script validates the proposed trust model against Omega Protocol invariants
# Objective: Ensure trust decreases for novelty (wide scans) and increases for stability

import math
from typing import List

def simulate_trust_model(
    access_sequence: List[bool],  # True = novel path, False = familiar path
    access_decay: float = 0.99,
    learning_rate: float = 0.01,
    time_decay_rate: float = 0.05  # 5% per hour (for inactivity)
) -> List[float]:
    """
    Simulates the proposed trust model update rule:
    trust = trust * access_decay + (1.0 if familiar else 0.0) * learning_rate
    Then applies time-based decay for inactivity (simulated as hours between accesses)
    
    For validation, we assume:
    - Each access is 1 second apart (so time_decay per access = (0.95)^(1/3600) ≈ 0.999986)
    - Focus on access-based behavior as primary novelty detector
    """
    trust = 0.0
    time_decay_per_access = math.pow(1.0 - time_decay_rate, 1/3600)  # ~0.999986
    trust_history = [trust]
    
    for is_novel in access_sequence:
        # Familiarity: 1.0 if familiar (not novel), 0.0 if novel
        familiarity = 0.0 if is_novel else 1.0
        
        # Access-based update (core novelty detection)
        trust = trust * access_decay + familiarity * learning_rate
        
        # Time-based decay (inactivity penalty)
        trust *= time_decay_per_access
        
        # Clamp to [0,1]
        trust = max(0.0, min(1.0, trust))
        trust_history.append(trust)
    
    return trust_history

def validate_trust_model():
    """Validate trust model against Omega Protocol requirements"""
    print("=== AFDS v3.0 Trust Model Validation ===\n")
    
    # Test 1: Trust must DECREASE during wide scan (novelty)
    print("Test 1: Wide Scan Behavior (100 novel paths)")
    wide_scan = [True] * 100  # 100 consecutive novel paths
    trust_wide = simulate_trust_model(wide_scan)
    initial_trust = trust_wide[0]
    final_trust = trust_wide[-1]
    print(f"  Initial trust: {initial_trust:.4f}")
    print(f"  Final trust after 100 novel paths: {final_trust:.4f}")
    print(f"  Trust change: {final_trust - initial_trust:.4f} (should be NEGATIVE)")
    assert final_trust < initial_trust, "Trust MUST decrease during wide scan"
    print("  ✓ PASS: Trust decreases with novelty\n")
    
    # Test 2: Trust must INCREASE during stable behavior
    print("Test 2: Stable Behavior (100 familiar paths after warmup)")
    # First establish some familiarity with 50 novel paths then 50 familiar
    warmup = [True]*50 + [False]*50  # Build familiarity
    stable_test = [False]*100       # Then 100 familiar accesses
    full_sequence = warmup + stable_test
    trust_stable = simulate_trust_model(full_sequence)
    warmup_end = trust_stable[len(warmup)]
    stable_end = trust_stable[-1]
    print(f"  Trust after warmup (50 novel + 50 familiar): {warmup_end:.4f}")
    print(f"  Trust after 100 familiar accesses: {stable_end:.4f}")
    print(f"  Trust change: {stable_end - warmup_end:.4f} (should be POSITIVE)")
    assert stable_end > warmup_end, "Trust MUST increase during stable behavior"
    print("  ✓ PASS: Trust increases with stability\n")
    
    # Test 3: Attacker cannot launder trust via brief low-novelty behavior
    print("Test 3: Trust Laundering Resistance")
    # Phase 1: Wide scan to establish low trust
    phase1 = [True]*200  # 200 novel paths -> very low trust
    # Phase 2: Brief low-novelty behavior (attacker tries to build trust)
    phase2 = [False]*20   # Only 20 familiar accesses
    # Phase 3: Another wide scan (should see low trust)
    phase3 = [True]*200
    full_sequence = phase1 + phase2 + phase3
    trust_launder = simulate_trust_model(full_sequence)
    
    trust_after_phase1 = trust_launder[len(phase1)]
    trust_after_phase2 = trust_launder[len(phase1)+len(phase2)]
    trust_after_phase3 = trust_launder[-1]
    
    print(f"  Trust after Phase 1 (200 novel): {trust_after_phase1:.4f}")
    print(f"  Trust after Phase 2 (+20 familiar): {trust_after_phase2:.4f}")
    print(f"  Trust after Phase 3 (+200 novel): {trust_after_phase3:.4f}")
    
    # Critical check: Trust after Phase 3 should be SIMILAR to after Phase 1
    # (i.e., the brief familiar behavior didn't significantly boost trust for next scan)
    trust_diff = abs(trust_after_phase3 - trust_after_phase1)
    print(f"  Trust difference (Phase3 vs Phase1): {trust_diff:.4f}")
    assert trust_diff < 0.05, "Brief low-novelty behavior should NOT significantly boost trust for subsequent scans"
    print("  ✓ PASS: Trust laundering attempt fails\n")
    
    # Test 4: Boundary conditions
    print("Test 4: Boundary Validation")
    # Trust must never exceed 1.0 or go below 0.0
    extreme_sequence = [True]*1000 + [False]*1000  # Extreme novel then familiar
    trust_extreme = simulate_trust_model(extreme_sequence)
    max_trust = max(trust_extreme)
    min_trust = min(trust_extreme)
    print(f"  Max trust observed: {max_trust:.6f} (must be ≤ 1.0)")
    print(f"  Min trust observed: {min_trust:.6f} (must be ≥ 0.0)")
    assert max_trust <= 1.0 + 1e-9, "Trust exceeded upper bound"
    assert min_trust >= 0.0 - 1e-9, "Trust exceeded lower bound"
    print("  ✓ PASS: Trust remains in [0,1] bounds\n")
    
    print("=== ALL TESTS PASSED ===")
    print("The trust model satisfies Omega Protocol invariants:")
    print("- Trust decreases for novelty (wide scans)")
    print("- Trust increases for stability (repeated access)")
    print("- Resists trust laundering attacks")
    print("- Maintains strict [0,1] bounds")
    return True

if __name__ == "__main__":
    validate_trust_model()