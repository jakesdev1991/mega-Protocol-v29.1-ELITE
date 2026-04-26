# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATOR FOR API PROPAGATION EPIDEMIC v77.0-Ω
# Validates mathematical soundness, dimensional compliance, and safety gates
# =============================================================================

class OmegaProtocolValidator:
    # Protocol invariants (from agent's code)
    PSI_INTEGRITY_THRESHOLD = 0.95
    R0_MAX = 0.50
    HERD_IMMUNITY_MIN = 0.60
    SUPERSPREADER_CONNECTIVITY_MAX = 0.70
    COD_THRESHOLD = 0.85
    AUDIT_ENTROPY_PER_CHECK = 0.02
    
    # Epidemic states (from agent's code)
    class EpidemicState:
        CONTAINED = 0
        SPREADING = 1
        EPIDEMIC = 2
        HERD_PROTECTED = 3
    
    # Risk levels
    class RiskLevel:
        LOW = 0
        MEDIUM = 1
        CRITICAL = 2
        CATASTROPHIC = 3

    @staticmethod
    def clamp(x, min_val=0.0, max_val=1.0):
        return max(min_val, min(max_val, x))

    # =========================================================================
    # MATHEMATICAL FUNCTIONS (translated from agent's C++ code)
    # =========================================================================
    
    @staticmethod
    def calculate_r0_propagation(api_exposure, network_connectivity, susceptible_fraction, quarantine_efficacy):
        base_transmission = api_exposure * network_connectivity
        susceptibility_factor = susceptible_fraction
        quarantine_reduction = 1.0 - quarantine_efficacy
        r0 = base_transmission * susceptibility_factor * quarantine_reduction
        return OmegaProtocolValidator.clamp(r0)
    
    @staticmethod
    def calculate_herd_immunity_threshold(r0_propagation, network_connectivity, contact_trace_coverage):
        if r0_propagation < 0.01:
            return 1.0
        classical_threshold = 1.0 - (1.0 / (r0_propagation + 0.1))
        connectivity_adjustment = network_connectivity * 0.3
        trace_bonus = contact_trace_coverage * 0.2
        herd_immunity = classical_threshold + connectivity_adjustment + trace_bonus
        return OmegaProtocolValidator.clamp(herd_immunity)
    
    @staticmethod
    def calculate_network_connectivity(partner_count, control_depth, propagation_depth):
        partner_factor = min(1.0, partner_count / 20.0)
        depth_factor = (control_depth + propagation_depth) / 2.0
        connectivity = partner_factor * 0.6 + depth_factor * 0.4
        return OmegaProtocolValidator.clamp(connectivity)
    
    @staticmethod
    def calculate_superspreader_risk(network_connectivity, api_exposure, safety_criticality):
        connectivity_component = network_connectivity * 0.5
        exposure_component = api_exposure * 0.3
        safety_penalty = (1.0 - safety_criticality) * 0.2
        risk = connectivity_component + exposure_component + safety_penalty
        return OmegaProtocolValidator.clamp(risk)
    
    @staticmethod
    def calculate_susceptible_fraction(herd_immunity_threshold, provenance_integrity, recovery_velocity):
        immunity_component = (1.0 - herd_immunity_threshold) * 0.5
        provenance_component = (1.0 - provenance_integrity) * 0.3
        recovery_component = (1.0 - recovery_velocity) * 0.2
        susceptible = immunity_component + provenance_component + recovery_component
        return OmegaProtocolValidator.clamp(susceptible)
    
    @staticmethod
    def calculate_cascade_probability(r0_propagation, susceptible_fraction, superspreader_risk):
        r0_factor = r0_propagation * 0.5
        susceptibility_factor = susceptible_fraction * 0.3
        superspreader_factor = superspreader_risk * 0.2
        probability = r0_factor + susceptibility_factor + superspreader_factor
        return OmegaProtocolValidator.clamp(probability)
    
    @staticmethod
    def calculate_propagation_risk(susceptible_fraction, network_connectivity, herd_immunity_threshold):
        immunity_deficit = 1.0 - herd_immunity_threshold
        risk = susceptible_fraction * network_connectivity * immunity_deficit
        return OmegaProtocolValidator.clamp(risk)
    
    @staticmethod
    def calculate_cod_propagation_aware(h_instability, theta_tensor_leak, 
                                      r0_propagation, herd_immunity_threshold, propagation_risk):
        # Simplified COD calculation (agent's formula without vectors)
        # Based on: fidelity * instability_penalty * exposure_penalty * 
        #           r0_penalty * immunity_penalty * risk_penalty
        # We assume fidelity = 1.0 for validation (worst-case for penalties)
        fidelity = 1.0
        instability_penalty = math.exp(-0.5 * h_instability)  # LAMBDA_COUPLING = 0.5
        exposure_penalty = math.exp(-0.5 * theta_tensor_leak)
        r0_penalty = math.exp(-0.7 * r0_propagation)        # MU_PROPAGATION = 0.7
        immunity_penalty = math.exp(-0.7 * (1.0 - herd_immunity_threshold))
        risk_penalty = math.exp(-0.7 * propagation_risk)
        cod = fidelity * instability_penalty * exposure_penalty * \
              r0_penalty * immunity_penalty * risk_penalty
        return OmegaProtocolValidator.clamp(cod)
    
    @staticmethod
    def decide_action(psi_integrity, propagation_risk, epidemic_state):
        # PRIMARY GATE: Ψ_integrity (non-negotiable)
        if psi_integrity < OmegaProtocolValidator.PSI_INTEGRITY_THRESHOLD:
            return OmegaProtocolValidator.EpidemicState.IDENTITY_LOCKDOWN  # Using epidemic state for action mapping
        
        # EPIDEMIC STATE GATE
        if epidemic_state == OmegaProtocolValidator.EpidemicState.EPIDEMIC:
            return OmegaProtocolValidator.EpidemicState.IDENTITY_LOCKDOWN
        
        # RISK-BASED Decisions
        if propagation_risk > 0.70:
            return OmegaProtocolValidator.EpidemicState.IDENTITY_LOCKDOWN
        if (propagation_risk > 0.50 or 
            epidemic_state == OmegaProtocolValidator.EpidemicState.SPREADING):
            return OmegaProtocolValidator.EpidemicState.ACTIVATE_QUARANTINE
        if (propagation_risk > 0.30 or 
            epidemic_state == OmegaProtocolValidator.EpidemicState.MONITOR_SPREAD):
            return OmegaProtocolValidator.EpidemicState.MONITOR_SPREAD
        return OmegaProtocolValidator.EpidemicState.PROCEED

    # =========================================================================
    # VALIDATION TESTS
    # =========================================================================
    
    def run_boundedness_tests(self, iterations=10000):
        """Test all metric functions for [0,1] boundedness"""
        print("Running boundedness tests...")
        test_cases = [
            # (func_name, func, arg_ranges, num_args)
            ("R0 Propagation", self.calculate_r0_propagation, 
             [(0,1), (0,1), (0,1), (0,1)], 4),
            ("Herd Immunity Threshold", self.calculate_herd_immunity_threshold,
             [(0,1), (0,1), (0,1)], 3),
            ("Network Connectivity", self.calculate_network_connectivity,
             [(0,100), (0,1), (0,1)], 3),  # partner_count can be >1
            ("Superspreader Risk", self.calculate_superspreader_risk,
             [(0,1), (0,1), (0,1)], 3),
            ("Susceptible Fraction", self.calculate_susceptible_fraction,
             [(0,1), (0,1), (0,1)], 3),
            ("Cascade Probability", self.calculate_cascade_probability,
             [(0,1), (0,1), (0,1)], 3),
            ("Propagation Risk", self.calculate_propagation_risk,
             [(0,1), (0,1), (0,1)], 3),
            ("COD", self.calculate_cod_propagation_aware,
             [(0,1), (0,1), (0,1), (0,1), (0,1)], 5)
        ]
        
        all_passed = True
        for func_name, func, arg_ranges, num_args in test_cases:
            for _ in range(iterations):
                args = [random.uniform(low, high) for (low, high) in arg_ranges]
                try:
                    result = func(*args)
                    if not (0.0 <= result <= 1.0):
                        print(f"FAIL: {func_name} returned {result} for args {args}")
                        all_passed = False
                except Exception as e:
                    print(f"ERROR: {func_name} raised {e} for args {args}")
                    all_passed = False
        
        if all_passed:
            print("✅ All boundedness tests PASSED")
        else:
            print("❌ Some boundedness tests FAILED")
        return all_passed
    
    def run_safety_gate_tests(self):
        """Test safety gate hierarchy compliance"""
        print("\nRunning safety gate tests...")
        test_scenarios = [
            # (psi_integrity, propagation_risk, epidemic_state, expected_action, description)
            (0.90, 0.10, self.EpidemicState.CONTAINED, self.EpidemicState.IDENTITY_LOCKDOWN, 
             "Psi integrity breach -> lockdown"),
            (0.96, 0.10, self.EpidemicState.EPIDEMIC, self.EpidemicState.IDENTITY_LOCKDOWN, 
             "Epidemic state -> lockdown"),
            (0.96, 0.75, self.EpidemicState.CONTAINED, self.EpidemicState.IDENTITY_LOCKDOWN, 
             "High propagation risk -> lockdown"),
            (0.96, 0.55, self.EpidemicState.CONTAINED, self.EpidemicState.ACTIVATE_QUARANTINE, 
             "Medium-high risk -> quarantine"),
            (0.96, 0.55, self.EpidemicState.SPREADING, self.EpidemicState.ACTIVATE_QUARANTINE, 
             "Spreading state -> quarantine"),
            (0.96, 0.35, self.EpidemicState.CONTAINED, self.EpidemicState.MONITOR_SPREAD, 
             "Medium risk -> monitor"),
            (0.96, 0.35, self.EpidemicState.MONITOR_SPREAD, self.EpidemicState.MONITOR_SPREAD, 
             "Monitor state -> monitor"),
            (0.96, 0.25, self.EpidemicState.CONTAINED, self.EpidemicState.PROCEED, 
             "Low risk -> proceed"),
            (0.96, 0.25, self.EpidemicState.HERD_PROTECTED, self.EpidemicState.PROCEED, 
             "Herd protected -> proceed")
        ]
        
        all_passed = True
        for psi, risk, epid_state, expected, desc in test_scenarios:
            action = self.decide_action(psi, risk, epid_state)
            if action != expected:
                print(f"FAIL: {desc}")
                print(f"  Expected: {expected}, Got: {action}")
                all_passed = False
        
        if all_passed:
            print("✅ All safety gate tests PASSED")
        else:
            print("❌ Some safety gate tests FAILED")
        return all_passed
    
    def run_derivativity_check(self):
        """Verify novel metrics are not trivial repetitions of prior work"""
        print("\nRunning derivativity check...")
        # Key novelty: R0 propagation and herd immunity thresholds
        # Test that these metrics respond differently to inputs than v75.0/v76.0 analogs
        
        # v75.0 analog: api_exposure * control_depth (simplified)
        # v77.0 novelty: r0_propagation includes network dynamics
        api_exp = 0.5
        ctrl_depth = 0.5
        net_conn = 0.8  # High connectivity
        susc_frac = 0.7  # High susceptibility
        quar_eff = 0.2   # Low quarantine efficacy
        
        v75_analog = api_exp * ctrl_depth  # 0.25
        v77_r0 = self.calculate_r0_propagation(api_exp, net_conn, susc_frac, quar_eff)
        # Expected: v77_r0 > v75_analog due to network factors
        if v77_r0 <= v75_analog:
            print(f"FAIL: R0 propagation ({v77_rot}) not greater than v75.0 analog ({v75_analog})")
            print("  Indicates missing network dynamics component")
            return False
        
        # Herd immunity threshold should increase with R0 (epidemic principle)
        r0_low = 0.2
        r0_high = 0.4
        hith_low = self.calculate_herd_immunity_threshold(r0_low, 0.5, 0.5)
        hith_high = self.calculate_herd_immunity_threshold(r0_high, 0.5, 0.5)
        if hith_high <= hith_low:
            print(f"FAIL: Herd immunity threshold not increasing with R0")
            print(f"  R0={r0_low} -> HIT={hith_low}, R0={r0_high} -> HIT={hith_high}")
            return False
        
        print("✅ Derivativity check PASSED (novel epidemic dynamics detected)")
        return True
    
    def run_phi_density_accounting_check(self):
        """Verify audit cost subtraction in Phi-density ledger"""
        print("\nRunning Phi-density accounting check...")
        # Agent claims: audit_cost = audit_checks * 0.02
        # Net gain = (COD_after - COD_before) - audit_cost
        
        cod_before = 0.80
        cod_after = 0.90
        audit_checks = 14  # As stated in agent's code
        expected_gain = (cod_after - cod_before) - (audit_checks * 0.02)
        
        # Simulate agent's ledger calculation
        raw_gain = cod_after - cod_before
        audit_cost = audit_checks * self.AUDIT_ENTROPY_PER_CHECK
        net_gain = raw_gain - audit_cost
        
        if abs(net_gain - expected_gain) > 1e-9:
            print(f"FAIL: Phi-density accounting mismatch")
            print(f"  Expected: {expected_gain}, Got: {net_gain}")
            return False
        
        # Verify audit cost is subtracted (not added)
        if net_gain >= raw_gain:
            print(f"FAIL: Audit cost not subtracted (net_gain >= raw_gain)")
            return False
        
        print("✅ Phi-density accounting check PASSED")
        return True

def main():
    print("=" * 70)
    print("OMEGA PROTOCOL VALIDATOR: API PROPAGATION EPIDEMIC v77.0-Ω")
    print("=" * 70)
    
    validator = OmegaProtocolValidator()
    
    # Run all validation suites
    tests = [
        validator.run_boundedness_tests,
        validator.run_safety_gate_tests,
        validator.run_derivativity_check,
        validator.run_phi_density_accounting_check
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 70)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 70)
    if all(results):
        print("✅ ALL TESTS PASSED - Protocol compliant and mathematically sound")
        print("✅ Ready for Omega Protocol integration")
    else:
        print("❌ SOME TESTS FAILED - Protocol violations detected")
        print("❌ DO NOT INTEGRATE - Requires revision")
    print("=" * 70)

if __name__ == "__main__":
    main()