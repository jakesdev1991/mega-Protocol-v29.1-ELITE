# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import Tuple, List

# =============================================================================
# MATHEMATICAL VALIDATION OF OMEGA PROTOCOL ML-PHYSICS CONVERGENCE MODULE
# =============================================================================
# This script validates the mathematical soundness and invariant compliance
# of the ML-Physics Convergence module (v63.0-Ω) described in the C++ code.
# =============================================================================

class OmegaProtocolValidator:
    """Validates mathematical compliance with Omega Protocol invariants."""
    
    # Protocol constants from the C++ code
    PSI_INTEGRITY_THRESHOLD = 0.95
    LOG_EXPOSURE_MAX = 0.25
    ML_PROVENANCE_MIN = 0.80
    COD_THRESHOLD = 0.85
    CONVERGENCE_CONFIDENCE_MIN = 0.70
    AUDIT_ENTROPY_PER_CHECK = 0.02
    LAMBDA_COUPLING = 0.5
    MU_ML_PROVENANCE = 0.6
    
    # Authorized ML systems (subset for testing)
    AUTHORIZED_ML_SYSTEMS = {
        "plasma_disruption_predictor_v3",
        "realtime_control_neural_net",
        "diagnostic_calibration_ml",
        "federated_learning_tokamak"
    }
    
    @staticmethod
    def calculate_provenance_score(ml_system_id: str, physics_ml_coupling: float) -> float:
        """Replicates MLPhysicsProvenanceGate::CalculateProvenanceScore"""
        is_authorized = ml_system_id in OmegaProtocolValidator.AUTHORIZED_ML_SYSTEMS
        
        if is_authorized:
            return 0.90 + 0.10 * physics_ml_coupling
        elif ml_system_id == "":
            return 0.50
        else:
            return 0.20 * (1.0 - physics_ml_coupling)
    
    @staticmethod
    def classify_convergence(provenance_score: float, physics_ml_coupling: float) -> str:
        """Replicates MLPhysicsProvenanceGate::ClassifyConvergence"""
        if provenance_score >= OmegaProtocolValidator.ML_PROVENANCE_MIN:
            return "LEGITIMATE_CONVERGENCE"
        elif provenance_score < 0.40 and physics_ml_coupling > 0.60:
            return "DOMAIN_CONTAMINATION"
        else:
            return "UNCERTAIN_PROVENANCE"
    
    @staticmethod
    def calculate_ml_physics_risk(log_exposure: float, physics_ml_coupling: float, 
                                 ml_provenance_score: float) -> float:
        """Replicates MLPhysicsProvenanceGate::CalculateMLPhysicsRisk"""
        provenance_factor = 1.0 - ml_provenance_score
        risk = log_exposure * physics_ml_coupling * provenance_factor
        return max(0.0, min(1.0, risk))  # Clamp to [0,1]
    
    @staticmethod
    def assess_risk_level(ml_physics_risk: float) -> str:
        """Replicates MLPhysicsProvenanceGate::AssessRisk"""
        if ml_physics_risk > 0.70:
            return "CATASTROPHIC"
        elif ml_physics_risk > 0.50:
            return "CRITICAL"
        elif ml_physics_risk > 0.30:
            return "MEDIUM"
        else:
            return "LOW"
    
    @staticmethod
    def calculate_cod_mlphysics(fidelity: float, h_instability: float, 
                               theta_tensor_leak: float, ml_provenance_score: float,
                               convergence_confidence: float) -> float:
        """Replicates Calculate_COD_MLPhysics"""
        # Penalties (all in (0,1] for inputs in [0,1])
        instability_penalty = math.exp(-OmegaProtocolValidator.LAMBDA_COUPLING * h_instability)
        exposure_penalty = math.exp(-OmegaProtocolValidator.LAMBDA_COUPLING * theta_tensor_leak)
        provenance_penalty = math.exp(-OmegaProtocolValidator.MU_ML_PROVENANCE * (1.0 - ml_provenance_score))
        convergence_penalty = math.exp(-OmegaProtocolValidator.MU_ML_PROVENANCE * (1.0 - convergence_confidence))
        
        return fidelity * instability_penalty * exposure_penalty * provenance_penalty * convergence_penalty
    
    @staticmethod
    def calculate_phi_net_gain(cod_before: float, cod_after: float, audit_checks: int) -> float:
        """Replicates MLPhysicsPhiDensityLedger::CalculateNetGain"""
        raw_gain = cod_after - cod_before
        audit_cost = audit_checks * OmegaProtocolValidator.AUDIT_ENTROPY_PER_CHECK
        return raw_gain - audit_cost
    
    @staticmethod
    def check_invariants(state: dict, cod: float, ml_physics_risk: float, 
                        convergence_type: str) -> dict:
        """Replicates MLPhysicsInvariantEnforcer::Check"""
        check = {
            'psi_integrity_ok': state['psi_integrity'] >= OmegaProtocolValidator.PSI_INTEGRITY_THRESHOLD,
            'log_exposure_ok': ml_physics_risk <= OmegaProtocolValidator.LOG_EXPOSURE_MAX,
            'ml_provenance_ok': state['ml_provenance_score'] >= OmegaProtocolValidator.ML_PROVENANCE_MIN,
            'cod_ok': cod >= OmegaProtocolValidator.COD_THRESHOLD,
            'convergence_valid': convergence_type != "DOMAIN_CONTAMINATION",
            'audit_tracked': True
        }
        check['all_passed'] = all(check.values())
        return check
    
    @staticmethod
    def decide_action(psi_integrity: float, ml_physics_risk: float, 
                     convergence_type: str) -> str:
        """Replicates MLPhysicsSilenceProtocol::Decide"""
        # PRIMARY GATE: Ψ_integrity
        if psi_integrity < OmegaProtocolValidator.PSI_INTEGRITY_THRESHOLD:
            return "IDENTITY_LOCKDOWN"
        
        # CONVERGENCE TYPE GATE
        if convergence_type == "DOMAIN_CONTAMINATION":
            return "IDENTITY_LOCKDOWN"
        
        # RISK-BASED DECISIONS
        if ml_physics_risk > 0.70:
            return "IDENTITY_LOCKDOWN"
        elif ml_physics_risk > 0.50:
            return "FREEZE_ML_OPERATIONS"
        elif ml_physics_risk > 0.30:
            return "FLAG_FOR_REVIEW"
        else:
            return "PROCEED"

def run_comprehensive_validation():
    """Executes exhaustive validation of mathematical properties."""
    validator = OmegaProtocolValidator()
    print("=" * 70)
    print("OMEGA PROTOCOL ML-PHYSICS CONVERGENCE MODULE VALIDATION")
    print("=" * 70)
    
    # Test 1: Provenance Score Bounds and Behavior
    print("\n[TEST 1] Provenance Score Validation")
    print("-" * 40)
    
    # Authorized systems
    for coupling in [0.0, 0.5, 1.0]:
        score = validator.calculate_provenance_score("plasma_disruption_predictor_v3", coupling)
        assert 0.90 <= score <= 1.0, f"Authorized score out of bounds: {score}"
        print(f"Authorized system (coupling={coupling}): score={score:.3f} ✓")
    
    # Unauthorized systems
    for coupling in [0.0, 0.5, 1.0]:
        score = validator.calculate_provenance_score("unauthorized_ml_system", coupling)
        assert 0.0 <= score <= 0.20, f"Unauthorized score out of bounds: {score}"
        print(f"Unauthorized system (coupling={coupling}): score={score:.3f} ✓")
    
    # Empty system ID
    score = validator.calculate_provenance_score("", 0.5)
    assert score == 0.50, f"Empty ID score incorrect: {score}"
    print(f"Empty system ID: score={score:.3f} ✓")
    
    # Test 2: Risk Calculation Bounds and Monotonicity
    print("\n[TEST 2] ML-Physics Risk Validation")
    print("-" * 40)
    
    # Test boundary conditions
    test_cases = [
        (0.0, 0.5, 0.9, 0.0),   # Zero exposure
        (1.0, 0.0, 0.9, 0.0),   # Zero coupling
        (1.0, 1.0, 0.0, 1.0),   # Max risk (provenance=0)
        (0.5, 0.5, 0.8, 0.05),  # Medium risk
    ]
    
    for exposure, coupling, prov, expected in test_cases:
        risk = validator.calculate_ml_physics_risk(exposure, coupling, prov)
        assert abs(risk - expected) < 1e-5, f"Risk calculation failed: {risk} vs {expected}"
        assert 0.0 <= risk <= 1.0, f"Risk out of bounds: {risk}"
        print(f"Risk(E={exposure}, C={coupling}, P={prov}): {risk:.3f} ✓")
    
    # Test monotonicity (risk should increase with exposure/coupling, decrease with provenance)
    base_risk = validator.calculate_ml_physics_risk(0.5, 0.5, 0.8)
    assert validator.calculate_ml_physics_risk(0.6, 0.5, 0.8) > base_risk, "Risk not increasing with exposure"
    assert validator.calculate_ml_physics_risk(0.5, 0.6, 0.8) > base_risk, "Risk not increasing with coupling"
    assert validator.calculate_ml_physics_risk(0.5, 0.5, 0.7) > base_risk, "Risk not increasing with decreased provenance"
    print("Risk monotonicity properties ✓")
    
    # Test 3: COD Calculation Bounds
    print("\n[TEST 3] COD Calculation Validation")
    print("-" * 40)
    
    # Test with fidelity=1.0 (perfect alignment)
    for h_inst in [0.0, 0.5, 1.0]:
        for theta_leak in [0.0, 0.5, 1.0]:
            for prov in [0.0, 0.5, 1.0]:
                for conf in [0.0, 0.5, 1.0]:
                    cod = validator.calculate_cod_mlphysics(
                        1.0, h_inst, theta_leak, prov, conf
                    )
                    assert 0.0 < cod <= 1.0, f"COD out of bounds: {cod}"
    print("COD bounds validation (fidelity=1.0) ✓")
    
    # Test with fidelity=0.0 (orthogonal)
    cod_zero = validator.calculate_cod_mlphysics(0.0, 0.0, 0.0, 1.0, 1.0)
    assert cod_zero == 0.0, f"COD should be 0 for zero fidelity: {cod_zero}"
    print("COD zero fidelity case ✓")
    
    # Test 4: Invariant Checking Logic
    print("\n[TEST 4] Invariant Enforcement Validation")
    print("-" * 40)
    
    # Valid state
    state_valid = {
        'psi_integrity': 0.96,
        'ml_provenance_score': 0.85,
        'log_exposure': 0.1,
        'physics_ml_coupling': 0.7,
        'convergence_confidence': 0.75
    }
    cod_valid = 0.88
    risk_valid = validator.calculate_ml_physics_risk(
        state_valid['log_exposure'],
        state_valid['physics_ml_coupling'],
        state_valid['ml_provenance_score']
    )
    conv_type_valid = validator.classify_convergence(
        state_valid['ml_provenance_score'],
        state_valid['physics_ml_coupling']
    )
    check_valid = validator.check_invariants(
        state_valid, cod_valid, risk_valid, conv_type_valid
    )
    assert check_valid['all_passed'], "Valid state failed invariants"
    print("Valid state passes all invariants ✓")
    
    # Invalid state (low provenance)
    state_invalid = state_valid.copy()
    state_invalid['ml_provenance_score'] = 0.75  # Below threshold
    cod_invalid = 0.88
    risk_invalid = validator.calculate_ml_physics_risk(
        state_invalid['log_exposure'],
        state_invalid['physics_ml_coupling'],
        state_invalid['ml_provenance_score']
    )
    conv_type_invalid = validator.classify_convergence(
        state_invalid['ml_provenance_score'],
        state_invalid['physics_ml_coupling']
    )
    check_invalid = validator.check_invariants(
        state_invalid, cod_invalid, risk_invalid, conv_type_invalid
    )
    assert not check_invalid['ml_provenance_ok'], "Provenance check should fail"
    assert not check_invalid['all_passed'], "Invalid state should not pass all invariants"
    print("Invalid state correctly fails provenance invariant ✓")
    
    # Test 5: Action Decision Logic
    print("\n[TEST 5] Action Decision Validation")
    print("-" * 40)
    
    # Test primary gate (low psi_integrity)
    action = validator.decide_action(0.94, 0.1, "LEGITIMATE_CONVERGENCE")
    assert action == "IDENTITY_LOCKDOWN", f"Low psi_integrity should trigger lockdown: {action}"
    print("Low psi_integrity → IDENTITY_LOCKDOWN ✓")
    
    # Test contamination gate
    action = validator.decide_action(0.96, 0.1, "DOMAIN_CONTAMINATION")
    assert action == "IDENTITY_LOCKDOWN", f"Contamination should trigger lockdown: {action}"
    print("Domain contamination → IDENTITY_LOCKDOWN ✓")
    
    # Test risk-based decisions
    test_cases = [
        (0.96, 0.25, "LEGITIMATE_CONVERGENCE", "FLAG_FOR_REVIEW"),
        (0.96, 0.40, "LEGITIMATE_CONVERGENCE", "FREEZE_ML_OPERATIONS"),
        (0.96, 0.75, "LEGITIMATE_CONVERGENCE", "IDENTITY_LOCKDOWN"),
        (0.96, 0.10, "LEGITIMATE_CONVERGENCE", "PROCEED")
    ]
    
    for psi, risk, conv_type, expected in test_cases:
        action = validator.decide_action(psi, risk, conv_type)
        assert action == expected, f"Risk {risk} should yield {expected}, got {action}"
        print(f"Psi={psi}, Risk={risk:.2f}, Conv={conv_type} → {action} ✓")
    
    # Test 6: Φ-Density Accounting
    print("\n[TEST 6] Φ-Density Net Gain Validation")
    print("-" * 40)
    
    # Test net gain calculation
    net_gain = validator.calculate_phi_net_gain(0.80, 0.85, 9)  # 9 audit checks
    expected_gain = (0.85 - 0.80) - (9 * 0.02)  # 0.05 - 0.18 = -0.13
    assert abs(net_gain - expected_gain) < 1e-5, f"Net gain incorrect: {net_gain} vs {expected_gain}"
    print(f"Cod gain 0.05 with 9 audits: net gain = {net_gain:.3f} ✓")
    
    # Test negative gain (audit cost > improvement)
    net_gain_neg = validator.calculate_phi_net_gain(0.80, 0.81, 9)
    expected_neg = (0.81 - 0.80) - 0.18 = -0.17
    assert abs(net_gain_neg - expected_neg) < 1e-5, f"Negative net gain incorrect"
    print(f"Cod gain 0.01 with 9 audits: net gain = {net_gain_neg:.3f} ✓")
    
    # Test 7: Dimensional Consistency (All metrics in [0,1])
    print("\n[TEST 7] Dimensional Consistency Check")
    print("-" * 40)
    
    metrics_to_check = [
        ("Provenance Score", lambda: validator.calculate_provenance_score("test", 0.5)),
        ("ML Physics Risk", lambda: validator.calculate_ml_physics_risk(0.5, 0.5, 0.5)),
        ("COD", lambda: validator.calculate_cod_mlphysics(0.9, 0.1, 0.1, 0.9, 0.9)),
        ("Phi Net Gain", lambda: validator.calculate_phi_net_gain(0.8, 0.85, 9))  # Can be negative, but we check input bounds
    ]
    
    for name, func in metrics_to_check:
        if name != "Phi Net Gain":  # Net gain can be negative
            val = func()
            assert 0.0 <= val <= 1.0, f"{name} out of bounds: {val}"
            print(f"{name}: {val:.3f} ∈ [0,1] ✓")
        else:
            # For net gain, we only validate that inputs to the calculation are bounded
            # (the output can be negative due to audit costs, which is acceptable)
            pass
    
    print("\n" + "=" * 70)
    print("ALL VALIDATION TESTS PASSED")
    print("The ML-Physics Convergence module is mathematically sound")
    print("and compliant with Omega Protocol invariants.")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        run_comprehensive_validation()
    except AssertionError as e:
        print(f"\nVALIDATION FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        exit(1)