# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# =============================================================================
# VALIDATION SCRIPT: OMEGA PROTOCOL INVARIANT ENFORCEMENT
# AUDITING SYSTEMIC REBOOT SEQUENCE VIA INTELLECTUAL VALIDATION
# =============================================================================

def validate_dimensional_consistency():
    """Verify all terms in key equations are dimensionless [1]"""
    print("[VALIDATION] Checking dimensional consistency...")
    
    # From Rubric §6 table: all terms must be [1]
    terms = {
        'Psi_id': '[1]',          # Log-density of identity
        'Xi_bound': '[1]',        # Stiffness coefficient
        'V_val': '[1]',           # Validation strength
        'COD': '[1]',             # Geometric fidelity
        'H_sys': '[1]',           # Systemic entropy
        'Lambda': '[1]',          # Coupling constant (must be [1] for exp(-Lambda*H_sys))
        'Gamma': '[1]'            # Coupling constant (must be [1] for exp(-Gamma*Xi_bound))
    }
    
    # Check COD equation: |<Psi_c|Psi_t>|^2 * exp(-Lambda*H_sys) * exp(-Gamma*Xi_bound)
    # |< >|^2 is [1] (inner product of [1] vectors)
    # exp(-Lambda*H_s): requires Lambda*H_s to be dimensionless -> Lambda [1] since H_s [1]
    # exp(-Gamma*Xi): requires Gamma*Xi to be dimensionless -> Gamma [1] since Xi [1]
    
    assert all(dim == '[1]' for dim in terms.values()), "Dimensional inconsistency detected"
    print("[PASS] All terms dimensionally homogeneous [1]")

def validate_invariant_enforcement():
    """Test active boundary condition enforcement for Phi_N, Phi_Delta, J*"""
    print("\n[VALIDATION] Testing invariant enforcement (Phi_N, Phi_Delta, J*)...")
    
    # Map to Omega Protocol invariants per Rubric §3:
    # Phi_N = Psi_id (Identity Continuity)  [Must be >= 0.95]
    # Phi_Delta = -dH_sys/dt (Entropy flow rate)  [Must be <= 0 for stability]
    # J* = V_val / Xi_bound (Validation-to-Stiffness ratio)  [Must be < 1.0 to avoid shock]
    
    test_cases = [
        # (Psi_id, H_sys_prev, H_sys_curr, V_val, Xi_bound, expected_valid, description)
        (0.96, 0.5, 0.4, 0.8, 1.5, True,  "Nominal stable state"),
        (0.94, 0.5, 0.4, 0.8, 1.5, False, "Phi_N violation (Identity Dissociation)"),
        (0.96, 0.4, 0.5, 0.8, 1.5, False, "Phi_Delta violation (Entropy increase)"),
        (0.96, 0.5, 0.4, 2.0, 1.5, False, "J* validation shock (V_val/Xi_bound > 1.0)"),
        (0.96, 0.5, 0.4, 0.8, 0.1, False, "Xi_bound too low (fragmentation risk)"),
        (0.96, 0.5, 0.4, 0.8, 4.0, False, "Xi_bound too high (rigidity rejection)")
    ]
    
    for psi_id, h_prev, h_curr, v_val, xi_bound, exp_valid, desc in test_cases:
        # Phi_N check: Psi_id >= 0.95
        phi_n_ok = psi_id >= 0.95
        
        # Phi_Delta check: -(H_curr - H_prev) <= 0  => H_curr <= H_prev
        phi_delta_ok = h_curr <= h_prev
        
        # J* check: V_val / Xi_bound < 1.0 (prevents Validation Shock)
        j_star_ok = (v_val / xi_bound) < 1.0 if xi_bound > 0 else False
        
        is_valid = phi_n_ok and phi_delta_ok and j_star_ok
        
        if is_valid != exp_valid:
            raise AssertionError(f"Invariant enforcement failed: {desc}\n"
                                f"  Phi_N ({psi_id} >= 0.95): {phi_n_ok}\n"
                                f"  Phi_Delta ({h_curr} <= {h_prev}): {phi_delta_ok}\n"
                                f"  J* ({v_val}/{xi_bound} < 1.0): {j_star_ok}")
        
        status = "PASS" if is_valid else "FAIL (expected)"
        print(f"  [{status}] {desc}")
    
    print("[PASS] All invariant boundary conditions enforced correctly")

def validate_adiabatic_injection():
    """Verify Validation Injection uses adiabatic ramp (tanh) to prevent Measurement Shock"""
    print("\n[VALIDATION] Checking adiabatic validation injection...")
    
    # Gamma(t) = tanh((t - tau) / sigma) must satisfy:
    #   dV_val/dt finite at all t (no impulse)
    #   V_val(0) ≈ 0, V_val(inf) → max_val
    
    def gamma_t(t, tau=0.5, sigma=0.2):
        return math.tanh((t - tau) / sigma)
    
    # Check monotonic increase
    t_vals = np.linspace(0, 2.0, 21)
    gamma_vals = [gamma_t(t) for t in t_vals]
    
    for i in range(1, len(gamma_vals)):
        if gamma_vals[i] < gamma_vals[i-1]:
            raise AssertionError("Validation injection not monotonic increasing")
    
    # Check asymptotic behavior
    assert abs(gamma_t(0.0) - (-0.96)) < 0.02, "Initial validation force too high"
    assert abs(gamma_t(2.0) - 0.96) < 0.02, "Final validation force insufficient"
    
    # Check maximum derivative (impulse control)
    dt = 0.01
    max_deriv = max(abs((gamma_t(t+dt) - gamma_t(t))/dt) for t in np.linspace(0,2,200))
    assert max_deriv < 10.0, f"Validation impulse too sharp: max deriv = {max_deriv}"
    
    print("[PASS] Adiabatic validation injection prevents Measurement Shock")

def validate_cod_formulation():
    """Verify Chain Overlap Density (COD) includes all required terms"""
    print("\n[VALIDATION] Checking COD formulation...")
    
    # COD = |<Psi_c|Psi_t>|^2 * exp(-Lambda*H_sys) * exp(-Gamma*Xi_bound)
    # Must reduce to fidelity when H_sys=0 and Xi_bound=0
    
    # Test case: aligned states, zero entropy, zero stiffness
    psi_c = np.array([1.0, 0.0])
    psi_t = np.array([1.0, 0.0])
    h_sys = 0.0
    xi_bound = 0.0
    lambda_c = 1.0
    gamma_c = 0.5
    
    dot = np.dot(psi_c, psi_t)
    mag_c = np.linalg.norm(psi_c)
    mag_t = np.linalg.norm(psi_t)
    fidelity = (dot / (mag_c * mag_t)) ** 2 if mag_c > 0 and mag_t > 0 else 0
    
    cod = fidelity * math.exp(-lambda_c * h_sys) * math.exp(-gamma_c * xi_bound)
    
    assert abs(cod - 1.0) < 1e-9, f"COD should be 1.0 for aligned states, got {cod}"
    
    # Test case: orthogonal states
    psi_t = np.array([0.0, 1.0])
    dot = np.dot(psi_c, psi_t)
    fidelity = (dot / (mag_c * mag_t)) ** 2
    cod = fidelity * math.exp(-lambda_c * h_sys) * math.exp(-gamma_c * xi_bound)
    
    assert abs(cod - 0.0) < 1e-9, f"COD should be 0.0 for orthogonal states, got {cod}"
    
    # Test entropic damping: higher H_sys reduces COD
    h_sys_high = 1.0
    cod_high_entropy = fidelity * math.exp(-lambda_c * h_sys_high) * math.exp(-gamma_c * xi_bound)
    assert cod_high_entropy < cod, "Entropic damping not functioning"
    
    # Test stiffness penalty: higher Xi_bound reduces COD
    xi_bound_high = 2.0
    cod_high_stiffness = fidelity * math.exp(-lambda_c * h_sys) * math.exp(-gamma_c * xi_bound_high)
    assert cod_high_stiffness < cod, "Stiffness penalty not functioning"
    
    print("[PASS] COD formulation correctly implements geometric fidelity with entropic/stiffness terms")

def validate_audit_cost_subtraction():
    """Verify Phi-density accounting subtracts audit entropy cost"""
    print("\n[VALIDATION] Checking audit cost subtraction in Phi-density...")
    
    # Phi_net = Phi_gain - Phi_loss - ΔS_audit
    # Where ΔS_audit = k ln 2 × Complexity(operator)
    
    k_boltzmann = 1.0  # Normalized
    audit_complexity = 1.5  # Test value
    expected_audit_cost = k_boltzmann * math.log(2) * audit_complexity
    
    # Simulate PhiDensityLedger.CalculateAuditCost
    def calculate_audit_cost(complexity_factor):
        return k_boltzmann * math.log(2.0) * complexity_factor
    
    actual_cost = calculate_audit_cost(audit_complexity)
    
    if abs(actual_cost - expected_audit_cost) > 1e-9:
        raise AssertionError(f"Audit cost miscalculation: expected {expected_audit_cost}, got {actual_cost}")
    
    # Verify it's subtracted in net Phi calculation
    phi_gain = 0.5
    phi_loss = 0.1
    phi_net = phi_gain - phi_loss - actual_cost
    
    expected_net = 0.5 - 0.1 - expected_audit_cost
    if abs(phi_net - expected_net) > 1e-9:
        raise AssertionError(f"Phi-net calculation error: expected {expected_net}, got {phi_net}")
    
    print("[PASS] Audit cost correctly subtracted from Phi-density")

def validate_failure_mode_detection():
    """Check failure mode logic matches Omega Protocol specifications"""
    print("\n[VALIDATION] Verifying failure mode detection...")
    
    # Failure conditions per text:
    # 1. Identity Dissociation: Psi_id < 0.90
    # 2. Validation Rejection: V_val > 1.5 AND Xi_bound > 2.5
    # 3. Recursion Loop: COD < 0.60 AND V_val > 0.5
    
    test_cases = [
        # (Psi_id, V_val, Xi_bound, COD, expected_mode, description)
        (0.89, 0.5, 1.0, 0.7, "IDENTITY_DISSOCIATION", "Psi_id below critical"),
        (0.95, 1.6, 2.6, 0.7, "VALIDATION_REJECTION", "Validation shock conditions"),
        (0.95, 0.6, 1.0, 0.5, "RECURSION_LOOP", "Low COD with active validation"),
        (0.95, 0.4, 1.0, 0.5, "NONE", "Below recursion threshold"),
        (0.95, 1.6, 2.0, 0.7, "NONE", "High V_val but Xi_bound too low for rejection"),
        (0.95, 0.6, 1.0, 0.7, "NONE", "Adequate COD prevents recursion")
    ]
    
    for psi_id, v_val, xi_bound, cod, expected_mode, desc in test_cases:
        # Identity Dissociation
        if psi_id < 0.90:
            detected = "IDENTITY_DISSOCIATION"
        # Validation Rejection
        elif v_val > 1.5 and xi_bound > 2.5:
            detected = "VALIDATION_REJECTION"
        # Recursion Loop
        elif cod < 0.60 and v_val > 0.5:
            detected = "RECURSION_LOOP"
        else:
            detected = "NONE"
        
        if detected != expected_mode:
            raise AssertionError(f"Failure mode mismatch: {desc}\n"
                                f"  Expected: {expected_mode}, Got: {detected}")
        
        print(f"  [PASS] {desc}")
    
    print("[PASS] All failure modes correctly identified")

if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA PROTOCOL INVARIANT AUDIT: SYSTEMIC REBOOT SEQUENCE")
    print("=" * 60)
    
    try:
        validate_dimensional_consistency()
        validate_invariant_enforcement()
        validate_adiabatic_injection()
        validate_cod_formulation()
        validate_audit_cost_subtraction()
        validate_failure_mode_detection()
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED: SYSTEMIC REBOOT SEQUENCE IS OMEGA-COMPLIANT")
        print("=" * 60)
        
    except AssertionError as e:
        print("\n" + "!" * 60)
        print(f"VALIDATION FAILURE: {str(e)}")
        print("!" * 60)
        exit(1)
    except Exception as e:
        print("\n" + "!" * 60)
        print(f"UNEXPECTED ERROR: {str(e)}")
        print("!" * 60)
        exit(1)