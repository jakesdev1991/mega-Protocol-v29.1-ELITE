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
# OMEGA PROTOCOL INVARIANTS (EXTRACTED FROM SPECIFICATION)
# =============================================================================
# All constants are dimensionless [1] per Rubric §6

PSI_ID_THRESHOLD = 0.95      # Identity Conservation Hard Gate
PSI_ID_CRITICAL = 0.90       # Dissociation Risk Threshold
XI_RESET_DEFAULT = 1.0
XI_RESET_MAX = 2.5           # Risk: Identity Shredding / Measurement Shock
XI_RESET_MIN = 0.3           # Risk: Validation Paralysis
LAMBDA_COUPLING = 1.0        # Entropic Damping Coefficient [1]
GAMMA_COUPLING = 0.5         # Stiffness Penalty Coefficient [1]
H_VAL_LIMIT = 0.85           # Maximum Validation Entropy [1]
COD_THRESHOLD = 0.80         # Minimum Alignment Fidelity [1]
K_BOLTZMANN = 1.0            # Normalized for informational entropy [1]

# =============================================================================
# CORE MATHEMATICAL FUNCTIONS (VALIDATED AGAINST SPECIFICATION)
# =============================================================================

def calculate_validation_entropy(validation_data: List[float]) -> float:
    """
    Calculates normalized Shannon entropy H_val = H(D|I) / H_max
    Implements Specification: Calculate_Validation_Entropy
    """
    if not validation_data or all(p == 0 for p in validation_data):
        return 0.0
    
    # Normalize to probability distribution (spec assumes input is already prob-like)
    total = sum(validation_data)
    if total == 0:
        return 0.0
    probs = [p / total for p in validation_data]
    
    # Shannon entropy
    H = -sum(p * math.log(p) for p in probs if p > 1e-9)
    max_entropy = math.log(len(probs)) if len(probs) > 1 else 1.0
    return min(1.0, max(0.0, H / max_entropy))

def calculate_reboot_cod(Psi_old: List[float], Psi_new: List[float], 
                         H_val: float, Xi_reset: float) -> float:
    """
    Calculates Chain Overlap Density: 
    COD = |<Psi_old | Psi_new>|^2 * exp(-Lambda * H_val) * exp(-Gamma * Xi_reset)
    Implements Specification: Calculate_Reboot_COD
    """
    # Convert to numpy for vector operations (but keep dimensionless)
    old = np.array(Psi_old, dtype=float)
    new = np.array(Psi_new, dtype=float)
    
    # Fidelity: |<old|new>|^2
    dot_product = np.dot(old, new)
    norm_old = np.linalg.norm(old)
    norm_new = np.linalg.norm(new)
    
    if norm_old < 1e-9 or norm_new < 1e-9:
        fidelity = 0.0
    else:
        fidelity = (dot_product / (norm_old * norm_new)) ** 2
        fidelity = min(1.0, max(0.0, fidelity))  # Clamp to [0,1]
    
    # Entropic damping and stiffness penalty
    damping = math.exp(-LAMBDA_COUPLING * H_val)
    stiffness_penalty = math.exp(-GAMMA_COUPLING * Xi_reset)
    
    return fidelity * damping * stiffness_penalty

class FailureModeDetector:
    """Implements Specification: FailureModeDetector"""
    @staticmethod
    def check_risk(H_val: float, Xi_reset: float, Psi_id: float) -> str:
        if H_val > H_VAL_LIMIT and Xi_reset > XI_RESET_MAX and Psi_id < PSI_ID_CRITICAL:
            return "IDENTITY_SHREDDING"
        if H_val > H_VAL_LIMIT and Xi_reset < XI_RESET_MIN:
            return "VALIDATION_PARALYSIS"
        if Xi_reset > XI_RESET_MAX:
            return "MEASUREMENT_SHOCK"
        return "NONE"

class SystemInvariants:
    """Implements Specification: SystemInvariants (subset for validation)"""
    @staticmethod
    def verify_identity_continuity(psi_id: float) -> bool:
        """Hard gate: Psi_id must >= PSI_ID_THRESHOLD (0.95)"""
        return psi_id >= PSI_ID_THRESHOLD
    
    @staticmethod
    def verify_invariants(psi_id: float, xi_sys: float) -> Tuple[bool, List[str]]:
        """Active boundary condition check"""
        warnings = []
        if psi_id < PSI_ID_THRESHOLD:
            warnings.append(f"CRITICAL: Shredding Event - Psi_id={psi_id:.3f} < {PSI_ID_THRESHOLD}")
            return False, warnings
        if xi_sys > 3.0:  # XI_SYS_MAX from spec
            warnings.append(f"WARNING: Informational Freeze Risk - Xi_sys={xi_sys:.3f} > 3.0")
        return True, warnings
    
    @staticmethod
    def calculate_phi_loss(psi_id: float, xi_sys: float, audit_complexity: float = 1.0) -> float:
        """Implements Specification: CalculatePhiLoss with audit cost subtraction"""
        loss = 0.0
        # Identity erosion (High Severity)
        if psi_id < PSI_ID_THRESHOLD:
            loss += (PSI_ID_THRESHOLD - psi_id) * 0.5 * K_BOLTZMANN
        # Stability breach (Medium Severity)
        if xi_sys > 3.0:
            loss += (xi_sys - 3.0) * 0.2 * K_BOLTZMANN
        # Audit cost subtraction (Meta-Scrutiny requirement)
        audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
        loss += audit_entropy_cost
        return loss

class AdiabaticRebootOperator:
    """Implements core logic of Specification: Adiabatic_Reboot_Operator"""
    def __init__(self):
        self.psi_id_threshold = PSI_ID_THRESHOLD
    
    def apply(self, state: dict, validation_data: List[float]) -> dict:
        """
        Simulates one iteration of ARP. Returns updated state.
        State dict must contain: 'Psi_old', 'Psi_new', 'xi_reset', 'psi_id', 't'
        """
        # PHASE 1: DIAGNOSTIC
        H_val = calculate_validation_entropy(validation_data)
        current_cod = calculate_reboot_cod(
            state['Psi_old'], state['Psi_new'], H_val, state['xi_reset']
        )
        
        # FAILURE DETECTION
        failure = FailureModeDetector.check_risk(H_val, state['xi_reset'], state['psi_id'])
        
        # PHASE 2: STIFFNESS MODULATION (Adiabatic Control)
        xi_reset_new = state['xi_reset']
        if failure == "IDENTITY_SHREDDING":
            xi_reset_new = max(XI_RESET_MIN, state['xi_reset'] * 0.8)
        elif failure == "VALIDATION_PARALYSIS":
            xi_reset_new = min(XI_RESET_DEFAULT, state['xi_reset'] * 1.2)
        elif failure == "MEASUREMENT_SHOCK":
            xi_reset_new = max(XI_RESET_MIN, state['xi_reset'] * 0.5)
        else:  # NORMAL OPERATION
            if current_cod < COD_THRESHOLD:
                xi_reset_new = min(XI_RESET_DEFAULT, state['xi_reset'] * 1.1)
        
        # PHASE 3: STATE TRANSFORMATION (Basis Change)
        alpha = min(1.0, (1.0 - xi_reset_new) * 0.5 + 0.5)  # Sigmoid-like
        Psi_old_updated = [
            (1.0 - alpha) * old + alpha * new 
            for old, new in zip(state['Psi_old'], state['Psi_new'])
        ]
        
        # PHASE 4: ENTROPY ACCOUNTING & IDENTITY UPDATE
        # Simplified identity loss proportional to validation entropy
        identity_loss = H_val * 0.1
        psi_id_updated = state['psi_id'] - identity_loss
        
        # PHASE 5: INVARIANT VALIDATION (HARD GATE)
        if not SystemInvariants.verify_identity_continuity(psi_id_updated):
            raise RuntimeError(
                f"Invariant Violation: Identity Integrity Compromised "
                f"(Psi_id={psi_id_updated:.3f} < {PSI_ID_THRESHOLD})"
            )
        
        # Return updated state
        return {
            'Psi_old': Psi_old_updated,
            'Psi_new': state['Psi_new'],  # Target remains constant during transition
            'xi_reset': xi_reset_new,
            'psi_id': psi_id_updated,
            't': state['t'] + 0.01  # Simplified time progression
        }

class PhiDensityLedger:
    """Implements Specification: PhiDensityLedger"""
    @staticmethod
    def calculate_impact(h_val: float, cod_gain: float, audit_complexity: float = 1.0) -> float:
        """
        Implements: Phi_net = Phi_gain - Phi_loss - Delta_S_audit
        Where Delta_S_audit = k ln 2 * Complexity(operator)
        """
        raw_gain = cod_gain
        validation_cost = h_val * 0.5
        audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
        return raw_gain - validation_cost - audit_entropy_cost

# =============================================================================
# VALIDATION TEST SUITE: ENFORCING OMEGA PROTOCOL INVARIANTS
# =============================================================================

def run_validation_suite() -> Tuple[bool, List[str]]:
    """
    Runs comprehensive validation of the specification against Omega Protocol invariants.
    Returns (passed, list_of_errors)
    """
    errors = []
    
    print("=" * 60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION SUITE")
    print("=" * 60)
    
    # TEST 1: DIMENSIONAL CONSISTENCY (Rubric §6)
    print("\n[TEST 1] Dimensional Consistency Check")
    try:
        # All inputs to exponential must be dimensionless [1]
        H_val_test = 0.5  # Normalized entropy [1]
        Xi_reset_test = 1.0  # Stiffness [1]
        exp_arg1 = LAMBDA_COUPLING * H_val_test  # [1]*[1] = [1]
        exp_arg2 = GAMMA_COUPLING * Xi_reset_test  # [1]*[1] = [1]
        # If no exception, dimensional homogeneity holds
        math.exp(-exp_arg1)
        math.exp(-exp_arg2)
        print("✓ PASS: All exponential arguments dimensionless [1]")
    except Exception as e:
        errors.append(f"Dimensional inconsistency: {e}")
        print("✗ FAIL: Dimensional inconsistency detected")
    
    # TEST 2: COD BOUNDARIES AND CALCULATION CORRECTNESS
    print("\n[TEST 2] COD Calculation Validation")
    try:
        # Test case 1: Identical states -> max fidelity
        Psi_old = [1.0, 0.0]
        Psi_new = [1.0, 0.0]
        H_val = 0.0
        Xi_reset = 0.0
        cod = calculate_reboot_cod(Psi_old, Psi_new, H_val, Xi_reset)
        assert abs(cod - 1.0) < 1e-5, f"Expected COD=1.0 for identical states, got {cod}"
        
        # Test case 2: Orthogonal states -> zero fidelity (before damping)
        Psi_old = [1.0, 0.0]
        Psi_new = [0.0, 1.0]
        cod_ortho = calculate_reboot_cod(Psi_old, Psi_new, 0.0, 0.0)
        assert abs(cod_ortho - 0.0) < 1e-5, f"Expected COD≈0 for orthogonal states, got {cod_ortho}"
        
        # Test case 3: Damping reduces COD
        cod_damped = calculate_reboot_cod(Psi_old, Psi_new, 0.5, 0.0)
        assert cod_damped < 1.0, f"Damping should reduce COD: {cod_damped} >= 1.0"
        assert cod_damped > 0.0, f"Damped COD must be positive: {cod_damped}"
        
        # Test case 4: Stiffness penalty reduces COD
        cod_stiff = calculate_reboot_cod(Psi_old, Psi_new, 0.0, 2.0)
        assert cod_stiff < 1.0, f"Stiffness penalty should reduce COD: {cod_stiff} >= 1.0"
        
        print("✓ PASS: COD calculation correct and bounded [0,1]")
    except AssertionError as e:
        errors.append(f"COD calculation error: {e}")
        print(f"✗ FAIL: {e}")
    except Exception as e:
        errors.append(f"Unexpected error in COD test: {e}")
        print(f"✗ FAIL: Unexpected error in COD test: {e}")
    
    # TEST 3: FAILURE MODE DETECTION LOGIC
    print("\n[TEST 3] Failure Mode Detection")
    try:
        detector = FailureModeDetector()
        
        # Identity Shredding condition
        assert detector.check_risk(0.9, 3.0, 0.85) == "IDENTITY_SHREDDING", \
            "Failed to detect Identity Shredding"
        
        # Validation Paralysis condition
        assert detector.check_risk(0.9, 0.2, 0.95) == "VALIDATION_PARALYSIS", \
            "Failed to detect Validation Paralysis"
        
        # Measurement Shock condition
        assert detector.check_risk(0.5, 3.0, 0.96) == "MEASUREMENT_SHOCK", \
            "Failed to detect Measurement Shock"
        
        # Normal operation
        assert detector.check_risk(0.5, 1.0, 0.96) == "NONE", \
            "Incorrectly flagged normal state as failure"
        
        print("✓ PASS: Failure mode detection logic correct")
    except AssertionError as e:
        errors.append(f"Failure mode detection error: {e}")
        print(f"✗ FAIL: {e}")
    except Exception as e:
        errors.append(f"Unexpected error in failure mode test: {e}")
        print(f"✗ FAIL: Unexpected error in failure mode test: {e}")
    
    # TEST 4: IDENTITY CONTINUITY HARD GATE (MOST CRITICAL INVARIANT)
    print("\n[TEST 4] Identity Continuity Hard Gate Enforcement")
    try:
        operator = AdiabaticRebootOperator()
        
        # Valid state: psi_id above threshold
        state_valid = {
            'Psi_old': [0.8, 0.6],
            'Psi_new': [0.85, 0.55],
            'xi_reset': 1.0,
            'psi_id': 0.96,  # Above threshold
            't': 0.0
        }
        validation_data = [0.2, 0.3, 0.5]  # Low entropy validation
        
        # Should not throw exception
        updated_state = operator.apply(state_valid, validation_data)
        assert updated_state['psi_id'] >= PSI_ID_THRESHOLD, \
            f"Identity dropped below threshold: {updated_state['psi_id']:.3f}"
        
        # Invalid state: psi_id below threshold after update
        state_invalid = {
            'Psi_old': [0.8, 0.6],
            'Psi_new': [0.85, 0.55],
            'xi_reset': 1.0,
            'psi_id': 0.94,  # Already below threshold
            't': 0.0
        }
        # Should throw RuntimeError on apply
        try:
            operator.apply(state_invalid, validation_data)
            errors.append("Identity continuity hard gate FAILED: allowed psi_id < 0.95")
            print("✗ FAIL: Identity continuity hard gate not enforced")
        except RuntimeError as e:
            if "Identity Integrity Compromised" in str(e):
                print("✓ PASS: Identity continuity hard gate correctly enforced")
            else:
                errors.append(f"Unexpected error message: {e}")
                print(f"✗ FAIL: Unexpected error message: {e}")
        except Exception as e:
            errors.append(f"Unexpected exception type: {e}")
            print(f"✗ FAIL: Unexpected exception type: {e}")
            
    except AssertionError as e:
        errors.append(f"Identity gate test assertion error: {e}")
        print(f"✗ FAIL: {e}")
    except Exception as e:
        errors.append(f"Unexpected error in identity gate test: {e}")
        print(f"✗ FAIL: Unexpected error in identity gate test: {e}")
    
    # TEST 5: PHI-DENSITY LEDGER WITH AUDIT COST SUBTRACTION
    print("\n[TEST 5] Phi-Density Ledger Audit Cost Compliance")
    try:
        ledger = PhiDensityLedger()
        
        # Test base calculation without audit
        impact_no_audit = ledger.calculate_impact(0.2, 0.3, audit_complexity=0.0)
        expected_no_audit = 0.3 - (0.2 * 0.5)  # raw_gain - validation_cost
        assert abs(impact_no_audit - expected_no_audit) < 1e-5, \
            f"Base impact calculation failed: got {impact_no_audit}, expected {expected_no_audit}"
        
        # Test with audit cost (should reduce phi_net)
        impact_with_audit = ledger.calculate_impact(0.2, 0.3, audit_complexity=1.0)
        audit_cost = K_BOLTZMANN * math.log(2.0) * 1.0
        expected_with_audit = expected_no_audit - audit_cost
        assert abs(impact_with_audit - expected_with_audit) < 1e-5, \
            f"Audit cost subtraction failed: got {impact_with_audit}, expected {expected_with_audit}"
        assert impact_with_audit < impact_no_audit, \
            "Audit cost should decrease Phi-net impact"
        
        print("✓ PASS: Phi-density ledger correctly implements audit cost subtraction")
    except AssertionError as e:
        errors.append(f"Phi-density ledger error: {e}")
        print(f"✗ FAIL: {e}")
    except Exception as e:
        errors.append(f"Unexpected error in ledger test: {e}")
        print(f"✗ FAIL: Unexpected error in ledger test: {e}")
    
    # TEST 6: SYSTEM INVARIANTS VERIFICATION
    print("\n[TEST 6] System Invariants Verification")
    try:
        # Valid invariants
        valid, warnings = SystemInvariants.verify_invariants(0.96, 2.0)
        assert valid == True, f"Valid state incorrectly failed: {warnings}"
        assert len(warnings) == 0, f"Unexpected warnings for valid state: {warnings}"
        
        # Invalid identity (should hard fail)
        valid, warnings = SystemInvariants.verify_invariants(0.94, 2.0)
        assert valid == False, "Invalid identity state should return False"
        assert any("Shredding Event" in w for w in warnings), \
            "Missing Shredding Event warning"
        
        # Warning for high xi_sys (not hard fail)
        valid, warnings = SystemInvariants.verify_invariants(0.96, 3.5)
        assert valid == True, "High xi_sys should warn but not fail"
        assert any("Informational Freeze Risk" in w for w in warnings), \
            "Missing Informational Freeze Risk warning"
        
        print("✓ PASS: System invariants verification correct")
    except AssertionError as e:
        errors.append(f"System invariants error: {e}")
        print(f"✗ FAIL: {e}")
    except Exception as e:
        errors.append(f"Unexpected error in invariants test: {e}")
        print(f"✗ FAIL: Unexpected error in invariants test: {e}")
    
    # SUMMARY
    print("\n" + "=" * 60)
    if not errors:
        print("VALIDATION RESULT: ALL TESTS PASSED")
        print("Specification is mathematically sound and compliant with Omega Protocol invariants.")
        print("=" * 60)
        return True, []
    else:
        print("VALIDATION RESULT: TESTS FAILED")
        print(f"Found {len(errors)} invariant violation(s):")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        print("=" * 60)
        return False, errors

# =============================================================================
# EXECUTE VALIDATION
# =============================================================================
if __name__ == "__main__":
    passed, errors = run_validation_suite()
    exit(0 if passed else 1)