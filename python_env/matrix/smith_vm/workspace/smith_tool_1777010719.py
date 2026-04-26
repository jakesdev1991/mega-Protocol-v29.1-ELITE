# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATOR FOR QUANTUM-CLASSICAL COGNITIVE ARCHITECTURE
# =============================================================================
# Validates mathematical soundness and invariant compliance of the provided C++ implementation
# Focus: COD formula, entropy calculations, invariant boundaries, AMP operator logic
# =============================================================================

class OmegaProtocolValidator:
    def __init__(self):
        # Constants from C++ implementation (normalized to [1])
        self.LAMBDA = 1.0   # Entropic damping coupling
        self.GAMMA = 0.5    # Stiffness penalty coupling
        self.PSI_ID_MIN = 0.95   # Identity continuity threshold
        self.XI_MEAS_MAX = 3.0   # Measurement shock threshold
        self.XI_MEAS_MIN = 0.2   # Analysis paralysis threshold
        self.COD_THRESHOLD = 0.80 # Stability threshold
        
    def validate_cod_formula(self, psi_quantum, psi_classical, h_quantum, xi_meas):
        """
        Validates COD = |<ψ_q|ψ_c>|² * exp(-Λ·H) * exp(-Γ·Ξ)
        Checks: dimensionality, range [0,1], correct damping/penalty application
        """
        # Ensure inputs are numpy arrays for vector ops
        psi_q = np.array(psi_quantum, dtype=float)
        psi_c = np.array(psi_classical, dtype=float)
        
        # 1. Fidelity term: |<ψ_q|ψ_c>|²
        dot = np.dot(psi_q, psi_c)
        mag_q = np.linalg.norm(psi_q)
        mag_c = np.linalg.norm(psi_c)
        if mag_q < 1e-9 or mag_c < 1e-9:
            fidelity = 0.0
        else:
            fidelity = (dot / (mag_q * mag_c)) ** 2
        
        # 2. Entropic damping: exp(-Λ·H)
        damping = math.exp(-self.LAMBDA * h_quantum)
        
        # 3. Stiffness penalty: exp(-Γ·Ξ)
        penalty = math.exp(-self.GAMMA * xi_meas)
        
        cod = fidelity * damping * penalty
        
        # Validation checks
        assert 0.0 <= cod <= 1.0, f"COD out of bounds: {cod}"
        assert isinstance(cod, float), "COD must be scalar float"
        assert math.isfinite(cod), "COD must be finite"
        
        # Verify damping/penalty are in (0,1] for valid inputs
        assert 0.0 < damping <= 1.0, f"Damping invalid: {damping}"
        assert 0.0 < penalty <= 1.0, f"Penalty invalid: {penalty}"
        assert 0.0 <= fidelity <= 1.0, f"Fidelity invalid: {fidelity}"
        
        return cod
    
    def validate_invariants(self, psi_id, xi_meas):
        """
        Validates Omega Protocol invariants:
        - psi_id >= 0.95 (identity continuity)
        - xi_meas in [0.2, 3.0] for stable operation (warnings outside)
        """
        # Hard boundary: identity continuity
        if psi_id < self.PSI_ID_MIN:
            raise ValueError(f"IDENTITY DISSOCIATION: psi_id={psi_id} < {self.PSI_ID_MIN}")
        
        # Soft boundaries (logged as warnings in C++ but we track for audit)
        shock_risk = xi_meas > self.XI_MEAS_MAX
        paralysis_risk = xi_meas < self.XI_MEAS_MIN
        
        return {
            'psi_id_valid': psi_id >= self.PSI_ID_MIN,
            'xi_meas_shock_risk': shock_risk,
            'xi_meas_paralysis_risk': paralysis_risk,
            'stable_operation': (not shock_risk) and (not paralysis_risk)
        }
    
    def validate_amp_logic(self, initial_state, target_xi=1.0, lock_xi=2.0, t=0.5):
        """
        Validates AMP operator mathematical logic:
        1. Stiffness softening: xi_new = xi*(1-α) + target*xi*α
        2. Measurement injection: gamma = tanh((t-τ)/σ) * max_gamma
        3. State update: ψ_classical = 0.7*ψ_classical + 0.3*ψ_quantum
        4. Invariant preservation post-update
        """
        psi_q, psi_c, h_q, xi, psi_id = initial_state
        alpha = 0.1  # Softening rate
        tau, sigma = 0.5, 0.2  # Injection parameters
        max_gamma = 1.2
        
        # Phase 1: Stiffness softening
        xi_soft = xi * (1.0 - alpha) + target_xi * alpha
        assert 0.0 <= xi_soft <= xi, f"Stiffness softening failed: {xi} -> {xi_soft}"
        
        # Phase 2: Measurement injection
        ramp = math.tanh((t - tau) / sigma)
        gamma = min(max_gamma, ramp * max_gamma)
        assert 0.0 <= gamma <= max_gamma, f"Gamma out of range: {gamma}"
        
        # Phase 3: State update (simulate collapse)
        psi_c_new = 0.7 * np.array(psi_c) + 0.3 * np.array(psi_q)
        # Renormalize to preserve dimensionless [1] constraint
        psi_c_new = psi_c_new / np.linalg.norm(psi_c_new) if np.linalg.norm(psi_c_new) > 1e-9 else psi_c_new
        
        # Phase 4: Lock state (increase stiffness on new path)
        xi_locked = xi_soft * (1.0 - alpha) + lock_xi * alpha
        assert xi_locked >= xi_soft, f"Stiffness lock failed: {xi_soft} -> {xi_locked}"
        
        # Verify invariants hold post-update
        try:
            inv = self.validate_invariants(psi_id, xi_locked)
            assert inv['psi_id_valid'], "Identity continuity broken post-AMP"
        except ValueError as e:
            raise AssertionError(f"AMP violated invariants: {e}")
        
        return {
            'xi_softened': xi_soft,
            'gamma_injected': gamma,
            'psi_classical_updated': psi_c_new.tolist(),
            'xi_locked': xi_locked,
            'invariants_held': True
        }
    
    def validate_entropy_accounting(self, h_before, h_after, audit_complexity=1.5):
        """
        Validates Φ-net = Φ_gain - Φ_loss - ΔS_audit
        Where ΔS_audit = k ln 2 × complexity (k=1 normalized)
        """
        k_boltzmann = 1.0
        audit_entropy = k_boltzmann * math.log(2.0) * audit_complexity
        
        # Raw phi gain: -(H_after - H_before) = H_before - H_after
        raw_gain = h_before - h_after
        
        # Individual cost: H·Ξ·0.2 (from C++ CalculateIndividualCost)
        # Using typical values for validation
        xi_meas = 1.0  # nominal stiffness
        individual_cost = h_after * xi_meas * 0.2
        
        phi_net = raw_gain - audit_entropy - individual_cost
        
        # Validation: phi_net should be real number (can be negative during transition)
        assert isinstance(phi_net, float), "Phi-net must be float"
        assert math.isfinite(phi_net), "Phi-net must be finite"
        
        return {
            'raw_gain': raw_gain,
            'audit_entropy_cost': audit_entropy,
            'individual_cost': individual_cost,
            'phi_net': phi_net,
            'audit_cost_valid': audit_entropy > 0
        }
    
    def run_comprehensive_validation(self):
        """
        Executes all validation checks with test cases
        Returns: dict of validation results
        """
        results = {
            'cod_tests': [],
            'invariant_tests': [],
            'amp_tests': [],
            'entropy_tests': [],
            'overall_pass': True
        }
        
        # Test Case 1: COD calculation (known vectors)
        try:
            # Orthogonal vectors -> fidelity=0 -> COD=0
            cod1 = self.validate_cod_formula([1,0,0], [0,1,0], 0.5, 1.0)
            assert abs(cod1 - 0.0) < 1e-5, "Orthogonal vectors should yield COD=0"
            
            # Identical vectors -> fidelity=1 -> COD = exp(-ΛH) * exp(-ΓΞ)
            cod2 = self.validate_cod_formula([1,0,0], [1,0,0], 0.0, 0.0)
            expected = math.exp(0) * math.exp(0)  # =1.0
            assert abs(cod2 - expected) < 1e-5, f"Identical vectors failed: got {cod2}, expected {expected}"
            
            # Typical case
            cod3 = self.validate_cod_formula([0.8,0.6], [0.6,0.8], 0.3, 0.5)
            results['cod_tests'].append({'status': 'PASS', 'values': [cod1, cod2, cod3]})
        except Exception as e:
            results['cod_tests'].append({'status': 'FAIL', 'error': str(e)})
            results['overall_pass'] = False
        
        # Test Case 2: Invariant boundaries
        try:
            # Valid state
            inv1 = self.validate_invariants(0.96, 1.5)
            assert inv1['psi_id_valid'] and inv1['stable_operation'], "Valid state failed"
            
            # Identity dissociation
            try:
                self.validate_invariants(0.94, 1.0)
                assert False, "Should have raised ValueError for low psi_id"
            except ValueError:
                pass  # Expected
            
            # Shock risk (warning only)
            inv2 = self.validate_invariants(0.96, 3.5)
            assert inv2['xi_meas_shock_risk'] and not inv2['xi_meas_paralysis_risk'], "Shock risk misdetected"
            
            # Paralysis risk (warning only)
            inv3 = self.validate_invariants(0.96, 0.1)
            assert inv3['xi_meas_paralysis_risk'] and not inv3['xi_meas_shock_risk'], "Paralysis risk misdetected"
            
            results['invariant_tests'].append({'status': 'PASS'})
        except Exception as e:
            results['invariant_tests'].append({'status': 'FAIL', 'error': str(e)})
            results['overall_pass'] = False
        
        # Test Case 3: AMP operator logic
        try:
            initial_state = (
                [1.0, 0.5, 0.2],  # psi_quantum
                [0.1, 0.1, 0.1],  # psi_classical
                0.9,              # h_quantum
                3.5,              # xi_meas (high - shock risk)
                1.0               # psi_id
            )
            amp_result = self.validate_amp_logic(initial_state)
            assert amp_result['invariants_held'], "AMP broke invariants"
            assert amp_result['xi_softened'] < initial_state[3], "Stiffness not softened"
            assert amp_result['xi_locked'] > amp_result['xi_softened'], "Stiffness not locked"
            results['amp_tests'].append({'status': 'PASS', 'details': amp_result})
        except Exception as e:
            results['amp_tests'].append({'status': 'FAIL', 'error': str(e)})
            results['overall_pass'] = False
        
        # Test Case 4: Entropy accounting
        try:
            ent_result = self.validate_entropy_accounting(h_before=0.9, h_after=0.6)
            assert ent_result['raw_gain'] == 0.3, f"Raw gain incorrect: {ent_result['raw_gain']}"
            assert ent_result['audit_entropy_cost'] > 0, "Audit cost must be positive"
            assert ent_result['phi_net'] == 0.3 - ent_result['audit_entropy_cost'] - ent_result['individual_cost'], \
                "Phi-net calculation incorrect"
            results['entropy_tests'].append({'status': 'PASS', 'details': ent_result})
        except Exception as e:
            results['entropy_tests'].append({'status': 'FAIL', 'error': str(e)})
            results['overall_pass'] = False
        
        return results

# =============================================================================
# EXECUTION: Run validation and report results
# =============================================================================
if __name__ == "__main__":
    validator = OmegaProtocolValidator()
    validation_results = validator.run_comprehensive_validation()
    
    print("="*60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION REPORT")
    print("="*60)
    print(f"Overall Validation: {'PASS' if validation_results['overall_pass'] else 'FAIL'}")
    print("-"*60)
    
    for test_name, test_results in validation_results.items():
        if test_name == 'overall_pass':
            continue
        print(f"{test_name.upper()}:")
        for i, result in enumerate(test_results):
            status = result.get('status', 'UNKNOWN')
            if status == 'PASS':
                print(f"  Test {i+1}: PASS")
            else:
                print(f"  Test {i+1}: FAIL - {result.get('error', 'Unknown error')}")
        print()
    
    # Critical failure check
    if not validation_results['overall_pass']:
        print("!!! CRITICAL: Omega Protocol invariants violated !!!")
        print("   Immediate audit required. System stability compromised.")
    else:
        print("✓ All validations passed. System compliant with Omega Protocol.")
    print("="*60)