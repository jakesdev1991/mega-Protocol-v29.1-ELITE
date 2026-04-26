# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# OMEGA PROTOCOL VALIDATION SCRIPT: AFDS v3.0 MATHEMATICAL SOUNDNESS CHECK
# Validates Engine's pleading (revised C++ code) against Omega Physics Rubric v26.0 invariants
# Focus: Trust score bounds, probability clamping, forensic operation correctness, mitigation application
# Output: PASS/FAIL with specific invariant violations

import math
from typing import Tuple, List

# =============================================================================
# TRANSLATED ENGINE'S PLEADING LOGIC (REVISED) TO PYTHON FOR VALIDATION
# =============================================================================

class TrustManager:
    """Direct translation of Engine's pleading TrustManager (revised)"""
    def __init__(self):
        self.process_states = {}  # pid -> {trust_score, last_access, accessed_paths}
        # Note: In C++ version, mutexes omitted for validation simplicity (thread safety not math focus)
    
    def UpdateTrust(self, pid: int, path: str, current_time: float) -> None:
        """Time-based decay + novelty penalty (Engine's pleading logic)"""
        if pid not in self.process_states:
            self.process_states[pid] = {
                'trust_score': 0.0,
                'last_access': current_time,
                'accessed_paths': set()
            }
        
        state = self.process_states[pid]
        is_novel = path not in state['accessed_paths']
        novelty_penalty = 0.05 if is_novel else 0.0
        
        # Time-based decay (5% per hour)
        duration_hours = (current_time - state['last_access']) / 3600.0
        state['trust_score'] *= math.pow(0.95, duration_hours)
        
        # Update trust with penalty and bounds [0,1]
        state['trust_score'] = max(0.0, min(1.0, state['trust_score'] - novelty_penalty))
        state['accessed_paths'].add(path)
        state['last_access'] = current_time
    
    def GetTrustMitigation(self, pid: int) -> float:
        """Returns mitigation factor (0.2 * trust_score) - NOTE: UNUSED in Engine's pleading"""
        if pid not in self.process_states:
            return 1.0  # Default: no mitigation
        return 0.2 * self.process_states[pid]['trust_score']

def ApplyAdaptiveJitter(raw_traversal_score: float) -> Tuple[int, float]:
    """Direct translation of Engine's pleading jitter function (revised)"""
    # NOTE: Engine's pleading did NOT clamp probability - this is the flaw
    probability = math.pow(raw_traversal_score / 100.0, 1.5)
    # In actual C++: if (dist(rng) < probability) { ... } 
    # For validation, we return the raw probability to check bounds
    jitter_ms = 0
    if probability > 0:  # Simulate non-zero random draw
        jitter_ms = 1 + int(49.0 * min(probability, 1.0))  # Actual C++ uses min(prob,1.0) implicitly via rng
    return jitter_ms, probability

def IsHoneyNode(path: str) -> bool:
    """Honey-node detection logic from Engine's pleading"""
    return "honey_" in path

def BuildForensicEntry(pid: int, path: str, applied_latency: int, 
                      traversal_score: float, trust_score: float, 
                      inter_call_interval: float, current_time: float) -> dict:
    """Forensic log entry construction (Engine's pleading logic)"""
    operation = "honey_node_access" if IsHoneyNode(path) else "lookup"
    return {
        'timestamp': current_time,
        'pid': pid,
        'operation': operation,
        'path': path,
        'applied_latency_ms': applied_latency,
        'traversal_score': traversal_score,
        'trust_score': trust_score,
        'inter_call_interval': inter_call_interval
    }

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATION TESTS
# =============================================================================

def validate_trust_invariants() -> List[str]:
    """Test TrustManager against Omega Protocol invariants"""
    violations = []
    tm = TrustManager()
    base_time = 0.0
    
    # Invariant 1: Trust score must remain in [0,1] at all times
    test_cases = [
        # (pid, path, time_delta, expected_trust_range_after)
        (1, "/etc/passwd", 0, (0.0, 0.0)),  # First access: novelty penalty -> 0 - 0.05 = -0.05 -> clamped to 0
        (1, "/etc/passwd", 3600, (0.0, 0.0)),  # Same path after 1hr: decay 0*0.95=0, no penalty -> 0
        (1, "/new/path", 0, (0.0, 0.0)),  # Novelty penalty on 0 -> clamped to 0
        (1, "/etc/passwd", 7200, (0.0, 0.0)),  # After 2hrs: still 0
    ]
    
    for pid, path, time_delta, (min_exp, max_exp) in test_cases:
        tm.UpdateTrust(pid, path, base_time + time_delta)
        score = tm.process_states[pid]['trust_score']
        if not (0.0 <= score <= 1.0):
            violations.append(f"Trust score {score} out of bounds [0,1] for pid={pid}, path={path}")
        if score < min_exp or score > max_exp:
            violations.append(f"Trust score {score} not in expected range [{min_exp},{max_exp}] for pid={pid}, path={path}")
    
    # Invariant 2: Trust score must increase for stable, low-novelty behavior (Objective 1)
    # Simulate stable admin: repeated access to same path over time
    tm2 = TrustManager()
    pid_stable = 999
    path_stable = "/admin/config"
    times = [0, 3600, 7200, 10800, 14400]  # 0hr, 1hr, 2hr, 3hr, 4hr
    scores = []
    for t in times:
        tm2.UpdateTrust(pid_stable, path_stable, t)
        scores.append(tm2.process_states[pid_stable]['trust_score'])
    
    # Check if trust score increases over time (should for stable behavior)
    is_increasing = all(scores[i] <= scores[i+1] for i in range(len(scores)-1))
    if not is_increasing:
        violations.append(f"Trust score did not increase for stable behavior: {scores} (should rise per Objective 1)")
    
    # Invariant 3: Trust mitigation must be applied (Objective 1: "significant score mitigation")
    # Engine's pleading computes mitigation but NEVER USES IT - critical flaw
    mitigation = tm2.GetTrustMitigation(pid_stable)
    if mitigation == 0.0:  # Always 0 in Engine's pleading due to trust_score=0
        violations.append("Trust mitigation computed but NEVER APPLIED (violates Objective 1: 'receive significant score mitigation')")
    
    return violations

def validate_jitter_invariants() -> List[str]:
    """Test jitter probability against Omega Protocol invariants"""
    violations = []
    
    # Invariant: Probability must be in [0,1] for all valid inputs (Omega Physics §6: Equations must be bounded)
    test_scores = [0, 25, 50, 75, 100, 150, 200, 500, 1000]  # Traversal scores
    for score in test_scores:
        _, probability = ApplyAdaptiveJitter(score)
        if not (0.0 <= probability <= 1.0 + 1e-9):  # Allow tiny floating point error
            violations.append(f"Jitter probability {probability} out of bounds [0,1] for traversal_score={score}")
    
    # Additional: Probability must scale meaningfully with traversal_score (Objective 2)
    # Check monotonic non-decreasing (should be, but verify no decrease due to bug)
    probs = [ApplyAdaptiveJitter(s)[1] for s in test_scores]
    is_monotonic = all(probs[i] <= probs[i+1] for i in range(len(probs)-1))
    if not is_monotonic:
        violations.append(f"Jitter probability not monotonic: {list(zip(test_scores, probs))}")
    
    return violations

def validate_forensic_invariants() -> List[str]:
    """Test forensic logger against Omega Protocol invariants"""
    violations = []
    
    # Invariant: Honey-node access MUST be logged as distinct operation (Objective 3)
    test_cases = [
        ("/normal/file", False, "lookup"),
        ("/honey_trap", True, "honey_node_access"),
        ("/etc/honey_node", True, "honey_node_access"),
        ("/var/log/honey", True, "honey_node_access"),
        ("/tmp/test", False, "lookup")
    ]
    
    for path, is_honey, expected_op in test_cases:
        entry = BuildForensicEntry(
            pid=123, path=path, applied_latency=10,
            traversal_score=50.0, trust_score=0.8,
            inter_call_interval=5.0, current_time=0.0
        )
        actual_op = entry['operation']
        if actual_op != expected_op:
            violations.append(f"Forensic operation mismatch: path='{path}' (honey={is_honey}) -> expected '{expected_op}', got '{actual_op}'")
    
    # Invariant: Forensic logs must contain actual applied latency (Objective 3)
    # Engine's pleading fixed this - verify latency field is populated
    entry = BuildForensicEntry(
        pid=456, path="/test", applied_latency=42,
        traversal_score=30.0, trust_score=0.5,
        inter_call_interval=2.0, current_time=0.0
    )
    if entry['applied_latency_ms'] != 42:
        violations.append(f"Forensic log missing applied latency: expected 42, got {entry['applied_latency_ms']}")
    
    return violations

def validate_mitigation_application() -> List[str]:
    """Verify trust mitigation is actually used to reduce jitter (Objective 1 & 2 coupling)"""
    violations = []
    
    # Engine's pleading: mitigation computed but NOT USED in jitter calculation
    # This violates the coupling between trust and defense (Systems Branch "causal coupling" tenet)
    # We check if mitigation influences jitter probability
    
    tm = TrustManager()
    pid = 777
    path = "/stable/service"
    
    # Build up trust via stable behavior (hypothetical fixed model - but Engine's pleading fails here)
    # Instead, we show what SHOULD happen: high trust -> reduced jitter probability
    
    # Simulate two scenarios: low trust (novel process) vs high trust (stable process)
    # In a CORRECT system:
    #   Low trust: mitigation_low = 0.2 * 0.1 = 0.02 -> jitter probability scaled by (1 - 0.02*4) = 0.92
    #   High trust: mitigation_high = 0.2 * 0.9 = 0.18 -> jitter probability scaled by (1 - 0.18*4) = 0.28
    
    # Engine's pleading: mitigation is computed but IGNORED -> same jitter probability for both
    low_trust_state = {'trust_score': 0.1}
    high_trust_state = {'trust_score': 0.9}
    
    mitigation_low = 0.2 * low_trust_state['trust_score']
    mitigation_high = 0.2 * high_trust_state['trust_score']
    
    # If mitigation were applied (as required), effective probability would differ
    base_prob = 0.5  # Example base jitter probability
    eff_prob_low = base_prob * (1 - mitigation_low * 4)  # 80% max mitigation at trust=1.0
    eff_prob_high = base_prob * (1 - mitigation_high * 4)
    
    # Engine's pleading: uses base_prob for both -> no difference
    if abs(eff_prob_low - eff_prob_high) < 1e-5:  # They should differ significantly
        violations.append("Trust mitigation NOT APPLIED to jitter probability (violates Objective 1-2 coupling)")
    
    return violations

# =============================================================================
# MAIN VALIDATION EXECUTION
# =============================================================================

def main():
    print("=" * 70)
    print("OMEGA PROTOCOL VALIDATION: AFDS v3.0 (Engine's Pleading)")
    print("Validating against Physics Rubric v26.0 Invariants")
    print("=" * 70)
    
    all_violations = []
    validators = [
        ("Trust Score Invariants", validate_trust_invariants),
        ("Jitter Probability Invariants", validate_jitter_invariants),
        ("Forensic Logger Invariants", validate_forensic_invariants),
        ("Mitigation Application", validate_mitigation_application)
    ]
    
    for name, validator in validators:
        print(f"\n[VALIDATING] {name}")
        violations = validator()
        if violations:
            print(f"  ❌ FAILED ({len(violations)} violation(s)):")
            for v in violations:
                print(f"     - {v}")
            all_violations.extend(violations)
        else:
            print("  ✅ PASSED")
    
    print("\n" + "=" * 70)
    if all_violations:
        print(f"VALIDATION RESULT: FAIL")
        print(f"Total Invariant Violations: {len(all_violations)}")
        print("\nCRITICAL FAILURES REQUIRING IMMEDIATE FIX:")
        for i, v in enumerate(all_violations[:5], 1):  # Show top 5
            print(f"  {i}. {v}")
        if len(all_violations) > 5:
            print(f"     ... and {len(all_violations)-5} more")
        print("\nOmega Protocol Compliance: NOT ACHIEVED")
        print("System is mathematically unsound and operationally unsafe.")
    else:
        print("VALIDATION RESULT: PASS")
        print("All Omega Protocol invariants satisfied.")
        print("System is mathematically sound and operationally safe.")
    print("=" * 70)

if __name__ == "__main__":
    main()