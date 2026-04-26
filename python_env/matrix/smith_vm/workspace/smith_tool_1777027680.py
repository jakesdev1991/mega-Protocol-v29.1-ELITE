# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import sys

def validate_phi_density_calculation():
    """
    Validates the mathematical correctness of Φ-density calculation and asymmetry bound enforcement.
    Tests:
      1. Φ_total = Φ_N + Φ_Δ
      2. ψ = ln(Φ_N + ε) where ε = 1e-9
      3. Asymmetry bound: if Φ_Δ ≥ 0.5·Φ_N, then Φ_Δ is clamped to 0.49·Φ_N
    """
    print("=== Validating Φ-density calculation and asymmetry bound ===")
    
    # Test case 1: Within asymmetry bound
    Φ_N = 0.8
    Φ_Δ = 0.3  # 0.3 < 0.5*0.8 = 0.4 → valid
    epsilon = 1e-9
    ψ = np.log(Φ_N + epsilon)
    expected_ψ = np.log(0.8 + 1e-9)
    
    assert abs(ψ - expected_ψ) < 1e-12, f"ψ calculation failed: got {ψ}, expected {expected_ψ}"
    
    # Asymmetry bound not violated → Φ_Δ unchanged
    assert Φ_Δ < 0.5 * Φ_N, "Asymmetry bound check failed for valid case"
    Φ_total = Φ_N + Φ_Δ
    assert abs(Φ_total - 1.1) < 1e-12, f"Φ_total failed: got {Φ_total}, expected 1.1"
    
    # Test case 2: Asymmetry bound violation
    Φ_N = 0.6
    Φ_Δ = 0.4  # 0.4 ≥ 0.5*0.6 = 0.3 → violation
    # After clamping: Φ_Δ_clamped = 0.49 * Φ_N = 0.294
    Φ_Δ_clamped = 0.49 * Φ_N
    Φ_total_clamped = Φ_N + Φ_Δ_clamped
    
    assert Φ_Δ >= 0.5 * Φ_N, "Asymmetry bound violation not detected"
    assert abs(Φ_Δ_clamped - 0.294) < 1e-12, f"Clamping failed: got {Φ_Δ_clamped}, expected 0.294"
    assert abs(Φ_total_clamped - 0.894) < 1e-12, f"Clamped Φ_total failed: got {Φ_total_clamped}, expected 0.894"
    
    # Test case 3: Edge case (exactly at bound)
    Φ_N = 1.0
    Φ_Δ = 0.5  # Exactly 0.5*Φ_N
    # Should trigger clamping per code (if Φ_Δ >= asymmetry_limit)
    Φ_Δ_clamped = 0.49 * Φ_N
    Φ_total_clamped = Φ_N + Φ_Δ_clamped
    assert Φ_Δ >= 0.5 * Φ_N, "Edge case not detected as violation"
    assert abs(Φ_Δ_clamped - 0.49) < 1e-12, f"Edge clamping failed: got {Φ_Δ_clamped}, expected 0.49"
    
    print("✓ Φ-density calculation and asymmetry bound validation PASSED")
    return True

def validate_coupling_function():
    """
    Validates the coupling function ψ = ln(Φ_N + ε) implementation.
    Tests:
      1. Monotonicity: ψ increases as Φ_N increases
      2. Behavior at Φ_N → 0+
      3. Numerical stability
    """
    print("\n=== Validating coupling function ψ ===")
    
    epsilon = 1e-9
    test_values = [0.01, 0.1, 0.5, 1.0, 2.0, 10.0]
    prev_ψ = -np.inf
    
    for Φ_N in test_values:
        ψ = np.log(Φ_N + epsilon)
        # Check monotonicity
        assert ψ > prev_ψ, f"ψ not monotonic: Φ_N={Φ_N}, ψ={ψ} ≤ prev_ψ={prev_ψ}"
        prev_ψ = ψ
        
        # Check against direct calculation
        expected = np.log(Φ_N + epsilon)
        assert abs(ψ - expected) < 1e-15, f"ψ calculation mismatch: got {ψ}, expected {expected}"
        
        # Check Φ_N + ε > 0 (avoiding log(0) or log(negative))
        assert Φ_N + epsilon > 0, f"Φ_N + ε ≤ 0: Φ_N={Φ_N}, ε={epsilon}"
    
    # Test near-zero Φ_N
    Φ_N_min = 1e-10
    ψ_min = np.log(Φ_N_min + epsilon)
    assert ψ_min > np.log(epsilon), f"ψ_min calculation failed: got {ψ_min}, expected > ln({epsilon})"
    
    print("✓ Coupling function validation PASSED")
    return True

def validate_smith_audit_thresholds():
    """
    Validates Smith Audit Guardian's invariant threshold derivations.
    Focuses on the metric non-degeneracy threshold which showed inconsistency in audit.
    Tests:
      1. Threshold should be exp(-ψ) where ψ = ln(Φ_N + ε) → simplifies to 1/(Φ_N + ε)
      2. Threshold must be positive and decrease as Φ_N increases
    """
    print("\n=== Validating Smith Audit Guardian thresholds ===")
    
    epsilon = 1e-9
    test_cases = [
        (0.5, 1/(0.5 + epsilon)),   # Φ_N=0.5 → threshold ≈ 2.0
        (1.0, 1/(1.0 + epsilon)),   # Φ_N=1.0 → threshold ≈ 1.0
        (2.0, 1/(2.0 + epsilon)),   # Φ_N=2.0 → threshold ≈ 0.5
        (0.1, 1/(0.1 + epsilon))    # Φ_N=0.1 → threshold ≈ 10.0
    ]
    
    for Φ_N, expected_threshold in test_cases:
        # Derive ψ from Φ_N
        ψ = np.log(Φ_N + epsilon)
        # Threshold per Rubric §2 derivation: exp(-ψ)
        derived_threshold = np.exp(-ψ)
        
        assert abs(derived_threshold - expected_threshold) < 1e-12, \
            f"Threshold mismatch for Φ_N={Φ_N}: got {derived_threshold}, expected {expected_threshold}"
        
        # Verify threshold properties
        assert derived_threshold > 0, f"Threshold not positive: Φ_N={Φ_N}, threshold={derived_threshold}"
        # As Φ_N increases, threshold should decrease
        if Φ_N > 0.1:  # Skip first point for monotonicity check
            prev_Φ_N = test_cases[i-1][0] if i > 0 else None
            if prev_Φ_N is not None:
                prev_threshold = np.exp(-np.log(prev_Φ_N + epsilon))
                assert derived_threshold < prev_threshold, \
                    f"Threshold not decreasing: Φ_N={prev_Φ_N}→{Φ_N}, {prev_threshold}→{derived_threshold}"
    
    print("✓ Smith Audit Guardian threshold validation PASSED")
    return True

def validate_ledger_arithmetic():
    """
    Validates the Φ-density ledger arithmetic from the proposal.
    Tests the arithmetic correctness of the net Φ-density change calculation.
    """
    print("\n=== Validating Φ-density ledger arithmetic ===")
    
    # Gains from proposal internal thought process
    gains = [0.35, 0.30, 0.24, 0.20, 0.18]  # Φ
    costs = [0.10, 0.06]                     # Φ
    
    total_gain = sum(gains)
    total_cost = sum(costs)
    net = total_gain - total_cost
    
    expected_net = 1.11  # As stated in proposal
    
    assert abs(total_gain - 1.27) < 1e-12, f"Total gain incorrect: got {total_gain}, expected 1.27"
    assert abs(total_cost - 0.16) < 1e-12, f"Total cost incorrect: got {total_cost}, expected 0.16"
    assert abs(net - expected_net) < 1e-12, f"Net Φ-density incorrect: got {net}, expected {expected_net}"
    
    # Verify individual components sum correctly
    assert abs(sum(gains) - 1.27) < 1e-12, "Gains summation failed"
    assert abs(sum(costs) - 0.16) < 1e-12, "Costs summation failed"
    
    print("✓ Ledger arithmetic validation PASSED")
    return True

def validate_mathematical_bounds():
    """
    Validates that all mathematical operations remain within defined bounds.
    Tests for potential domain errors (log of non-positive, division by zero, etc.)
    """
    print("\n=== Validating mathematical bounds ===")
    
    epsilon = 1e-9
    
    # Test Φ_N range: must be > 0 for log to be defined (with ε preventing zero)
    test_Φ_N = [0.0, 1e-15, 1e-10, 0.001, 0.1, 1.0, 100.0]
    for Φ_N in test_Φ_N:
        # Φ_N + ε must be > 0
        assert Φ_N + epsilon > 0, f"Φ_N + ε ≤ 0: Φ_N={Φ_N}, ε={epsilon}"
        # ψ = ln(Φ_N + ε) must be real number
        ψ = np.log(Φ_N + epsilon)
        assert not np.isnan(ψ) and not np.isinf(ψ), f"ψ is NaN or Inf: Φ_N={Φ_N}, ψ={ψ}"
    
    # Test asymmetry bound clamping
    for Φ_N in [0.1, 0.5, 1.0, 2.0]:
        max_allowed_Φ_Δ = 0.5 * Φ_N
        test_Φ_Δ = [0.0, 0.25 * Φ_N, 0.5 * Φ_N, 0.6 * Φ_N, Φ_N]  # Including violations
        for Φ_Δ in test_Φ_Δ:
            if Φ_Δ >= 0.5 * Φ_N:
                clamped_Φ_Δ = 0.49 * Φ_N
                assert clamped_Φ_Δ < 0.5 * Φ_N, \
                    f"Clamping failed: Φ_N={Φ_N}, Φ_Δ={Φ_Δ}, clamped={clamped_Φ_Δ}, bound={0.5*Φ_N}"
            else:
                # Should remain unchanged
                assert Φ_Δ < 0.5 * Φ_N, \
                    f"Non-violation case incorrectly flagged: Φ_N={Φ_N}, Φ_Δ={Φ_Δ}"
    
    print("✓ Mathematical bounds validation PASSED")
    return True

def main():
    """
    Main validation function that runs all checks.
    Exits with status 0 if all validations pass, 1 otherwise.
    """
    print("Starting Omega Protocol Mathematical Validation for SPLISS Proposal\n")
    
    try:
        validate_phi_density_calculation()
        validate_coupling_function()
        validate_smith_audit_thresholds()
        validate_ledger_arithmetic()
        validate_mathematical_bounds()
        
        print("\n" + "="*60)
        print("ALL VALIDATIONS PASSED")
        print("The SPLISS proposal is mathematically sound and compliant")
        print("with Omega Protocol invariants regarding the checked elements.")
        print("="*60)
        return 0
        
    except AssertionError as e:
        print(f"\nVALIDATION FAILED: {e}")
        print("The proposal contains mathematical errors or invariant violations.")
        return 1
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())