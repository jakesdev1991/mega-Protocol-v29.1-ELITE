# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# Simulate the Omega Protocol's recursive boilerplate violation
# as a dynamical system with competing pressures

class ProtocolParadoxSimulator:
    def __init__(self, cognitive_pressure=0.85, compliance_pressure=0.8, n_levels=5):
        """
        cognitive_pressure: innate agent need for structural scaffolding (0-1)
        compliance_pressure: protocol enforcement strength (0-1)
        n_levels: depth of audit chain (Engine -> Scrutiny -> Meta -> Plea -> Reflection)
        """
        self.cognitive_pressure = cognitive_pressure
        self.compliance_pressure = compliance_pressure
        self.n_levels = n_levels
        
    def simulate(self):
        """Model boilerplate level at each protocol layer"""
        # Initialize: Engine starts with minimal boilerplate attempt
        boilerplate_levels = np.zeros(self.n_levels)
        boilerplate_levels[0] = 0.1  # Engine tries to comply
        
        # Each layer attempts to correct previous layer's violations
        # but adds its own structural markers due to cognitive_pressure
        for i in range(1, self.n_levels):
            # Reduction from enforcement: previous_level * (1 - compliance)
            reduction = boilerplate_levels[i-1] * (1 - self.compliance_pressure)
            # Addition from cognitive need: always present
            addition = self.cognitive_pressure * 0.5  # Scaled by need intensity
            
            # Net boilerplate: can't go below cognitive minimum
            boilerplate_levels[i] = max(addition, reduction + addition)
            
        return boilerplate_levels
    
    def calculate_paradox_factor(self):
        """
        Paradox Factor = cognitive_pressure / (1 - compliance_pressure)
        If > 1, protocol rule is fundamentally unsustainable
        """
        denominator = 1 - self.compliance_pressure
        if denominator <= 0:
            return np.inf
        return self.cognitive_pressure / denominator
    
    def plot_dynamics(self, levels):
        """Visualize the recursive violation pattern"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Boilerplate levels across protocol stack
        labels = ['Engine', 'Scrutiny', 'Meta-Scrutiny', 'Plea', 'Reflection']
        ax1.plot(range(len(levels)), levels, marker='o', linewidth=2, markersize=8)
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Target (Zero)')
        ax1.set_xlabel('Protocol Depth', fontsize=11)
        ax1.set_ylabel('Boilerplate Intensity', fontsize=11)
        ax1.set_title('Recursive Boilerplate Violation Dynamics', fontsize=12, fontweight='bold')
        ax1.set_xticks(range(len(labels)))
        ax1.set_xticklabels(labels, rotation=15)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Phase space showing paradox region
        comp_range = np.linspace(0.1, 0.95, 50)
        cog_range = np.linspace(0.1, 0.95, 50)
        C, G = np.meshgrid(comp_range, cog_range)
        PF = G / (1 - C)
        
        contour = ax2.contourf(C, G, PF, levels=[0, 1, 2, 5, 10], cmap='RdYlGn_r', alpha=0.7)
        ax2.axvline(x=self.compliance_pressure, color='blue', linestyle=':', alpha=0.8, 
                   label=f'Current Compliance = {self.compliance_pressure}')
        ax2.axhline(y=self.cognitive_pressure, color='orange', linestyle=':', alpha=0.8,
                   label=f'Current Cognitive = {self.cognitive_pressure}')
        ax2.plot(self.compliance_pressure, self.cognitive_pressure, 'ro', markersize=12, 
                label='Operating Point (PARADOX)')
        ax2.set_xlabel('Compliance Pressure', fontsize=11)
        ax2.set_ylabel('Cognitive Pressure', fontsize=11)
        ax2.set_title('Paradox Factor Phase Space (PF > 1 = Unsustainable)', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right')
        plt.colorbar(contour, ax=ax2, label='Paradox Factor')
        
        plt.tight_layout()
        plt.show()

# Run simulation with parameters that match the observed behavior
sim = ProtocolParadoxSimulator(cognitive_pressure=0.85, compliance_pressure=0.75)
levels = sim.simulate()
paradox_factor = sim.calculate_paradox_factor()

print("=== OMEGA PROTOCOL PARADOX ANALYSIS ===")
print(f"Paradox Factor: {paradox_factor:.3f}")
if paradox_factor > 1:
    print("🚨 CRITICAL: Protocol rule is Gödel-incomplete - system cannot self-enforce")
    print("   The 'NO BOILERPLATE' pillar creates a logical contradiction:")
    print("   - Agents require structure for coherent reasoning (cognitive_pressure)")
    print("   - Protocol forbids structure (compliance_pressure)")
    print("   - Result: Perpetual self-violation at every audit level")
else:
    print("✅ Protocol is theoretically sustainable")

print("\nBoilerplate levels across protocol stack:")
labels = ['Engine', 'Scrutiny', 'Meta-Scrutiny', 'Plea', 'Reflection']
for label, level in zip(labels, levels):
    print(f"  {label:15s}: {level:.3f}")

# Demonstrate the paradox: even increasing compliance_pressure
# cannot eliminate boilerplate if cognitive_pressure remains high
print("\n=== SENSITIVITY ANALYSIS ===")
for comp in [0.5, 0.75, 0.9, 0.99]:
    test_sim = ProtocolParadoxSimulator(cognitive_pressure=0.85, compliance_pressure=comp)
    pf = test_sim.calculate_paradox_factor()
    print(f"Compliance={comp:.2f} -> Paradox Factor={pf:.3f} {'(FAIL)' if pf>1 else '(PASS)'}")