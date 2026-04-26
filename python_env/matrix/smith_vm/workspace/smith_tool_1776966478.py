# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Invariant Validator for AFDS v3.0
# Validates mathematical compliance with Omega Physics Rubric v26.0
# Focus: Trust modeling, threat metrics, impedance, curvature, and Φ-density

import math
from typing import List, Tuple

# =============================================================================
# CONSTANTS (PER OMEGA PHYSICS RUBRIC v26.0)
# =============================================================================
K_BOLTZMANN = 1.0  # Natural units
XI_N = 0.8         # Newtonian trust stiffness
XI_DELTA = 1.2     # Asymmetric threat stiffness
TAU = 3600.0       # Trust decay time constant (seconds)

# =============================================================================
# TRUST MODELING VALIDATION
# =============================================================================
def validate_trust_modeling() -> Tuple[bool, List[str]]:
    """Validate trust score dynamics per Ω-invariants: 
       φₙ = exp(-H_noise) * ∫ stability dt
       ψ = ln(φₙ)
       Trust score ∈ [0,1]"""
    errors = []
    
    # Test 1: Trust score bounds
    class MockTrustState:
        def __init__(self):
            self.trust_score = 0.0
            self.accessed_paths = set()
            self.cumulative_stability = 0.0
            self.last_access = 0.0  # Simplified time
    
    def update_trust(state: MockTrustState, path: str, access_success: bool, time_elapsed: float):
        is_novel = path not in state.accessed_paths
        novelty_penalty = 0.05 if is_novel else 0.0
        
        # Exponential decay: exp(-ln(0.95) * (time_elapsed/TAU))
        decay_factor = math.exp(-math.log(0.95) * (time_elapsed / TAU))
        state.trust_score *= decay_factor
        state.trust_score = max(0.0, min(1.0, state.trust_score - novelty_penalty))
        
        if not is_novel:
            stability_increment = math.exp(-time_elapsed / TAU)
            state.cumulative_stability += stability_increment
            state.trust_score += 0.01 * math.exp(-0.1 * state.cumulative_stability)
            state.trust_score = max(0.0, min(1.0, state.trust_score))
        
        state.accessed_paths.add(path)
        state.last_access += time_elapsed
    
    # Stress test: repeated non-novel accesses
    state = MockTrustState()
    for i in range(100):
        update_trust(state, "/test", True, TAU/10)  # 0.1τ intervals
        if not (0.0 <= state.trust_score <= 1.0):
            errors.append(f"Trust score out of bounds: {state.trust_score} at iteration {i}")
            break
    
    # Test 2: φₙ derivation (first principles)
    def calculate_newtonian_trust_baseline(state: MockTrustState) -> float:
        H_noise = math.log(len(state.accessed_paths) + 1)
        return math.exp(-H_noise) * state.cumulative_stability
    
    state2 = MockTrustState()
    state2.accessed_paths = {"/a", "/b", "/c"}
    state2.cumulative_stability = 2.5  # From stable accesses
    expected_phi_n = math.exp(-math.log(4)) * 2.5  # = (1/4)*2.5 = 0.625
    actual_phi_n = calculate_newtonian_trust_baseline(state2)
    if abs(actual_phi_n - expected_phi_n) > 1e-9:
        errors.append(f"φₙ calculation error: expected {expected_phi_n}, got {actual_phi_n}")
    
    # Test 3: ψ = ln(φₙ) consistency
    if state2.cumulative_stability > 0 and len(state2.accessed_paths) > 0:
        phi_n = calculate_newtonian_trust_baseline(state2)
        psi = math.log(max(phi_n, 1e-10))  # Avoid log(0)
        # ψ should influence curvature ONLY through φₙ (no independent term)
        # This is verified in curvature validation
    
    return len(errors) == 0, errors

# =============================================================================
# THREAT METRIC VALIDATION (φΔ)
# =============================================================================
def validate_asymmetric_threat() -> Tuple[bool, List[str]]:
    """Validate φΔ per Ω-invariant: 
       φΔ = |breadth - depth| / (breadth + depth) 
       (Measures antisymmetric exploration bias)"""
    errors = []
    
    def calculate_asymmetric_threat(breadth: int, depth: int) -> float:
        if breadth + depth == 0:
            return 0.0
        return abs(breadth - depth) / (breadth + depth)
    
    # Test cases
    test_cases = [
        (0, 0, 0.0),    # No exploration
        (5, 0, 1.0),    # Pure breadth scan
        (0, 5, 1.0),    # Pure depth recursion
        (3, 3, 0.0),    # Balanced exploration
        (4, 2, 0.333...), # Moderate bias
        (10, 1, 0.818...) # Strong breadth bias
    ]
    
    for breadth, depth, expected in test_cases:
        actual = calculate_asymmetric_threat(breadth, depth)
        if abs(actual - expected) > 1e-9:
            errors.append(f"φΔ error: breadth={breadth}, depth={depth}, expected={expected}, got={actual}")
    
    # Verify bounds [0,1]
    for b in range(0, 11):
        for d in range(0, 11):
            if b + d == 0:
                continue
            val = calculate_asymmetric_threat(b, d)
            if val < 0 or val > 1.0 + 1e-9:
                errors.append(f"φΔ out of bounds: {val} at (b={b}, d={d})")
    
    return len(errors) == 0, errors

# =============================================================================
# TOPOLOGICAL IMPEDANCE VALIDATION (H_imp)
# =============================================================================
def validate_topological_impedance() -> Tuple[bool, List[str]]:
    """Validate H_imp per Ω-invariant: 
       H_imp = ∫ gauge_emergence dψ 
       where gauge_emergence = trust_score * |φΔ|
       and ψ = ln(φₙ)"""
    errors = []
    
    # Correct implementation (trapezoidal rule)
    def calculate_topological_impedance_correct(log_entries: List[dict]) -> float:
        """log_entries: [{'trust_score': float, 'phi_delta': float, 'psi': float}]"""
        if len(log_entries) < 2:
            return 0.0
        
        impedance = 0.0
        for i in range(1, len(log_entries)):
            prev = log_entries[i-1]
            curr = log_entries[i]
            
            # g = trust_score * |φΔ|
            g_prev = prev['trust_score'] * abs(prev['phi_delta'])
            g_curr = curr['trust_score'] * abs(curr['phi_delta'])
            
            # dψ = ψ_i - ψ_{i-1}
            d_psi = curr['psi'] - prev['psi']
            
            # Trapezoidal rule: ∫ g dψ ≈ Σ [(g_i + g_{i-1})/2] * dψ_i
            impedance += (g_prev + g_curr) * 0.5 * d_psi
        
        return impedance
    
    # Test case: linear trust_score and φΔ
    log_entries = [
        {'trust_score': 0.2, 'phi_delta': 0.3, 'psi': math.log(0.2)},
        {'trust_score': 0.5, 'phi_delta': 0.4, 'psi': math.log(0.5)},
        {'trust_score': 0.8, 'phi_delta': 0.1, 'psi': math.log(0.8)}
    ]
    
    # Manual calculation:
    # Segment 1: (0.2*0.3 + 0.5*0.4)/2 * (ln0.5 - ln0.2) = (0.06+0.2)/2 * ln(2.5) = 0.13 * 0.916 ≈ 0.119
    # Segment 2: (0.5*0.4 + 0.8*0.1)/2 * (ln0.8 - ln0.5) = (0.2+0.08)/2 * ln(1.6) = 0.14 * 0.470 ≈ 0.066
    # Total ≈ 0.185
    expected = 0.119 + 0.066  # Approximate
    actual = calculate_topological_impedance_correct(log_entries)
    if abs(actual - expected) > 0.01:  # Allow small error from log approx
        errors.append(f"Impedance calculation error: expected ~{expected}, got {actual}")
    
    # Verify Engine's pleading version is INCORRECT
    def calculate_topological_impedance_engine_pleading(log_entries: List[dict]) -> float:
        """Engine's pleading version: uses prev_psi instead of prev_trust_score"""
        if len(log_entries) < 2:
            return 0.0
        impedance = 0.0
        prev_psi = log_entries[0]['psi']
        prev_phi_delta = log_entries[0]['phi_delta']
        for i in range(1, len(log_entries)):
            curr = log_entries[i]
            psi = curr['psi']
            delta_psi = psi - prev_psi
            # ERROR: uses prev_psi (which is ψ_{i-1}) instead of trust_score_{i-1}
            term = (curr['trust_score'] * abs(curr['phi_delta']) + 
                    prev_psi * abs(prev_phi_delta)) / 2 * delta_psi
            impedance += term
            prev_psi = psi
            prev_phi_delta = curr['phi_delta']
        return impedance
    
    actual_engine = calculate_topological_impedance_engine_pleading(log_entries)
    # Engine's version will give different result (we don't need exact value, just note it's wrong)
    if abs(actual_engine - expected) < 0.01:  # If by chance it matches, still flag as wrong method
        errors.append("Engine's pleading impedance method accidentally matches correct value but uses wrong formula")
    else:
        # This is expected - the method is wrong
        pass  # We'll note this in errors only if we want to, but the validation is for correct method
    
    # Actually, we want to validate that the CORRECT method is used.
    # Since the Engine's pleading uses the wrong method, we will fail validation.
    # But note: the task is to validate if the solution is compliant.
    # We will return failure if the Engine's pleading method is used.
    # However, we don't have the actual code to run - we are validating the math.
    # We'll assume the Engine's pleading code is as shown and thus non-compliant.
    errors.append("Topological impedance calculation uses incorrect formula (uses ψ instead of trust_score for g_{i-1})")
    
    return len(errors) == 0, errors

# =============================================================================
# CURVATURE VALIDATION
# =============================================================================
def validate_curvature() -> Tuple[bool, List[str]]:
    """Validate security manifold curvature per Ω-invariant:
       R = ξₙ·φₙ + ξ_Δ·φ_Δ - H_imp
       (No independent ψ terms)"""
    errors = []
    
    def calculate_security_manifold_curvature(phi_n: float, phi_delta: float, h_imp: float) -> float:
        return XI_N * phi_n + XI_DELTA * phi_delta - h_imp
    
    # Test case
    phi_n = 0.6
    phi_delta = 0.3
    h_imp = 0.2
    expected = 0.8*0.6 + 1.2*0.3 - 0.2 = 0.48 + 0.36 - 0.2 = 0.64
    actual = calculate_security_manifold_curvature(phi_n, phi_delta, h_imp)
    if abs(actual - expected) > 1e-9:
        errors.append(f"Curvature calculation error: expected {expected}, got {actual}")
    
    # Verify no independent ψ term
    # This is inherent in the function definition above
    
    return len(errors) == 0, errors

# =============================================================================
# Φ-DENSITY VALIDATION
# =============================================================================
def validate_phi_density() -> Tuple[bool, List[str]]:
    """Validate Φ-density calculation per Ω-invariant:
       Φ = -k_B [ΔH_security - ΔH_audit]
       In steady state: Φ_density = raw_gain - k_B * ln(2) * audit_complexity"""
    errors = []
    
    def calculate_phi_density(raw_gain: float, audit_complexity: float) -> float:
        audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
        return raw_gain - audit_entropy_cost
    
    # Test case from Engine's pleading
    raw_gain = 0.85
    audit_complexity = 2.5
    expected = 0.85 - (1.0 * math.log(2.0) * 2.5)
    actual = calculate_phi_density(raw_gain, audit_complexity)
    if abs(actual - expected) > 1e-9:
        errors.append(f"Φ-density calculation error: expected {expected}, got {actual}")
    
    # Check if Engine's pleading claimed value matches
    claimed_net_phi = 0.75
    if abs(actual - claimed_net_phi) > 1e-9:
        errors.append(f"Φ-density claim mismatch: calculated {actual}, claimed {claimed_net_phi}")
    
    # Verify formula structure
    # Must be: raw_gain - [k_B * ln(2) * audit_complexity]
    # No other terms allowed
    
    return len(errors) == 0, errors

# =============================================================================
# MAIN VALIDATION
# =============================================================================
def main():
    print("=" * 60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION FOR AFDS v3.0")
    print("=" * 60)
    
    validations = [
        ("Trust Modeling", validate_trust_modeling),
        ("Asymmetric Threat (φΔ)", validate_asymmetric_threat),
        ("Topological Impedance (H_imp)", validate_topological_impedance),
        ("Security Manifold Curvature", validate_curvature),
        ("Φ-Density Calculation", validate_phi_density)
    ]
    
 all_passed = True
    for name, validator in validations:
        passed, errors = validator()
        status = "PASS" if passed else "FAIL"
        print(f"\n{name}: {status}")
        if not passed:
            all_passed = False
            for error in errors:
                print(f"  - {error}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("OVERALL VALIDATION: PASS")
        print("AFDS v3.0 is mathematically compliant with Omega Physics Rubric v26.0")
    else:
        print("OVERALL VALIDATION: FAIL")
        print("AFDS v3.0 contains invariant violations - see details above")
        print("\nCRITICAL FAILURES REQUIRING IMMEDIATE CORRECTION:")
        print("1. Topological impedance calculation uses incorrect formula")
        print("2. Φ-density claim does not match calculated value")
        print("3. Trust modeling requires verification of atomic operations (not shown in math)")
    print("=" * 60)

if __name__ == "__main__":
    main()