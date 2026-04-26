# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import List, Tuple, Dict, Any, NamedTuple

# =============================================================================
# OMEGA PROTOCOL INVARIANTS (Smith Audit v65.0) - DO NOT MODIFY
# =============================================================================
class SmithInvariants:
    COD_THRESHOLD = 0.85          # Invariant 1: Alignment Fidelity (Hard Gate)
    COD_FLOOR = 0.39              # Invariant 2: Identity Continuity
    H_VOL_MIN = 0.15              # Invariant 3: Uncertainty Band (low)
    H_VOL_MAX = 0.80              # Invariant 3: Uncertainty Band (high)
    PSI_INTEGRITY_THRESHOLD = 0.95# Independent solvency floor
    B1_HOMOLOGY_MAX = 0.80        # Invariant 8: Decision Loop Guard
    THETA_LEAK_MAX = 0.50         # Invariant 5: Environmental Cap
    XI_CONFIG_MAX_DELTA = 0.10    # Invariant 4: Stiffness-Impedance Match
    PHI_DELTA_MAX = 0.50          # Invariant 7: Asymmetry Control
    
    # Audit Entropy Constants (Rubric §6)
    K_BOLTZMANN = 1.0
    AUDIT_ENTROPY_PER_CHECK = 0.02
    TOTAL_AUDIT_COST = 9 * AUDIT_ENTROPY_PER_CHECK  # All 9 invariants

# =============================================================================
# CORE MATHEMATICAL OPERATIONS (VALIDATION MODULE)
# =============================================================================
def calculate_fidelity(exec_vec: List[complex], book_vec: List[complex]) -> float:
    """
    Calculate price discovery fidelity: |⟨P_exec|Ψ_book⟩|² / (||P_exec||² ||Ψ_book||²)
    Ensures dimensionless [0,1] output per Rubric §6
    """
    if len(exec_vec) != len(book_vec):
        raise ValueError("Vector dimensions must match")
    
    dot = np.vdot(exec_vec, book_vec)  # ⟨exec|book⟩
    magE = np.vdot(exec_vec, exec_vec)  # ⟨exec|exec⟩
    magB = np.vdot(book_vec, book_vec)  # ⟨book|book⟩
    
    if magE < 1e-12 or magB < 1e-12:
        return 0.0
    
    fidelity = np.abs(dot) ** 2 / (magE * magB)
    return min(max(fidelity, 0.0), 1.0)  # Clamp to [0,1]

def calculate_COD(
    fidelity: float,
    h_vol: float,
    xi_config: float,
    theta_leak: float,
    lambda_coupling: float = 0.5,   # Λ from UIPO v65.0
    kappa_config: float = 0.5,      # κ from UIPO v65.0
    eta_exposure: float = 0.3       # λ from UIPO v65.0
) -> float:
    """
    Chain Overlap Density (COD) - EXACT match to UIPO v65.0 structure:
    COD = Fidelity × exp(-Λ·H) × exp(-κ·Ξ) × exp(-λ·Z)
    All terms dimensionless [0,1] → COD ∈ [0,1]
    """
    if not (0.0 <= fidelity <= 1.0):
        raise ValueError("Fidelity must be in [0,1]")
    if not (0.0 <= h_vol <= 1.0):
        raise ValueError("h_vol must be in [0,1]")
    if not (0.0 <= xi_config <= 1.0):
        raise ValueError("xi_config must be in [0,1]")
    if not (0.0 <= theta_leak <= 1.0):
        raise ValueError("theta_leak must be in [0,1]")
    
    volatility_penalty = math.exp(-lambda_coupling * h_vol)
    stiffness_penalty = math.exp(-kappa_config * xi_config)
    exposure_penalty = math.exp(-eta_exposure * theta_leak)
    
    cod = fidelity * volatility_penalty * stiffness_penalty * exposure_penalty
    return min(max(cod, 0.0), 1.0)  # Ensure [0,1] bounds

def check_smith_invariants(
    state: Dict[str, Any]
) -> Tuple[bool, Dict[str, bool]]:
    """
    Validate all 9 Smith Invariants v65.0
    Returns: (all_passed, individual_results)
    """
    # Extract state variables (with defaults for missing)
    cod = state.get('cod', 0.0)
    h_vol = state.get('h_vol', 0.0)
    xi_config = state.get('xi_config', 0.0)
    z_liquidity = state.get('z_liquidity', 0.0)
    theta_leak = state.get('theta_leak', 0.0)
    b1_homology = state.get('b1_homology', 0.0)
    psi_integrity = state.get('psi_integrity', 0.0)
    
    # Calculate derived metrics
    phi_N = math.log2(max(cod, SmithInvariants.COD_FLOOR)) if cod > 0 else -float('inf')
    phi_delta = phi_N * math.tanh((xi_config - z_liquidity) / 3.0) if phi_N > -float('inf') else 0.0
    
    # Invariant Checks
    checks = {
        'cod_ok': cod >= SmithInvariants.COD_THRESHOLD,                    # Inv 1
        'phi_floor_ok': phi_N >= math.log2(SmithInvariants.COD_FLOOR),    # Inv 2
        'h_vol_low_ok': h_vol >= SmithInvariants.H_VOL_MIN,               # Inv 3a
        'h_vol_high_ok': h_vol <= SmithInvariants.H_VOL_MAX,              # Inv 3b
        'stiffness_match_ok': xi_config <= z_liquidity + SmithInvariants.XI_CONFIG_MAX_DELTA,  # Inv 4
        'env_cap_ok': theta_leak <= SmithInvariants.THETA_LEAK_MAX,       # Inv 5
        'dissonance_ok': True,                                            # Inv 6 (placeholder)
        'asymmetry_ok': abs(phi_delta) < SmithInvariants.PHI_DELTA_MAX * abs(phi_N) if phi_N != 0 else True,  # Inv 7
        'homology_ok': b1_homology <= SmithInvariants.B1_HOMOLOGY_MAX,    # Inv 8
        'integrity_ok': psi_integrity >= SmithInvariants.PSI_INTEGRITY_THRESHOLD  # Independent solvency floor
    }
    
    all_passed = all(checks.values())
    return all_passed, checks

def silence_protocol_decision(
    cod: float,
    failure_type: str,
    psi_integrity: float
) -> str:
    """
    Determine action per Silence Protocol (Root-Aligned)
    Returns: 'PROCEED', 'FREEZE_CONFIG', 'HALT_TRADING', or 'FULL_SILENCE'
    """
    if psi_integrity < SmithInvariants.PSI_INTEGRITY_THRESHOLD:
        return 'HALT_TRADING'
    if cod < SmithInvariants.COD_THRESHOLD:
        return 'FREEZE_CONFIG'
    if failure_type != 'NONE':
        return 'FREEZE_CONFIG'
    return 'PROCEED'

def apply_adiabatic_modulation(
    state: Dict[str, Any],
    dt_hours: float,
    gamma: float = 0.005  # Root Kernel: γ = 0.005 hr⁻¹
) -> Dict[str, Any]:
    """
    Apply adiabatic modulation to state variables
    Returns updated state dictionary
    """
    # Extract current state
    xi_config = state.get('xi_config', 0.0)
    z_liquidity = state.get('z_liquidity', 0.0)
    theta_leak = state.get('theta_leak', 0.0)
    h_vol = state.get('h_vol', 0.0)
    
    # Adiabatic modulation of config stiffness toward liquidity depth
    exp_term = math.exp(-gamma * dt_hours)
    new_xi_config = xi_config * exp_term + z_liquidity * (1.0 - exp_term)
    
    # Exposure reduction over time (security remediation)
    new_theta_leak = max(0.0, theta_leak * exp_term)
    
    # Return updated state (other variables unchanged in this step)
    updated_state = state.copy()
    updated_state['xi_config'] = new_xi_config
    updated_state['theta_leak'] = new_theta_leak
    
    return updated_state

def calculate_phi_density_ledger(
    cod_before: float,
    cod_after: float,
    audit_checks_performed: int
) -> float:
    """
    Calculate net Φ-density gain after audit cost subtraction (Rubric §6)
    """
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks_performed * SmithInvariants.AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost

# =============================================================================
# VALIDATION TEST SUITE
# =============================================================================
def run_validation_tests():
    """
    Execute comprehensive validation tests for Omega Protocol compliance
    """
    print("=" * 60)
    print("OMEGA PROTOCOL VALIDATION SUITE - FINANCIAL CONFIG AUDIT")
    print("=" * 60)
    
    # Test 1: COD Calculation Bounds and Dimensionless Property
    print("\n[TEST 1] COD Calculation Validation")
    test_vectors = [
        ([1+0j, 0+0j], [1+0j, 0+0j]),  # Identical vectors
        ([1+0j, 0+0j], [0+0j, 1+0j]),  # Orthogonal vectors
        ([0+0j, 0+0j], [1+0j, 0+0j])   # Zero vector
    ]
    
    for exec_vec, book_vec in test_vectors:
        fidelity = calculate_fidelity(exec_vec, book_vec)
        cod = calculate_COD(fidelity, 0.2, 0.3, 0.1)
        print(f"  Fidelity: {fidelity:.4f} → COD: {cod:.6f} "
              f"(Bounds check: {'PASS' if 0.0 <= cod <= 1.0 else 'FAIL'})")
    
    # Test 2: Smith Invariant Enforcement
    print("\n[TEST 2] Smith Invariant Validation")
    test_states = [
        {
            'name': 'COMPLIANT STATE',
            'state': {
                'cod': 0.88,
                'h_vol': 0.4,
                'xi_config': 0.3,
                'z_liquidity': 0.4,
                'theta_leak': 0.2,
                'b1_homology': 0.5,
                'psi_integrity': 0.96
            }
        },
        {
            'name': 'COD BELOW THRESHOLD',
            'state': {
                'cod': 0.80,  # Below 0.85 threshold
                'h_vol': 0.4,
                'xi_config': 0.3,
                'z_liquidity': 0.4,
                'theta_leak': 0.2,
                'b1_homology': 0.5,
                'psi_integrity': 0.96
            }
        },
        {
            'name': 'INTEGRITY FAILURE',
            'state': {
                'cod': 0.90,
                'h_vol': 0.4,
                'xi_config': 0.3,
                'z_liquidity': 0.4,
                'theta_leak': 0.2,
                'b1_homology': 0.5,
                'psi_integrity': 0.94  # Below 0.95 threshold
            }
        }
    ]
    
    for ts in test_states:
        all_passed, checks = check_smith_invariants(ts['state'])
        print(f"  {ts['name']}: {'PASS' if all_passed else 'FAIL'}")
        if not all_passed:
            failed = [k for k, v in checks.items() if not v]
            print(f"    Failed Invariants: {', '.join(failed)}")
    
    # Test 3: Silence Protocol Logic
    print("\n[TEST 3] Silence Protocol Decision Tree")
    decision_tests = [
        (0.90, 'NONE', 0.96, 'PROCEED'),      # Normal operation
        (0.80, 'NONE', 0.96, 'FREEZE_CONFIG'), # Low COD
        (0.90, 'CONFIG_REALITY_LOOP', 0.96, 'FREEZE_CONFIG'), # Failure detected
        (0.90, 'NONE', 0.94, 'HALT_TRADING')   # Integrity breach
    ]
    
    for cod, failure, integrity, expected in decision_tests:
        decision = silence_protocol_decision(cod, failure, integrity)
        status = 'PASS' if decision == expected else 'FAIL'
        print(f"  COD={cod:.2f}, Failure={failure}, Integrity={integrity:.2f} → "
              f"{decision} (Expected: {expected}) [{status}]")
    
    # Test 4: Adiabatic Modulation Physics
    print("\n[TEST 4] Adiabatic Modulation Validation")
    initial_state = {
        'xi_config': 0.8,
        'z_liquidity': 0.3,
        'theta_leak': 0.6,
        'h_vol': 0.5
    }
    
    # Test over 10 hours (should move toward liquidity depth)
    updated_state = apply_adiabatic_modulation(initial_state, dt_hours=10.0)
    xi_change = updated_state['xi_config'] - initial_state['xi_config']
    leak_change = updated_state['theta_leak'] - initial_state['theta_leak']
    
    print(f"  Initial ξ_config: {initial_state['xi_config']:.3f} → "
          f"After 10h: {updated_state['xi_config']:.3f} (Δ={xi_change:+.3f})")
    print(f"  Initial θ_leak: {initial_state['theta_leak']:.3f} → "
          f"After 10h: {updated_state['theta_leak']:.3f} (Δ={leak_change:+.3f})")
    
    # Verify monotonic convergence toward z_liquidity
    xi_valid = (updated_state['xi_config'] - initial_state['xi_config']) * \
               (initial_state['z_liquidity'] - initial_state['xi_config']) >= 0
    leak_valid = updated_state['theta_leak'] <= initial_state['theta_leak']
    print(f"  Convergence Check: ξ_config → {'PASS' if xi_valid else 'FAIL'}")
    print(f"  Exposure Reduction: {'PASS' if leak_valid else 'FAIL'}")
    
    # Test 5: Φ-Density Ledger with Audit Cost
    print("\n[TEST 5] Φ-Density Ledger Validation")
    ledger_tests = [
        (0.80, 0.85, 9, 0.04 - 9*0.02),   # Raw gain 0.05, audit cost 0.18 → net -0.13
        (0.80, 0.90, 9, 0.10 - 9*0.02),   # Raw gain 0.10, audit cost 0.18 → net -0.08
        (0.80, 0.88, 0, 0.08)             # No audit → net gain = raw gain
    ]
    
    for cod_b, cod_a, checks, expected in ledger_tests:
        net_gain = calculate_phi_density_ledger(cod_b, cod_a, checks)
        status = 'PASS' if abs(net_gain - expected) < 1e-5 else 'FAIL'
        print(f"  COD: {cod_b:.2f}→{cod_a:.2f} ({checks} audits) → "
              f"Net Φ: {net_gain:+.4f} (Expected: {expected:+.4f}) [{status}]")
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

# =============================================================================
# EXECUTE VALIDATION WHEN RUN AS SCRIPT
# =============================================================================
if __name__ == "__main__":
    run_validation_tests()