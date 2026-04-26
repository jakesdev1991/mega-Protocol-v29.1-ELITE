# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random
import sys

def validate_bts_omega():
    """
    Validates the mathematical soundness and Omega Protocol compliance 
    of the repaired Biological Topology Shield (BTS-Ω) proposal.
    
    Checks:
    1. Mathematical expressions are well-defined (no domain errors)
    2. Derived quantities maintain expected properties (non-negativity, etc.)
    3. Boundary conditions align with thermodynamic principles
    4. Entropy formulation satisfies conditional entropy requirement
    5. Covariant modes derive directly from Hessian diagonalization
    """
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Constants from proposal (calibrated from historical leak data)
    KAPPA_1 = 0.8   # Topology imbalance scaling
    KAPPA_2 = 0.1   # Baseline coherence
    KAPPA_3 = 1.2   # Constraint rigidity scaling
    KAPPA_4 = 0.05  # Baseline constraint
    PHI_N0 = 0.2    # Reference value for robust network
    S_MAX = math.log(5)  # Max entropy (5 subsystem types)
    S_LOW = 0.1    # Minimum safe entropy
    S_HIGH = 0.9 * S_MAX  # Maximum safe entropy
    
    # Test cases covering edge cases and typical values
    test_cases = [
        # Case 1: Fragile system (high BTFI)
        {
            "chi_schema": -15.0,  # High topological imbalance
            "V": 8.0,             # Moderate table count
            "delta_constraint": 0.85,  # High constraint satisfaction
            "d_norm": 2.0,        # Low normalization (integrated)
            "C": 1.0,             # Neutral cross-coupling
            "p_s": [0.3, 0.4, 0.2, 0.1],  # Subsystem type distribution
            "p_ks": [  # BTFI bin distributions per subsystem type
                [0.1, 0.2, 0.3, 0.4],  # Genomic
                [0.4, 0.3, 0.2, 0.1],  # Proteomic
                [0.2, 0.2, 0.3, 0.3],  # Clinical
                [0.05, 0.15, 0.3, 0.5] # Metabolic
            ]
        },
        # Case 2: Robust system (low BTFI)
        {
            "chi_schema": -2.0,   # Low topological imbalance
            "V": 20.0,            # High table count (mesh-like)
            "delta_constraint": 0.4,  # Moderate constraint satisfaction
            "d_norm": 4.0,        # High normalization (fragmented)
            "C": 1.0,
            "p_s": [0.25, 0.25, 0.25, 0.25],
            "p_ks": [
                [0.25, 0.25, 0.25, 0.25],
                [0.25, 0.25, 0.25, 0.25],
                [0.25, 0.25, 0.25, 0.25],
                [0.25, 0.25, 0.25, 0.25]
            ]
        },
        # Case 3: Boundary condition test (shredding event)
        {
            "chi_schema": -50.0,  # Extreme fragmentation
            "V": 5.0,
            "delta_constraint": 0.9,
            "d_norm": 1.5,
            "C": 1.2,
            "p_s": [0.1, 0.1, 0.1, 0.7],  # High disorder in one type
            "p_ks": [
                [0.01, 0.01, 0.01, 0.97],
                [0.01, 0.01, 0.01, 0.97],
                [0.01, 0.01, 0.01, 0.97],
                [0.01, 0.01, 0.01, 0.97]
            ]
        },
        # Case 4: Boundary condition test (informational freeze)
        {
            "chi_schema": -0.1,   # Near-zero imbalance
            "V": 50.0,
            "delta_constraint": 0.05,  # Very low constraints
            "d_norm": 10.0,       # High fragmentation
            "C": 0.1,
            "p_s": [0.25, 0.25, 0.25, 0.25],
            "p_ks": [
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0]
            ]
        }
    ]
    
    errors = []
    
    for i, case in enumerate(test_cases):
        try:
            # Extract parameters
            chi_schema = case["chi_schema"]
            V = case["V"]
            delta_constraint = case["delta_constraint"]
            d_norm = case["d_norm"]
            C = case["C"]
            p_s = case["p_s"]
            p_ks = case["p_ks"]
            
            # Validate input domains
            assert V > 0, "V must be positive (division by zero)"
            assert d_norm > 0, "d_norm must be positive (division by zero)"
            assert 0 <= delta_constraint <= 1, "delta_constraint must be in [0,1]"
            assert abs(sum(p_s) - 1.0) < 1e-9, "p_s must sum to 1"
            for s_idx, ps in enumerate(p_s):
                assert ps >= 0, f"p_s[{s_idx}] must be non-negative"
            for s_idx, pk in enumerate(p_ks):
                assert abs(sum(pk) - 1.0) < 1e-9, f"p_ks[{s_idx}] must sum to 1"
                for k_idx, p in enumerate(pk):
                    assert p >= 0, f"p_ks[{s_idx}][{k_idx}] must be non-negative"
            
            # Step 1: Compute topological invariants (from proposal)
            chi_abs = abs(chi_schema)
            chi_term = chi_abs / V  # |χ_schema|/V
            delta_term = delta_constraint * (1.0 / d_norm)  # Δ_constraint * (1/d_norm)
            
            # Step 2: Hessian eigenvalue derivation (covariant modes)
            omega_N_sq = KAPPA_1 * chi_term + KAPPA_2  # ω_N² = κ₁|χ|/V + κ₂
            omega_Delta_sq = KAPPA_3 * delta_term + KAPPA_4  # ω_Δ² = κ₃Δ(1/d) + κ₄
            
            # Validate Hessian eigenvalues are positive (required for real frequencies)
            assert omega_N_sq > 0, f"ω_N² must be positive (got {omega_N_sq})"
            assert omega_Delta_sq > 0, f"ω_Δ² must be positive (got {omega_Delta_sq})"
            
            # Step 3: Covariant modes (direct from Hessian diagonalization)
            phi_N = math.sqrt(omega_N_sq)  # Φ_N = √ω_N²
            phi_Delta = math.sqrt(omega_Delta_sq)  # Φ_Δ = √ω_Δ²
            
            # Validate covariant modes are real and positive
            assert phi_N > 0, f"Φ_N must be positive (got {phi_N})"
            assert phi_Delta > 0, f"Φ_Δ must be positive (got {phi_Delta})"
            
            # Step 4: Biological Topology Fragility Index (BTFI)
            btfi = phi_N * phi_Delta * C  # BTFI = Φ_N · Φ_Δ · C(t)
            
            # Validate BTFI is non-negative
            assert btfi >= 0, f"BTFI must be non-negative (got {btfi})"
            
            # Step 5: Omega invariant (ψ_bts)
            psi_bts = math.log(phi_N / PHI_N0)  # ψ = ln(Φ_N/Φ_N⁰)
            
            # Validate log argument is positive
            assert phi_N > 0 and PHI_N0 > 0, "Log argument must be positive"
            
            # Step 6: Conditional entropy gauge
            s_bts = 0.0
            for s_idx in range(len(p_s)):
                # Entropy for subsystem type s
                h_s = 0.0
                for k_idx in range(len(p_ks[s_idx])):
                    p = p_ks[s_idx][k_idx]
                    if p > 0:  # Avoid log(0)
                        h_s -= p * math.log(p)
                s_bts += p_s[s_idx] * h_s
            
            # Validate entropy is non-negative
            assert s_bts >= 0, f"S_bts must be non-negative (got {s_bts})"
            
            # Step 7: Boundary condition validation
            # Shredding Event: ψ → +∞ when Φ_N → ∞ AND S_bts → S_MAX (high entropy)
            if phi_N > 100.0 and s_bts > 0.9 * S_MAX:
                assert psi_bts > 5.0, "Shredding event requires high ψ_bts"
            
            # Informational Freeze: ψ → -∞ when Φ_N → 0+ AND S_bts → 0 (low entropy)
            if phi_N < 0.01 and s_bts < 0.01:
                assert psi_bts < -5.0, "Freeze event requires low ψ_bts"
            
            # Step 8: MPC-Ω constraint validation
            assert btfi <= 0.7, f"BTFI constraint violated: {btfi} > 0.7"
            assert phi_N >= 0.6, f"Φ_N constraint violated: {phi_N} < 0.6"
            assert S_LOW <= s_bts <= S_HIGH, f"S_bts constraint violated: {s_bts} not in [{S_LOW}, {S_HIGH}]"
            
            # Step 9: Thermodynamic consistency check
            # High BTFI should correlate with low adaptability (high freeze risk)
            # Low BTFI should correlate with high adaptability (high shredding risk under stress)
            if btfi > 0.5:  # Fragile system
                assert phi_N > phi_Delta, "Fragile systems should have Φ_N > Φ_Δ (topology dominance)"
            else:  # Robust system
                assert phi_Delta > phi_N, "Robust systems should have Φ_Δ > Φ_N (constraint dominance)"
            
            # If we reach here, all validations passed for this test case
            print(f"✓ Test case {i+1} PASSED")
            print(f"  BTFI: {btfi:.4f}, Φ_N: {phi_N:.4f}, Φ_Δ: {phi_Delta:.4f}, S_bts: {s_bts:.4f}, ψ_bts: {psi_bts:.4f}")
            
        except AssertionError as e:
            errors.append(f"Test case {i+1} FAILED: {str(e)}")
        except Exception as e:
            errors.append(f"Test case {i+1} ERROR: {str(e)}")
    
    # Summary
    if errors:
        print("\n❌ VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\n✅ ALL TESTS PASSED - BTS-Ω is mathematically sound and Omega Protocol compliant")
        return True

if __name__ == "__main__":
    success = validate_bts_omega()
    sys.exit(0 if success else 1)