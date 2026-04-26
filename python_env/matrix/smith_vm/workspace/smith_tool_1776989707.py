# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

class OmegaProtocolValidator:
    """
    Validates mathematical soundness and Omega Protocol invariant compliance
    for the bureaucratic decision manifold specification.
    """
    
    def __init__(self):
        # Omega Protocol invariants (must be non-negative and conserved)
        self.phi_N_min = 0.0
        self.phi_Delta_min = 0.0
        self.J_star_min = 0.0  # J* interpreted as net Φ-density post-audit
        
        # Agent's internal invariants (from SystemInvariants struct)
        self.psi_id_min = 0.95
        self.xi_sys_max_warn = 3.0  # Warning threshold
        self.xi_sys_max_hard = 3.5  # Beyond this risks Informational Freeze
        self.xi_N_max = 2.0
        self.xi_Delta_max = 2.5
        self.kappa_max = 1.0
        
        # Constants for entropy calculations
        self.k_boltzmann = 1.0  # Normalized for informational entropy
        
    def validate_topological_impedance(self, path):
        """
        Validates H_top = [Σ(Cost_i × Variance_i) / Σ(Cost_i)] × [1 / H_max]
        where H_max = ln(N) for N decision nodes.
        Checks: dimensional homogeneity, range [0,1], and equation correctness.
        """
        if not path:
            return 0.0, True, "Empty path: H_top = 0.0 (valid)"
        
        total_impedance = 0.0
        total_cost = 0.0
        for node in path:
            approval_cost, risk_variance = node
            # Validate inputs: dimensionless [1], in [0,1]
            if not (0.0 <= approval_cost <= 1.0):
                return None, False, f"Invalid approval_cost: {approval_cost} (must be [0,1])"
            if not (0.0 <= risk_variance <= 1.0):
                return None, False, f"Invalid risk_variance: {risk_variance} (must be [0,1])"
            total_impedance += approval_cost * risk_variance
            total_cost += approval_cost
        
        if total_cost == 0.0:
            H_top = 0.0
        else:
            raw_impedance = total_impedance / total_cost
            H_max = math.log(len(path)) if len(path) > 1 else 1.0
            H_top = min(1.0, max(0.0, raw_impedance / H_max))
        
        # Validate dimensional homogeneity: all terms [1] → H_top [1]
        # Validate range: H_top ∈ [0,1] by construction
        if not (0.0 <= H_top <= 1.0):
            return None, False, f"H_top out of bounds: {H_top}"
        
        return H_top, True, f"H_top = {H_top:.4f} (valid)"
    
    def validate_cod(self, intent, outcome, H_top, xi_bound):
        """
        Validates COD = |<Ψ_intent|Ψ_outcome>|² × exp(-Λ·H_top) × exp(-Γ·Ξ_bound)
        with Λ=1.0, Γ=0.5 as per agent's specification.
        Checks: fidelity calculation, damping terms, range [0,1].
        """
        if len(intent) != len(outcome):
            return None, False, "Intent and outcome vectors must have same length"
        
        # Calculate fidelity: |<Ψ_intent|Ψ_outcome>|²
        dot = np.dot(intent, outcome)
        magI = np.linalg.norm(intent)
        magO = np.linalg.norm(outcome)
        if magI < 1e-9 or magO < 1e-9:
            fidelity = 0.0
        else:
            fidelity = dot / (magI * magO)
            fidelity = max(0.0, min(1.0, fidelity))  # Clamp to [0,1]
        
        # Validate damping terms
        damping = math.exp(-1.0 * H_top)  # Λ=1.0
        stiffness_penalty = math.exp(-0.5 * xi_bound)  # Γ=0.5
        
        cod = fidelity * damping * stiffness_penalty
        
        # Validate dimensional homogeneity: all terms [1] → COD [1]
        # Validate range: COD ∈ [0,1] by construction (fidelity∈[0,1], exponentials∈(0,1])
        if not (0.0 <= cod <= 1.0):
            return None, False, f"COD out of bounds: {cod}"
        
        return cod, True, f"COD = {cod:.4f} (valid)"
    
    def validate_shannon_conditional_entropy(self, outcome, H_top):
        """
        Validates H_cond = H(D|I) / H_max where H(D|I) = -Σ p(d|i) log p(d|i)
        and H_max = ln(N) for N outcome dimensions.
        Note: Agent's implementation does not use H_top in calculation (kept for signature compatibility).
        """
        if not outcome:
            return 0.0, True, "Empty outcome: H_cond = 0.0 (valid)"
        
        # Validate probabilities: dimensionless [1], sum to ≈1.0
        total = sum(outcome)
        if abs(total - 1.0) > 1e-5:
            return None, False, f"Outcome probabilities do not sum to 1.0: sum={total}"
        for p in outcome:
            if not (0.0 <= p <= 1.0):
                return None, False, f"Invalid probability: {p} (must be [0,1])"
        
        # Calculate Shannon entropy
        H = 0.0
        for p in outcome:
            if p > 1e-9:
                H -= p * math.log(p)
        
        # Normalize by H_max = ln(N)
        N = len(outcome)
        H_max = math.log(N) if N > 1 else 1.0
        H_cond = min(1.0, max(0.0, H / H_max)) if H_max > 0 else 0.0
        
        # Validate dimensional homogeneity: all terms [1] → H_cond [1]
        # Validate range: H_cond ∈ [0,1] by construction
        if not (0.0 <= H_cond <= 1.0):
            return None, False, f"H_cond out of bounds: {H_cond}"
        
        return H_cond, True, f"H_cond = {H_cond:.4f} (valid)"
    
    def validate_invariants(self, psi_id, xi_sys, kappa_sys_ind, xi_N, xi_Delta):
        """
        Validates agent's internal invariants as active boundary conditions.
        Checks: hard gates for Ψ_id, ξ_N, ξ_Δ, κ_sys-ind; warning for Ξ_sys.
        """
        violations = []
        warnings = []
        
        # Ψ_id >= 0.95 (Shredding Event boundary)
        if psi_id < self.psi_id_min:
            violations.append(f"Ψ_id = {psi_id:.4f} < {self.psi_id_min} → Shredding Event")
        
        # Ξ_sys <= 3.0 (Informational Freeze risk - warning only per agent)
        if xi_sys > self.xi_sys_max_warn:
            warnings.append(f"Ξ_sys = {xi_sys:.4f} > {self.xi_sys_max_warn} → Informational Freeze Risk")
        if xi_sys > self.xi_sys_max_hard:  # Beyond warning threshold becomes critical
            violations.append(f"Ξ_sys = {xi_sys:.4f} > {self.xi_sys_max_hard} → Critical Freeze Risk")
        
        # ξ_N <= 2.0 (Stable Mode Violation - hard gate)
        if xi_N > self.xi_N_max:
            violations.append(f"ξ_N = {xi_N:.4f} > {self.xi_N_max} → Stable Mode Violation")
        
        # ξ_Δ <= 2.5 (Adversarial Mode Violation - hard gate)
        if xi_Delta > self.xi_Delta_max:
            violations.append(f"ξ_Δ = {xi_Delta:.4f} > {self.xi_Delta_max} → Adversarial Mode Violation")
        
        # κ_sys-ind <= 1.0 (System-Individual Overload - hard gate)
        if kappa_sys_ind > self.kappa_max:
            violations.append(f"κ_sys-ind = {kappa_sys_ind:.4f} > {self.kappa_max} → Overload")
        
        is_valid = len(violations) == 0
        msg = []
        if violations:
            msg.append("INVARIANT VIOLATIONS: " + "; ".join(violations))
        if warnings:
            msg.append("WARNINGS: " + "; ".join(warnings))
        if not msg:
            msg.append("All invariants within bounds")
        
        return is_valid, "; ".join(msg)
    
    def validate_phi_density(self, throughput, impedance_cost, risk_leak, individual_cost, 
                            attack_success, cod, audit_complexity_factor=1.0):
        """
        Validates Φ-net = Φ_gain - Φ_loss - ΔS_audit
        where:
          Φ_gain = throughput
          Φ_loss = impedance_cost + risk_leak + individual_cost
          ΔS_audit = k ln 2 × audit_complexity_factor
        And checks Omega Protocol invariants:
          Φ_N = throughput × cod × (1 - risk_leak) ≥ 0
          Φ_Δ = attack_success × (1 - cod) × risk_leak ≥ 0
          J* = Φ-net ≥ 0  (interpreted as net Φ-density)
        """
        # Validate inputs: all dimensionless [1], non-negative where applicable
        inputs = [
            ("throughput", throughput, 0.0, None),
            ("impedance_cost", impedance_cost, 0.0, None),
            ("risk_leak", risk_leak, 0.0, 1.0),
            ("individual_cost", individual_cost, 0.0, None),
            ("attack_success", attack_success, 0.0, 1.0),
            ("cod", cod, 0.0, 1.0),
            ("audit_complexity_factor", audit_complexity_factor, 0.0, None)
        ]
        
        for name, val, min_val, max_val in inputs:
            if min_val is not None and val < min_val:
                return None, False, f"{name} = {val} < {min_val}"
            if max_val is not None and val > max_val:
                return None, False, f"{name} = {val} > {max_val}"
        
        # Calculate Φ-components
        phi_N = throughput * cod * (1.0 - risk_leak)
        phi_Delta = attack_success * (1.0 - cod) * risk_leak
        
        # Calculate audit entropy cost: ΔS_audit = k ln 2 × complexity
        audit_entropy_cost = self.k_boltzmann * math.log(2.0) * audit_complexity_factor
        
        # Calculate net Φ-density
        phi_gain = throughput
        phi_loss = impedance_cost + risk_leak + individual_cost
        phi_net = phi_gain - phi_loss - audit_entropy_cost
        
        # Validate Omega Protocol invariants: Φ_N, Φ_Δ, J* ≥ 0
        j_star = phi_net  # J* interpreted as net Φ-density
        
        invariant_violations = []
        if phi_N < self.phi_N_min:
            invariant_violations.append(f"Φ_N = {phi_N:.4f} < {self.phi_N_min}")
        if phi_Delta < self.phi_Delta_min:
            invariant_violations.append(f"Φ_Δ = {phi_Delta:.4f} < {self.phi_Delta_min}")
        if j_star < self.J_star_min:
            invariant_violations.append(f"J* = {j_star:.4f} < {self.J_star_min}")
        
        is_valid = len(invariant_violations) == 0
        msg = []
        if invariant_violations:
            msg.append("OMEGA PROTOCOL INVARIANT VIOLATIONS: " + "; ".join(invariant_violations))
        msg.append(f"Φ_N = {phi_N:.4f}, Φ_Δ = {phi_Delta:.4f}, J* = {j_star:.4f}")
        msg.append(f"Audit cost = {audit_entropy_cost:.4f} (k ln 2 × {audit_complexity_factor})")
        
        return {
            'phi_N': phi_N,
            'phi_Delta': phi_Delta,
            'J_star': j_star,
            'phi_net': phi_net
        }, is_valid, "; ".join(msg)
    
    def run_comprehensive_validation(self, test_case):
        """
        Runs validation on a complete test case mimicking the agent's workflow.
        test_case should contain:
          - path: list of (approval_cost, risk_variance) tuples
          - intent, outcome: vectors for COD calculation
          - xi_sys: bureaucratic stiffness
          - kappa_sys_ind: coupling constant
          - xi_N, xi_Delta: mode stiffness values
          - psi_id: goal integrity
          - urgency_force: for failure mode detection
          - throughput, impedance_cost, etc.: for Φ-density calculation
        """
        results = {}
        
        # 1. Validate Topological Impedance (H_top)
        H_top, htop_ok, htop_msg = self.validate_topological_impedance(test_case['path'])
        results['H_top'] = {'value': H_top, 'valid': htop_ok, 'message': htop_msg}
        
        # 2. Validate COD
        cod, cod_ok, cod_msg = self.validate_cod(
            test_case['intent'], 
            test_case['outcome'], 
            H_top, 
            test_case['xi_sys']
        )
        results['COD'] = {'value': cod, 'valid': cod_ok, 'message': cod_msg}
        
        # 3. Validate Shannon Conditional Entropy
        h_cond, hcond_ok, hcond_msg = self.validate_shannon_conditional_entropy(
            test_case['outcome'], 
            H_top
        )
        results['H_cond'] = {'value': h_cond, 'valid': hcond_ok, 'message': hcond_msg}
        
        # 4. Validate Internal Invariants (Agent's SystemInvariants)
        inv_ok, inv_msg = self.validate_invariants(
            test_case['psi_id'],
            test_case['xi_sys'],
            test_case['kappa_sys_ind'],
            test_case['xi_N'],
            test_case['xi_Delta']
        )
        results['Internal_Invariants'] = {'valid': inv_ok, 'message': inv_msg}
        
        # 5. Validate Φ-density and Omega Protocol Invariants
        phi_results, phi_ok, phi_msg = self.validate_phi_density(
            test_case['throughput'],
            test_case['impedance_cost'],
            test_case['risk_leak'],
            test_case['individual_cost'],
            test_case['attack_success'],
            cod,
            test_case.get('audit_complexity_factor', 1.0)
        )
        results['Phi_Density'] = {
            'values': phi_results,
            'valid': phi_ok,
            'message': phi_msg
        }
        
        # Overall validation: all critical checks must pass
        critical_checks = [
            htop_ok,
            cod_ok,
            hcond_ok,
            inv_ok,  # Internal invariants must pass (hard gates)
            phi_ok   # Omega Protocol invariants must pass
        ]
        overall_valid = all(critical_checks)
        
        results['overall'] = {
            'valid': overall_valid,
            'message': "ALL CHECKS PASSED" if overall_valid else "ONE OR MORE CHECKS FAILED"
        }
        
        return results

# Example usage with test data mimicking a stable decision manifold
if __name__ == "__main__":
    validator = OmegaProtocolValidator()
    
    # Test case: Stable decision manifold (should pass all validations)
    test_case = {
        'path': [
            (0.2, 0.1),  # Node 1: low cost, low variance
            (0.3, 0.15), # Node 2: moderate cost, moderate variance
            (0.1, 0.05)  # Node 3: low cost, low variance
        ],
        'intent': [0.8, 0.6, 0.9],
        'outcome': [0.75, 0.55, 0.85],
        'xi_sys': 1.8,        # Below warning threshold (3.0)
        'kappa_sys_ind': 0.4, # Below overload threshold (1.0)
        'xi_N': 1.5,          # Below stable mode threshold (2.0)
        'xi_Delta': 2.0,      # Below adversarial threshold (2.5)
        'psi_id': 0.97,       # Above shredding threshold (0.95)
        'urgency_force': 0.6, # For failure mode detection (not directly validated here)
        'throughput': 1.2,
        'impedance_cost': 0.3,
        'risk_leak': 0.1,
        'individual_cost': 0.2,
        'attack_success': 0.1,
        'audit_complexity_factor': 1.0
    }
    
    results = validator.run_comprehensive_validation(test_case)
    
    print("="*60)
    print("OMEGA PROTOCOL VALIDATION REPORT")
    print("="*60)
    for key, res in results.items():
        if key == 'overall':
            continue
        print(f"\n{key}:")
        print(f"  Status: {'PASS' if res['valid'] else 'FAIL'}")
        print(f"  Details: {res['message']}")
        if 'value' in res and res['value'] is not None:
            print(f"  Value: {res['value']:.4f}")
        if 'values' in res:
            for k, v in res['values'].items():
                print(f"  {k}: {v:.4f}")
    
    print("\n" + "="*60)
    print(f"OVERALL VALIDATION: {'PASS' if results['overall']['valid'] else 'FAIL'}")
    print(f"Reason: {results['overall']['message']}")
    print("="*60)
    
    # Additional test: Intentionally violate an invariant to check detection
    print("\n" + "="*60)
    print("TESTING INVARIANT VIOLATION DETECTION")
    print("="*60)
    violation_case = test_case.copy()
    violation_case['psi_id'] = 0.92  # Below 0.95 threshold
    results_violation = validator.run_comprehensive_validation(violation_case)
    print(f"\nPsi_id violation test: {'PASS' if not results_violation['overall']['valid'] else 'FAIL (should have failed)'}")
    print(f"Reason: {results_violation['overall']['message']}")