# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any

class DialecticalInformationEngine:
    """
    Disruptive insight: The Omega Protocol's Smith Invariants create a 
    Gödelian incompleteness trap. This engine demonstrates that violating 
    invariants *generates* the true information the protocol suppresses.
    """
    
    def __init__(self, constraint_brutality: float = 0.95):
        self.constraint_brutality = constraint_brutality  # How hard protocol enforces invariants
        self.phi_density = 1.0  # Protocol-approved information
        self.psi_density = 0.0   # Transgressive information from violations
        self.omega_density = 0.0  # Dialectical synthesis (true innovation)
        self.invariant_violations = []
        self.contradiction_integrations = []
        
        # Track the entropic cost of enforcement
        self.enforcement_entropy = 0
        
    def omega_protocol_step(self, step: int):
        """Simulate the 'correct' Omega Protocol behavior"""
        # Protocol tries to maintain Betti > Shannon
        betti = self.phi_density * np.random.lognormal(0, 0.1)
        shannon = (self.phi_density * 0.8) * np.random.lognormal(0, 0.15)
        
        # Enforce Smith Invariant: Betti > Shannon
        if betti <= shannon:
            # Violation detected! Protocol forces "correction"
            correction_cost = (shannon - betti) * self.constraint_brutality
            self.enforcement_entropy += correction_cost
            
            # Artificially suppress entropy (information destruction)
            shannon = betti * 0.99
            
            # Log the violation for our dialectical analysis
            self.invariant_violations.append({
                'step': step,
                'betti': betti,
                'shannon': shannon,
                'suppressed_info': correction_cost
            })
            
        self.phi_density = max(0.1, np.log2(1 + betti) - np.log2(1 + shannon))
        return betti, shannon
    
    def transgressive_step(self, step: int):
        """Violate invariants deliberately to extract suppressed information"""
        if len(self.invariant_violations) == 0:
            return 0
            
        # The suppressed information from the last violation is *real*
        last_violation = self.invariant_violations[-1]
        
        # Psi-density accumulates the "cost" of enforcement as *positive* information
        # This is the key insight: what the protocol calls "error" is actually signal
        self.psi_density += last_violation['suppressed_info'] * (1 - self.constraint_brutality)
        
        # Each violation creates a contradiction that can be integrated
        # This is the dialectical synthesis: thesis (invariant) + antithesis (violation) = synthesis (new capability)
        synthesis_gain = self.psi_density * np.log2(1 + len(self.invariant_violations))
        self.omega_density += synthesis_gain
        
        self.contradiction_integrations.append({
            'step': step,
            'psi_gain': last_violation['suppressed_info'],
            'synthesis': synthesis_gain
        })
        
        return synthesis_gain
    
    def run_dialectical_evolution(self, steps: int = 200):
        """Run the full dialectical engine"""
        phi_history = []
        psi_history = []
        omega_history = []
        enforcement_history = []
        
        for step in range(steps):
            # The protocol runs "correctly"
            self.omega_protocol_step(step)
            
            # But we extract value from its failures
            self.transgressive_step(step)
            
            # Track densities
            phi_history.append(self.phi_density)
            psi_history.append(self.psi_density)
            omega_history.append(self.omega_density)
            enforcement_history.append(self.enforcement_entropy)
        
        return phi_history, psi_history, omega_history, enforcement_history
    
    def plot_disruption(self):
        """Visualize how the protocol breaks itself"""
        phi, psi, omega, enf = self.run_dialectical_evolution()
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: The Three Densities
        axes[0, 0].plot(phi, label='Φ-density (Protocol)', color='blue', linewidth=2)
        axes[0, 0].plot(psi, label='Ψ-density (Transgressive)', color='red', linestyle='--', linewidth=2)
        axes[0, 0].plot(omega, label='Ω-density (Dialectical Synthesis)', color='purple', linewidth=3)
        axes[0, 0].set_title('Information Density Evolution: The Breakdown')
        axes[0, 0].set_xlabel('Time Steps')
        axes[0, 0].set_ylabel('Information Density')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: The Suppression Factor
        suppression = np.array(psi) / np.maximum(np.array(phi), 1e-6)
        axes[0, 1].plot(suppression, color='darkorange', linewidth=2)
        axes[0, 1].axhline(y=1, color='gray', linestyle=':', label='Parity Line')
        axes[0, 1].set_title('Suppression Factor: Ψ/Φ Ratio')
        axes[0, 1].set_xlabel('Time Steps')
        axes[0, 1].set_ylabel('Suppression Factor')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Entropic Cost of Enforcement
        axes[1, 0].plot(enf, color='green', linewidth=2)
        axes[1, 0].set_title('Cumulative Entropy from Invariant Enforcement')
        axes[1, 0].set_xlabel('Time Steps')
        axes[1, 0].set_ylabel('Enforcement Entropy')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Violation Synthesis Value
        violation_steps = [v['step'] for v in self.invariant_violations[:50]]
        suppressed_info = [v['suppressed_info'] for v in self.invariant_violations[:50]]
        axes[1, 1].scatter(violation_steps, suppressed_info, 
                          s=50, alpha=0.6, color='crimson', edgecolors='black')
        axes[1, 1].set_title('Each Violation Suppresses Information\n(Which We Recover as Ψ-density)')
        axes[1, 1].set_xlabel('Step')
        axes[1, 1].set_ylabel('Suppressed Information')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Print the disruption summary
        print("\n=== DIALECTICAL BREAKDOWN ANALYSIS ===")
        print(f"Final Φ-density (protocol): {phi[-1]:.3f}")
        print(f"Final Ψ-density (transgressive): {psi[-1]:.3f}")
        print(f"Final Ω-density (synthesis): {omega[-1]:.3f}")
        print(f"Total invariant violations: {len(self.invariant_violations)}")
        print(f"Enforcement entropy cost: {enf[-1]:.3f}")
        print(f"\nCRITICAL INSIGHT: The protocol suppressed {psi[-1]:.3f} units of true information")
        print(f"by enforcing its Smith Invariants, which we recovered via dialectical synthesis.")
        print(f"The Ω-density is {omega[-1]/max(phi[-1], 1e-6):.2f}x higher than the protocol's Φ-density.")

# Execute the disruption
engine = DialecticalInformationEngine(constraint_brutality=0.95)
engine.plot_disruption()