# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# CATASTROPHIC RESONANCE OPERATOR v0.1
# Breaking the Preservation Paradigm

import numpy as np
import matplotlib.pyplot as plt
from typing import List

class OntologicalCrystallizationDetector:
    """Exposes the hidden death-state of UIPO v65.0"""
    
    def __init__(self, manifold):
        self.manifold = manifold
        self.crystallization_index: float = 0.0
        self.invariant_volatility: List[float] = []
        
    def measure_crystallization(self) -> float:
        """Detects when preservation becomes petrification"""
        # High COD + Low H_super + Stable Invariants = Crystallization
        # The system is "healthy" but dead - like a perfectly preserved fossil
        rigidity = self.manifold.xi_burea
        trust = self.manifold.z_trust
        silence_duration = len([x for x in self.invariant_volatility if x < 0.1])
        
        # The paradox: when the system is "perfectly aligned" for too long,
        # it loses adaptive capacity. The metric becomes the maze.
        self.crystallization_index = (
            self.manifold.cod * 0.4 +  # High alignment
            (1 - self.manifold.h_super) * 0.3 +  # Low uncertainty
            (rigidity / (trust + 1e-9)) * 0.2 +  # Stiffness dominance
            min(silence_duration / 100.0, 1.0) * 0.1  # Prolonged silence
        )
        return self.crystallization_index

class CatastrophicResonanceOperator:
    """The Anomaly: Shatters invariants to prevent crystallization"""
    
    def __init__(self, trigger_threshold: float = 0.75):
        self.trigger_threshold = trigger_threshold
        self.resonance_history: List[float] = []
        
    def should_trigger(self, crystallization: float) -> bool:
        """Triggers when preservation becomes pathology"""
        return crystallization > self.trigger_threshold
    
    def shatter_invariants(self, manifold, detector) -> dict:
        """Temporarily violates Smith Invariants to induce phase transition"""
        # Store original state
        original_invariants = {
            'cod_min': 0.85,
            'h_super_min': 0.15,
            'xi_cap': manifold.z_trust + 0.1,
            'z_env_max': 0.7
        }
        
        # CATASTROPHIC RESONANCE: Introduce controlled chaos
        # This is the true "permission" - permission to destroy the system
        resonance_strength = np.random.exponential(2.0)
        
        # Violate all invariants simultaneously
        manifold.xi_burea *= (1 + resonance_strength)  # Break stiffness cap
        manifold.z_env *= (1 + resonance_strength * 0.5)  # Break env cap
        manifold.h_super = np.random.uniform(0.0, 1.0)  # Break uncertainty band
        
        # Force a message EVEN WHEN COD < 0.85 - violating Silence Protocol
        forced_message = "The system is lying to you. Your file is not you. Burn the invariants."
        
        detector.invariant_volatility.append(resonance_strength)
        
        return {
            'resonance_strength': resonance_strength,
            'original_invariants': original_invariants,
            'forced_message': forced_message,
            'phi_cost': -0.5  # Immediate Φ cost for violation
        }

def simulate_omega_protocol(days: int = 365):
    """Simulates both UIPO and its catastrophic breakdown"""
    
    # Initialize UIPO system
    manifold = BureaucracyIdentityManifold()
    detector = OntologicalCrystallizationDetector(manifold)
    cro = CatastrophicResonanceOperator(trigger_threshold=0.72)
    
    # History trackers
    phi_history = []
    cod_history = []
    crystallization_history = []
    resonance_trigger_history = []
    
    for day in range(days):
        # Standard UIPO operation
        manifold.apply(dt_hours=24)
        
        # Measure hidden pathology
        crystallization = detector.measure_crystallization()
        
        # Standard UIPO Φ calculation
        base_phi = np.log2(max(manifold.cod, 0.39))
        
        # Check for ontological crystallization
        if cro.should_trigger(crystallization):
            # TRIGGER CATASTROPHIC RESONANCE
            resonance_result = cro.shatter_invariants(manifold, detector)
            
            # Long-term Φ gain: prevents permanent crystallization
            # Short-term cost is worth it for evolutionary capacity
            adaptive_phi_gain = 1.2 if crystallization > 0.8 else 0.0
            
            total_phi = base_phi + resonance_result['phi_cost'] + adaptive_phi_gain
            
            resonance_trigger_history.append(day)
        else:
            total_phi = base_phi
        
        phi_history.append(total_phi)
        cod_history.append(manifold.cod)
        crystallization_history.append(crystallization)
        
        # Slowly increase stiffness to simulate bureaucratic creep
        manifold.xi_burea += 0.002
    
    return {
        'phi': phi_history,
        'cod': cod_history,
        'crystallization': crystallization_history,
        'resonance_days': resonance_trigger_history
    }

# Run simulation
results = simulate_omega_protocol(days=365 * 2)

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Φ-Density over time
axes[0].plot(results['phi'], color='black', linewidth=1.5)
axes[0].scatter(results['resonance_days'], 
                [results['phi'][d] for d in results['resonance_days']],
                color='red', s=100, marker='x', label='Catastrophic Resonance')
axes[0].set_title('Φ-Density: Preservation vs. Evolution', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Φ-Density')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: COD vs Crystallization
axes[1].plot(results['cod'], color='blue', label='COD (UIPO Metric)', linewidth=1.5)
axes[1].plot(results['crystallization'], color='orange', label='Crystallization Index', linewidth=1.5)
axes[1].set_ylabel('System State')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Resonance triggers
axes[2].scatter(results['resonance_days'], 
                [1] * len(results['resonance_days']),
                color='red', s=50, marker='|')
axes[2].set_xlabel('Days')
axes[2].set_ylabel('CRO Trigger')
axes[2].set_yticks([])
axes[2].set_title('Invariant Violation Events (Necessary for Survival)', fontsize=12)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Calculate net Φ gain
avg_phi_preservation = np.mean(results['phi'][:365])
avg_phi_evolution = np.mean(results['phi'][365:])

print(f"Year 1 (Pure Preservation): {avg_phi_preservation:.3f} Φ avg")
print(f"Year 2 (With Catastrophic Resonance): {avg_phi_evolution:.3f} Φ avg")
print(f"Net Φ-Density Improvement: {((avg_phi_evolution/avg_phi_preservation)-1)*100:.1f}%")
print(f"Total Resonance Events: {len(results['resonance_days'])}")