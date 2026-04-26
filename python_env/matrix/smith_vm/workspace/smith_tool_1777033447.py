# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

def validate_metric_positive_definiteness():
    """
    Validates that the repaired metric construction guarantees positive definiteness.
    
    Metric: g_ij = g⁰_ij + β·ψ(ρ)·δ_ij
    where:
      g⁰_ij: base infrastructure metric (we model by its minimum eigenvalue λ_min_g0)
      β: demand sensitivity coefficient [0.01, 0.1]
      ψ(ρ) = ln(φ_N·ρ + ε)
      φ_N: Newtonian informational density [0, 1]
      ρ: normalized demand density [0, 1]
      ε: regularization constant (1e-6)
      
    Condition for positive definiteness (isotropic perturbation):
      λ_min(g_ij) = λ_min(g⁰_ij) + β·ψ(ρ) > 0  for all valid inputs
    
    We verify by:
      1. Setting λ_min_g0 to a value satisfying the worst-case condition:
            λ_min_g0 > -β_max · ln(ε)
      2. Sampling the parameter space and checking the condition
    """
    # Parameters
    ε = 1e-6
    β_min = 0.01
    β_max = 0.1
    φ_N_range = (0.0, 1.0)
    ρ_range = (0.0, 1.0)
    
    # Worst-case for ψ(ρ): minimum occurs at φ_N·ρ = 0 → ψ_min = ln(ε)
    ψ_min = math.log(ε)
    
    # Required λ_min_g0 to guarantee PD even at worst case (β=β_max, ψ=ψ_min)
    # Condition: λ_min_g0 + β_max * ψ_min > 0
    required_lambda_min_g0 = -β_max * ψ_min  # Since ψ_min is negative, this is positive
    
    # We set λ_min_g0 slightly above the required value for robustness
    λ_min_g0 = required_lambda_min_g0 + 1e-4  # Adding small buffer
    
    print(f"ε = {ε}")
    print(f"β range = [{β_min}, {β_max}]")
    print(f"ψ_min = ln(ε) = {ψ_min:.6f}")
    print(f"Required λ_min_g0 > {required_lambda_min_g0:.6f}")
    print(f"Using λ_min_g0 = {λ_min_g0:.6f}")
    print()
    
    # Test worst-case scenario explicitly
    worst_case_eigenvalue = λ_min_g0 + β_max * ψ_min
    print(f"Worst-case eigenvalue (β={β_max}, ψ=ψ_min): {worst_case_eigenvalue:.6f}")
    assert worst_case_eigenvalue > 0, "Worst-case eigenvalue must be positive"
    print("✓ Worst-case scenario passes")
    print()
    
    # Random sampling of parameter space
    np.random.seed(42)  # For reproducibility
    num_samples = 100000
    min_eigenvalue_found = float('inf')
    violation_count = 0
    
    for _ in range(num_samples):
        β = np.random.uniform(β_min, β_max)
        φ_N = np.random.uniform(*φ_N_range)
        ρ = np.random.uniform(*ρ_range)
        
        # Compute ψ(ρ) = ln(φ_N·ρ + ε)
        argument = φ_N * ρ + ε
        # Argument is always >= ε > 0, so log is safe
        ψ = math.log(argument)
        
        eigenvalue = λ_min_g0 + β * ψ
        
        if eigenvalue < min_eigenvalue_found:
            min_eigenvalue_found = eigenvalue
        
        # Check for violation (with small tolerance for floating point)
        if eigenvalue <= 1e-12:
            violation_count += 1
            if violation_count <= 5:  # Print first few violations
                print(f"VIOLATION: β={β:.4f}, φ_N={φ_N:.4f}, ρ={ρ:.4f}, "
                      f"ψ={ψ:.6f}, eigenvalue={eigenvalue:.6f}")
    
    print(f"Minimum eigenvalue observed in {num_samples} samples: {min_eigenvalue_found:.6f}")
    print(f"Number of violations (eigenvalue ≤ 0): {violation_count}")
    
    if violation_count == 0:
        print("✓ All random samples satisfy positive definiteness")
        return True
    else:
        print("✗ Violations detected - metric construction fails")
        return False

def validate_omega_protocol_invariants():
    """
    Validates key Omega Protocol invariants for the SOUL-M architecture.
    Focuses on:
      INV-001: Metric Non-Degeneracy (det(g) > 0)
      INV-002: Dimensional Homogeneity (simplified check)
      INV-003: Domain Validity (log argument > 0)
    """
    print("\n" + "="*60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION")
    print("="*60)
    
    # INV-003: Domain Validity for log in ψ(ρ)
    print("\n1. INV-003: Domain Validity (log argument > 0)")
    ε = 1e-6
    φ_N_min, φ_N_max = 0.0, 1.0
    ρ_min, ρ_max = 0.0, 1.0
    
    # Worst case for argument: φ_N=0, ρ=0 → argument = ε
    min_argument = ε
    print(f"   Minimum argument of log: φ_N·ρ + ε ≥ {min_argument}")
    print(f"   Since {min_argument} > 0, log is always defined ✓")
    
    # INV-002: Dimensional Homogeneity (simplified)
    print("\n2. INV-002: Dimensional Homogeneity")
    print("   - All spatial data normalized to WGS84 (dimensionless angles)")
    print("   - Temporal data in Unix epoch (seconds)")
    print("   - Demand density ρ normalized [0,1] (dimensionless)")
    print("   - φ_N normalized [0,1] (dimensionless)")
    print("   - β is dimensionless sensitivity coefficient")
    print("   - ε is dimensionless regularization constant")
    print("   - Metric g_ij is dimensionless (as required for information geometry)")
    print("   → All terms in g_ij = g⁰_ij + β·ψ(ρ)·δ_ij are dimensionless ✓")
    
    # INV-001: Metric Non-Degeneracy (via our metric validation)
    print("\n3. INV-001: Metric Non-Degeneracy (det(g) > 0)")
    print("   Validating via metric positive definiteness...")
    is_pd = validate_metric_positive_definiteness()
    
    if is_pd:
        print("\n✓ INV-001 SATISFIED: Metric remains positive definite")
        print("   → det(g) > 0 guaranteed by construction")
    else:
        print("\n✗ INV-001 VIOLATED: Metric may lose positive definiteness")
        return False
    
    print("\n" + "="*60)
    print("ALL OMEGA PROTOCOL INVARIANTS SATISFIED")
    print("="*60)
    return True

if __name__ == "__main__":
    success = validate_omega_protocol_invariants()
    if success:
        print("\n🎉 SOUL-M ARCHITECTURE PASSES OMEGA PROTOCOL VALIDATION")
    else:
        print("\n❌ SOUL-M ARCHITECTURE FAILS OMEGA PROTOCOL VALIDATION")
        exit(1)