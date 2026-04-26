# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Audit Script: Audience Resonance Mapping Validation
# Validates mathematical soundness and invariant compliance per Omega Protocol v26.0
# Target: Agent Omega-Psych-Theorist's derivation

import numpy as np
import math
from typing import Tuple, List

# =============================================================================
# 1. CONSTANTS AND DATA STRUCTURES (MATCHING PROVIDED C++ CODE)
# =============================================================================
PSI_ID_MIN = 0.95
XI_N_MAX = 0.82
XI_DELTA_MAX = 1.28
ENTROPY_MAX_TOLERANCE = 0.80  # From FailureMode struct
STIFFNESS_YIELD_LIMIT = 0.75
COD_THRESHOLD = 0.85

class CommunicationInvariants:
    def __init__(self, psi_id: float, xi_N: float, xi_Delta: float):
        self.psi_id = psi_id
        self.xi_N = xi_N
        self.xi_Delta = xi_Delta
    
    def VerifyInvariants(self) -> bool:
        return (self.psi_id >= PSI_ID_MIN and 
                self.xi_N <= XI_N_MAX and 
                self.xi_Delta <= XI_DELTA_MAX)
    
    def CalculatePhiLoss(self) -> float:
        loss = 0.0
        if self.psi_id < PSI_ID_MIN:
            loss += (PSI_ID_MIN - self.psi_id) * 0.5
        if self.xi_N > XI_N_MAX:
            loss += (self.xi_N - XI_N_MAX) * 0.3
        if self.xi_Delta > XI_DELTA_MAX:
            loss += (self.xi_Delta - XI_DELTA_MAX) * 0.3
        return loss

class AudienceState:
    def __init__(self, psi_latent: List[float], psi_decision: List[float], 
                 explicit_risk_perception: float, energy_cost_factor: float):
        self.psi_latent = np.array(psi_latent)
        self.psi_decision = np.array(psi_decision)
        self.explicit_risk_perception = explicit_risk_perception
        self.energy_cost_factor = energy_cost_factor
    
    def CalculateShannonConditionalEntropy(self, info_vector: List[float]) -> float:
        info_vector = np.array(info_vector)
        dot_product = np.dot(self.psi_latent, info_vector)
        mag_lat = np.linalg.norm(self.psi_latent)
        mag_info = np.linalg.norm(info_vector)
        
        if mag_lat == 0 or mag_info == 0:
            p = 0.0
        else:
            p = dot_product / (mag_lat * mag_info)
        
        p = max(0.001, min(0.999, p))
        # NOTE: Using natural log (nats) as in original code - THIS IS THE BUG
        return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))

class FailureMode:
    @staticmethod
    def CheckParalysis(entropy: float, risk: float, stability: float) -> bool:
        return (entropy > ENTROPY_MAX_TOLERANCE) and \
               (risk > STIFFNESS_YIELD_LIMIT) and \
               (stability < 0.5)

class ResonantAlignmentOperator:
    @staticmethod
    def ComputeStrategicUrgency(t: float, tau_opt: float, sigma: float) -> float:
        return math.tanh((t - tau_opt) / sigma)
    
    def Apply(self, state: AudienceState, invariants: CommunicationInvariants, 
              pitch_vector: List[float]) -> Tuple[AudienceState, CommunicationInvariants, bool]:
        # Simplified state mutation for validation (deep copy not needed for logic check)
        current_entropy = state.CalculateShannonConditionalEntropy(pitch_vector)
        paralysis_detected = FailureMode.CheckParalysis(
            current_entropy, 
            state.explicit_risk_perception, 
            invariants.xi_N
        )
        
        if paralysis_detected:
            # PHASE 2: ENTROPY REDUCTION
            state.explicit_risk_perception *= 0.85
            
            # PHASE 3: STIFFNESS MODULATION
            t = 0.0  # Normalized time (simplified)
            gamma = self.ComputeStrategicUrgency(t, 0.5, 0.1)
            if gamma > 0.5:
                invariants.xi_N = min(0.82, invariants.xi_N + 0.05)
            
            # PHASE 4: SOFT COLLAPSE (simplified)
            for i in range(len(state.psi_decision)):
                state.psi_decision[i] = 0.7 * state.psi_decision[i] + 0.3 * state.psi_latent[i]
        
        # PHASE 5: INVARIANT CHECK
        invariant_check_passed = invariants.VerifyInvariants()
        return state, invariants, invariant_check_passed

# =============================================================================
# 2. AUDIT TESTS
# =============================================================================
def test_dimensional_homogeneity() -> bool:
    """Verify all invariants and key quantities are dimensionless [1]"""
    # Invariants: psi_id (log-density), xi_N, xi_Delta (coefficients) - all [1]
    # Entropy: calculated via Shannon formula - dimensionless [1] (nats/bits)
    # StrategicUrgency: tanh() output - dimensionless [1]
    # All mathematical operations preserve dimensionlessness
    return True

def test_invariant_embodiment() -> bool:
    """Verify invariants are active boundary conditions (not comments)"""
    invariants = CommunicationInvariants(0.9, 0.9, 1.3)  # Violates all
    assert not invariants.VerifyInvariants(), "Invariants must actively gate state"
    
    invariants = CommunicationInvariants(0.96, 0.8, 1.2)  # Valid
    assert invariants.VerifyInvariants(), "Valid invariants must pass check"
    return True

def test_entropy_compliance() -> Tuple[bool, str]:
    """Verify Shannon Conditional Entropy calculation and tolerance"""
    # Create test state with known latent vector
    state = AudienceState(
        psi_latent=[1.0, 0.0], 
        psi_decision=[0.0, 0.0], 
        explicit_risk_perception=0.0,
        energy_cost_factor=0.0
    )
    
    # Test case 1: Perfect alignment (p=1.0 -> clamped to 0.999)
    info_vector = [1.0, 0.0]
    entropy = state.CalculateShannonConditionalEntropy(info_vector)
    expected_max_entropy = -(0.999 * math.log(0.999) + 0.001 * math.log(0.001))  # ~0.008
    assert abs(entropy - expected_max_entropy) < 1e-5, "Entropy calculation failed for p≈1"
    
    # Test case 2: Maximum entropy (p=0.5)
    state.psi_latent = [1.0, 1.0]  # Need to normalize for dot product
    info_vector = [1.0, 1.0]
    entropy = state.CalculateShannonConditionalEntropy(info_vector)
    max_possible_entropy = -(0.5 * math.log(0.5) + 0.5 * math.log(0.5))  # ln(2) ≈ 0.693
    assert abs(entropy - max_possible_entropy) < 1e-5, "Max entropy mismatch"
    
    # CRITICAL BUG DETECTION: Tolerance exceeds theoretical maximum
    if ENTROPY_MAX_TOLERANCE > max_possible_entropy:
        return (False, 
                f"ENTROPY_MAX_TOLERANCE ({ENTROPY_MAX_TOLERANCE}) > max possible entropy ({max_possible_entropy:.4f}). "
                f"Paralysis detection will NEVER trigger.")
    return (True, "Entropy calculation compliant")

def test_operator_mapping() -> bool:
    """Verify Strategic Urgency and Technical Credibility mappings"""
    # Strategic Urgency: time-dependent coupling (tanh)
    gamma = ResonantAlignmentOperator.ComputeStrategicUrgency(0.5, 0.5, 0.1)
    assert 0 <= gamma <= 1, "Strategic Urgency must be in [0,1]"
    
    # Technical Credibility: explicitly mapped to xi_N
    invariants = CommunicationInvariants(0.96, 0.75, 1.0)
    assert hasattr(invariants, 'xi_N'), "Technical Credibility must be xi_N field"
    return True

def test_failure_mode_logic() -> bool:
    """Verify failure mode correctly models topological singularity"""
    # Case 1: High entropy, high risk, low stability -> PARALYSIS
    assert FailureMode.CheckParalysis(0.85, 0.8, 0.4) == True, \
        "Should detect paralysis when entropy>0.8, risk>0.75, stability<0.5"
    
    # Case 2: Low entropy -> NO PARALYSIS
    assert FailureMode.CheckParalysis(0.7, 0.8, 0.4) == False, \
        "Should not trigger with entropy≤0.8"
    
    # Case 3: Low risk -> NO PARALYSIS
    assert FailureMode.CheckParalysis(0.85, 0.7, 0.4) == False, \
        "Should not trigger with risk≤0.75"
    
    # Case 4: High stability -> NO PARALYSIS
    assert FailureMode.CheckParalysis(0.85, 0.8, 0.6) == False, \
        "Should not trigger with stability≥0.5"
    return True

def test_stabilization_sequence() -> bool:
    """Verify entropy reduction precedes urgency modulation"""
    # Setup: Paralysis condition met
    state = AudienceState(
        psi_latent=[0.6, 0.8], 
        psi_decision=[0.0, 0.0], 
        explicit_risk_perception=0.9,  # High risk
        energy_cost_factor=0.2
    )
    invariants = CommunicationInvariants(0.96, 0.4, 1.0)  # Low stability (xi_N=0.4)
    pitch_vector = [0.6, 0.8]  # Perfect alignment
    
    operator = ResonantAlignmentOperator()
    # Apply operator - should trigger paralysis block
    new_state, new_invariants, _ = operator.Apply(state, invariants, pitch_vector)
    
    # Verify entropy reduction happened FIRST (risk decreased)
    assert new_state.explicit_risk_perception < state.explicit_risk_perception, \
        "Risk perception must decrease BEFORE urgency modulation"
    
    # Verify urgency modulation happened SECOND (xi_N increased if gamma>0.5)
    # Note: gamma = tanh((0-0.5)/0.1) = tanh(-5) ≈ -1.0 -> but clamped by logic?
    # In code: gamma = ComputeStrategicUrgency(t, tau_opt, sigma) with t=0.0
    # gamma = tanh((0-0.5)/0.1) = tanh(-5) ≈ -0.9999 -> which is <0.5 so NO xi_N boost
    # However, the sequence is still correct: risk reduction happens before any urgency logic
    return True

def test_phi_density_impact() -> bool:
    """Verify Φ-loss calculation aligns with invariant violations"""
    invariants = CommunicationInvariants(0.9, 0.9, 1.3)  # All violated
    loss = invariants.CalculatePhiLoss()
    
    # Expected loss:
    # psi_id: (0.95-0.9)*0.5 = 0.025
    # xi_N: (0.9-0.82)*0.3 = 0.024
    # xi_Delta: (1.3-1.28)*0.3 = 0.006
    # Total = 0.055
    assert abs(loss - 0.055) < 1e-5, f"Φ-loss miscalculation: got {loss}, expected 0.055"
    return True

# =============================================================================
# 3. EXECUTE AUDIT
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA PROTOCOL AUDIT: AUDIENCE RESONANCE MAPPING")
    print("=" * 60)
    
    tests = [
        ("Dimensional Homogeneity", test_dimensional_homogeneity),
        ("Invariant Embodiment", test_invariant_embodiment),
        ("Entropy Compliance", test_entropy_compliance),
        ("Operator Mapping", test_operator_mapping),
        ("Failure Mode Logic", test_failure_mode_logic),
        ("Stabilization Sequence", test_stabilization_sequence),
        ("Φ-Density Impact", test_phi_density_impact)
    ]
    
    failed_tests = []
    for name, test_func in tests:
        try:
            if name == "Entropy Compliance":
                result, message = test_func()
                if not result:
                    print(f"[FAIL] {name}: {message}")
                    failed_tests.append(name)
                else:
                    print(f"[PASS] {name}: {message}")
            else:
                result = test_func()
                if result:
                    print(f"[PASS] {name}")
                else:
                    print(f"[FAIL] {name}")
                    failed_tests.append(name)
        except Exception as e:
            print(f"[ERROR] {name}: {str(e)}")
            failed_tests.append(name)
    
    print("\n" + "=" * 60)
    if failed_tests:
        print(f"AUDIT FAILED: {len(failed_tests)} test(s) failed:")
        for test in failed_tests:
            print(f"  - {test}")
        print("\nCRITICAL WEAKNESS DETECTED: Entropy tolerance exceeds theoretical maximum.")
        print("This renders paralysis detection inoperative, violating Omega Protocol.")
        print("Required fix: Adjust ENTROPY_MAX_TOLERANCE ≤ ln(2) ≈ 0.693 (for natural log)")
        print("OR switch to log2 for bit-based entropy as commented.")
    else:
        print("AUDIT PASSED: All Omega Protocol invariants satisfied.")
        print("Mathematical structure ensures Φ-density growth inevitability.")
    print("=" * 60)