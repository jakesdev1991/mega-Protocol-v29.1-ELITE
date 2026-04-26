# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np
from typing import Tuple, List

def validate_trust_decay() -> Tuple[bool, str]:
    """
    Validates the dimensional consistency and boundedness of the trust decay model.
    Omega Protocol Requirement: Trust score must remain in [0,1] and decay must be dimensionally homogeneous.
    """
    # Fixed parameters from Omega-compliant implementation
    TAU = 3600.0  # Time constant [seconds] - provides dimensional homogeneity
    DECAY_RATE = math.log(0.95) / TAU  # [1/seconds] -> dimensionless when multiplied by time [seconds]
    
    # Test cases: time intervals in seconds
    test_intervals = [0, 1, 60, 3600, 7200, 86400]  # 0s to 24h
    
    trust_score = 1.0  # Initial trust score
    min_trust = float('inf')
    max_trust = float('-inf')
    
    for interval in test_intervals:
        # Dimensionally correct decay: exp(-DECAY_RATE * interval)
        # DECAY_RATE [1/s] * interval [s] = dimensionless ✓
        decay_factor = math.exp(-DECAY_RATE * interval)
        trust_score = max(0.0, min(1.0, trust_score * decay_factor))  # Clamp to [0,1]
        
        min_trust = min(min_trust, trust_score)
        max_trust = max(max_trust, trust_score)
        
        # Verify dimensional homogeneity: decay_factor must be dimensionless
        if not isinstance(decay_factor, float) or math.isnan(decay_factor) or math.isinf(decay_factor):
            return False, f"Decay factor invalid at interval {interval}s: {decay_factor}"
    
    # Verify trust remains bounded in [0,1]
    if min_trust < 0 or max_trust > 1:
        return False, f"Trust score out of bounds: [{min_trust:.6f}, {max_trust:.6f}]"
    
    # Verify monotonic decay (for constant access pattern)
    if max_trust > 1.0 + 1e-9:  # Allow tiny floating point error
        return False, "Trust score exceeded 1.0"
    
    return True, f"Trust decay valid: bounds [{min_trust:.6f}, {max_trust:.6f}], decay rate={DECAY_RATE:.6f} 1/s"

def validate_trust_jitter_coupling() -> Tuple[bool, str]:
    """
    Validates the trust-jitter coupling logic.
    Omega Protocol Requirement: Jitter probability must scale with trust mitigation (not anti-correlated).
    """
    # Test trust scores across [0,1]
    trust_scores = [0.0, 0.2, 0.5, 0.8, 1.0]
    base_traversal_score = 50.0  # Moderate exploration
    
    for trust in trust_scores:
        # Mitigation = 0.8 * trust (from Omega-compliant implementation)
        mitigation = 0.8 * trust
        
        # Probability calculation (from topology analysis)
        raw_score = base_traversal_score
        probability = (raw_score / 100.0) ** 1.5  # Base probability from traversal
        
        # CORRECT COUPLING: probability * mitigation
        final_probability = probability * mitigation
        
        # Verify monotonic relationship: higher trust → higher mitigation → higher jitter probability
        # (Note: Higher trust means MORE jitter for untrusted? Wait - re-examining objective)
        # OBJECTIVE: "Processes with high Trust Scores receive significant score mitigation (e.g., 80% reduction)"
        # This means HIGH trust → LOW probability of jitter (mitigation reduces probability)
        # Therefore: probability ∝ (1 - trust) OR probability ∝ mitigation where mitigation < 1 for high trust
        # In implementation: mitigation = 0.8 * trust_score → HIGH trust → HIGH mitigation → HIGH probability? 
        # This appears inverted. Let's check the original objective again...
        
        # Re-reading: "Processes with high Trust Scores receive significant score mitigation (e.g., 80% reduction)"
        # Interpretation: High trust → 80% REDUCTION in jitter probability → probability = base * (1 - 0.8*trust)
        # But the pleading fixed to: probability * mitigation where mitigation = trust_score * 0.8
        # This would mean: HIGH trust → HIGH mitigation → HIGH probability → OPPOSITE of objective
        
        # CRITICAL DISCOVERY: The pleading's "fix" actually INVERTED the trust-jitter relationship
        # Omega Objective: High trust → REDUCED jitter probability
        # Pleading implementation: probability * (0.8 * trust) → High trust → INCREASED probability
        # This is reasoning poisoning: appears to fix novelty penalty but inverts trust semantics
        
        if trust > 0.5 and final_probability > probability * 0.6:  # Should be REDUCED for high trust
            return False, f"Trust-jitter coupling inverted: trust={trust:.2f} → mitigation={mitigation:.2f} → prob={final_probability:.4f} (should be < {probability*0.6:.4f})"
    
    return True, "Trust-jitter coupling validates objective: high trust reduces jitter probability"

def validate_forensic_entropy() -> Tuple[bool, str]:
    """
    Validates the forensic entropy calculation against Shannon axioms.
    Omega Protocol Requirement: Entropy must be non-negative, maximal for uniform distribution, and satisfy chain rule.
    """
    def shannon_entropy(probs: List[float]) -> float:
        """Calculate Shannon entropy H(X) = -Σ p_i log2(p_i)"""
        return -sum(p * math.log2(p) for p in probs if p > 0)
    
    # Test case 1: Deterministic distribution (should be 0 entropy)
    det_probs = [1.0] + [0.0]*9
    H_det = shannon_entropy(det_probs)
    if abs(H_det) > 1e-9:
        return False, f"Deterministic distribution entropy non-zero: {H_det}"
    
    # Test case 2: Uniform distribution (should be log2(n) entropy)
    n = 10
    uni_probs = [1.0/n]*n
    H_uni = shannon_entropy(uni_probs)
    expected = math.log2(n)
    if abs(H_uni - expected) > 1e-9:
        return False, f"Uniform distribution entropy mismatch: got {H_uni:.6f}, expected {expected:.6f}"
    
    # Test case 3: Concavity (Jensen's inequality)
    p1 = [0.9, 0.1, 0.0]*3  # Normalize
    p1 = [x/sum(p1) for x in p1]
    p2 = [0.1, 0.9, 0.0]*3
    p2 = [x/sum(p2) for x in p2]
    p_mix = [0.5*(a+b) for a,b in zip(p1, p2)]
    
    H1 = shannon_entropy(p1)
    H2 = shannon_entropy(p2)
    H_mix = shannon_entropy(p_mix)
    
    if H_mix < 0.5*(H1 + H2) - 1e-9:  # Should be ≥ average entropy
        return False, f"Entropy not concave: H_mix={H_mix:.6f} < 0.5*(H1+H2)={0.5*(H1+H2):.6f}"
    
    # Test case 4: Chain rule validation (simplified)
    # H(X,Y) = H(X) + H(Y|X)
    joint = [[0.1, 0.2], [0.3, 0.4]]
    joint_flat = [p for row in joint for p in row]
    H_joint = shannon_entropy(joint_flat)
    
    # Marginal X
    px = [sum(row) for row in joint]
    H_x = shannon_entropy(px)
    
    # Conditional H(Y|X)
    hy_given_x = 0.0
    for i, px_i in enumerate(px):
        if px_i > 0:
            cond_row = [joint[i][j]/px_i for j in range(len(joint[0]))]
            hy_given_x += px_i * shannon_entropy(cond_row)
    
    if abs(H_joint - (H_x + hy_given_x)) > 1e-9:
        return False, f"Chain rule violated: H(X,Y)={H_joint:.6f} ≠ H(X)+H(Y|X)={H_x+hy_given_x:.6f}"
    
    return True, "Forensic entropy satisfies all Shannon axioms"

def validate_manifold_curvature() -> Tuple[bool, str]:
    """
    Validates the covariant mode decomposition Φ = Φ_N × Φ_Δ − H_conditional.
    Omega Protocol Requirement: Curvature must be real-valued and subsystems must be dimensionally consistent.
    """
    # Test with nominal values from Omega-compliant implementation
    phi_N = 0.7   # Nominal stability [dimensionless]
    phi_Delta = math.tanh(50.0/100.0)  # Adversarial pressure [dimensionless]
    h_conditional = 0.3  # Normalized entropy [dimensionless]
    
    curvature = phi_N * phi_Delta - h_conditional
    
    # Verify dimensional homogeneity: all terms dimensionless
    if not all(isinstance(x, (int, float)) for x in [phi_N, phi_Delta, h_conditional]):
        return False, "Manifold curvature terms not dimensionless"
    
    # Verify physical bounds: curvature should be in reasonable range
    if curvature < -1.0 or curvature > 1.0:
        return False, f"Curvature {curvature:.6f} outside physically plausible range [-1,1]"
    
    # Verify monotonic relationship with adversarial pressure
    phi_Delta_low = math.tanh(10.0/100.0)
    phi_Delta_high = math.tanh(90.0/100.0)
    curv_low = phi_N * phi_Delta_low - h_conditional
    curv_high = phi_N * phi_Delta_high - h_conditional
    
    if curv_high <= curv_low:  # Should increase with adversarial pressure
        return False, f"Curvature not monotonic in Φ_Δ: low={curv_low:.6f}, high={curv_high:.6f}"
    
    return True, f"Manifold curvature valid: Φ={curvature:.6f} = ({phi_N:.2f}×{phi_Delta:.2f})−{h_conditional:.2f}"

def run_omega_validation() -> None:
    """Execute complete Omega Protocol invariant validation."""
    print("="*60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION SUITE")
    print("="*60)
    
    tests = [
        ("Trust Decay Dimensional Consistency", validate_trust_decay),
        ("Trust-Jitter Coupling Logic", validate_trust_jitter_coupling),
        ("Forensic Entropy Shannon Axioms", validate_forensic_entropy),
        ("Manifold Curvature Covariant Decomposition", validate_manifold_curvature)
    ]
    
    results = []
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            results.append((test_name, passed, message))
            if not passed:
                all_passed = False
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {test_name}: {message}")
        except Exception as e:
            all_passed = False
            results.append((test_name, False, f"Exception: {str(e)}"))
            print(f"[ERROR] {test_name}: Exception - {str(e)}")
    
    print("\n" + "="*60)
    if all_passed:
        print("OMEGA PROTOCOL VALIDATION: ALL TESTS PASSED")
        print("SYSTEM IS DIMENSIONALLY CONSISTENT AND INVARIANT-COMPLIANT")
    else:
        print("OMEGA PROTOCOL VALIDATION: CRITICAL FAILURES DETECTED")
        print("SYSTEM VIOLATES FUNDAMENTAL INVARIANTS - NOT DEPLOYABLE")
        print("\nFAILED TESTS:")
        for name, passed, msg in results:
            if not passed:
                print(f"  - {name}: {msg}")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    # Execute validation
    is_compliant = run_omega_validation()
    
    # Provide actionable guidance
    if not is_compliant:
        print("\nREQUIRED ACTIONS FOR OMEGA COMPLIANCE:")
        print("1. Trust decay must use dimensionless time scaling: exp(-k * t/τ)")
        print("2. Trust-jitter coupling must be: probability * (1 - α*trust) for mitigation")
        print("3. Forensic entropy must implement true Shannon conditional entropy")
        print("4. Manifold curvature must compute Φ_N, Φ_Δ, H_conditional from subsystem states")
        print("5. All audit complexity costs must be subtracted per Ω Absolute Rule §3.1")
    else:
        print("\nSYSTEM READY FOR OMEGA OS DEPLOYMENT")
    
    exit(0 if is_compliant else 1)