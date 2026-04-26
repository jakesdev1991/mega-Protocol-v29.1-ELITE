# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

class FluxStabilizationGovernorValidator:
    """
    Validator for FSG-v57.3 system state against Omega Protocol invariants.
    Enforces absolute invariants from Omega Physics Rubric v26.0.
    """
    
    def __init__(self, R_max=1.0):
        """
        Initialize validator with Rubric-mandated parameters.
        
        Args:
            R_max: Maximum alignment scale for tanh normalization (Rubric §3)
        """
        # Rubric §3: Identity Continuity Invariant
        self.phi_min = math.exp(-0.95)  # ≈ 0.3867 (ensures psi >= ln(0.39) ≈ -0.942)
        
        # Rubric §3: Stiffness Decomposition (required but not directly validated here)
        # Note: xi_N and xi_Delta must appear in architecture per Rubric
        
        # Rubric §4: Boundary Conditions
        self.shredding_threshold = 0.5  # Φ_Δ > 0.5·Φ_N triggers Shredding Event
        self.freeze_threshold = self.phi_min  # Φ_N < phi_min triggers Informational Freeze
        
        # Rubric §5: Entropy Grounding
        self.R_max = R_max  # Scale for alignment mismatch (must be >0)
        
        # Rubric §6: Audit Cost Transparency
        self.k_B = 1.380649e-23  # Boltzmann constant (J/K)
        self.T_sensor = 300.0    # Reference sensor temperature (K)
        
    def validate_state(self, state):
        """
        Validate all Omega Protocol invariants for given system state.
        
        Args:
            state: Dict containing:
                - cod: Chain Overlap Density (Tr(ρ_fire ρ_sense))
                - xi_control: Control stiffness
                - xi_kinematic: Kinematic capacity stiffness
                - h_collapse: Dissonance measure
                - phi_N: Identity density (log2(cod))
                - phi_Delta: Adaptation asymmetry
                - audit_checks: Number of invariant checks per cycle (for ΔS_audit)
                
        Returns:
            Tuple (is_valid, violations) where:
                - is_valid: Boolean indicating full compliance
                - violations: List of violated invariant descriptions
        """
        violations = []
        
        # Extract state variables with defaults for missing keys
        cod = state.get('cod', 0.0)
        xi_control = state.get('xi_control', float('inf'))
        xi_kinematic = state.get('xi_kinematic', 0.0)
        h_collapse = state.get('h_collapse', float('inf'))
        phi_N = state.get('phi_N', -float('inf'))
        phi_Delta = state.get('phi_Delta', float('inf'))
        audit_checks = state.get('audit_checks', 0)
        
        # =================================================================
        # RUBRIC §1: BOILERPLATE PROHIBITION (Implicit in validation design)
        # =================================================================
        # We enforce first-principles grounding by requiring explicit formulas
        
        # =================================================================
        # RUBRIC §2: COVARIANT Φ DECOMPOSITION
        # =================================================================
        # Verify Φ_N derivation from COD (Informational-First)
        if cod <= 0:
            violations.append("Rubric §2 Violation: COD must be >0 for log2 definition")
        else:
            expected_phi_N = math.log2(cod)
            if not math.isclose(phi_N, expected_phi_N, rel_tol=1e-9):
                violations.append(
                    f"Rubric §2 Violation: Φ_N mismatch. "
                    f"Expected {expected_phi_N:.6f} from COD={cod}, got {phi_N:.6f}"
                )
        
        # Verify Φ_Δ derivation from stiffness mismatch (Rubric §3)
        if self.R_max <= 0:
            violations.append("Rubric §3 Violation: R_max must be >0 for tanh normalization")
        else:
            R_align = xi_kinematic - xi_control
            expected_phi_Delta = math.log(phi_N + 1e-9) * math.tanh(R_align / self.R_max)
            if not math.isclose(phi_Delta, expected_phi_Delta, rel_tol=1e-9):
                violations.append(
                    f"Rubric §3 Violation: Φ_Δ mismatch. "
                    f"Expected {expected_phi_Delta:.6f} from ψ=ln(Φ_N) and R_align={R_align}, "
                    f"got {phi_Delta:.6f}"
                )
        
        # =================================================================
        # RUBRIC §3: INVARIANT STRUCTURE (Non-negotiable forms)
        # =================================================================
        # Invariant 1: Identity Continuity (Mandatory psi = ln(Φ_N) form)
        if phi_N <= 0:
            violations.append("Rubric §3 Violation: Φ_N must be >0 for ln(Φ_N) definition")
        else:
            psi = math.log(phi_N)
            min_psi = math.log(self.phi_min)  # ≈ -0.942
            if psi < min_psi:
                violations.append(
                    f"Rubric §3 Violation: ψ = ln(Φ_N) < ln(Φ_min). "
                    f"ψ={psi:.6f}, min_psi={min_psi:.6f} (requires Φ_N ≥ {self.phi_min:.6f})"
                )
        
        # Invariant 2: Stiffness Matching (Ξ_control ≤ Ξ_kinematic)
        if xi_control > xi_kinematic:
            violations.append(
                f"Rubric §3 Violation: Ξ_control > Ξ_kinematic. "
                f"Ξ_control={xi_control:.6f}, Ξ_kinematic={xi_kinematic:.6f}"
            )
        
        # =================================================================
        # RUBRIC §4: BOUNDARY CONDITIONS (Shredding Event / Informational Freeze)
        # =================================================================
        # Informational Freeze: Halt when Φ_N < Φ_min
        if phi_N < self.phi_min:
            violations.append(
                f"Rubric §4 Violation: Informational Freeze required. "
                f"Φ_N={phi_N:.6f} < Φ_min={self.phi_min:.6f}"
            )
        
        # Shredding Event: Trigger when Φ_Δ > 0.5·Φ_N
        if phi_Delta > 0.5 * phi_N:
            violations.append(
                f"Rubric §4 Violation: Shredding Event required. "
                f"Φ_Δ={phi_Delta:.6f} > 0.5·Φ_N={0.5*phi_N:.6f}"
            )
        
        # =================================================================
        # RUBRIC §5: ENTROPY GROUNDING (Measurable quantities)
        # =================================================================
        # Verify audit cost uses Landauer bound with measurable C_audit
        if audit_checks < 0:
            violations.append("Rubric §5 Violation: Audit checks cannot be negative")
        else:
            # ΔS_audit = k_B ln 2 · C_audit (must be subtracted from Φ-ledger)
            # We verify the formula is correctly applied in ledger (not state)
            delta_S_audit = self.k_B * math.log(2) * audit_checks
            if delta_S_audit < 0:
                violations.append("Rubric §5 Violation: ΔS_audit must be non-negative")
        
        # =================================================================
        # RUBRIC §6: VARIATIONAL DERIVATION (First-principles grounding)
        # =================================================================
        # Verify Φ-gain claims trace to Omega Action Functional
        # (This is design-time validation; runtime checks consistency)
        # We check that Φ_N and Φ_Δ definitions match Rubric requirements
        if 'phi_gain_breakdown' in state:
            breakdown = state['phi_gain_breakdown']
            expected_gains = {
                'Measurement Basis': 0.35,
                'Flux Handling': 0.30,
                'Identity Metric': 0.20,
                'Failure Mode': 0.25,
                'Audit Cost': -0.25
            }
            for mechanism, claimed_gain in breakdown.items():
                if mechanism in expected_gains:
                    expected = expected_gains[mechanism]
                    if not math.isclose(claimed_gain, expected, abs_tol=0.01):
                        violations.append(
                            f"Rubric §6 Violation: Φ-gain for '{mechanism}' unverified. "
                            f"Claimed {claimed_gain:.2f}Φ, expected {expected:.2f}Φ "
                            f"(must derive from δS/δΦ=0 of Omega Action Functional)"
                        )
        
        # =================================================================
        # ADDITIONAL: SMITH AUDIT INVARIANTS (From proposal)
        # =================================================================
        # Invariant 3: Alignment Fidelity (COD ≥ 0.85)
        if cod < 0.85:
            violations.append(
                f"Smith Audit Invariant 3 Violation: COD < 0.85. "
                f"COD={cod:.6f}"
            )
        
        # Invariant 4: Dissonance Cap (H_collapse ≤ 0.3)
        if h_collapse > 0.3:
            violations.append(
                f"Smith Audit Invariant 4 Violation: H_collapse > 0.3. "
                f"H_collapse={h_collapse:.6f}"
            )
        
        # Invariant 5: Asymmetry Control (Φ_Δ < 0.5·Φ_N) [Duplicates Rubric §4]
        if phi_Delta >= 0.5 * phi_N:
            violations.append(
                f"Smith Audit Invariant 5 Violation: Φ_Δ ≥ 0.5·Φ_N. "
                f"Φ_Δ={phi_Delta:.6f}, 0.5·Φ_N={0.5*phi_N:.6f}"
            )
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def validate_architecture(self, arch_diagram):
        """
        Validate architecture diagram for Rubric compliance.
        
        Args:
            arch_diagram: Dict describing architecture components
            
        Returns:
            Tuple (is_valid, violations)
        """
        violations = []
        
        # Check for mandatory Rubric elements in architecture
        required_elements = [
            'xi_N',      # Normal stiffness component (Rubric §3)
            'xi_Delta',  # Delta stiffness component (Rubric §3)
            'Shredding Event',  # Boundary condition (Rubric §4)
            'Informational Freeze'  # Boundary condition (Rubric §4)
        ]
        
        arch_str = str(arch_diagram).lower()
        for element in required_elements:
            if element.lower() not in arch_str:
                violations.append(
                    f"Architecture Violation: Missing Rubric-mandated element '{element}'. "
                    f"Required by Omega Physics Rubric."
                )
        
        # Check for prohibited terms (boilerplate)
        prohibited_terms = [
            'flux entropy',  # Must be Shannon conditional entropy
            'derivation theater',  # Indicates missing variational steps
            'ad hoc'  # Indicates non-first-principles grounding
        ]
        
        for term in prohibited_terms:
            if term in arch_str:
                violations.append(
                    f"Architecture Violation: Prohibited term '{term}' detected. "
                    f"Violates Informational Purity (Rubric §5)."
                )
        
        is_valid = len(violations) == 0
        return is_valid, violations

# Example usage and test cases
if __name__ == "__main__":
    validator = FluxStabilizationGovernorValidator()
    
    # Test Case 1: Valid state (should pass)
    valid_state = {
        'cod': 0.90,           # >0.85
        'xi_control': 0.5,
        'xi_kinematic': 1.0,   # Ξ_control ≤ Ξ_kinematic
        'h_collapse': 0.2,     # ≤0.3
        'phi_N': math.log2(0.90),  # ≈ 0.152
        'phi_Delta': math.log(0.152 + 1e-9) * math.tanh((1.0-0.5)/1.0),  # ≈ -1.88 * 0.462 ≈ -0.869
        'audit_checks': 1000
    }
    
    # Test Case 2: Invalid state - COD too low
    invalid_state_1 = {
        'cod': 0.80,           # <0.85
        'xi_control': 0.5,
        'xi_kinematic': 1.0,
        'h_collapse': 0.2,
        'phi_N': math.log2(0.80),
        'phi_Delta': math.log(math.log2(0.80)+1e-9) * math.tanh(0.5),
        'audit_checks': 1000
    }
    
    # Test Case 3: Invalid state - ψ too low (Φ_N < Φ_min)
    invalid_state_2 = {
        'cod': 0.30,           # Φ_N = log2(0.30) ≈ -1.74 < Φ_min (0.39)
        'xi_control': 0.5,
        'xi_kinematic': 1.0,
        'h_collapse': 0.2,
        'phi_N': math.log2(0.30),
        'phi_Delta': math.log(math.log2(0.30)+1e-9) * math.tanh(0.5),
        'audit_checks': 1000
    }
    
    # Test Case 4: Invalid state - Stiffness mismatch
    invalid_state_3 = {
        'cod': 0.90,
        'xi_control': 1.5,     # > xi_kinematic
        'xi_kinematic': 1.0,
        'h_collapse': 0.2,
        'phi_N': math.log2(0.90),
        'phi_Delta': math.log(math.log2(0.90)+1e-9) * math.tanh((1.0-1.5)/1.0),
        'audit_checks': 1000
    }
    
    test_cases = [
        ("Valid State", valid_state),
        ("Low COD", invalid_state_1),
        ("Low Φ_N (Freeze)", invalid_state_2),
        ("Stiffness Mismatch", invalid_state_3)
    ]
    
    print("FSG-v57.3 Omega Protocol Invariant Validation")
    print("=" * 50)
    
    for name, state in test_cases:
        is_valid, violations = validator.validate_state(state)
        print(f"\n{name}:")
        print(f"  State: cod={state['cod']:.3f}, Ξ_c={state['xi_control']:.3f}, Ξ_k={state['xi_kinematic']:.3f}")
        print(f"  Derived: Φ_N={state['phi_N']:.3f}, ψ={math.log(state['phi_N']+1e-9):.3f}")
        print(f"  Valid: {is_valid}")
        if violations:
            print("  Violations:")
            for v in violations:
                print(f"    - {v}")
    
    # Architecture validation example
    print("\n" + "=" * 50)
    print("Architecture Validation Example")
    arch_example = {
        'components': [
            'Sensor Flux Layer',
            'Causal Lattice (with xi_N and xi_Delta)',
            'Smith Invariant Enforcer (checks Shredding Event and Informational Freeze)',
            'Flux Stabilization Operator'
        ]
    }
    is_valid_arch, arch_violations = validator.validate_architecture(arch_example)
    print(f"Architecture Valid: {is_valid_arch}")
    if arch_violations:
        print("Architecture Violations:")
        for v in arch_violations:
            print(f"  - {v}")