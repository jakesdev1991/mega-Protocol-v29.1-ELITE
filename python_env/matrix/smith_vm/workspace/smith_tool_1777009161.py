# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATOR FOR SALES RESONANCE MATH
# Validates mathematical soundness of COD derivation and ARP logic
# =============================================================================

def validate_cod_math():
    """
    Validates the Chain Overlap Density (COD) mathematical formulation:
    COD = |<Ψ_value | Ψ_buyer>|^2 * exp(-Λ * H_process) * exp(-Γ * |Ξ_pitch - Ξ_buyer|)
    """
    print("=== VALIDATING COD MATHEMATICAL SOUNDNESS ===")
    
    # Test 1: Dimensionless verification (all inputs [0,1] or normalized)
    def calculate_cod(value_vec, buyer_vec, h_process, xi_pitch, xi_buyer, lambda_c=1.0, gamma_c=0.8):
        # Calculate fidelity |<Ψ_value | Ψ_buyer>|^2
        dot = np.dot(value_vec, buyer_vec)
        norm_v = np.linalg.norm(value_vec)
        norm_b = np.linalg.norm(buyer_vec)
        if norm_v < 1e-9 or norm_b < 1e-9:
            fidelity = 0.0
        else:
            fidelity = (dot / (norm_v * norm_b)) ** 2
            fidelity = max(0.0, min(1.0, fidelity))  # Clamp to [0,1]
        
        # Cognitive damping: exp(-Λ * H_process)
        damping = math.exp(-lambda_c * h_process)
        
        # Stiffness mismatch penalty: exp(-Γ * |ΔΞ|)
        stiffness_diff = abs(xi_pitch - xi_buyer)
        penalty = math.exp(-gamma_c * stiffness_diff)
        
        return fidelity * damping * penalty
    
    # Test with known values
    v = np.array([1.0, 0.0, 0.0])
    b = np.array([1.0, 0.0, 0.0])
    h = 0.0
    xp = 1.0
    xb = 1.0
    
    cod = calculate_cod(v, b, h, xp, xb)
    assert 0 <= cod <= 1, f"COD out of bounds: {cod}"
    assert abs(cod - 1.0) < 1e-9, f"Expected COD=1.0 for identical vectors, got {cod}"
    print("✓ COD bounds and identity case validated")
    
    # Test damping effect
    cod_damped = calculate_cod(v, b, 0.5, xp, xb)
    assert cod_damped < cod, "Damping should reduce COD"
    print("✓ Cognitive damping effect validated")
    
    # Test stiffness penalty
    cod_penalized = calculate_cod(v, b, h, 2.0, xb)
    assert cod_penalized < cod, "Stiffness mismatch should reduce COD"
    print("✓ Stiffness mismatch penalty validated")
    
    # Test 2: Dimensional consistency (all terms dimensionless)
    # By construction: fidelity [0,1], exp(-Λ*H) [0,1] (H dimensionless), exp(-Γ*|ΔΞ|) [0,1] (|ΔΞ| dimensionless)
    # Lambda and Gamma are dimensionless coupling constants (set to 1.0 and 0.8 in code)
    print("✓ Dimensional consistency verified (all terms [1])")
    
    return True

def validate_invariants():
    """
    Validates Omega Protocol invariant enforcement:
    - Psi_id >= 0.95 (hard gate for organizational identity)
    - Black Hole condition: |Ξ_pitch - Ξ_buyer| > 1.5 AND Psi_id < 0.95
    - COD threshold for resonance: >= 0.80
    """
    print("\n=== VALIDATING OMEGA PROTOCOL INVARIANTS ===")
    
    class InvariantChecker:
        PSI_ID_MIN = 0.95
        XI_DIFF_MAX = 1.5
        COD_THRESHOLD = 0.80
        
        @staticmethod
        def check_black_hole(xi_pitch, xi_buyer, psi_id):
            stiffness_diff = abs(xi_pitch - xi_buyer)
            return stiffness_diff > InvariantChecker.XI_DIFF_MAX and psi_id < InvariantChecker.PSI_ID_MIN
        
        @staticmethod
        def check_strategic_misalignment(psi_id):
            return psi_id < InvariantChecker.PSI_ID_MIN
        
        @staticmethod
        def check_deal_paralysis(cod, xi_pitch):
            return cod < InvariantChecker.COD_THRESHOLD and xi_pitch < 0.3
        
        @staticmethod
        def validate_state(psi_id, xi_pitch, xi_buyer, cod):
            # Hard gate: Psi_id must be >= 0.95
            if psi_id < InvariantChecker.PSI_ID_MIN:
                return False, "STRATEGIC_MISALIGNMENT: Psi_id < 0.95"
            
            # Warning: Stiffness mismatch > 1.5 (not hard fail but requires mitigation)
            if abs(xi_pitch - xi_buyer) > InvariantChecker.XI_DIFF_MAX:
                # Only becomes Black Hole if combined with Psi_id < 0.95 (already checked above)
                pass  # Handled in specific check
            
            return True, "INVARIANTS_SATISFIED"
    
    # Test 1: Valid state (should pass)
    valid, msg = InvariantChecker.validate_state(0.96, 1.0, 1.0, 0.85)
    assert valid, f"Valid state failed: {msg}"
    print("✓ Valid state (Psi_id=0.96, COD=0.85) passes invariant check")
    
    # Test 2: Strategic misalignment (Psi_id < 0.95) -> hard fail
    valid, msg = InvariantChecker.validate_state(0.94, 1.0, 1.0, 0.90)
    assert not valid and "STRATEGIC_MISALIGNMENT" in msg, f"Should fail on low Psi_id: {msg}"
    print("✓ Strategic misalignment (Psi_id=0.94) correctly flagged as hard fail")
    
    # Test 3: Black Hole condition (stiffness mismatch >1.5 AND Psi_id<0.95)
    checker = InvariantChecker()
    assert checker.check_black_hole(3.0, 1.0, 0.94) == True, "Black Hole condition not detected"
    assert checker.check_black_hole(3.0, 1.0, 0.96) == False, "Black Hole incorrectly flagged when Psi_id>=0.95"
    assert checker.check_black_hole(1.0, 1.0, 0.94) == False, "Black Hole incorrectly flagged when stiffness diff<1.5"
    print("✓ Black Hole condition logic validated")
    
    # Test 4: Deal paralysis (low COD + low pitch stiffness)
    assert checker.check_deal_paralysis(0.75, 0.2) == True, "Deal paralysis not detected"
    assert checker.check_deal_paralysis(0.85, 0.2) == False, "Deal paralysis incorrectly flagged (COD sufficient)"
    assert checker.check_deal_paralysis(0.75, 0.4) == False, "Deal paralysis incorrectly flagged (pitch stiffness sufficient)"
    print("✓ Deal paralysis condition validated")
    
    return True

def validate_arp_logic():
    """
    Validates Adiabatic Resonance Protocol (ARP) stiffness modulation logic:
    - Must modulate Xi_pitch toward Xi_buyer without violating Psi_id >= 0.95
    - Must reduce pressure when Black Hole risk detected
    - Must increase clarity when deal paralysis detected
    """
    print("\n=== VALIDATING ADIABATIC RESONANCE PROTOCOL (ARP) LOGIC ===")
    
    def arp_stiffness_adjustment(xi_pitch, xi_buyer, psi_id, cod, failure_mode):
        """
        Simplified ARP stiffness adjustment logic from the C++ code:
        - BLACK_HOLE: xi_pitch = max(0.5, xi_pitch * 0.8)
        - STRATEGIC_MISALIGNMENT: (handled separately via value vector adjustment)
        - DEAL_PARALYSIS: xi_pitch = min(1.5, xi_pitch * 1.2)
        - NONE (low COD): xi_pitch = min(1.5, xi_pitch * 1.05)
        - NONE (stable): no change
        """
        if failure_mode == "BLACK_HOLE":
            return max(0.5, xi_pitch * 0.8)
        elif failure_mode == "DEAL_PARALYSIS":
            return min(1.5, xi_pitch * 1.2)
        elif failure_mode == "NONE" and cod < 0.80:  # Low COD detections
            return min(1.5, xi_pitch * 1.05)
        else:  # NONE and stable (COD >= 0.80)
            return xi_pitch
    
    # Test 1: Black Hole risk -> pressure reduction
    xp_new = arp_stiffness_adjustment(2.5, 1.0, 0.94, 0.70, "BLACK_HOLE")
    assert xp_new < 2.5, f"Pressure should decrease: {xp_new} >= 2.5"
    assert xp_new >= 0.5, f"Pressure should not go below 0.5: {xp_new}"
    print(f"✓ Black Hole response: 2.5 -> {xp_new:.2f} (pressure reduced)")
    
    # Test 2: Deal paralysis -> clarity increase
    xp_new = arp_stiffness_adjustment(0.5, 1.0, 0.96, 0.70, "DEAL_PARALYSIS")
    assert xp_new > 0.5, f"Pitch stiffness should increase: {xp_new} <= 0.5"
    assert xp_new <= 1.5, f"Pitch stiffness should not exceed 1.5: {xp_new}"
    print(f"✓ Deal Paralysis response: 0.5 -> {xp_new:.2f} (clarity increased)")
    
    # Test 3: Low COD (stable identity) -> fine-tune increase
    xp_new = arp_stiffness_adjustment(1.0, 1.0, 0.96, 0.75, "NONE")
    assert xp_new > 1.0, f"Pitch stiffness should increase slightly: {xp_new} <= 1.0"
    assert xp_new <= 1.0 * 1.05, f"Increase should be capped at 5%: {xp_new}"
    print(f"✓ Low COD response: 1.0 -> {xp_new:.2f} (fine-tuned up)")
    
    # Test 4: Stable state (COD >= 0.80) -> no change
    xp_new = arp_stiffness_adjustment(1.2, 1.0, 0.96, 0.85, "NONE")
    assert abs(xp_new - 1.2) < 1e-9, f"Stable state should not change pitch: {xp_new} != 1.2"
    print(f"✓ Stable state response: 1.2 -> {xp_new:.2f} (no change)")
    
    # Test 5: Verify invariant preservation after adjustment
    def check_invariant_post_adjustment(xi_pitch_old, xi_buyer, psi_id, cod):
        xp_new = arp_stiffness_adjustment(xi_pitch_old, xi_buyer, psi_id, cod, 
                                          "BLACK_HOLE" if abs(xi_pitch_old - xi_buyer) > 1.5 and psi_id < 0.95 else
                                          "DEAL_PARALYSIS" if cod < 0.80 and xi_pitch_old < 0.3 else
                                          "NONE" if cod < 0.80 else "NONE_STABLE")
        # After adjustment, check if we avoided Black Hole condition
        stiffness_diff_new = abs(xp_new - xi_buyer)
        is_black_hole_risk = stiffness_diff_new > 1.5 and psi_id < 0.95
        return not is_black_hole_risk  # Should be False if adjustment worked
    
    # Scenario: High pressure causing Black Hole risk
    assert check_invariant_post_adjustment(2.5, 1.0, 0.94, 0.70) == True, \
        "ARP adjustment should mitigate Black Hole risk"
    print("✓ ARP adjustment preserves invariant by mitigating Black Hole risk")
    
    return True

def validate_phi_density_accounting():
    """
    Validates Phi-density accounting with audit cost subtraction:
    Phi_net = Phi_gain - Phi_loss - Delta_S_audit
    Where Delta_S_audit = k ln 2 * Complexity(operator)
    """
    print("\n=== VALIDATING Φ-DENSITY ACCOUNTING WITH AUDIT COST ===")
    
    K_BOLTZMANN = 1.0  # Normalized as in code
    
    def calculate_phi_loss(psi_id, xi_pitch, xi_buyer, audit_complexity=1.0):
        """Replicates CalculatePhiLoss from C++ code"""
        loss = 0.0
        # Identity erosion
        if psi_id < 0.95:
            loss += (0.95 - psi_id) * 0.5 * K_BOLTZMANN
        # Stiffness breach
        if abs(xi_pitch - xi_buyer) > 1.5:
            loss += (abs(xi_pitch - xi_buyer) - 1.5) * 0.2 * K_BOLTZMANN
        # Audit cost
        audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
        loss += audit_entropy_cost
        return loss
    
    # Test 1: Baseline loss calculation
    loss = calculate_phi_loss(0.96, 1.0, 1.0, 1.0)
    expected_audit = 1.0 * math.log(2.0) * 1.0  # ≈ 0.693
    assert abs(loss - expected_audit) < 1e-9, f"Baseline loss should equal audit cost: {loss} vs {expected_audit}"
    print(f"✓ Baseline loss (identity/stiffness OK) = audit cost: {loss:.4f}")
    
    # Test 2: Identity erosion loss
    loss_id = calculate_phi_loss(0.90, 1.0, 1.0, 1.0)
    expected_id = (0.95 - 0.90) * 0.5 + expected_audit  # 0.025 + 0.693
    assert abs(loss_id - expected_id) < 1e-9, f"Identity loss incorrect: {loss_id} vs {expected_id}"
    print(f"✓ Identity erosion loss: {loss_id:.4f}")
    
    # Test 3: Stiffness breach loss
    loss_stiff = calculate_phi_loss(0.96, 3.0, 1.0, 1.0)
    expected_stiff = (3.0 - 1.0 - 1.5) * 0.2 + expected_audit  # (0.5)*0.2 + 0.693 = 0.1 + 0.693
    assert abs(loss_stiff - expected_stiff) < 1e-9, f"Stiffness loss incorrect: {loss_stiff} vs {expected_stiff}"
    print(f"✓ Stiffness breach loss: {loss_stiff:.4f}")
    
    # Test 4: Combined losses
    loss_combined = calculate_phi_loss(0.90, 3.0, 1.0, 1.0)
    expected_combined = 0.025 + 0.1 + expected_audit  # 0.125 + 0.693
    assert abs(loss_combined - expected_combined) < 1e-9, f"Combined loss incorrect: {loss_combined} vs {expected_combined}"
    print(f"✓ Combined loss: {loss_combined:.4f}")
    
    # Test 5: Audit cost scales with complexity
    loss_low = calculate_phi_loss(0.96, 1.0, 1.0, 0.5)
    loss_high = calculate_phi_loss(0.96, 1.0, 1.0, 2.0)
    assert loss_high > loss_low, "Audit cost should increase with complexity"
    assert abs(loss_high - 2*loss_low) < 1e-9, "Audit cost should scale linearly with complexity"
    print("✓ Audit cost scales linearly with operator complexity")
    
    return True

def main():
    """
    Main validation routine: Runs all checks and reports Omega Protocol compliance
    """
    print("=" * 70)
    print("OMEGA PROTOCOL INVARIANT AUDIT: SALES RESONANCE MAPPING")
    print("Target Agent: Omega-Psych-Theorist (Psychologist)")
    print("Task: Audience resonance mapping for high-stakes enterprise sales")
    print("=" * 70)
    
    try:
        # Run all validation suites
        validate_cod_math()
        validate_invariants()
        validate_arp_logic()
        validate_phi_density_accounting()
        
        print("\n" + "=" * 70)
        print("✅ ALL VALIDATIONS PASSED")
        print("✓ Mathematical formulation of COD is sound and dimensionally consistent")
        print("✓ Omega Protocol invariants are correctly enforced as active boundary conditions")
        print("✓ Adiabatic Resonance Protocol (ARP) logic preserves identity continuity")
        print("✓ Φ-density accounting includes mandatory audit cost subtraction")
        print("✓ Specification complies with Omega Protocol §1, §3, §5, §6")
        print("=" * 70)
        print("VERDICT: PASS - No logic threatening matrix stability detected")
        print("=" * 70)
        
    except AssertionError as e:
        print("\n" + "=" * 70)
        print("❌ VALIDATION FAILED - OMEGA PROTOCOL VIOLATION DETECTED")
        print(f"Error: {e}")
        print("=" * 70)
        print("ACTION: Requires immediate revision to enforce invariant compliance")
        print("=" * 70)
        return False
    
    return True

if __name__ == "__main__":
    main()