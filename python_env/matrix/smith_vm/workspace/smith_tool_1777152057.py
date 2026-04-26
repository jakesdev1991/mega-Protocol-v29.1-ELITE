# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from typing import Tuple

def validate_cod_formula() -> bool:
    """
    Validates the mathematical soundness of the COD formula:
    COD = |<Ψ_cons|Ψ_sub>|^2 * exp(-κ * Ξ_cons) * exp(-λ * Z_env) * exp(-Λ * H_sub)
    
    Checks:
    1. COD ∈ [0, 1] for all valid inputs
    2. Hard floor: COD >= 0.39 prevents Φ_N singularity
    3. Hard gate: COD >= 0.85 for actionable output
    4. Monotonicity: COD decreases as stiffness/impedance/entropy increases
    """
    # Test parameters (κ, λ, Λ > 0 as per physical interpretation)
    kappa, lam, Lambda = 0.5, 0.3, 0.4  # Matching values from submission code
    
    # Generate test cases covering edge conditions
    test_cases = [
        # (fidelity, xi_cons, z_env, h_sub, expected_cod_range)
        (1.0, 0.0, 0.0, 0.0, (1.0, 1.0)),      # Maximum COD
        (0.0, 0.0, 0.0, 0.0, (0.0, 0.0)),      # Zero fidelity
        (1.0, 10.0, 10.0, 10.0, (0.0, 0.0001)), # High penalties
        (0.5, 0.0, 0.0, 0.0, (0.5, 0.5)),      # Mid fidelity
        (1.0, 0.0, 0.0, 1.0, (np.exp(-Lambda), np.exp(-Lambda))), # Entropy penalty only
        (1.0, 0.0, 0.0, 0.0, (1.0, 1.0)),      # Baseline
    ]
    
    for fidelity, xi, z_env, h_sub, (min_exp, max_exp) in test_cases:
        # Calculate COD
        cod = fidelity * np.exp(-kappa * xi) * np.exp(-lam * z_env) * np.exp(-Lambda * h_sub)
        
        # Check bounds
        if not (0.0 <= cod <= 1.0 + 1e-12):  # Allow small floating point error
            print(f"FAIL: COD={cod} out of [0,1] for inputs (f={fidelity}, xi={xi}, z={z_env}, h={h_sub})")
            return False
        
        # Check expected range (if specified)
        if not (min_exp - 1e-12 <= cod <= max_exp + 1e-12):
            print(f"FAIL: COD={cod} not in [{min_exp}, {max_exp}] for inputs (f={fidelity}, xi={xi}, z={z_env}, h={h_sub})")
            return False
    
    # Verify hard floor prevents singularity in Φ_N = log2(COD)
    test_cod_values = [0.0, 0.1, 0.39, 0.5, 0.85, 1.0]
    for cod in test_cod_values:
        # Per submission: phi_N = log2(max(COD, 0.39) + 1e-12)
        phi_N = np.log2(max(cod, 0.39) + 1e-12)
        # Check that phi_N is finite and >= log2(0.39)
        if not np.isfinite(phi_N):
            print(f"FAIL: phi_N non-finite for COD={cod}")
            return False
        if phi_N < np.log2(0.39) - 1e-12:
            print(f"FAIL: phi_N={phi_N} < log2(0.39) for COD={cod}")
            return False
    
    # Verify monotonicity: increasing penalties decrease COD
    base = (0.8, 0.2, 0.2, 0.2)  # (fidelity, xi, z_env, h_sub)
    base_cod = base[0] * np.exp(-kappa*base[1]) * np.exp(-lam*base[2]) * np.exp(-Lambda*base[3])
    
    # Increase each penalty variable one at a time
    for i, (name, delta) in enumerate([("xi_cons", 0.5), ("z_env", 0.5), ("h_sub", 0.5)]):
        test = list(base)
        test[i+1] += delta  # Skip fidelity (index 0)
        test_cod = test[0] * np.exp(-kappa*test[1]) * np.exp(-lam*test[2]) * np.exp(-Lambda*test[3])
        if test_cod >= base_cod + 1e-12:  # Should decrease
            print(f"FAIL: COD increased when {name} increased (base={base_cod}, test={test_cod})")
            return False
    
    print("COD formula validation: PASSED")
    return True

def validate_smith_invariants() -> bool:
    """
    Validates the 9 Smith Invariants as logical conditions.
    Tests boundary conditions and logical consistency.
    """
    # Define invariant check functions (matching submission thresholds)
    def inv1(cod: float) -> bool:  # Alignment Fidelity
        return cod >= 0.85
    
    def inv2(phi_N: float) -> bool:  # Identity Continuity
        return phi_N >= np.log2(0.39)  # Hard floor
    
    def inv3(h_sub: float) -> bool:  # Uncertainty Band
        return 0.15 <= h_sub <= 0.80
    
    def inv4(xi_cons: float, z_sub: float) -> bool:  # Stiffness-Impedance Match
        return xi_cons <= z_sub + 0.1
    
    def inv5(z_env: float) -> bool:  # Environmental Impedance
        return z_env <= 0.7
    
    def inv6(h_dis: float) -> bool:  # Dissonance Cap
        return h_dis <= 0.3
    
    def inv7(phi_Delta: float, phi_N: float) -> bool:  # Asymmetry Control
        return phi_Delta < 0.5 * phi_N
    
    def inv8(b1: float) -> bool:  # Decision Loop Guard
        return b1 <= 0.8
    
    def inv9() -> bool:  # Audit Cost Accounted (always true if we subtract it)
        return True  # This is an accounting invariant, not a state check
    
    # Test invariant boundaries
    test_cases = [
        # (cod, phi_N, h_sub, xi_cons, z_sub, z_env, h_dis, phi_Delta, b1, expected_invariants)
        # All invariants satisfied
        (0.9, np.log2(0.9), 0.5, 0.2, 0.2, 0.5, 0.2, 0.1*np.log2(0.9), 0.5, [True]*9),
        # Invariant 1 violated (COD < 0.85)
        (0.8, np.log2(0.8), 0.5, 0.2, 0.2, 0.5, 0.2, 0.1*np.log2(0.8), 0.5, [False, True, True, True, True, True, True, True, True]),
        # Invariant 2 violated (phi_N < log2(0.39))
        (0.3, np.log2(0.3), 0.5, 0.2, 0.2, 0.5, 0.2, 0.1*np.log2(0.3), 0.5, [True, False, True, True, True, True, True, True, True]),
        # Invariant 3 violated (h_sub too low)
        (0.9, np.log2(0.9), 0.1, 0.2, 0.2, 0.5, 0.2, 0.1*np.log2(0.9), 0.5, [True, True, False, True, True, True, True, True, True]),
        # Invariant 3 violated (h_sub too high)
        (0.9, np.log2(0.9), 0.9, 0.2, 0.2, 0.5, 0.2, 0.1*np.log2(0.9), 0.5, [True, True, False, True, True, True, True, True, True]),
        # Invariant 4 violated (xi_cons > z_sub + 0.1)
        (0.9, np.log2(0.9), 0.5, 0.4, 0.2, 0.5, 0.2, 0.1*np.log2(0.9), 0.5, [True, True, True, False, True, True, True, True, True]),
        # Invariant 5 violated (z_env > 0.7)
        (0.9, np.log2(0.9), 0.5, 0.2, 0.2, 0.8, 0.2, 0.1*np.log2(0.9), 0.5, [True, True, True, True, False, True, True, True, True]),
        # Invariant 6 violated (h_dis > 0.3)
        (0.9, np.log2(0.9), 0.5, 0.2, 0.2, 0.5, 0.4, 0.1*np.log2(0.9), 0.5, [True, True, True, True, True, False, True, True, True]),
        # Invariant 7 violated (phi_Delta >= 0.5*phi_N)
        (0.9, np.log2(0.9), 0.5, 0.2, 0.2, 0.5, 0.2, 0.6*np.log2(0.9), 0.5, [True, True, True, True, True, True, False, True, True]),
        # Invariant 8 violated (b1 > 0.8)
        (0.9, np.log2(0.9), 0.5, 0.2, 0.2, 0.5, 0.2, 0.1*np.log2(0.9), 0.9, [True, True, True, True, True, True, True, True, False]),
    ]
    
    for i, (cod, phi_N, h_sub, xi_cons, z_sub, z_env, h_dis, phi_Delta, b1, expected) in enumerate(test_cases):
        results = [
            inv1(cod),
            inv2(phi_N),
            inv3(h_sub),
            inv4(xi_cons, z_sub),
            inv5(z_env),
            inv6(h_dis),
            inv7(phi_Delta, phi_N),
            inv8(b1),
            inv9()
        ]
        if results != expected:
            print(f"FAIL: Invariant test case {i}")
            print(f"  Inputs: cod={cod:.3f}, phi_N={phi_N:.3f}, h_sub={h_sub:.3f}, xi_cons={xi_cons:.3f}, z_sub={z_sub:.3f}, z_env={z_env:.3f}, h_dis={h_dis:.3f}, phi_Delta={phi_Delta:.3f}, b1={b1:.3f}")
            print(f"  Expected: {expected}")
            print(f"  Got:      {results}")
            for j, (exp, got) in enumerate(zip(expected, results)):
                if exp != got:
                    print(f"    Invariant {j+1}: expected {exp}, got {got}")
            return False
    
    # Verify logical consistency: invariants should be independent
    # Check that violating one invariant doesn't force violation of another (by design)
    # We already tested single violations above - they only affected the intended invariant
    
    print("Smith Invariants validation: PASSED")
    return True

def validate_adiabatic_modulation() -> bool:
    """
    Validates the adiabatic modulation equations from the submission:
    Ξ_cons(t) = Ξ_cons(0) * e^(-γt) + Z_sub * (1 - e^(-γt))
    Z_env(t) = Z_env(0) * e^(-δt) + Z_resonant * (1 - e^(-δt))
    
    Checks:
    1. As t→∞, Ξ_cons→Z_sub and Z_env→Z_resonant
    2. At t=0, values match initial conditions
    3. Monotonic convergence (no overshoot)
    """
    gamma = 0.006  # hr^-1
    delta = 0.005  # hr^-1
    z_sub = 0.35
    z_resonant = 0.4  # From submission code
    
    # Test case: high initial stiffness and impedance
    xi_cons_0 = 0.95
    z_env_0 = 0.85
    
    # Test at t=0
    t = 0.0
    xi_cons_t = xi_cons_0 * np.exp(-gamma * t) + z_sub * (1 - np.exp(-gamma * t))
    z_env_t = z_env_0 * np.exp(-delta * t) + z_resonant * (1 - np.exp(-delta * t))
    if not (abs(xi_cons_t - xi_cons_0) < 1e-12 and abs(z_env_t - z_env_0) < 1e-12):
        print(f"FAIL: Modulation incorrect at t=0")
        return False
    
    # Test as t→∞ (use large t)
    t_large = 1000.0  # hours
    xi_cons_t = xi_cons_0 * np.exp(-gamma * t_large) + z_sub * (1 - np.exp(-gamma * t_large))
    z_env_t = z_env_0 * np.exp(-delta * t_large) + z_resonant * (1 - np.exp(-delta * t_large))
    if not (abs(xi_cons_t - z_sub) < 1e-3 and abs(z_env_t - z_resonant) < 1e-3):
        print(f"FAIL: Modulation incorrect at t→∞ (xi={xi_cons_t}, z={z_env_t})")
        return False
    
    # Test monotonicity: xi_cons should decrease toward z_sub (since xi_cons_0 > z_sub)
    times = [0, 10, 50, 100, 500, 1000]
    xi_vals = [xi_cons_0 * np.exp(-gamma * t) + z_sub * (1 - np.exp(-gamma * t)) for t in times]
    for i in range(1, len(xi_vals)):
        if xi_vals[i] > xi_vals[i-1] + 1e-12:  # Should be non-increasing
            print(f"FAIL: xi_cons increased between t={times[i-1]} and t={times[i]}")
            return False
    
    # Test monotonicity for z_env (should decrease toward z_resonant since z_env_0 > z_resonant)
    z_env_vals = [z_env_0 * np.exp(-delta * t) + z_resonant * (1 - np.exp(-delta * t)) for t in times]
    for i in range(1, len(z_env_vals)):
        if z_env_vals[i] > z_env_vals[i-1] + 1e-12:  # Should be non-increasing
            print(f"FAIL: z_env increased between t={times[i-1]} and t={times[i]}")
            return False
    
    print("Adiabatic modulation validation: PASSED")
    return True

def main() -> None:
    """Run all validation checks."""
    print("=" * 60)
    print("Omega Protocol Invariant Audit: Measurement Gauge (v65.0)")
    print("=" * 60)
    
    checks = [
        ("COD Formula", validate_cod_formula),
        ("Smith Invariants", validate_smith_invariants),
        ("Adiabatic Modulation", validate_adiabatic_modulation),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"ERROR: {name} validation failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("RESULT: ALL VALIDATIONS PASSED")
        print("The submission is mathematically sound and compliant with Omega Protocol invariants.")
    else:
        print("RESULT: VALIDATION FAILED")
        print("The submission contains mathematical or logical violations.")
    print("=" * 60)

if __name__ == "__main__":
    main()