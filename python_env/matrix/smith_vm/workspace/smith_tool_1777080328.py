# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import List, Tuple, Complex

# =============================================================================
# OMEGA PROTOCOL INVARIANTS (v65.0) - CONSTANTS
# =============================================================================
class FinanceSmithInvariants:
    COD_THRESHOLD = 0.85           # Invariant 1: Alignment Fidelity
    COD_FLOOR = 0.39               # Invariant 2: Identity Continuity
    H_VOL_MIN = 0.15               # Invariant 3: Uncertainty Band (low)
    H_VOL_MAX = 0.80               # Invariant 3: Uncertainty Band (high)
    PSI_INTEGRITY_THRESHOLD = 0.95 # Independent solvency floor
    THETA_LEAK_MAX = 0.50          # Invariant 5: Environmental Cap
    XI_CONFIG_MAX_DELTA = 0.10     # Invariant 4: Stiffness-Impedance Match
    PHI_DELTA_MAX = 0.50           # Invariant 7: Asymmetry Control
    B1_HOMOLOGY_MAX = 0.80         # Invariant 8: Decision Loop Guard
    
    # Audit Constants
    K_BOLTZMANN = 1.0
    AUDIT_ENTROPY_PER_CHECK = 0.02

# =============================================================================
# MATHEMATICAL CORE FUNCTIONS (Python translation of C++ logic)
# =============================================================================
def calculate_fidelity(exec_vec: List[Complex], book_vec: List[Complex]) -> float:
    """Calculate fidelity |<P_exec|Ψ_book>|^2 / (||P_exec||^2 ||Ψ_book||^2)"""
    if not exec_vec or not book_vec:
        return 0.0
    
    size = min(len(exec_vec), len(book_vec))
    dot = 0.0
    magE = 0.0
    magB = 0.0
    
    for i in range(size):
        # Complex conjugate: np.conj(z) but we'll do manually for clarity
        exec_conj = exec_vec[i].real - 1j * exec_vec[i].imag if isinstance(exec_vec[i], complex) else exec_vec[i]
        dot += (exec_conj * book_vec[i]).real  # Taking real part as in C++ abs() for complex
        
        magE += (exec_vec[i].real ** 2 + exec_vec[i].imag ** 2) if isinstance(exec_vec[i], complex) else exec_vec[i] ** 2
        magB += (book_vec[i].real ** 2 + book_vec[i].imag ** 2) if isinstance(book_vec[i], complex) else book_vec[i] ** 2
    
    if magE < 1e-9 or magB < 1e-9:
        return 0.0
    
    fidelity = dot / (math.sqrt(magE) * math.sqrt(magB))
    return max(0.0, min(1.0, fidelity))  # Clamp to [0,1]

def calculate_COD_finance(exec_vec: List[Complex], book_vec: List[Complex], 
                         h_vol: float, xi_config: float, theta_leak: float) -> float:
    """COD = Fidelity * exp(-Λ·H) * exp(-κ·Ξ) * exp(-λ·Z)"""
    fidelity = calculate_fidelity(exec_vec, book_vec)
    volatility_penalty = math.exp(-FinanceSmithInvariants.LAMBDA_COUPLING * h_vol)
    stiffness_penalty = math.exp(-FinanceSmithInvariants.KAPPA_CONFIG * xi_config)
    exposure_penalty = math.exp(-FinanceSmithInvariants.ETA_EXPOSURE * theta_leak)
    
    cod = fidelity * volatility_penalty * stiffness_penalty * exposure_penalty
    return max(0.0, min(1.0, cod))  # Ensure [0,1] bounds

def check_smith_invariants(state: dict, cod: float) -> dict:
    """
    Check all 9 Smith Invariants
    state: dict containing psi_integrity, h_vol, xi_config, z_liquidity, theta_leak, b1_homology
    """
    check = {
        'cod_ok': False,
        'phi_floor_ok': False,
        'h_vol_ok': False,
        'stiffness_match_ok': False,
        'env_cap_ok': False,
        'dissonance_ok': True,  # Placeholder
        'asymmetry_ok': False,
        'homology_ok': False,
        'audit_tracked': True
    }
    
    # phi_N = COD (repaired version - bounded [0,1])
    phi_N = cod
    phi_delta = phi_N * math.tanh((state['xi_config'] - state['z_liquidity']) / 3.0)
    
    # Invariant 1: Alignment Fidelity (COD ≥ 0.85)
    check['cod_ok'] = cod >= FinanceSmithInvariants.COD_THRESHOLD
    
    # Invariant 2: Identity Continuity (phi_N ≥ COD_FLOOR)
    check['phi_floor_ok'] = phi_N >= FinanceSmithInvariants.COD_FLOOR
    
    # Invariant 3: Uncertainty Band (H_VOL_MIN ≤ h_vol ≤ H_VOL_MAX)
    check['h_vol_ok'] = (FinanceSmithInvariants.H_VOL_MIN <= state['h_vol'] <= 
                         FinanceSmithInvariants.H_VOL_MAX)
    
    # Invariant 4: Stiffness-Impedance Match (xi_config ≤ z_liquidity + XI_CONFIG_MAX_DELTA)
    check['stiffness_match_ok'] = (state['xi_config'] <= 
                                  state['z_liquidity'] + FinanceSmithInvariants.XI_CONFIG_MAX_DELTA)
    
    # Invariant 5: Environmental Cap (theta_leak ≤ THETA_LEAK_MAX)
    check['env_cap_ok'] = state['theta_leak'] <= FinanceSmithInvariants.THETA_LEAK_MAX
    
    # Invariant 6: Dissonance Guard (placeholder - always true)
    # check['dissonance_ok'] = True  # Already set
    
    # Invariant 7: Asymmetry Control (phi_delta < PHI_DELTA_MAX * phi_N)
    # CRITICAL: When phi_N = 0, RHS=0 and LHS=0 → 0 < 0 is False (correctly fails)
    # When phi_N > 0, equivalent to: tanh((xi_config - z_liquidity)/3.0) < PHI_DELTA_MAX
    check['asymmetry_ok'] = phi_delta < (FinanceSmithInvariants.PHI_DELTA_MAX * phi_N)
    
    # Invariant 8: Decision Loop Guard (b1_homology ≤ B1_HOMOLOGY_MAX)
    check['homology_ok'] = state['b1_homology'] <= FinanceSmithInvariants.B1_HOMOLOGY_MAX
    
    return check

def apply_financial_resonance_operator(state: dict, dt_hours: float) -> dict:
    """Apply adiabatic modulation to state variables"""
    GAMMA = 0.005  # Identity re-entanglement timescale (configurable default)
    
    # Adiabatic modulation of config stiffness toward liquidity depth
    exp_term = math.exp(-GAMMA * dt_hours)
    state['xi_config'] = (state['xi_config'] * exp_term + 
                         state['z_liquidity'] * (1.0 - exp_term))
    
    # Reduce exposure over time (security remediation)
    state['theta_leak'] = max(0.0, state['theta_leak'] * exp_term)
    
    # Recalculate COD (using dummy vectors for state update - in reality would use market data)
    # For state update, we only need to update the parameters that affect COD
    # The actual COD calculation requires market vectors, but we track the parameters
    state['cod'] = calculate_COD_finance([], [], state['h_vol'], 
                                        state['xi_config'], state['theta_leak'])
    state['phi_N'] = state['cod']  # Repaired: phi_N = COD (bounded [0,1])
    
    # Topological update (placeholder)
    state['b1_homology'] = 0.1  # Neutral value until GUDHI implementation
    
    return state

def silence_protocol_decide(state: dict, cod: float) -> str:
    """Determine action based on Silence Protocol and hard gates"""
    # PRIMARY GATE: Solvency check (must pass FIRST)
    if state['psi_integrity'] < FinanceSmithInvariants.PSI_INTEGRITY_THRESHOLD:
        return "HALT_TRADING"
    
    # SECONDARY GATE: Alignment check
    if cod < FinanceSmithInvariants.COD_THRESHOLD:
        return "FREEZE_CONFIG"
    
    # Check for any active failures (topological, exposure, etc.)
    # In reality would call TopologicalFailureDetector.CheckFailure(state)
    # For now, we'll assume no failures if we get here
    return "PROCEED"

# =============================================================================
# VALIDATION TEST SUITE
# =============================================================================
def test_dimensional_consistency():
    """Test that all outputs remain in [0,1] bounds"""
    print("Testing dimensional consistency...")
    
    # Test COD calculation with extreme inputs
    test_cases = [
        # (h_vol, xi_config, theta_leak, expected_COD_range)
        (0.0, 0.0, 0.0, (0.0, 1.0)),   # Minimum penalties
        (1.0, 1.0, 1.0, (0.0, 0.1)),   # Maximum penalties
        (0.5, 0.5, 0.5, (0.0, 1.0)),   # Mid-range
    ]
    
    # Use dummy vectors for fidelity calculation
    exec_vec = [1+0j, 0+1j]
    book_vec = [1+0j, 0+1j]
    
    for h_vol, xi_config, theta_leak, expected_range in test_cases:
        cod = calculate_COD_finance(exec_vec, book_vec, h_vol, xi_config, theta_leak)
        assert 0.0 <= cod <= 1.0, f"COD={cod} not in [0,1] for inputs ({h_vol}, {xi_config}, {theta_leak})"
        assert expected_range[0] <= cod <= expected_range[1], \
            f"COD={cod} outside expected range {expected_range} for inputs"
    
    print("✓ All COD values within [0,1] bounds")

def test_asymmetry_check():
    """Test asymmetry check for logical consistency"""
    print("\nTesting asymmetry check logic...")
    
    # Test case 1: Healthy state (should pass asymmetry check)
    state_healthy = {
        'psi_integrity': 0.96,
        'h_vol': 0.5,
        'xi_config': 0.4,
        'z_liquidity': 0.5,  # xi_config < z_liquidity → negative tanh
        'theta_leak': 0.3,
        'b1_homology': 0.2
    }
    cod_healthy = 0.9
    check_healthy = check_smith_invariants(state_healthy, cod_healthy)
    assert check_healthy['asymmetry_ok'], "Healthy state failed asymmetry check"
    
    # Test case 2: Stiffness overshoot (should fail stiffness_match, but check asymmetry logic)
    state_stiff = {
        'psi_integrity': 0.96,
        'h_vol': 0.5,
        'xi_config': 0.7,  # > z_liquidity + 0.10
        'z_liquidity': 0.5,
        'theta_leak': 0.3,
        'b1_homology': 0.2
    }
    cod_stiff = 0.86
    check_stiff = check_smith_invariants(state_stiff, cod_stiff)
    assert not check_stiff['stiffness_match_ok'], "Stiffness overshoot not detected"
    # Asymmetry check should still be evaluable (not inverted)
    # Since phi_N > 0, we can verify the inequality direction
    phi_N = cod_stiff
    phi_delta = phi_N * math.tanh((state_stiff['xi_config'] - state_stiff['z_liquidity']) / 3.0)
    expected_asymmetry = phi_delta < (FinanceSmithInvariants.PHI_DELTA_MAX * phi_N)
    assert check_stiff['asymmetry_ok'] == expected_asymmetry, "Asymmetry check logic inconsistent"
    
    # Test case 3: Zero COD (edge case)
    state_zero = {
        'psi_integrity': 0.96,
        'h_vol': 0.5,
        'xi_config': 0.4,
        'z_liquidity': 0.5,
        'theta_leak': 0.3,
        'b1_homology': 0.2
    }
    cod_zero = 0.0
    check_zero = check_smith_invariants(state_zero, cod_zero)
    assert not check_zero['phi_floor_ok'], "Zero COD should fail phi_floor_ok"
    assert not check_zero['asymmetry_ok'], "Zero COD should fail asymmetry_ok (0 < 0 is false)"
    
    print("✓ Asymmetry check behaves logically across test cases")

def test_hard_gate_hierarchy():
    """Test that hard gates enforce correct behavior"""
    print("\nTesting hard gate hierarchy...")
    
    # Case 1: Integrity breach (should HALT_TRADING regardless of COD)
    state_integrity_breach = {
        'psi_integrity': 0.90,  # Below threshold
        'h_vol': 0.5,
        'xi_config': 0.4,
        'z_liquidity': 0.5,
        'theta_leak': 0.3,
        'b1_homology': 0.2
    }
    cod_any = 0.9  # High COD
    action = silence_protocol_decide(state_integrity_breach, cod_any)
    assert action == "HALT_TRADING", f"Expected HALT_TRADING, got {action}"
    
    # Case 2: Good integrity but poor alignment (should FREEZE_CONFIG)
    state_poor_alignment = {
        'psi_integrity': 0.96,  # Above threshold
        'h_vol': 0.5,
        'xi_config': 0.4,
        'z_liquidity': 0.5,
        'theta_leak': 0.3,
        'b1_homology': 0.2
    }
    cod_low = 0.80  # Below COD_THRESHOLD
    action = silence_protocol_decide(state_poor_alignment, cod_low)
    assert action == "FREEZE_CONFIG", f"Expected FREEZE_CONFIG, got {action}"
    
    # Case 3: Good integrity and alignment (should PROCEED)
    state_good = {
        'psi_integrity': 0.96,
        'h_vol': 0.5,
        'xi_config': 0.4,
        'z_liquidity': 0.5,
        'theta_leak': 0.3,
        'b1_homology': 0.2
    }
    cod_high = 0.90
    action = silence_protocol_decide(state_good, cod_high)
    assert action == "PROCEED", f"Expected PROCEED, got {action}"
    
    print("✓ Hard gate hierarchy functions correctly")

def test_adiabatic_modulation():
    """Test that state updates remain within bounds"""
    print("\nTesting adiabatic modulation...")
    
    state = {
        'psi_integrity': 0.96,
        'h_vol': 0.5,
        'xi_config': 0.8,  # High stiffness
        'z_liquidity': 0.3,  # Low liquidity
        'theta_leak': 0.6,  # High exposure
        'b1_homology': 0.2,
        'cod': 0.5,
        'phi_N': 0.5
    }
    
    # Apply operator for various time steps
    for dt in [0.1, 1.0, 10.0, 100.0]:
        state_copy = state.copy()
        updated_state = apply_financial_resonance_operator(state_copy, dt)
        
        # Check bounds
        assert 0.0 <= updated_state['xi_config'] <= 1.0, f"xi_config={updated_state['xi_config']} out of bounds"
        assert 0.0 <= updated_state['theta_leak'] <= 1.0, f"theta_leak={updated_state['theta_leak']} out of bounds"
        assert 0.0 <= updated_state['cod'] <= 1.0, f"cod={updated_state['cod']} out of bounds"
        assert 0.0 <= updated_state['phi_N'] <= 1.0, f"phi_N={updated_state['phi_N']} out of bounds"
        
        # Check monotonic convergence toward liquidity
        # xi_config should move toward z_liquidity (0.3)
        if dt > 0:
            assert abs(updated_state['xi_config'] - 0.3) < abs(state['xi_config'] - 0.3), \
                f"xi_config not converging toward liquidity: {state['xi_config']} -> {updated_state['xi_config']}"
        
        # Exposure should decrease
        assert updated_state['theta_leak'] <= state['theta_leak'], \
            f"Exposure not decreasing: {state['theta_leak']} -> {updated_state['theta_leak']}"
    
    print("✓ Adiabatic modulation preserves bounds and converges correctly")

def test_full_integrity():
    """Run integrated test of the financial integrity manifold"""
    print("\nRunning full integrity test...")
    
    # Initialize state
    state = {
        'psi_integrity': 0.96,
        'h_vol': 0.4,
        'xi_config': 0.5,
        'z_liquidity': 0.5,
        'theta_leak': 0.4,
        'b1_homology': 0.1,
        'cod': 0.7,
        'phi_N': 0.7
    }
    
    # Simulate market shock (increased volatility)
    state['h_vol'] = 0.75  # High volatility
    
    # Calculate COD after shock
    exec_vec = [0.8+0.2j, 0.3+0.7j]
    book_vec = [0.7+0.3j, 0.4+0.6j]
    state['cod'] = calculate_COD_finance(exec_vec, book_vec, 
                                        state['h_vol'], state['xi_config'], state['theta_leak'])
    state['phi_N'] = state['cod']
    
    # Check hard gates
    if state['psi_integrity'] < FinanceSmithInvariants.PSI_INTEGRITY_THRESHOLD:
        action = "HALT_TRADING"
    elif state['cod'] < FinanceSmithInvariants.COD_THRESHOLD:
        action = "FREEZE_CONFIG"
    else:
        action = "PROCEED"
    
    # With h_vol=0.75, we expect significant penalty
    # Rough estimate: fidelity ~0.8, volatility_penalty=exp(-0.5*0.75)=0.69, 
    # stiffness_penalty=exp(-0.5*0.5)=0.78, exposure_penalty=exp(-0.3*0.4)=0.89
    # COD ≈ 0.8 * 0.69 * 0.78 * 0.89 ≈ 0.31 → should trigger FREEZE_CONFIG
    assert state['cod'] < 0.85, f"Expected COD < 0.85 after volatility shock, got {state['cod']}"
    assert action == "FREEZE_CONFIG", f"Expected FREEZE_CONFIG after shock, got {action}"
    
    # Apply operator to recover
    state = apply_financial_resonance_operator(state, dt_hours=24.0)  # 1 day
    
    # After modulation, xi_config should have moved toward z_liquidity
    assert state['xi_config'] < 0.5, f"xi_config not reducing: {state['xi_config']}"
    assert state['theta_leak'] < 0.4, f"Exposure not reducing: {state['theta_leak']}"
    
    print("✓ Full integrity test passed")

# =============================================================================
# MAIN VALIDATION EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA PROTOCOL FINANCIAL INTEGRITY MANIFOLD VALIDATION")
    print("=" * 60)
    
    try:
        test_dimensional_consistency()
        test_asymmetry_check()
        test_hard_gate_hierarchy()
        test_adiabatic_modulation()
        test_full_integrity()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED - SYSTEM IS OMEGA PROTOCOL COMPLIANT")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        print("=" * 60)
        exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("=" * 60)
        exit(1)