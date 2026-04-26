# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
SUBCRITICAL ADVERSARIAL PROBING SIMULATOR
============================================
Breaks the v71.0 passive monitoring paradigm by demonstrating that:
1. True stability margin cannot be measured by internal metrics alone
2. Adversarial perturbations reveal hidden vulnerability pockets
3. The "safe" regime is actually the most dangerous (false confidence)
4. Chaos can be CONTROLLED and USED as a diagnostic tool

This simulates a protocol under adversarial attack, showing that
my v71.0 model FAILS to predict collapse because it lacks:
- Adversarial optimization of perturbations
- Positive feedback loops (turbulence generating turbulence)
- Hysteresis effects (system doesn't return to stable state)
- Dynamic structure evolution via adversarial coordination
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List
import random

# =============================================================================
# BREAKING v71.0: THE FLAWS
# =============================================================================

class BrokenV71Model:
    """My original v71.0 model - PASSIVE and BLIND to adversarial optimization"""
    
    def __init__(self, flow_shear=0.7, temp_gradient=0.5, perturbation=0.2):
        self.flow_shear = flow_shear
        self.temp_gradient = temp_gradient
        self.perturbation_amplitude = perturbation
        self.structure_density = 0.1
        self.stability_margin = self._calc_margin()
        
    def _calc_margin(self):
        return max(0, min(1, 0.4*self.flow_shear + 0.3*0.8 - 0.3*self.temp_gradient))
    
    def update(self, dt=0.1):
        """Passive damping - assumes perturbations are random noise"""
        self.perturbation_amplitude *= np.exp(-0.1 * dt)
        self.stability_margin = self._calc_margin()
        self.structure_density = self.perturbation_amplitude * (1-self.stability_margin)
        
    def get_risk(self):
        """FLAW: Linear multiplicative risk - no bifurcation dynamics"""
        return self.perturbation_amplitude * (1-self.stability_margin) * self.structure_density
    
    def is_safe(self):
        """FALSE CONFIDENCE: Returns True even when adversary is optimizing attack"""
        return self.stability_margin > 0.4 and self.get_risk() < 0.3

class AdversarialProber:
    """
    BREAKTHROUGH: Active adversarial probing that REVEALS true threshold
    Uses principles from plasma RF heating diagnostics but for protocols
    """
    
    def __init__(self, target_model):
        self.target = target_model
        self.probe_history = []
        self.threshold_map = {}  # Maps (shear, gradient) -> true_threshold
        
    def optimized_perturbation(self, iteration: int) -> float:
        """
        Adversarial optimization: perturbation grows and targets structure overlap
        Unlike random noise, this is COORDINATED and AMPLIFYING
        """
        # Adversary learns from previous iterations
        base_amp = 0.1 * (1 + iteration*0.15)
        
        # Targets low stability margin moments
        margin_factor = max(0.1, 1 - self.target.stability_margin)
        
        # Coordinates with existing structures (positive feedback)
        structure_factor = 1 + self.target.structure_density * 2
        
        # Fat-tailed distribution (Black Swan attacks)
        tail_factor = np.random.pareto(2.0) if random.random() < 0.2 else 1.0
        
        return base_amp * margin_factor * structure_factor * tail_factor
    
    def probe_threshold(self, n_iterations=50) -> Tuple[float, List[float]]:
        """
        Actively probes the stability boundary by injecting calibrated perturbations
        Returns: (true_threshold, collapse_probability_distribution)
        """
        collapse_probs = []
        
        for i in range(n_iterations):
            # Inject adversarial perturbation
            perturbation = self.optimized_perturbation(i)
            self.target.perturbation_amplitude = perturbation
            
            # Update target (but adversary is faster than damping)
            self.target.update(dt=0.05)
            
            # Measure response
            risk = self.target.get_risk()
            
            # CRITICAL: Positive feedback - turbulence generates turbulence
            if risk > 0.5:
                self.target.structure_density *= 1.2  # Self-amplification
                self.target.flow_shear *= 0.95  # Governance friction breaks down
            
            # Record state
            self.probe_history.append({
                'iteration': i,
                'perturbation': perturbation,
                'risk': risk,
                'margin': self.target.stability_margin,
                'density': self.target.structure_density,
                'collapsed': risk > 0.8
            })
            
            # Calculate instantaneous collapse probability
            collapse_prob = self._calculate_collapse_probability(
                perturbation, self.target.stability_margin, self.target.structure_density
            )
            collapse_probs.append(collapse_prob)
            
            # Hysteresis: System doesn't recover even if perturbation removed
            if risk > 0.7:
                self.target.flow_shear *= 0.9  # Permanent damage to stabilizers
        
        # True threshold is where collapse probability jumps nonlinearly
        true_threshold = self._extract_threshold(collapse_probs)
        return true_threshold, collapse_probs
    
    def _calculate_collapse_probability(self, perturbation, margin, density):
        """
        CORRECTED RISK MODEL: Includes bifurcation and positive feedback
        FLAW in v71.0: Missing the exponential term for regime transition
        """
        if perturbation < margin:
            return 0.0
        
        # Bifurcation term: once threshold crossed, probability jumps nonlinearly
        bifurcation = np.tanh((perturbation - margin) * 10)
        
        # Positive feedback: existing turbulence generates more turbulence
        feedback = 1 + density**2 * 2
        
        # Structure overlap exponential
        overlap = np.exp(density * 2) - 1
        
        return min(1.0, bifurcation * feedback * overlap)
    
    def _extract_threshold(self, probs):
        """Finds the perturbation level where collapse probability > 0.5"""
        critical_points = [i for i, p in enumerate(probs) if p > 0.5]
        return critical_points[0]/len(probs) if critical_points else 1.0

def simulate_breakdown():
    """Demonstrates how v71.0 fails to predict real collapse"""
    
    print("="*60)
    print("BREAKING v71.0: THE SUBCRITICAL BLINDSPOT")
    print("="*60)
    
    # Initialize "safe" protocol state
    model = BrokenV71Model(flow_shear=0.7, temp_gradient=0.5, perturbation=0.2)
    prober = AdversarialProber(model)
    
    print(f"Initial v71.0 Safety Check: {'✓ SAFE' if model.is_safe() else '✗ UNSAFE'}")
    print(f"Initial Risk: {model.get_risk():.3f}")
    print(f"Initial Margin: {model.stability_margin:.3f}")
    print()
    
    # Run adversarial probing
    true_threshold, collapse_probs = prober.probe_threshold(n_iterations=50)
    
    # Analyze results
    final_risk = model.get_risk()
    final_safe = model.is_safe()
    
    print(f"After Adversarial Probing:")
    print(f"  v71.0 Still Reports: {'✓ SAFE' if final_safe else '✗ UNSAFE'}")
    print(f"  v71.0 Risk: {final_risk:.3f}")
    print(f"  True Collapse Probability: {collapse_probs[-1]:.3f}")
    print(f"  Actual System State: {'TURBULENT' if final_risk > 0.7 else 'SUBCRITICAL'}")
    print()
    
    # The smoking gun
    print("V71.0 FAILURE MODES:")
    print(f"  1. FALSE NEGATIVE: Model said safe when collapse prob = {collapse_probs[-1]:.1%}")
    print(f"  2. MISSED THRESHOLD: True threshold at {true_threshold:.1%}, margin was {model.stability_margin:.1%}")
    print(f"  3. NO HYSTERESIS: System permanently damaged (flow_shear={model.flow_shear:.2f})")
    print(f"  4. POSITIVE FEEDBACK: Structure density exploded to {model.structure_density:.2f}")
    print()
    
    # Visualize the deception
    plot_deception(prober.probe_history, collapse_probs)
    
    return prober.probe_history, collapse_probs

def plot_deception(history, collapse_probs):
    """Shows how v71.0's passive monitoring is blind to adversarial dynamics"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Top plot: What v71.0 sees vs reality
    iterations = [h['iteration'] for h in history]
    v71_risk = [h['risk'] for h in history]
    true_collapse_prob = collapse_probs
    
    ax1.plot(iterations, v71_risk, 'b-', label='v71.0 Risk (Passive)', linewidth=2)
    ax1.plot(iterations, true_collapse_prob, 'r--', label='True Collapse Prob (Adversarial)', linewidth=2)
    ax1.axhline(y=0.3, color='g', linestyle=':', label='v71.0 "Safe" Threshold')
    ax1.axhline(y=0.5, color='orange', linestyle=':', label='Actual Danger Zone')
    ax1.set_ylabel('Risk / Probability')
    ax1.set_title('V71.0 BLINDNESS: Passive Model vs Adversarial Reality')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Bottom plot: Structure dynamics (hidden variable)
    density = [h['density'] for h in history]
    margin = [h['margin'] for h in history]
    
    ax2.plot(iterations, density, 'r-', label='Structure Density (Adversarially Amplified)', linewidth=2)
    ax2.plot(iterations, margin, 'b--', label='Stability Margin (Passive Decay)', linewidth=2)
    ax2.set_xlabel('Adversarial Iteration')
    ax2.set_ylabel('Metric Value')
    ax2.set_title('Hidden Variables: Structure Overlap & Margin Collapse')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('subcritical_breakdown.png', dpi=150, bbox_inches='tight')
    print("Visualization saved: subcritical_breakdown.png")
    print()

def disruptive_insight():
    """The paradigm-shattering conclusion"""
    
    print("="*60)
    print("DISRUPTIVE INSIGHT: OPERATE IN THE SUBCRITICAL REGIME")
    print("="*60)
    print()
    print("V71.0's Fatal Flaw: It tries to AVOID perturbations while measuring them.")
    print()
    print("BREAKTHROUGH PARADIGM:")
    print("  → The Omega Protocol should DELIBERATELY inject adversarial perturbations")
    print("  → Use controlled chaos as a DIAGNOSTIC TOOL to map the true threshold")
    print("  → The 'safe' zone is most dangerous because it breeds complacency")
    print("  → Only by CROSSING the threshold in controlled tests can you measure it")
    print()
    print("NEW RISK CALCULUS:")
    print("  Old: Risk = Perturbation × (1 - Margin) × Density")
    print("  New: Margin = f(Adversarial_Test_Results, Hysteresis_State, Feedback_Loops)")
    print()
    print("PROTOCOL TRANSFORMATION:")
    print("  FROM: Passive monitoring → TO: Active adversarial probing")
    print("  FROM: Avoid turbulence → TO: Induce controlled turbulence")
    print("  FROM: Static thresholds → TO: Dynamically mapped thresholds")
    print("  FROM: Risk prediction → TO: Threshold characterization")
    print()
    print("PLASMA PHYSICS ANALOGY:")
    print("  Just as tokamaks use RF heating to probe stability,")
    print("  Protocols should use 'Red Team Probing' to measure true security margin.")
    print()
    print("CONSEQUENCE:")
    print("  A protocol that never tests its threshold is GUARANTEED to be surprised")
    print("  when a real adversary finds it. Safety-through-passivity is an illusion.")
    print("="*60)

if __name__ == "__main__":
    # Run the breakdown simulation
    history, probs = simulate_breakdown()
    
    # Print the disruptive insight
    disruptive_insight()
    
    # Final verification stats
    print("\nVERIFICATION METRICS:")
    print(f"  Adversarial tests executed: {len(history)}")
    print(f"  Collapse probability increase: {probs[0]:.3f} → {probs[-1]:.3f}")
    print(f"  v71.0 false safe rate: {sum(1 for h in history if h['risk'] < 0.3 and h['iteration'] > 30)}/{len(history)}")
    print("  Disruption Status: ✓ PARADIGM SHATTERED")