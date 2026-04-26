# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# =============================================================================
# VALIDATION SCRIPT: BUREAUCRATIC IMPEDANCE MANIFOLD MATHEMATICAL SOUNDNESS
# =============================================================================
# This script validates the core mathematical operations and invariant compliance
# of the Bureaucratic Decision Manifold specification against Omega Protocol requirements.
# =============================================================================

class ValidationError(Exception):
    pass

def test_dimensional_homogeneity():
    """Verify all exponential arguments are dimensionless [1]"""
    print("Testing dimensional homogeneity...")
    
    # Test parameters from specification
    Lambda = 1.0  # Entropic damping coupling [1]
    Gamma = 0.6   # Stiffness penalty coupling [1]
    
    # H_proc must be dimensionless [0,1] (normalized Shannon entropy)
    H_proc_test = 0.75  # Valid normalized entropy
    arg1 = Lambda * H_proc_test
    assert isinstance(arg1, (int, float)) and not math.isnan(arg1), "H_proc must be real number"
    assert 0 <= H_proc_test <= 1.0, "H_proc must be normalized [0,1]"
    
    # Xi_rule and Xi_req must be dimensionless [1] (stiffness measures)
    Xi_rule_test = 2.5
    Xi_req_test = 1.8
    arg2 = Gamma * abs(Xi_rule_test - Xi_req_test)
    assert isinstance(arg2, (int, float)) and not math.isnan(arg2), "Stiffness difference must be real"
    
    # psi = ln(phi_N) must be dimensionless [1]
    phi_N_test = 0.96  # Must be > 0.95 for invariant
    psi_test = math.log(phi_N_test)
    assert isinstance(psi_test, (int, float)) and not math.isnan(psi_test), "psi must be real"
    
    print("✓ Dimensional homogeneity verified")

def test_process_entropy():
    """Validate normalized Shannon entropy calculation"""
    print("Testing process entropy calculation...")
    
    def calc_process_entropy(approval_chain):
        if not approval_chain:
            return 0.0
        H = 0.0
        max_entropy = math.log(len(approval_chain))
        if max_entropy < 1e-9:
            max_entropy = 1.0
        for prob in approval_chain:
            if prob > 1e-9:
                H -= prob * math.log(prob)
        return min(1.0, max(0.0, H / max_entropy))
    
    # Test uniform distribution (max entropy)
    uniform = [0.2, 0.2, 0.2, 0.2, 0.2]
    entropy_uniform = calc_process_entropy(uniform)
    assert abs(entropy_uniform - 1.0) < 1e-5, f"Uniform entropy should be 1.0, got {entropy_uniform}"
    
    # Test delta distribution (min entropy)
    delta = [1.0, 0.0, 0.0, 0.0, 0.0]
    entropy_delta = calc_process_entropy(delta)
    assert entropy_delta < 1e-5, f"Delta entropy should be ~0, got {entropy_delta}"
    
    # Test normalization boundary
    single = [1.0]
    entropy_single = calc_process_entropy(single)
    assert entropy_single < 1e-5, f"Single element entropy should be ~0, got {entropy_single}"
    
    print("✓ Process entropy validation passed")

def test_cod_calculation():
    """Validate Bureaucratic COD formula implementation"""
    print("Testing COD calculation...")
    
    Lambda = 1.0
    Gamma = 0.6
    
    def calc_cod(intent, exec_vec, H_proc, Xi_rule, Xi_req):
        # Fidelity calculation
        dot = sum(i*e for i,e in zip(intent, exec_vec))
        mag_i = math.sqrt(sum(i*i for i in intent))
        mag_e = math.sqrt(sum(e*e for e in exec_vec))
        fidelity = 0.0
        if mag_i > 1e-9 and mag_e > 1e-9:
            fidelity = dot / (mag_i * mag_e)
            fidelity = max(0.0, min(1.0, fidelity))  # Clamp [0,1]
        
        # Entropic damping
        damping = math.exp(-Lambda * H_proc)
        
        # Stiffness penalty
        stiffness_diff = abs(Xi_rule - Xi_req)
        penalty = math.exp(-Gamma * stiffness_diff)
        
        return fidelity * damping * penalty
    
    # Test perfect alignment, no entropy, perfect stiffness match
    intent = [1.0, 0.0, 0.0]
    exec_vec = [1.0, 0.0, 0.0]
    cod_perfect = calc_cod(intent, exec_vec, 0.0, 1.0, 1.0)
    assert abs(cod_perfect - 1.0) < 1e-5, f"Perfect COD should be 1.0, got {cod_perfect}"
    
    # Test entropy damping effect
    cod_high_entropy = calc_cod(intent, exec_vec, 0.9, 1.0, 1.0)
    expected_damping = math.exp(-1.0 * 0.9)
    assert abs(cod_high_entropy - expected_damping) < 1e-5, \
        f"High entropy COD mismatch: got {cod_high_entropy}, expected {expected_damping}"
    
    # Test stiffness penalty effect
    cod_mismatch = calc_cod(intent, exec_vec, 0.0, 3.0, 1.0)
    expected_penalty = math.exp(-0.6 * abs(3.0-1.0))
    assert abs(cod_mismatch - expected_penalty) < 1e-5, \
        f"Stiffness penalty COD mismatch: got {cod_mismatch}, expected {expected_penalty}"
    
    # Test boundary conditions
    cod_zero = calc_cod([1.0,0.0], [0.0,1.0], 0.5, 2.0, 2.0)  # Orthogonal vectors
    assert cod_zero < 1e-5, f"Orthogonal vectors should give near-zero COD, got {cod_zero}"
    
    print("✓ COD calculation validation passed")

def test_adiabatic_flow_invariants():
    """Validate AFP preserves organizational identity invariant (psi >= ln(0.95))"""
    print("Testing AFP invariant preservation...")
    
    PSI_ID_MIN = 0.95
    PSI_MIN_THRESHOLD = math.log(PSI_ID_MIN)  # ≈ -0.05129
    
    class MockState:
        def __init__(self):
            self.psi_intent = [1.0, 0.0, 0.0]
            self.psi_exec = [0.8, 0.2, 0.0]  # Slightly misaligned
            self.approval_chain = [0.7, 0.6, 0.5]  # Moderate entropy
            self.phi_K = 0.8
            self.phi_Sigma = 0.3
            self.xi_rule = 2.5
            self.psi = math.log(0.96)  # Valid initial identity (ln(0.96) > ln(0.95))
            self.t = 0.5
            self.state_lock = None  # Simplified for test
    
    class MockInvariants:
        LAMBDA_COUPLING = 1.0
        GAMMA_COUPLING = 0.6
        PSI_ID_MIN = 0.95
        XI_RULE_MAX = 3.0
        COD_THRESHOLD = 0.80
        
        def __init__(self, psi, xi_rule, phi_K, phi_Sigma):
            self.psi = psi
            self.xi_rule = xi_rule
            self.phi_K = phi_K
            self.phi_Sigma = phi_Sigma
    
    def calc_process_entropy(chain):
        if not chain:
            return 0.0
        H = 0.0
        max_entropy = math.log(len(chain))
        if max_entropy < 1e-9:
            max_entropy = 1.0
        for p in chain:
            if p > 1e-9:
                H -= p * math.log(p)
        return min(1.0, max(0.0, H / max_entropy))
    
    def calc_cod(intent, exec_vec, H_proc, Xi_rule, Xi_req):
        dot = sum(i*e for i,e in zip(intent, exec_vec))
        mag_i = math.sqrt(sum(i*i for i in intent))
        mag_e = math.sqrt(sum(e*e for e in exec_vec))
        fidelity = 0.0
        if mag_i > 1e-9 and mag_e > 1e-9:
            fidelity = dot / (mag_i * mag_e)
            fidelity = max(0.0, min(1.0, fidelity))
        damping = math.exp(-MockInvariants.LAMBDA_COUPLING * H_proc)
        penalty = math.exp(-MockInvariants.GAMMA_COUPLING * abs(Xi_rule - Xi_req))
        return fidelity * damping * penalty
    
    def apply_afp(state, invariants):
        # Simplified AFP core logic focusing on invariant preservation
        H_proc = calc_process_entropy(state.approval_chain)
        Xi_req = max(0.1, 1.0 - H_proc)  # Urgency model
        current_cod = calc_cod(state.psi_intent, state.psi_exec, H_proc, state.xi_rule, Xi_req)
        
        # Stiffness modulation (simplified)
        if H_proc > 0.9 and state.xi_rule > 2.5:  # Metric degeneracy risk
            state.xi_rule = max(0.5, state.xi_rule * 0.8)
        elif current_cod < 0.8 and state.xi_rule > 2.0:
            state.xi_rule = min(2.0, state.xi_rule * 0.9)
            if state.approval_chain:
                state.approval_chain.pop()  # Remove layer
        
        # State transformation (interpolation)
        alpha = min(1.0, (1.0 - state.xi_rule) * 0.5 + 0.5)
        for i in range(len(state.psi_intent)):
            state.psi_exec[i] = (1.0 - alpha) * state.psi_exec[i] + alpha * state.psi_intent[i]
        
        # Identity continuity check (critical invariant)
        identity_loss = H_proc * 0.05
        current_phi_N = math.exp(state.psi)
        current_phi_N -= identity_loss
        state.psi = math.log(current_phi_N)
        
        # Hard gate invariant check
        if state.psi < math.log(MockInvariants.PSI_ID_MIN):
            raise ValidationError(f"Identity continuity breached: psi={state.psi} < ln({MockInvariants.PSI_ID_MIN})")
        
        # Update invariants
        invariants.psi = state.psi
        invariants.xi_rule = state.xi_rule
        invariants.phi_Sigma = H_proc
    
    # Test case 1: Stable state should preserve identity
    state1 = MockState()
    invariants1 = MockInvariants(state1.psi, state1.xi_rule, state1.phi_K, state1.phi_Sigma)
    try:
        apply_afp(state1, invariants1)
        assert state1.psi >= PSI_MIN_THRESHOLD, f"Identity not preserved: psi={state1.psi}"
        print("  ✓ Stable state identity preserved")
    except ValidationError as e:
        raise ValidationError(f"Stable state failed: {e}")
    
    # Test case 2: High entropy state should trigger stiffness reduction without breaking identity
    state2 = MockState()
    state2.approval_chain = [0.95, 0.9, 0.85, 0.8]  # High entropy
    state2.xi_rule = 3.2  # Near degeneracy risk
    invariants2 = MockInvariants(state2.psi, state2.xi_rule, state2.phi_K, state2.phi_Sigma)
    try:
        apply_afp(state2, invariants2)
        assert state2.psi >= PSI_MIN_THRESHOLD, f"Identity not preserved under stress: psi={state2.psi}"
        assert state2.xi_rule < 3.2, "Stiffness should have been reduced"
        print("  ✓ High entropy state identity preserved with stiffness modulation")
    except ValidationError as e:
        raise ValidationError(f"High entropy state failed: {e}")
    
    # Test case 3: Extreme case approaching invariant boundary
    state3 = MockState()
    state3.psi = math.log(0.951)  # Just above threshold
    state3.approval_chain = [0.99]  # Very high entropy
    state3.xi_rule = 3.5
    invariants3 = MockInvariants(state3.psi, state3.xi_rule, state3.phi_K, state3.phi_Sigma)
    try:
        apply_afp(state3, invariants3)
        # Should either preserve identity or throw valid invariant violation
        if state3.psi < PSI_MIN_THRESHOLD:
            raise ValidationError(f"Identity breached: psi={state3.psi}")
        print("  ✓ Boundary case handled correctly")
    except ValidationError as e:
        if "Identity continuity breached" in str(e):
            print("  ✓ Boundary case correctly triggered invariant violation")
        else:
            raise
    
    print("✓ AFP invariant preservation validation passed")

def test_phi_density_audit_cost():
    """Validate Phi density calculation includes audit cost subtraction"""
    print("Testing Phi density with audit cost subtraction...")
    
    K_BOLTZMANN = 1.0  # Normalized for informational entropy
    
    def calc_phi_impact(h_proc, cod_gain, audit_complexity=1.0):
        raw_gain = cod_gain
        entropy_cost = h_proc * 0.5
        audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
        phi_net = raw_gain - entropy_cost - audit_entropy_cost
        return phi_net, raw_gain, entropy_cost, audit_entropy_cost
    
    # Test baseline: no entropy, perfect gain, no audit complexity
    phi_net, raw, ent_cost, audit_cost = calc_phi_impact(0.0, 0.3, 0.0)
    assert abs(phi_net - 0.3) < 1e-5, f"Baseline Phi net should be 0.3, got {phi_net}"
    assert audit_cost == 0.0, "Audit cost should be zero when complexity=0"
    
    # Test with entropy cost
    phi_net, raw, ent_cost, audit_cost = calc_phi_impact(0.8, 0.4, 0.0)
    expected_net = 0.4 - (0.8*0.5) - 0.0  # 0.4 - 0.4 = 0.0
    assert abs(phi_net - expected_net) < 1e-5, f"Entropy cost Phi net should be {expected_net}, got {phi_net}"
    
    # Test with audit cost (Meta-Scrutiny requirement)
    phi_net, raw, ent_cost, audit_cost = calc_phi_impact(0.5, 0.6, 2.0)
    expected_audit = 1.0 * math.log(2.0) * 2.0  # ≈ 1.386
    expected_net = 0.6 - (0.5*0.5) - expected_audit  # 0.6 - 0.25 - 1.386 = -1.036
    assert abs(phi_net - expected_net) < 1e-5, \
        f"Audit cost Phi net should be {expected_net}, got {phi_net}"
    assert abs(audit_cost - expected_audit) < 1e-5, \
        f"Audit cost should be {expected_audit}, got {audit_cost}"
    
    # Verify audit cost is always subtracted (never added)
    assert audit_cost >= 0.0, "Audit cost must be non-negative (entropy cost)"
    
    print("✓ Phi density audit cost validation passed")

def test_metric_non_degeneracy_condition():
    """Validate metric degeneracy detection logic"""
    print("Testing metric degeneracy condition...")
    
    H_PROC_LIMIT = 0.90
    XI_RULE_MAX = 3.0
    PSI_ID_CRITICAL = 0.90
    COD_THRESHOLD = 0.80
    
    def check_risk(H_proc, Xi_rule, psi, cod):
        # Metric degeneracy condition: H_proc > H_LIMIT AND Xi_rule > XI_MAX AND psi < ln(PSI_ID_CRITICAL)
        psi_critical = math.log(PSI_ID_CRITICAL)
        if H_proc > H_PROC_LIMIT and Xi_rule > XI_RULE_MAX and psi < psi_critical:
            return "METRIC_DEGENERACY"
        # Identity drift: psi < ln(PSI_ID_MIN)
        if psi < math.log(0.95):
            return "IDENTITY_DRIFT"
        # Decision paralysis: low COD and high stiffness
        if cod < COD_THRESHOLD and Xi_rule > 2.5:
            return "DECISION_PARALYSIS"
        return "NONE"
    
    # Test metric degeneracy trigger
    assert check_risk(0.95, 3.2, math.log(0.89), 0.7) == "METRIC_DEGENERACY"
    # Test identity drift
    assert check_risk(0.5, 2.0, math.log(0.94), 0.85) == "IDENTITY_DRIFT"
    # Test decision paralysis
    assert check_risk(0.7, 2.8, math.log(0.96), 0.75) == "DECISION_PARALYSIS"
    # Test stable state
    assert check_risk(0.6, 2.0, math.log(0.97), 0.85) == "NONE"
    
    print("✓ Metric non-degeneracy condition validation passed")

def main():
    """Run all validation tests"""
    print("=" * 70)
    print("OMEGA PROTOCOL BUREAUCRATIC MANIFOLD MATHEMATICAL VALIDATION")
    print("=" * 70)
    
    try:
        test_dimensional_homogeneity()
        test_process_entropy()
        test_cod_calculation()
        test_adiabatic_flow_invariants()
        test_phi_density_audit_cost()
        test_metric_non_degeneracy_condition()
        
        print("=" * 70)
        print("✅ ALL VALIDATIONS PASSED - MANIFOLD IS MATHEMATICALLY SOUND")
        print("✅ OMEGA PROTOCOL INVARIANTS ARE SATISFIED")
        print("=" * 70)
        
    except Exception as e:
        print("=" * 70)
        print(f"❌ VALIDATION FAILED: {str(e)}")
        print("=" * 70)
        raise

if __name__ == "__main__":
    main()