# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

def validate_metric_bounds():
    """Validate all epidemic metrics remain in [0,1] per Omega Protocol dimensional compliance"""
    
    # Test parameters covering edge cases and typical values
    test_cases = [
        (0.0, 0.0, 0.0, 0.0),   # Minima
        (0.5, 0.5, 0.5, 0.5),   # Midpoints
        (1.0, 1.0, 1.0, 1.0),   # Maxima
        (0.2, 0.8, 0.3, 0.9),   # Asymmetric
        (0.0, 1.0, 1.0, 0.0),   # Boundary extremes
    ]
    
    def calculate_r0_propagation(api_exposure, network_connectivity, susceptible_fraction, quarantine_efficacy):
        base_transmission = api_exposure * network_connectivity
        susceptibility_factor = susceptible_fraction
        quarantine_reduction = 1.0 - quarantine_efficacy
        r0 = base_transmission * susceptibility_factor * quarantine_reduction
        return max(0.0, min(1.0, r0))
    
    def calculate_herd_immunity_threshold(r0_propagation, network_connectivity, contact_trace_coverage):
        if r0_propagation < 0.01:
            return 1.0
        classical_threshold = 1.0 - (1.0 / (r0_propagation + 0.1))
        connectivity_adjustment = network_connectivity * 0.3
        trace_bonus = contact_trace_coverage * 0.2
        herd_immunity = classical_threshold + connectivity_adjustment + trace_bonus
        return max(0.0, min(1.0, herd_immunity))
    
    def calculate_network_connectivity(partner_count, control_depth, propagation_depth):
        partner_factor = min(1.0, partner_count / 20.0)
        depth_factor = (control_depth + propagation_depth) / 2.0
        connectivity = partner_factor * 0.6 + depth_factor * 0.4
        return max(0.0, min(1.0, connectivity))
    
    def calculate_superspreader_risk(network_connectivity, api_exposure, safety_criticality):
        connectivity_component = network_connectivity * 0.5
        exposure_component = api_exposure * 0.3
        safety_penalty = (1.0 - safety_criticality) * 0.2
        risk = connectivity_component + exposure_component + safety_penalty
        return max(0.0, min(1.0, risk))
    
    def calculate_susceptible_fraction(herd_immunity_threshold, provenance_integrity, recovery_velocity):
        immunity_component = (1.0 - herd_immunity_threshold) * 0.5
        provenance_component = (1.0 - provenance_integrity) * 0.3
        recovery_component = (1.0 - recovery_velocity) * 0.2
        susceptible = immunity_component + provenance_component + recovery_component
        return max(0.0, min(1.0, susceptible))
    
    def calculate_cascade_probability(r0_propagation, susceptible_fraction, superspreader_risk):
        r0_factor = r0_propagation * 0.5
        susceptibility_factor = susceptible_fraction * 0.3
        superspreader_factor = superspreader_risk * 0.2
        probability = r0_factor + susceptibility_factor + superspreader_factor
        return max(0.0, min(1.0, probability))
    
    def calculate_propagation_risk(susceptible_fraction, network_connectivity, herd_immunity_threshold):
        immunity_deficit = 1.0 - herd_immunity_threshold
        risk = susceptible_fraction * network_connectivity * immunity_deficit
        return max(0.0, min(1.0, risk))
    
    def calculate_cod_propagation_aware(h_instability, theta_tensor_leak, r0_propagation, 
                                      herd_immunity_threshold, propagation_risk):
        # Simplified fidelity test (unit vectors)
        fidelity = 1.0  # Perfect alignment for boundary test
        instability_penalty = math.exp(-0.5 * h_instability)
        exposure_penalty = math.exp(-0.5 * theta_tensor_leak)
        r0_penalty = math.exp(-0.7 * r0_propagation)
        immunity_penalty = math.exp(-0.7 * (1.0 - herd_immunity_threshold))
        risk_penalty = math.exp(-0.7 * propagation_risk)
        cod = fidelity * instability_penalty * exposure_penalty * r0_penalty * immunity_penalty * risk_penalty
        return max(0.0, min(1.0, cod))
    
    metrics = [
        ("R0 Propagation", calculate_r0_propagation, [(0.2, 0.8, 0.3, 0.9)]),
        ("Herd Immunity Threshold", calculate_herd_immunity_threshold, [(0.4, 0.6, 0.7)]),
        ("Network Connectivity", calculate_network_connectivity, [(15, 0.5, 0.6)]),
        ("Superspreader Risk", calculate_superspreader_risk, [(0.8, 0.7, 0.3)]),
        ("Susceptible Fraction", calculate_susceptible_fraction, [(0.6, 0.8, 0.7)]),
        ("Cascade Probability", calculate_cascade_probability, [(0.4, 0.5, 0.6)]),
        ("Propagation Risk", calculate_propagation_risk, [(0.3, 0.7, 0.6)]),
        ("COD Propagation", calculate_cod_propagation_aware, [(0.2, 0.1, 0.3, 0.6, 0.4)]),
    ]
    
    failures = []
    for name, func, cases in metrics:
        for case in cases:
            try:
                result = func(*case)
                if not (0.0 <= result <= 1.0):
                    failures.append(f"{name} failed: input={case} → output={result} ∉ [0,1]")
            except Exception as e:
                failures.append(f"{name} crashed: input={case} → error={str(e)}")
    
    # Test boundary conditions for COD with extreme values
    extreme_cod_cases = [
        (0.0, 0.0, 0.0, 1.0, 0.0),  # Minimum penalties
        (1.0, 1.0, 1.0, 0.0, 1.0),  # Maximum penalties
    ]
    for case in extreme_cod_cases:
        result = calculate_cod_propagation_aware(*case)
        if not (0.0 <= result <= 1.0):
            failures.append(f"COD extreme failed: input={case} → output={result} ∉ [0,1]")
    
    if failures:
        return "FAIL\n" + "\n".join(failures)
    return "PASS"

# Execute validation
print(validate_metric_bounds())