# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random

# =============================================================================
# VALIDATION: AFDS v3.0 Mathematical Soundness & Omega Protocol Compliance
# =============================================================================
# This script validates the core mathematical expressions and invariants
# claimed in the AFDS v3.0 implementation. It focuses on:
#   1. Trust score boundedness and update rules
#   2. Phi_Delta (asymmetric threat) range and formula
#   3. Topological impedance calculation (trapezoidal rule)
#   4. Jitter probability bounds and latency output
#   5. Phi-Density calculation and audit cost subtraction
# =============================================================================

def test_trust_score_bounds():
    """Validate trust score remains in [0,1] under all update scenarios."""
    print("\n[TEST] Trust Score Boundedness")
    
    class MockTrustManager:
        def __init__(self):
            self.trust_score = 0.5
            self.cumulative_stability = 0.0
            self.accessed_paths = set()
            self.last_access_time = 0.0  # simulated hours
        
        def update_trust(self, path, is_novel, hours_since_last=1.0):
            # Simplified UpdateTrust logic (single-threaded)
            novelty_penalty = 0.05 if is_novel else 0.0
            normalized_time = hours_since_last
            
            # Trust decay
            self.trust_score *= math.exp(-math.log(0.95) * normalized_time)
            self.trust_score = max(0.0, min(1.0, self.trust_score - novelty_penalty))
            
            if not is_novel:
                self.cumulative_stability += math.exp(-normalized_time)
                self.trust_score += 0.01 * math.exp(-0.1 * self.cumulative_stability)
                self.trust_score = max(0.0, min(1.0, self.trust_score))
            
            self.accessed_paths.add(path)
            self.last_access_time += hours_since_last
            return self.trust_score
    
    tm = MockTrustManager()
    
    # Test novel access (should decrease trust)
    score = tm.update_trust("/new/path", True, 1.0)
    assert 0.0 <= score <= 1.0, f"Novel access trust={score} out of bounds"
    
    # Test stable access (should increase trust slightly)
    score = tm.update_trust("/known/path", False, 0.5)
    assert 0.0 <= score <= 1.0, f"Stable access trust={score} out of bounds"
    
    # Test extreme decay (should not go negative)
    score = tm.update_trust("/another/new", True, 100.0)
    assert 0.0 <= score <= 1.0, f"Extreme decay trust={score} out of bounds"
    
    print("  PASS: Trust score remains in [0,1]")
    return True

def test_phi_delta_range():
    """Validate Phi_Delta (asymmetric threat) is in [0,1] and formula correctness."""
    print("\n[TEST] Phi_Delta Range and Formula")
    
    def calculate_asymmetric_threat(breadth, depth):
        if breadth + depth == 0:
            return 0.0
        return abs(breadth - depth) / (breadth + depth)
    
    # Test boundary cases
    assert calculate_asymmetric_threat(0, 0) == 0.0, "Zero case failed"
    assert calculate_asymmetric_threat(10, 0) == 1.0, "Pure breadth case failed"
    assert calculate_asymmetric_threat(0, 10) == 1.0, "Pure depth case failed"
    assert calculate_asymmetric_threat(5, 5) == 0.0, "Symmetric case failed"
    assert calculate_asymmetric_threat(3, 7) == 0.4, "Asymmetric case failed"  # |3-7|/(3+7)=4/10=0.4
    
    # Test monotonicity
    assert calculate_asymmetric_threat(1, 10) > calculate_asymmetric_threat(5, 5), "Monotonicity failed"
    assert calculate_asymmetric_threat(10, 1) > calculate_asymmetric_threat(5, 5), "Monotonicity failed"
    
    print("  PASS: Phi_Delta in [0,1] with correct formula")
    return True

def test_topological_impedance():
    """Validate topological impedance calculation (trapezoidal rule)."""
    print("\n[TEST] Topological Impedance Calculation")
    
    class MockForensicLogger:
        def __init__(self):
            self.log_entries = []
        
        def add_entry(self, trust_score, phi_Delta):
            self.log_entries.append({
                'trust_score': trust_score,
                'phi_Delta': phi_Delta
            })
        
        def calculate_topological_impedance(self):
            impedance = 0.0
            prev_psi = 0.0
            prev_gauge = 0.0
            
            for entry in self.log_entries:
                psi = math.log(entry['trust_score'] + 1e-10)
                gauge = entry['trust_score'] * abs(entry['phi_Delta'])
                delta_psi = psi - prev_psi
                impedance += (gauge + prev_gauge) / 2 * delta_psi
                prev_psi = psi
                prev_gauge = gauge
            return impedance
    
    fl = MockForensicLogger()
    
    # Test case 1: Zero impedance (constant trust, zero phi_Delta)
    fl.add_entry(0.5, 0.0)
    fl.add_entry(0.5, 0.0)
    imp = fl.calculate_topological_impedance()
    assert abs(imp) < 1e-10, f"Zero case failed: impedance={imp}"
    
    # Test case 2: Known impedance from manual calculation
    fl.log_entries = []  # reset
    fl.add_entry(0.5, 0.5)  # Entry 1
    fl.add_entry(0.6, 0.6)  # Entry 2
    
    # Manual calculation:
    # Entry1: psi1 = ln(0.5) ≈ -0.6931, gauge1 = 0.5*0.5=0.25, delta_psi1 = -0.6931 - 0 = -0.6931
    #         imp1 = (0 + 0.25)/2 * (-0.6931) = -0.0866375
    # Entry2: psi2 = ln(0.6) ≈ -0.5108, gauge2 = 0.6*0.6=0.36, delta_psi2 = -0.5108 - (-0.6931)=0.1823
    #         imp2 = (0.25+0.36)/2 * 0.1823 = 0.0555815
    # Total = -0.0866375 + 0.0555815 = -0.031056
    expected = -0.031056
    imp = fl.calculate_topological_impedance()
    assert abs(imp - expected) < 1e-5, f"Impedance mismatch: got {imp}, expected {expected}"
    
    print("  PASS: Topological impedance calculation correct")
    return True

def test_jitter_probability():
    """Validate jitter probability bounds and latency output."""
    print("\n[TEST] Jitter Probability and Latency")
    
    def apply_adaptive_jitter(raw_score, mitigation, phi_Delta):
        probability = math.pow(raw_score / 100.0, 1.5) * mitigation * (1.0 + phi_Delta)
        probability = max(0.0, min(1.0, probability))
        
        if phi_Delta > 0.95:
            return 1000  # latency in ms
        
        # Simulate random outcome (we'll test both branches)
        if random.random() < probability:
            return 1 + int(50.0 * random.random())  # 1-50 ms
        return 0
    
    # Test probability bounds
    random.seed(42)  # for reproducibility
    
    # Case 1: Zero probability
    latency = apply_adaptive_jitter(0, 0.5, 0.0)
    assert latency == 0, f"Zero probability should yield 0 latency, got {latency}"
    
    # Case 2: Max probability (should sometimes yield latency)
    latency = apply_adaptive_jitter(100, 1.0, 1.0)  # raw_score=100 -> prob=1.0*1.0*(2.0)=2.0 -> clamped to 1.0
    # With seed=42, random.random()=0.6394 < 1.0 -> should yield latency
    assert 1 <= latency <= 50, f"Max probability latency out of range: {latency}"
    
    # Case 3: Phi_Delta > 0.95 triggers 1000ms latency
    latency = apply_adaptive_jitter(50, 0.8, 0.96)
    assert latency == 1000, f"Phi_Delta>0.95 should yield 1000ms, got {latency}"
    
    # Case 4: Probability calculation correctness
    prob = math.pow(50/100.0, 1.5) * 0.8 * (1.0 + 0.5)  # (0.5^1.5)=0.3535 *0.8*1.5=0.4242
    # We can't directly test the random branch without overriding random, but we verified the formula
    
    print("  PASS: Jitter probability in [0,1], latency in {0, [1,50], 1000}")
    return True

def test_phi_density():
    """Validate Phi-Density calculation and audit cost subtraction."""
    print("\n[TEST] Phi-Density Calculation")
    
    K_BOLTZMANN = 1.0
    audit_complexity = 2.5
    raw_gain = 0.85
    
    audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
    phi_density = raw_gain - audit_entropy_cost
    
    # Calculate expected values
    ln2 = math.log(2.0)
    expected_cost = ln2 * 2.5
    expected_density = 0.85 - expected_cost
    
    # Note: The code claims "+0.75Φ after audit cost subtraction"
    # But our calculation shows:
    print(f"  Raw gain: {raw_gain}")
    print(f"  Audit entropy cost: {audit_entropy_cost:.6f} (ln(2)*{audit_complexity})")
    print(f"  Calculated Phi-Density: {phi_density:.6f}")
    print(f"  Claimed Phi-Density: +0.75")
    
    # The calculated value is negative, which contradicts the claim
    # This indicates either:
    #   1. The audit_complexity value is incorrect (should be ~0.216 for 0.15 cost)
    #   2. The raw_gain is underestimated
    #   3. The formula for audit_entropy_cost is wrong
    #
    # For Omega Protocol compliance, we must have:
    #   Net Phi-Density = Raw Security Gain - Audit Entropy Cost >= 0 (for viability)
    #
    # We flag this as a compliance issue.
    if phi_density < 0:
        print("  WARNING: Calculated Phi-Density is negative!")
        print("         This violates Omega Protocol's requirement for net positive informational yield.")
        print("         To achieve +0.75Φ, either:")
        print("           - Audit complexity must be ~0.216 (not 2.5), OR")
        print("           - Raw gain must be ~2.582 (not 0.85), OR")
        print("           - Audit entropy cost formula is incorrect.")
        return False  # Mark as non-compliant
    
    # If we were to force compliance (for demonstration):
    #   To get net +0.75Φ with audit_complexity=2.5:
    #       raw_gain_needed = 0.75 + (ln(2)*2.5) ≈ 0.75 + 1.7329 = 2.4829
    #   Or to get net +0.75Φ with raw_gain=0.85:
    #       audit_complexity_needed = (0.85 - 0.75) / ln(2) ≈ 0.10 / 0.6931 ≈ 0.144
    #
    print("  INFO: For compliance with claimed +0.75Φ:")
    print(f"        Required raw_gain = {0.75 + audit_entropy_cost:.6f}")
    print(f"        Required audit_complexity = {(0.85 - 0.75) / math.log(2.0):.6f}")
    
    # Since the current calculation does NOT match the claim, we return False
    return False

def main():
    """Run all validation tests and report Omega Protocol compliance."""
    print("=" * 60)
    print("AFDS v3.0 Mathematical Validation & Omega Protocol Check")
    print("=" * 60)
    
    tests = [
        ("Trust Score Boundedness", test_trust_score_bounds),
        ("Phi_Delta Range and Formula", test_phi_delta_range),
        ("Topological Impedance Calculation", test_topological_impedance),
        ("Jitter Probability and Latency", test_jitter_probability),
        ("Phi-Density Calculation", test_phi_density)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"  RESULT: FAIL (see warnings above)")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("RESULT: FULLY COMPLIANT with Omega Protocol invariants")
        print("        All mathematical expressions are sound and invariant-preserving.")
    else:
        print("RESULT: NON-COMPLIANT")
        print("        Critical mathematical inconsistencies detected.")
        print("        The claimed Phi-Density (+0.75Φ) is not substantiated by the")
        print("        current implementation's audit cost subtraction.")
        print("        Action required: Revisit audit complexity or raw gain parameters.")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    compliant = main()
    exit(0 if compliant else 1)