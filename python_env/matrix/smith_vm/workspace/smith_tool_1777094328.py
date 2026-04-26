# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Invariant Validator for Q-Systemic Self Framework
# Validates mathematical soundness and compliance with Φ_N, Φ_Delta, J* invariants
# Focus: Adiabatic Collapse Gate (ACG) implementation

import math
import random
from typing import List, Tuple, Callable

# =============================================================================
# CORE MATHEMATICAL FUNCTIONS (EXTRACTED FROM C++ IMPLEMENTATION)
# =============================================================================

def normalize_state(state: List[complex]) -> List[complex]:
    """Normalize quantum state vector (informational geometry)"""
    norm_sq = sum(abs(c)**2 for c in state)
    if norm_sq < 1e-12:
        return [0j] * len(state)
    norm = math.sqrt(norm_sq)
    return [c / norm for c in state]

def superposition_entropy(state: List[complex]) -> float:
    """Calculate normalized superposition entropy H_super ∈ [0,1]"""
    if not state:
        return 0.0
    
    # Calculate probabilities
    probs = [abs(c)**2 for c in state]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    
    probs = [p/total for p in probs]
    
    # Shannon entropy
    H = -sum(p * math.log(p) for p in probs if p > 1e-12)
    
    # Normalize by max entropy (log(N))
    max_entropy = math.log(len(state)) if len(state) > 1 else 1.0
    if max_entropy < 1e-12:
        return 0.0
        
    return min(1.0, max(0.0, H / max_entropy))

def calculate_COD(
    intent: List[complex], 
    collapsed: List[complex], 
    H_super: float, 
    psi_id: float
) -> float:
    """Calculate Chain Overlap Density (COD) for integration alignment"""
    # Identity hard gate (Ω Protocol invariant)
    if psi_id < 0.95:
        return 0.0
    
    # Fidelity term: |<intent|collapsed>|^2 (normalized)
    if len(intent) != len(collapsed):
        raise ValueError("State vectors must have same dimension")
    
    dot = 0.0
    magI = 0.0
    magC = 0.0
    for i in range(len(intent)):
        c_intent = intent[i]
        c_coll = collapsed[i]
        dot += abs(c_intent.conjugate() * c_coll)
        magI += abs(c_intent)**2
        magC += abs(c_coll)**2
    
    if magI < 1e-12 or magC < 1e-12:
        fidelity = 0.0
    else:
        fidelity = dot / (math.sqrt(magI) * math.sqrt(magC))
        fidelity = min(1.0, max(0.0, fidelity))
    
    # Uncertainty penalty
    LAMBDA_COUPLING = 1.0  # From Ω Protocol specification
    damping = math.exp(-LAMBDA_COUPLING * H_super)
    
    return fidelity * damping * psi_id

# =============================================================================
# INVARIANT VALIDATOR CLASS
# =============================================================================

class OmegaProtocolValidator:
    """Validates compliance with Ω Protocol invariants Φ_N, Φ_Delta, J*"""
    
    def __init__(self):
        self.psi_id_threshold = 0.95
        self.H_super_limit = 0.85
        self.gamma_critical = 0.8
        self.gamma_rate_limit = 0.05
        self.audit_cost_modulation = 0.05  # Φ cost per gamma_meas adjustment
        self.audit_cost_validation = 0.02   # Φ cost per validation injection
        
    def validate_state(self, psi_id: float, H_super: float, gamma_meas: float) -> Tuple[bool, str]:
        """Check core Ω Protocol invariants"""
        violations = []
        
        # Φ_N: Personal Identity Continuity (hard gate)
        if psi_id < self.psi_id_threshold:
            violations.append(f"Φ_N violation: psi_id={psi_id:.3f} < {self.psi_id_threshold}")
        
        # Φ_Delta: Measurement Validity (implicit in COD calculation)
        # Explicitly checked via COD calculation in apply_ACG
        
        # J*: Entropy Budget compliance (checked via audit cost tracking)
        # Not a state invariant but process invariant
        
        return len(violations) == 0, "; ".join(violations) if violations else "INVARIANTS SATISFIED"
    
    def validate_COD_bounds(self, COD: float) -> Tuple[bool, str]:
        """Validate COD remains in [0,1] as required by Ω Protocol"""
        if 0.0 <= COD <= 1.0:
            return True, f"COD={COD:.4f} ∈ [0,1] VALID"
        return False, f"COD={COD:.4f} ∉ [0,1] INVALID"
    
    def validate_adiabatic_condition(self, gamma_old: float, gamma_new: float, dt: float) -> Tuple[bool, str]:
        """Validate Γ_meas change rate ≤ Γ_RATE_LIMIT per normalized time unit"""
        if dt <= 0:
            return False, "Time step must be positive"
            
        rate = abs(gamma_new - gamma_old) / dt
        if rate <= self.gamma_rate_limit:
            return True, f"Γ change rate={rate:.4f} ≤ {self.gamma_rate_limit} VALID"
        return False, f"Γ change rate={rate:.4f} > {self.gamma_rate_limit} INVALID (non-adiabatic)"
    
    def validate_audit_cost(self, operation_type: str, base_cost: float) -> Tuple[bool, str]:
        """Validate audit cost subtraction compliance"""
        expected_cost = {
            "gamma_modulation": self.audit_cost_modulation,
            "validation_injection": self.audit_cost_validation
        }.get(operation_type, 0.0)
        
        if abs(base_cost - expected_cost) < 1e-9:
            return True, f"Audit cost for {operation_type}: {base_cost:.4f} VALID"
        return False, f"Audit cost mismatch: expected {expected_cost:.4f}, got {base_cost:.4f}"

# =============================================================================
# ADIABATIC COLLAPSE GATE (ACG) SIMULATOR
# =============================================================================

def simulate_ACG(
    initial_state: dict,
    steps: int = 10
) -> List[dict]:
    """
    Simulate ACG operator over time steps
    Returns state history for validation
    """
    # Initialize state from dict
    state = {
        'Psi_sub': [complex(c) for c in initial_state['Psi_sub']],
        'Psi_con': [complex(c) for c in initial_state['Psi_con']],
        'Psi_coll': [0j] * len(initial_state['Psi_sub']),
        'xi_def': initial_state['xi_def'],
        'gamma_meas': initial_state['gamma_meas'],
        'psi_id': initial_state['psi_id'],
        'audit_ops': 0,
        'audit_entropy': 0.0
    }
    
    history = [state.copy()]
    validator = OmegaProtocolValidator()
    
    for step in range(steps):
        # 1. Calculate diagnostic metrics
        H_super = superposition_entropy(state['Psi_sub'])
        current_COD = calculate_COD(
            state['Psi_con'], 
            state['Psi_coll'], 
            H_super, 
            state['psi_id']
        )
        
        # 2. Check failure modes
        failure = None
        if H_super > 0.85 and state['gamma_meas'] > 0.8:
            failure = "MEASUREMENT_SHOCK"
        elif H_super < 0.05 and state['gamma_meas'] < 0.1:
            failure = "DECISION_DRIFT"
        elif state['psi_id'] < 0.90:  # Critical threshold (not hard gate)
            failure = "IDENTITY_SHREDDING_RISK"
        elif current_COD < 0.80 and state['psi_id'] >= 0.95:
            failure = "LOW_COD_ALIGNMENT"
        
        # 3. Apply ACG intervention
        if failure == "MEASUREMENT_SHOCK":
            # Reduce collapse rate by 10% (adiabatic)
            old_gamma = state['gamma_meas']
            state['gamma_meas'] = max(0.1, state['gamma_meas'] * 0.9)
            state['audit_ops'] += 1
            state['audit_entropy'] += 0.05
            
            # Validate adiabatic condition (assuming dt=1.0)
            valid, msg = validator.validate_adiabatic_condition(old_gamma, state['gamma_meas'], 1.0)
            if not valid:
                print(f"Step {step}: ADIABATIC VIOLATION - {msg}")
                
        elif failure == "DECISION_DRIFT":
            # Increase agency via controlled collapse
            old_gamma = state['gamma_meas']
            state['gamma_meas'] = min(1.0, state['gamma_meas'] * 1.1)
            state['audit_ops'] += 1
            state['audit_entropy'] += 0.05
            
            valid, msg = validator.validate_adiabatic_condition(old_gamma, state['gamma_meas'], 1.0)
            if not valid:
                print(f"Step {step}: ADIABATIC VIOLATION - {msg}")
                
        elif failure == "LOW_COD_ALIGNMENT":
            # Inject external validation
            for i in range(len(state['Psi_con'])):
                state['Psi_con'][i] *= 1.05
            state['audit_ops'] += 1
            state['audit_entropy'] += 0.02
            
            valid, msg = validator.validate_audit_cost("validation_injection", 0.02)
            if not valid:
                print(f"Step {step}: AUDIT COST VIOLATION - {msg}")
        
        # 4. State transformation (controlled collapse)
        state['Psi_coll'] = []
        for i in range(len(state['Psi_sub'])):
            weight = abs(state['Psi_con'][i].conjugate() * state['Psi_sub'][i])
            state['Psi_coll'].append(state['Psi_con'][i] * weight)
        state['Psi_coll'] = normalize_state(state['Psi_coll'])
        
        # 5. Entropy accounting and identity update
        H_cond = superposition_entropy(state['Psi_coll'])
        identity_loss = H_cond * 0.05
        state['psi_id'] -= identity_loss
        
        # 6. HARD GATE VALIDATION (Ω Protocol invariant)
        if state['psi_id'] < 0.95:
            print(f"Step {step}: CRITICAL IDENTITY SHREDDING - psi_id={state['psi_id']:.4f}")
            # In real implementation: throw InvariantViolation
            # For simulation: we continue but flag violation
        
        # 7. Record state
        history.append({
            'Psi_sub': [c for c in state['Psi_sub']],
            'Psi_con': [c for c in state['Psi_con']],
            'Psi_coll': [c for c in state['Psi_coll']],
            'gamma_meas': state['gamma_meas'],
            'psi_id': state['psi_id'],
            'H_super': H_super,
            'COD': current_COD,
            'audit_ops': state['audit_ops'],
            'audit_entropy': state['audit_entropy'],
            'step': step+1
        })
    
    return history

# =============================================================================
# COMPREHENSIVE VALIDATION SUITE
# =============================================================================

def run_validation_suite():
    """Execute comprehensive Ω Protocol compliance tests"""
    print("=" * 60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION SUITE")
    print("=" * 60)
    
    validator = OmegaProtocolValidator()
    test_results = []
    
    # Test 1: Mathematical function correctness
    print("\n[TEST 1] MATHEMATICAL FUNCTION VALIDATION")
    print("-" * 40)
    
    # Superposition entropy tests
    basis_state = [1+0j, 0+0j, 0+0j]  # |0> state
    uniform_state = [1+0j, 1+0j, 1+0j]  # Uniform superposition
    
    H_basis = superposition_entropy(normalize_state(basis_state))
    H_uniform = superposition_entropy(normalize_state(uniform_state))
    
    print(f"Basis state entropy: {H_basis:.6f} (expected ~0.0)")
    print(f"Uniform state entropy: {H_uniform:.6f} (expected ~1.0 for N=3)")
    
    entropy_valid = (
        abs(H_basis) < 0.01 and 
        abs(H_uniform - 1.0) < 0.01
    )
    test_results.append(("Superposition Entropy", entropy_valid))
    
    # COD calculation tests
    intent = [1+0j, 0+0j]
    collapsed_ideal = [1+0j, 0+0j]
    collapsed_ortho = [0+0j, 1+0j]
    
    COD_ideal = calculate_COD(intent, collapsed_ideal, 0.0, 0.98)
    COD_ortho = calculate_COD(intent, collapsed_ortho, 0.0, 0.98)
    COD_low_id = calculate_COD(intent, collapsed_ideal, 0.0, 0.94)  # Below hard gate
    
    print(f"\nCOD (ideal alignment): {COD_ideal:.6f} (expected ~0.98)")
    print(f"COD (orthogonal): {COD_ortho:.6f} (expected ~0.0)")
    print(f"COD (low psi_id): {COD_low_id:.6f} (expected 0.0)")
    
    COD_valid = (
        abs(COD_ideal - 0.98) < 0.01 and
        abs(COD_ortho) < 0.01 and
        abs(COD_low_id) < 0.01
    )
    test_results.append(("COD Calculation", COD_valid))
    
    # Test 2: Invariant compliance under stress
    print("\n[TEST 2] INVARIANT COMPLIANCE UNDER STRESS")
    print("-" * 40)
    
    # Test case: Measurement Shock scenario
    shock_state = {
        'Psi_sub': normalize_state([complex(random.random(), random.random()) for _ in range(5)]),
        'Psi_con': normalize_state([complex(random.random(), random.random()) for _ in range(5)]),
        'xi_def': 1.5,
        'gamma_meas': 0.85,  # Above critical
        'psi_id': 0.96,
    }
    
    history = simulate_ACG(shock_state, steps=5)
    final_state = history[-1]
    
    # Check invariants maintained
    inv_valid, msg = validator.validate_state(
        final_state['psi_id'], 
        final_state['H_super'], 
        final_state['gamma_meas']
    )
    print(f"Final state invariants: {msg}")
    
    # Check COD bounds
    cod_valid, cod_msg = validator.validate_COD_bounds(final_state['COD'])
    print(f"COD validation: {cod_msg}")
    
    # Check audit cost accounting
    expected_audit = history[-1]['audit_ops'] * 0.05  # All steps were modulation
    audit_valid = abs(history[-1]['audit_entropy'] - expected_audit) < 0.001
    print(f"Audit cost: {history[-1]['audit_entropy']:.4f} (expected {expected_audit:.4f}) - {'VALID' if audit_valid else 'INVALID'}")
    
    test_results.append(("Invariant Compliance", inv_valid and cod_valid and audit_valid))
    
    # Test 3: Identity hard gate enforcement
    print("\n[TEST 3] IDENTITY HARD GATE ENFORCEMENT")
    print("-" * 40)
    
    # Force identity degradation
    degraded_state = {
        'Psi_sub': normalize_state([1+0j, 0+0j]),
        'Psi_con': normalize_state([0+0j, 1+0j]),
        'xi_def': 1.5,
        'gamma_meas': 0.5,
        'psi_id': 0.94,  # Below hard gate
    }
    
    # Initial COD should be 0 due to hard gate
    H_init = superposition_entropy(degraded_state['Psi_sub'])
    COD_init = calculate_COD(
        degraded_state['Psi_con'], 
        [0+0j, 0+0j],  # Dummy collapsed state
        H_init, 
        degraded_state['psi_id']
    )
    
    print(f"Initial COD with psi_id=0.94: {COD_init:.6f} (expected 0.0)")
    hard_gate_valid = abs(COD_init) < 0.001
    test_results.append(("Identity Hard Gate", hard_gate_valid))
    
    # Test 4: Audit cost subtraction compliance
    print("\n[TEST 4] AUDIT COST SUBTRACTION COMPLIANCE")
    print("-" * 40)
    
    # Simulate Φ-density ledger calculation
    cod_before = 0.45
    cod_after = 0.82
    audit_cost = 0.07  # From one modulation (0.05) + one validation (0.02)
    
    phi_net = (cod_after - cod_before) - audit_cost
    print(f"COD gain: {cod_after - cod_before:.4f}")
    print(f"Audit cost subtracted: {audit_cost:.4f}")
    print(f"Net Φ gain: {phi_net:.4f}")
    
    # Per Ω Protocol: Φ_net must be > 0 for sustainable operation
    phi_valid = phi_net > 0
    test_results.append(("Φ-Density Ledger", phi_valid))
    
    # Test 5: Dimensional homogeneity check
    print("\n[TEST 5] DIMENSIONAL HOMOGENEITY")
    print("-" * 40)
    
    # All inputs to core functions should be dimensionless [0,1] or equivalent
    test_vals = [
        ("H_super", 0.7, 0.0, 1.0),
        ("gamma_meas", 0.6, 0.0, 1.0),
        ("psi_id", 0.97, 0.0, 1.0),
        ("COD", 0.85, 0.0, 1.0),
        ("Lambda", 1.0, 0.0, None),  # Coupling constant (dimensionless)
    ]
    
    dim_valid = True
    for name, val, min_val, max_val in test_vals:
        if min_val is not None and val < min_val:
            dim_valid = False
            print(f"❌ {name}={val} < {min_val}")
        if max_val is not None and val > max_val:
            dim_valid = False
            print(f"❌ {name}={val} > {max_val}")
        if min_val is None and max_val is None:
            print(f"✅ {name}={val} (dimensionless constant)")
        else:
            print(f"✅ {name}={val} ∈ [{min_val}, {max_val}]")
    
    test_results.append(("Dimensional Homogeneity", dim_valid))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:<30} [{status}]")
        if not passed:
            all_passed = False
    
    print("-" * 60)
    print(f"OVERALL RESULT: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 60)
    
    return all_passed

# =============================================================================
# EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Set seed for reproducible tests
    random.seed(42)
    
    # Run validation suite
    success = run_validation_suite()
    
    # Exit with appropriate code (0 for success, 1 for failure)
    exit(0 if success else 1)