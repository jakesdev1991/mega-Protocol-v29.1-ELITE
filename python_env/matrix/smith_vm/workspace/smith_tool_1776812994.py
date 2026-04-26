# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

def validate_pasm_omega(t, 
                       Phi_N0=1.0, 
                       Phi_Delta0=0.0, 
                       I0=1.0, 
                       lambda_val=0.5,
                       SW_WRI=None,
                       S_weap=None,
                       intent_conv=None,
                       strategy_div=None,
                       I_corr=None):
    """
    Validate mathematical consistency and Omega Protocol invariants for refined PASM-Ω.
    
    Parameters:
    t (float): Current time (unused in calc but kept for interface)
    Phi_N0 (float): Baseline Phi_N (default=1.0 for normalization)
    Phi_Delta0 (float): Baseline Phi_Delta (default=0.0)
    I0 (float): Baseline intent correlation (default=1.0)
    lambda_val (float): Coupling constant in invariant (default=0.5)
    SW_WRI (float): Sophistication-Weighted WRI at t-14days [0,1)
    S_weap (float): Strategic diversity metric at t-14days
    intent_conv (float): Intent convergence at t-14days
    strategy_div (float): Strategy diversity at t-14days
    I_corr (float): Intent correlation at time t
    
    Returns:
    dict: Validation results including:
        - sw_wri_valid: SW-WRI in [0,1)
        - phi_n_weap_valid: Phi_N_weap >= 0.5
        - s_weap_valid: S_weap >= ln(4)
        - invariant_holds: |psi_weap - RHS| < tolerance
        - computed_values: Dictionary of computed intermediates
        - errors: List of validation errors
    """
    # Initialize results
    results = {
        'sw_wri_valid': False,
        'phi_n_weap_valid': False,
        's_weap_valid': False,
        'invariant_holds': False,
        'computed_values': {},
        'errors': []
    }
    
    # Tolerance for floating point comparisons
    TOL = 1e-8
    LN_4 = math.log(4)  # ≈1.38629436112
    
    # Validate inputs are provided
    if SW_WRI is None:
        results['errors'].append("SW_WRI input required")
    if S_weap is None:
        results['errors'].append("S_weap input required")
    if intent_conv is None:
        results['errors'].append("intent_conv input required")
    if strategy_div is None:
        results['errors'].append("strategy_div input required")
    if I_corr is None:
        results['errors'].append("I_corr input required")
    
    if results['errors']:
        return results
    
    # Validate SW-WRI range [0,1) from tanh of non-negative argument
    if not (0 <= SW_WRI < 1):
        results['errors'].append(f"SW_WRI={SW_WRI} must be in [0,1)")
        results['sw_wri_valid'] = False
    else:
        results['sw_wri_valid'] = True
    
    # Compute Phi_N_weap
    phi_n_weap = Phi_N0 - 0.9 * SW_WRI + 0.4 * S_weap
    results['computed_values']['Phi_N_weap'] = phi_n_weap
    
    # Validate Phi_N_weap >= 0.5 (Omega invariant constraint)
    if phi_n_weap < 0.5 - TOL:
        results['errors'].append(f"Phi_N_weap={phi_n_weap} < 0.5 violates invariant")
        results['phi_n_weap_valid'] = False
    else:
        results['phi_n_weap_valid'] = True
    
    # Compute Phi_Delta_weap
    phi_delta_weap = Phi_Delta0 + 0.7 * intent_conv - 0.5 * strategy_div
    results['computed_values']['Phi_Delta_weap'] = phi_delta_weap
    
    # Compute S_weap validity (constraint: S_weap >= ln(4))
    if S_weap < LN_4 - TOL:
        results['errors'].append(f"S_weap={S_weap} < ln(4)≈{LN_4:.6f} violates constraint")
        results['s_weap_valid'] = False
    else:
        results['s_weap_valid'] = True
    
    # Compute psi_weap = ln(Phi_N_weap / Phi_N0)
    if phi_n_weap <= 0:
        results['errors'].append(f"Phi_N_weap={phi_n_weap} <= 0 makes log undefined")
        results['invariant_holds'] = False
    else:
        psi_weap = math.log(phi_n_weap / Phi_N0)
        results['computed_values']['psi_weap'] = psi_weap
        
        # Compute RHS of invariant: ln(I_corr/I0) + lambda * SW_WRI
        if I_corr <= 0 or I0 <= 0:
            results['errors'].append(f"I_corr={I_corr} or I0={I0} <= 0 makes log undefined")
            results['invariant_holds'] = False
        else:
            rhs = math.log(I_corr / I0) + lambda_val * SW_WRI
            results['computed_values']['RHS_invariant'] = rhs
            
            # Check invariant equality within tolerance
            if abs(psi_weap - rhs) < TOL:
                results['invariant_holds'] = True
            else:
                results['errors'].append(
                    f"Invariant violation: |psi_weap ({psi_weap:.6f}) - RHS ({rhs:.6f})| = "
                    f"{abs(psi_weap - rhs):.6f} > TOL ({TOL})"
                )
                results['invariant_holds'] = False
    
    return results

def test_validation():
    """Test the validator with nominal and edge-case values."""
    print("=== PASM-Ω Mathematical Validation ===\n")
    
    # Test Case 1: Nominal values satisfying all constraints
    print("Test Case 1: Nominal valid scenario")
    res1 = validate_pasm_omega(
        t=0,
        SW_WRI=0.5,          # Valid [0,1)
        S_weap=2.0,          # > ln(4)≈1.386
        intent_conv=0.8,
        strategy_div=0.2,
        I_corr=1.5           # > I0=1.0
    )
    print(f"SW-WRI valid: {res1['sw_wri_valid']}")
    print(f"Phi_N_weap valid: {res1['phi_n_weap_valid']} (value={res1['computed_values']['Phi_N_weap']:.4f})")
    print(f"S_weap valid: {res1['s_weap_valid']} (value={res1['computed_values']['S_weap']:.4f})")
    print(f"Invariant holds: {res1['invariant_holds']}")
    if res1['errors']:
        print(f"Errors: {res1['errors']}")
    print()
    
    # Test Case 2: SW-WRI out of bounds
    print("Test Case 2: Invalid SW-WRI (negative)")
    res2 = validate_pasm_omega(
        t=0,
        SW_WRI=-0.1,         # Invalid
        S_weap=2.0,
        intent_conv=0.8,
        strategy_div=0.2,
        I_corr=1.5
    )
    print(f"SW-WRI valid: {res2['sw_wri_valid']}")
    if res2['errors']:
        print(f"Errors: {res2['errors']}")
    print()
    
    # Test Case 3: Phi_N_weap too small
    print("Test Case 3: Phi_N_weap < 0.5")
    res3 = validate_pasm_omega(
        t=0,
        SW_WRI=0.9,          # High SW-WRI reduces Phi_N_weap
        S_weap=0.5,          # Low S_weap doesn't compensate enough
        intent_conv=0.8,
        strategy_div=0.2,
        I_corr=1.5
    )
    print(f"Phi_N_weap valid: {res3['phi_n_weap_valid']} (value={res3['computed_values']['Phi_N_weap']:.4f})")
    if res3['errors']:
        print(f"Errors: {res3['errors']}")
    print()
    
    # Test Case 4: S_weap too small
    print("Test Case 4: S_weap < ln(4)")
    res4 = validate_pasm_omega(
        t=0,
        SW_WRI=0.5,
        S_weap=1.0,          # < ln(4)≈1.386
        intent_conv=0.8,
        strategy_div=0.2,
        I_corr=1.5
    )
    print(f"S_weap valid: {res4['s_weap_valid']} (value={res4['computed_values']['S_weap']:.4f})")
    if res4['errors']:
        print(f"Errors: {res4['errors']}")
    print()
    
    # Test Case 5: Invariant violation
    print("Test Case 5: Intent correlation mismatch")
    res5 = validate_pasm_omega(
        t=0,
        SW_WRI=0.5,
        S_weap=2.0,
        intent_conv=0.8,
        strategy_div=0.2,
        I_corr=0.5           # Too low to satisfy invariant
    )
    print(f"Invariant holds: {res5['invariant_holds']}")
    print(f"  psi_weap = {res5['computed_values']['psi_weap']:.6f}")
    print(f"  RHS = {res5['computed_values']['RHS_invariant']:.6f}")
    if res5['errors']:
        print(f"Errors: {res5['errors']}")
    print()
    
    # Test Case 6: Edge case SW_WRI=0
    print("Test Case 6: SW_WRI=0 (minimum)")
    res6 = validate_pasm_omega(
        t=0,
        SW_WRI=0.0,
        S_weap=2.0,
        intent_conv=0.0,
        strategy_div=0.0,
        I_corr=1.0
    )
    print(f"SW-WRI valid: {res6['sw_wri_valid']}")
    print(f"Phi_N_weap valid: {res6['phi_n_weap_valid']} (value={res6['computed_values']['Phi_N_weap']:.4f})")
    print(f"Invariant holds: {res6['invariant_holds']}")
    if res6['errors']:
        print(f"Errors: {res6['errors']}")
    print()
    
    # Test Case 7: Edge case SW_WRI approaching 1
    print("Test Case 7: SW_WRI=0.999 (near maximum)")
    res7 = validate_pasm_omega(
        t=0,
        SW_WRI=0.999,
        S_weap=2.0,
        intent_conv=1.0,
        strategy_div=0.0,
        I_corr=math.exp(0.5) * 1.0  # Chosen to satisfy invariant: ln(I_corr/I0) = -lambda*SW_WRI
    )
    print(f"SW-WRI valid: {res7['sw_wri_valid']}")
    print(f"Phi_N_weap valid: {res7['phi_n_weap_valid']} (value={res7['computed_values']['Phi_N_weap']:.4f})")
    print(f"Invariant holds: {res7['invariant_holds']}")
    if res7['errors']:
        print(f"Errors: {res7['errors']}")
    print()

if __name__ == "__main__":
    test_validation()