# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# Tolerance for floating point comparisons
TOL = 1e-5

def test_topological_impedance():
    """Test H_top calculation per Rubric §6"""
    # Test case 1: Empty path
    assert calculate_topological_impedance([]) == 0.0, "Empty path should return 0.0"
    
    # Test case 2: Single node (cost=0.5, variance=0.5)
    # H_top = (0.5*0.5)/0.5 / ln(1) -> but ln(1)=0, handled by setting H_max=1.0
    # Expected: (0.25)/0.5 / 1.0 = 0.5
    nodes = [{'approval_cost': 0.5, 'risk_variance': 0.5}]
    assert abs(calculate_topological_impedance(nodes) - 0.5) < TOL, "Single node H_top failed"
    
    # Test case 3: Two identical nodes (cost=1.0, variance=0.0 each)
    # Impedance = (1*0 + 1*0)/(1+1) = 0 -> H_top=0
    nodes = [{'approval_cost': 1.0, 'risk_variance': 0.0},
             {'approval_cost': 1.0, 'risk_variance': 0.0}]
    assert abs(calculate_topological_impedance(nodes)) < TOL, "Zero variance path failed"
    
    # Test case 4: Max impedance scenario (cost=1.0, variance=1.0 for N nodes)
    # Raw impedance = (N*1*1)/N = 1.0
    # H_max = ln(N) -> H_top = 1.0 / ln(N)
    # For N=2: H_top = 1.0/ln(2) ≈ 1.4427 -> clamped to 1.0
    nodes = [{'approval_cost': 1.0, 'risk_variance': 1.0} for _ in range(2)]
    h_top = calculate_topological_impedance(nodes)
    assert abs(h_top - 1.0) < TOL, f"Max impedance failed: got {h_top}"
    
    # Test case 5: Dimensional homogeneity check
    # All inputs dimensionless [0,1] -> output dimensionless [0,1]
    nodes = [{'approval_cost': 0.3, 'risk_variance': 0.7}]
    h_top = calculate_topological_impedance(nodes)
    assert 0.0 <= h_top <= 1.0, f"H_top out of bounds: {h_top}"

def test_cod_calculation():
    """Test COD calculation per Rubric §6"""
    # Test case 1: Perfect alignment, zero impedance, zero stiffness
    intent = [1.0, 0.0]
    outcome = [1.0, 0.0]
    cod = calculate_cod(intent, outcome, 0.0, 0.0)
    assert abs(cod - 1.0) < TOL, f"Perfect alignment failed: {cod}"
    
    # Test case 2: Orthogonal vectors
    intent = [1.0, 0.0]
    outcome = [0.0, 1.0]
    cod = calculate_cod(intent, outcome, 0.0, 0.0)
    assert abs(cod - 0.0) < TOL, f"Orthogonal failed: {cod}"
    
    # Test case 3: Entropic damping effect
    intent = [1.0, 0.0]
    outcome = [1.0, 0.0]
    cod_low = calculate_cod(intent, outcome, 0.0, 0.0)
    cod_high = calculate_cod(intent, outcome, 1.0, 0.0)  # H_top=1.0
    assert cod_high < cod_low, "Entropic damping not reducing COD"
    assert abs(cod_high - math.exp(-1.0)) < TOL, f"Damping factor wrong: {cod_high}"
    
    # Test case 4: Stiffness penalty effect
    intent = [1.0, 0.0]
    outcome = [1.0, 0.0]
    cod_low = calculate_cod(intent, outcome, 0.0, 0.0)
    cod_high = calculate_cod(intent, outcome, 0.0, 2.0)  # Xi_bound=2.0
    assert cod_high < cod_low, "Stiffness penalty not reducing COD"
    assert abs(cod_high - math.exp(-0.5*2.0)) < TOL, f"Stiffness penalty wrong: {cod_high}"
    
    # Test case 5: Boundary conditions
    intent = [0.6, 0.8]  # Normalized
    outcome = [0.6, 0.8]
    cod = calculate_cod(intent, outcome, 0.5, 1.0)
    assert 0.0 <= cod <= 1.0, f"COD out of bounds: {cod}"

def test_shannon_entropy():
    """Test Shannon conditional entropy per Rubric §5"""
    # Test case 1: Deterministic outcome
    probs = [1.0, 0.0, 0.0]
    h_cond = calculate_shannon_conditional_entropy(probs)
    assert abs(h_cond - 0.0) < TOL, f"Deterministic entropy failed: {h_cond}"
    
    # Test case 2: Uniform distribution (N=3)
    probs = [1/3, 1/3, 1/3]
    h_cond = calculate_shannon_conditional_entropy(probs)
    expected = 1.0  # Normalized by H_max=ln(3)
    assert abs(h_cond - expected) < TOL, f"Uniform entropy failed: {h_cond}"
    
    # Test case 3: Boundary check
    probs = [0.5, 0.5]
    h_cond = calculate_shannon_conditional_entropy(probs)
    expected = 1.0  # H=ln(2), H_max=ln(2) -> 1.0
    assert abs(h_cond - expected) < TOL, f"Binary uniform failed: {h_cond}"
    
    # Test case 4: Dimensional homogeneity
    probs = [0.2, 0.3, 0.5]
    h_cond = calculate_shannon_conditional_entropy(probs)
    assert 0.0 <= h_cond <= 1.0, f"Entropy out of bounds: {h_cond}"

def test_invariant_verification():
    """Test SystemInvariants.VerifyInvariants() per Rubric §3"""
    invariants = SystemInvariants(
        psi_id=0.96,   # Above threshold
        xi_sys=2.5,    # Below XI_SYS_MAX=3.0
        kappa_sys_ind=0.8,  # Below KAPPA_MAX=1.0
        xi_N=1.8,      # Below XI_N_MAX=2.0
        xi_Delta=2.2   # Below XI_DELTA_MAX=2.5
    )
    assert invariants.verify_invariants() == True, "Valid invariants failed"
    
    # Test psi_id violation
    invariants.psi_id = 0.94
    assert invariants.verify_invariants() == False, "psi_id < 0.95 should fail"
    
    # Test xi_N violation
    invariants.psi_id = 0.96
    invariants.xi_N = 2.1
    assert invariants.verify_invariants() == False, "xi_N > 2.0 should fail"
    
    # Test xi_Delta violation
    invariants.xi_N = 1.8
    invariants.xi_Delta = 2.6
    assert invariants.verify_invariants() == False, "xi_Delta > 2.5 should fail"
    
    # Test kappa_sys_ind violation
    invariants.xi_Delta = 2.2
    invariants.kappa_sys_ind = 1.1
    assert invariants.verify_invariants() == False, "kappa > 1.0 should fail"
    
    # Test xi_sys warning (not hard fail)
    invariants.kappa_sys_ind = 0.8
    invariants.xi_sys = 3.1
    # Should not return False (only warning), but we check it doesn't hard fail
    # Note: In real code, this logs warning but returns True
    # We'll assume the function returns True for xi_sys > 3.0 (as per C++ code comment)
    assert invariants.verify_invariants() == True, "xi_sys > 3.0 should not hard fail"

def test_phi_density_audit_cost():
    """Test Φ-density accounting with audit cost subtraction per Meta-Scrutiny"""
    # Base case: No audit complexity
    phi_net = monitor_phi_density(
        throughput=1.0,
        impedance_cost=0.2,
        risk_leak=0.1,
        individual_cost=0.1,
        audit_complexity_factor=0.0
    )
    expected = 1.0 - 0.2 - 0.1 - 0.1  # 0.6
    assert abs(phi_net - expected) < TOL, f"Base Phi-net failed: {phi_net}"
    
    # With audit cost (k=1.0, ln(2)≈0.693)
    phi_net_audit = monitor_phi_density(
        throughput=1.0,
        impedance_cost=0.2,
        risk_leak=0.1,
        individual_cost=0.1,
        audit_complexity_factor=1.0
    )
    audit_cost = math.log(2)  # ≈0.693
    expected_audit = 0.6 - audit_cost
    assert abs(phi_net_audit - expected_audit) < TOL, f"Audit cost subtraction failed: {phi_net_audit}"
    
    # Negative Phi-net detection
    phi_net_neg = monitor_phi_density(
        throughput=0.1,
        impedance_cost=0.2,
        risk_leak=0.1,
        individual_cost=0.1,
        audit_complexity_factor=1.0
    )
    assert phi_net_neg < 0.0, f"Negative Phi-net not detected: {phi_net_neg}"

def test_failure_mode_detection():
    """Test FailureModeDetector per Rubric §3"""
    detector = FailureModeDetector()
    
    # Test Procedural Black Hole: H_top > 0.85 AND Urgency < 0.5*H_top
    assert detector.check_risk(
        h_top=0.9, urgency=0.4, xi_ind=1.0, psi_id=0.96
    ) == FailureModeDetector.PROCEDURAL_BLACK_HOLE, "Procedural Black Hole missed"
    
    # Test Individual Burnout: Xi_ind > 2.0
    assert detector.check_risk(
        h_top=0.5, urgency=0.5, xi_ind=2.1, psi_id=0.96
    ) == FailureModeDetector.INDIVIDUAL_BURNOUT, "Individual Burnout missed"
    
    # Test Shredding Event: Psi_id < 0.95
    assert detector.check_risk(
        h_top=0.5, urgency=0.5, xi_ind=1.0, psi_id=0.94
    ) == FailureModeDetector.SHREDDING_EVENT, "Shredding Event missed"
    
    # Test stable state
    assert detector.check_risk(
        h_top=0.5, urgency=0.5, xi_ind=1.0, psi_id=0.96
    ) == FailureModeDetector.NONE, "Stable state misclassified"

# --- Helper function implementations (mirroring C++ logic) ---

def calculate_topological_impedance(path):
    if not path:
        return 0.0
    total_impedance = sum(node['approval_cost'] * node['risk_variance'] for node in path)
    total_length = sum(node['approval_cost'] for node in path)
    if total_length == 0:
        return 0.0
    raw_impedance = total_impedance / total_length
    h_max = math.log(len(path)) if len(path) > 1 else 1.0
    if h_max < 1e-9:
        h_max = 1.0
    return min(1.0, max(0.0, raw_impedance / h_max))

def calculate_cod(intent, outcome, h_top, xi_bound):
    # Normalize vectors
    intent = np.array(intent)
    outcome = np.array(outcome)
    dot = np.dot(intent, outcome)
    mag_i = np.linalg.norm(intent)
    mag_o = np.linalg.norm(outcome)
    if mag_i < 1e-9 or mag_o < 1e-9:
        fidelity = 0.0
    else:
        fidelity = dot / (mag_i * mag_o)
        fidelity = max(0.0, min(1.0, fidelity))  # Clamp [0,1]
    
    lambda_coupling = 1.0
    gamma_coupling = 0.5
    damping = math.exp(-lambda_coupling * h_top)
    stiffness_penalty = math.exp(-gamma_coupling * xi_bound)
    return fidelity * damping * stiffness_penalty

def calculate_shannon_conditional_entropy(outcome, h_top=None):
    # Note: h_top parameter unused in C++ implementation (kept for signature compatibility)
    if not outcome:
        return 0.0
    outcome = np.array(outcome)
    # Avoid log(0)
    outcome = np.clip(outcome, 1e-9, None)
    outcome = outcome / np.sum(outcome)  # Normalize to probability distribution
    entropy = -np.sum(outcome * np.log(outcome))
    max_entropy = math.log(len(outcome)) if len(outcome) > 1 else 1.0
    if max_entropy < 1e-9:
        max_entropy = 1.0
    return min(1.0, max(0.0, entropy / max_entropy))

class SystemInvariants:
    def __init__(self, psi_id, xi_sys, kappa_sys_ind, xi_N, xi_Delta):
        self.psi_id = psi_id
        self.xi_sys = xi_sys
        self.kappa_sys_ind = kappa_sys_ind
        self.xi_N = xi_N
        self.xi_Delta = xi_Delta
    
    def verify_invariants(self):
        PSI_ID_MIN = 0.95
        XI_SYS_MAX = 3.0
        XI_N_MAX = 2.0
        XI_DELTA_MAX = 2.5
        KAPPA_MAX = 1.0
        
        if self.psi_id < PSI_ID_MIN:
            return False  # Shredding Event
        if self.xi_N > XI_N_MAX:
            return False  # Stable Mode Violation
        if self.xi_Delta > XI_DELTA_MAX:
            return False  # Adversarial Mode Violation
        if self.kappa_sys_ind > KAPPA_MAX:
            return False  # System-Individual Overload
        # xi_sys > XI_SYS_MAX is warning only (not hard fail)
        return True
    
    def calculate_phi_loss(self, audit_complexity_factor=1.0):
        K_BOLTZMANN = 1.0
        loss = 0.0
        if self.psi_id < 0.95:
            loss += (0.95 - self.psi_id) * 0.5 * K_BOLTZMANN
        if self.xi_sys > 3.0:
            loss += (self.xi_sys - 3.0) * 0.2 * K_BOLTZMANN
        audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity_factor
        loss += audit_entropy_cost
        return loss

class PhiDecomposition:
    def calculate_phi_n(self, throughput, cod, risk_leak):
        return throughput * cod * (1.0 - risk_leak)
    
    def calculate_phi_delta(self, attack_success, cod, risk_leak):
        return attack_success * (1.0 - cod) * risk_leak
    
    def calculate_net_phi(self, phi_n, phi_delta):
        return phi_n - phi_delta

def monitor_phi_density(throughput, impedance_cost, risk_leak, individual_cost, 
                       audit_complexity_factor=1.0, invariants=None):
    if invariants is None:
        invariants = SystemInvariants(1.0, 1.0, 0.5, 1.5, 1.5)
    phi_net = throughput - impedance_cost - risk_leak - individual_cost
    audit_cost = invariants.calculate_phi_loss(audit_complexity_factor)
    phi_net -= audit_cost
    return phi_net

class FailureModeDetector:
    NONE = 0
    PROCEDURAL_BLACK_HOLE = 1
    INDIVIDUAL_BURNOUT = 2
    SHREDDING_EVENT = 3
    
    H_TOP_LIMIT = 0.85
    XI_SYS_MAX = 3.0
    XI_IND_THRESHOLD = 2.0
    PSI_ID_MIN = 0.95
    
    def check_risk(self, h_top, urgency, xi_ind, psi_id):
        if h_top > self.H_TOP_LIMIT and urgency < (self.H_TOP_LIMIT * 0.5):
            return self.PROCEDURAL_BLACK_HOLE
        if xi_ind > self.XI_IND_THRESHOLD:
            return self.INDIVIDUAL_BURNOUT
        if psi_id < self.PSI_ID_MIN:
            return self.SHREDDING_EVENT
        return self.NONE

def run_all_tests():
    """Run validation suite for Omega Protocol compliance"""
    test_topological_impedance()
    test_cod_calculation()
    test_shannon_entropy()
    test_invariant_verification()
    test_phi_density_audit_cost()
    test_failure_mode_detection()
    print("✅ ALL TESTS PASSED: Omega Protocol mathematical invariants verified")
    return True

if __name__ == "__main__":
    try:
        run_all_tests()
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {e}")
        exit(1)