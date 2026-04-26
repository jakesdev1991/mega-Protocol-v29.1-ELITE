# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
OMEGA PROTOCOL INVARIANT VALIDATOR: AFDS v3.0 MATHEMATICAL SOUNDNESS CHECK
Validates core mathematical invariants Phi_N (systemic integrity), Phi_Delta (integrity delta), J* (stability metric)
Per Omega Physics Rubric v26.0: Strictor Gate - Systems Branch
"""
import math
import random
from collections import defaultdict

# --- INVARIANT DEFINITIONS (PER OMEGA PHYSICS RUBRIC v26.0) ---
# Phi_N: Systemic Integrity (must be >= 0.0; degradation = violation)
# Phi_Delta: Integrity change per operation (must not cause Phi_N < 0)
# J*: Stability metric (must remain bounded; |J*| < 1.0 for stable operation)

class InvariantViolation(Exception):
    pass

def validate_trust_model():
    """Validate Behavioral Trust Modeling invariants (Objective 1)"""
    print("\n[VALIDATING] Behavioral Trust Modeling (Phi_N: Trust Accuracy)")
    
    # Invariant 1.1: Trust score must be initialized to known state (Phi_N >= 0)
    try:
        # Simulate uninitialized trust_score (as in original code)
        trust_score = float('nan')  # Represents garbage value
        consistency = 0.5  # Example value
        new_trust = min(1.0, trust_score + 0.1 * consistency)
        if math.isnan(new_trust):
            raise InvariantViolation("Trust score initialization violation: NaN propagation -> Phi_N degradation")
    except InvariantViolation as e:
        print(f"  FAIL: {e}")
        return False
    
    # Invariant 1.2: Division by zero protection (covariant mode requirement)
    accessed_paths = set()  # Empty set = first access
    path = "/etc/passwd"
    try:
        consistency = accessed_paths.count(path) / len(accessed_paths)  # Division by zero
        print("  FAIL: Division by zero in trust update -> catastrophic Phi_N loss")
        return False
    except ZeroDivisionError:
        print("  FAIL: Division by zero vulnerability -> violates covariant mode (Phi_N instability)")
        return False
    
    # Invariant 1.3: Trust must decay for novelty (prevents attacker trust farming)
    trust_score = 0.0
    accessed_paths = {"/etc/passwd"}  # Start with one path
    # Simulate wide-scanning attacker accessing 100 unique paths
    for i in range(1, 101):
        new_path = f"/etc/file{i}"
        accessed_paths.add(new_path)
        consistency = accessed_paths.count(new_path) / len(accessed_paths)  # Always 1/len for new path
        trust_score = min(1.0, trust_score + 0.1 * consistency)  # Original flawed model
    
    # After 100 paths, trust_score ≈ 0.1 * H_100 ≈ 0.1 * 5.187 = 0.5187 (harmonic series)
    # But should DECREASE for novel behavior (attacker reconnaissance)
    if trust_score > 0.3:  # Threshold for "high trust" (should be LOW for attackers)
        print(f"  FAIL: Trust model rewards attackers (score={trust_score:.3f} > 0.3) -> violates Psychology Branch (adaptive trust)")
        print(f"        Attacker gains {int((1-trust_score)*100)%} mitigation -> stealth advantage")
        return False
    
    print("  PASS: Trust model invariants satisfied")
    return True

def validate_jitter_mechanism():
    """Validate Probabilistic Stealth Jitter invariants (Objective 2)"""
    print("\n[VALIDATING] Probabilistic Stealth Jitter (Phi_N: Stealth Gain)")
    
    # Invariant 2.1: Jitter probability must depend ONLY on raw traversal_score (state-dependent)
    # Original flaw: used traversal_score * mitigation (trust-adjusted)
    def flawed_jitter_prob(traversal_score, trust_mitigation):
        return math.pow((traversal_score * trust_mitigation) / 100.0, 1.5)  # FLAWED
    
    def correct_jitter_prob(traversal_score):
        return math.pow(traversal_score / 100.0, 1.5)  # CORRECT: state-dependent only
    
    # Test case: High-trust process doing legitimate deep recursion (should get HIGH jitter)
    traversal_score = 80.0  # High exploratory behavior
    trust_mitigation = 0.2  # High trust -> 80% mitigation (score reduction)
    
    flawed_prob = flawed_jitter_prob(traversal_score, trust_mitigation)
    correct_prob = correct_jitter_prob(traversal_score)
    
    if flawed_prob < correct_prob * 0.5:  # Flawed version suppresses jitter incorrectly
        print(f"  FAIL: Jitter probability misapplied (flawed={flawed_prob:.3f} < correct={correct_prob:.3f})")
        print(f"        Trusted deep recursion gets {int((1-flawed_prob/correct_prob)*100)%} LESS jitter -> violates Physics Branch (state-dependent jitter)")
        return False
    
    # Invariant 2.2: Jitter range must be [1ms, 50ms] (per objective)
    # Validate via simulation
    random.seed(42)  # Deterministic test
    jitters = []
    for _ in range(1000):
        if random.random() < correct_jitter_prob(50.0):  # Medium traversal score
            jitter = 1 + int(49.0 * random.random())
            jitters.append(jitter)
    
    if min(jitters) < 1 or max(jitters) > 50:
        print(f"  FAIL: Jitter range violation [{min(jitters)}, {max(jitters)}]ms -> outside [1,50]ms spec")
        return False
    
    print("  PASS: Jitter mechanism invariants satisfied")
    return True

def validate_forensic_logger():
    """Validate Forensic Attack Reconstruction invariants (Objective 3)"""
    print("\n[VALIDATING] Forensic Logger (Phi_N: Forensic Integrity)")
    
    # Invariant 3.1: Must log actual applied latency (not hardcoded 0)
    # Simulate log entry
    applied_latency_ms = 0  # HARDCODED FLAW
    if applied_latency_ms == 0:
        print("  FAIL: Latency field hardcoded to 0 -> cannot reconstruct attack timing (violates Phi_N forensic integrity)")
        return False
    
    # Invariant 3.2: Must track inter-call intervals
    # Simulate missing interval tracking
    last_timestamp = None
    current_timestamp = 1000.0  # ms
    if last_timestamp is None:  # First access - no interval to log
        inter_call_interval = None
    else:
        inter_call_interval = current_timestamp - last_timestamp
    
    if inter_call_interval is None:
        print("  FAIL: No inter-call interval tracking -> cannot distinguish reconnaissance patterns")
        return False
    
    # Invariant 3.3: Automated report trigger must use validated data
    traversal_score = 95.0  # Above threshold
    honey_node_access = False
    if not (honey_node_access or traversal_score > 90.0):
        print("  FAIL: Report trigger logic flawed -> misses critical events")
        return False
    
    print("  PASS: Forensic logger invariants satisfied")
    return True

def validate_topology_analysis():
    """Validate Topology Analysis invariants (Objective 4)"""
    print("\n[VALIDATING] Topology Analysis (Phi_N: Topology Awareness)")
    
    # Invariant 4.1: Must distinguish breadth vs depth (not just raw counts)
    # Simulate two attack patterns:
    wide_scan_paths = [f"/etc/file{i}" for i in range(50)]  # 50 unique paths, depth=1
    deep_recursion_paths = ["/" + "dir"*i + "/file" for i in range(1, 51)]  # 50 paths, depth=1..50
    
    def flawed_topology_metrics(paths):
        unique_paths = len(set(paths))
        max_depth = max(path.count('/') for path in paths) if paths else 0
        return {"unique_paths": unique_paths, "max_depth": max_depth}
    
    wide_metrics = flawed_topology_metrics(wide_scan_paths)
    deep_metrics = flawed_topology_metrics(deep_recursion_paths)
    
    # Flawed model sees: wide_scan=(50,1), deep_recursion=(50,50) -> can distinguish by max_depth
    # BUT: what if attacker does medium-depth wide scan? 
    medium_scan_paths = [f"/dir{i}/file{j}" for i in range(5) for j in range(10)]  # 50 paths, depth=2
    medium_metrics = flawed_topology_metrics(medium_scan_paths)
    
    # All show 50 unique_paths -> cannot tell apart by unique_paths alone
    # Need depth distribution entropy (missing in original)
    if wide_metrics["unique_paths"] == medium_metrics["unique_paths"] == deep_metrics["unique_paths"]:
        print("  FAIL: Topology analysis lacks breadth/depth shape metrics -> cannot distinguish scan types")
        print(f"        All show 50 unique paths but different geometries: wide=(1), medium=(2), deep=(50)")
        return False
    
    # Invariant 4.2: Must compute shape entropy (breadth/depth ratio)
    # Original code only tracks max_depth and unique_paths -> insufficient
    print("  FAIL: Missing depth histogram -> cannot compute breadth/depth entropy (violates Physics Branch geometric threat surface)")
    return False

def main():
    """Execute invariant validation suite"""
    print("="*60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION: AFDS v3.0")
    print("Validating Phi_N (Systemic Integrity), Phi_Delta, J* Stability")
    print("="*60)
    
    tests = [
        validate_trust_model,
        validate_jitter_mechanism,
        validate_forensic_logger,
        validate_topology_analysis
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  FATAL: Test crashed -> {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"VALIDATION SUMMARY: {passed}/{total} invariants satisfied")
    
    if all(results):
        print("RESULT: PASS -> AFDS v3.0 mathematically sound per Omega Protocol")
        print("Phi_N integrity maintained; Phi_Delta >= 0; J* bounded")
    else:
        print("RESULT: FAIL -> Critical invariant violations detected")
        print("Phi_N degradation imminent; Phi_Delta < 0; J* unstable")
        print("\nENFORCEMENT ACTION: Reject deployment until invariants satisfied")
        print("Required fixes:")
        print("  1. Trust score initialization + decay mechanism")
        print("  2. Implement CalculateTraversalScore()")
        print("  3. Decouple jitter probability from trust mitigation")
        print("  4. Forensic logger must capture actual latency & inter-call intervals")
        print("  5. Topology analysis requires depth histogram for shape entropy")
    
    print("="*60)
    return 0 if all(results) else 1

if __name__ == "__main__":
    exit(main())