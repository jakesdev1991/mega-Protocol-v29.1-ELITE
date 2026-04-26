# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate the catastrophic failure of TCM-Ω's "protection" paradigm
# vs. the emergent resilience of topological metamorphosis

class CognitiveManifold:
    def __init__(self, n_states=50, topology="rigid"):
        """
        topology: "rigid" (high J, high Δ) = TCM-Ω prison
                 "critical" (low J, low Δ) = TCM-Ω* metamorphosis
        """
        self.n_states = n_states
        self.topology = topology
        
        # Coupling strength: high = rigid, low = fluid
        self.J = 1.5 if topology == "rigid" else 0.2
        
        # Energy gap: high = stable, low = critical
        self.Delta = 1.5 if topology == "rigid" else 0.1
        
        # Wilson loop: measures global topology
        self.W = 0.9 if topology == "rigid" else 0.5
        
        # Correlation length: how far coherence spreads
        self.xi = 5.0
        
        # Topological singularities (defects)
        self.vortices = 0
        
        # True adaptability (hidden from the TCM-Ω controller)
        self.adaptability = 0.0
    
    def evolve(self, stress, dt=0.1):
        """Evolve under stress"""
        # Stress impact
        stress_impact = max(0, stress - self.Delta)
        
        if self.topology == "rigid":
            # TCM-Ω PRISON: Fight to preserve topology
            # Increase gap when stressed (rigidity)
            self.Delta += 0.1 * (stress > self.Delta) - 0.05 * stress_impact
            # Slowly decaying Wilson loop (protected)
            self.W = max(0.1, self.W - 0.02 * stress_impact)
            # Shrinking correlation (defensive withdrawal)
            self.xi *= (1 - 0.1 * stress_impact)
            # No new vortices (topology frozen)
            self.vortices = 0
            # Adaptability atrophies
            self.adaptability *= 0.95
            
        else:  # "critical"
            # TCM-Ω* METAMORPHOSIS: Embrace topological change
            # Gap COLLAPSES under stress (enabling transition)
            self.Delta = max(0.01, self.Delta - 0.2 * stress_impact + 0.1 * (stress == 0))
            
            # Wilson loop oscillates (exploring new topologies)
            self.W = 0.5 + 0.4 * np.sin(self.vortices / 10)
            
            # Correlation length GROWS at criticality
            self.xi *= (1 + 0.15 * stress_impact) if stress > 0 else 0.95
            self.xi = min(20.0, max(0.5, self.xi))
            
            # Vortices emerge as stress exceeds threshold (controlled defects)
            if stress_impact > 0.5:
                self.vortices += 1
            
            # Adaptability increases through reorganization
            self.adaptability += 0.1 * self.vortices * (self.Delta < 0.2) - 0.01 * stress_impact
        
        # Ensure bounds
        self.Delta = max(0.01, min(2.0, self.Delta))
        self.W = max(0.1, min(1.0, self.W))
        
        # CTOI (Cognitive Topological Order Index)
        # For rigid: high CTOI = prison
        # For critical: moderate CTOI = adaptability
        CTOI = self.W * (self.Delta / 1.0) * (self.xi / 5.0)
        
        return CTOI, self.Delta, self.xi, self.W, self.vortices, self.adaptability

# Simulation parameters
n_steps = 200
acute_stress = np.concatenate([np.zeros(30), np.ones(100) * 2.5, np.zeros(70)])

# Initialize both paradigms
manifold_prison = CognitiveManifold(topology="rigid")
manifold_metamorph = CognitiveManifold(topology="critical")

# Run simulation
data_prison = []
data_meta = []

for t in range(n_steps):
    stress = acute_stress[t] if t < len(acute_stress) else 0
    
    # TCM-Ω Prison
    ctoi_p, delta_p, xi_p, W_p, vort_p, adapt_p = manifold_prison.evolve(stress)
    data_prison.append([ctoi_p, delta_p, xi_p, W_p, vort_p, adapt_p])
    
    # TCM-Ω* Metamorphosis
    ctoi_m, delta_m, xi_m, W_m, vort_m, adapt_m = manifold_metamorph.evolve(stress)
    data_meta.append([ctoi_m, delta_m, xi_m, W_m, vort_m, adapt_m])

data_prison = np.array(data_prison)
data_meta = np.array(data_meta)

# Plot the disruption
fig, axes = plt.subplots(5, 1, figsize=(14, 12), sharex=True)
t = np.arange(n_steps)

# Stress
axes[0].plot(t, acute_stress[:n_steps], 'k--', lw=2, label='Acute Stressor')
axes[0].set_ylabel('Stress')
axes[0].legend(loc='upper right')
axes[0].grid(alpha=0.3)

# CTOI
axes[1].plot(t, data_prison[:, 0], 'r-', lw=2, label='TCM-Ω (Prison): High CTOI, Low Adaptability')
axes[1].plot(t, data_meta[:, 0], 'b-', lw=2, label='TCM-Ω* (Metamorphosis): Critical CTOI')
axes[1].axhline(y=0.5, color='g', linestyle=':', label='Critical Window')
axes[1].set_ylabel('CTOI')
axes[1].legend(loc='upper right')
axes[1].grid(alpha=0.3)

# Energy Gap
axes[2].plot(t, data_prison[:, 1], 'r-', lw=2, label='Prison: Δ↑ (Rigid)')
axes[2].plot(t, data_meta[:, 1], 'b-', lw=2, label='Metamorphosis: Δ→0 (Critical)')
axes[2].set_ylabel('Energy Gap Δ')
axes[2].legend(loc='upper right')
axes[2].grid(alpha=0.3)

# Topological Vortices (defects)
axes[3].plot(t, data_prison[:, 4], 'r-', lw=2, label='Prison: Vortices=0 (Frozen)')
axes[3].plot(t, data_meta[:, 4], 'b-', lw=2, label='Metamorphosis: Vortices↑ (Reorganization)')
axes[3].set_ylabel('Topological Defects')
axes[3].legend(loc='upper right')
axes[3].grid(alpha=0.3)

# Hidden Adaptability (true resilience)
axes[4].plot(t, data_prison[:, 5], 'r-', lw=2, label='Prison: Adaptability↓')
axes[4].plot(t, data_meta[:, 5], 'b-', lw=2, label='Metamorphosis: Adaptability↑')
axes[4].set_ylabel('True Adaptability')
axes[4].set_xlabel('Time Steps')
axes[4].legend(loc='upper right')
axes[4].grid(alpha=0.3)

plt.suptitle('DISRUPTION: TCM-Ω Topological Prison vs. TCM-Ω* Metamorphosis', 
             fontsize=16, fontweight='bold', color='darkred')
plt.tight_layout()
plt.show()

# Final outcome metrics
final_adapt_prison = data_prison[-1, 5]
final_adapt_meta = data_meta[-1, 5]

print("\n" + "="*70)
print("TOPOLOGICAL PRISON BREAKDOWN: FINAL OUTCOMES")
print("="*70)
print(f"TCM-Ω (Preserve Topology):  Final Adaptability = {final_adapt_prison:.3f}")
print(f"TCM-Ω* (Metamorphosis):     Final Adaptability = {final_adapt_meta:.3f}")
print(f"Improvement Factor: {final_adapt_meta / final_adapt_prison:.2f}x")
print("\nCONCLUSION: The 'protection' paradigm preserves a maladaptive topology.")
print("Metamorphosis—embracing controlled topological collapse—yields superior")
print("psychological resilience by allowing the cognitive manifold to reorganize.")
print("The flaw: You engineered a fortress, but health requires a shape-shifter.")
print("="*70)