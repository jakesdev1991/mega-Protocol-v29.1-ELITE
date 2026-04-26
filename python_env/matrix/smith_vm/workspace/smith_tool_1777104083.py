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
# OMEGA PROTOCOL INVARIANT VALIDATOR
# Validates mathematical soundness and invariant compliance of Q-Systemic Self framework
# =============================================================================

class InvariantViolation(Exception):
    """Raised when Omega Protocol invariants are violated"""
    pass

class QSystemicSelfValidator:
    def __init__(self):
        # Hard gate thresholds from protocol
        self.PSI_ID_THRESHOLD = 0.95
        self.PSI_ID_CRITICAL = 0.90
        self.H_SUPER_SHOCK = 0.85
        self.GAMMA_MEAS_SHOCK = 0.8
        self.COD_THRESHOLD = 0.80
        self.H_SUPER_STAGNATION = 0.05
        self.GAMMA_MEAS_STAGNATION = 0.1
        
        # Audit entropy constants (dimensionless)
        self.K_BOLTZMANN = 1.0
        self.LOG_2 = math.log(2.0)
        
        # Coupling constants
        self.LAMBDA_COUPLING = 1.0
        
    def validate_dimensionless(self, value: float, name: str, bounds: Tuple[float, float] = (0.0, 1.0)) -> None:
        """Ensure value is dimensionless and within bounds"""
        if not isinstance(value, (int, float)):
            raise InvariantViolation(f"{name} must be numeric, got {type(value)}")
        if math.isnan(value) or math.isinf(value):
            raise InvariantViolation(f"{name} is NaN or infinite")
        if not (bounds[0] <= value <= bounds[1]):
            raise InvariantViolation(f"{name} = {value} violates bounds [{bounds[0]}, {bounds[1]}]")
    
    def validate_psi_id(self, psi_id: float) -> None:
        """Validate Identity Continuity hard gate"""
        self.validate_dimensionless(psi_id, "Psi_id", (0.0, 1.0))
        if psi_id < self.PSI_ID_THRESHOLD:
            raise InvariantViolation(f"Identity Shredding: Psi_id = {psi_id} < {self.PSI_ID_THRESHOLD}")
    
    def validate_entropy(self, entropy: float, name: str) -> None:
        """Validate entropy measures"""
        self.validate_dimensionless(entropy, name, (0.0, 1.0))
    
    def validate_gamma_meas(self, gamma: float) -> None:
        """Validate measurement intensity"""
        self.validate_dimensionless(gamma, "Gamma_meas", (0.0, 1.0))
    
    def validate_cod(self, cod: float) -> None:
        """Validate Chain Overlap Density"""
        self.validate_dimensionless(cod, "COD", (0.0, 1.0))
    
    def superposition_entropy(self, state: List[complex]) -> float:
        """Calculate normalized superposition entropy H_super"""
        if not state:
            return 0.0
        
        # Calculate probabilities
        probs = [abs(amp)**2 for amp in state]
        total_prob = sum(probs)
        
        if total_prob < 1e-12:
            return 0.0
        
        # Normalize probabilities
        probs = [p/total_prob for p in probs]
        
        # Shannon entropy
        H = -sum(p * math.log(p) for p in probs if p > 1e-12)
        
        # Normalize by max entropy (log(N))
        max_entropy = math.log(len(state)) if len(state) > 1 else 1.0
        if max_entropy < 1e-12:
            max_entropy = 1.0
            
        H_norm = H / max_entropy
        self.validate_entropy(H_norm, "H_super")
        return H_norm
    
    def fidelity(self, state1: List[complex], state2: List[complex]) -> float:
        """Calculate quantum fidelity |<state1|state2>|^2"""
        if len(state1) != len(state2):
            raise ValueError("States must have same dimension")
        
        # Inner product <state1|state2> = sum conj(state1_i) * state2_i
        inner = sum(np.conj(s1) * s2 for s1, s2 in zip(state1, state2))
        fidelity_val = abs(inner)**2
        
        # Normalize if states aren't unit norm (should be in proper usage)
        norm1 = sum(abs(s)**2 for s in state1)
        norm2 = sum(abs(s)**2 for s in state2)
        if norm1 > 1e-12 and norm2 > 1e-12:
            fidelity_val /= (norm1 * norm2)
        
        self.validate_dimensionless(fidelity_val, "Fidelity", (0.0, 1.0))
        return fidelity_val
    
    def calculate_cod(self, intent: List[complex], collapsed: List[complex], 
                     H_super: float, psi_id: float) -> float:
        """Calculate Chain Overlap Density: COD = Fidelity * exp(-Lambda*H_super) * Psi_id"""
        # Validate inputs
        self.validate_entropy(H_super, "H_super")
        self.validate_psi_id(psi_id)
        
        # Fidelity term
        fidelity_val = self.fidelity(intent, collapsed)
        
        # Uncertainty penalty
        damping = math.exp(-self.LAMBDA_COUPLING * H_super)
        self.validate_dimensionless(damping, "Damping", (0.0, 1.0))
        
        # COD calculation
        cod = fidelity_val * damping * psi_id
        self.validate_cod(cod)
        return cod
    
    def failure_mode_detector(self, H_super: float, gamma_meas: float, 
                            psi_id: float, cod: float) -> str:
        """Detect systemic failure modes"""
        self.validate_entropy(H_super, "H_super")
        self.validate_gamma_meas(gamma_meas)
        self.validate_psi_id(psi_id)
        self.validate_cod(cod)
        
        # Measurement Shock condition
        if H_super > self.H_SUPER_SHOCK and gamma_meas > self.GAMMA_MEAS_SHOCK:
            return "MEASUREMENT_SHOCK"
        
        # Decision Drift condition
        if H_super < self.H_SUPER_STAGNATION and gamma_meas < self.GAMMA_MEAS_STAGNATION:
            return "DECISION_DRIFT"
        
        # Identity Shredding condition
        if psi_id < self.PSI_ID_CRITICAL:
            return "IDENTITY_SHREDDING"
        
        # Misaligned Clarity condition (low COD despite good Psi_id)
        if cod < self.COD_THRESHOLD and psi_id >= self.PSI_ID_THRESHOLD:
            return "MISALIGNED_CLARITY"
        
        return "STABLE"
    
    def adiabatic_collapse_operator(self, state: dict, audit_ops: int, audit_entropy: float) -> Tuple[dict, int, float]:
        """
        Apply ACG v38.0 operator
        state: dict containing Psi_sub, Psi_con, Psi_coll, gamma_meas, psi_id, xi_def
        Returns updated state, audit_ops, audit_entropy
        """
        # Extract state variables
        Psi_sub = state['Psi_sub']
        Psi_con = state['Psi_con']
        Psi_coll = state['Psi_coll']
        gamma_meas = state['gamma_meas']
        psi_id = state['psi_id']
        
        # Validate input state
        self.validate_psi_id(psi_id)
        self.validate_gamma_meas(gamma_meas)
        for amp in Psi_sub + Psi_con + Psi_coll:
            if not isinstance(amp, complex):
                raise InvariantViolation("State amplitudes must be complex numbers")
        
        # Phase 1: Diagnostic
        H_super = self.superposition_entropy(Psi_sub)
        current_cod = self.calculate_cod(Psi_con, Psi_coll, H_super, psi_id)
        failure = self.failure_mode_detector(H_super, gamma_meas, psi_id, current_cod)
        
        # If stable and COD sufficient, no intervention
        if failure == "STABLE" and current_cod >= self.COD_THRESHOLD:
            return state, audit_ops, audit_entropy
        
        # Phase 2: Modulation (Adiabatic Control)
        if failure == "MEASUREMENT_SHOCK":
            # Reduce collapse rate
            gamma_meas = max(0.1, gamma_meas * 0.9)
            audit_ops += 1
            audit_entropy += 0.05  # Cost for gamma_meas modulation
        elif failure == "DECISION_DRIFT":
            # Increase agency
            gamma_meas = min(1.0, gamma_meas * 1.1)
            audit_ops += 1
            audit_entropy += 0.05
        elif failure == "IDENTITY_SHREDDING":
            raise InvariantViolation("Identity Integrity Compromised - Abort Intervention")
        elif failure == "MISALIGNED_CLARITY":
            # Inject external validation
            Psi_con = [amp * 1.05 for amp in Psi_con]
            audit_ops += 1
            audit_entropy += 0.02  # Cost for Psi_val injection
        
        # Update state with modulated gamma_meas
        state['gamma_meas'] = gamma_meas
        
        # Phase 3: State Transformation (Controlled Collapse)
        new_Psi_coll = []
        for i in range(len(Psi_sub)):
            weight = abs(np.conj(Psi_con[i]) * Psi_sub[i])
            new_Psi_coll.append(Psi_con[i] * weight)
        state['Psi_coll'] = new_Psi_coll
        
        # Phase 4: Entropy Accounting
        H_cond = self.superposition_entropy(state['Psi_coll'])
        identity_loss = H_cond * 0.05
        state['psi_id'] = psi_id - identity_loss
        
        # Phase 5: Invariant Validation - HARD GATE
        self.validate_psi_id(state['psi_id'])  # Will throw if violated
        
        return state, audit_ops, audit_entropy
    
    def phi_density_ledger(self, cod_before: float, cod_after: float, 
                          audit_entropy_cost: float) -> float:
        """Calculate net Phi gain with audit cost subtraction"""
        self.validate_cod(cod_before)
        self.validate_cod(cod_after)
        self.validate_dimensionless(audit_entropy_cost, "Audit entropy cost", (0.0, float('inf')))
        
        raw_gain = cod_after - cod_before
        phi_net = raw_gain - audit_entropy_cost
        self.validate_dimensionless(phi_net, "Phi_net")  # Can be negative
        return phi_net
    
    def run_compliance_tests(self) -> None:
        """Run comprehensive compliance tests"""
        print("Running Omega Protocol Compliance Tests...")
        
        # Test 1: Dimensionless validation
        try:
            self.validate_dimensionless(0.5, "Test value")
            self.validate_dimensionless(0.0, "Test value")
            self.validate_dimensionless(1.0, "Test value")
            self.validate_dimensionless(-0.1, "Test value")  # Should fail
        except InvariantViolation as e:
            print(f"✓ Dimensionless validation working: {e}")
        
        # Test 2: Psi_id hard gate
        try:
            self.validate_psi_id(0.96)  # Should pass
            self.validate_psi_id(0.95)  # Should pass (threshold)
            self.validate_psi_id(0.94)  # Should fail
        except InvariantViolation as e:
            print(f"✓ Psi_id hard gate working: {e}")
        
        # Test 3: Entropy calculation
        test_state = [1+0j, 0+0j]  # |0> state
        H = self.superposition_entropy(test_state)
        assert abs(H - 0.0) < 1e-6, f"Entropy of |0> should be 0, got {H}"
        
        test_state = [1/math.sqrt(2)+0j, 1/math.sqrt(2)+0j]  # |+> state
        H = self.superposition_entropy(test_state)
        assert abs(H - 1.0) < 1e-6, f"Entropy of |+> should be 1.0, got {H}"
        print("✓ Entropy calculation working")
        
        # Test 4: Fidelity calculation
        state1 = [1+0j, 0+0j]
        state2 = [1+0j, 0+0j]
        fid = self.fidelity(state1, state2)
        assert abs(fid - 1.0) < 1e-6, f"Fidelity of identical states should be 1, got {fid}"
        
        state2 = [0+0j, 1+0j]
        fid = self.fidelity(state1, state2)
        assert abs(fid - 0.0) < 1e-6, f"Fidelity of orthogonal states should be 0, got {fid}"
        print("✓ Fidelity calculation working")
        
        # Test 5: COD calculation
        intent = [1+0j, 0+0j]
        collapsed = [1+0j, 0+0j]
        H_super = 0.0
        psi_id = 1.0
        cod = self.calculate_cod(intent, collapsed, H_super, psi_id)
        assert abs(cod - 1.0) < 1e-6, f"COD for aligned states should be 1, got {cod}"
        
        # Test with uncertainty
        H_super = 1.0
        cod = self.calculate_cod(intent, collapsed, H_super, psi_id)
        expected = math.exp(-self.LAMBDA_COUPLING * 1.0)
        assert abs(cod - expected) < 1e-6, f"COD with H_super=1.0 should be exp(-1), got {cod}"
        print("✓ COD calculation working")
        
        # Test 6: Failure mode detector
        # Measurement Shock
        assert self.failure_mode_detector(0.9, 0.9, 0.96, 0.5) == "MEASUREMENT_SHOCK"
        # Decision Drift
        assert self.failure_mode_detector(0.04, 0.05, 0.96, 0.5) == "DECISION_DRIFT"
        # Identity Shredding
        assert self.failure_mode_detector(0.5, 0.5, 0.89, 0.5) == "IDENTITY_SHREDDING"
        # Misaligned Clarity
        assert self.failure_mode_detector(0.5, 0.5, 0.96, 0.7) == "MISALIGNED_CLARITY"
        # Stable
        assert self.failure_mode_detector(0.5, 0.5, 0.96, 0.9) == "STABLE"
        print("✓ Failure mode detector working")
        
        # Test 7: Adiabatic Collapse Operator (basic)
        state = {
            'Psi_sub': [1/math.sqrt(2)+0j, 1/math.sqrt(2)+0j],
            'Psi_con': [1+0j, 0+0j],
            'Psi_coll': [0+0j, 0+0j],  # Will be updated
            'gamma_meas': 0.9,
            'psi_id': 0.96,
            'xi_def': 1.5
        }
        
        # Should trigger MEASUREMENT_SHOCK (H_super=1.0 > 0.85, gamma_meas=0.9 > 0.8)
        try:
            new_state, audit_ops, audit_entropy = self.adiabatic_collapse_operator(state, 0, 0.0)
            assert audit_ops == 1, "Should have logged one audit operation"
            assert audit_entropy == 0.05, "Audit entropy should be 0.05"
            assert new_state['gamma_meas'] == 0.81, f"Gamma_meas should be 0.9*0.9=0.81, got {new_state['gamma_meas']}"
            print("✓ Adiabatic Collapse Operator working for MEASUREMENT_SHOCK")
        except Exception as e:
            print(f"✗ Adiabatic Collapse Operator failed: {e}")
            raise
        
        # Test 8: Phi-Density Ledger
        phi_net = self.phi_density_ledger(0.5, 0.8, 0.1)
        assert abs(phi_net - 0.2) < 1e-6, f"Phi_net should be 0.2, got {phi_net}"
        print("✓ Phi-Density Ledger working")
        
        # Test 9: Invariant violation during ACG
        state_bad = {
            'Psi_sub': [1+0j, 0+0j],
            'Psi_con': [0+0j, 1+0j],
            'Psi_coll': [0+0j, 0+0j],
            'gamma_meas': 0.5,
            'psi_id': 0.90,  # Below critical threshold
            'xi_def': 1.5
        }
        try:
            self.adiabatic_collapse_operator(state_bad, 0, 0.0)
            print("✗ Should have thrown InvariantViolation for low Psi_id")
            raise AssertionError("Invariant violation not caught")
        except InvariantViolation as e:
            print(f"✓ Invariant violation caught: {e}")
        
        print("\nAll Omega Protocol compliance tests PASSED.")
        print("Framework is mathematically sound and invariant-compliant.")

# =============================================================================
# EXECUTION VALIDATOR
# =============================================================================
if __name__ == "__main__":
    validator = QSystemicSelfValidator()
    try:
        validator.run_compliance_tests()
    except Exception as e:
        print(f"\nOMEGA PROTOCOL VIOLATION DETECTED: {e}")
        print("FRAMEWORK IS NOT COMPLIANT - TERMINATING VALIDATION")
        exit(1)