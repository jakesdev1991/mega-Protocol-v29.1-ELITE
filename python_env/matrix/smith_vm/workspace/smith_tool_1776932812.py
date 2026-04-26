# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

def validate_trust_decay():
    """
    Validates the trust decay formula in AFDS v3.0.
    The Omega Protocol requires continuous exponential decay of trust at 5% per hour.
    Correct formula: trust_score * (0.95)^hours
    Current (buggy) implementation: trust_score * exp(-ln(0.95)*hours) = trust_score * (1/0.95)^hours
    """
    print("=== TRUST DECAY VALIDATION ===")
    print("Omega Protocol Requirement: 5% hourly decay (95% retention per hour)")
    print("Correct multiplier: 0.95^hours\n")
    
    test_hours = [0, 0.5, 1, 2, 5, 10, 24]
    print(f"{'Hours':<8} {'Correct Multiplier':<20} {'Buggy Multiplier':<20} {'Error':<15} {'Verdict'}")
    print("-" * 80)
    
    for h in test_hours:
        correct = 0.95 ** h
        # Buggy implementation: exp(-ln(0.95)*h) = (1/0.95)^h
        buggy = math.exp(-math.log(0.95) * h) 
        error = abs(correct - buggy)
        verdict = "FAIL" if error > 1e-10 else "PASS"
        
        print(f"{h:<8} {correct:<20.6f} {buggy:<20.6f} {error:<15.6f} {verdict}")
    
    print("\nCRITICAL FINDING:")
    print("The buggy implementation causes TRUST GROWTH over time (multiplier > 1 for h>0)")
    print("Example: After 1 hour, trust increases by ~5.26% instead of decreasing by 5%")
    print("This violates Omega Protocol invariant Phi_N (trust decay manifold)")
    print("Required fix: Remove negative sign -> exp(log(0.95)*hours) or 0.95**hours\n")
    
    # Validate corrected formula
    print("=== CORRECTED FORMULA VALIDATION ===")
    corrected = [math.exp(math.log(0.95) * h) for h in test_hours]
    print(f"{'Hours':<8} {'Corrected Multiplier':<20} {'Matches 0.95^h?':<15}")
    print("-" * 40)
    for h, cor in zip(test_hours, corrected):
        matches = abs(cor - 0.95**h) < 1e-10
        print(f"{h:<8} {cor:<20.6f} {str(matches):<15}")
    
    print("\nConclusion: Trust decay formula is mathematically unsound.")
    print("Phi_N invariant violation: Trust accumulation instead of decay")
    print("Recommended enforcement: Audit all exponential decay terms for sign errors\n")

def validate_traversal_score_bounds():
    """
    Validates that traversal score remains within [0, ∞) and 
    that jitter probability calculation is bounded.
    """
    print("\n=== TRAVERSAL SCORE & JITTER VALIDATION ===")
    # Simulate extreme topology metrics
    test_cases = [
        (0, 0),      # Root only
        (1, 10),     # Shallow but wide
        (100, 1),    # Deep but narrow
        (1000, 100)  # Extreme case
    ]
    
    print(f"{'Unique Paths':<12} {'Max Depth':<10} {'Raw Score':<12} {'Jitter Prob (mit=0)':<22} {'Verdict'}")
    print("-" * 65)
    for paths, depth in test_cases:
        score = paths * 0.6 + depth * 0.4
        # Jitter probability calculation (mitigation=0 for worst case)
        prob = min(1.0, (score / 100.0) ** 1.5)
        verdict = "PASS" if 0 <= prob <= 1.0 else "FAIL"
        print(f"{paths:<12} {depth:<10} {score:<12.2f} {prob:<22.6f} {verdict}")
    
    print("\nNote: Traversal score unbounded but jitter probability clamped to [0,1]")
    print("This satisfies Omega Protocol invariant J* (bounded jitter manifold)\n")

def validate_phi_density_claims():
    """
    Validates the Phi-Density Impact Analysis claims mathematically.
    Focuses on the trust model's contribution to Phi_N.
    """
    print("=== PHI-DENSITY TRUST MODEL VALIDATION ===")
    print("Claim: Trust Accuracy contributes +0.20Φ")
    print("Requirement: Continuous 5%/hr decay with <0.1% error over 24h\n")
    
    # Simulate trust decay over 24 hours with hourly accesses
    hours = 24
    correct_trust = 1.0 * (0.95 ** hours)  # Starting trust=1.0
    # Buggy implementation would be:
    buggy_trust = 1.0 * math.exp(-math.log(0.95) * hours)
    
    print(f"After {hours} hours with no novel accesses:")
    print(f"  Correct trust (95%^24): {correct_trust:.6f}")
    print(f"  Buggy trust:            {buggy_trust:.6f}")
    print(f"  Error:                  {abs(correct_trust - buggy_trust):.6f}")
    print(f"  Relative error:         {abs(correct_trust - buggy_trust)/correct_trust*100:.2f}%\n")
    
    if abs(correct_trust - buggy_trust) > 0.001:  # 0.1% threshold
        print("VIOLATION: Trust model error exceeds 0.1% threshold")
        print("This invalidates the +0.20Φ claim for trust accuracy")
        print("Omega Protocol invariant Phi_N requires decay fidelity\n")
    else:
        print("Trust model meets fidelity requirement (if corrected)")

if __name__ == "__main__":
    validate_trust_decay()
    validate_traversal_score_bounds()
    validate_phi_density_claims()
    print("\n" + "="*60)
    print("FINAL AUDIT RESULT: FAIL")
    print("Reason: Fundamental sign error in trust decay formula")
    print("        causes trust growth instead of decay")
    print("        Violates Omega Protocol invariant Phi_N")
    print("        Net Phi-Density impact: UNDEFINED (system non-compliant)")
    print("="*60)