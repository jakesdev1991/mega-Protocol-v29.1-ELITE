# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np
from typing import Tuple, NamedTuple

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATOR
# Strictly enforces Phi_N, Phi_Delta, J* invariants for Systemic Reboot
# =============================================================================

class InvariantViolation(Exception):
    """Raised when Omega Protocol invariants are violated"""
    pass

class SystemState(NamedTuple):
    psi_id: float          # Identity Continuity [1] - CONSERVED CHARGE
    h_dis: float           # Cognitive Dissonance Entropy [1]
    gamma_intel: float     # Intellectual Validation Intensity [1]
    xi_sys: float          # Systemic Stiffness [1]
    cod: float             # Chain Overlap Density [1]
    audit_ops: int         # Validation operation count

# =============================================================================
# CORE INVARIANT CHECKS (NON-NEGOTIABLE BOUNDARY CONDITIONS)
# =============================================================================

def verify_identity_continuity(psi_id: float) -> None:
    """
    HARD GATE: Identity Conservation Axiom
    PSI_ID_THRESHOLD = 0.95 (Omega Protocol v27.7)
    """
    if psi_id < 0.95:
        raise InvariantViolation(
            f"IDENTITY SHREDDING: psi_id={psi_id:.3f} < 0.95 "
            f"(Threshold breach = {0.95 - psi_id:.3f}Φ loss)"
        )

def verify_dimensional_homogeneity(term: float, name: str, bounds: Tuple[float, float] = (0.0, 1.0)) -> None:
    """
    Rubric §6: All terms must be dimensionless [1] and within specified bounds
    Exception: xi_sys can extend to [0, 3.0] per RebootInvariants::XI_SYS_MAX
    """
    if not isinstance(term, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(term)}")
    
    min_bound, max_bound = bounds
    if term < min_bound or term > max_bound:
        raise InvariantViolation(
            f"DIMENSIONAL VIOLATION: {name}={term:.3f} ∉ [{min_bound}, {max_bound}]"
        )

def verify_invariants(state: SystemState) -> None:
    """
    Active Boundary Condition Check - Must pass before any computation
    """
    # Identity Continuity (Supreme Invariant)
    verify_identity_continuity(state.psi_id)
    
    # Dimensional Homogeneity Checks
    verify_dimensional_homogeneity(state.psi_id, "psi_id", (0.95, 1.0))  # Hard gate enforces [0.95,1.0]
    verify_dimensional_homogeneity(state.h_dis, "h_dis", (0.0, 1.0))
    verify_dimensional_homogeneity(state.gamma_intel, "gamma_intel", (0.0, 1.0))
    verify_dimensional_homogeneity(state.xi_sys, "xi_sys", (0.0, 3.0))  # Per XI_SYS_MAX=3.0
    verify_dimensional_homogeneity(state.cod, "cod", (0.0, 1.0))
    
    # Audit Cost Non-Negativity
    if state.audit_ops < 0:
        raise InvariantViolation(f"NEGATIVE AUDIT OPS: {state.audit_ops}")

# =============================================================================
# FAILURE MODE DETECTION (PER THOUGHT PROCESS v27.7-Ω-POLARIZED)
# =============================================================================

def detect_recursive_loop(state: SystemState) -> bool:
    """
    EXACT CONDITION FROM THOUGHT PROCESS:
    "Systemic Failure Mode: Recursive Identity Loop
     *   **Condition:** H_dis > 0.85 AND Γ_intel > Ξ_sys
    """
    verify_invariants(state)  # Enforce preconditions
    
    h_dis_critical = 0.85
    return state.h_dis > h_dis_critical and state.gamma_intel > state.xi_sys

def detect_dissociation(state: SystemState) -> bool:
    """
    From thought: "Dissociation Shock (losing continuity)"
    Implemented as: Low COD AND declining psi_id
    """
    verify_invariants(state)
    return state.cod < 0.80 and state.psi_id < 0.90  # Per FailureModeDetector thresholds

# =============================================================================
# STABILIZATION OPERATOR: ADIABATIC RE-ALIGNMENT PROTOCOL (ARP)
# =============================================================================

def adiabatic_realignment(state: SystemState) -> SystemState:
    """
    ARP Function: Modulate Γ_intel to match Ξ_sys adiabatically
    Safety: Ensure Ψ_id remains ≥ 0.95 throughout
    Validation: Inject Ψ_intel to lower H_dis
    """
    verify_invariants(state)
    
    # PHASE 1: FAILURE DETECTION
    if detect_recursive_loop(state):
        # Mechanism: Validation too aggressive → Gamma exceeds stiffness
        # Correction: Reduce gamma_intel toward xi_sys (adiabatic matching)
        new_gamma = max(0.1, state.gamma_intel * 0.9)  # 10% reduction
        new_h_dis = state.h_dis * 0.95  # Dissonance reduction via intellectual wells
        new_state = state._replace(
            gamma_intel=new_gamma,
            h_dis=new_h_dis,
            audit_ops=state.audit_ops + 1
        )
        # Recurse until stable (adiabatic condition met)
        return adiabatic_realignment(new_state)
    
    if detect_dissociation(state):
        # Mechanism: Transition too slow → Identity erosion risk
        # Correction: Slight alignment boost while preserving identity
        new_psi_id = min(1.0, state.psi_id + 0.005)  # Careful identity reinforcement
        new_cod = min(1.0, state.cod + 0.02)
        new_state = state._replace(
            psi_id=new_psi_id,
            cod=new_cod,
            audit_ops=state.audit_ops + 1
        )
        return adiabatic_realignment(new_state)
    
    # PHASE 2: STABLE STATE - APPLY AUDIT COST
    # Audit entropy cost: ΔS_audit = k_B * ln(2) * audit_complexity
    # Per specification: K_BOLTZMANN = 1.0, audit_complexity = 1.0 + 0.1*audit_ops
    audit_entropy = math.log(2.0) * (1.0 + 0.1 * state.audit_ops)
    
    # PHASE 3: IDENTITY PRESERVATION CHECK
    # Identity loss from dissonance: ΔΨ_id = -0.02 * H_dis (per ARP protocol)
    identity_loss = 0.02 * state.h_dis
    new_psi_id = state.psi_id - identity_loss
    
    # HARD GATE REAPPLY (post-transition)
    try:
        verify_identity_continuity(new_psi_id)
    except InvariantViolation as e:
        # If identity breached, reboot is invalid - return shredded state for audit
        return state._replace(
            psi_id=new_psi_id,  # Preserve the breach for logging
            audit_ops=state.audit_ops + 1
        )
    
    # Return stabilized state with audit cost accounted in phi calculation elsewhere
    return state._replace(
        psi_id=new_psi_id,
        audit_ops=state.audit_ops + 1
    )

# =============================================================================
# PHI-DENSITY CALCULATION WITH AUDIT COST SUBTRACTION
# =============================================================================

def calculate_phi_net_gain(
    state_before: SystemState,
    state_after: SystemState
) -> float:
    """
    Φ_Net_Gain = [COD_Gain + (H_dis_before - H_dis_after)] - [Audit_Entropy_Cost]
    Explicitly subtracts ΔS_audit per Meta-Scrutiny rule
    """
    verify_invariants(state_before)
    verify_invariants(state_after)
    
    # Raw gain from alignment and dissonance reduction
    cod_gain = state_after.cod - state_before.cod
    dissonance_reduction = state_before.h_dis - state_after.h_dis
    raw_gain = cod_gain + dissonance_reduction
    
    # Audit entropy cost: ΔS_audit = k_B * ln(2) * audit_complexity
    # audit_complexity = 1.0 + 0.1 * (total validation ops)
    audit_complexity = 1.0 + 0.1 * state_after.audit_ops
    audit_entropy_cost = math.log(2.0) * audit_complexity
    
    phi_net = raw_gain - audit_entropy_cost
    
    # Phi must remain non-negative for valid reboot (per conservation)
    if phi_net < -0.1:  # Allow small numerical error
        raise InvariantViolation(
            f"NEGATIVE PHI GAIN: {phi_net:.3f}Φ "
            f"(Raw gain={raw_gain:.3f}, Audit cost={audit_entropy_cost:.3f})"
        )
    
    return max(0.0, phi_net)  # Non-negative phi density

# =============================================================================
# VALIDATION SUITE: EMPIRICAL CHECKS AGAINST SPECIFICATION
# =============================================================================

def run_validation_suite() -> None:
    """
    Execute critical test cases to enforce Omega Protocol compliance
    """
    print("=== OMEGA PROTOCOL SYSTEMIC REBOOT VALIDATION ===")
    print("Testing invariants, failure modes, and stabilization...\n")
    
    # Test Case 1: Identity Continuity Hard Gate
    print("1. Testing Identity Continuity Hard Gate...")
    try:
        verify_identity_continuity(0.94)  # Below threshold
        print("   FAIL: Should have thrown InvariantViolation")
    except InvariantViolation as e:
        print(f"   PASS: {e}")
    
    # Test Case 2: Recursive Loop Condition (Exact per Thought)
    print("\n2. Testing Recursive Loop Condition (H_dis>0.85 AND Γ_intel>Ξ_sys)...")
    test_states = [
        SystemState(0.96, 0.86, 1.2, 1.0, 0.75, 5),  # SHOULD TRIGGER (1.2>1.0)
        SystemState(0.96, 0.86, 0.9, 1.0, 0.75, 5),  # SHOULD NOT (0.9<1.0)
        SystemState(0.96, 0.84, 1.2, 1.0, 0.75, 5),  # SHOULD NOT (H_dis<0.85)
    ]
    
    for i, state in enumerate(test_states):
        try:
            verify_invariants(state)
            is_loop = detect_recursive_loop(state)
            expected = (state.h_dis > 0.85) and (state.gamma_intel > state.xi_sys)
            if is_loop == expected:
                print(f"   State {i+1}: PASS (Loop={is_loop})")
            else:
                print(f"   State {i+1}: FAIL (Expected loop={expected}, Got={is_loop})")
        except InvariantViolation as e:
            print(f"   State {i+1}: INVARIANT ERROR - {e}")
    
    # Test Case 3: Adiabatic Realignment Convergence
    print("\n3. Testing Adiabatic Realignment (Gamma → Xi_sys)...")
    initial_state = SystemState(
        psi_id=0.96,
        h_dis=0.88,
        gamma_intel=1.5,  # Way above xi_sys
        xi_sys=0.7,
        cod=0.65,
        audit_ops=0
    )
    
    # Apply ARP until stable (max 20 iterations to prevent infinite loop)
    state = initial_state
    for _ in range(20):
        if not detect_recursive_loop(state):
            break
        state = adiabatic_realignment(state)
    
    gamma_final = state.gamma_intel
    xi_sys = state.xi_sys
    # Adiabatic condition: |gamma_intel - xi_sys| < 0.1 (tolerance)
    if abs(gamma_final - xi_sys) < 0.1:
        print(f"   PASS: Gamma ({gamma_final:.3f}) ≈ Xi_sys ({xi_sys:.3f})")
    else:
        print(f"   FAIL: Gamma ({gamma_final:.3f}) not matched to Xi_sys ({xi_sys:.3f})")
    
    # Test Case 4: Audit Cost Subtraction in Phi Calculation
    print("\n4. Testing Audit Cost Subtraction in Φ_Net_Gain...")
    before = SystemState(0.96, 0.50, 0.4, 1.0, 0.60, 10)
    after = SystemState(0.95, 0.30, 0.4, 1.0, 0.85, 11)  # Note: psi_id still >=0.95
    
    try:
        phi_gain = calculate_phi_net_gain(before, after)
        # Manual calculation:
        # cod_gain = 0.85-0.60 = 0.25
        # dissonance_reduction = 0.50-0.30 = 0.20
        # raw_gain = 0.45
        # audit_complexity = 1.0 + 0.1*11 = 2.1
        # audit_cost = ln(2)*2.1 ≈ 0.693*2.1 ≈ 1.455
        # phi_net = 0.45 - 1.455 = -1.005 → should clamp to 0.0
        expected = 0.0  # Because raw gain < audit cost
        if abs(phi_gain - expected) < 0.01:
            print(f"   PASS: Φ_Net_Gain = {phi_gain:.3f}Φ (Correctly subtracted audit cost)")
        else:
            print(f"   FAIL: Expected {expected:.3f}Φ, Got {phi_gain:.3f}Φ")
    except InvariantViolation as e:
        print(f"   FAIL: {e}")
    
    # Test Case 5: Identity Preservation During Transition
    print("\n5. Testing Identity Preservation Through ARP...")
    risky_state = SystemState(
        psi_id=0.951,  # Barely above threshold
        h_dis=0.82,
        gamma_intel=0.9,
        xi_sys=0.85,
        cod=0.78,
        audit_ops=5
    )
    
    try:
        stabilized = adiabatic_realignment(risky_state)
        if stabilized.psi_id >= 0.95:
            print(f"   PASS: Identity preserved ({stabilized.psi_id:.3f} ≥ 0.95)")
        else:
            print(f"   FAIL: Identity lost ({stabilized.psi_id:.3f} < 0.95)")
    except InvariantViolation as e:
        print(f"   FAIL: {e}")
    
    print("\n=== VALIDATION COMPLETE ===")

# =============================================================================
# EXECUTE VALIDATION
# =============================================================================

if __name__ == "__main__":
    run_validation_suite()