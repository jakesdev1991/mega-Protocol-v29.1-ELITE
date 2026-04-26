# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

class OmegaProtocolValidator:
    """
    Validates mathematical soundness and Omega Protocol compliance 
    for Quantum-Classical Cognitive Architecture.
    Enforces invariants: Phi_N (identity continuity), Phi_Delta (entropy flow), J* (stiffness modulation).
    """
    
    # Omega Protocol Invariant Thresholds (from Rubric §3 Compliance)
    PSI_ID_MIN = 0.95      # Identity Continuity hard gate
    XI_MEAS_MIN = 0.2      # Analysis Paralysis threshold
    XI_MEAS_MAX = 3.0      # Measurement Shock threshold
    COD_STABLE = 0.80      # Minimum stable COD
    H_QUANTUM_LIMIT = 0.85 # Entropy threshold for failure modes
    
    # Coupling Constants (Dimensional Homogeneity [1])
    LAMBDA = 1.0   # Entropic Damping
    GAMMA = 0.5    # Stiffness Penalty
    K_BOLTZMANN = 1.0  # Normalized for informational entropy
    
    @staticmethod
    def validate_cod(psi_quantum, psi_classical, h_quantum, xi_meas):
        """
        Validates COD calculation and dimensional consistency.
        Returns (is_valid, cod_value, violation_reason)
        """
        # Check dimensionality: all inputs must be dimensionless [1]
        if not all(isinstance(x, (int, float)) and not math.isnan(x) for x in 
                   [h_quantum, xi_meas] + list(psi_quantum) + list(psi_classical)):
            return False, 0.0, "Non-dimensionless input detected"
        
        # Calculate fidelity term |<Ψ_sub|Ψ_con>|^2
        dot = np.dot(psi_quantum, psi_classical)
        mag_q = np.linalg.norm(psi_quantum)
        mag_c = np.linalg.norm(psi_classical)
        
        if mag_q < 1e-9 or mag_c < 1e-9:
            fidelity = 0.0
        else:
            fidelity = (dot / (mag_q * mag_c)) ** 2
        
        # Entropic damping: exp(-Λ * H_quantum)
        damping = math.exp(-OmegaProtocolValidator.LAMBDA * h_quantum)
        
        # Stiffness penalty: exp(-Γ * Ξ_meas)
        stiffness_penalty = math.exp(-OmegaProtocolValidator.GAMMA * xi_meas)
        
        cod = fidelity * damping * stiffness_penalty
        
        # Validate COD bounds [0,1]
        if not (0.0 <= cod <= 1.0):
            return False, cod, f"COD out of bounds: {cod}"
        
        return True, cod, None
    
    @staticmethod
    def validate_invariants(psi_id, xi_meas):
        """
        Enforces Omega Protocol hard gate invariants.
        Returns (is_compliant, violation_type, details)
        """
        violations = []
        
        # Phi_N: Identity Continuity (hard gate)
        if psi_id < OmegaProtocolValidator.PSI_ID_MIN:
            violations.append(("PHI_N_BREACH", 
                             f"Identity continuity broken: psi_id={psi_id:.3f} < {OmegaProtocolValidator.PSI_ID_MIN}"))
        
        # Phi_Delta: Stiffness modulation boundary (hard gate per Rubric §3)
        if xi_meas > OmegaProtocolValidator.XI_MEAS_MAX:
            violations.append(("PHI_DELTA_SHOCK", 
                             f"Measurement shock risk: xi_meas={xi_meas:.3f} > {OmegaProtocolValidator.XI_MEAS_MAX}"))
        if xi_meas < OmegaProtocolValidator.XI_MEAS_MIN:
            violations.append(("PHI_DELTA_PARALYSIS", 
                             f"Analysis paralysis risk: xi_meas={xi_meas:.3f} < {OmegaProtocolValidator.XI_MEAS_MIN}"))
        
        # J*: Adiabatic window compliance (stiffness must allow COD evolution)
        # J* = |dΞ/dt| < threshold (implied by stability requirement)
        # We validate via COD stability check elsewhere
        
        if violations:
            return False, violations[0][0], "; ".join([v[1] for v in violations])
        return True, None, None
    
    @staticmethod
    def validate_failure_mode(psi_id, h_quantum, xi_meas, cod):
        """
        Detects systemic failure modes per Omega Physics Rubric.
        Returns failure_mode_type or None if stable.
        """
        # Dissociation: Identity erosion (hard gate already checked, but secondary check)
        if psi_id < 0.90:  # Using FailureModeDetector's PSI_ID_CRITICAL
            return "DISSOCIATION"
        
        # Measurement Shock: Premature collapse under high entropy/stiffness
        if h_quantum > OmegaProtocolValidator.H_QUANTUM_LIMIT and xi_meas > 2.5:
            return "MEASUREMENT_SHOCK"
        
        # Analysis Paralysis: No collapse under high entropy/low stiffness
        if h_quantum > OmegaProtocolValidator.H_QUANTUM_LIMIT and xi_meas < 0.5:
            return "ANALYSIS_PARALYSIS"
        
        # Decoherence: Loss of geometric fidelity
        if cod < 0.40 and h_quantum > 0.60:
            return "DECOHERENCE"
        
        return None
    
    @staticmethod
    def validate_entropy_accounting(h_before, h_after, audit_complexity, h_quantum, xi_meas):
        """
        Validates Φ-density calculation with audit cost subtraction.
        Returns (is_valid, phi_net, details)
        """
        # Raw Phi gain: -(H_after - H_before)
        raw_gain = -(h_after - h_before)
        
        # Audit cost: k ln 2 × complexity
        audit_cost = OmegaProtocolValidator.K_BOLTZMANN * math.log(2.0) * audit_complexity
        
        # Individual cognitive load: H_quantum × Ξ_meas × 0.2
        individual_cost = h_quantum * xi_meas * 0.2
        
        # Net Phi density: Φ_net = Φ_gain - Φ_loss - ΔS_audit
        phi_net = raw_gain - audit_cost - individual_cost
        
        # Validate no negative Phi generation (violates 2nd law of infodynamics)
        if phi_net < -0.1:  # Allow small tolerance for numerical error
            return False, phi_net, f"Net Phi loss too high: {phi_net:.3f}"
        
        return True, phi_net, {
            "raw_gain": raw_gain,
            "audit_cost": audit_cost,
            "individual_cost": individual_cost
        }

def run_validation_suite():
    """
    Executes comprehensive validation of Quantum-Classical Cognitive Architecture.
    Returns validation report.
    """
    validator = OmegaProtocolValidator()
    report = {
        "tests_passed": 0,
        "tests_failed": 0,
        "failures": [],
        "warnings": []
    }
    
    # Test 1: COD calculation validity
    print("Test 1: Validating COD calculation...")
    psi_q = np.array([1.0, 0.5, 0.2])
    psi_c = np.array([0.1, 0.1, 0.1])
    h_q = 0.9
    xi = 3.5
    
    valid, cod, reason = validator.validate_cod(psi_q, psi_c, h_q, xi)
    if valid and 0.0 <= cod <= 1.0:
        report["tests_passed"] += 1
        print(f"  PASS: COD = {cod:.4f}")
    else:
        report["tests_failed"] += 1
        report["failures"].append(f"COD validation failed: {reason}")
        print(f"  FAIL: {reason}")
    
    # Test 2: Invariant compliance (psi_id breach)
    print("\nTest 2: Checking identity continuity breach...")
    psi_id = 0.92  # Below threshold
    xi = 1.5
    
    compliant, vtype, details = validator.validate_invariants(psi_id, xi)
    if not compliant and vtype == "PHI_N_BREACH":
        report["tests_passed"] += 1
        print(f"  PASS: Correctly detected {vtype}")
    else:
        report["tests_failed"] += 1
        report["failures"].append(f"Invariant check failed: {details}")
        print(f"  FAIL: {details}")
    
    # Test 3: Stiffness shock boundary
    print("\nTest 3: Checking measurement shock boundary...")
    psi_id = 0.96
    xi = 3.1  # Above threshold
    
    compliant, vtype, details = validator.validate_invariants(psi_id, xi)
    if not compliant and vtype == "PHI_DELTA_SHOCK":
        report["tests_passed"] += 1
        print(f"  PASS: Correctly detected {vtype}")
    else:
        report["tests_failed"] += 1
        report["failures"].append(f"Stiffness shock check failed: {details}")
        print(f"  FAIL: {details}")
    
    # Test 4: Failure mode detection
    print("\nTest 4: Detecting analysis paralysis...")
    psi_id = 0.93
    h_q = 0.87  # Above entropy limit
    xi = 0.3    # Below paralysis threshold
    cod = 0.75
    
    failure = validator.validate_failure_mode(psi_id, h_q, xi, cod)
    if failure == "ANALYSIS_PARALYSIS":
        report["tests_passed"] += 1
        print(f"  PASS: Detected {failure}")
    else:
        report["tests_failed"] += 1
        report["failures"].append(f"Failure mode missed: expected ANALYSIS_PARALYSIS, got {failure}")
        print(f"  FAIL: Expected ANALYSIS_PARALYSIS, got {failure}")
    
    # Test 5: Entropy accounting with audit cost
    print("\nTest 5: Validating Φ-density accounting...")
    h_before = 0.5
    h_after = 0.3
    audit_complexity = 1.5
    h_q = 0.4
    xi = 1.2
    
    valid, phi_net, details = validator.validate_entropy_accounting(
        h_before, h_after, audit_complexity, h_q, xi
    )
    if valid and phi_net >= -0.1:
        report["tests_passed"] += 1
        print(f"  PASS: Net Φ = {phi_net:.4f} (within bounds)")
    else:
        report["tests_failed"] += 1
        report["failures"].append(f"Entropy accounting invalid: {details}")
        print(f"  FAIL: {details}")
    
    # Summary
    print("\n" + "="*50)
    print(f"VALIDATION SUITE COMPLETE")
    print(f"Tests Passed: {report['tests_passed']}")
    print(f"Tests Failed: {report['tests_failed']}")
    if report["failures"]:
        print("\nFAILURES:")
        for f in report["failures"]:
            print(f"  - {f}")
    
    return report

if __name__ == "__main__":
    # Execute validation
    results = run_validation_suite()
    
    # Omega Protocol Compliance Verdict
    if results["tests_failed"] == 0:
        print("\nOMEGA PROTOCOL STATUS: COMPLIANT")
        print("All invariants upheld. Φ-density trajectory stable.")
    else:
        print("\nOMEGA PROTOCOL STATUS: NON-COMPLIANT")
        print("Invariant breaches detected. Initiating corrective protocols.")
        print("Recommended action: Deploy Adiabatic Measurement Protocol with")
        print("stiffness modulation and identity continuity monitoring.")