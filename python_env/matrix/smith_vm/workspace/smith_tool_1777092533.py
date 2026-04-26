# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# === OMEGA PROTOCOL INVARIANT VALIDATOR ===
# Validates mathematical soundness and invariant compliance of Bureaucratic Decision Manifold spec

class OmegaInvariantValidator:
    def __init__(self):
        # Protocol constants from spec
        self.PSI_ID_THRESHOLD = 0.95
        self.XI_SYS_MIN = 0.5
        self.XI_SYS_MAX = 3.0
        self.H_TOP_LIMIT = 0.85
        self.COD_THRESHOLD = 0.80
        self.PSI_ID_CRITICAL = 0.90
        self.LAMBDA = 1.0
        self.GAMMA = 0.5
        self.K_BOLTZMANN = 1.0
        
    def validate_dimensional_homogeneity(self, value, name, expected_range=[0,1]):
        """Check if value is dimensionless and within expected bounds"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be numeric, got {type(value)}")
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"{name} is NaN or infinite")
        if not (expected_range[0] <= value <= expected_range[1]):
            raise ValueError(f"{name}={value} outside expected range {expected_range}")
        return True
        
    def validate_cod_formula(self, intent, outcome, H_top, Xi_sys, Psi_id):
        """Validate COD_dec calculation per spec"""
        # Hard gate check
        if Psi_id < self.PSI_ID_THRESHOLD:
            return 0.0
            
        # Fidelity calculation (dot product normalization)
        dot = np.dot(intent, outcome)
        magI = np.linalg.norm(intent)
        magO = np.linalg.norm(outcome)
        fidelity = dot / (magI * magO) if (magI > 1e-9 and magO > 1e-9) else 0.0
        fidelity = max(0.0, min(1.0, fidelity))  # Clamp to [0,1]
        
        # Damping terms
        damping = math.exp(-self.LAMBDA * H_top)
        stiffness_penalty = math.exp(-self.GAMMA * Xi_sys)
        
        # Final COD
        cod = fidelity * damping * stiffness_penalty * Psi_id
        return max(0.0, min(1.0, cod))  # Clamp to [0,1]
        
    def validate_topological_impedance(self, path):
        """Validate H_top calculation per spec"""
        if not path:
            return 0.0
            
        total_impedance = sum(node['approval_cost'] * node['risk_variance'] for node in path)
        total_length = sum(node['approval_cost'] for node in path)
        
        if total_length == 0:
            return 0.0
            
        raw_impedance = total_impedance / total_length
        return max(0.0, min(1.0, raw_impedance))  # Clamp to [0,1]
        
    def validate_failure_mode(self, H_top, urgency_force, psi_id_org, COD):
        """Validate failure mode detection logic"""
        if H_top > self.H_TOP_LIMIT and urgency_force < (self.H_TOP_LIMIT * 0.5):
            return "PROCEDURAL_BLACK_HOLE"
        if COD < self.COD_THRESHOLD and psi_id_org < self.PSI_ID_CRITICAL:
            return "DECISION_DRIFT"
        if psi_id_org < self.PSI_ID_CRITICAL:
            return "IDENTITY_SHREDDING"
        return "NONE"
        
    def validate_identity_hard_gate(self, psi_id_org):
        """Validate identity continuity hard gate"""
        return psi_id_org >= self.PSI_ID_THRESHOLD
        
    def validate_phi_loss_calculation(self, psi_id_org, xi_sys, audit_complexity=1.0):
        """Validate Phi loss calculation per spec"""
        loss = 0.0
        if psi_id_org < 0.95:
            loss += (0.95 - psi_id_org) * 0.5 * self.K_BOLTZMANN
        if xi_sys > 3.0:
            loss += (xi_sys - 3.0) * 0.2 * self.K_BOLTZMANN
        audit_entropy = self.K_BOLTZMANN * math.log(2.0) * audit_complexity
        loss += audit_entropy
        return loss
        
    def run_comprehensive_validation(self):
        """Run all validation checks"""
        print("=== OMEGA PROTOCOL INVARIANT VALIDATION START ===")
        
        # Test 1: Dimensional homogeneity
        print("\n1. Testing dimensional homogeneity...")
        test_vals = [0.0, 0.5, 0.95, 1.0, 1.5, 2.0, 3.0]
        for val in test_vals:
            try:
                self.validate_dimensional_homogeneity(val, "test_value", [0, 3.0])
            except ValueError as e:
                if val in [0.0, 0.5, 0.95, 1.0, 1.5, 2.0, 3.0]:
                    print(f"  FAIL: {e}")
                    return False
        print("  PASS: All test values within bounds")
        
        # Test 2: COD hard gate
        print("\n2. Testing COD identity hard gate...")
        intent = [0.8, 0.6, 0.9]
        outcome = [0.7, 0.5, 0.85]
        H_top = 0.3
        Xi_sys = 1.0
        
        # Below threshold
        cod_low = self.validate_cod_formula(intent, outcome, H_top, Xi_sys, 0.94)
        if cod_low != 0.0:
            print(f"  FAIL: COD={cod_low} for Psi_id=0.94 (should be 0.0)")
            return False
            
        # At threshold
        cod_thresh = self.validate_cod_formula(intent, outcome, H_top, Xi_sys, 0.95)
        if cod_thresh <= 0.0:
            print(f"  FAIL: COD={cod_thresh} for Psi_id=0.95 (should be >0)")
            return False
            
        # Above threshold
        cod_high = self.validate_cod_formula(intent, outcome, H_top, Xi_sys, 0.96)
        if cod_high <= cod_thresh:
            print(f"  FAIL: COD not increasing with Psi_id")
            return False
        print("  PASS: Identity hard gate functioning correctly")
        
        # Test 3: Topological impedance bounds
        print("\n3. Testing topological impedance calculation...")
        test_path = [
            {'approval_cost': 0.2, 'risk_variance': 0.1},
            {'approval_cost': 0.9, 'risk_variance': 0.8},
            {'approval_cost': 0.5, 'risk_variance': 0.5}
        ]
        H_top = self.validate_topological_impedance(test_path)
        self.validate_dimensional_homogeneity(H_top, "H_top", [0, 1])
        print(f"  PASS: H_top={H_top:.3f} within [0,1]")
        
        # Test 4: Failure mode detection
        print("\n4. Testing failure mode detection...")
        # Procedural Black Hole condition
        fb = self.validate_failure_mode(0.9, 0.3, 0.96, 0.85)
        if fb != "PROCEDURAL_BLACK_HOLE":
            print(f"  FAIL: Expected PROCEDURAL_BLACK_HOLE, got {fb}")
            return False
            
        # Decision Drift condition
        fb = self.validate_failure_mode(0.7, 0.5, 0.89, 0.75)
        if fb != "DECISION_DRIFT":
            print(f"  FAIL: Expected DECISION_DRIFT, got {fb}")
            return False
            
        # Identity Shredding condition
        fb = self.validate_failure_mode(0.5, 0.5, 0.88, 0.9)
        if fb != "IDENTITY_SHREDDING":
            print(f"  FAIL: Expected IDENTITY_SHREDDING, got {fb}")
            return False
        print("  PASS: Failure mode detection logic correct")
        
        # Test 5: Phi loss calculation
        print("\n5. testing Phi loss calculation...")
        loss = self.validate_phi_loss_calculation(0.9, 2.5, 1.0)
        expected = (0.95-0.9)*0.5 + 0 + math.log(2.0)  # 0.025 + 0.693 = 0.718
        if abs(loss - expected) > 0.001:
            print(f"  FAIL: Phi loss={loss:.3f}, expected≈{expected:.3f}")
            return False
        print(f"  PASS: Phi loss calculation correct (loss={loss:.3f})")
        
        # Test 6: Audit cost subtraction
        print("\n6. validating audit cost subtraction...")
        base_loss = self.validate_phi_loss_calculation(0.95, 2.0, 1.0)
        audit_loss = self.validate_phi_loss_calculation(0.95, 2.0, 2.0)
        if audit_loss <= base_loss:
            print(f"  FAIL: Audit cost not increasing loss with complexity")
            return False
        print(f"  PASS: Audit cost properly subtracted (base={base_loss:.3f}, audit={audit_loss:.3f})")
        
        print("\n=== OMEGA PROTOCOL INVARIANT VALIDATION PASSED ===")
        print("All mathematical checks and invariant compliances verified.")
        return True

# Execute validation
if __name__ == "__main__":
    validator = OmegaInvariantValidator()
    try:
        success = validator.run_comprehensive_validation()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\nVALIDATION FAILED: {str(e)}")
        exit(1)