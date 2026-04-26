# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

def validate_soul_m_metric():
    """
    Validates the pleaded SOUL-M metric construction against Omega Protocol invariant INV-001 (non-degeneracy).
    
    Pleaded metric: g_ij = g⁰_ij + β·ψ(ρ)·δ_ij, where ψ(ρ) = ln(φ_N·ρ + ε)
    Pleaded parameters:
        β ∈ [0.01, 0.1] (demand sensitivity)
        φ_N ∈ [0, 1] (Newtonian informational density, normalized)
        ρ ∈ [0, 1] (demand density, normalized)
        ε = 1e-6 (regularization)
    
    INV-001 requires: det(g) > 0 for all valid parameter combinations.
    
    Since perturbation is β·ψ(ρ) times identity matrix, eigenvalues of g are:
        λ_i(g⁰) + β·ψ(ρ)
    Thus, g is PD iff: min_i λ_i(g⁰) + min_{β,φ_N,ρ}[β·ψ(ρ)] > 0
    
    Given β ≥ 0 and ψ(ρ) increasing in φ_N,ρ:
        min[β·ψ(ρ)] occurs at β=β_max, φ_N=0, ρ=0 → ψ(ρ)=ln(ε)
    
    Validation condition: λ_min(g⁰) + β_max·ln(ε) > 0
    """
    # Pleaded parameters
    ε = 1e-6
    β_min, β_max = 0.01, 0.1
    φ_N_min, φ_N_max = 0.0, 1.0
    ρ_min, ρ_max = 0.0, 1.0
    
    # Critical values for worst-case analysis
    ψ_min = math.log(ε)  # ln(ε) < 0
    worst_case_perturbation = β_max * ψ_min  # Most negative perturbation
    required_λ_min = -worst_case_perturbation  # = β_max * |ln(ε)|
    
    # Test with realistic base metric eigenvalues (from urban logistics infrastructure)
    test_cases = [
        ("Euclidean 2D (lat/lon)", 1.0),          # g⁰ = I → λ_min=1.0
        ("Weak infrastructure", 0.5),             # Degraded roads/network
        ("Threshold case", required_λ_min),       # Exact boundary
        ("Robust infrastructure", 2.0),           # Strong grid
        ("Over-engineered", 5.0)                  # Redundant capacity
    ]
    
    print("OMEGA PROTOCOL INV-001 VALIDATION: SOUL-M METRIC CONSTRUCTION")
    print("=" * 70)
    print(f"Pleaded parameters: β∈[{β_min},{β_max}], φ_N∈[{φ_N_min},{φ_N_max}], ρ∈[{ρ_min},{ρ_max}], ε={ε}")
    print(f"Worst-case perturbation: β_max·ln(ε) = {β_max:.4f} × {ψ_min:.6f} = {worst_case_perturbation:.6f}")
    print(f"Required λ_min(g⁰) > {required_λ_min:.6f} for INV-001 to hold\n")
    
    all_passed = True
    for name, λ_min in test_cases:
        min_eigenvalue_g = λ_min + worst_case_perturbation
        passed = min_eigenvalue_g > 0
        status = "PASS" if passed else "FAIL (INV-001 VIOLATED)"
        print(f"{name:25} | λ_min(g⁰)={λ_min:6.3f} | min λ(g)={min_eigenvalue_g:8.6f} | {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("RESULT: INV-001 SATISFIED for all test cases.")
        print("        Metric construction is mathematically sound under pleaded parameters.")
    else:
        print("RESULT: INV-001 VIOLATED in some test cases.")
        print("        Metric construction is NOT mathematically sound as pleaded.")
        print(f"        REQUIRED: λ_min(g⁰) > {required_λ_min:.6f} to guarantee non-degeneracy.")
        print("        OMEGA PROTOCOL VIOLATION: Invariant not enforced by construction.")
    
    print("\nKEY FINDING:")
    print("The pleaded repair falsely claimed β·ψ(ρ)·δ_ij is PSD (non-negative).")
    print("In reality, ψ(ρ) < 0 when φ_N·ρ < 1-ε (e.g., low demand), making perturbation NEGATIVE.")
    print("Thus, INV-001 holds ONLY if base metric has sufficiently large minimum eigenvalue.")
    print("This contradicts the pleaded claim of invariant safety 'by construction'.")

if __name__ == "__main__":
    validate_soul_m_metric()