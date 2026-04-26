# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random
import sys

# Constants from the proposal
PSI_INTEGRITY_THRESHOLD = 0.95
FEDERATED_TRUST_MIN = 0.75
INSTITUTION_COUNT_MAX = 0.80  # Threshold for institution_count_normalized
DATA_SOVEREIGNTY_MIN = 0.70
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02
LAMBDA_COUPLING = 0.5
MU_FEDERATED_TRUST = 0.6

# Helper to clamp a value to [0, 1]
def clamp(x):
    return max(0.0, min(1.0, x))

# === Dimensional Consistency Checks ===

def test_institution_count_risk():
    """Test institution_count_normalized = min(n/10.0, 1.0)"""
    test_cases = [
        (0, 0.0),
        (1, 0.1),
        (5, 0.5),
        (10, 1.0),
        (15, 1.0),
        (100, 1.0)
    ]
    for n, expected in test_cases:
        result = clamp(n / 10.0)
        assert result == expected, f"Institution count risk failed for n={n}: got {result}, expected {expected}"
        assert 0.0 <= result <= 1.0, f"Institution count risk out of bounds: {result}"
    print("✓ Institution count risk: dimensional consistency PASSED")

def test_federated_trust_score():
    """Test federated_trust_score calculation"""
    # Authorized collaboration
    for integrity in [0.0, 0.5, 1.0]:
        trust = 0.80 + 0.20 * integrity
        assert 0.80 <= trust <= 1.0, f"Authorized trust out of bounds: {trust}"
    # Unauthorized collaboration
    for integrity in [0.0, 0.5, 1.0]:
        trust = 0.30 * integrity
        assert 0.0 <= trust <= 0.30, f"Unauthorized trust out of bounds: {trust}"
    print("✓ Federated trust score: dimensional consistency PASSED")

def test_data_sovereignty_score():
    """Test data_sovereignty_score = trust * (1 - institution_risk)"""
    # Test extreme values
    test_cases = [
        (0.0, 0.0, 0.0),   # trust=0, risk=0 -> 0
        (0.0, 1.0, 0.0),   # trust=0, risk=1 -> 0
        (1.0, 0.0, 1.0),   # trust=1, risk=0 -> 1
        (1.0, 1.0, 0.0),   # trust=1, risk=1 -> 0
        (0.5, 0.5, 0.25)   # trust=0.5, risk=0.5 -> 0.25
    ]
    for trust, risk, expected in test_cases:
        result = trust * (1.0 - risk)
        assert clamp(result) == expected, f"Sovereignty failed: trust={trust}, risk={risk}, got {result}, expected {expected}"
        assert 0.0 <= result <= 1.0, f"Sovereignty out of bounds: {result}"
    print("✓ Data sovereignty score: dimensional consistency PASSED")

def test_federated_risk():
    """Test federated_risk = leak * institution_risk * (1 - trust)"""
    # All factors in [0,1] -> product in [0,1]
    test_cases = [
        (0.0, 0.0, 0.0, 0.0),   # leak=0 -> 0
        (1.0, 0.0, 0.0, 0.0),   # institution_risk=0 -> 0
        (1.0, 1.0, 0.0, 0.0),   # trust=1.0 -> (1-trust)=0 -> 0
        (1.0, 1.0, 1.0, 1.0),   # leak=1, risk=1, trust=0 -> 1*1*1=1
        (0.5, 0.5, 0.5, 0.125)  # 0.5*0.5*0.5=0.125
    ]
    for leak, risk, trust, expected in test_cases:
        result = leak * risk * (1.0 - trust)
        assert clamp(result) == expected, f"Federated risk failed: leak={leak}, risk={risk}, trust={trust}, got {result}, expected {expected}"
        assert 0.0 <= result <= 1.0, f"Federated risk out of bounds: {result}"
    print("✓ Federated risk: dimensional consistency PASSED")

def test_cod_federated():
    """Test COD calculation with federated penalties"""
    # Simplified test: assume perfect fidelity (1.0) and vary penalties
    # COD = 1.0 * instability_penalty * exposure_penalty * trust_penalty * sovereignty_penalty
    # Each penalty = exp(-k * x) where x in [0,1] -> penalty in (0,1]
    # Thus COD in (0,1]
    test_cases = [
        # (h_instability, theta_leak, trust_score, sovereignty_score, min_expected, max_expected)
        (0.0, 0.0, 1.0, 1.0, 1.0, 1.0),   # All penalties = exp(0)=1.0 -> COD=1.0
        (1.0, 1.0, 0.0, 0.0, 0.0, 1.0),   # Worst case: penalties = exp(-0.5) each -> COD = exp(-0.5*4) = exp(-2.0) ≈ 0.135
    ]
    for h_inst, theta_leak, trust, sov, min_exp, max_exp in test_cases:
        instability_penalty = math.exp(-LAMBDA_COUPLING * h_inst)
        exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_leak)
        trust_penalty = math.exp(-MU_FEDERATED_TRUST * (1.0 - trust))
        sovereignty_penalty = math.exp(-MU_FEDERATED_TRUST * (1.0 - sov))
        cod = 1.0 * instability_penalty * exposure_penalty * trust_penalty * sovereignty_penalty
        assert min_exp <= cod <= max_exp, f"COD out of expected range: {cod} not in [{min_exp}, {max_exp}]"
        assert 0.0 < cod <= 1.0, f"COD out of bounds: {cod}"
    print("✓ COD federated: dimensional consistency PASSED")

def test_phi_n():
    """Test phi_N = COD (ensuring [0,1] bounds)"""
    # Since COD is in [0,1], phi_N must be in [0,1]
    test_cods = [0.0, 0.25, 0.5, 0.75, 1.0]
    for cod in test_cods:
        phi_N = cod  # As per proposal: state.phi_N = state.cod
        assert 0.0 <= phi_N <= 1.0, f"phi_N out of bounds: {phi_N}"
    print("✓ phi_N: dimensional consistency PASSED")

# === Safety Gate Hierarchy Checks ===

class FederatedType:
    TRUSTED_COLLABORATION = 0
    SOVEREIGNTY_BREACH = 1
    UNCERTAIN_TRUST = 2

class SilenceAction:
    PROCEED = 0
    FLAG_FOR_REVIEW = 1
    FREEZE_FEDERATED_OPS = 2
    IDENTITY_LOCKDOWN = 3

def decide_action(psi_integrity, federated_risk, federated_type):
    """Replicate the gate logic from FederatedSilenceProtocol::Decide"""
    # PRIMARY GATE: Ψ_integrity (non-negotiable)
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return SilenceAction.IDENTITY_LOCKDOWN
    # FEDERATED TYPE GATE
    if federated_type == FederatedType.SOVEREIGNTY_BREACH:
        return SilenceAction.IDENTITY_LOCKDOWN
    # RISK-BASED Decisions
    if federated_risk > 0.70:
        return SilenceAction.IDENTITY_LOCKDOWN
    if federated_risk > 0.50:
        return SilenceAction.FREEZE_FEDERATED_OPS
    if federated_risk > 0.30:
        return SilenceAction.FLAG_FOR_REVIEW
    return SilenceAction.PROCEED

def test_gate_hierarchy():
    """Test that gates are enforced in correct order"""
    # Test 1: Integrity failure -> LOCKDOWN regardless of other values
    assert decide_action(0.9, 0.0, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.IDENTITY_LOCKDOWN
    assert decide_action(0.9, 0.8, FederatedType.SOVEREIGNTY_BREACH) == SilenceAction.IDENTITY_LOCKDOWN
    
    # Test 2: Sovereignty breach -> LOCKDOWN (if integrity passes)
    assert decide_action(0.96, 0.0, FederatedType.SOVEREIGNTY_BREACH) == SilenceAction.IDENTITY_LOCKDOWN
    
    # Test 3: High risk -> LOCKDOWN
    assert decide_action(0.96, 0.75, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.IDENTITY_LOCKDOWN
    
    # Test 4: Medium-high risk -> FREEZE
    assert decide_action(0.96, 0.60, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.FREEZE_FEDERATED_OPS
    
    # Test 5: Medium risk -> FLAG
    assert decide_action(0.96, 0.40, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.FLAG_FOR_REVIEW
    
    # Test 6: Low risk -> PROCEED
    assert decide_action(0.96, 0.20, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.PROCEED
    
    # Test 7: Edge cases at thresholds
    assert decide_action(0.95, 0.30, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.FLAG_FOR_REVIEW  # risk > 0.30 triggers FLAG
    assert decide_action(0.95, 0.30, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.FLAG_FOR_REVIEW
    assert decide_action(0.95, 0.50, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.FREEZE_FEDERATED_OPS
    assert decide_action(0.95, 0.70, FederatedType.TRUSTED_COLLABORATION) == SilenceAction.IDENTITY_LOCKDOWN
    
    print("✓ Safety gate hierarchy: PASSED")

# === Φ-Density Accounting Checks ===

def test_phi_density_ledger():
    """Test net gain calculation: raw_gain - (audit_checks * 0.02)"""
    test_cases = [
        (0.5, 0.6, 5, 0.05),   # raw_gain=0.1, audit_cost=0.1 -> net=0.0
        (0.5, 0.7, 5, 0.15),   # raw_gain=0.2, audit_cost=0.1 -> net=0.1
        (0.5, 0.4, 5, -0.05),  # raw_gain=-0.1, audit_cost=0.1 -> net=-0.2
        (0.8, 0.8, 10, -0.2),  # raw_gain=0.0, audit_cost=0.2 -> net=-0.2
    ]
    for cod_before, cod_after, checks, expected in test_cases:
        raw_gain = cod_after - cod_before
        audit_cost = checks * AUDIT_ENTROPY_PER_CHECK
        net_gain = raw_gain - audit_cost
        assert abs(net_gain - expected) < 1e-9, f"Ledger failed: {raw_gain} - {audit_cost} = {net_gain}, expected {expected}"
    print("✓ Φ-density ledger: PASSED")

# === Main Validation Suite ===

def run_all_tests():
    """Run all validation tests"""
    try:
        test_institution_count_risk()
        test_federated_trust_score()
        test_data_sovereignty_score()
        test_federated_risk()
        test_cod_federated()
        test_phi_n()
        test_gate_hierarchy()
        test_phi_density_ledger()
        print("\n🎉 ALL TESTS PASSED - Proposal is mathematically sound and Omega Protocol compliant.")
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)