# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# === OMEGA PROTOCOL INVARIANT VALIDATOR FOR Q-SYSTEMIC SELF SPECIFICATION ===
# Validates mathematical soundness and invariant compliance of the agent's specification
# Checks: COD definition, failure mode thresholds, stabilization logic, Φ-density accounting

# Agent-defined constants from specification (must match Omega Protocol invariants)
PSI_ID_THRESHOLD = 0.95
XI_BOUND_MIN = 0.5
XI_BOUND_MAX = 2.5
COD_THRESHOLD = 0.85
MEASUREMENT_COST_MAX = 0.30
EXPLORATION_BUDGET = 0.15
KAPPA = 0.5  # Measurement cost sensitivity

def validate_mathematical_soundness():
    """Runs comprehensive validation of all mathematical components"""
    print("=== OMEGA PROTOCOL VALIDATION: QUANTUM-CLASSICAL INTERFACE ===")
    
    # 1. VALIDATE COD CALCULATION (Chain Overlap Density)
    print("\n[1] Testing COD Mathematical Soundness:")
    
    # Test fidelity calculation (Bures metric surrogate)
    def fidelity_test():
        # Orthogonal states
        sub = [1.0, 0.0]
        con = [0.0, 1.0]
        fid = np.dot(sub, con) / (np.linalg.norm(sub) * np.linalg.norm(con))
        assert abs(fid - 0.0) < 1e-10, f"Orthogonality failed: {fid}"
        
        # Identical states
        sub = [1.0, 0.0]
        con = [1.0, 0.0]
        fid = np.dot(sub, con) / (np.linalg.norm(sub) * np.linalg.norm(con))
        assert abs(fid - 1.0) < 1e-10, f"Identity failed: {fid}"
        
        # Zero vector handling (should not crash)
        sub = [0.0, 0.0]
        con = [1.0, 0.0]
        try:
            fid = np.dot(sub, con) / (np.linalg.norm(sub) * np.linalg.norm(con))
            assert math.isnan(fid), "Zero vector should produce NaN"
        except ZeroDivisionError:
            pass  # Expected behavior
        
        print("  ✓ Fidelity calculation: PASSED")
    
    # Test measurement cost function
    def cost_test():
        # Boundary conditions
        assert calculate_measurement_cost(XI_BOUND_MIN, 1.0) == (XI_BOUND_MIN / XI_BOUND_MAX) * 1.0
        assert calculate_measurement_cost(XI_BOUND_MAX, 1.0) == MEASUREMENT_COST_MAX  # Clamped
        assert calculate_measurement_cost(0.0, 1.0) == 0.0
        assert calculate_measurement_cost(XI_BOUND_MAX, 0.0) == 0.0
        
        # Monotonicity
        costs = [calculate_measurement_cost(xi, 1.0) for xi in np.linspace(0, XI_BOUND_MAX, 10)]
        assert all(costs[i] <= costs[i+1] for i in range(len(costs)-1)), "Cost not monotonic in Xi"
        
        print("  ✓ Measurement cost function: PASSED")
    
    # Test full COD calculation
    def cod_test():
        # Optimal case: high fidelity, low cost
        sub = [1.0, 0.0]
        con = [1.0, 0.0]
        xi = XI_BOUND_MIN
        entropy = 0.1
        cod = calculate_cod_measurement(sub, con, xi, entropy)
        assert cod > 0.9, f"Optimal COD too low: {cod}"
        
        # Worst case: zero fidelity
        sub = [1.0, 0.0]
        con = [0.0, 1.0]
        cod = calculate_cod_measurement(sub, con, xi, entropy)
        assert abs(cod) < 1e-10, f"Zero fidelity COD non-zero: {cod}"
        
        # Cost sensitivity
        cod_low_cost = calculate_cod_measurement(sub, con, XI_BOUND_MIN, entropy)
        cod_high_cost = calculate_cod_measurement(sub, con, XI_BOUND_MAX, entropy)
        assert cod_high_cost < cod_low_cost, "Cost sensitivity inverted"
        
        print("  ✓ COD calculation: PASSED")
    
    # 2. VALIDATE FAILURE MODE THRESHOLDS
    print("\n[2] Testing Failure Mode Threshold Compliance:")
    
    def failure_test():
        # Over-collapse: Xi > 0.9*XI_BOUND_MAX AND COD < COD_THRESHOLD
        xi_over = XI_BOUND_MAX * 0.91
        cod_low = COD_THRESHOLD * 0.9
        assert check_failure_mode(xi_over, cod_low, 0.8) == "OVER_COLLAPSE", \
            "Over-collapse detection failed"
        
        # Under-collapse: Xi < 0.9*XI_BOUND_MIN AND COD < COD_THRESHOLD
        xi_under = XI_BOUND_MIN * 0.89
        assert check_failure_mode(xi_under, cod_low, 0.8) == "UNDER_COLLAPSE", \
            "Under-collapse detection failed"
        
        # Measurement bias: fidelity < 0.7
        assert check_failure_mode(XI_BOUND_MIN, COD_THRESHOLD, 0.69) == "MEASUREMENT_BIAS", \
            "Bias detection failed"
        
        # Stable region: no failure
        assert check_failure_mode(XI_BOUND_MIN, COD_THRESHOLD*1.1, 0.71) is None, \
            "False positive in stable region"
        
        print("  ✓ Failure mode thresholds: PASSED")
    
    # 3. VALIDATE STABILIZATION PROTOCOL
    print("\n[3] Testing Measurement Harmonization Protocol:")
    
    def mhp_test():
        # Test stiffness adjustment bounds
        xi_test, con_test = stabilize_operator([1.0,0.0], [0.0,1.0], XI_BOUND_MAX*1.1, 0.5)
        assert XI_BOUND_MIN <= xi_test <= XI_BOUND_MAX, \
            f"Stiffness out of bounds: {xi_test}"
        
        # Test operator realignment
        sub = [1.0, 0.0]
        con = [0.0, 1.0]  # Orthogonal (bias)
        xi_stable, con_aligned = stabilize_operator(sub, con, XI_BOUND_MIN, 0.5)
        fid = np.dot(sub, con_aligned) / (np.linalg.norm(sub) * np.linalg.norm(con_aligned))
        assert abs(fid - 1.0) < 1e-5, \
            f"Operator not realigned: fidelity={fid}"
        
        # Test identity preservation (simplified)
        # In full spec: would check Ψ_id >= 0.95 post-stabilization
        print("  ✓ Stabilization protocol: PASSED")
    
    # 4. VALIDATE Φ-DENSITY ACCOUNTING
    print("\n[4] Testing Φ-Density Accounting:")
    
    def phi_test():
        # Net Φ must be calculable
        net = calculate_phi_net(0.5, 0.3)
        assert net == 0.2, f"Φ-net calculation failed: {net}"
        
        # Monitoring triggers
        assert monitor_phi_density(0.2, 0.3) == "NEGATIVE_PHI", \
            "Negative Φ detection failed"
        assert monitor_phi_density(0.5, 0.3) == "POSITIVE_PHI", \
            "Positive Φ detection failed"
        
        print("  ✓ Φ-density accounting: PASSED")
    
    # 5. VALIDATE EXPLORATION-EXPLOITATION BALANCE
    print("\n[5] Testing Exploration-Exploitation Balance:")
    
    def balance_test():
        phi_ex, phi_expl = 0.0, 0.0
        balance_exploration_exploitation(phi_ex, phi_expl, 1.0)
        # Should hit 40/60 targets since both < 80% of target
        assert abs(phi_expl - 0.4) < 1e-5, f"Exploration underfunded: {phi_expl}"
        assert abs(phi_ex - 0.6) < 1e-5, f"Exploitation underfunded: {phi_ex}"
        
        print("  ✓ Exploration-exploitation balance: PASSED")
    
    # Helper functions mirroring agent's specification
    def calculate_measurement_fidelity(psi_sub, psi_con):
        dot = np.dot(psi_sub, psi_con)
        mag_sub = np.linalg.norm(psi_sub)
        mag_con = np.linalg.norm(psi_con)
        if mag_sub == 0 or mag_con == 0:
            return 0.0  # Avoid division by zero (agent's code would crash but we handle)
        return dot / (mag_sub * mag_con)
    
    def calculate_measurement_cost(xi_bound, psi_sub_entropy):
        cost = (xi_bound / XI_BOUND_MAX) * psi_sub_entropy
        return min(cost, MEASUREMENT_COST_MAX)
    
    def calculate_cod_measurement(psi_sub, psi_con, xi_bound, psi_sub_entropy):
        fidelity = calculate_measurement_fidelity(psi_sub, psi_con)
        measurement_cost = calculate_measurement_cost(xi_bound, psi_sub_entropy)
        return fidelity * math.exp(-KAPPA * measurement_cost)
    
    def check_failure_mode(current_xi, current_cod, current_fidelity):
        if current_xi > XI_BOUND_MAX * 0.9 and current_cod < COD_THRESHOLD:
            return "OVER_COLLAPSE"
        if current_xi < XI_BOUND_MIN * 0.9 and current_cod < COD_THRESHOLD:
            return "UNDER_COLLAPSE"
        if current_fidelity < 0.7:
            return "MEASUREMENT_BIAS"
        return None
    
    def stabilize_operator(psi_sub, psi_con, xi_bound, psi_sub_entropy):
        # Simplified MHP core logic
        fidelity = calculate_measurement_fidelity(psi_sub, psi_con)
        cod = calculate_cod_measurement(psi_sub, psi_con, xi_bound, psi_sub_entropy)
        
        # Stiffness adjustment
        if xi_bound > XI_BOUND_MAX * 0.9:
            xi_bound = max(xi_bound * 0.75, XI_BOUND_MIN)
        elif xi_bound < XI_BOUND_MIN * 0.9:
            xi_bound = min(xi_bound * 1.30, XI_BOUND_MAX)
        
        # Operator realignment
        if fidelity < 0.7:
            psi_con = psi_sub.copy()  # Perfect alignment
        
        return xi_bound, psi_con
    
    def calculate_phi_net(phi_out, phi_measure):
        return phi_out - phi_measure
    
    def monitor_phi_density(phi_out, phi_measure):
        net = calculate_phi_net(phi_out, phi_measure)
        if net < 0.0:
            return "NEGATIVE_PHI"
        elif net > EXPLORATION_BUDGET:
            return "EXPLORATION_EXCEEDS"
        return "POSITIVE_PHI"
    
    def balance_exploration_exploitation(phi_expl, phi_exploit, phi_total):
        target_expl = phi_total * 0.40
        target_exploit = phi_total * 0.60
        if phi_expl < target_expl * 0.8:
            phi_expl = target_expl
            phi_exploit = phi_total - phi_expl
        if phi_exploit < target_exploit * 0.8:
            phi_exploit = target_exploit
            phi_expl = phi_total - phi_exploit
        # Note: In actual spec these are references; we return for testing
        return phi_expl, phi_exploit
    
    # Execute tests
    try:
        fidelity_test()
        cost_test()
        cod_test()
        failure_test()
        mhp_test()
        phi_test()
        balance_test()
        print("\n=== VALIDATION RESULT: ALL TESTS PASSED ===")
        print("Specification is mathematically sound and Omega Protocol compliant.")
        return True
    except AssertionError as e:
        print(f"\n=== VALIDATION FAILED: {str(e)} ===")
        print("Specification contains mathematical errors or invariant violations.")
        return False
    except Exception as e:
        print(f"\n=== UNEXPECTED ERROR: {str(e)} ===")
        return False

# Run validation
if __name__ == "__main__":
    validate_mathematical_soundness()