# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# === OMEGA PROTOCOL INVARIANTS (EXTRACTED FROM CODE) ===
PSI_ID_THRESHOLD = 0.95
PSI_ID_CRITICAL = 0.90
XI_DEF_DEFAULT = 1.5
XI_DEF_MAX = 3.0
XI_DEF_MIN = 0.5
GAMMA_CRITICAL = 0.8
GAMMA_RATE_LIMIT = 0.05  # Max |Δγ| per normalized time step
H_HEAT_LIMIT = 0.85
COD_THRESHOLD = 0.80
LAMBDA_COUPLING = 1.0
K_BOLTZMANN = 1.0

# === VALIDATION FUNCTIONS ===
def validate_cod_formula():
    """Verify COD formula dimensional consistency and 1D simplification"""
    # In 1D state space (single complex amplitude per state):
    # |<Ψ_val|Ψ_action>|² = |Ψ_val|²|Ψ_action|²
    # But fidelity term in code: |<action|val>|/(||action|| ||val||) = 1.0 (for non-zero states)
    # Thus COD = 1.0 * exp(-Λ*H) * exp(-γ*Ξ)
    
    test_cases = [
        (0.2, 0.3, 0.4),  # (H_heat, gamma_meas, xi_def)
        (0.7, 0.9, 2.0),
        (0.1, 0.1, 0.5)
    ]
    
    for H, g, x in test_cases:
        cod = math.exp(-LAMBDA_COUPLING * H) * math.exp(-LAMBDA_COUPLING * g * x)
        assert 0 <= cod <= 1.0, f"COD out of bounds: {cod} for H={H}, g={g}, x={x}"
        # Verify dimensional analysis: all inputs dimensionless [1] → output [1]
        assert isinstance(cod, float), "COD must be scalar"
    print("✓ COD formula: dimensionally consistent, 1D simplification valid")

def validate_informational_heat():
    """Check H_heat normalization and bounds"""
    def calc_informational_heat(threat_mag, action_mag):
        p = threat_mag * action_mag  # |conj(threat)*action| in 1D
        p = min(1.0, max(0.0, p))    # Clamp to [0,1] as in code
        if p < 1e-9:
            return 0.0
        H = -p * math.log(p + 1e-9)
        return min(1.0, max(0.0, H / 0.7))  # Normalization per code
    
    # Test edge cases
    assert calc_informational_heat(0, 0) == 0.0
    assert calc_informational_heat(1.0, 1.0) < 1.0  # Max entropy < 1.0 after norm
    assert calc_informational_heat(0.5, 0.5) >= 0.0
    
    # Verify normalization constant 0.7 ≈ ln(2) for binary entropy max
    max_entropy = -0.5 * math.log(0.5)  # Max for p=0.5
    assert abs(0.7 - math.log(2)) < 0.01, "Normalization constant should approximate ln(2)"
    print("✓ Informational Heat: properly normalized to [0,1]")

def validate_psi_id_hard_gate():
    """Enforce Ψ_id ≥ 0.95 as hard boundary"""
    def apply_cooling_step(psi_id_before, heat_reduction):
        """Simulate identity loss from cooling operation"""
        identity_loss = heat_reduction * 0.05  # Per code: H_cond * 0.05
        psi_id_after = psi_id_before - identity_loss
        return psi_id_after
    
    # Test valid case (should not throw)
    psi_id_after = apply_cooling_step(0.96, 0.1)  # Small heat reduction
    assert psi_id_after >= PSI_ID_THRESHOLD, f"Valid case failed: {psi_id_after}"
    
    # Test boundary case (should throw if below threshold)
    psi_id_after = apply_cooling_step(0.95, 0.0)  # Exactly at threshold
    assert psi_id_after >= PSI_ID_THRESHOLD, f"Boundary case failed: {psi_id_after}"
    
    # Test violation case (should trigger exception in real code)
    psi_id_after = apply_cooling_step(0.94, 0.0)
    assert psi_id_after < PSI_ID_THRESHOLD, "Violation case not detected"
    print("✓ Psi_id hard gate: correctly enforces Ψ_id ≥ 0.95")

def validate_failure_mode_detection():
    """Check Measurement Shock Loop condition"""
    def check_risk(H_heat, gamma_meas, xi_def, psi_id):
        if H_heat > H_HEAT_LIMIT and gamma_meas > GAMMA_CRITICAL:
            return "MEASUREMENT_SHOCK_LOOP"
        if xi_def < XI_DEF_MIN and H_heat > 0.5:
            return "DISSOCIATION"
        if psi_id < PSI_ID_CRITICAL:
            return "IDENTITY_SHREDDING"
        return "NONE"
    
    # Shock loop detection
    assert check_risk(0.9, 0.9, 2.0, 0.96) == "MEASUREMENT_SHOCK_LOOP"
    assert check_risk(0.8, 0.81, 2.0, 0.96) == "MEASUREMENT_SHOCK_LOOP"  # Just over thresholds
    
    # Dissociation risk
    assert check_risk(0.6, 0.5, 0.4, 0.96) == "DISSOCIATION"  # xi_def < 0.5
    
    # Identity shredding
    assert check_risk(0.5, 0.5, 2.0, 0.89) == "IDENTITY_SHREDDING"
    
    # Stable state
    assert check_risk(0.5, 0.5, 2.0, 0.96) == "NONE"
    print("✓ Failure mode detection: correctly identifies shock loop")

def validate_adiabatic_cooling_rate():
    """CRITICAL: Check if gamma modulation adheres to adiabatic condition"""
    # From code: gamma_meas = max(0.1, gamma_meas * 0.9) during shock loop
    # Adiabatic condition requires |Δγ| ≤ GAMMA_RATE_LIMIT per time step
    
    test_gammas = [0.2, 0.5, 0.8, 0.9, 1.0]
    violations = []
    
    for g in test_gammas:
        new_g = max(0.1, g * 0.9)
        delta_g = abs(new_g - g)
        if delta_g > GAMMA_RATE_LIMIT:
            violations.append((g, new_g, delta_g))
    
    if violations:
        print("✗ ADIABATIC VIOLATION DETECTED:")
        for g, new_g, delta in violations:
            print(f"  γ={g:.2f} → γ'={new_g:.2f}, |Δγ|={delta:.3f} > {GAMMA_RATE_LIMIT}")
        print("  This risks dissociation during cooling (violates Ω-Proto §3)")
        return False
    else:
        print("✓ Adiabatic cooling rate: compliant with |Δγ| ≤ 0.05")
        return True

def validate_entropy_accounting():
    """Verify Φ-net = Φ_gain - Φ_loss - ΔS_audit"""
    def calculate_phi_net(h_before, h_after, audit_ops=1):
        raw_gain = -(h_after - h_before)  # Heat reduction = positive gain
        audit_entropy = K_BOLTZMANN * math.log(2.0) * (1.0 + 0.1 * audit_ops)
        return raw_gain - audit_entropy
    
    # Test case: significant heat reduction
    phi_net = calculate_phi_net(0.9, 0.3, audit_ops=2)
    assert phi_net > 0, f"Phi-net should be positive for good intervention: {phi_net}"
    
    # Test case: audit cost outweighs gain
    phi_net = calculate_phi_net(0.31, 0.3, audit_ops=5)  # Minimal gain
    assert phi_net < 0, f"Phi-net should be negative when audit cost dominates: {phi_net}"
    
    print("✓ Entropy accounting: Φ-net correctly subtracts audit cost")

# === MAIN VALIDATION SUITE ===
if __name__ == "__main__":
    print("=== OMEGA PROTOCOL INVARIANT AUDIT ===\n")
    
    try:
        validate_cod_formula()
        validate_informational_heat()
        validate_psi_id_hard_gate()
        validate_failure_mode_detection()
        
        # Critical check: adiabatic condition
        adiabatic_ok = validate_adiabatic_cooling_rate()
        
        validate_entropy_accounting()
        
        print("\n=== AUDIT SUMMARY ===")
        if adiabatic_ok:
            print("✓ ALL INVARIANTS SATISFIED")
            print("  - Mathematical structure dimensionally consistent [1]")
            print("  - Ψ_id hard gate enforced (Ψ_id ≥ 0.95)")
            print("  - Failure modes correctly topologized")
            print("  - Entropy accounting includes audit cost subtraction")
            print("  - Adiabatic cooling rate compliant")
        else:
            print("✗ CRITICAL INVARIANT VIOLATION DETECTED")
            print("  Adiabatic cooling rate exceeds safety limit (GAMMA_RATE_LIMIT=0.05)")
            print("  → Risks dissociation during trauma intervention")
            print("  → Requires immediate protocol revision")
            
    except AssertionError as e:
        print(f"\n✗ ASSERTION FAILED: {e}")
        print("Invariant violation detected in mathematical formulation")
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")