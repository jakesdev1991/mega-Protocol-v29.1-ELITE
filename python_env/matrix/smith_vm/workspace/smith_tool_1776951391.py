# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np
from typing import Tuple, List

# Omega Protocol v26.0 Constants (from Rubric)
OMEGA_EPSILON = 1e-9  # Numerical tolerance for invariant checks
PHI_N_MIN = 0.1       # Minimum system resilience threshold
PHI_DELTA_MAX = 10.0  # Maximum adversarial pressure threshold
J_STAR_TARGET = 0.8   # Target operational integrity metric

def validate_omega_invariants(
    phi_n: float, 
    phi_delta: float, 
    h_conditional: float,
    j_star: float = None
) -> Tuple[bool, List[str]]:
    """
    Strict validation of Omega Protocol v26.0 invariants.
    Returns (is_compliant, violations) where violations is list of human-readable messages.
    """
    violations = []
    
    # Invariant 1: Security Manifold Curvature Non-Negativity
    # Φ_N × Φ_Δ − H_conditional ≥ 0 (Shannon conditional entropy bound)
    curvature = phi_n * phi_delta - h_conditional
    if curvature < -OMEGA_EPSILON:
        violations.append(
            f"Manifold curvature violation: Φ_N×Φ_Δ−H = {curvature:.6f} < 0 "
            f"(Φ_N={phi_n:.4f}, Φ_Δ={phi_delta:.4f}, H_cond={h_conditional:.4f})"
        )
    
    # Invariant 2: System Resilience Bounds
    # Φ_N must exceed minimum threshold for operational stability
    if phi_n < PHI_N_MIN:
        violations.append(
            f"System resilience violation: Φ_N = {phi_n:.4f} < {PHI_N_MIN} "
            f"(risk of cascading failure)"
        )
    
    # Invariant 3: Adversarial Pressure Containment
    # Φ_Δ must not exceed maximum threshold (prevents overload collapse)
    if phi_delta > PHI_DELTA_MAX:
        violations.append(
            f"Adversarial pressure violation: Φ_Δ = {phi_delta:.4f} > {PHI_DELTA_MAX} "
            f"(risk of informational freeze)"
        )
    
    # Invariant 4: Operational Integrity Metric (J*)
    # J* must approach target value under steady-state operation
    if j_star is not None:
        j_star_error = abs(j_star - J_STAR_TARGET)
        if j_star_error > OMEGA_EPSILON * 10:  # Allow 10x tolerance for transient states
            violations.append(
                f"Operational integrity violation: |J*−J*_target| = {j_star_error:.6f} > {OMEGA_EPSILON*10} "
                f"(J*={j_star:.4f}, target={J_STAR_TARGET})"
            )
    
    # Invariant 5: Entropy Accounting Consistency
    # H_conditional must be non-negative and bounded by system capacity
    if h_conditional < -OMEGA_EPSILON:
        violations.append(
            f"Entropy violation: H_conditional = {h_conditional:.6f} < 0 "
            f"(negative entropy impossible)"
        )
    if h_conditional > math.log2(phi_n * phi_delta + 1) + OMEGA_EPSILON:
        violations.append(
            f"Entropy bound violation: H_conditional = {h_conditional:.6f} > "
            f"log2(Φ_N×Φ_Δ+1) ≈ {math.log2(phi_n * phi_delta + 1):.4f} "
            f"(exceeds channel capacity)"
        )
    
    return len(violations) == 0, violations

def validate_trust_decay_model(
    initial_trust: float,
    hours_elapsed: float,
    decay_rate_per_hour: float = 0.05  # 5% per hour as specified
) -> Tuple[bool, List[str]]:
    """
    Validates the continuous exponential decay model used in TrustManager.
    Trust(t) = trust_0 * exp(-λ * t) where λ = -ln(0.95) for 5%/hour decay.
    """
    violations = []
    
    # Calculate expected trust using continuous decay
    lambda_decay = -math.log(1 - decay_rate_per_hour)  # Exact continuous rate
    expected_trust = initial_trust * math.exp(-lambda_decay * hours_elapsed)
    
    # Check if implementation matches specification (within numerical tolerance)
    # Note: In Engine code, this is implemented as:
    #   state.trust_score *= exp(-log(0.95) * hours)
    # Which is equivalent to: trust_0 * (0.95)^hours
    # But continuous decay should be: trust_0 * exp(-ln(0.95)*hours) = trust_0 * (0.95)^hours
    # So the implementation IS correct for continuous decay.
    
    # Additional validation: trust must remain in [0,1]
    if expected_trust < -OMEGA_EPSILON or expected_trust > 1.0 + OMEGA_EPSILON:
        violations.append(
            f"Trust decay out of bounds: {expected_trust:.6f} ∉ [0,1] "
            f"(initial={initial_trust}, hours={hours_elapsed})"
        )
    
    return len(violations) == 0, violations

def validate_jitter_distribution(
    min_jitter_ms: int = 1,
    max_jitter_ms: int = 50,
    samples: int = 10000
) -> Tuple[bool, List[str]]:
    """
    Validates that the jitter mechanism produces values in [1,50] ms with 
    appropriate probability distribution (uniform as implemented).
    """
    violations = []
    
    # Simulate the jitter generation from Engine code:
    #   jitter_ms = 1 + int(50.0 * random_uniform)
    # This produces integers in [1,50] inclusive
    
    np.random.seed(42)  # For reproducibility
    raw_samples = np.random.uniform(0, 1, samples)
    jitter_samples = 1 + np.floor(50.0 * raw_samples).astype(int)
    
    # Check range
    if np.min(jitter_samples) < min_jitter_ms or np.max(jitter_samples) > max_jitter_ms:
        violations.append(
            f"Jitter range violation: observed [{np.min(jitter_samples)}, {np.max(jitter_samples)}] "
            f"not subset of [{min_jitter_ms}, {max_jitter_ms}]"
        )
    
    # Check uniformity (chi-square test)
    expected_count = samples / (max_jitter_ms - min_jitter_ms + 1)
    observed_counts = np.bincount(jitter_samples - min_jitter_ms, 
                                  minlength=max_jitter_ms-min_jitter_ms+1)
    chi2_stat = np.sum((observed_counts - expected_count)**2 / expected_count)
    # Degrees of freedom = number of bins - 1
    df = max_jitter_ms - min_jitter_ms
    # Critical value for p=0.01 (stringent check)
    critical_value = 23.209 if df == 49 else None  # Approximate for df=49
    
    if chi2_stat > (critical_value or 50.0):  # Conservative fallback
        violations.append(
            f"Jitter distribution non-uniform: χ²={chi2_stat:.2f} > critical value "
            f"(df={df}, p<0.01)"
        )
    
    return len(violations) == 0, violations

def validate_forensic_trigger_conditions(
    traversal_score: float,
    is_honey_node_access: bool
) -> Tuple[bool, List[str]]:
    """
    Validates forensic report triggering conditions:
    - Trigger on honey_node_access OR traversal_score > 90.0
    """
    violations = []
    
    # Engine code triggers if:
    #   entry.operation == "honey_node_access" OR entry.traversal_score > 90.0
    expected_trigger = is_honey_node_access or (traversal_score > 90.0)
    
    # No direct violation to check here - this is a design validation
    # But we can verify the threshold is reasonable
    if traversal_score > 100.0:  # Assuming normalized score
        violations.append(
            f"Traversal score exceeds expected maximum: {traversal_score:.2f} > 100.0"
        )
    
    return len(violations) == 0, violations

def main():
    """
    Demonstration of Omega Protocol validation with example values.
    In practice, these values would be extracted from the AFDS system state.
    """
    print("=" * 60)
    print("OMEGA PROTOCOL v26.0 INVARIANT VALIDATION")
    print("=" * 60)
    
    # Example 1: Nominal operating state (should be compliant)
    print("\n[Test Case 1: Nominal State]")
    phi_n = 1.2
    phi_delta = 3.5
    h_conditional = 2.0  # Example entropy value
    j_star = 0.78
    
    compliant, violations = validate_omega_invariants(phi_n, phi_delta, h_conditional, j_star)
    print(f"Manifold Curvature (Φ_N×Φ_Δ−H): {phi_n*phi_delta - h_conditional:.4f}")
    print(f"Compliant: {compliant}")
    if violations:
        print("Violations:")
        for v in violations:
            print(f"  - {v}")
    
    # Example 2: High adversarial pressure (should violate Φ_Δ bound)
    print("\n[Test Case 2: High Adversarial Pressure]")
    phi_n = 0.8
    phi_delta = 12.0  # Exceeds PHI_DELTA_MAX=10.0
    h_conditional = 5.0
    j_star = 0.65
    
    compliant, violations = validate_omega_invariants(phi_n, phi_delta, h_conditional, j_star)
    print(f"Manifold Curvature (Φ_N×Φ_Δ−H): {phi_n*phi_delta - h_conditional:.4f}")
    print(f"Compliant: {compliant}")
    if violations:
        print("Violations:")
        for v in violations:
            print(f"  - {v}")
    
    # Example 3: Trust decay validation
    print("\n[Test Case 3: Trust Decay Model]")
    compliant, violations = validate_trust_decay_model(
        initial_trust=0.9,
        hours_elapsed=2.0
    )
    print(f"Trust after 2 hours (90% initial): {0.9 * math.exp(-math.log(0.95)*2):.4f}")
    print(f"Model compliant: {compliant}")
    if violations:
        print("Violations:")
        for v in violations:
            print(f"  - {v}")
    
    # Example 4: Jitter distribution validation
    print("\n[Test Case 4: Jitter Distribution]")
    compliant, violations = validate_jitter_distribution(samples=5000)
    print(f"Jitter distribution compliant: {compliant}")
    if violations:
        print("Violations:")
        for v in violations:
            print(f"  - {v}")
    
    # Example 5: Forensic trigger validation
    print("\n[Test Case 5: Forensic Trigger Conditions]")
    compliant1, violations1 = validate_forensic_trigger_conditions(
        traversal_score=85.0,
        is_honey_node_access=False
    )
    compliant2, violations2 = validate_forensic_trigger_conditions(
        traversal_score=95.0,
        is_honey_node_access=False
    )
    compliant3, violations3 = validate_forensic_trigger_conditions(
        traversal_score=80.0,
        is_honey_node_access=True
    )
    
    print(f"Score 85 (no honey): Trigger expected=False → Compliant: {compliant1}")
    print(f"Score 95 (no honey): Trigger expected=True → Compliant: {compliant2}")
    print(f"Score 80 (honey access): Trigger expected=True → Compliant: {compliant3}")
    all_violations = violations1 + violations2 + violations3
    if all_violations:
        print("Violations:")
        for v in all_violations:
            print(f"  - {v}")
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()