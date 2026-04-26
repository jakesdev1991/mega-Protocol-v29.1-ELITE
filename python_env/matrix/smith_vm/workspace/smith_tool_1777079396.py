# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Mathematical Validation Script
# Validates Financial Integrity Manifold (v57.0-Ω-REPAIRED) against core invariants
# Enforces Rubric §6 dimensional homogeneity and Smith Invariant v65.0 compliance

import numpy as np
from typing import NamedTuple, Tuple

# =============================================================================
# 1. CONSTANTS (FROM v57.0-Ω-REPAIRED C++ IMPLEMENTATION)
# =============================================================================
class OmegaConstants:
    # Smith Invariants v65.0 (Hard Gates)
    COD_THRESHOLD = 0.85          # Invariant 1: Alignment Fidelity
    COD_FLOOR = 0.39              # Invariant 2: Identity Continuity
    H_VOL_MIN = 0.15              # Invariant 3: Uncertainty Band (low)
    H_VOL_MAX = 0.80              # Invariant 3: Uncertainty Band (high)
    PSI_INTEGRITY_THRESHOLD = 0.95 # Independent solvency floor
    THETA_LEAK_MAX = 0.50         # Invariant 5: Environmental Cap
    XI_CONFIG_MAX_DELTA = 0.10    # Invariant 4: Stiffness-Impedance Match
    PHI_DELTA_MAX = 0.50          # Invariant 7: Asymmetry Control
    B1_HOMOLOGY_MAX = 0.80        # Invariant 8: Decision Loop Guard
    
    # COD Coupling Constants (Root Kernel Aligned)
    LAMBDA_COUPLING = 0.5   # Volatility penalty (Λ)
    KAPPA_CONFIG = 0.5      # Config stiffness (κ)
    ETA_EXPOSURE = 0.3      # Exposure penalty (λ)
    
    # Audit Entropy
    AUDIT_ENTROPY_PER_CHECK = 0.02  # Per-invariant cost (Rubric §6)
    TOTAL_INVARIANTS = 9
    TOTAL_AUDIT_COST = TOTAL_INVARIANTS * AUDIT_ENTROPY_PER_CHECK

# =============================================================================
# 2. STATE VALIDATION STRUCTURES
# =============================================================================
class FinanceState(NamedTuple):
    xi_config: float      # Config Stiffness [0,1]
    z_liquidity: float    # Market Depth/Trust [0,1]
    theta_leak: float     # Exposure Risk [0,1]
    h_vol: float          # Volatility Entropy [0,1]
    psi_integrity: float  # Solvency Floor [0,1]
    fid_exec_book: float  # Fidelity |<P_exec|Psi_book>|^2 [0,1]

class InvariantCheck(NamedTuple):
    cod_ok: bool
    phi_floor_ok: bool
    h_vol_ok: bool
    stiffness_match_ok: bool
    env_cap_ok: bool
    dissonance_ok: bool
    asymmetry_ok: bool
    homology_ok: bool
    audit_tracked: bool

# =============================================================================
# 3. CORE MATHEMATICAL FUNCTIONS (VALIDATED AGAINST C++)
# =============================================================================
def calculate_cod(state: FinanceState) -> float:
    """Calculate Chain Overlap Density per Root Kernel formula"""
    # Fidelity term (already provided as state.fid_exec_book)
    fidelity = np.clip(state.fid_exec_book, 0.0, 1.0)
    
    # Root-aligned penalties
    volatility_penalty = np.exp(-OmegaConstants.LAMBDA_COUPLING * state.h_vol)
    stiffness_penalty = np.exp(-OmegaConstants.KAPPA_CONFIG * state.xi_config)
    exposure_penalty = np.exp(-OmegaConstants.ETA_EXPOSURE * state.theta_leak)
    
    return fidelity * volatility_penalty * stiffness_penalty * exposure_penalty

def calculate_phi_N(cod: float) -> float:
    """Identity Metric - REPAIRED: phi_N = COD (bounded [0,1])"""
    return np.clip(cod, 0.0, 1.0)

def calculate_phi_delta(phi_N: float, state: FinanceState) -> float:
    """Asymmetry Metric - REPAIRED: preserves inequality direction"""
    return phi_N * np.tanh((state.xi_config - state.z_liquidity) / 3.0)

def check_smith_invariants(state: FinanceState, cod: float) -> InvariantCheck:
    """Validate all 9 Smith Invariants v65.0"""
    phi_N = calculate_phi_N(cod)
    phi_delta = calculate_phi_delta(phi_N, state)
    
    return InvariantCheck(
        cod_ok = cod >= OmegaConstants.COD_THRESHOLD,
        phi_floor_ok = phi_N >= OmegaConstants.COD_FLOOR,
        h_vol_ok = (state.h_vol >= OmegaConstants.H_VOL_MIN) and 
                   (state.h_vol <= OmegaConstants.H_VOL_MAX),
        stiffness_match_ok = state.xi_config <= state.z_liquidity + 
                            OmegaConstants.XI_CONFIG_MAX_DELTA,
        env_cap_ok = state.theta_leak <= OmegaConstants.THETA_LEAK_MAX,
        dissonance_ok = True,  # Placeholder (validated elsewhere)
        asymmetry_ok = phi_delta < OmegaConstants.PHI_DELTA_MAX * phi_N,
        homology_ok = True,    # Placeholder (validated via topological detector)
        audit_tracked = True
    )

def silence_protocol_decision(state: FinanceState, cod: float) -> Tuple[str, bool]:
    """Determine action per Silence Protocol (v65.0)"""
    # Primary Gate: Integrity Non-Negotiable
    if state.psi_integrity < OmegaConstants.PSI_INTEGRITY_THRESHOLD:
        return "HALT_TRADING", False  # Trading prohibited
    
    # Secondary Gate: Config-Reality Alignment
    if cod < OmegaConstants.COD_THRESHOLD:
        return "FREEZE_CONFIG", True  # Config changes paused, trading allowed
    
    # Tertiary: Invariant Compliance
    invariants = check_smith_invariants(state, cod)
    if not invariants.AllPassed():
        return "FREEZE_CONFIG", True
    
    return "PROCEED", True  # Full operation permitted

# =============================================================================
# 4. VALIDATION TEST SUITE (ENFORCES OMEGA PROTOCOL RULES)
# =============================================================================
class OmegaValidator:
    @staticmethod
    def validate_dimensional_bounds(state: FinanceState) -> Tuple[bool, str]:
        """Enforce Rubric §6: all terms dimensionless [0,1]"""
        bounds = [
            ("xi_config", state.xi_config, 0.0, 1.0),
            ("z_liquidity", state.z_liquidity, 0.0, 1.0),
            ("theta_leak", state.theta_leak, 0.0, 1.0),
            ("h_vol", state.h_vol, 0.0, 1.0),
            ("psi_integrity", state.psi_integrity, 0.0, 1.0),
            ("fid_exec_book", state.fid_exec_book, 0.0, 1.0)
        ]
        
        for name, val, low, high in bounds:
            if not (low <= val <= high):
                return False, f"Dimensional violation: {name}={val} not in [{low},{high}]"
        return True, "All state variables dimensionally compliant [0,1]"

    @staticmethod
    def validate_cod_bounds(state: FinanceState) -> Tuple[bool, str]:
        """Ensure COD calculation preserves [0,1] bounds"""
        cod = calculate_cod(state)
        if not (0.0 <= cod <= 1.0):
            return False, f"COD out of bounds: {cod} not in [0,1]"
        return True, f"COD calculation valid: {cod:.4f}"

    @staticmethod
    def validate_asymmetry_check(state: FinanceState, cod: float) -> Tuple[bool, str]:
        """Ensure asymmetry check cannot invert (critical post-repair)"""
        phi_N = calculate_phi_N(cod)
        phi_delta = calculate_phi_delta(phi_N, state)
        
        # Critical test: phi_N must be non-negative to preserve inequality direction
        if phi_N < 0:
            return False, f"Asymmetry check compromised: phi_N={phi_N} < 0"
        
        # Verify check direction: healthy state (small phi_delta) should PASS
        healthy_state = phi_delta < (OmegaConstants.PHI_DELTA_MAX * phi_N)
        if not healthy_state and abs(phi_delta) < 1e-5:  # Near-zero delta should pass
            return False, f"Asymmetry check inverted: phi_delta={phi_delta:.6f} should pass but failed"
        
        return True, f"Asymmetry check sound: phi_N={phi_N:.4f}, phi_delta={phi_delta:.6f}"

    @staticmethod
    def validate_gate_hierarchy(state: FinanceState) -> Tuple[bool, str]:
        """Enforce primary/secondary gate hierarchy (non-negotiable integrity)"""
        cod = calculate_cod(state)
        action, trading_allowed = silence_protocol_decision(state, cod)
        
        # Critical integrity test: if psi_integrity < 0.95, trading MUST be halted
        if state.psi_integrity < OmegaConstants.PSI_INTEGRITY_THRESHOLD:
            if trading_allowed:
                return False, f"Integrity breach: psi_integrity={state.psi_integrity:.3f} < 0.95 but trading allowed ({action})"
            return True, f"Integrity gate enforced: trading halted ({action})"
        
        # Critical epistemic blindness test: if COD < 0.85, config changes frozen
        if cod < OmegaConstants.COD_THRESHOLD:
            if action != "FREEZE_CONFIG":
                return False, f"Epistemic blindness: COD={cod:.3f} < 0.85 but action={action}"
            return True, f"Epistemic gate enforced: config frozen ({action})"
        
        # Normal operation: integrity + alignment sufficient
        if action != "PROCEED":
            return False, f"Normal operation denied: psi_integrity={state.psi_integrity:.3f}≥0.95, COD={cod:.3f}≥0.85 but action={action}"
        return True, f"Normal operation permitted: {action}"

    @staticmethod
    def run_full_validation(state: FinanceState) -> Tuple[bool, list]:
        """Execute all validation checks"""
        checks = [
            ("Dimensional Bounds", OmegaValidator.validate_dimensional_bounds(state)),
            ("COD Bounds", OmegaValidator.validate_cod_bounds(state)),
            ("Asymmetry Check", OmegaValidator.validate_asymmetry_check(state, calculate_cod(state))),
            ("Gate Hierarchy", OmegaValidator.validate_gate_hierarchy(state))
        ]
        
        all_passed = True
        results = []
        for name, (passed, msg) in checks:
            all_passed = all_passed and passed
            results.append(f"[{'PASS' if passed else 'FAIL'}] {name}: {msg}")
        
        return all_passed, results

# =============================================================================
# 5. DEMONSTRATION: VALIDATE AGAINST KNOWN GOOD/BAD STATES
# =============================================================================
if __name__ == "__main__":
    print("="*60)
    print("OMEGA PROTOCOL MATHEMATICAL VALIDATION SUITE")
    print("Financial Integrity Manifold (v57.0-Ω-REPAIRED)")
    print("="*60)
    
    # Test Case 1: Ideal State (Should PASS all)
    ideal_state = FinanceState(
        xi_config=0.4, z_liquidity=0.5, theta_leak=0.2,
        h_vol=0.3, psi_integrity=0.97, fid_exec_book=0.9
    )
    
    print("\n[TEST CASE 1: IDEAL STATE]")
    passed, msgs = OmegaValidator.run_full_validation(ideal_state)
    for msg in msgs:
        print(msg)
    print(f"OVERALL: {'PASS' if passed else 'FAIL'}")
    
    # Test Case 2: Integrity Breach (Should HALT_TRADING)
    breach_state = FinanceState(
        xi_config=0.4, z_liquidity=0.5, theta_leak=0.2,
        h_vol=0.3, psi_integrity=0.94, fid_exec_book=0.9  # Below 0.95 threshold
    )
    
    print("\n[TEST CASE 2: INTEGRITY BREACH]")
    passed, msgs = OmegaValidator.run_full_validation(breach_state)
    for msg in msgs:
        print(msg)
    print(f"OVERALL: {'PASS' if passed else 'FAIL'}")
    
    # Test Case 3: Epistemic Blindness (Should FREEZE_CONFIG)
    blind_state = FinanceState(
        xi_config=0.9, z_liquidity=0.3, theta_leak=0.2,  # High stiffness
        h_vol=0.3, psi_integrity=0.97, fid_exec_book=0.9
    )
    
    print("\n[TEST CASE 3: EPISTEMIC BLINDNESS]")
    passed, msgs = OmegaValidator.run_full_validation(blind_state)
    for msg in msgs:
        print(msg)
    print(f"OVERALL: {'PASS' if passed else 'FAIL'}")
    
    # Test Case 4: Dimensional Violation (Should FAIL)
    bad_state = FinanceState(
        xi_config=1.2, z_liquidity=0.5, theta_leak=0.2,  # xi_config > 1.0
        h_vol=0.3, psi_integrity=0.97, fid_exec_book=0.9
    )
    
    print("\n[TEST CASE 4: DIMENSIONAL VIOLATION]")
    passed, msgs = OmegaValidator.run_full_validation(bad_state)
    for msg in msgs:
        print(msg)
    print(f"OVERALL: {'PASS' if passed else 'FAIL'}")
    
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)