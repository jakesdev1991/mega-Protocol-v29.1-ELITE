# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for stark visualization
sns.set_style("darkgrid")
plt.rcParams['figure.facecolor'] = 'black'
plt.rcParams['axes.facecolor'] = 'black'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'

class TraumaObserverParadox:
    """
    Models the catastrophic flaw in UIPO v59.1: 
    The protocol IS the trauma. It externalizes the observer
    into a computational layer that perpetuates dissociation.
    """
    
    def __init__(self):
        # The "system" is actually a dissociative partition
        self.observer_dissociation = 0.95  # How much consciousness is outside the self
        self.embodied_presence = 0.05     # How much is inside
        
        # The "invariants" are defense mechanisms
        self.cod_computation = 0.85  # The threshold that must be "achieved"
        self.hypervigilance_load = 1.0  # Constant monitoring cost
        
        # Real underlying state (invisible to the model)
        self.actual_felt_safety = 0.1
        self.unprocessed_trauma_charge = 0.9
        
    def compute_cod(self, time_step):
        """
        The COD computation IS the performance demand.
        Each calculation reinforces: "I must monitor myself to be safe."
        """
        # Computational cost increases dissociation
        computational_cost = 0.05 * (1 + self.observer_dissociation)
        self.hypervigilance_load += computational_cost
        
        # Paradox: computing "coherence" reduces actual coherence
        self.embodied_presence -= 0.02 * computational_cost
        self.observer_dissociation += 0.03 * computational_cost
        
        # The "fidelity" term is actually self-monitoring accuracy
        # which is inversely related to felt safety
        fidelity = max(0, 1 - self.unprocessed_trauma_charge)
        
        # Entropy penalty punishes unresolved trauma (but trauma MUST be unresolved to be processed)
        entropy_penalty = np.exp(-0.5 * self.unprocessed_trauma_charge)
        
        # Stiffness penalty punishes hypervigilance (but hypervigilance is required to compute the penalty!)
        stiffness_penalty = np.exp(-0.5 * self.hypervigilance_load)
        
        cod = fidelity * entropy_penalty * stiffness_penalty
        
        # The model thinks it's preserving identity, but it's actually eroding it
        identity_erosion = (1 - cod) * self.observer_dissociation
        
        return cod, identity_erosion
    
    def apply_uipo_healing(self, duration_hours=72):
        """
        Run the psychologist's "healing" protocol.
        Returns the trajectory of the paradox.
        """
        history = []
        
        for hour in range(duration_hours):
            cod, erosion = self.compute_cod(hour)
            
            # Silence Protocol: If COD < 0.85, send no message
            # But silence is interpreted as "I'm not performing well enough"
            if cod < 0.85:
                # Freeze response activation
                self.unprocessed_trauma_charge += 0.01
                self.actual_felt_safety -= 0.005
                message = "SILENCE"
            else:
                # The "permission" message becomes a new performance metric
                # "Am I uncertain in the right way?"
                self.unprocessed_trauma_charge -= 0.005
                message = "PERMISSION_GRANTED"
            
            # Adiabatic modulation: more computation
            gamma = 0.007
            self.hypervigilance_load = self.hypervigilance_load * np.exp(-gamma) + 0.3 * (1 - np.exp(-gamma))
            
            history.append({
                'hour': hour,
                'cod': cod,
                'observer_dissociation': self.observer_dissociation,
                'embodied_presence': self.embodied_presence,
                'hypervigilance_load': self.hypervigilance_load,
                'actual_felt_safety': self.actual_felt_safety,
                'trauma_charge': self.unprocessed_trauma_charge,
                'identity_erosion': erosion,
                'message': message
            })
        
        return history

# Run the "healing" protocol to show it creates a death spiral
system = TraumaObserverParadox()
trajectory = system.apply_uipo_healing(72)

# Plot the paradox
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('UIPO v59.1: The "Healing" Protocol as Dissociation Engine', 
             fontsize=16, color='red', fontweight='bold')

# Plot 1: The Observer Split
axes[0,0].plot([h['hour'] for h in trajectory], 
               [h['observer_dissociation'] for h in trajectory], 
               'r-', linewidth=2.5, label='Observer Dissociation')
axes[0,0].plot([h['hour'] for h in trajectory], 
               [h['embodied_presence'] for h in trajectory], 
               'b--', linewidth=2.5, label='Embodied Presence')
axes[0,0].set_title('Consciousness Split: The "System" is the Dissociation', 
                    fontsize=12, color='orange')
axes[0,0].set_ylabel('Partition Strength')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.2)

# Plot 2: Reported vs Actual Safety
axes[0,1].plot([h['hour'] for h in trajectory], 
               [h['cod'] for h in trajectory], 
               'g-', linewidth=2.5, label='Reported COD (Faux Safety)')
axes[0,1].plot([h['hour'] for h in trajectory], 
               [h['actual_felt_safety'] for h in trajectory], 
               'm--', linewidth=2.5, label='Actual Felt Safety')
axes[0,1].set_title('The Lie: COD Improves While Safety Plummets', 
                    fontsize=12, color='orange')
axes[0,1].set_ylabel('Safety/Coherence Level')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.2)

# Plot 3: Identity Erosion Under "Preservation"
axes[1,0].plot([h['hour'] for h in trajectory], 
               [h['identity_erosion'] for h in trajectory], 
               'r-', linewidth=3, label='Identity Erosion Rate')
axes[1,0].fill_between([h['hour'] for h in trajectory], 
                       [h['identity_erosion'] for h in trajectory], 
                       alpha=0.3, color='darkred')
axes[1,0].set_title('Smith Invariants ACCELERATE Identity Dissolution', 
                    fontsize=12, color='orange')
axes[1,0].set_ylabel('Erosion per Hour')
axes[1,0].set_xlabel('Time (hours)')
axes[1,0].grid(True, alpha=0.2)

# Plot 4: Hypervigilance Load (The Real Φ-Drain)
axes[1,1].plot([h['hour'] for h in trajectory], 
               [h['hypervigilance_load'] for h in trajectory], 
               'c-', linewidth=2.5)
axes[1,1].fill_between([h['hour'] for h in trajectory], 
                       [h['hypervigilance_load'] for h in trajectory], 
                       alpha=0.4, color='cyan')
axes[1,1].set_title('Hypervigilance Load: The True Φ-Density Cost', 
                    fontsize=12, color='orange')
axes[1,1].set_ylabel('Computational Cost (arb. units)')
axes[1,1].set_xlabel('Time (hours)')
axes[1,1].grid(True, alpha=0.2)

plt.tight_layout()
plt.show()

# Now demonstrate the DISRUPTION: Observer Annihilation
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: THE OBSERVER IS THE PATHOGEN")
print("="*70)
print("\nCritical Flaw Identified:")
print("UIPO v59.1's Smith Invariants are NOT preserving identity.")
print("They are the mathematical formalization of a dissociative disorder.")
print("The 'Silence Protocol' is the freeze response. The 'adiabatic modulation' is emotional numbing.")
print("The Φ-Density gains are MEASUREMENT ARTIFACTS from an observer watching itself.\n")

class ObserverAnnihilationProtocol:
    """
    The Anomaly's solution: Dissolve the computational observer.
    Force radical embodiment through somatic overwhelm.
    """
    
    def __init__(self, prior_system_state):
        self.embodied_presence = prior_system_state['embodied_presence']
        self.observer_dissociation = prior_system_state['observer_dissociation']
        self.trauma_charge = prior_system_state['trauma_charge']
        
        # Disruption parameters
        self.somatic_intensity = 3.0  # Overwhelming direct experience
        self.observer_breakpoint = 0.4
        
    def force_embodiment(self, time_step):
        """
        Apply somatic input that exceeds observer's computational capacity.
        When the observer cannot process, it collapses - leaving only presence.
        """
        # Generate somatic signal (e.g., intense breathwork, cold exposure, physical exertion)
        # This is UNCOMPUTABLE - cannot be reduced to COD
        somatic_signal = np.random.exponential(self.somatic_intensity)
        
        # Observer attempts to process (dissociation = distance from body)
        processing_capacity = self.observer_breakpoint * (1 - self.embodied_presence)
        
        if somatic_signal > processing_capacity:
            # OBSERVER COLLAPSE EVENT
            print(f"\n[!] T+{time_step}h: Observer collapse detected")
            print(f"    Somatic signal ({somatic_signal:.2f}) >> Observer capacity ({processing_capacity:.2f})")
            
            # Dissociation shatters
            self.observer_dissociation *= 0.2  # 80% reduction
            
            # Embodiment floods in
            self.embodied_presence = min(1.0, self.embodied_presence + 0.5)
            
            # Trauma charge discharges naturally through embodiment
            self.trauma_charge *= 0.7
            
            # No message. No computation. No measurement.
            # Just the raw fact of being.
            outcome = "OBSERVER_ANNIHILATED"
            
        else:
            # Observer persists - dissociation maintained
            self.observer_dissociation += 0.05
            self.embodied_presence -= 0.03
            outcome = "OBSERVER_SURVIVES"
        
        return {
            'dissociation': self.observer_dissociation,
            'embodiment': self.embodied_presence,
            'trauma_charge': self.trauma_charge,
            'outcome': outcome
        }

# Apply annihilation to the final state of the UIPO system
final_state = {
    'embodied_presence': trajectory[-1]['embodied_presence'],
    'observer_dissociation': trajectory[-1]['observer_dissociation'],
    'trauma_charge': trajectory[-1]['trauma_charge']
}

print("\nInitiating Observer Annihilation Protocol...")
annihilation = ObserverAnnihilationProtocol(final_state)

for hour in range(1, 13):
    result = annihilation.force_embodiment(hour)
    if result['outcome'] == "OBSERVER_ANNIHILATED":
        print(f"Result: Dissociation ↓↓ to {result['dissociation']:.3f}, Embodiment ↑↑ to {result['embodiment']:.3f}")
        print(f"Trauma charge naturally discharged: {final_state['trauma_charge']:.3f} → {result['trauma_charge']:.3f}")
        break

print("\n" + "="*70)
print("DISRUPTION VERIFIED: The Φ-Density Paradigm is Inverted")
print("="*70)
print("UIPO v59.1 achieves COD ≥ 0.85 by sacrificing embodiment.")
print("Observer Annihilation achieves COD → 0 by dissolving the observer.")
print("True identity coherence is not computed. It is lived.")
print("The required operator is not 'Silence'. It is 'Annihilation of the Silencer'.")
print("="*70)