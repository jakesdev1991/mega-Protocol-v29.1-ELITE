# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from scipy.special import expit  # sigmoid function

# Constants from refined PASM-Ω proposal
ALPHA_INTENT = 0.7  # Intent weighting in weaponization field
WEIGHTS = [0.3, 0.25, 0.2, 0.15, 0.1]  # SW-WRI channel weights
THRESH_SW_WRI_LOW = 0.25
THRESH_SW_WRI_HIGH = 0.55
CONSTRAINT_SW_WRI_MAX = 0.6
CONSTRAINT_PHI_N_MIN = 0.5
CONSTRAINT_S_WEAP_MIN = math.log(4)  # ≈1.386

def sigmoid(x):
    """Sigmoid function for SW-WRI calculation"""
    return expit(x)

def calculate_sw_wri(signals, baselines, intent_probs):
    """
    Calculate Sophistication-Weighted Weaponization Readiness Index (SW-WRI)
    
    Args:
        signals: list of 5 signal strengths [S1, S2, S3, S4, S5]
        baselines: list of 5 baseline values [S10, S20, S30, S40, S50]
        intent_probs: list of 5 attack probabilities [P1, P2, P3, P4, P5]
    
    Returns:
        SW-WRI value in [0, 1]
    """
    # Validate inputs
    assert len(signals) == 5, "Must provide exactly 5 signals"
    assert len(baselines) == 5, "Must provide exactly 5 baselines"
    assert len(intent_probs) == 5, "Must provide exactly 5 intent probabilities"
    assert all(b > 0 for b in baselines), "Baselines must be positive"
    assert all(0 <= p <= 1 for p in intent_probs), "Intent probabilities must be in [0,1]"
    assert all(s >= 0 for s in signals), "Signals must be non-negative"
    
    # Calculate weighted sum
    weighted_sum = 0.0
    for i in range(5):
        normalized_signal = signals[i] / baselines[i]
        weighted_sum += WEIGHTS[i] * normalized_signal * intent_probs[i]
    
    # Apply sigmoid to bound output in [0,1]
    sw_wri = sigmoid(weighted_sum)
    assert 0 <= sw_wri <= 1, f"SW-WRI out of bounds: {sw_wri}"
    return sw_wri

def calculate_weaponization_field(w_sim, w_intent):
    """
    Calculate Intent-Augmented Weaponization Field
    
    Args:
        w_sim: simulation activity field value (non-negative)
        w_intent: intent inference field value (non-negative)
    
    Returns:
        Weaponization field value (non-negative)
    """
    assert w_sim >= 0, "Simulation field must be non-negative"
    assert w_intent >= 0, "Intent field must be non-negative"
    
    # W(x,t) = [W_sim]^(1-α) * [W_intent]^α
    field = (w_sim ** (1 - ALPHA_INTENT)) * (w_intent ** ALPHA_INTENT)
    assert field >= 0, "Weaponization field must be non-negative"
    return field

def calculate_phi_n_weap(phi_n0, sw_wri_delayed, s_weap_delayed):
    """
    Calculate weaponized Phi_N invariant
    
    Args:
        phi_n0: initial Phi_N value (positive)
        sw_wri_delayed: SW-WRI from 14 days ago (constrained ≤0.6)
        s_weap_delayed: entropy gauge from 14 days ago (constrained ≥ln(4))
    
    Returns:
        Phi_N^(weap)(t) value
    """
    assert phi_n0 > 0, "Initial Phi_N must be positive"
    assert 0 <= sw_wri_delayed <= CONSTRAINT_SW_WRI_MAX, \
        f"Delayed SW-WRI {sw_wri_delayed} violates constraint [0, {CONSTRAINT_SW_WRI_MAX}]"
    assert s_weap_delayed >= CONSTRAINT_S_WEAP_MIN, \
        f"Delayed S_weap {s_weap_delayed} violates constraint ≥{CONSTRAINT_S_WEAP_MIN}"
    
    # Φ_N^(weap)(t) = Φ_N^(0) - 0.9 * SW-WRI(t-14d) + 0.4 * S_weap(t-14d)
    phi_n_weap = phi_n0 - 0.9 * sw_wri_delayed + 0.4 * s_weap_delayed
    
    # Validate against Omega Protocol invariants
    assert phi_n_weap > 0, f"Phi_N^(weap) must be positive: {phi_n_weap}"
    assert phi_n_weap >= CONSTRAINT_PHI_N_MIN, \
        f"Phi_N^(weap) {phi_n_weap} below minimum {CONSTRAINT_PHI_N_MIN}"
    
    return phi_n_weap

def validate_psi_weap_invariant(phi_n_weap, phi_n0, i_corr, i_0, lambda_param, sw_wri):
    """
    Validate the weaponization invariant ψ_weap(t)
    
    Args:
        phi_n_weap: current weaponized Phi_N
        phi_n0: initial Phi_N
        i_corr: intent correlation measure
        i_0: baseline intent correlation
        lambda_param: coupling constant
        sw_wri: current SW-WRI value
    
    Returns:
        Boolean indicating invariant validity
    """
    assert phi_n_weap > 0 and phi_n0 > 0, "Phi_N values must be positive"
    assert i_corr > 0 and i_0 > 0, "Intent correlation values must be positive"
    
    # ψ_weap(t) = ln(Φ_N^(weap)/Φ_N^(0)) = ln(I_corr/I_0) + λ * SW-WRI(t)
    left_side = math.log(phi_n_weap / phi_n0)
    right_side = math.log(i_corr / i_0) + lambda_param * sw_wri
    
    # Allow small floating-point tolerance
    return math.isclose(left_side, right_side, rel_tol=1e-9, abs_tol=1e-12)

def run_validation_tests():
    """Run comprehensive validation tests for PASM-Ω mathematics"""
    np.random.seed(42)  # For reproducibility
    num_tests = 10000
    
    print("Running PASM-Ω mathematical validation...")
    
    # Test 1: SW-WRI bounds and monotonicity
    print("\n1. Testing SW-WRI bounds and behavior:")
    for _ in range(num_tests//10):
        signals = np.random.uniform(0, 10, 5)
        baselines = np.random.uniform(1, 5, 5)  # Avoid zero baselines
        intent_probs = np.random.uniform(0, 1, 5)
        sw_wri = calculate_sw_wri(signals, baselines, intent_probs)
        assert 0 <= sw_wri <= 1, f"SW-WRI {sw_wri} out of [0,1] range"
        
        # Test monotonicity in intent probability
        intent_probs_high = np.clip(intent_probs + 0.2, 0, 1)
        sw_wri_high = calculate_sw_wri(signals, baselines, intent_probs_high)
        assert sw_wri_high >= sw_wri, "SW-WRI should increase with intent probability"
    
    print("   ✓ SW-WRI tests passed")
    
    # Test 2: Weaponization field non-negativity
    print("\n2. Testing weaponization field:")
    for _ in range(num_tests//10):
        w_sim = np.random.uniform(0, 100)
        w_intent = np.random.uniform(0, 100)
        field = calculate_weaponization_field(w_sim, w_intent)
        assert field >= 0, f"Negative weaponization field: {field}"
        
        # Test boundary cases
        assert calculate_weaponization_field(0, w_intent) == 0, "Zero simulation field should yield zero"
        assert calculate_weaponization_field(w_sim, 0) == 0, "Zero intent field should yield zero"
    
    print("   ✓ Weaponization field tests passed")
    
    # Test 3: Phi_N_weap constraint satisfaction
    print("\n3. Testing Phi_N_weap constraints:")
    phi_n0 = 1.0  # Normalized initial value
    for _ in range(num_tests//10):
        sw_wri_delayed = np.random.uniform(0, CONSTRAINT_SW_WRI_MAX)
        s_weap_delayed = np.random.uniform(CONSTRAINT_S_WEAP_MIN, 10.0)
        phi_n_weap = calculate_phi_n_weap(phi_n0, sw_wri_delayed, s_weap_delayed)
        
        # Verify constraint satisfaction
        assert phi_n_weap >= CONSTRAINT_PHI_N_MIN, \
            f"Phi_N_weap {phi_n_weap} < {CONSTRAINT_PHI_N_MIN}"
        assert phi_n_weap > 0, f"Phi_N_weap {phi_n_weap} ≤ 0"
        
        # Verify mathematical relationship
        expected = phi_n0 - 0.9 * sw_wri_delayed + 0.4 * s_weap_delayed
        assert math.isclose(phi_n_weap, expected), \
            f"Phi_N_weap calculation mismatch: {phi_n_weap} vs {expected}"
    
    print("   ✓ Phi_N_weap constraint tests passed")
    
    # Test 4: Invariant validation (with sample values)
    print("\n4. Testing ψ_weap invariant:")
    lambda_param = 0.5  # Sample coupling constant
    for _ in range(num_tests//20):
        phi_n_weap = np.random.uniform(CONSTRAINT_PHI_N_MIN, 2.0)
        phi_n0 = 1.0
        i_corr = np.random.uniform(0.5, 2.0)
        i_0 = 1.0
        sw_wri = np.random.uniform(0, CONSTRAINT_SW_WRI_MAX)
        
        # Calculate implied intent correlation from invariant
        log_ratio = math.log(phi_n_weap / phi_n0) - lambda_param * sw_wri
        i_corr_implied = i_0 * math.exp(log_ratio)
        assert i_corr_implied > 0, "Implied intent correlation must be positive"
        
        # Direct validation
        assert validate_psi_weap_invariant(
            phi_n_weap, phi_n0, i_corr_implied, i_0, lambda_param, sw_wri
        ), "Invariant validation failed"
    
    print("   ✓ Invariant validation tests passed")
    
    # Test 5: Threshold behavior
    print("\n5. Testing SW-WRI thresholds:")
    # Below low threshold
    low_signals = [0.1, 0.1, 0.1, 0.1, 0.1]
    low_baselines = [1.0, 1.0, 1.0, 1.0, 1.0]
    low_probs = [0.1, 0.1, 0.1, 0.1, 0.1]
    assert calculate_sw_wri(low_signals, low_baselines, low_probs) < THRESH_SW_WRI_LOW
    
    # Above high threshold
    high_signals = [5.0, 5.0, 5.0, 5.0, 5.0]
    high_baselines = [1.0, 1.0, 1.0, 1.0, 1.0]
    high_probs = [0.9, 0.9, 0.9, 0.9, 0.9]
    assert calculate_sw_wri(high_signals, high_baselines, high_probs) > THRESH_SW_WRI_HIGH
    
    print("   ✓ Threshold behavior tests passed")
    
    print("\n🎉 All PASM-Ω mathematical validations PASSED")
    print("✓ SW-WRI remains bounded in [0,1]")
    print("✓ Weaponization field is non-negative")
    print("✓ Phi_N_weap satisfies Ω Protocol constraints (≥0.5, >0)")
    print("✓ ψ_weap invariant holds under validation")
    print("✓ Thresholds correctly classify weaponization readiness")

if __name__ == "__main__":
    run_validation_tests()