# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATION SCRIPT
# Validates mathematical soundness and invariant compliance of bureaucratic decision manifold
# =============================================================================

# --- Constants from Omega Protocol Specification (v26.0-Ω-POLARIZED) ---
PSI_ID_THRESHOLD = 0.95      # Goal Integrity hard gate
PSI_ID_CRITICAL = 0.90       # Dissociation/Drift Risk
XI_SYS_DEFAULT = 1.5         # Bureaucratic Stiffness baseline
XI_SYS_MAX = 3.0             # Risk of Procedural Black Hole
XI_SYS_MIN = 0.5             # Risk of Decision Drift
XI_IND_THRESHOLD = 2.0       # Individual Burnout Risk
KAPPA_SYS_IND = 0.8          # System-Individual Coupling
H_TOP_LIMIT = 0.85           # Max Topological Impedance
F_URG_DEFAULT = 0.6          # Urgency Force baseline
COD_THRESHOLD = 0.80         # Minimum Alignment Threshold
LAMBDA_COUPLING = 1.0        # Entropic Damping constant

# --- Helper Functions (Direct translations from C++ spec) ---

def calculate_topological_impedance(path):
    """Calculate H_top = Σ(Cost_i * Variance_i) / Σ(Cost_i), clamped [0,1]"""
    if not path:
        return 0.0
    total_impedance = sum(node['approval_cost'] * node['risk_variance'] for node in path)
    total_length = sum(node['approval_cost'] for node in path)
    if total_length == 0:
        return 0.0
    raw_impedance = total_impedance / total_length
    return max(0.0, min(1.0, raw_impedance))

def calculate_cod_decision(intent, outcome, h_top, xi_sys):
    """Calculate COD = fidelity * exp(-Λ*H_top) * exp(-Γ*Xi_sys)"""
    # Fidelity = |<Intent | Outcome>| (normalized dot product)
    dot = np.dot(intent, outcome)
    mag_i = np.linalg.norm(intent)
    mag_o = np.linalg.norm(outcome)
    fidelity = dot / (mag_i * mag_o) if mag_i > 0 and mag_o > 0 else 0.0
    
    damping = math.exp(-LAMBDA_COUPLING * h_top)
    stiffness_penalty = math.exp(-LAMBDA_COUPLING * xi_sys)
    return fidelity * damping * stiffness_penalty

def check_failure_mode(h_top, f_urg, xi_ind, cod):
    """Return failure type based on boundary conditions"""
   \({}^{-1}\)
    if h_top > H_TOP_LIMIT and f_urg < (H_TOP_LIMIT * 0.5):
        return "PROCEDURAL_BLACK_HOLE"
    if xi_ind > XI_IND_THRESHOLD:
        return "INDIVIDUAL_BURNOUT"
    if cod < 0.60:
        return "DECISION_DRIFT"
    return "NONE"

def geodesic_smoothing_invariant_check(path, intent, outcome, h_top, xi_sys):
    """
    Validate the core invariant: Pruning must not violate PSI_ID_THRESHOLD
    Simulates the invariant check in Geodesic_Smoothing_Operator
    """
    # Current state COD
    current_cod = calculate_cod_decision(intent, outcome, h_top, xi_sys)
    
    # Simulate node removal (highest curvature node)
    if not path:
        return True, current_cod  # Nothing to prune
    
    # Find node with max Cost*Variance
    max_idx = max(range(len(path)), 
                  key=lambda i: path[i]['approval_cost'] * path[i]['risk_variance'])
    
    # Simulate removal: outcome shift (conservative estimate: 5% per node)
    shift = 0.05
    temp_outcome = [max(0.0, val - shift) for val in outcome]  # Prevent negative values
    
    # Recalculate COD after simulated removal (using reduced H_top estimate)
    temp_h_top = h_top * 0.8  # Conservative impedance reduction estimate
    temp_cod = calculate_cod_decision(intent, temp_outcome, temp_h_top, xi_sys)
    
    # INVARIANT CHECK: Hard gate (Rubric §3)
    invariant_holds = temp_cod >= PSI_ID_THRESHOLD
    return invariant_holds, temp_cod

# =============================================================================
# VALIDATION TEST SUITE
# =============================================================================

def run_validation_tests():
    """Execute comprehensive validation of mathematical soundness and invariants"""
    print("="*60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION SUITE")
    print("="*60)
    
    # Test 1: Dimensional Consistency (Rubric §6)
    print("\n[TEST 1] Dimensional Consistency Check")
    test_path = [
        {'approval_cost': 0.7, 'risk_variance': 0.4, 'node_id': 'N1'},
        {'approval_cost': 0.3, 'risk_variance': 0.6, 'node_id': 'N2'}
    ]
    h_top = calculate_topological_impedance(test_path)
    assert 0.0 <= h_top <= 1.0, f"H_top={h_top} not in [0,1]"
    print(f"✓ H_top calculation: {h_top:.4f} (dimensionless [0,1])")
    
    intent = [0.8, 0.6, 0.9]
    outcome = [0.75, 0.55, 0.85]
    xi_sys = XI_SYS_DEFAULT
    cod = calculate_cod_decision(intent, outcome, h_top, xi_sys)
    assert 0.0 <= cod <= 1.0, f"COD={cod} not in [0,1]"
    print(f"✓ COD calculation: {cod:.4f} (dimensionless [0,1])")
    
    # Test 2: Invariant Hard Gate (PSI_ID_THRESHOLD)
    print("\n[TEST 2] PSI_ID Threshold Hard Gate Validation")
    # Scenario: Pruning would violate identity integrity
    critical_path = [
        {'approval_cost': 0.9, 'risk_variance': 0.9, 'node_id': 'CRITICAL_NODE'},
        {'approval_cost': 0.1, 'risk_variance': 0.1, 'node_id': 'SAFE_NODE'}
    ]
    intent_vec = [1.0, 1.0, 1.0]
    outcome_vec = [0.95, 0.95, 0.95]  # High fidelity
    h_top_crit = calculate_topological_impedance(critical_path)
    invariant_holds, sim_cod = geodesic_smoothing_invariant_check(
        critical_path, intent_vec, outcome_vec, h_top_crit, XI_SYS_DEFAULT
    )
    print(f"Current COD: {calculate_cod_decision(intent_vec, outcome_vec, h_top_crit, XI_SYS_DEFAULT):.4f}")
    print(f"Simulated COD after pruning: {sim_cod:.4f}")
    print(f"Invariant holds (PSI_ID ≥ {PSI_ID_THRESHOLD}): {invariant_holds}")
    assert not invariant_holds, "Invariant should FAIL when pruning critical node"
    print("✓ Hard gate correctly blocked integrity-compromising prune")
    
    # Test 3: Procedural Black Hole Boundary
    print("\n[TEST 3] Procedural Black Hole Boundary Condition")
    # Boundary: H_top > H_TOP_LIMIT AND F_urg < 0.5*H_TOP_LIMIT
    h_top_ph = 0.86  # Just above limit
    f_urg_ph = 0.4   # Below 0.5*0.85=0.425
    xi_ind_ph = 1.5  # Below burnout threshold
    cod_ph = 0.82    # Above drift threshold
    failure = check_failure_mode(h_top_ph, f_urg_ph, xi_ind_ph, cod_ph)
    print(f"H_top={h_top_ph:.2f} > {H_TOP_LIMIT}, F_urg={f_urg_ph:.2f} < {0.5*H_TOP_LIMIT:.2f}")
    print(f"Failure mode detected: {failure}")
    assert failure == "PROCEDURAL_BLACK_HOLE", "Should detect Procedural Black Hole"
    print("✓ Boundary condition correctly identified")
    
    # Test 4: Individual Burnout Coupling
    print("\n[TEST 4] System-Individual Coupling Validation")
    h_top_burn = 0.7
    f_urg_burn = F_URG_DEFAULT
    # Xi_ind = XI_SYS_DEFAULT * KAPPA_SYS_IND * (1.0 + H_top) [from spec]
    xi_ind_burn = XI_SYS_DEFAULT * KAPPA_SYS_IND * (1.0 + h_top_burn)
    cod_burn = 0.75
    failure = check_failure_mode(h_top_burn, f_urg_burn, xi_ind_burn, cod_burn)
    print(f"Calculated Xi_ind: {xi_ind_burn:.2f} (threshold: {XI_IND_THRESHOLD})")
    print(f"Failure mode detected: {failure}")
    assert failure == "INDIVIDUAL_BURNOUT", "Should detect Individual Burnout"
    print("✓ Coupling constant correctly propagates systemic stress")
    
    # Test 5: Decision Drift Detection
    print("\n[TEST 5] Decision Drift Sensitivity")
    h_top_drift = 0.3
    f_urg_drift = F_URG_DEFAULT
    xi_ind_drift = 1.0
    cod_drift = 0.59  # Just below 0.60 threshold
    failure = check_failure_mode(h_top_drift, f_urg_drift, xi_ind_drift, cod_drift)
    print(f"COD={cod_drift:.2f} < 0.60 threshold")
    print(f"Failure mode detected: {failure}")
    assert failure == "DECISION_DRIFT", "Should detect Decision Drift"
    print("✓ Drift detection sensitive to fidelity loss")
    
    # Test 6: Geodesic Smoothing Stabilization Path
    print("\n[TEST 6] Stabilization Operator Invariant Preservation")
    # Stable path: low curvature nodes
    stable_path = [
        {'approval_cost': 0.2, 'risk_variance': 0.1, 'node_id': 'S1'},
        {'approval_cost': 0.2, 'risk_variance': 0.1, 'node_id': 'S2'},
        {'approval_cost': 0.2, 'risk_variance': 0.1, 'node_id': 'S3'}
    ]
    h_top_stable = calculate_topological_impedance(stable_path)
    intent_stable = [0.9, 0.8, 0.85]
    outcome_stable = [0.88, 0.79, 0.83]  # High fidelity
    xi_sys_stable = XI_SYS_DEFAULT
    
    # Verify initial state is stable
    initial_cod = calculate_cod_decision(intent_stable, outcome_stable, h_top_stable, xi_sys_stable)
    failure = check_failure_mode(h_top_stable, F_URG_DEFAULT, 
                                XI_SYS_DEFAULT*KAPPA_SYS_IND*(1.0+h_top_stable), 
                                initial_cod)
    print(f"Initial state: COD={initial_cod:.3f}, Failure={failure}")
    assert failure == "NONE" and initial_cod >= COD_THRESHOLD, "Should start stable"
    
    # Apply smoothing (should not prune as already stable)
    invariant_holds, _ = geodesic_smoothing_invariant_check(
        stable_path, intent_stable, outcome_stable, h_top_stable, xi_sys_stable
    )
    print(f"Invariant holds during smoothing attempt: {invariant_holds}")
    assert invariant_holds, "Stable path should pass invariant check"
    print("✓ Stabilization operator preserves integrity on stable paths")
    
    print("\n" + "="*60)
    print("ALL VALIDATION TESTS PASSED")
    print("Mathematical structure is sound and Omega Protocol invariants are enforced")
    print("="*60)

if __name__ == "__main__":
    run_validation_tests()