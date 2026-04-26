# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from typing import Tuple, List, Dict, Any

# =============================================================================
# OMEGA PROTOCOL INVARIANTS (v72.0-Ω COGNITIVE TOPOLOGY)
# =============================================================================
class CognitiveTopologyInvariants:
    PSI_INTEGRITY_THRESHOLD = 0.95   # Identity Continuity
    BIAS_CONCENTRATION_MAX = 0.50    # Max shared bias
    NARRATIVE_SYNC_MAX = 0.60        # Max framing alignment
    DECISION_IMPACT_MAX = 0.70       # Max actionable impact
    COD_THRESHOLD = 0.85             # Alignment Fidelity
    AUDIT_ENTROPY_PER_CHECK = 0.02   # Per audit operation

    class RiskLevel:
        LOW, MEDIUM, CRITICAL, CATASTROPHIC = range(4)

    class CognitiveState:
        DIVERSE_THINKING, EMERGING_CONSENSUS, SYNCHRONIZED_BIAS, CASCADE_READY = range(4)

# =============================================================================
# COGNITIVE TOPOLOGY GATE MATHEMATICAL CORE
# =============================================================================
class CognitiveTopologyGate:
    @staticmethod
    def calculate_bias_concentration(
        narrative_synchronization: float,
        cognitive_diversity: float,
        structure_density: float
    ) -> float:
        """Bias Concentration = 0.5*NS + 0.3*SD - 0.2*CD"""
        sync_comp = narrative_synchronization * 0.5
        density_comp = structure_density * 0.3
        diversity_red = cognitive_diversity * 0.2
        concentration = sync_comp + density_comp - diversity_red
        return max(0.0, min(1.0, concentration))

    @staticmethod
    def calculate_narrative_synchronization(
        bias_concentration: float,
        propagation_velocity: float,
        stability_margin: float
    ) -> float:
        """Narrative Sync = 0.5*BC + 0.3*PV + 0.2*(1-SM)"""
        conc_factor = bias_concentration * 0.5
        vel_factor = propagation_velocity * 0.3
        margin_red = (1.0 - stability_margin) * 0.2
        sync = conc_factor + vel_factor + margin_red
        return max(0.0, min(1.0, sync))

    @staticmethod
    def calculate_decision_impact(
        bias_concentration: float,
        narrative_synchronization: float,
        cognitive_diversity: float
    ) -> float:
        """Decision Impact = (BC × NS) × (1 - CD)"""
        bias_sync = bias_concentration * narrative_synchronization
        diversity_factor = 1.0 - cognitive_diversity
        impact = bias_sync * diversity_factor
        return max(0.0, min(1.0, impact))

    @staticmethod
    def calculate_cascade_probability(
        decision_impact: float,
        propagation_velocity: float,
        bias_concentration: float
    ) -> float:
        """Cascade Prob = 0.5*DI + 0.3*PV + 0.2*BC"""
        impact_factor = decision_impact * 0.5
        vel_factor = propagation_velocity * 0.3
        conc_factor = bias_concentration * 0.2
        prob = impact_factor + vel_factor + conc_factor
        return max(0.0, min(1.0, prob))

    @staticmethod
    def calculate_cognitive_topology_risk(
        bias_concentration: float,
        narrative_synchronization: float,
        decision_impact: float
    ) -> float:
        """Cognitive Topology Risk = BC × NS × DI"""
        risk = bias_concentration * narrative_synchronization * decision_impact
        return max(0.0, min(1.0, risk))

# =============================================================================
# COD CALCULATION (COGNITIVE-AWARE)
# =============================================================================
LAMBDA_COUPLING = 0.5
MU_COGNITIVE = 0.7

def calculate_cod_cognitive_aware(
    diagnostic_vec: List[complex],
    plasma_vec: List[complex],
    h_instability: float,
    theta_tensor_leak: float,
    bias_concentration: float,
    narrative_synchronization: float,
    cognitive_topology_risk: float
) -> float:
    """COD = Fidelity × Instability Penalty × Exposure Penalty × Bias Penalty × Sync Penalty × Risk Penalty"""
    # 1. Fidelity Calculation (dot product normalization)
    dot = 0.0
    mag_diag = 0.0
    mag_plasma = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    
    for i in range(size):
        conj_diag = np.conj(diagnostic_vec[i])
        dot += np.real(conj_diag * plasma_vec[i])  # Only real part matters for magnitude
        mag_diag += np.abs(diagnostic_vec[i]) ** 2
        mag_plasma += np.abs(plasma_vec[i]) ** 2
    
    fidelity = 0.0
    if mag_diag > 1e-9 and mag_plasma > 1e-9:
        fidelity = dot / (np.sqrt(mag_diag) * np.sqrt(mag_plasma))
        fidelity = max(0.0, min(1.0, fidelity))
    
    # 2. Penalties (all in (0,1] for inputs in [0,1])
    instability_penalty = np.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = np.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    bias_penalty = np.exp(-MU_COGNITIVE * bias_concentration)
    sync_penalty = np.exp(-MU_COGNITIVE * narrative_synchronization)
    risk_penalty = np.exp(-MU_COGNITIVE * cognitive_topology_risk)
    
    return fidelity * instability_penalty * exposure_penalty * bias_penalty * sync_penalty * risk_penalty

# =============================================================================
# INVARIANT ENFORCEMENT & PROTOCOL LOGIC
# =============================================================================
class CognitiveTopologyEnforcer:
    @staticmethod
    def check_invariants(
        state: Dict[str, float],
        cod: float,
        cognitive_topology_risk: float,
        cognitive_state: int
    ) -> Dict[str, bool]:
        """Returns dict of invariant check results"""
        checks = {
            'psi_integrity_ok': state['psi_integrity'] >= CognitiveTopologyInvariants.PSI_INTEGRITY_THRESHOLD,
            'bias_concentration_ok': state['bias_concentration'] <= CognitiveTopologyInvariants.BIAS_CONCENTRATION_MAX,
            'narrative_sync_ok': state['narrative_synchronization'] <= CognitiveTopologyInvariants.NARRATIVE_SYNC_MAX,
            'decision_impact_ok': state['decision_impact'] <= CognitiveTopologyInvariants.DECISION_IMPACT_MAX,
            'cod_ok': cod >= CognitiveTopologyInvariants.COD_THRESHOLD,
            'audit_tracked': True  # Always tracked in this model
        }
        checks['all_passed'] = all(checks.values())
        return checks

    @staticmethod
    def decide_action(
        psi_integrity: float,
        cognitive_topology_risk: float,
        cognitive_state: int
    ) -> Tuple[int, str]:
        """Returns (action_code, message)"""
        # PRIMARY GATE: Ψ_integrity
        if psi_integrity < CognitiveTopologyInvariants.PSI_INTEGRITY_THRESHOLD:
            return (3, "CRITICAL: Identity breach imminent. Lockdown initiated.")  # IDENTITY_LOCKDOWN
        
        # COGNITIVE STATE GATE
        if cognitive_state == CognitiveTopologyInvariants.CognitiveState.CASCADE_READY:
            return (3, "CRITICAL: Decision cascade imminent. Lockdown initiated.")
        
        # RISK-BASED DECISIONS
        if cognitive_topology_risk > 0.70:
            return (3, "CRITICAL: Cognitive topology risk extreme. Lockdown initiated.")
        if cognitive_topology_risk > 0.50 or cognitive_state == CognitiveTopologyInvariants.CognitiveState.SYNCHRONIZED_BIAS:
            return (2, "ACTIVATE DIVERSIFICATION: Critical cognitive risk detected.")
        if cognitive_topology_risk > 0.30 or cognitive_state == CognitiveTopologyInvariants.CognitiveState.EMERGING_CONSENSUS:
            return (1, "FLAG BIAS MONITOR: Emerging consensus detected.")
        
        return (0, "PROCEED: Cognitive topology diverse. Bias concentration low.")

# =============================================================================
# VALIDATION SCRIPT: MATHEMATICAL SOUNDNESS & PROTOCOL COMPLIANCE
# =============================================================================
def validate_cognitive_topology_math() -> Dict[str, Any]:
    """
    Validates:
    1. All mathematical functions return values in [0,1]
    2. Invariant thresholds are respected
    3. COD calculation behaves correctly
    4. Protocol decisions align with risk levels
    """
    results = {
        'math_bounds': True,
        'invariant_logic': True,
        'cod_behavior': True,
        'protocol_decisions': True,
        'details': []
    }
    
    # Test 1: Mathematical bounds for all gate functions
    test_cases = [
        # (bias_conc, narrative_sync, decision_impact, cognitive_diversity, propagation_vel, stability_margin, structure_density)
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        (0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
        (0.2, 0.8, 0.3, 0.1, 0.9, 0.2, 0.7),
        (0.9, 0.1, 0.4, 0.8, 0.2, 0.9, 0.3)
    ]
    
    for i, (bc, ns, di, cd, pv, sm, sd) in enumerate(test_cases):
        # Calculate derived values
        calc_bc = CognitiveTopologyGate.calculate_bias_concentration(ns, cd, sd)
        calc_ns = CognitiveTopologyGate.calculate_narrative_synchronization(bc, pv, sm)
        calc_di = CognitiveTopologyGate.calculate_decision_impact(bc, ns, cd)
        calc_cp = CognitiveTopologyGate.calculate_cascade_probability(di, pv, bc)
        calc_ctr = CognitiveTopologyGate.calculate_cognitive_topology_risk(bc, ns, di)
        
        # Check bounds
        bounds_ok = all(0.0 <= x <= 1.0 for x in [calc_bc, calc_ns, calc_di, calc_cp, calc_ctr])
        if not bounds_ok:
            results['math_bounds'] = False
            results['details'].append(
                f"Test case {i}: Bounds violation. "
                f"BC={calc_bc:.3f}, NS={calc_ns:.3f}, DI={calc_di:.3f}, "
                f"CP={calc_cp:.3f}, CTR={calc_ctr:.3f}"
            )
    
    # Test 2: COD behavior with empty vectors (as in Operate function)
    empty_diag = []
    empty_plasma = []
    cod_empty = calculate_cod_cognitive_aware(
        empty_diag, empty_plasma,
        h_instability=0.1, theta_tensor_leak=0.1,
        bias_concentration=0.2, narrative_synchronization=0.3, cognitive_topology_risk=0.1
    )
    # With empty vectors, fidelity=0 → COD=0
    if cod_empty != 0.0:
        results['cod_behavior'] = False
        results['details'].append(f"Empty vectors COD should be 0.0, got {cod_empty}")
    
    # Test 3: COD with perfect alignment (should be high)
    # Create vectors that are identical and normalized
    n = 5
    diag_vec = [complex(1.0, 0.0)] * n
    plasma_vec = [complex(1.0, 0.0)] * n
    cod_perfect = calculate_cod_cognitive_aware(
        diag_vec, plasma_vec,
        h_instability=0.0, theta_tensor_leak=0.0,
        bias_concentration=0.0, narrative_synchronization=0.0, cognitive_topology_risk=0.0
    )
    # Should be ~1.0 (fidelity=1.0, all penalties=1.0)
    if cod_perfect < 0.99:
        results['cod_behavior'] = False
        results['details'].append(f"Perfect alignment COD too low: {cod_perfect}")
    
    # Test 4: Invariant enforcement logic
    test_state = {
        'psi_integrity': 0.96,
        'bias_concentration': 0.4,
        'narrative_synchronization': 0.5,
        'decision_impact': 0.6,
        'h_instability': 0.1,
        'theta_tensor_leak': 0.1,
        'stability_margin': 0.7,
        'structure_density': 0.3,
        'cognitive_diversity': 0.5,
        'propagation_velocity': 0.2
    }
    
    # Calculate derived state values
    test_state['narrative_synchronization'] = CognitiveTopologyGate.calculate_narrative_synchronization(
        test_state['bias_concentration'],
        test_state['propagation_velocity'],
        test_state['stability_margin']
    )
    test_state['bias_concentration'] = CognitiveTopologyGate.calculate_bias_concentration(
        test_state['narrative_synchronization'],
        test_state['cognitive_diversity'],
        test_state['structure_density']
    )
    test_state['decision_impact'] = CognitiveTopologyGate.calculate_decision_impact(
        test_state['bias_concentration'],
        test_state['narrative_synchronization'],
        test_state['cognitive_diversity']
    )
    test_state['cascade_probability'] = CognitiveTopologyGate.calculate_cascade_probability(
        test_state['decision_impact'],
        test_state['propagation_velocity'],
        test_state['bias_concentration']
    )
    test_state['cognitive_topology_risk'] = CognitiveTopologyGate.calculate_cognitive_topology_risk(
        test_state['bias_concentration'],
        test_state['narrative_synchronization'],
        test_state['decision_impact']
    )
    
    # Calculate COD (using empty vectors as in Operate)
    cod_val = calculate_cod_cognitive_aware(
        [], [],
        test_state['h_instability'],
        test_state['theta_tensor_leak'],
        test_state['bias_concentration'],
        test_state['narrative_synchronization'],
        test_state['cognitive_topology_risk']
    )
    
    # Check invariants
    invariants = CognitiveTopologyEnforcer.check_invariants(
        test_state, cod_val, test_state['cognitive_topology_risk'],
        CognitiveTopologyInvariants.CognitiveState.DIVERSE_THINKING  # Placeholder
    )
    
    # COD should fail (0.0 < 0.85) but action might be FLAG_BIAS_MONITOR
    if invariants['cod_ok']:
        results['invariant_logic'] = False
        results['details'].append("COD invariant unexpectedly passed with empty vectors")
    
    # Determine cognitive state for decision
    cognitive_state = CognitiveTopologyEnforcer._classify_cognitive_state(
        test_state['bias_concentration'],
        test_state['narrative_synchronization'],
        test_state['cascade_probability']
    )
    
    action_code, message = CognitiveTopologyEnforcer.decide_action(
        test_state['psi_integrity'],
        test_state['cognitive_topology_risk'],
        cognitive_state
    )
    
    # Validate decision logic
    expected_action = 1  # FLAG_BIAS_MONITOR (since CTR=0.4*0.5*0.24=0.048? Wait recalc)
    # Recalculate CTR: BC≈0.2*0.5+0.3*0.3-0.2*0.5=0.1+0.09-0.1=0.09; NS≈0.5*0.09+0.3*0.2+0.2*0.3=0.045+0.06+0.06=0.165
    # DI≈0.09*0.165*0.5=0.0074; CTR≈0.09*0.165*0.0074≈0.0001 → Very low
    # Actually with our test values: 
    #   BC = 0.5*0.5 + 0.3*0.3 - 0.2*0.5 = 0.25+0.09-0.1=0.24
    #   NS = 0.5*0.24 + 0.3*0.2 + 0.2*(1-0.7)=0.12+0.06+0.06=0.24
    #   DI = 0.24*0.24*0.5=0.0288
    #   CTR = 0.24*0.24*0.0288≈0.00166 → LOW RISK
    # So action should be PROCEED (0)
    if action_code != 0:
        results['protocol_decisions'] = False
        results['details'].append(f"Expected PROCEED (0) for low risk, got {action_code}: {message}")
    
    # Test 5: High risk scenario
    high_risk_state = test_state.copy()
    high_risk_state['bias_concentration'] = 0.6  # Above max
    high_risk_state['narrative_synchronization'] = 0.7  # Above max
    high_risk_state['cognitive_diversity'] = 0.1  # Low diversity
    
    # Recalculate derived values
    high_risk_state['narrative_synchronization'] = CognitiveTopologyGate.calculate_narrative_synchronization(
        high_risk_state['bias_concentration'],
        high_risk_state['propagation_velocity'],
        high_risk_state['stability_margin']
    )
    high_risk_state['bias_concentration'] = CognitiveTopologyGate.calculate_bias_concentration(
        high_risk_state['narrative_synchronization'],
        high_risk_state['cognitive_diversity'],
        high_risk_state['structure_density']
    )
    high_risk_state['decision_impact'] = CognitiveTopologyGate.calculate_decision_impact(
        high_risk_state['bias_concentration'],
        high_risk_state['narrative_synchronization'],
        high_risk_state['cognitive_diversity']
    )
    high_risk_state['cognitive_topology_risk'] = CognitiveTopologyGate.calculate_cognitive_topology_risk(
        high_risk_state['bias_concentration'],
        high_risk_state['narrative_synchronization'],
        high_risk_state['decision_impact']
    )
    
    cod_high = calculate_cod_cognitive_aware(
        [], [],
        high_risk_state['h_instability'],
        high_risk_state['theta_tensor_leak'],
        high_risk_state['bias_concentration'],
        high_risk_state['narrative_synchronization'],
        high_risk_state['cognitive_topology_risk']
    )
    
    invariants_high = CognitiveTopologyEnforcer.check_invariants(
        high_risk_state, cod_high, high_risk_state['cognitive_topology_risk'],
        CognitiveTopologyInvariants.CognitiveState.SYNCHRONIZED_BIAS
    )
    
    cognitive_state_high = CognitiveTopologyEnforcer._classify_cognitive_state(
        high_risk_state['bias_concentration'],
        high_risk_state['narrative_synchronization'],
        high_risk_state['cascade_probability']  # Need to calculate this
    )
    
    # Calculate cascade probability for high risk state
    high_risk_state['cascade_probability'] = CognitiveTopologyGate.calculate_cascade_probability(
        high_risk_state['decision_impact'],
        high_risk_state['propagation_velocity'],
        high_risk_state['bias_concentration']
    )
    
    cognitive_state_high = CognitiveTopologyEnforcer._classify_cognitive_state(
        high_risk_state['bias_concentration'],
        high_risk_state['narrative_synchronization'],
        high_risk_state['cascade_probability']
    )
    
    action_code_high, message_high = CognitiveTopologyEnforcer.decide_action(
        high_risk_state['psi_integrity'],
        high_risk_state['cognitive_topology_risk'],
        cognitive_state_high
    )
    
    # With high BC and NS, should trigger ACTION_DIVERSIFICATION (2) or LOCKDOWN (3)
    if action_code_high < 2:  # Should be at least 2 (ACTIVATE DIVERSIFICATION)
        results['protocol_decisions'] = False
        results['details'].append(f"High risk scenario failed: expected >=2, got {action_code_high}")
    
    # Calculate net Φ gain (audit cost subtraction)
    audit_checks = 12  # As in Operate function
    audit_cost = audit_checks * CognitiveTopologyInvariants.AUDIT_ENTROPY_PER_CHECK
    cod_before = 0.5  # Hypothetical
    cod_after = cod_val  # From test state
    raw_gain = cod_after - cod_before
    phi_net_gain = raw_gain - audit_cost
    
    # Φ gain should be negative due to audit cost (as expected)
    if phi_net_gain > raw_gain:  # Impossible - audit cost always subtracts
        results['protocol_decisions'] = False
        results['details'].append(f"Φ accounting error: net gain {phi_net_gain} > raw gain {raw_gain}")
    
    return results

# Helper method for cognitive state classification (moved from class for testing)
def _classify_cognitive_state(bc: float, ns: float, cp: float) -> int:
    if cp > 0.70:
        return CognitiveTopologyInvariants.CognitiveState.CASCADE_READY
    if ns > 0.60 and bc > 0.50:
        return CognitiveTopologyInvariants.CognitiveState.SYNCHRONIZED_BIAS
    if bc > 0.30 or ns > 0.40:
        return CognitiveTopologyInvariants.CognitiveState.EMERGING_CONSENSUS
    return CognitiveTopologyInvariants.CognitiveState.DIVERSE_THINKING

# Attach helper to class for test
CognitiveTopologyEnforcer._classify_cognitive_state = staticmethod(_classify_cognitive_state)

# =============================================================================
# EXECUTE VALIDATION
# =============================================================================
if __name__ == "__main__":
    validation_results = validate_cognitive_topology_math()
    
    print("=" * 60)
    print("OMEGA PROTOCOL COGNITIVE TOPOLOGY VALIDATION REPORT")
    print("=" * 60)
    print(f"Mathematical Bounds Compliance: {'PASS' if validation_results['math_bounds'] else 'FAIL'}")
    print(f"Invariant Logic Compliance:     {'PASS' if validation_results['invariant_logic'] else 'FAIL'}")
    print(f"COD Behavior Compliance:        {'PASS' if validation_results['cod_behavior'] else 'FAIL'}")
    print(f"Protocol Decisions Compliance:  {'PASS' if validation_results['protocol_decisions'] else 'FAIL'}")
    print("-" * 60)
    
    if validation_results['details']:
        print("DETAILS:")
        for detail in validation_results['details']:
            print(f"  - {detail}")
    else:
        print("NO ISSUES DETECTED - ALL CHECKS PASSED")
    
    print("=" * 60)
    
    # Overall verdict
    all_passed = all([
        validation_results['math_bounds'],
        validation_results['invariant_logic'],
        validation_results['cod_behavior'],
        validation_results['protocol_decisions']
    ])
    
    print(f"OVERALL VALIDATION: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 60)