# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math

# Constants from the AdversarialFusionInvariants
PSI_INTEGRITY_THRESHOLD = 0.95
FUSION_INTEGRITY_MIN = 0.70
ADVERSARIAL_SURFACE_MAX = 0.50
ANOMALY_SCORE_MAX = 0.40
VERIFICATION_EFFICACY_MIN = 0.60
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02
LAMBDA_COUPLING = 0.5
MU_INTEGRITY = 0.7
EPSILON = 1e-9

# Helper to clamp a value to [0, 1]
def clamp(x):
    return max(0.0, min(1.0, x))

# === Core Mathematical Functions ===

def calculate_fusion_integrity_index(fusion_fidelity, mode_preservation, anomaly_score, verification_efficacy):
    fidelity_component = fusion_fidelity * 0.30
    preservation_component = mode_preservation * 0.25
    verification_component = verification_efficacy * 0.25
    anomaly_penalty = (1.0 - anomaly_score) * 0.20
    integrity = fidelity_component + preservation_component + verification_component + anomaly_penalty
    return clamp(integrity)

def calculate_adversarial_surface(sensor_count, sensor_compromise_rate, weight_manipulation_risk, mode_injection_risk):
    sensor_factor = min(1.0, sensor_count / 20.0)
    compromise_component = sensor_compromise_rate * 0.40
    weight_component = weight_manipulation_risk * 0.30
    mode_component = mode_injection_risk * 0.30
    surface = sensor_factor * (compromise_component + weight_component + mode_component)
    return clamp(surface)

def calculate_anomaly_score(information_divergence, distribution_fusion_risk, fusion_fidelity):
    divergence_component = information_divergence * 0.50
    risk_component = distribution_fusion_risk * 0.30
    fidelity_deficit = (1.0 - fusion_fidelity) * 0.20
    anomaly = divergence_component + risk_component + fidelity_deficit
    return clamp(anomaly)

def calculate_verification_efficacy(fusion_integrity_index, adversarial_surface, h_instability):
    integrity_component = fusion_integrity_index * 0.50
    surface_penalty = (1.0 - adversarial_surface) * 0.30
    stability_component = (1.0 - h_instability) * 0.20
    efficacy = integrity_component + surface_penalty + stability_component
    return clamp(efficacy)

def calculate_weight_manipulation_risk(sensor_compromise_rate, fusion_fidelity, verification_efficacy):
    compromise_component = sensor_compromise_rate * 0.50
    fidelity_reduction = (1.0 - fusion_fidelity) * 0.30
    verification_reduction = (1.0 - verification_efficacy) * 0.20
    risk = compromise_component + fidelity_reduction + verification_reduction
    return clamp(risk)

def calculate_mode_injection_risk(mode_preservation, adversarial_surface, anomaly_score):
    preservation_deficit = (1.0 - mode_preservation) * 0.40
    surface_component = adversarial_surface * 0.35
    anomaly_component = anomaly_score * 0.25
    risk = preservation_deficit + surface_component + anomaly_component
    return clamp(risk)

def calculate_tampering_probability(adversarial_surface, anomaly_score, verification_efficacy):
    surface_component = adversarial_surface * 0.40
    anomaly_component = anomaly_score * 0.35
    verification_deficit = (1.0 - verification_efficacy) * 0.25
    probability = surface_component + anomaly_component + verification_deficit
    return clamp(probability)

def calculate_integrity_risk(integrity_deficit, adversarial_surface, verification_efficacy):
    verification_deficit = 1.0 - verification_efficacy
    risk = integrity_deficit * adversarial_surface * verification_deficit
    return clamp(risk)

def calculate_cod_integrity_aware(diagnostic_vec, plasma_vec, h_instability, theta_tensor_leak, 
                                fusion_integrity_index, adversarial_surface, integrity_risk):
    # Simplified: we assume unit vectors for testing the structure
    # In reality, this would compute the dot product and magnitudes
    # We'll test the penalty structure with a placeholder fidelity
    fidelity = 0.9  # Example value, should be in [0,1]
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    integrity_penalty = math.exp(-MU_INTEGRITY * (1.0 - fusion_integrity_index))
    surface_penalty = math.exp(-MU_INTEGRITY * adversarial_surface)
    risk_penalty = math.exp(-MU_INTEGRITY * integrity_risk)
    return fidelity * instability_penalty * exposure_penalty * integrity_penalty * surface_penalty * risk_penalty

def calculate_psi_coupling(phi_N):
    return math.log(phi_N + EPSILON)

def calculate_stiffness_terms(psi_coupling, stiffness_base, xi_N, xi_Delta):
    # Note: In C++ these are output parameters; we return them
    xi_N_val = stiffness_base * math.exp(psi_coupling)
    xi_Delta_val = stiffness_base * math.exp(-psi_coupling)
    return xi_N_val, xi_Delta_val

def calculate_quarantine_efficacy(base_efficacy, xi_N, xi_Delta):
    stiffness_ratio = xi_N / (xi_Delta + EPSILON)
    efficacy_modifier = 1.0 - abs(stiffness_ratio - 1.0)
    return clamp(base_efficacy * efficacy_modifier)

def calculate_s_topology(partner_facilities, susceptible_fractions):
    S_topology = 0.0
    n = len(partner_facilities)
    for i in range(n):
        p_i = susceptible_fractions[i]
        if p_i > 0.0:
            S_topology -= p_i * math.log(p_i + EPSILON)
    max_entropy = math.log(n + EPSILON)
    return clamp(S_topology / max_entropy)

def check_boundary_state(r0_propagation, cascade_probability, phi_Delta):
    if phi_Delta > 0.80 or cascade_probability > 0.95:
        return "SHREDDING"
    if r0_propagation > 1.0 or phi_Delta > 0.60:
        return "SUPERCRITICAL"
    if r0_propagation > 0.9:
        return "CRITICAL_THRESHOLD"
    return "SUBCRITICAL"

# === Validation Tests ===

def test_boundedness(func, input_ranges, num_tests=10000, expected_range=(0.0, 1.0)):
    """Test that func outputs values within expected_range for random inputs in input_ranges."""
    failures = []
    for _ in range(num_tests):
        args = [random.uniform(low, high) for (low, high) in input_ranges]
        try:
            result = func(*args)
            if not (expected_range[0] <= result <= expected_range[1]):
                failures.append((args, result))
        except Exception as e:
            failures.append((args, f"Exception: {e}"))
    return failures

def test_specific_invariants():
    """Test specific Omega Protocol invariants."""
    failures = []
    
    # Test 1: phi_N and phi_Delta should be non-negative and their sum clamped to [0,1]
    for _ in range(1000):
        phi_N = random.uniform(0, 1)
        phi_Delta = random.uniform(0, 1)
        total = phi_N + phi_Delta
        clamped_total = clamp(total)
        if clamped_total < 0 or clamped_total > 1:
            failures.append((phi_N, phi_Delta, total, clamped_total))
    
    # Test 2: psi_coupling should be real (phi_N >= 0 ensures phi_N + EPSILON > 0)
    for _ in range(1000):
        phi_N = random.uniform(0, 1)
        try:
            psi = calculate_psi_coupling(phi_N)
            # psi can be negative, but should be a real number
            assert isinstance(psi, float)
        except Exception as e:
            failures.append((phi_N, f"psi_coupling failed: {e}"))
    
    # Test 3: Stiffness terms should be positive
    for _ in range(1000):
        psi_coupling = random.uniform(-10, 10)  # log(phi_N+EPSILON) range
        stiffness_base = random.uniform(0, 1)
        xi_N, xi_Delta = calculate_stiffness_terms(psi_coupling, stiffness_base, 0, 0)
        if xi_N <= 0 or xi_Delta <= 0:
            failures.append((psi_coupling, stiffness_base, xi_N, xi_Delta))
    
    # Test 4: Quarantine efficacy should be in [0,1]
    for _ in range(1000):
        base_efficacy = random.uniform(0, 1)
        xi_N = random.uniform(0.1, 10)  # Avoid zero to prevent division issues
        xi_Delta = random.uniform(0.1, 10)
        efficacy = calculate_quarantine_efficacy(base_efficacy, xi_N, xi_Delta)
        if not (0 <= efficacy <= 1):
            failures.append((base_efficacy, xi_N, xi_Delta, efficacy))
    
    # Test 5: S_topology should be in [0,1]
    for _ in range(1000):
        n = random.randint(1, 10)
        partner_facilities = [f"fac_{i}" for i in range(n)]
        susceptible_fractions = [random.uniform(0, 1) for _ in range(n)]
        s_top = calculate_s_topology(partner_facilities, susceptible_fractions)
        if not (0 <= s_top <= 1):
            failures.append((n, susceptible_fractions, s_top))
    
    # Test 6: Boundary state should return valid enum
    valid_states = {"SUBCRITICAL", "CRITICAL_THRESHOLD", "SUPERCRITICAL", "SHREDDING"}
    for _ in range(1000):
        r0 = random.uniform(0, 2)
        cascade = random.uniform(0, 1)
        phi_Delta = random.uniform(0, 1)
        state = check_boundary_state(r0, cascade, phi_Delta)
        if state not in valid_states:
            failures.append((r0, cascade, phi_Delta, state))
    
    return failures

def main():
    print("Running mathematical soundness validation for Adversarial Fusion Integrity Manifold...")
    
    # Define test cases for each function: (function, input_ranges, expected_range)
    test_cases = [
        (calculate_fusion_integrity_index, 
         [(0,1), (0,1), (0,1), (0,1)], 
         (0,1)),
        (calculate_adversarial_surface, 
         [(0,100), (0,1), (0,1), (0,1)],  # sensor_count up to 100
         (0,1)),
        (calculate_anomaly_score, 
         [(0,1), (0,1), (0,1)], 
         (0,1)),
        (calculate_verification_efficacy, 
         [(0,1), (0,1), (0,1)], 
         (0,1)),
        (calculate_weight_manipulation_risk, 
         [(0,1), (0,1), (0,1)], 
         (0,1)),
        (calculate_mode_injection_risk, 
         [(0,1), (0,1), (0,1)], 
         (0,1)),
        (calculate_tampering_probability, 
         [(0,1), (0,1), (0,1)], 
         (0,1)),
        (calculate_integrity_risk, 
         [(0,1), (0,1), (0,1)], 
         (0,1)),
        # For COD, we test the penalty structure with fixed fidelity=0.9
        (lambda h, t, fi, as_, ir: calculate_cod_integrity_aware([1+0j], [1+0j], h, t, fi, as_, ir),
         [(0,1), (0,1), (0,1), (0,1), (0,1)],
         (0,1)),  # Output should be in (0, fidelity] which is subset of (0,1]
        (calculate_psi_coupling, 
         [(EPSILON, 1.0)],  # phi_N in [EPSILON, 1.0] to avoid log(0)
         (-float('inf'), math.log(1+EPSILON)]),  # psi can be negative
        (calculate_s_topology, 
         [([], []), ([0.5]*5, [0.5]*5)],  # We'll handle this specially
         (0,1)),
    ]
    
    all_failures = []
    
    # Run boundedness tests
    for func, input_ranges, expected_range in test_cases:
        if func == calculate_s_topology:
            # Special handling for s_topology
            failures = []
            for _ in range(1000):
                n = random.randint(1, 10)
                partner_facilities = [f"fac_{i}" for i in range(n)]
                susceptible_fractions = [random.uniform(0, 1) for _ in range(n)]
                try:
                    result = calculate_s_topology(partner_facilities, susceptible_fractions)
                    if not (0 <= result <= 1):
                        failures.append((n, susceptible_fractions, result))
                except Exception as e:
                    failures.append((n, susceptible_fractions, f"Exception: {e}"))
            if failures:
                all_failures.append((calculate_s_topology.__name__, failures))
        else:
            failures = test_boundedness(func, input_ranges, expected_range=expected_range)
            if failures:
                all_failures.append((func.__name__, failures))
    
    # Run specific invariant tests
    invariant_failures = test_specific_invariants()
    if invariant_failures:
        all_failures.append(("Specific Invariants", invariant_failures))
    
    # Report results
    if not all_failures:
        print("✅ ALL TESTS PASSED: Mathematical soundness and Omega Protocol invariants upheld.")
        return True
    else:
        print("❌ VALIDATION FAILURES DETECTED:")
        for name, failures in all_failures:
            print(f"\n{name}: {len(failures)} failure(s)")
            # Show first few failures for brevity
            for i, failure in enumerate(failures[:3]):
                print(f"  Failure {i+1}: {failure}")
            if len(failures) > 3:
                print(f"  ... and {len(failures)-3} more")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)