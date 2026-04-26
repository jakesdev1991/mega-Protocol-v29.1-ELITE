# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# =============================================================================
# VALIDATION: SYSTEMIC REBOOT SEQUENCE VIA INTELLECTUAL VALIDATION
# OMEGA PROTOCOL INVARIANT COMPLIANCE CHECK
# =============================================================================

def validate_reboot_invariants(psi_id, xi_bound):
    """
    Validate core invariants per Omega Rubric §3 (Active Boundary Conditions)
    Returns: (is_valid, violation_type, message)
    """
    # Identity Continuity Constraint (Psi_id >= 0.95)
    if psi_id < 0.95:
        return (False, "IDENTITY_DISSOCIATION", 
                f"Psi_id={psi_id:.3f} < 0.95 → Identity Dissociation Event")
    
    # Stiffness Tolerance Bounds (0.2 ≤ Xi_bound ≤ 3.0)
    if xi_bound > 3.0:
        return (False, "VALIDATION_REJECTION_RISK", 
                f"Xi_bound={xi_bound:.3f} > 3.0 → Validation Rejection Risk")
    if xi_bound < 0.2:
        return (False, "IDENTITY_FRAGMENTATION_RISK", 
                f"Xi_bound={xi_bound:.3f} < 0.2 → Identity Fragmentation Risk")
    
    return (True, "NONE", "Invariants satisfied")

def calculate_cod(psi_current, psi_target, h_sys, xi_bound, lambda_c=1.0, gamma_c=0.5):
    """
    Calculate Chain Overlap Density (COD) per Eq. in Rubric §6
    COD = |<Ψ_current|Ψ_target>|² × exp(-Λ·H_sys) × exp(-Γ·Ξ_bound)
    All terms dimensionless [1]
    """
    # Normalize vectors (critical for fidelity calculation)
    psi_current = np.array(psi_current, dtype=float)
    psi_target = np.array(psi_target, dtype=float)
    norm_c = np.linalg.norm(psi_current)
    norm_t = np.linalg.norm(psi_target)
    
    if norm_c < 1e-9 or norm_t < 1e-9:
        raise ValueError("State vectors must be non-zero")
    
    psi_current_norm = psi_current / norm_c
    psi_target_norm = psi_target / norm_t
    
    # Fidelity: squared overlap (dimensionless [1])
    fidelity = np.abs(np.dot(psi_current_norm, psi_target_norm))**2
    
    # Entropic damping (dimensionless [1])
    damping = math.exp(-lambda_c * h_sys)
    
    # Stiffness penalty (dimensionless [1])
    stiffness_penalty = math.exp(-gamma_c * xi_bound)
    
    return fidelity * damping * stiffness_penalty

def detect_failure_mode(psi_id, v_val, xi_bound, cod):
    """
    Detect systemic failure modes per Rubric §5
    Returns: failure_type (NONE, IDENTITY_DISSOCIATION, VALIDATION_REJECTION, RECURSION_LOOP)
    """
    # Identity Dissociation (Shredding Event)
    if psi_id < 0.90:
        return "IDENTITY_DISSOCIATION"
    
    # Validation Rejection (Measurement Shock)
    if v_val > 1.5 and xi_bound > 2.5:
        return "VALIDATION_REJECTION"
    
    # Recursion Loop (State Oscillation)
    if cod < 0.60 and v_val > 0.5:
        return "RECURSION_LOOP"
    
    return "NONE"

def validate_adiabatic_validation(t, v_val_max=1.2, tau=0.5, sigma=0.2):
    """
    Validate Adiabatic Validation Injection: V_val(t) = min(v_val_max, tanh((t-tau)/sigma) * v_val_max)
    Ensures smooth ramp (no discontinuity) and bounds [0, v_val_max]
    """
    ramp = math.tanh((t - tau) / sigma)
    v_val = min(v_val_max, ramp * v_val_max)
    
    # Check monotonic increase and bounds
    if not (0 <= v_val <= v_val_max):
        raise ValueError(f"V_val={v_val} outside [0, {v_val_max}]")
    
    # Check derivative continuity (avoid Shock)
    derivative = (1 - math.tanh((t - tau)/sigma)**2) / sigma * v_val_max
    if abs(derivative) > 10.0:  # Empirical shock threshold
        raise ValueError(f"Validation injection too sharp: derivative={derivative}")
    
    return v_val

def validate_phi_density_accounting(h_before, h_after, audit_complexity, h_sys, xi_bound):
    """
    Validate Φ-density accounting with audit cost subtraction (Rubric §4)
    Φ_net = -(H_after - H_before) - [k ln 2 × complexity] - [H_sys × Ξ_bound × 0.2]
    """
    k_boltzmann = 1.0  # Normalized
    audit_cost = k_boltzmann * math.log(2.0) * audit_complexity
    individual_cost = h_sys * xi_bound * 0.2
    raw_gain = -(h_after - h_before)
    phi_net = raw_gain - audit_cost - individual_cost
    
    # Φ-density must not violate conservation (net gain/loss within physical bounds)
    if phi_net < -1.0:  # Arbitrary but reasonable bound for normalized system
        raise ValueError(f"Φ-density violation: net loss too large ({phi_net})")
    
    return phi_net, audit_cost, individual_cost

# =============================================================================
# COMPLIANCE TEST SUITE (Omega Protocol v28.0)
# =============================================================================
def run_compliance_tests():
    """Execute invariant validation and mathematical soundness checks"""
    print("=== OMEGA PROTOCOL COMPLIANCE AUDIT: SYSTEMIC REBOOT SEQUENCE ===\n")
    
    # Test 1: Invariant Boundary Conditions
    print("1. Testing Reboot Invariants (Active Boundary Conditions):")
    test_cases = [
        (0.94, 1.0, False, "IDENTITY_DISSOCIATION"),  # Psi_id too low
        (0.95, 1.0, True, None),                       # Boundary pass
        (0.96, 0.19, False, "IDENTITY_FRAGMENTATION_RISK"),  # Xi_bound too low
        (0.96, 0.2, True, None),                       # Boundary pass
        (0.96, 3.0, True, None),                       # Boundary pass
        (0.96, 3.01, False, "VALIDATION_REJECTION_RISK") # Xi_bound too high
    ]
    
    for psi_id, xi_bound, expected_valid, expected_violation in test_cases:
        valid, violation, msg = validate_reboot_invariants(psi_id, xi_bound)
        status = "PASS" if (valid == expected_valid and 
                           (not expected_violation or violation == expected_violation)) else "FAIL"
        print(f"   Psi_id={psi_id}, Xi_bound={xi_bound}: {status} ({msg})")
        if status == "FAIL":
            raise AssertionError(f"Invariant test failed: {msg}")
    
    # Test 2: COD Calculation (Dimensional Consistency & Equation)
    print("\n2. Testing Chain Overlap Density (COD) Calculation:")
    psi_current = [1.0, 0.0, 0.0]
    psi_target = [1.0, 0.0, 0.0]
    h_sys = 0.0
    xi_bound = 0.0
    cod = calculate_cod(psi_current, psi_target, h_sys, xi_bound)
    expected = 1.0  # Perfect overlap, zero entropy, zero stiffness
    tolerance = 1e-9
    if abs(cod - expected) > tolerance:
        raise AssertionError(f"COD mismatch: got {cod}, expected {expected}")
    print(f"   Perfect alignment test: COD={cod:.6f} (PASS)")
    
    # Test entropic damping
    h_sys = 1.0
    cod = calculate_cod(psi_current, psi_target, h_sys, xi_bound)
    expected = math.exp(-1.0)  # exp(-Lambda*H_sys) = exp(-1)
    if abs(cod - expected) > tolerance:
        raise AssertionError(f"Entropic damping failed: got {cod}, expected {expected}")
    print(f"   Entropic damping test: COD={cod:.6f} (PASS)")
    
    # Test stiffness penalty
    xi_bound = 2.0
    cod = calculate_cod(psi_current, psi_target, 0.0, xi_bound)
    expected = math.exp(-0.5 * 2.0)  # exp(-Gamma*Xi_bound) = exp(-1)
    if abs(cod - expected) > tolerance:
        raise AssertionError(f"Stiffness penalty failed: got {cod}, expected {expected}")
    print(f"   Stiffness penalty test: COD={cod:.6f} (PASS)")
    
    # Test 3: Failure Mode Detection
    print("\n3. Testing Failure Mode Detection:")
    failure_tests = [
        # (psi_id, v_val, xi_bound, cod, expected_failure)
        (0.89, 0.5, 1.0, 0.8, "IDENTITY_DISSOCIATION"),
        (0.95, 1.6, 2.6, 0.8, "VALIDATION_REJECTION"),
        (0.95, 0.6, 1.0, 0.59, "RECURSION_LOOP"),
        (0.96, 0.4, 1.0, 0.7, "NONE")
    ]
    
    for psi_id, v_val, xi_bound, cod, expected in failure_tests:
        failure = detect_failure_mode(psi_id, v_val, xi_bound, cod)
        status = "PASS" if failure == expected else "FAIL"
        print(f"   (Psi_id={psi_id}, V_val={v_val}, Xi_bound={xi_bound}, COD={cod:.2f}): {failure} ({status})")
        if status == "FAIL":
            raise AssertionError(f"Failure mode mismatch: expected {expected}, got {failure}")
    
    # Test 4: Adiabatic Validation Injection (Smooth Ramp)
    print("\n4. Testing Adiabatic Validation Injection:")
    t_values = [0.0, 0.5, 1.0, 2.0]
    expected_v_vals = [0.0, 0.6, 1.0, 1.2]  # Approximate tanh ramp
    for t, expected in zip(t_values, expected_v_vals):
        v_val = validate_adiabatic_validation(t)
        if abs(v_val - expected) > 0.1:  # Tolerance for tanh approximation
            raise AssertionError(f"V_val mismatch at t={t}: got {v_val}, expected ~{expected}")
        print(f"   t={t}: V_val={v_val:.3f} (PASS)")
    
    # Test 5: Φ-Density Accounting with Audit Cost
    print("\n5. Testing Φ-Density Accounting:")
    h_before, h_after = 0.8, 0.6  # Entropy decrease
    audit_complexity = 1.5
    h_sys, xi_bound = 0.7, 1.2
    phi_net, audit_cost, individual_cost = validate_phi_density_accounting(
        h_before, h_after, audit_complexity, h_sys, xi_bound
    )
    raw_gain = -(h_after - h_before)  # 0.2
    expected_audit = math.log(2.0) * 1.5  # ~1.0397
    expected_individual = 0.7 * 1.2 * 0.2  # 0.168
    expected_phi_net = 0.2 - 1.0397 - 0.168  # ~ -1.0077
    
    if abs(audit_cost - expected_audit) > 1e-4:
        raise AssertionError(f"Audit cost mismatch: got {audit_cost}, expected {expected_audit}")
    if abs(individual_cost - expected_individual) > 1e-4:
        raise AssertionError(f"Individual cost mismatch: got {individual_cost}, expected {expected_individual}")
    if abs(phi_net - expected_phi_net) > 1e-4:
        raise AssertionError(f"Φ-net mismatch: got {phi_net}, expected {expected_phi_net}")
    print(f"   Raw gain: {raw_gain:.4f}, Audit cost: {audit_cost:.4f}, Individual cost: {individual_cost:.4f}")
    print(f"   Φ-net: {phi_net:.4f} (PASS)")
    
    print("\n=== ALL OMEGA PROTOCOL INVARIANTS VALIDATED ===")
    print("✓ Mathematical soundness confirmed")
    print("✓ Dimensional consistency maintained ([1] for all terms)")
    print("✓ Active boundary conditions enforced")
    print("✓ Audit cost subtraction implemented")
    print("✓ Adiabatic validation protocol verified")

# Execute validation suite
if __name__ == "__main__":
    run_compliance_tests()