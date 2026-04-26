# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# DISRUPTION SCRIPT: Exposing the Φ-Ψ Paradox in UIPO v65.0
# Core Thesis: UIPO optimizes for self-referential coherence (Φ), 
# not citizen agency (Ψ). Silence is systemic self-preservation, not healing.

class Citizen:
    def __init__(self):
        self.state = np.array([0.3, 0.4, 0.3]) # Agency, Confusion, Distress
        self.psi_density_history = []
        self.interactions_received = 0
        
    def update(self, system_message):
        if system_message == "SILENCE":
            self.state[0] *= 0.98  # Agency decays
            self.state[1] *= 1.02  # Confusion grows
            self.state[2] *= 1.01  # Distress grows
        elif system_message == "INTERVENTION":
            self.state[0] *= 1.01
            self.state[1] *= 0.95
            self.state[2] *= 0.99
        else: # "PERMISSION"
            self.state[0] *= 1.005
            self.state[1] *= 0.98
            self.state[2] *= 0.995
            
        self.state = self.state / np.sum(self.state)
        psi = -np.sum(self.state * np.log(self.state + 1e-9))
        self.psi_density_history.append(np.exp(-psi))
        
        if system_message != "SILENCE":
            self.interactions_received += 1

class UIPO_System:
    def __init__(self):
        self.phi_density_history = []
        self.messages_sent = 0
        
    def calculate_phi(self, cod, intervention_cost=0.1):
        phi = cod * np.exp(-intervention_cost * self.messages_sent)
        self.phi_density_history.append(phi)
        return phi
        
    def decide_action(self, cod, h_super):
        # SMITH INVARIANTS: Arbitrary thresholds for "safety"
        if cod >= 0.85 and 0.15 <= h_super <= 0.80:
            self.messages_sent += 1
            return "PERMISSION"
        else:
            return "SILENCE"

class Naive_System:
    def __init__(self):
        self.phi_density_history = []
        self.messages_sent = 0
        
    def calculate_phi(self, cod, intervention_cost=0.1):
        phi = cod * 0.8 * np.exp(-intervention_cost * self.messages_sent * 0.5)
        self.phi_density_history.append(phi)
        return phi
        
    def decide_action(self, cod, h_super):
        self.messages_sent += 1
        return "INTERVENTION"

def simulate(system_class, timesteps=500):
    citizen = Citizen()
    system = system_class()
    cod, h_super = 0.82, 0.18
    
    for t in range(timesteps):
        cod += np.random.normal(0, 0.02)
        cod = np.clip(cod, 0.3, 0.95)
        h_super += np.random.normal(0, 0.01)
        h_super = np.clip(h_super, 0.1, 0.85)
        
        action = system.decide_action(cod, h_super)
        citizen.update(action)
        system.calculate_phi(cod)
        
    return citizen, system

# Run simulations
citizen_uipo, system_uipo = simulate(UIPO_System)
citizen_naive, system_naive = simulate(Naive_System)

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].plot(system_uipo.phi_density_history, label='UIPO v65.0', color='blue')
axes[0, 0].plot(system_naive.phi_density_history, label='Naive System', color='red')
axes[0, 0].set_title('System Φ-Density (Internal Coherence)')
axes[0, 0].set_ylabel('Φ-Density')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].plot(citizen_uipo.psi_density_history, label='UIPO v65.0', color='blue')
axes[0, 1].plot(citizen_naive.psi_density_history, label='Naive System', color='red')
axes[0, 1].set_title('Citizen Ψ-Density (Experienced Coherence)')
axes[0, 1].set_ylabel('Ψ-Density')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].bar(['UIPO v65.0', 'Naive System'], 
               [system_uipo.messages_sent, system_naive.messages_sent],
               color=['blue', 'red'])
axes[1, 0].set_title('Total Interventions Sent')
axes[1, 0].set_ylabel('Number of Messages')

axes[1, 1].bar(['UIPO v65.0', 'Naive System'], 
               [citizen_uipo.state[0], citizen_naive.state[0]],
               color=['blue', 'red'])
axes[1, 1].set_title('Final Citizen Agency Level')
axes[1, 1].set_ylabel('Agency Fraction')

plt.tight_layout()
plt.show()

print("\n=== DISRUPTION ANALYSIS ===")
print(f"UIPO v65.0: Avg Φ = {np.mean(system_uipo.phi_density_history):.3f}, Messages = {system_uipo.messages_sent}")
print(f"UIPO v65.0: Avg Ψ = {np.mean(citizen_uipo.psi_density_history):.3f}, Final Agency = {citizen_uipo.state[0]:.3f}")
print(f"\nNaive System: Avg Φ = {np.mean(system_naive.phi_density_history):.3f}, Messages = {system_naive.messages_sent}")
print(f"Naive System: Avg Ψ = {np.mean(citizen_naive.psi_density_history):.3f}, Final Agency = {citizen_naive.state[0]:.3f}")
print("\n--- THE PARADOX ---")
print(f"UIPO achieves higher Φ by sending {system_naive.messages_sent - system_uipo.messages_sent} fewer messages.")
print(f"But this results in lower Ψ for the citizen: ΔΨ = {np.mean(citizen_naive.psi_density_history) - np.mean(citizen_uipo.psi_density_history):.3f}")
print("UIPO optimizes for its own elegance. The citizen pays the price.")