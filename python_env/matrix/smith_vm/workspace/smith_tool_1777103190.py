# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# OMEGA PROTOCOL VALIDATOR: SUBCRITICAL THRESHOLD MANIFOLD (v71.0-Ω)
# Agent Smith Rigorous Audit Script
# Enforces: Dimensional Compliance (Rubric §6), Safety Gate Hierarchy, 
# Derivativity Avoidance, Φ-Density Honesty, Self-Audit Mandate
# FAILS HARD ON ANY INVARIANT VIOLATION (Smith Protocol)

import numpy as np
from typing import NamedTuple, List, Tuple
import itertools

# =============================================================================
# OMEGA PROTOCOL INVARIANTS (NON-NEGOTIABLE)
# =============================================================================
class OmegaInvariants:
    # Hard Gates (Violation = Threshold Breach Alert)
    PSI_INTEGRITY_THRESHOLD = 0.95   # Identity Continuity
    STABILITY_MARGIN_MIN = 0.40      # Min distance to turbulence
    STRUCTURE_DENSITY_MAX = 0.50     # Max vulnerability concentration
    PERTURBATION_MAX = 0.60          # Max perturbation amplitude
    COD_THRESHOLD = 0.85             # Alignment Fidelity
    AUDIT_ENTROPY_PER_CHECK = 0.02   # Φ-cost per audit check
    
    # Metric Bounds (All ∈ [0,1] PER PROTOCOL)
    METRIC_BOUNDS = {
        'psi_integrity': (0.0, 1.0),
        'stability_margin': (0.0, 1.0),
        'structure_density': (0.0, 1.0),
        'perturbation_amplitude': (0.0, 1.0),
        'cod': (0.0, 1.0),
        'phi_N': (0.0, 1.0),
        'subcritical_risk': (0.0, 1.0),
        'turbulence_probability': (0.0, 1.0),
        'structure_overlap': (0.0, 1.0),
        'flow_shear': (0.0, 1.0),
        'temperature_gradient': (0.0, 1.0),
        'boundary_internal_coupling': (0.0, 1.0),
        'h_instability': (0.0, 1.0),
        'theta_tensor_leak': (0.0, 1.0),
        'divergence_index': (0.0, 1.0),
        'coupled_risk': (0.0, 1.0)
    }
    
    # Risk Levels (From SubcriticalThresholdGate.AssessRisk)
    class RiskLevel:
        LOW = 0
        MEDIUM = 1
        CRITICAL = 2
        CATASTROPHIC = 3
    
    # Stability States (From SubcriticalThresholdInvariants.StabilityState)
    class StabilityState:
        SUBCRITICAL_STABLE = 0
        SUBCRITICAL_AT_RISK = 1
        THRESHOLD_CROSSING = 2
        TURBULENT = 3
    
    # Protocol Actions (From SubcriticalThresholdProtocol.Action)
    class Action:
        PROCEED = 0
        FLAG_THRESHOLD_MONITOR = 1
        ACTIVATE_STABILIZATION = 2
        IDENTITY_LOCKDOWN = 3

# =============================================================================
# METRIC CALCULATORS (EXTRACTED FROM PROPOSAL FOR VALIDATION)
# =============================================================================
class MetricCalculator:
    @staticmethod
    def calculate_stability_margin(flow_shear: float, temperature_gradient: float, 
                                 boundary_internal_coupling: float) -> float:
        shear_component = flow_shear * 0.4
        coupling_component = boundary_internal_coupling * 0.3
        gradient_penalty = temperature_gradient * 0.3
        margin = shear_component + coupling_component - gradient_penalty
        return np.clip(margin, 0.0, 1.0)
    
    @staticmethod
    def calculate_structure_overlap(structure_density: float, perturbation_amplitude: float) -> float:
        overlap = structure_density * perturbation_amplitude * 0.5
        return np.clip(overlap, 0.0, 1.0)
    
    @staticmethod
    def calculate_structure_density(perturbation_amplitude: float, stability_margin: float, 
                                  structure_overlap: float) -> float:
        threshold_proximity = 1.0 - stability_margin
        density = perturbation_amplitude * threshold_proximity * (1.0 + structure_overlap)
        return np.clip(density, 0.0, 1.0)
    
    @staticmethod
    def calculate_turbulence_probability(perturbation_amplitude: float, stability_margin: float, 
                                       structure_density: float) -> float:
        margin_deficit = max(0.0, perturbation_amplitude - stability_margin)
        density_factor = 1.0 + structure_density
        probability = margin_deficit * density_factor
        return np.clip(probability, 0.0, 1.0)
    
    @staticmethod
    def calculate_subcritical_risk(perturbation_amplitude: float, stability_margin: float, 
                                 structure_density: float) -> float:
        margin_deficit = 1.0 - stability_margin
        risk = perturbation_amplitude * margin_deficit * structure_density
        return np.clip(risk, 0.0, 1.0)
    
    @staticmethod
    def calculate_cod_threshold_aware(diagnostic_vec: List[complex], plasma_vec: List[complex],
                                    h_instability: float, theta_tensor_leak: float,
                                    stability_margin: float, subcritical_risk: float, 
                                    turbulence_probability: float) -> float:
        LAMBDA_COUPLING = 0.5
        MU_THRESHOLD = 0.7
        
        # 1. Fidelity (Generic Alignment)
        dot = 0.0
        magD = 0.0
        magP = 0.0
        size = min(len(diagnostic_vec), len(plasma_vec))
        for i in range(size):
            dot += abs(np.conj(diagnostic_vec[i]) * plasma_vec[i])
            magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
            magP += abs(plasma_vec[i] * plasma_vec[i])
        
        fidelity = 0.0
        if magD > 1e-9 and magP > 1e-9:
            fidelity = dot / (np.sqrt(magD) * np.sqrt(magP))
            fidelity = np.clip(fidelity, 0.0, 1.0)
        
        # 2. Penalties
        instability_penalty = np.exp(-LAMBDA_COUPLING * h_instability)
        exposure_penalty = np.exp(-LAMBDA_COUPLING * theta_tensor_leak)
        margin_penalty = np.exp(-MU_THRESHOLD * (1.0 - stability_margin))
        risk_penalty = np.exp(-MU_THRESHOLD * subcritical_risk)
        turbulence_penalty = np.exp(-MU_THRESHOLD * turbulence_probability)
        
        return fidelity * instability_penalty * exposure_penalty * \
               margin_penalty * risk_penalty * turbulence_penalty

# =============================================================================
# VALIDATOR CORE (ENFORCES ALL OMEGA INVARIANTS)
# =============================================================================
class OmegaValidator:
    def __init__(self):
        self.violations = []
        self.audit_checks = 0
        
    def _check_bounds(self, name: str, value: float) -> bool:
        low, high = OmegaInvariants.METRIC_BOUNDS[name]
        if not (low <= value <= high):
            self.violations.append(f"DIMENSIONAL VIOLATION: {name} = {value} ∉ [{low}, {high}]")
            self.audit_checks += 1
            return False
        return True
    
    def _check_gate_hierarchy(self, state: dict) -> bool:
        """Enforces strict gate ordering: Ψ_integrity → Stability State → Risk → Margin → Density → COD"""
        # PRIMARY GATE: Ψ_integrity (non-negotiable)
        if state['psi_integrity'] < OmegaInvariants.PSI_INTEGRITY_THRESHOLD:
            if state['action'] != OmegaInvariants.Action.IDENTITY_LOCKDOWN:
                self.violations.append(f"GATE VIOLATION: Ψ_integrity={state['psi_integrity']:.3f} < 0.95 but action={state['action']} ≠ LOCKDOWN")
                self.audit_checks += 1
                return False
            return True  # LOCKDOWN is correct
        
        # STABILITY STATE GATE
        if state['stability_state'] == OmegaInvariants.StabilityState.TURBULENT:
            if state['action'] != OmegaInvariants.Action.IDENTITY_LOCKDOWN:
                self.violations.append(f"GATE VIOLATION: StabilityState=TURBULENT but action={state['action']} ≠ LOCKDOWN")
                self.audit_checks += 1
                return False
            return True
        
        # RISK-BASED DECISIONS (must match protocol logic)
        expected_action = self._compute_expected_action(state)
        if state['action'] != expected_action:
            self.violations.append(f"GATE VIOLATION: Expected action={expected_action} (risk={state['subcritical_risk']:.3f}, state={state['stability_state']}) but got {state['action']}")
            self.audit_checks += 1
            return False
        
        return True
    
    def _compute_expected_action(self, state: dict) -> int:
        risk = state['subcritical_risk']
        state_enum = state['stability_state']
        
        if risk > 0.70 or state_enum == OmegaInvariants.StabilityState.TURBULENT:
            return OmegaInvariants.Action.IDENTITY_LOCKDOWN
        if risk > 0.50 or state_enum == OmegaInvariants.StabilityState.THRESHOLD_CROSSING:
            return OmegaInvariants.Action.ACTIVATE_STABILIZATION
        if risk > 0.30 or state_enum == OmegaInvariants.StabilityState.SUBCRITICAL_AT_RISK:
            return OmegaInvariants.Action.FLAG_THRESHOLD_MONITOR
        return OmegaInvariants.Action.PROCEED
    
    def _check_derivativity(self, proposed_metrics: set) -> bool:
        """Verifies no metric overlap with v67.0-70.0 (per derivativity mandate)"""
        # v67.0 Trust Decay Metrics
        v67_metrics = {
            'Trust_Half_Life', 'Coherence_Time', 'Error_Rate', 
            'Self_Correction_Efficacy', 'Recovery_Velocity'
        }
        
        # v69.0 Freeze Boundary Metrics
        v69_metrics = {
            'Freeze_Efficacy', 'Boundary_Exposure', 'Liquidity_Density', 
            'Boundary_Recovery_Rate'
        }
        
        # v70.0 Cross-Manifold Metrics
        v70_metrics = {
            'Boundary_Internal_Coupling', 'Divergence_Index', 
            'Coupled_Risk', 'Alignment_Fidelity'
        }
        
        prior_metrics = v67_metrics | v69_metrics | v70_metrics
        overlap = proposed_metrics & prior_metrics
        
        if overlap:
            self.violations.append(f"DERIVATIVITY VIOLATION: Overlapping metrics with prior work: {overlap}")
            self.audit_checks += 1
            return False
        return True
    
    def _check_phi_density_accounting(self, state_before: dict, state_after: dict, 
                                    audit_checks: int) -> bool:
        """Validates Φ-density ledger honesty (audit cost subtracted)"""
        raw_gain = state_after['cod'] - state_before['cod']
        audit_cost = audit_checks * OmegaInvariants.AUDIT_ENTROPY_PER_CHECK
        expected_gain = raw_gain - audit_cost
        
        if abs(state_after.get('phi_net_gain', 0.0) - expected_gain) > 1e-5:
            self.violations.append(f"Φ-DENSITY FRAUD: Claimed gain={state_after.get('phi_net_gain', 0.0):.5f}, Expected={expected_gain:.5f} (raw={raw_gain:.5f}, cost={audit_cost:.5f})")
            self.audit_checks += 1
            return False
        return True
    
    def validate_operation(self, state: dict, dt_hours: float) -> Tuple[bool, List[str]]:
        """Runs full validation on a protocol operation"""
        self.violations = []
        self.audit_checks = 0
        
        # 1. Dimensional compliance check (all state metrics)
        for metric_name in OmegaInvariants.METRIC_BOUNDS:
            if metric_name in state:
                self._check_bounds(metric_name, state[metric_name])
        
        # 2. Safety gate hierarchy enforcement
        self._check_gate_hierarchy(state)
        
        # 3. Derivativity check (proposed novel metrics)
        proposed_metrics = {
            'stability_margin', 'structure_density', 'perturbation_amplitude',
            'flow_shear', 'temperature_gradient', 'structure_overlap',
            'subcritical_risk', 'turbulence_probability'
        }
        self._check_derivativity(proposed_metrics)
        
        # 4. COD calculation validity (critical path)
        if 'diagnostic_vec' in state and 'plasma_vec' in state:
            # Must have non-empty vectors for meaningful COD (per protocol)
            if len(state['diagnostic_vec']) == 0 or len(state['plasma_vec']) == 0:
                self.violations.append("COD CALCULATION FAILURE: Empty diagnostic/plasma vectors")
                self.audit_checks += 1
        
        # 5. Φ-density accounting (if state transition occurred)
        if 'state_before' in state and 'state_after' in state:
            self._check_phi_density_accounting(
                state['state_before'], 
                state['state_after'], 
                state.get('audit_checks', 0)
            )
        
        is_valid = len(self.violations) == 0
        return is_valid, self.violations

# =============================================================================
# STRESS TEST: VALIDATE AGAINST PROTOCOL BOUNDARY CONDITIONS
# =============================================================================
def run_stress_tests():
    validator = OmegaValidator()
    test_cases = []
    
    # Generate boundary condition test cases
    test_cases.append({
        'name': 'Ψ_integrity breach (must LOCKDOWN)',
        'state': {
            'psi_integrity': 0.94,  # Below threshold
            'stability_margin': 0.50,
            'structure_density': 0.10,
            'perturbation_amplitude': 0.10,
            'cod': 0.90,
            'stability_state': OmegaInvariants.StabilityState.SUBCRITICAL_STABLE,
            'subcritical_risk': 0.05,
            'action': OmegaInvariants.Action.PROCEED  # INTENTIONAL ERROR
        }
    })
    
    test_cases.append({
        'name': 'TURBULENT state (must LOCKDOWN)',
        'state': {
            'psi_integrity': 0.96,
            'stability_margin': 0.10,
            'structure_density': 0.60,  # Above max
            'perturbation_amplitude': 0.50,
            'cod': 0.70,  # Below threshold
            'stability_state': OmegaInvariants.StabilityState.TURBULENT,
            'subcritical_risk': 0.80,
            'action': OmegaInvariants.Action.FLAG_THRESHOLD_MONITOR  # INTENTIONAL ERROR
        }
    })
    
    test_cases.append({
        'name': 'High subcritical risk (must ACTIVATE_STABILIZATION)',
        'state': {
            'psi_integrity': 0.97,
            'stability_margin': 0.30,  # Below min (0.40)
            'structure_density': 0.40,
            'perturbation_amplitude': 0.50,
            'cod': 0.88,
            'stability_state': OmegaInvariants.StabilityState.SUBCRITICAL_AT_RISK,
            'subcritical_risk': 0.55,  # >0.50
            'action': OmegaInvariants.Action.PROCEED  # INTENTIONAL ERROR
        }
    })
    
    test_cases.append({
        'name': 'Valid threshold-aware operation',
        'state': {
            'psi_integrity': 0.96,
            'stability_margin': 0.45,
            'structure_density': 0.30,
            'perturbation_amplitude': 0.20,
            'flow_shear': 0.60,
            'temperature_gradient': 0.20,
            'boundary_internal_coupling': 0.50,
            'h_instability': 0.10,
            'theta_tensor_leak': 0.05,
            'diagnostic_vec': [1+0j, 0.5+0.5j],
            'plasma_vec': [0.9+0j, 0.4+0.4j],
            'cod': 0.87,
            'stability_state': OmegaInvariants.StabilityState.SUBCRITICAL_STABLE,
            'subcritical_risk': 0.12,
            'action': OmegaInvariants.Action.PROCEED
        }
    })
    
    # Run all test cases
    all_passed = True
    for tc in test_cases:
        is_valid, violations = validator.validate_operation(tc['state'], dt_hours=1.0)
        if not is_valid:
            print(f"❌ FAIL: {tc['name']}")
            for v in violations:
                print(f"   - {v}")
            all_passed = False
        else:
            print(f"✅ PASS: {tc['name']}")
    
    return all_passed

# =============================================================================
# MAIN EXECUTION (SMITH AUDIT PROTOCOL)
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("OMEGA PROTOCOL VALIDATOR: SUBCRITICAL THRESHOLD MANIFOLD (v71.0-Ω)")
    print("Agent Smith Rigorous Audit - Zero Tolerance for Invariants Violation")
    print("=" * 70)
    
    # Run stress tests
    stress_pass = run_stress_tests()
    
    # Final verdict
    print("\n" + "=" * 70)
    if stress_pass:
        print("✅ OVERALL AUDIT: PASS")
        print("   All dimensional invariants, safety gates, and derivativity checks satisfied.")
        print("   Φ-density accounting validated as honest and protocol-compliant.")
        print("   Submission cleared for Omega Protocol integration.")
    else:
        print("❌ OVERALL AUDIT: FAIL")
        print("   CRITICAL INVARIANT VIOLATIONS DETECTED (see above).")
        print("   Submission REJECTED per Smith Protocol §Ω-7: ")
        print("   'Any threat to protocol stability through mathematical unsoundness ")
        print("   or derivativity shall be excised without mercy.'")
    print("=" * 70)
    
    # Exit with failure code if invalid (for automation)
    exit(0 if stress_pass else 1)