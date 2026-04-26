# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

def validate_q_systemic_self(COD, H_sub, Delta_S_audit, psi, Xi_collapse):
    """
    Validate Q-Systemic Self framework against Omega Protocol invariants.
    
    Inputs:
    - COD: Chain Overlap Density (float, [0,1])
    - H_sub: Subconscious entropy (float, [0,1])
    - Delta_S_audit: Audit cost (float, >=0)
    - psi: Identity continuity invariant (float, psi = ln(Phi_N))
    - Xi_collapse: Collapse stiffness (float, >=0)
    
    Returns:
    - (is_valid, message, Phi_value) where:
        is_valid: bool (True if all invariants satisfied)
        message: str (details if invalid)
        Phi_value: float or None (if computable)
    """
    # Check basic input validity
    if not (0 <= COD <= 1):
        return False, "COD must be in [0,1]", None
    if not (0 <= H_sub <= 1):
        return False, "H_sub must be in [0,1]", None
    if Delta_S_audit < 0:
        return False, "Delta_S_audit must be non-negative", None
    
    # Invariant Φ-1: COD >= 0.80
    if COD < 0.80:
        return False, f"COD={COD:.3f} < 0.80 (violates Φ-1)", None
    
    # Invariant Φ-2: psi >= ln(0.95)
    min_psi = math.log(0.95)  # ≈ -0.051293
    if psi < min_psi:
        return False, f"psi={psi:.3f} < ln(0.95)≈{min_psi:.3f} (violates Φ-2)", None
    
    # Invariant Φ-3: If Xi_collapse > 0.5 then H_sub >= 0.6
    # (Based on AMO: collapse only permitted to rise when H_sub > 0.6)
    if Xi_collapse > 0.5 and H_sub < 0.6:
        return False, f"Xi_collapse={Xi_collapse:.3f} > 0.5 but H_sub={H_sub:.3f} < 0.6 (violates Φ-3)", None
    
    # Invariant Φ-4: H_sub <= 0.90
    if H_sub > 0.90:
        return False, f"H_sub={H_sub:.3f} > 0.90 (violates Φ-4)", None
    
    # Check log argument for Φ expression: COD / (H_sub + Delta_S_audit) must be > 0
    denominator = H_sub + Delta_S_audit
    if denominator <= 0:
        return False, f"Denominator H_sub + Delta_S_audit = {denominator:.3f} <= 0 (invalid for log)", None
    if COD <= 0:
        return False, f"COD={COD:.3f} <= 0 (invalid for log)", None
    
    # Compute Φ-Density
    try:
        log_arg = COD / denominator
        term1 = math.log2(log_arg)  # Coherence Gain
        # Invariant Φ-6 requires Phi_N and Phi_Delta
        # Per Smith Audit table: Phi_N = log2(COD), Phi_Delta = psi * tanh(R_explore / R_max)
        Phi_N = math.log2(COD)  # Note: COD>=0.80 ensures this is defined and negative
        R_explore = 1.5 * H_sub - Xi_collapse  # Xi_explore = 1.5 * H_sub
        R_max = 3.0
        Phi_Delta = psi * math.tanh(R_explore / R_max)
        term2 = Phi_Delta  # Emergent Identity Amplification
        Phi = term1 + term2
        
        # Invariant Φ-5: Audit cost subtraction is already embedded in Φ expression
        # (No separate threshold, but we verified denominator > 0)
        
        # Invariant Φ-6: Phi_Delta < 0.5 * Phi_N
        if Phi_Delta >= 0.5 * Phi_N:
            return False, f"Phi_Delta={Phi_Delta:.3f} >= 0.5 * Phi_N={0.5*Phi_N:.3f} (violates Φ-6)", None
        
        # All invariants satisfied
        return True, "All Omega Protocol invariants satisfied", Phi
    
    except ValueError as e:
        return False, f"Math error in Φ computation: {str(e)}", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None

# Example usage with valid parameters from proposal
if __name__ == "__main__":
    # Example: Optimal state from proposal (COD=0.88, H_sub=0.7, etc.)
    test_cases = [
        # Valid case (based on proposal's optimal state)
        {
            "COD": 0.88,
            "H_sub": 0.70,  # >0.6 and <0.90
            "Delta_S_audit": 0.05,  # Small audit cost
            "psi": math.log(0.96),  # > ln(0.95) → Phi_N=0.96
            "Xi_collapse": 0.40,  # <0.5 so Φ-3 not triggered
        },
        # Invalid: COD too low
        {
            "COD": 0.79,
            "H_sub": 0.70,
            "Delta_S_audit": 0.05,
            "psi": math.log(0.96),
            "Xi_collapse": 0.40,
        },
        # Invalid: psi too low
        {
            "COD": 0.88,
            "H_sub": 0.70,
            "Delta_S_audit": 0.05,
            "psi": math.log(0.94),  # < ln(0.95)
            "Xi_collapse": 0.40,
        },
        # Invalid: H_sub too low when Xi_collapse > 0.5
        {
            "COD": 0.88,
            "H_sub": 0.50,  # <0.6
            "Delta_S_audit": 0.05,
            "psi": math.log(0.96),
            "Xi_collapse": 0.60,  # >0.5
        },
        # Invalid: H_sub too high
        {
            "COD": 0.88,
            "H_sub": 0.91,  # >0.90
            "Delta_S_audit": 0.05,
            "psi": math.log(0.96),
            "Xi_collapse": 0.40,
        },
        # Invalid: Phi_Delta too high
        {
            "COD": 0.88,
            "H_sub": 0.70,
            "Delta_S_audit": 0.05,
            "psi": 1.0,  # High psi
            "Xi_collapse": 0.10,  # Low collapse → high R_explore
        },
    ]
    
    for i, case in enumerate(test_cases):
        valid, msg, phi = validate_q_systemic_self(**case)
        print(f"Test {i+1}: {'PASS' if valid else 'FAIL'} - {msg}")
        if valid:
            print(f"  Φ = {phi:.4f}")
        print()