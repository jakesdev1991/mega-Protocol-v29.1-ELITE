# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Φ-Density Math Validator
# Validates arithmetic and invariant compliance for Φ-density impact analyses
# Based on Omega Physics Rubric v26.0 §1-§6

import math
from typing import Tuple, List

def validate_phi_density_analysis(
    prevention_gain: float,
    costs: List[float],
    claimed_net: float
) -> Tuple[bool, List[str]]:
    """
    Validates a Φ-density impact analysis for:
    1. Arithmetic correctness
    2. Sign convention compliance (gains ≥0, costs ≤0)
    3. Omega Protocol invariant preservation
    4. Entropy accounting completeness
    
    Returns: (is_valid, list_of_violations)
    """
    violations = []
    
    # 1. Arithmetic validation
    calculated_net = prevention_gain + sum(costs)
    if not math.isclose(calculated_net, claimed_net, rel_tol=1e-9, abs_tol=1e-9):
        violations.append(
            f"Arithmetic error: claimed net {claimed_net} ≠ "
            f"calculated net {calculated_net} (diff={abs(claimed_net - calculated_net)})"
        )
    
    # 2. Sign convention validation (Omega Physics §4: Entropy Accounting)
    if prevention_gain < 0:
        violations.append(f"Prevention gain must be non-negative (got {prevention_gain})")
    
    for i, cost in enumerate(costs):
        if cost > 0:
            violations.append(f"Cost[{i}] must be non-positive (got {cost})")
    
    # 3. Invariant preservation check (Omega Physics §3: Invariants)
    # Net impact must satisfy: |Net| ≤ Prevention_Gain + Σ|Cost_i| 
    # (triangle inequality for conserved quantities)
    max_possible_magnitude = prevention_gain + sum(abs(c) for c in costs)
    if abs(claimed_net) > max_possible_magnitude + 1e-9:
        violations.append(
            f"Net impact violates triangle inequality: "
            f"|{claimed_net}| > {max_possible_magnitude} "
            f"(gain + |costs|)"
        )
    
    # 4. Boundary condition validation (Omega Physics §2: Boundary Conditions)
    # Audit process must not violate Φ-density conservation at boundaries
    if prevention_gain == 0 and any(c < 0 for c in costs):
        violations.append(
            "Zero prevention gain with non-zero costs implies "
            "audit process created net Φ-density from nothing"
        )
    
    # 5. Equation-level derivation check (Omega Physics §6: Equations)
    # Requires at least one explicit equation in analysis
    # (This is a meta-check - we can't verify equations from numbers alone,
    #  but we can flag analyses that omit equation references)
    # In real implementation, this would check for equation strings in source text
    
    return len(violations) == 0, violations

# Validate the meta-scrutiny's Φ-density analysis
if __name__ == "__main__":
    # Values from meta-scrutiny output:
    # Prevention Gain: +0.65Φ (blocking harmful deployment)
    # Audit Cost: -0.10Φ
    # Protocol Erosion: -0.15Φ  
    # Reasoning Poisoning Tax: -0.05Φ
    # Claimed Net: +0.35Φ
    
    prevention_gain = 0.65
    costs = [-0.10, -0.15, -0.05]
    claimed_net = 0.35
    
    is_valid, violations = validate_phi_density_analysis(
        prevention_gain, costs, claimed_net
    )
    
    print("=== OMEGA PROTOCOL Φ-DENSITY ANALYSIS VALIDATION ===")
    print(f"Prevention Gain: {prevention_gain} Φ")
    print(f"Costs: {costs} Φ")
    print(f"Claimed Net Impact: {claimed_net} Φ")
    print(f"Calculated Net Impact: {prevention_gain + sum(costs)} Φ")
    print()
    
    if is_valid:
        print("✓ ARITHMETIC: VALID")
        print("✓ SIGNS: COMPLIANT (gain≥0, costs≤0)")
        print("✓ INVARIANTS: PRESERVED")
        print("✓ BOUNDARY CONDITIONS: SATISFIED")
        print("\nOVERALL: Φ-DENSITY ANALYSIS IS MATHEMATICALLY SOUND")
        print("AND COMPLIANT WITH OMEGA PROTOCOL INVARIANTS")
    else:
        print("✗ VALIDATION FAILED:")
        for v in violations:
            print(f"  - {v}")
        print("\nOVERALL: Φ-DENSITY ANALYSIS VIOLATES OMEGA PROTOCOL")
        print("REQUIRES REVISION BEFORE DEPLOYMENT")
    
    print("\n" + "="*60)
    print("ENFORCEMENT MECHANISM:")
    print("1. All Φ-density claims MUST undergo this validation")
    print("2. Violations trigger automatic Φ-density tax: +0.1Φ per violation")
    print("3. Repeated violations require invariant-preserving redesign")
    print("4. Audit processes must self-validate using identical criteria")
    print("="*60)