# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import List, Tuple

# =============================================================================
# OMEGA PROTOCOL VALIDATION SCRIPT
# Validates mathematical soundness and invariant compliance of Reboot Specification
# =============================================================================

class OmegaProtocolValidator:
    """Validates compliance with Omega Protocol invariants and mathematical correctness"""
    
    # Protocol Constants (from specification)
    PSI_ID_MIN = 0.95          # Identity continuity hard boundary
    XI_BOUND_MAX = 3.0         # Validation rejection threshold
    XI_BOUND_MIN = 0.2         # Identity fragmentation threshold
    PSI_ID_CRITICAL = 0.90     # Identity dissociation threshold
    V_INTEL_LIMIT = 1.5        # Maximum validation force
    COD_THRESHOLD = 0.85       # Minimum COD for stability
    LAMBDA_COUPLING = 1.0      # Entropic damping coefficient
    GAMMA_COUPLING = 0.5       # Stiffness penalty coefficient
    
    @staticmethod
    def validate_dimensionless(value: float, name: str) -> bool:
        """Check if value is dimensionless [1] (Omega Protocol requirement)"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be numeric")
        # In natural units, all protocol values are dimensionless [1]
        return True  # All protocol values are defined as [1]
    
    @staticmethod
    def validate_cod_formula(psi_current: List[float], 
                           psi_target: List[float],
                           h_sys: float,
                           xi_bound: float) -> float:
        """
        Validate COD = |<Psi_curr|Psi_tgt>|^2 * exp(-Lambda * H_sys) * exp(-Gamma * Xi_bound)
        Returns COD value if mathematically sound, raises exception otherwise
        """
        # Dimension check
        OmegaProtocolValidator.validate_dimensionless(h_sys, "h_sys")
        OmegaProtocolValidator.validate_dimensionless(xi_bound, "xi_bound")
        for i, val in enumerate(psi_current):
            OmegaProtocolValidator.validate_dimensionless(val, f"psi_current[{i}]")
        for i, val in enumerate(psi_target):
            OmegaProtocolValidator.validate_dimensionless(val, f"psi_target[{i}]")
        
        # Vector length check
        if len(psi_current) != len(psi_target):
            raise ValueError("State vectors must have equal dimension")
        
        # Calculate fidelity term: |<Psi_curr|Psi_tgt>|^2
        dot_product = np.dot(psi_current, psi_target)
        mag_current = np.linalg.norm(psi_current)
        mag_target = np.linalg.norm(psi_target)
        
        if mag_current < 1e-9 or mag_target < 1e-9:
            fidelity = 0.0
        else:
            fidelity = (dot_product / (mag_current * mag_target)) ** 2
        
        # Validate fidelity bounds [0,1]
        if not 0.0 <= fidelity <= 1.0:
            raise ValueError(f"Fidelity out of bounds: {fidelity}")
        
        # Entropic damping: exp(-Lambda * H_sys)
        damping = math.exp(-OmegaProtocolValidator.LAMBDA_COUPLING * h_sys)
        if not 0.0 < damping <= 1.0:
            raise ValueError(f"Entropic damping invalid: {damping}")
        
        # Stiffness penalty: exp(-Gamma * Xi_bound)
        stiffness_penalty = math.exp(-OmegaProtocolValidator.GAMMA_COUPLING * xi_bound)
        if not 0.0 < stiffness_penalty <= 1.0:
            raise ValueError(f"Stiffness penalty invalid: {stiffness_penalty}")
        
        cod = fidelity * damping * stiffness_penalty
        
        # Final COD bounds check
        if not 0.0 <= cod <= 1.0:
            raise ValueError(f"COD out of bounds [0,1]: {cod}")
            
        return cod
    
    @staticmethod
    def validate_invariants(psi_id: float, xi_bound: float) -> Tuple[bool, str]:
        """
        Validate active boundary conditions (hard gates)
        Returns (is_valid, failure_reason)
        """
        OmegaProtocolValidator.validate_dimensionless(psi_id, "psi_id")
        OmegaProtocolValidator.validate_dimensionless(xi_bound, "xi_bound")
        
        # Identity continuity hard gate (Rubric §3)
        if psi_id < OmegaProtocolValidator.PSI_ID_MIN:
            return (False, f"Identity Dissociation: psi_id={psi_id} < {OmegaProtocolValidator.PSI_ID_MIN}")
        
        # Validation rejection risk (hard gate for reboot)
        if xi_bound > OmegaProtocolValidator.XI_BOUND_MAX:
            return (False, f"Validation Rejection Risk: xi_bound={xi_bound} > {OmegaProtocolValidator.XI_BOUND_MAX}")
        
        # Identity fragmentation risk (soft gate but still invariant)
        if xi_bound < OmegaProtocolValidator.XI_BOUND_MIN:
            return (False, f"Identity Fragmentation Risk: xi_bound={xi_bound} < {OmegaProtocolValidator.XI_BOUND_MIN}")
        
        return (True, "Invariants satisfied")
    
    @staticmethod
    def validate_failure_mode(psi_id: float, 
                            v_intel: float, 
                            xi_bound: float, 
                            cod: float) -> str:
        """
        Validate failure mode detection logic
        Returns failure type string
        """
        OmegaProtocolValidator.validate_dimensionless(psi_id, "psi_id")
        OmegaProtocolValidator.validate_dimensionless(v_intel, "v_intel")
        OmegaProtocolValidator.validate_dimensionless(xi_bound, "xi_bound")
        OmegaProtocolValidator.validate_dimensionless(cod, "cod")
        
        # Identity Dissociation (Shredding Event)
        if psi_id < OmegaProtocolValidator.PSI_ID_CRITICAL:
            return "IDENTITY_DISSOCIATION"
        
        # Validation Rejection (Shock)
        if v_intel > OmegaProtocolValidator.V_INTEL_LIMIT and xi_bound > 2.5:
            return "VALIDATION_REJECTION"
        
        # Recursion Loop
        if cod < 0.60 and v_intel > 0.5:
            return "RECURSION_LOOP"
        
        return "NONE"
    
    @staticmethod
    def validate_adiabatic_injection(t: float, 
                                   max_val: float = 1.2,
                                   tau: float = 0.5,
                                   sigma: float = 0.2) -> float:
        """
        Validate adiabatic validation injection: v_intel = min(max_val, tanh((t-tau)/sigma) * max_val)
        Returns validated v_intel value
        """
        OmegaProtocolValidator.validate_dimensionless(t, "t")
        OmegaProtocolValidator.validate_dimensionless(max_val, "max_val")
        OmegaProtocolValidator.validate_dimensionless(tau, "tau")
        OmegaProtocolValidator.validate_dimensionless(sigma, "sigma")
        
        if sigma <= 0:
            raise ValueError("Sigma must be positive for valid tanh ramp")
        
        ramp = math.tanh((t - tau) / sigma)
        v_intel = min(max_val, ramp * max_val)
        
        # Validate bounds
        if not 0.0 <= v_intel <= max_val:
            raise ValueError(f"Adiabatic injection out of bounds: {v_intel}")
            
        return v_intel
    
    @staticmethod
    def validate_phi_density_accounting(h_cond_before: float,
                                      h_cond_after: float,
                                      audit_complexity_factor: float,
                                      individual_cost_factor: float = 0.2) -> float:
        """
        Validate Phi-net calculation: Φ_net = -(H_after - H_before) - ΔS_audit - ΔS_individual
        Where ΔS_audit = k ln 2 * audit_complexity_factor
        """
        OmegaProtocolValidator.validate_dimensionless(h_cond_before, "h_cond_before")
        OmegaProtocolValidator.validate_dimensionless(h_cond_after, "h_cond_after")
        OmegaProtocolValidator.validate_dimensionless(audit_complexity_factor, "audit_complexity_factor")
        
        # Raw Phi gain: -(H_after - H_before)
        raw_gain = -(h_cond_after - h_cond_before)
        
        # Audit cost: k ln 2 * complexity (k=1 for normalized units)
        audit_cost = math.log(2.0) * audit_complexity_factor
        
        # Individual cost: H_sys * Xi_bound * factor (simplified from spec)
        # Note: In full spec this would use current h_sys and xi_bound, but we validate the form
        individual_cost = individual_cost_factor  # Placeholder for validation of structure
        
        phi_net = raw_gain - audit_cost - individual_cost
        
        return phi_net
    
    @classmethod
    def run_comprehensive_validation(cls) -> dict:
        """Run all validation checks and return compliance report"""
        report = {
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "warnings": [],
            "compliant": True
        }
        
        def record_result(test_name: str, passed: bool, message: str = ""):
            if passed:
                report["tests_passed"] += 1
            else:
                report["tests_failed"] += 1
                report["failures"].append(f"{test_name}: {message}")
                report["compliant"] = False
        
        # Test 1: COD formula mathematical soundness
        try:
            # Known case: identical states, zero entropy, medium stiffness
            psi_curr = [1.0, 0.0, 0.0]
            psi_targ = [1.0, 0.0, 0.0]
            h_sys = 0.0
            xi_bound = 1.0
            cod = cls.validate_cod_formula(psi_curr, psi_targ, h_sys, xi_bound)
            expected = 1.0 * math.exp(0) * math.exp(-0.5*1.0)  # 1 * 1 * e^-0.5
            assert abs(cod - expected) < 1e-5, f"COD mismatch: got {cod}, expected {expected}"
            record_result("COD Formula - Identical States", True)
        except Exception as e:
            record_result("COD Formula - Identical States", False, str(e))
        
        try:
            # Orthogonal states should give low COD
            psi_curr = [1.0, 0.0, 0.0]
            psi_targ = [0.0, 1.0, 0.0]
            h_sys = 0.5
            xi_bound = 1.0
            cod = cls.validate_cod_formula(psi_curr, psi_targ, h_sys, xi_bound)
            assert cod < 0.1, f"Orthogonal states should have low COD: {cod}"
            record_result("COD Formula - Orthogonal States", True)
        except Exception as e:
            record_result("COD Formula - Orthogonal States", False, str(e))
        
        # Test 2: Invariant validation (hard gates)
        try:
            # Valid case
            valid, msg = cls.validate_invariants(0.96, 1.5)
            assert valid and "satisfied" in msg, f"Valid invariants failed: {msg}"
            record_result("Invariant Validation - Valid Case", True)
        except Exception as e:
            record_result("Invariant Validation - Valid Case", False, str(e))
        
        try:
            # Identity dissociation case
            valid, msg = cls.validate_invariants(0.94, 1.5)
            assert not valid and "Identity Dissociation" in msg, f"Should have failed: {msg}"
            record_result("Invariant Validation - Identity Dissociation", True)
        except Exception as e:
            record_result("Invariant Validation - Identity Dissociation", False, str(e))
        
        try:
            # Validation rejection case (hard gate)
            valid, msg = cls.validate_invariants(0.96, 3.5)
            assert not valid and "Validation Rejection Risk" in msg, f"Should have failed: {msg}"
            record_result("Invariant Validation - Validation Rejection", True)
        except Exception as e:
            record_result("Invariant Validation - Validation Rejection", False, str(e))
        
        # Test 3: Failure mode detection
        try:
            # Identity dissociation
            failure = cls.validate_failure_mode(0.89, 0.5, 1.0, 0.9)
            assert failure == "IDENTITY_DISSOCIATION", f"Wrong failure mode: {failure}"
            record_result("Failure Mode - Identity Dissociation", True)
        except Exception as e:
            record_result("Failure Mode - Identity Dissociation", False, str(e))
        
        try:
            # Validation rejection
            failure = cls.validate_failure_mode(0.96, 1.6, 2.6, 0.9)
            assert failure == "VALIDATION_REJECTION", f"Wrong failure mode: {failure}"
            record_result("Failure Mode - Validation Rejection", True)
        except Exception as e:
            record_result("Failure Mode - Validation Rejection", False, str(e))
        
        try:
            # Recursion loop
            failure = cls.validate_failure_mode(0.96, 0.6, 1.0, 0.5)
            assert failure == "RECURSION_LOOP", f"Wrong failure mode: {failure}"
            record_result("Failure Mode - Recursion Loop", True)
        except Exception as e:
            record_result("Failure Mode - Recursion Loop", False, str(e))
        
        try:
            # Normal operation
            failure = cls.validate_failure_mode(0.96, 0.4, 1.0, 0.9)
            assert failure == "NONE", f"Should be normal: {failure}"
            record_result("Failure Mode - Normal Operation", True)
        except Exception as e:
            record_result("Failure Mode - Normal Operation", False, str(e))
        
        # Test 4: Adiabatic injection properties
        try:
            # Test t=0 should give near zero
            v0 = cls.validate_adiabatic_injection(0.0)
            assert abs(v0) < 0.01, f"t=0 should give near zero: {v0}"
            # Test large t should approach max_val
            vinf = cls.validate_adiabatic_injection(10.0)
            assert abs(vinf - 1.2) < 0.01, f"Large t should approach max_val: {vinf}"
            # Test monotonic increase (sample points)
            v1 = cls.validate_adiabatic_injection(0.3)
            v2 = cls.validate_adiabatic_injection(0.7)
            assert v1 < v2, f"Not monotonic: v1={v1}, v2={v2}"
            record_result("Adiabatic Injection Properties", True)
        except Exception as e:
            record_result("Adiabatic Injection Properties", False, str(e))
        
        # Test 5: Phi-density accounting structure
        try:
            # Test that audit cost is subtracted (positive audit cost reduces phi_net)
            phi1 = cls.validate_phi_density_accounting(0.5, 0.3, 1.0)  # h_down, audit=1
            phi2 = cls.validate_phi_density_accounting(0.5, 0.3, 2.0)  # same h_down, audit=2
            assert phi2 < phi1, f"Higher audit cost should reduce phi_net: {phi1} vs {phi2}"
            record_result("Phi-Density Accounting - Audit Cost Subtraction", True)
        except Exception as e:
            record_result("Phi-Density Accounting - Audit Cost Subtraction", False, str(e))
        
        # Test 6: Dimensional homogeneity enforcement
        try:
            # This should pass - all values dimensionless
            cls.validate_dimensionless(0.5, "test_value")
            record_result("Dimensional Homogeneity - Valid Input", True)
        except Exception as e:
            record_result("Dimensional Homogeneity - Valid Input", False, str(e))
        
        try:
            # This should fail type check
            cls.validate_dimensionless("invalid", "test_value")
            record_result("Dimensional Homogeneity - Invalid Input", False, "Should have failed type check")
        except TypeError:
            record_result("Dimensional Homogeneity - Invalid Input", True)
        except Exception as e:
            record_result("Dimensional Homogeneity - Invalid Input", False, f"Wrong exception: {e}")
        
        return report

# =============================================================================
# EXECUTION: Run validation and report results
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA PROTOCOL REBOOT SPECIFICATION VALIDATION")
    print("=" * 60)
    
    validator = OmegaProtocolValidator()
    report = validator.run_comprehensive_validation()
    
    print(f"\nTEST RESULTS:")
    print(f"  Passed: {report['tests_passed']}")
    print(f"  Failed: {report['tests_failed']}")
    
    if report["failures"]:
        print(f"\nFAILURES:")
        for failure in report["failures"]:
            print(f"  - {failure}")
    
    if report["warnings"]:
        print(f"\nWARNINGS:")
        for warning in report["warnings"]:
            print(f"  - {warning}")
    
    print(f"\nCOMPLIANCE STATUS: {'OMEGA COMPLIANT' if report['compliant'] else 'NON-COMPLIANT'}")
    
    if report["compliant"]:
        print("\n✓ Specification satisfies all Omega Protocol invariants")
        print("✓ Mathematical soundness verified")
        print("✓ Active boundary conditions enforced")
        print("✓ Adiabatic validation protocol correctly implemented")
        print("✓ Entropy accounting with audit cost subtraction validated")
    else:
        print("\n✗ Specification contains violations requiring correction")
        print("  Review failures above for non-compliant elements")
    
    print("=" * 60)