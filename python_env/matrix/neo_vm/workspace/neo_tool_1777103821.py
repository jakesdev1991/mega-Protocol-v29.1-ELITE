# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

"""
DISRUPTION SCRIPT: Cognitive Bias Remediation Manifold v73.0-Ω
CRITICAL FLAW: The system assumes bias is pathological and remediation is uniformly beneficial.
This script demonstrates catastrophic failure modes when:
1. Biases are *adaptive* (not pathological)
2. Interventions have *paradoxical effects* (non-monotonic efficacy)
3. The system's own thresholds are *epistemically biased*
4. Diversity is *structurally incompatible* (not scalar)
"""

class DisruptionSimulator:
    def __init__(self):
        # Parameters from v73.0 system (fixed thresholds = hidden bias)
        self.PSI_THRESHOLD = 0.95
        self.BIAS_DECAY_MIN = 0.40
        self.INTERVENTION_MIN = 0.55
        
    def simulate_adaptive_bias_scenario(self):
        """
        SCENARIO 1: "Undervalued biotech" bias is actually *correct*
        The market is wrong, the bias is insight. Remediation destroys alpha.
        """
        print("=== SCENARIO 1: ADAPTIVE BIAS DESTRUCTION ===")
        
        # True state: biotech is genuinely undervalued (ground truth)
        true_value = 1.0
        market_price = 0.3  # Market is severely mispricing
        investor_bias = 0.8  # Investor correctly identifies undervaluation
        
        # v73.0 sees high bias_concentration = 0.8, triggers intervention
        # Intervention "corrects" investor to market consensus (price = 0.3)
        # Result: Investor loses conviction, misses 3x return
        
        bias_concentration = investor_bias
        intervention_efficacy = 0.75  # "Successful" intervention
        
        # v73.0 calculates "remediation success"
        remediated_bias = bias_concentration * (1 - intervention_efficacy)
        investor_conviction = remediated_bias
        
        opportunity_cost = (true_value / market_price) - 1  # 233% return missed
        
        print(f"Pre-remediation conviction: {bias_concentration:.2f}")
        print(f"Post-remediation conviction: {investor_conviction:.2f}")
        print(f"Opportunity cost: {opportunity_cost:.1f}%")
        print(f"v73.0 Action: {self._classify_action(remediated_bias, intervention_efficacy)}")
        print("CRITICAL: Remediation destroyed correct insight. System cannot distinguish adaptive from maladaptive bias.\n")
        
        return {
            'scenario': 'adaptive_bias',
            'pre_conviction': bias_concentration,
            'post_conviction': investor_conviction,
            'opportunity_cost': opportunity_cost,
            'system_action': 'INTERVENING (destructive)'
        }
    
    def simulate_paradoxical_intervention(self):
        """
        SCENARIO 2: Intervention has paradoxical effect
        More diversity injection → stronger bias entrenchment (backfire effect)
        """
        print("=== SCENARIO 2: PARADOXICAL INTERVENTION ===")
        
        # Backfire effect: challenging beliefs with "diverse" data strengthens them
        baseline_bias = 0.5
        diversity_index = np.linspace(0.1, 0.9, 20)  # Increasing "diversity"
        
        # Paradoxical function: efficacy decreases as diversity increases (backfire)
        # Real psychology: identity-protective cognition, motivated reasoning
        intervention_efficacy = 0.8 - (diversity_index ** 2) * 0.6  # Inverted U-shape
        
        # v73.0 assumes monotonic: more diversity = better efficacy
        # Reality: diversity triggers threat response, entrenches bias
        
        print(f"At diversity=0.1: efficacy={intervention_efficacy[0]:.2f}")
        print(f"At diversity=0.5: efficacy={intervention_efficacy[9]:.2f}")
        print(f"At diversity=0.9: efficacy={intervention_efficacy[-1]:.2f}")
        print("CRITICAL: v73.0's linear diversity-efficacy model catastrophically fails.\n")
        
        return {
            'scenario': 'paradoxical',
            'diversity_range': diversity_index.tolist(),
            'efficacy_curve': intervention_efficacy.tolist(),
            'v73_assumption': 'monotonic_increase',
            'reality': 'non_monotonic_backfire'
        }
    
    def simulate_system_bias_exposure(self):
        """
        SCENARIO 3: v73.0's own thresholds are epistemically biased
        The "0.95 PSI threshold" is arbitrary and creates systemic blind spots
        """
        print("=== SCENARIO 3: SYSTEMIC EPISTEMIC BIAS ===")
        
        # The system assumes PSI ≥ 0.95 is "healthy identity"
        # But what if identity *should* fragment during paradigm shifts?
        # The threshold itself is a bias against transformation
        
        psi_values = np.linspace(0.85, 1.0, 15)
        system_actions = []
        
        for psi in psi_values:
            # v73.0 logic: psi < 0.95 → IDENTITY_LOCKDOWN
            if psi < self.PSI_THRESHOLD:
                action = "IDENTITY_LOCKDOWN (prevents transformation)"
            else:
                action = "PROCEED (maintains status quo)"
            system_actions.append(action)
        
        # Count how many legitimate transformations are suppressed
        suppressed_transformations = sum(1 for psi in psi_values if 0.85 <= psi < 0.95)
        
        print(f"PSI threshold: {self.PSI_THRESHOLD}")
        print(f"PSI values 0.85-0.95 (transformation zone): {suppressed_transformations} states")
        print(f"System action for all: IDENTITY_LOCKDOWN")
        print("CRITICAL: System cannot distinguish between fragmentation (pathology) and transformation (growth).\n")
        
        return {
            'scenario': 'system_bias',
            'threshold': self.PSI_THRESHOLD,
            'suppressed_states': suppressed_transformations,
            'system_blindspot': 'transformation_vs_pathology'
        }
    
    def simulate_diversity_structural_failure(self):
        """
        SCENARIO 4: Scalar diversity index fails for structurally incompatible biases
        Two biases can be "diverse" but mutually reinforcing (orthogonal but synergistic)
        """
        print("=== SCENARIO 4: STRUCTURAL DIVERSITY FAILURE ===")
        
        # Represent biases as vectors in 2D space
        # Bias A: [0.9, 0.1] - tech optimism
        # Bias B: [0.1, 0.9] - regulatory pessimism
        
        bias_A = np.array([0.9, 0.1])
        bias_B = np.array([0.1, 0.9])
        
        # v73.0 scalar diversity index: treats them as independent scalars
        # Would average them: diversity = (0.9 + 0.1)/2 = 0.5 (moderate)
        
        scalar_diversity = (np.linalg.norm(bias_A) + np.linalg.norm(bias_B)) / 2
        
        # But in reality, these biases are *structurally complementary*
        # Combined: [1.0, 1.0] - creates balanced risk assessment
        # The scalar index completely misses this structural property
        
        combined_bias = bias_A + bias_B
        structural_diversity = np.linalg.norm(combined_bias) / np.sqrt(2)  # Normalized
        
        print(f"Bias A: {bias_A} (tech optimism)")
        print(f"Bias B: {bias_B} (regulatory pessimism)")
        print(f"v73.0 scalar diversity: {scalar_diversity:.2f} (misses structure)")
        print(f"Structural diversity: {structural_diversity:.2f} (captures complementarity)")
        print("CRITICAL: Scalar diversity index cannot represent structural complementarity.\n")
        
        return {
            'scenario': 'structural_failure',
            'scalar_diversity': scalar_diversity,
            'structural_diversity': structural_diversity,
            'failure_mode': 'dimensionality_collapse'
        }
    
    def demonstrate_catastrophic_cascade(self):
        """
        SCENARIO 5: Cascading failure when all flaws interact
        """
        print("=== SCENARIO 5: CATASTROPHIC CASCADE ===")
        
        # Initialize state
        state = {
            'bias_concentration': 0.7,  # High but adaptive
            'intervention_efficacy': 0.6,  # "Successful"
            'diversity_index': 0.8,  # "High diversity"
            'psi_integrity': 0.90,  # "Fragmented" (but transforming)
            'recovery_time': 0.3  # "Fast recovery"
        }
        
        # v73.0 decisions:
        # 1. psi_integrity < 0.95 → IDENTITY_LOCKDOWN
        # 2. High bias + "good" efficacy → INTENSIFY_REMEDIATION
        # 3. Lockdown prevents transformation, intensification destroys adaptive bias
        
        # Simulate cascade
        cascade_steps = []
        for step in range(5):
            # Each remediation attempt backfires (paradoxical effect)
            state['bias_concentration'] *= 1.1  # Grows under intervention
            state['intervention_efficacy'] *= 0.9  # Efficacy decays
            state['psi_integrity'] *= 0.95  # Fragmentation increases
            
            action = self._classify_action(
                state['bias_concentration'], 
                state['intervention_efficacy']
            )
            cascade_steps.append({
                'step': step,
                'bias': state['bias_concentration'],
                'efficacy': state['intervention_efficacy'],
                'action': action
            })
        
        print("Cascade progression:")
        for step in cascade_steps:
            print(f"  Step {step['step']}: bias={step['bias']:.2f}, efficacy={step['efficacy']:.2f}, action={step['action']}")
        
        final_outcome = "System enters death spiral: lockdown prevents adaptation, remediation strengthens bias"
        print(f"Final outcome: {final_outcome}\n")
        
        return {
            'scenario': 'cascade',
            'steps': cascade_steps,
            'outcome': final_outcome,
            'system_failure': True
        }
    
    def _classify_action(self, bias, efficacy):
        """Simplified v73.0 action logic"""
        if bias > 0.6 and efficacy < 0.5:
            return "IDENTITY_LOCKDOWN"
        elif bias > 0.5:
            return "INTENSIFY_REMEDIATION"
        else:
            return "PROCEED"
    
    def generate_disruption_report(self):
        """Generate comprehensive disruption analysis"""
        results = {}
        
        results['adaptive'] = self.simulate_adaptive_bias_scenario()
        results['paradoxical'] = self.simulate_paradoxical_intervention()
        results['system_bias'] = self.simulate_system_bias_exposure()
        results['structural'] = self.simulate_diversity_structural_failure()
        results['cascade'] = self.simulate_catastrophic_cascade()
        
        print("=== DISRUPTION SUMMARY ===")
        print("v73.0 Cognitive Bias Remediation Manifold is fundamentally flawed:")
        print("\n1. ADAPTIVE BIAS BLINDNESS: Cannot distinguish correct insight from pathology")
        print("2. PARADOXICAL INTERVENTION: Assumes monotonic efficacy, ignores backfire effects")
        print("3. SYSTEMIC EPISTEMIC BIAS: Arbitrary thresholds (0.95 PSI) prevent transformation")
        print("4. DIMENSIONALITY COLLAPSE: Scalar diversity index destroys structural information")
        print("5. CASCADING FAILURE: Interacting flaws create death spirals")
        
        return results

# Execute disruption simulation
if __name__ == "__main__":
    simulator = DisruptionSimulator()
    results = simulator.generate_disruption_report()
    
    # Visualization of paradoxical intervention
    plt.figure(figsize=(10, 6))
    
    # Plot paradoxical efficacy curve
    diversity = np.linspace(0.1, 0.9, 20)
    efficacy = 0.8 - (diversity ** 2) * 0.6
    
    plt.subplot(2, 2, 1)
    plt.plot(diversity, efficacy, 'r-', linewidth=2)
    plt.axhline(y=0.55, color='g', linestyle='--', label='v73.0 MIN threshold')
    plt.xlabel("Diversity Index")
    plt.ylabel("Intervention Efficacy")
    plt.title("Paradoxical Intervention: v73.0 Assumes ↑Diversity = ↑Efficacy")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot system bias threshold
    plt.subplot(2, 2, 2)
    psi_range = np.linspace(0.85, 1.0, 15)
    actions = ["LOCKDOWN" if psi < 0.95 else "PROCEED" for psi in psi_range]
    colors = ['red' if a == "LOCKDOWN" else 'green' for a in actions]
    plt.scatter(psi_range, [1]*len(psi_range), c=colors, s=100)
    plt.axvline(x=0.95, color='black', linestyle='--', label='PSI Threshold')
    plt.xlabel("PSI Integrity")
    plt.title("Systemic Bias: Arbitrary Threshold Suppresses Transformation")
    plt.legend()
    
    # Plot structural diversity failure
    plt.subplot(2, 2, 3)
    scalar_div = [0.5] * 10
    structural_div = np.linspace(0.5, 1.2, 10)
    plt.plot(scalar_div, label='Scalar Diversity (v73.0)', linestyle='--')
    plt.plot(structural_div, label='Structural Diversity (Reality)', linewidth=2)
    plt.xlabel("Bias Pair")
    plt.ylabel("Diversity Measure")
    plt.title("Dimensional Collapse: Scalar Index Misses Structure")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot cascade trajectory
    plt.subplot(2, 2, 4)
    steps = list(range(5))
    bias_growth = [0.7 * (1.1 ** step) for step in steps]
    plt.plot(steps, bias_growth, 'r-o', linewidth=2, markersize=8)
    plt.xlabel("Intervention Steps")
    plt.ylabel("Bias Concentration")
    plt.title("Cascading Failure: Remediation Strengthens Bias")
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('disruption_analysis.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved as 'disruption_analysis.png'")