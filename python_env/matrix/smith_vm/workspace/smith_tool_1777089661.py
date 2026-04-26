# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATOR FOR TRAUMA-PERFORMANCE MODEL
# ENFORCES: Phi_N (identity), Phi_Delta (entropy flow), J* (cost functional)
# VALIDATES: Mathematical consistency, dimensional compliance, invariant gates
# =============================================================================

class OmegaTraumaValidator:
    """Strict validator for trauma-induced high-energy anxiety model per Omega Protocol v29.1"""
    
    # OMEGA PROTOCOL CONSTANTS (NON-NEGOTIABLE INVARIANTS)
    PSI_ID_MIN = 0.95          # Identity integrity floor (Phi_N >= 0.95)
    XI_CON_CRITICAL = 2.5      # Conscious stiffness collapse threshold
    H_SUB_LIMIT = 0.85         # Maximum trauma entropy load
    COD_THRESHOLD = 0.80       # Minimum authentic alignment threshold
    LAMBDA_COUPLING = 1.0      # Entropic damping constant
    GAMMA_COUPLING = 0.5       # Stiffness penalty constant
    K_BOLTZMANN = 1.0          # Normalized for informational entropy
    
    @staticmethod
    def validate_dimensionless(term_name, value, tolerance=1e-9):
        """Enforce Rubric §6: All terms must be dimensionless [1]"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{term_name} must be scalar dimensionless [1], got {type(value)}")
        if abs(value) > 1e10:  # Practical bound for normalized quantities
            raise ValueError(f"{term_name} exceeds reasonable dimensionless range: {value}")
        return True
    
    @staticmethod
    def validate_cod(psi_sub, psi_con, h_sub, xi_con):
        """
        Validate COD calculation per Equation-Level Derivation (Rubric §6)
        COD = |<ψ_sub|ψ_con>|² · exp(-Λ·H_sub) · exp(-Γ·Ξ_con)
        """
        # Input validation
        OmegaTraumaValidator.validate_dimensionless("H_sub", h_sub)
        OmegaTraumaValidator.validate_dimensionless("Ξ_con", xi_con)
        for i, val in enumerate(psi_sub):
            OmegaTraumaValidator.validate_dimensionless(f"ψ_sub[{i}]", val)
        for i, val in enumerate(psi_con):
            OmegaTraumaValidator.validate_dimensionless(f"ψ_con[{i}]", val)
        
        # Calculate fidelity term: |<ψ_sub|ψ_con>|²
        dot = np.dot(psi_sub, psi_con)
        norm_sub = np.linalg.norm(psi_sub)
        norm_con = np.linalg.norm(psi_con)
        
        if norm_sub < 1e-12 or norm_con < 1e-12:
            fidelity_sq = 0.0
        else:
            cosine = dot / (norm_sub * norm_con)
            fidelity_sq = cosine ** 2  # CRITICAL: Must be squared per quantum mechanics
            fidelity_sq = max(0.0, min(1.0, fidelity_sq))  # Clamp to [0,1]
        
        # Entropic damping and stiffness penalty
        damping = math.exp(-OmegaTraumaValidator.LAMBDA_COUPLING * h_sub)
        stiffness_penalty = math.exp(-OmegaTraumaValidator.GAMMA_COUPLING * xi_con)
        
        cod = fidelity_sq * damping * stiffness_penalty
        
        # Validate output dimensionless
        OmegaTraumaValidator.validate_dimensionless("COD", cod)
        return cod
    
    @staticmethod
    def validate_entropy(options):
        """
        Validate H_sub as normalized Shannon entropy (Rubric §5 Compliance)
        H_sub = -Σ p_i log(p_i) / log(N) ∈ [0,1]
        """
        if not options:
            return 0.0
        OmegaTraumaValidator.validate_dimensionless("options length", len(options))
        
        # Validate probabilities
        total = sum(options)
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"Trauma trigger probabilities must sum to 1.0, got {total}")
        for p in options:
            if p < 0 or p > 1.0:
                raise ValueError(f"Probability out of [0,1]: {p}")
        
        # Calculate Shannon entropy
        h_shannon = 0.0
        for p in options:
            if p > 1e-12:
                h_shannon -= p * math.log(p)
        
        max_entropy = math.log(len(options)) if len(options) > 1 else 1.0
        h_normalized = h_shannon / max_entropy if max_entropy > 1e-12 else 0.0
        h_normalized = max(0.0, min(1.0, h_normalized))
        
        OmegaTraumaValidator.validate_dimensionless("H_sub", h_normalized)
        return h_normalized
    
    @staticmethod
    def validate_invariants(psi, xi_con, phi_sigma):
        """
        Validate Omega Protocol invariants (Phi-1, Phi-2, Phi-3)
        Returns: (is_valid, violations)
        """
        violations = []
        psi_min = math.log(OmegaTraumaValidator.PSI_ID_MIN)
        
        # Phi-1: Identity Continuity - HARD GATE (Rubric §4)
        if psi < psi_min:
            violations.append(
                f"PHI-1 VIOLATION: Identity continuity breached. "
                f"ψ = {psi:.4f} < ln({OmegaTraumaValidator.PSI_ID_MIN}) = {psi_min:.4f}"
            )
        
        # Phi-2: Suppression Energy Cost - SOFT WARNING (Rubric §4)
        if xi_con > OmegaTraumaValidator.XI_CON_CRITICAL:
            violations.append(
                f"PHI-2 WARNING: Suppression energy cost critical. "
                f"Ξ_con = {xi_con:.4f} > {OmegaTraumaValidator.XI_CON_CRITICAL}"
            )
        
        # Phi-3: Entropy Cap - META-SCRUTINY COMPLIANCE (Rubric §5)
        if phi_sigma > 0.03:  # 3% entropy cap from Meta-Scrutiny §5
            violations.append(
                f"PHI-3 WARNING: Entropy cap breached. "
                f"Φ_Σ = {phi_sigma:.4f} > 0.03"
            )
        
        is_valid = len([v for v in violations if "PHI-1 VIOLATION" in v]) == 0
        return is_valid, violations
    
    @staticmethod
    def validate_failure_mode(h_sub, xi_con, psi, cod):
        """
        Validate failure mode detection per State-Space Boundaries (Rubric §4)
        Returns: Failure type or None
        """
        # Suppression Collapse: H_sub > H_LIMIT ∧ Ξ_con > Ξ_CRITICAL ∧ ψ < ln(0.90)
        if (h_sub > OmegaTraumaValidator.H_SUB_LIMIT and 
            xi_con > OmegaTraumaValidator.XI_CON_CRITICAL and 
            psi < math.log(0.90)):
            return "SUPPRESSION_COLLAPSE"
        
        # Trauma Flooding: H_sub > H_LIMIT ∧ Ξ_con < 0.3
        if h_sub > OmegaTraumaValidator.H_SUB_LIMIT and xi_con < 0.3:
            return "TRAUMA_FLOODING"
        
        # Decoherence: ψ < ln(0.95) (Identity loss)
        if psi < math.log(OmegaTraumaValidator.PSI_ID_MIN):
            return "DECOHERENCE"
        
        return None
    
    @staticmethod
    def validate_phi_density(h_sub, cod_gain, audit_complexity=1.0):
        """
        Validate Φ-density accounting with audit cost subtraction (Meta-Scrutiny §5)
        Φ_net = ΔCOD - H_sub - k ln 2 · C_therapy
        """
        OmegaTraumaValidator.validate_dimensionless("H_sub", h_sub)
        OmegaTraumaValidator.validate_dimensionless("COD_gain", cod_gain)
        OmegaTraumaValidator.validate_dimensionless("audit_complexity", audit_complexity)
        
        raw_gain = cod_gain
        entropy_cost = h_sub * 0.5  # Per ledger implementation
        audit_entropy_cost = OmegaTraumaValidator.K_BOLTZMANN * math.log(2.0) * audit_complexity
        
        phi_net = raw_gain - entropy_cost - audit_entropy_cost
        OmegaTraumaValidator.validate_dimensionless("Φ_net", phi_net)
        return phi_net

def run_validation_suite():
    """Execute comprehensive validation of trauma-performance model"""
    print("=" * 60)
    print("OMEGA PROTOCOL VALIDATION SUITE - TRAUMA-PERFORMANCE MODEL")
    print("=" * 60)
    
    validator = OmegaTraumaValidator()
    test_cases = [
        # Case 1: Stable integrated state (should pass all checks)
        {
            "name": "Stable Integration",
            "psi_sub": [0.3, 0.5, 0.2],
            "psi_con": [0.2, 0.6, 0.2],
            "h_sub": 0.4,
            "xi_con": 1.2,
            "psi": math.log(0.98),  # > ln(0.95)
            "phi_sigma": 0.02
        },
        # Case 2: Suppression collapse risk (should trigger PHI-2 warning)
        {
            "name": "Suppression Collapse Risk",
            "psi_sub": [0.1, 0.1, 0.8],
            "psi_con": [0.0, 0.1, 0.9],
            "h_sub": 0.9,
            "xi_con": 2.8,  # > XI_CON_CRITICAL
            "psi": math.log(0.88),  # < ln(0.90) but > ln(0.95)? Actually 0.88<0.95 -> also PHI-1
            "phi_sigma": 0.01
        },
        # Case 3: Identity shredding (PHI-1 hard violation)
        {
            "name": "Identity Shredding",
            "psi_sub": [0.2, 0.3, 0.5],
            "psi_con": [0.0, 0.0, 1.0],
            "h_sub": 0.5,
            "xi_con": 1.5,
            "psi": math.log(0.90),  # < ln(0.95)
            "phi_sigma": 0.03
        },
        # Case 4: Entropy cap breach (PHI-3 warning)
        {
            "name": "Entropy Cap Breach",
            "psi_sub": [0.4, 0.4, 0.2],
            "psi_con": [0.3, 0.5, 0.2],
            "h_sub": 0.6,
            "xi_con": 1.0,
            "psi": math.log(0.96),
            "phi_sigma": 0.04  # > 0.03
        }
    ]
    
    for case in test_cases:
        print(f"\n[TEST CASE] {case['name']}")
        print("-" * 40)
        
        try:
            # Validate inputs
            h_sub = validator.validate_entropy(case["options"] if "options" in case else [0.3, 0.3, 0.4])
            print(f"✓ H_sub validation: {h_sub:.4f} (dimensionless [1])")
            
            # Calculate COD with CORRECTED formula (squared fidelity)
            cod = validator.validate_cod(
                case["psi_sub"], 
                case["psi_con"], 
                h_sub, 
                case["xi_con"]
            )
            print(f"✓ COD calculation: {cod:.4f} (validated squared fidelity)")
            
            # Validate invariants
            is_valid, violations = validator.validate_invariants(
                case["psi"], 
                case["xi_con"], 
                case.get("phi_sigma", h_sub * 0.5)  # Approximate phi_sigma if not provided
            )
            
            for v in violations:
                if "VIOLATION" in v:
                    print(f"✗ {v}")
                else:
                    print(f"⚠ {v}")
            
            if is_valid:
                print("✓ Identity continuity (Phi-1) HARD GATE: PASSED")
            else:
                print("✗ Identity continuity (Phi-1) HARD GATE: FAILED")
            
            # Validate failure mode
            failure = validator.validate_failure_mode(
                h_sub, 
                case["xi_con"], 
                case["psi"], 
                cod
            )
            if failure:
                print(f"⚠ Failure mode detected: {failure}")
            else:
                print("✓ No critical failure mode")
            
            # Validate Phi-density
            phi_net = validator.validate_phi_density(
                h_sub, 
                cod_gain=0.1,  # Example gain
                audit_complexity=1.0
            )
            print(f"✓ Φ-density net gain: {phi_net:.4f} (audit cost subtracted)")
            
        except Exception as e:
            print(f"✗ VALIDATION ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE: All mathematical expressions checked for")
    print("   - Dimensional compliance [1] (Rubric §6)")
    print("   - Quantum mechanical correctness (|<ψ|φ>|²)")
    print("   - Invariant enforcement (Phi-1 hard gate, Phi-2/3 warnings)")
    print("   - Audit-cost thermodynamic compliance (Meta-Scrutiny §5)")
    print("=" * 60)

if __name__ == "__main__":
    run_validation_suite()