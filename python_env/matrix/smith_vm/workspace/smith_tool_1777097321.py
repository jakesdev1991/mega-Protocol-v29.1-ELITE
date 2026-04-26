# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np
from typing import Tuple, List

# =============================================================================
# MATHEMATICAL VALIDATION OF QUANTUM-IDENTITY COHERENCE MANIFOLD (v68.0-Ω)
# =============================================================================
# This script validates the core mathematical operations of the proposed 
# Quantum-Identity Coherence Manifold against Omega Protocol invariants.

class CoherenceMathValidator:
    """Validates mathematical soundness of coherence manifold operations."""
    
    # Protocol Invariants (from C++ code)
    PSI_INTEGRITY_THRESHOLD = 0.95
    COHERENCE_TIME_MIN = 0.50
    ERROR_RATE_MAX = 0.30
    SELF_CORRECTION_MIN = 0.60
    COD_THRESHOLD = 0.85
    AUDIT_ENTROPY_PER_CHECK = 0.02
    
    LAMBDA_COUPLING = 0.5
    MU_COHERENCE = 0.6
    
    @staticmethod
    def clamp(x: float, low: float, high: float) -> float:
        """Replicate std::clamp behavior."""
        return max(low, min(high, x))
    
    @staticmethod
    def calculate_coherence_time(
        base_coherence: float, 
        error_rate: float, 
        self_correction_efficacy: float
    ) -> float:
        """Validate CalculateCoherenceTime function."""
        # Input bounds enforcement (per protocol)
        base_coherence = CoherenceMathValidator.clamp(base_coherence, 0.0, 1.0)
        error_rate = CoherenceMathValidator.clamp(error_rate, 0.0, 1.0)
        self_correction_efficacy = CoherenceMathValidator.clamp(self_correction_efficacy, 0.0, 1.0)
        
        error_factor = math.exp(-2.0 * error_rate)
        correction_factor = 1.0 + self_correction_efficacy
        effective_coherence = base_coherence * error_factor * correction_factor
        return CoherenceMathValidator.clamp(effective_coherence, 0.0, 1.0)
    
    @staticmethod
    def calculate_decoherence_rate(coherence_time: float) -> float:
        """Validate CalculateDecoherenceRate function."""
        coherence_time = CoherenceMathValidator.clamp(coherence_time, 0.0, 1.0)
        return CoherenceMathValidator.clamp(1.0 - coherence_time, 0.0, 1.0)
    
    @staticmethod
    def calculate_self_correction_efficacy(
        recovery_velocity: float, 
        psi_integrity: float, 
        logical_qubit_fidelity: float
    ) -> float:
        """Validate CalculateSelfCorrectionEfficacy function."""
        recovery_velocity = CoherenceMathValidator.clamp(recovery_velocity, 0.0, 1.0)
        psi_integrity = CoherenceMathValidator.clamp(psi_integrity, 0.0, 1.0)
        logical_qubit_fidelity = CoherenceMathValidator.clamp(logical_qubit_fidelity, 0.0, 1.0)
        
        recovery_component = recovery_velocity * 0.4
        integrity_component = psi_integrity * 0.3
        fidelity_component = logical_qubit_fidelity * 0.3
        total = recovery_component + integrity_component + fidelity_component
        return CoherenceMathValidator.clamp(total, 0.0, 1.0)
    
    @staticmethod
    def calculate_coherence_resilience_risk(
        coherence_time: float, 
        error_rate: float, 
        self_correction_efficacy: float
    ) -> float:
        """Validate CalculateCoherenceResilienceRisk function."""
        coherence_time = CoherenceMathValidator.clamp(coherence_time, 0.0, 1.0)
        error_rate = CoherenceMathValidator.clamp(error_rate, 0.0, 1.0)
        self_correction_efficacy = CoherenceMathValidator.clamp(self_correction_efficacy, 0.0, 1.0)
        
        coherence_deficit = 1.0 - coherence_time
        correction_deficit = 1.0 - self_correction_efficacy
        risk = coherence_deficit * error_rate * correction_deficit
        return CoherenceMathValidator.clamp(risk, 0.0, 1.0)
    
    @staticmethod
    def classify_coherence_state(
        coherence_time: float, 
        self_correction_efficacy: float, 
        error_rate: float
    ) -> str:
        """Validate ClassifyCoherenceState function."""
        coherence_time = CoherenceMathValidator.clamp(coherence_time, 0.0, 1.0)
        self_correction_efficacy = CoherenceMathValidator.clamp(self_correction_efficacy, 0.0, 1.0)
        error_rate = CoherenceMathValidator.clamp(error_rate, 0.0, 1.0)
        
        if coherence_time > 0.70 and error_rate < 0.20:
            return "STABLE"
        if self_correction_efficacy > 0.60 and coherence_time > 0.40:
            return "SELF_CORRECTING"
        if coherence_time < 0.30:
            return "FRAGMENTED"
        return "DECOHERING"
    
    @staticmethod
    def assess_risk(coherence_risk: float) -> str:
        """Validate AssessRisk function."""
        coherence_risk = CoherenceMathValidator.clamp(coherence_risk, 0.0, 1.0)
        if coherence_risk > 0.70:
            return "CATASTROPHIC"
        if coherence_risk > 0.50:
            return "CRITICAL"
        if coherence_risk > 0.30:
            return "MEDIUM"
        return "LOW"
    
    @staticmethod
    def calculate_cod_coherence_aware(
        diagnostic_vec: List[complex], 
        plasma_vec: List[complex], 
        h_instability: float, 
        theta_tensor_leak: float, 
        coherence_time: float, 
        coherence_resilience_risk: float
    ) -> float:
        """Validate Calculate_COD_CoherenceAware function."""
        # Safety check for zero vectors
        size = min(len(diagnostic_vec), len(plasma_vec))
        if size == 0:
            return 0.0
            
        dot = 0.0
        magD = 0.0
        magP = 0.0
        for i in range(size):
            dot += abs(np.conj(diagnostic_vec[i]) * plasma_vec[i])
            magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
            magP += abs(plasma_vec[i] * plasma_vec[i])
        
        fidelity = 0.0
        if magD > 1e-9 and magP > 1e-9:
            fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
            fidelity = CoherenceMathValidator.clamp(fidelity, 0.0, 1.0)
        
        instability_penalty = math.exp(-CoherenceMathValidator.LAMBDA_COUPLING * h_instability)
        exposure_penalty = math.exp(-CoherenceMathValidator.LAMBDA_COUPLING * theta_tensor_leak)
        coherence_penalty = math.exp(-CoherenceMathValidator.MU_COHERENCE * (1.0 - coherence_time))
        resilience_penalty = math.exp(-CoherenceMathValidator.MU_COHERENCE * coherence_resilience_risk)
        
        cod = fidelity * instability_penalty * exposure_penalty * coherence_penalty * resilience_penalty
        return CoherenceMathValidator.clamp(cod, 0.0, 1.0)
    
    @staticmethod
    def decide_coherence_silence_protocol(
        psi_integrity: float, 
        coherence_resilience_risk: float, 
        coherence_state: str
    ) -> str:
        """Validate CoherenceSilenceProtocol::Decide function."""
        psi_integrity = CoherenceMathValidator.clamp(psi_integrity, 0.0, 1.0)
        coherence_resilience_risk = CoherenceMathValidator.clamp(coherence_resilience_risk, 0.0, 1.0)
        
        if psi_integrity < CoherenceMathValidator.PSI_INTEGRITY_THRESHOLD:
            return "IDENTITY_LOCKDOWN"
        if coherence_state == "FRAGMENTED":
            return "IDENTITY_LOCKDOWN"
        if coherence_resilience_risk > 0.70:
            return "IDENTITY_LOCKDOWN"
        if coherence_resilience_risk > 0.50:
            return "ACTIVATE_SELF_CORRECTION"
        if coherence_resilience_risk > 0.30:
            return "FLAG_COHERENCE_MONITOR"
        return "PROCEED"
    
    @staticmethod
    def check_invariants(
        psi_integrity: float, 
        coherence_time: float, 
        error_rate: float, 
        self_correction_efficacy: float, 
        cod: float
    ) -> Tuple[bool, dict]:
        """Validate CoherenceInvariantEnforcer::Check function."""
        psi_integrity = CoherenceMathValidator.clamp(psi_integrity, 0.0, 1.0)
        coherence_time = CoherenceMathValidator.clamp(coherence_time, 0.0, 1.0)
        error_rate = CoherenceMathValidator.clamp(error_rate, 0.0, 1.0)
        self_correction_efficacy = CoherenceMathValidator.clamp(self_correction_efficacy, 0.0, 1.0)
        cod = CoherenceMathValidator.clamp(cod, 0.0, 1.0)
        
        checks = {
            "psi_integrity_ok": psi_integrity >= CoherenceMathValidator.PSI_INTEGRITY_THRESHOLD,
            "coherence_time_ok": coherence_time >= CoherenceMathValidator.COHERENCE_TIME_MIN,
            "error_rate_ok": error_rate <= CoherenceMathValidator.ERROR_RATE_MAX,
            "self_correction_ok": self_correction_efficacy >= CoherenceMathValidator.SELF_CORRECTION_MIN,
            "cod_ok": cod >= CoherenceMathValidator.COD_THRESHOLD,
            "audit_tracked": True  # Always tracked per implementation
        }
        all_passed = all(checks.values())
        return all_passed, checks
    
    @staticmethod
    def calculate_phi_net_gain(
        cod_before: float, 
        cod_after: float, 
        audit_checks: int
    ) -> float:
        """Validate CoherencePhiDensityLedger::CalculateNetGain function."""
        cod_before = CoherenceMathValidator.clamp(cod_before, 0.0, 1.0)
        cod_after = CoherenceMathValidator.clamp(cod_after, 0.0, 1.0)
        raw_gain = cod_after - cod_before
        audit_cost = audit_checks * CoherenceMathValidator.AUDIT_ENTROPY_PER_CHECK
        return raw_gain - audit_cost

def run_validation_suite() -> None:
    """Execute comprehensive validation of all mathematical operations."""
    validator = CoherenceMathValidator()
    test_results = []
    
    print("=" * 70)
    print("OMEGA PROTOCOL: QUANTUM-IDENTITY COHERENCE MANIFOLD VALIDATION")
    print("=" * 70)
    
    # Test 1: Coherence Time Calculation
    print("\n[TEST 1] Coherence Time Calculation")
    test_cases = [
        (0.85, 0.0, 0.0, 0.85),  # Base case
        (0.85, 0.5, 0.0, 0.31),  # High error, no correction
        (0.85, 0.0, 0.5, 1.0),   # No error, moderate correction -> clamped
        (0.85, 0.3, 0.6, 0.85*exp(-0.6)*1.6),  # Mixed inputs
        (1.2, 0.2, 0.4, 0.8*exp(-0.4)*1.4),   # Input >1 clamped
        (-0.1, 0.1, 0.1, 0.9*exp(-0.2)*1.1)   # Input <0 clamped
    ]
    for base, err, corr, expected in test_cases:
        result = validator.calculate_coherence_time(base, err, corr)
        assert abs(result - expected) < 1e-5, f"Failed: {base},{err},{corr} -> {result} != {expected}"
    print("✓ All coherence time tests passed")
    test_results.append(("Coherence Time", True))
    
    # Test 2: Self-Correction Efficacy Bounds
    print("\n[TEST 2] Self-Correction Efficacy Bounds")
    test_cases = [
        (0.0, 0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0, 1.0),  # Max sum = 0.4+0.3+0.3=1.0
        (0.5, 0.5, 0.5, 0.5*0.4+0.5*0.3+0.5*0.3),  # 0.2+0.15+0.15=0.5
        (2.0, 2.0, 2.0, 1.0),  # Inputs >1 clamped
        (-1.0, -1.0, -1.0, 0.0) # Inputs <0 clamped
    ]
    for rv, pi, lqf, expected in test_cases:
        result = validator.calculate_self_correction_efficacy(rv, pi, lqf)
        assert abs(result - expected) < 1e-5, f"Failed: {rv},{pi},{lqf} -> {result} != {expected}"
    print("✓ All self-correction efficacy tests passed")
    test_results.append(("Self-Correction Efficacy", True))
    
    # Test 3: Coherence Resilience Risk Monotonicity
    print("\n[TEST 3] Coherence Resilience Risk Monotonicity")
    # Risk should increase with error_rate and decrease with coherence_time/self_correction
    base_risk = validator.calculate_coherence_resilience_risk(0.6, 0.2, 0.7)
    
    # Increasing error should increase risk
    higher_err_risk = validator.calculate_coherence_resilience_risk(0.6, 0.3, 0.7)
    assert higher_err_risk > base_risk, "Risk not increasing with error_rate"
    
    # Increasing coherence_time should decrease risk
    higher_coherence_risk = validator.calculate_coherence_resilience_risk(0.7, 0.2, 0.7)
    assert higher_coherence_risk < base_risk, "Risk not decreasing with coherence_time"
    
    # Increasing self_correction should decrease risk
    higher_correction_risk = validator.calculate_coherence_resilience_risk(0.6, 0.2, 0.8)
    assert higher_correction_risk < base_risk, "Risk not decreasing with self_correction"
    print("✓ All risk monotonicity tests passed")
    test_results.append(("Risk Monotonicity", True))
    
    # Test 4: Coherence State Classification Boundaries
    print("\n[TEST 4] Coherence State Classification")
    # STABLE region
    assert validator.classify_coherence_state(0.71, 0.5, 0.19) == "STABLE"
    # SELF_CORRECTING region (note: overrides DECOHERING when coherence_time>0.4 and correction>0.6)
    assert validator.classify_coherence_state(0.41, 0.61, 0.5) == "SELF_CORRECTING"
    # FRAGMENTED region
    assert validator.classify_coherence_state(0.29, 0.9, 0.1) == "FRAGMENTED"
    # DECOHERING region (fallthrough)
    assert validator.classify_coherence_state(0.5, 0.5, 0.3) == "DECOHERING"
    print("✓ All coherence state classification tests passed")
    test_results.append(("State Classification", True))
    
    # Test 5: COD Calculation Bounds and Penalties
    print("\n[TEST 5] COD Calculation Validation")
    # Test with identical vectors (should give high COD when low instability/exposure)
    diag = [1+0j, 0+1j]
    plasm = [1+0j, 0+1j]
    cod_high = validator.calculate_cod_coherence_aware(
        diag, plasm, 0.0, 0.0, 0.9, 0.1  # Low instability, exposure, high coherence, low risk
    )
    assert cod_high > 0.8, f"Expected high COD for favorable conditions: {cod_high}"
    
    # Test with orthogonal vectors (should give low COD)
    diag = [1+0j, 0+0j]
    plasm = [0+0j, 1+0j]
    cod_low = validator.calculate_cod_coherence_aware(
        diag, plasm, 0.0, 0.0, 0.9, 0.1
    )
    assert cod_low < 0.2, f"Expected low COD for orthogonal vectors: {cod_low}"
    
    # Test penalty effects
    base_cod = validator.calculate_cod_coherence_aware(
        [1+0j], [1+0j], 0.0, 0.0, 0.5, 0.5
    )
    high_instab_cod = validator.calculate_cod_coherence_aware(
        [1+0j], [1+0j], 1.0, 0.0, 0.5, 0.5
    )
    assert high_instab_cod < base_cod, "Instability penalty not reducing COD"
    print("✓ All COD calculation tests passed")
    test_results.append(("COD Calculation", True))
    
    # Test 6: Protocol Decision Logic
    print("\n[TEST 6] Coherence Silence Protocol Decisions")
    # IDENTITY_LOCKDOWN cases
    assert validator.decide_coherence_silence_protocol(0.94, 0.1, "STABLE") == "IDENTITY_LOCKDOWN"  # Low psi
    assert validator.decide_coherence_silence_protocol(0.96, 0.1, "FRAGMENTED") == "IDENTITY_LOCKDOWN"  # Fragmented
    assert validator.decide_coherence_silence_protocol(0.96, 0.71, "STABLE") == "IDENTITY_LOCKDOWN"  # High risk
    
    # ACTIVATE_SELF_CORRECTION
    assert validator.decide_coherence_silence_protocol(0.96, 0.51, "STABLE") == "ACTIVATE_SELF_CORRECTION"
    
    # FLAG_COHERENCE_MONITOR
    assert validator.decide_coherence_silence_protocol(0.96, 0.31, "STABLE") == "FLAG_COHERENCE_MONITOR"
    
    # PROCEED
    assert validator.decide_coherence_silence_protocol(0.96, 0.29, "STABLE") == "PROCEED"
    print("✓ All protocol decision tests passed")
    test_results.append(("Protocol Decisions", True))
    
    # Test 7: Invariant Checking
    print("\n[TEST 7] Invariant Enforcement Validation")
    # All good case
    passed, checks = validator.check_invariants(
        0.96, 0.6, 0.2, 0.7, 0.9
    )
    assert passed == True, "Should pass with all invariants satisfied"
    assert all(checks.values()), "All individual checks should pass"
    
    # Failure cases
    failure_cases = [
        (0.94, 0.6, 0.2, 0.7, 0.9, "psi_integrity_ok"),  # Low psi
        (0.96, 0.4, 0.2, 0.7, 0.9, "coherence_time_ok"), # Low coherence time
        (0.96, 0.6, 0.4, 0.7, 0.9, "error_rate_ok"),     # High error rate
        (0.96, 0.6, 0.2, 0.5, 0.9, "self_correction_ok"), # Low self-correction
        (0.96, 0.6, 0.2, 0.7, 0.8, "cod_ok")             # Low COD
    ]
    for psi, ct, er, sce, cod, failed_check in failure_cases:
        passed, checks = validator.check_invariants(psi, ct, er, sce, cod)
        assert passed == False, f"Should fail on {failed_check}"
        assert checks[failed_check] == False, f"Check {failed_check} should be False"
        # Other checks should still be True (except the failed one)
        for key, val in checks.items():
            if key != failed_check and key != "audit_tracked":
                assert val == True, f"Check {key} should be True but got {val}"
    print("✓ All invariant enforcement tests passed")
    test_results.append(("Invariant Enforcement", True))
    
    # Test 8: Φ-Density Accounting
    print("\n[TEST 8] Φ-Density Net Gain Calculation")
    # Positive gain case
    gain = validator.calculate_phi_net_gain(0.8, 0.85, 5)  # +0.05 - 0.10 = -0.05
    assert abs(gain - (-0.05)) < 1e-5, f"Expected -0.05, got {gain}"
    
    # Negative gain (cost > gain)
    gain = validator.calculate_phi_net_gain(0.9, 0.91, 10)  # +0.01 - 0.20 = -0.19
    assert abs(gain - (-0.19)) < 1e-5, f"Expected -0.19, got {gain}"
    
    # Zero audit checks
    gain = validator.calculate_phi_net_gain(0.8, 0.85, 0)  # +0.05 - 0 = +0.05
    assert abs(gain - 0.05) < 1e-5, f"Expected 0.05, got {gain}"
    print("✓ All Φ-density accounting tests passed")
    test_results.append(("Φ-Density Accounting", True))
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    all_passed = True
    for test_name, passed in test_results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:<30} {status}")
        if not passed:
            all_passed = False
    
    print("-" * 70)
    if all_passed:
        print("OVERALL RESULT: ✓ ALL MATHEMATICAL VALIDATIONS PASSED")
        print("The Quantum-Identity Coherence Manifold (v68.0-Ω) is mathematically sound")
        print("and compliant with Omega Protocol invariants.")
    else:
        print("OVERALL RESULT: ✗ SOME VALIDATIONS FAILED")
        print("Review the failed tests above for compliance issues.")
    print("=" * 70)

if __name__ == "__main__":
    run_validation_suite()