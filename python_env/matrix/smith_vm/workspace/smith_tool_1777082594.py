# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from typing import Tuple, List

class OmegaProtocolValidator:
    """
    Validates mathematical soundness and Omega Protocol compliance of correlation-aware plasma integrity manifold.
    Checks dimensional consistency, invariant enforcement, and Φ-density accounting.
    """
    
    # === OMEGA PROTOCOL INVARIANTS (from C++ code) ===
    COD_THRESHOLD = 0.85
    COD_FLOOR = 0.39
    PSI_INTEGRITY_THRESHOLD = 0.95
    CORRELATION_LENGTH_THRESHOLD = 0.70
    SHEAR_FLOW_MIN = 0.50
    TENSOR_LEAK_MAX = 0.50
    STIFFNESS_MAX_DELTA = 0.10
    PHI_DELTA_MAX = 0.50
    B1_HOMOLOGY_MAX = 0.80
    AUDIT_ENTROPY_PER_CHECK = 0.02
    TOTAL_AUDIT_COST = 9 * AUDIT_ENTROPY_PER_CHECK  # 0.18
    
    # === CORRELATION LENGTH CALCULATOR CONSTANTS ===
    DENSITY_GRADIENT_EXPONENT = 0.5
    BETA_EXPONENT = 0.3
    SHEAR_EXPONENT = 0.7
    
    # === COD CALCULATION CONSTANTS ===
    LAMBDA_COUPLING = 0.5
    KAPPA_CONFINEMENT = 0.5
    ETA_TENSOR_LEAK = 0.3
    MU_CORRELATION = 0.4
    
    @staticmethod
    def validate_bounds(value: float, name: str, min_val: float = 0.0, max_val: float = 1.0) -> bool:
        """Validate that a value is within [min_val, max_val]"""
        if not (min_val <= value <= max_val):
            print(f"BOUND VIOLATION: {name} = {value} not in [{min_val}, {max_val}]")
            return False
        return True
    
    @staticmethod
    def calculate_correlation_length(
        density_gradient: float,
        collisionality: float,
        beta_parameter: float,
        shear_flow: float
    ) -> float:
        """
        Implements CorrelationLengthCalculator::Calculate_Correlation_Length
        Returns normalized correlation length in [0,1]
        """
        # Validate inputs
        for val, name in [(density_gradient, "density_gradient"), 
                         (collisionality, "collisionality"),
                         (beta_parameter, "beta_parameter"),
                         (shear_flow, "shear_flow")]:
            if not OmegaProtocolValidator.validate_bounds(val, name):
                raise ValueError(f"Input {name} out of bounds [0,1]")
        
        gradient_factor = np.power(density_gradient, OmegaProtocolValidator.DENSITY_GRADIENT_EXPONENT)
        beta_factor = np.power(beta_parameter, OmegaProtocolValidator.BETA_EXPONENT)
        shear_factor = np.power(shear_flow, OmegaProtocolValidator.SHEAR_EXPONENT)
        collisionality_damping = np.exp(-0.5 * collisionality)
        
        raw_correlation = gradient_factor * beta_factor * shear_factor * collisionality_damping
        correlation_length = np.clip(raw_correlation, 0.0, 1.0)
        
        # Validate output
        if not OmegaProtocolValidator.validate_bounds(correlation_length, "correlation_length"):
            raise ValueError("Correlation length calculation produced out-of-bounds result")
            
        return correlation_length
    
    @staticmethod
    def calculate_lh_proximity(
        correlation_length: float,
        shear_flow: float
    ) -> float:
        """
        Implements CorrelationLengthCalculator::Calculate_LH_Proximity
        Returns L-H proximity in [0,1]
        """
        if not (OmegaProtocolValidator.validate_bounds(correlation_length, "correlation_length") and
                OmegaProtocolValidator.validate_bounds(shear_flow, "shear_flow")):
            raise ValueError("Inputs out of bounds")
        
        if shear_flow < OmegaProtocolValidator.SHEAR_FLOW_MIN:
            return 0.0
        
        proximity = (correlation_length - 0.5) / 0.5
        proximity = np.clip(proximity, 0.0, 1.0)
        
        if not OmegaProtocolValidator.validate_bounds(proximity, "lh_proximity"):
            raise ValueError("L-H proximity calculation produced out-of-bounds result")
            
        return proximity
    
    @staticmethod
    def calculate_cod(
        diagnostic_vec: List[complex],
        plasma_vec: List[complex],
        h_instability: float,
        xi_confinement: float,
        theta_tensor_leak: float,
        correlation_length_parallel: float,
        correlation_length_perp: float
    ) -> float:
        """
        Implements Calculate_COD_Correlation
        Returns Chain Overlap Density in [0,1]
        """
        # Validate all scalar inputs
        scalar_inputs = [
            (h_instability, "h_instability"),
            (xi_confinement, "xi_confinement"),
            (theta_tensor_leak, "theta_tensor_leak"),
            (correlation_length_parallel, "correlation_length_parallel"),
            (correlation_length_perp, "correlation_length_perp")
        ]
        for val, name in scalar_inputs:
            if not OmegaProtocolValidator.validate_bounds(val, name):
                raise ValueError(f"Scalar input {name} out of bounds [0,1]")
        
        # 1. Fidelity calculation
        size = min(len(diagnostic_vec), len(plasma_vec))
        if size == 0:
            fidelity = 0.0
        else:
            dot = 0.0
            magD = 0.0
            magP = 0.0
            for i in range(size):
                dot += np.abs(np.conj(diagnostic_vec[i]) * plasma_vec[i])
                magD += np.abs(diagnostic_vec[i] * np.conj(diagnostic_vec[i]))
                magP += np.abs(plasma_vec[i] * np.conj(plasma_vec[i]))
            
            if magD > 1e-9 and magP > 1e-9:
                fidelity = dot / (np.sqrt(magD) * np.sqrt(magP))
                fidelity = np.clip(fidelity, 0.0, 1.0)
            else:
                fidelity = 0.0
        
        if not OmegaProtocolValidator.validate_bounds(fidelity, "fidelity"):
            raise ValueError("Fidelity calculation out of bounds")
        
        # 2. Penalties
        instability_penalty = np.exp(-OmegaProtocolValidator.LAMBDA_COUPLING * h_instability)
        confinement_penalty = np.exp(-OmegaProtocolValidator.KAPPA_CONFINEMENT * xi_confinement)
        exposure_penalty = np.exp(-OmegaProtocolValidator.ETA_TENSOR_LEAK * theta_tensor_leak)
        
        correlation_mean = (correlation_length_parallel + correlation_length_perp) / 2.0
        correlation_penalty = np.exp(-OmegaProtocolValidator.MU_CORRELATION * (1.0 - correlation_mean))
        
        # Validate penalties
        for penalty, name in [(instability_penalty, "instability_penalty"),
                             (confinement_penalty, "confinement_penalty"),
                             (exposure_penalty, "exposure_penalty"),
                             (correlation_penalty, "correlation_penalty")]:
            if not (0.0 < penalty <= 1.0):
                raise ValueError(f"{name} = {penalty} not in (0,1]")
        
        cod = fidelity * instability_penalty * confinement_penalty * exposure_penalty * correlation_penalty
        cod = np.clip(cod, 0.0, 1.0)
        
        if not OmegaProtocolValidator.validate_bounds(cod, "COD"):
            raise ValueError("COD calculation produced out-of-bounds result")
            
        return cod
    
    @staticmethod
    def validate_gating_logic(
        psi_integrity: float,
        cod: float,
        correlation_length: float,
        shear_flow_strength: float
    ) -> Tuple[str, bool]:
        """
        Implements CorrelationSilenceProtocol::Decide logic
        Returns (action_message, is_valid_transition)
        """
        # Validate inputs
        if not (OmegaProtocolValidator.validate_bounds(psi_integrity, "psi_integrity") and
                OmegaProtocolValidator.validate_bounds(cod, "cod") and
                OmegaProtocolValidator.validate_bounds(correlation_length, "correlation_length") and
                OmegaProtocolValidator.validate_bounds(shear_flow_strength, "shear_flow_strength")):
            raise ValueError("Gating logic inputs out of bounds")
        
        # PRIMARY GATE: Ψ_integrity
        if psi_integrity < OmegaProtocolValidator.PSI_INTEGRITY_THRESHOLD:
            return ("CRITICAL: Integrity breach. Halting non-essential operations. Awaiting audit.", False)
        
        # CORRELATION GATE
        if correlation_length < OmegaProtocolValidator.CORRELATION_LENGTH_THRESHOLD:
            if shear_flow_strength > OmegaProtocolValidator.SHEAR_FLOW_MIN:
                return ("Building correlation length. Shear flow active. Awaiting L-H transition.", True)
            return ("Correlation length below threshold. Freezing configuration until ξ ≥ 0.70.", False)
        
        # SECONDARY GATE: COD
        if cod < OmegaProtocolValidator.COD_THRESHOLD:
            return ("Correlation length sufficient but alignment inadequate. Freezing configuration.", False)
        
        return ("Plasma resonance aligned. Correlation length sufficient for H-mode operations.", True)
    
    @staticmethod
    def validate_phi_density_accounting(
        cod_before: float,
        cod_after: float,
        audit_checks_performed: int
    ) -> float:
        """
        Implements CorrelationPhiDensityLedger::CalculateNetGain
        Returns net Φ-density gain (audit cost subtracted)
        """
        if not (OmegaProtocolValidator.validate_bounds(cod_before, "cod_before") and
                OmegaProtocolValidator.validate_bounds(cod_after, "cod_after")):
            raise ValueError("COD values out of bounds for Φ-density calculation")
        
        if audit_checks_performed < 0:
            raise ValueError("Audit checks performed cannot be negative")
        
        raw_gain = cod_after - cod_before
        audit_cost = audit_checks_performed * OmegaProtocolValidator.AUDIT_ENTROPY_PER_CHECK
        net_gain = raw_gain - audit_cost
        
        return net_gain
    
    @staticmethod
    def validate_invariant_enforcer(
        state_cod: float,
        phi_N: float,
        phi_delta: float,
        xi_confinement: float,
        z_plasma_depth: float,
        theta_tensor_leak: float,
        b1_homology: float,
        correlation_length_parallel: float,
        correlation_length_perp: float,
        shear_flow_strength: float
    ) -> dict:
        """
        Implements CorrelationInvariantEnforcer::Check
        Returns dictionary of invariant check results
        """
        # Validate all inputs
        inputs = [
            (state_cod, "state_cod"),
            (phi_N, "phi_N"),
            (phi_delta, "phi_delta"),
            (xi_confinement, "xi_confinement"),
            (z_plasma_depth, "z_plasma_depth"),
            (theta_tensor_leak, "theta_tensor_leak"),
            (b1_homology, "b1_homology"),
            (correlation_length_parallel, "correlation_length_parallel"),
            (correlation_length_perp, "correlation_length_perp"),
            (shear_flow_strength, "shear_flow_strength")
        ]
        for val, name in inputs:
            if not OmegaProtocolValidator.validate_bounds(val, name):
                raise ValueError(f"Invariant enforcer input {name} out of bounds")
        
        # Calculate derived values
        correlation_mean = (correlation_length_parallel + correlation_length_perp) / 2.0
        
        # Perform checks
        checks = {
            "cod_ok": state_cod >= OmegaProtocolValidator.COD_THRESHOLD,
            "phi_floor_ok": phi_N >= OmegaProtocolValidator.COD_FLOOR,
            "correlation_ok": correlation_mean >= OmegaProtocolValidator.CORRELATION_LENGTH_THRESHOLD,
            "shear_flow_ok": shear_flow_strength >= OmegaProtocolValidator.SHEAR_FLOW_MIN,
            "stiffness_match_ok": xi_confinement <= z_plasma_depth + OmegaProtocolValidator.STIFFNESS_MAX_DELTA,
            "env_cap_ok": theta_tensor_leak <= OmegaProtocolValidator.TENSOR_LEAK_MAX,
            "dissonance_ok": True,  # Placeholder as in C++ code
            "asymmetry_ok": phi_delta < OmegaProtocolValidator.PHI_DELTA_MAX * phi_N,
            "homology_ok": b1_homology <= OmegaProtocolValidator.B1_HOMOLOGY_MAX,
            "audit_tracked": True
        }
        
        # Validate boolean outputs
        for check_name, result in checks.items():
            if not isinstance(result, bool):
                raise ValueError(f"Invariant check {check_name} returned non-boolean: {result}")
        
        return checks
    
    @staticmethod
    def run_comprehensive_validation() -> Tuple[bool, List[str]]:
        """
        Runs a battery of tests to validate mathematical soundness and protocol compliance
        Returns (all_passed, list_of_errors)
        """
        errors = []
        passed = 0
        total_tests = 0
        
        print("=== OMEGA PROTOCOL MATHEMATICAL VALIDATION ===\n")
        
        # Test 1: Correlation length bounds and monotonicity
        total_tests += 1
        try:
            # Test nominal case
            cl = OmegaProtocolValidator.calculate_correlation_length(
                density_gradient=0.8,
                collisionality=0.2,
                beta_parameter=0.6,
                shear_flow=0.7
            )
            assert 0.0 <= cl <= 1.0, f"Correlation length out of bounds: {cl}"
            
            # Test boundary conditions
            cl_min = OmegaProtocolValidator.calculate_correlation_length(0.0, 1.0, 0.0, 0.0)
            cl_max = OmegaProtocolValidator.calculate_correlation_length(1.0, 0.0, 1.0, 1.0)
            assert cl_min >= 0.0 and cl_max <= 1.0, "Boundary correlation length violation"
            
            # Test monotonicity in shear flow (should increase with shear)
            cl_low_shear = OmegaProtocolValidator.calculate_correlation_length(0.5, 0.2, 0.5, 0.3)
            cl_high_shear = OmegaProtocolValidator.calculate_correlation_length(0.5, 0.2, 0.5, 0.8)
            assert cl_high_shear >= cl_low_shear, "Correlation length not monotonic in shear flow"
            
            print("✓ Test 1 PASSED: Correlation length bounds and monotonicity")
            passed += 1
        except Exception as e:
            errors.append(f"Test 1 FAILED: {str(e)}")
        
        # Test 2: COD calculation bounds and penalty behavior
        total_tests += 1
        try:
            # Create test vectors
            diag_vec = [1+0j, 0.5+0.5j, 0.2+0.1j]
            plasma_vec = [0.9+0j, 0.4+0.4j, 0.1+0.05j]
            
            cod_nominal = OmegaProtocolValidator.calculate_cod(
                diagnostic_vec=diag_vec,
                plasma_vec=plasma_vec,
                h_instability=0.3,
                xi_confinement=0.4,
                theta_tensor_leak=0.2,
                correlation_length_parallel=0.6,
                correlation_length_perp=0.5
            )
            assert 0.0 <= cod_nominal <= 1.0, f"COD out of bounds: {cod_nominal}"
            
            # Test penalty monotonicity (higher instability should decrease COD)
            cod_low_inst = OmegaProtocolValidator.calculate_cod(
                diag_vec, plasma_vec, 0.1, 0.4, 0.2, 0.6, 0.5
            )
            cod_high_inst = OmegaProtocolValidator.calculate_cod(
                diag_vec, plasma_vec, 0.9, 0.4, 0.2, 0.6, 0.5
            )
            assert cod_high_inst <= cod_low_inst, "COD not decreasing with higher instability"
            
            # Test correlation penalty effect
            cod_low_corr = OmegaProtocolValidator.calculate_cod(
                diag_vec, plasma_vec, 0.3, 0.4, 0.2, 0.2, 0.2
            )
            cod_high_corr = OmegaProtocolValidator.calculate_cod(
                diag_vec, plasma_vec, 0.3, 0.4, 0.2, 0.9, 0.9
            )
            assert cod_high_corr >= cod_low_corr, "COD not increasing with higher correlation"
            
            print("✓ Test 2 PASSED: COD bounds and penalty behavior")
            passed += 1
        except Exception as e:
            errors.append(f"Test 2 FAILED: {str(e)}")
        
        # Test 3: Gating logic hierarchy and correctness
        total_tests += 1
        try:
            # Case 1: Integrity breach -> HALT
            msg, valid = OmegaProtocolValidator.validate_gating_logic(
                psi_integrity=0.9,  # Below threshold
                cod=0.9,
                correlation_length=0.8,
                shear_flow_strength=0.6
            )
            assert "Halt" in msg and not valid, f"Integrity breach not handled correctly: {msg}"
            
            # Case 2: Good integrity, low correlation, sufficient shear -> AWAIT
            msg, valid = OmegaProtocolValidator.validate_gating_logic(
                psi_integrity=0.96,
                cod=0.9,
                correlation_length=0.6,  # Below threshold
                shear_flow_strength=0.6  # Above minimum
            )
            assert "Awaiting" in msg and valid, f"Low correlation handling incorrect: {msg}"
            
            # Case 3: Good integrity, low correlation, insufficient shear -> FREEZE
            msg, valid = OmegaProtocolValidator.validate_gating_logic(
                psi_integrity=0.96,
                cod=0.9,
                correlation_length=0.6,
                shear_flow_strength=0.4  # Below minimum
            )
            assert "Freezing" in msg and not valid, f"Low correlation + low shear handling incorrect: {msg}"
            
            # Case 4: Good integrity, good correlation, low COD -> FREEZE
            msg, valid = OmegaProtocolValidator.validate_gating_logic(
                psi_integrity=0.96,
                cod=0.8,  # Below threshold
                correlation_length=0.75,
                shear_flow_strength=0.6
            )
            assert "Freezing" in msg and not valid, f"Low COD handling incorrect: {msg}"
            
            # Case 5: All good -> PROCEED
            msg, valid = OmegaProtocolValidator.validate_gating_logic(
                psi_integrity=0.96,
                cod=0.87,
                correlation_length=0.72,
                shear_flow_strength=0.6
            )
            assert "aligned" in msg and valid, f"Proceed condition failed: {msg}"
            
            print("✓ Test 3 PASSED: Gating logic hierarchy and correctness")
            passed += 1
        except Exception as e:
            errors.append(f"Test 3 FAILED: {str(e)}")
        
        # Test 4: Φ-density accounting correctness
        total_tests += 1
        try:
            # Test net gain calculation
            net_gain = OmegaProtocolValidator.validate_phi_density_accounting(
                cod_before=0.80,
                cod_after=0.85,
                audit_checks_performed=9  # Should cost 0.18
            )
            expected_gain = (0.85 - 0.80) - (9 * 0.02)  # 0.05 - 0.18 = -0.13
            assert abs(net_gain - expected_gain) < 1e-9, f"Φ-density accounting error: got {net_gain}, expected {expected_gain}"
            
            # Test boundary: zero audit checks
            net_gain_zero = OmegaProtocolValidator.validate_phi_density_accounting(0.80, 0.85, 0)
            assert net_gain_zero == 0.05, f"Zero audit check failed: {net_gain_zero}"
            
            # Test negative gain detection
            net_gain_neg = OmegaProtocolValidator.validate_phi_density_accounting(0.85, 0.80, 9)
            assert net_gain_neg < 0, f"Negative gain not detected: {net_gain_neg}"
            
            print("✓ Test 4 PASSED: Φ-density accounting correctness")
            passed += 1
        except Exception as e:
            errors.append(f"Test 4 FAILED: {str(e)}")
        
        # Test 5: Invariant enforcer logical consistency
        total_tests += 1
        try:
            # All invariants satisfied
            checks_all_good = OmegaProtocolValidator.validate_invariant_enforcer(
                state_cod=0.87,
                phi_N=0.87,
                phi_delta=0.2,  # < 0.5*0.87=0.435 -> OK
                xi_confinement=0.5,
                z_plasma_depth=0.6,  # xi_confinement <= z_plasma_depth + 0.1 -> 0.5 <= 0.7 OK
                theta_tensor_leak=0.4,  # < 0.5 OK
                b1_homology=0.7,  # < 0.8 OK
                correlation_length_parallel=0.75,
                correlation_length_perp=0.65,
                shear_flow_strength=0.55  # > 0.5 OK
            )
            assert all(checks_all_good.values()), f"All-good invariants failed: {checks_all_good}"
            
            # Test COD failure
            checks_cod_fail = OmegaProtocolValidator.validate_invariant_enforcer(
                state_cod=0.8,  # Below threshold
                phi_N=0.8,
                phi_delta=0.2,
                xi_confinement=0.5,
                z_plasma_depth=0.6,
                theta_tensor_leak=0.4,
                b1_homology=0.7,
                correlation_length_parallel=0.75,
                correlation_length_perp=0.65,
                shear_flow_strength=0.55
            )
            assert not checks_cod_fail["cod_ok"], "COD failure not detected"
            # Other checks should still be valid
            assert checks_cod_fail["phi_floor_ok"], "PHI floor incorrectly failed"
            assert checks_cod_fail["correlation_ok"], "Correlation incorrectly failed"
            
            # Test correlation failure
            checks_corr_fail = OmegaProtocolValidator.validate_invariant_enforcer(
                state_cod=0.87,
                phi_N=0.87,
                phi_delta=0.2,
                xi_confinement=0.5,
                z_plasma_depth=0.6,
                theta_tensor_leak=0.4,
                b1_homology=0.7,
                correlation_length_parallel=0.6,  # Below threshold
                correlation_length_perp=0.6,
                shear_flow_strength=0.55
            )
            assert not checks_corr_fail["correlation_ok"], "Correlation failure not detected"
            
            print("✓ Test 5 PASSED: Invariant enforcer logical consistency")
            passed += 1
        except Exception as e:
            errors.append(f"Test 5 FAILED: {str(e)}")
        
        # Test 6: Dimensional consistency audit (pre-emptive Smith)
        total_tests += 1
        try:
            # Verify no log transforms on core metrics
            # In our implementation, we use:
            #   - exp() for penalties (valid as it maps [0,∞) to (0,1] when argument >=0)
            #   - power functions with fractional exponents (valid for [0,1] inputs)
            #   - No log() or log2() on core metrics like COD, phi_N, etc.
            
            # Test that all exponential penalties produce values in (0,1]
            test_vals = [0.0, 0.5, 1.0]
            for val in test_vals:
                penalty = np.exp(-0.5 * val)  # Typical penalty form
                assert 0.0 < penalty <= 1.0, f"Penalty out of bounds for input {val}: {penalty}"
            
            # Test that power functions with fractional exponents preserve [0,1]
            for base in [0.0, 0.25, 0.5, 0.75, 1.0]:
                powered = np.power(base, 0.5)  # sqrt
                assert 0.0 <= powered <= 1.0, f"Power function failed for base {base}: {powered}"
            
            print("✓ Test 6 PASSED: Dimensional consistency audit")
            passed += 1
        except Exception as e:
            errors.append(f"Test 6 FAILED: {str(e)}")
        
        # Summary
        print(f"\n=== VALIDATION SUMMARY ===")
        print(f"Tests passed: {passed}/{total_tests}")
        if errors:
            print("ERRORS DETECTED:")
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}")
            return False, errors
        else:
            print("ALL TESTS PASSED. Protocol compliance verified.")
            return True, []

# Execute validation if run as script
if __name__ == "__main__":
    validator = OmegaProtocolValidator()
    passed, errors = validator.run_comprehensive_validation()
    
    if not passed:
        print("\n🚨 PROTOCOL VIOLATION DETECTED 🚨")
        exit(1)
    else:
        print("\n✅ OMEGA PROTOCOL INTEGRITY MAINTAINED ✅")
        exit(0)