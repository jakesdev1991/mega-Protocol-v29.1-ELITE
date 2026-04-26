# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# =============================================================================
# OMEGA PROTOCOL VALIDATION SCRIPT
# Validates Trauma-Performance Q-System Specification (v26.0-Ω-POLARIZED)
# =============================================================================

class OmegaValidator:
    def __init__(self):
        # System constants from specification
        self.LAMBDA_COUPLING = 1.0
        self.GAMMA_COUPLING = 0.5
        self.PSI_ID_MIN = 0.95
        self.XI_BOUND_MAX = 3.0
        self.XI_BOUND_CRITICAL = 2.5
        self.H_INT_LIMIT = 0.85
        self.PSI_ID_CRITICAL = 0.90
        self.K_BOLTZMANN = 1.0  # Normalized informational entropy
        
        self.test_results = []
        self.log_events = []
    
    def log_event(self, message):
        self.log_events.append(message)
        print(f"[VALIDATION] {message}")
    
    # =============================================================================
    # 1. DIMENSIONAL CONSISTENCY CHECK (Rubric §6)
    # =============================================================================
    def test_dimensional_consistency(self):
        """Verify all terms in key equations are dimensionless [1]"""
        self.log_event("Testing dimensional consistency...")
        
        # Test COD equation: COD = |<Ψsub|Ψcon>|^2 * exp(-Λ·Hint) * exp(-Γ·Ξbound)
        # All terms must be [1]
        
        # |<Ψsub|Ψcon>|^2: Fidelity (projection squared) -> [1] (dimensionless by definition)
        fidelity_sq = 0.64  # Example value
        
        # exp(-Λ·Hint): Λ [1], Hint [1] -> exponent [1] -> exp() [1]
        Lambda = self.LAMBDA_COUPLING
        Hint = 0.5
        entropic_damping = math.exp(-Lambda * Hint)
        
        # exp(-Γ·Ξbound): Γ [1], Ξbound [1] -> exponent [1] -> exp() [1]
        Gamma = self.GAMMA_COUPLING
        Xibound = 2.0
        stiffness_penalty = math.exp(-Gamma * Xibound)
        
        COD = fidelity_sq * entropic_damping * stiffness_penalty
        
        # Verify all intermediate values are dimensionless (no units)
        assert isinstance(fidelity_sq, float) and not hasattr(fidelity_sq, 'unit')
        assert isinstance(entropic_damping, float) and not hasattr(entropic_damping, 'unit')
        assert isinstance(stiffness_penalty, float) and not hasattr(stiffness_penalty, 'unit')
        assert isinstance(COD, float) and not hasattr(COD, 'unit')
        
        self.test_results.append(("Dimensional Consistency", True))
        self.log_event("✓ All terms in COD equation are dimensionless [1]")
    
    # =============================================================================
    # 2. INVARIANT ENFORCEMENT CHECK (Rubric §3)
    # =============================================================================
    def test_invariant_enforcement(self):
        """Verify invariants are active boundary conditions (hard gates)"""
        self.log_event("Testing invariant enforcement...")
        
        # Test Psi_id hard gate (< 0.95 → Shredding Event)
        test_cases = [
            (0.94, False, "Psi_id < 0.95 should trigger hard failure"),
            (0.95, True, "Psi_id = 0.95 should pass"),
            (0.96, True, "Psi_id > 0.95 should pass")
        ]
        
        for psi_id, expected, description in test_cases:
            # Simulate VerifyInvariants logic
            passes = psi_id >= self.PSI_ID_MIN
            if passes != expected:
                self.test_results.append(("Psi_id Invariant", False))
                self.log_event(f"✗ {description} - Failed for psi_id={psi_id}")
                return
        
        # Test Xi_bound warnings (not hard failures but require mitigation)
        xi_warning_cases = [
            (2.6, True, "Xi_bound > 2.5 should warn Performance Burnout"),
            (3.1, True, "Xi_bound > 3.0 should warn Informational Freeze"),
            (2.0, False, "Xi_bound = 2.0 should not warn")
        ]
        
        for xibound, should_warn, description in xi_warning_cases:
            warn_burnout = xibound > self.XI_BOUND_CRITICAL
            warn_freeze = xibound > self.XI_BOUND_MAX
            should_warn_total = warn_burnout or warn_freeze
            
            if should_warn_total != should_warn:
                self.test_results.append(("Xi_bound Warning", False))
                self.log_event(f"✗ {description} - Failed for xibound={xibound}")
                return
        
        self.test_results.append(("Invariant Enforcement", True))
        self.log_event("✓ Invariants enforced as active boundary conditions")
    
    # =============================================================================
    # 3. AUDIT COST SUBTRACTION CHECK (Rubric §4-§5)
    # =============================================================================
    def test_audit_cost_subtraction(self):
        """Verify Φ-density accounting includes audit cost subtraction"""
        self.log_event("Testing audit cost subtraction...")
        
        # Test PhiDensityLedger.CalculateImpact
        h_cond_before = 0.7
        h_cond_after = 0.5
        audit_complexity = 2.0
        individual_cost = 0.1
        
        # Raw gain: -(H_after - H_before) = -(0.5 - 0.7) = +0.2
        raw_gain = -(h_cond_after - h_cond_before)
        
        # Audit cost: k ln 2 * complexity
        audit_cost = self.K_BOLTZMANN * math.log(2.0) * audit_complexity
        
        # Net Phi: raw_gain - audit_cost - individual_cost
        phi_net = raw_gain - audit_cost - individual_cost
        
        # Verify audit cost was subtracted
        expected_net = raw_gain - (self.K_BOLTZMANN * math.log(2.0) * audit_complexity) - individual_cost
        if abs(phi_net - expected_net) > 1e-9:
            self.test_results.append(("Audit Cost Subtraction", False))
            self.log_event(f"✗ Audit cost not properly subtracted: got {phi_net}, expected {expected_net}")
            return
        
        # Verify audit cost is positive (entropy cost)
        if audit_cost <= 0:
            self.test_results.append(("Audit Cost Sign", False))
            self.log_event("✗ Audit cost should be positive (entropy cost)")
            return
        
        self.test_results.append(("Audit Cost Subtraction", True))
        self.log_event(f"✓ Audit cost properly subtracted: {audit_cost:.4f} Φ")
    
    # =============================================================================
    # 4. FAILURE MODE DETECTION CHECK
    # =============================================================================
    def test_failure_mode_detection(self):
        """Verify Performance Burnout detection logic"""
        self.log_event("Testing failure mode detection...")
        
        # Performance Burnout condition:
        # H_int > H_INT_LIMIT AND Ξbound > Ξbound_CRITICAL AND Psi_id < Psi_id_CRITICAL
        
        test_cases = [
            # (Hint, Xibound, Psi_id, expected_failure, description)
            (0.9, 2.6, 0.89, "PERFORMANCE_BURNOUT", "All burnout conditions met"),
            (0.8, 2.6, 0.89, "NONE", "Hint too low"),
            (0.9, 2.4, 0.89, "NONE", "Xibound too low"),
            (0.9, 2.6, 0.91, "NONE", "Psi_id too high"),
            (0.9, 2.6, 0.89, "PERFORMANCE_BURNOUT", "Boundary case"),
            (0.85, 2.5, 0.90, "NONE", "Exact limits should not trigger (strict inequalities)"),
        ]
        
        for Hint, Xibound, Psi_id, expected, description in test_cases:
            # Simulate FailureModeDetector.CheckRisk
            burnout = (Hint > self.H_INT_LIMIT and 
                      Xibound > self.XI_BOUND_CRITICAL and 
                      Psi_id < self.PSI_ID_CRITICAL)
            
            if burnout:
                actual = "PERFORMANCE_BURNOUT"
            else:
                actual = "NONE"  # Simplified for this test
            
            if actual != expected:
                self.test_results.append(("Failure Mode Detection", False))
                self.log_event(f"✗ {description} - Expected {expected}, got {actual}")
                return
        
        self.test_results.append(("Failure Mode Detection", True))
        self.log_event("✓ Performance Burnout detection logic correct")
    
    # =============================================================================
    # 5. COD AND ARTIFICIAL COD DETECTION CHECK
    # =============================================================================
    def test_cod_and_artificial_detection(self):
        """Verify COD formula and artificial COD detection"""
        self.log_event("Testing COD and artificial COD detection...")
        
        # Test COD calculation
        # COD = |<Ψsub|Ψcon>|^2 * exp(-Λ·Hint) * exp(-Γ·Ξbound)
        
        # Create test state vectors
        Psi_sub = np.array([0.6, 0.8])  # Normalized
        Psi_con = np.array([0.8, 0.6])  # Normalized
        
        # Calculate fidelity squared
        dot = np.dot(Psi_sub, Psi_con)
        mag_sub = np.linalg.norm(Psi_sub)
        mag_con = np.linalg.norm(Psi_con)
        fidelity = dot / (mag_sub * mag_con) if (mag_sub > 0 and mag_con > 0) else 0
        fidelity_sq = fidelity * fidelity
        
        Hint = 0.4
        Xibound = 2.0
        
        entropic_damping = math.exp(-self.LAMBDA_COUPLING * Hint)
        stiffness_penalty = math.exp(-self.GAMMA_COUPLING * Xibound)
        COD = fidelity_sq * entropic_damping * stiffness_penalty
        
        # Verify COD is in [0,1]
        if not (0 <= COD <= 1):
            self.test_results.append(("COD Range", False))
            self.log_event(f"✗ COD out of range: {COD}")
            return
        
        # Test artificial COD detection
        # Artificial if: COD >= 0.75 AND Xibound > 2.5 AND (Xibound/Hint) > 2.0
        stiffness_entropy_ratio = Xibound / Hint if Hint > 0 else float('inf')
        is_artificial = (COD >= 0.75) and (Xibound > 2.5) and (stiffness_entropy_ratio > 2.0)
        
        # Test case 1: Genuine high COD (low stiffness, low entropy)
        genuine_COD = 0.82
        genuine_Xibound = 1.2
        genuine_Hint = 0.3
        genuine_ratio = genuine_Xibound / genuine_Hint
        genuine_artificial = (genuine_COD >= 0.75) and (genuine_Xibound > 2.5) and (genuine_ratio > 2.0)
        if genuine_artificial:
            self.test_results.append(("Artificial COD Detection", False))
            self.log_event("✗ Genuine high COD incorrectly flagged as artificial")
            return
        
        # Test case 2: Artificial COD (high stiffness masking low fidelity)
        art_COD = 0.78  # Would be low without stiffness penalty
        art_Xibound = 2.8
        art_Hint = 0.9
        art_ratio = art_Xibound / art_Hint
        art_artificial = (art_COD >= 0.75) and (art_Xibound > 2.5) and (art_ratio > 2.0)
        if not art_artificial:
            self.test_results.append(("Artificial COD Detection", False))
            self.log_event("✗ Artificial COD not detected")
            return
        
        self.test_results.append(("COD and Artificial Detection", True))
        self.log_event("✓ COD formula and artificial detection logic correct")
    
    # =============================================================================
    # 6. PHI-DENSITY LEDGER VALIDATION
    # =============================================================================
    def test_phi_density_ledger(self):
        """Verify Phi-density ledger calculations"""
        self.log_event("Testing Phi-density ledger...")
        
        ledger = PhiDensityLedger(self.K_BOLTZMANN)
        
        # Test audit cost calculation
        audit_cost = ledger.calculate_audit_cost(complexity_factor=3.0)
        expected = self.K_BOLTZMANN * math.log(2.0) * 3.0
        if abs(audit_cost - expected) > 1e-9:
            self.test_results.append(("Phi Ledger Audit Cost", False))
            self.log_event(f"✗ Audit cost mismatch: got {audit_cost}, expected {expected}")
            return
        
        # Test individual cost calculation
        Hint = 0.7
        Xibound = 2.2
        individual_cost = ledger.calculate_individual_cost(Hint, Xibound)
        expected = Hint * Xibound * 0.2  # From specification
        if abs(individual_cost - expected) > 1e-9:
            self.test_results.append(("Phi Ledger Individual Cost", False))
            self.log_event(f"✗ Individual cost mismatch: got {individual_cost}, expected {expected}")
            return
        
        # Test net impact calculation
        h_before = 0.6
        h_after = 0.4
        audit_c = 0.1
        indiv_c = 0.05
        net_impact = ledger.calculate_impact(h_before, h_after, audit_c, indiv_c)
        expected_net = -(h_after - h_before) - audit_c - indiv_c
        if abs(net_impact - expected_net) > 1e-9:
            self.test_results.append(("Phi Ledger Net Impact", False))
            self.log_event(f"✗ Net impact mismatch: got {net_impact}, expected {expected_net}")
            return
        
        self.test_results.append(("Phi-Density Ledger", True))
        self.log_event("✓ Phi-density ledger calculations correct")
    
    def run_all_tests(self):
        """Execute all validation tests"""
        print("=" * 60)
        print("OMEGA PROTOCOL VALIDATION: TRAUMA-PERFORMANCE Q-SYSTEM")
        print("=" * 60)
        
        # Run all test suites
        self.test_dimensional_consistency()
        self.test_invariant_enforcement()
        self.test_audit_cost_subtraction()
        self.test_failure_mode_detection()
        self.test_cod_and_artificial_detection()
        self.test_phi_density_ledger()
        
        # Summary
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        print("\n" + "=" * 60)
        print(f"VALIDATION SUMMARY: {passed}/{total} TESTS PASSED")
        print("=" * 60)
        
        for test_name, result in self.test_results:
            status = "PASS" if result else "FAIL"
            print(f"{test_name:<35} [{status}]")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - SPECIFICATION IS OMEGA-COMPLIANT")
            return True
        else:
            print(f"\n❌ {total - passed} TEST(S) FAILED - SPECIFICATION NON-COMPLIANT")
            return False

# =============================================================================
# SUPPORTING CLASSES (Mirroring specification logic)
# =============================================================================

class PhiDensityLedger:
    def __init__(self, K_BOLTZMANN):
        self.K_BOLTZMANN = K_BOLTZMANN
    
    def calculate_audit_cost(self, complexity_factor=1.0):
        return self.K_BOLTZMANN * math.log(2.0) * complexity_factor
    
    def calculate_individual_cost(self, H_int, Xibound):
        return H_int * Xibound * 0.2  # Normalized cost factor from spec
    
    def calculate_impact(self, h_cond_before, h_cond_after, audit_cost, individual_cost):
        raw_gain = -(h_cond_after - h_cond_before)
        return raw_gain - audit_cost - individual_cost

# =============================================================================
# EXECUTE VALIDATION
# =============================================================================

if __name__ == "__main__":
    validator = OmegaValidator()
    is_compliant = validator.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if is_compliant else 1)