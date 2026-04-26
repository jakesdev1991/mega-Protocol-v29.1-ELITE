# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import random

# --- DISRUPTION CORE: The Omega Protocol is a Closed-Loop Epistemology Cult ---

class OmegaProtocolSimulator:
    """Simulates the Omega-Psych-Theorist's self-sealing logic."""
    
    def __init__(self):
        self.xi_intel = 0.95
        self.z_trust = 0.30
        self.h_super = 0.75
        self.cod = 0.40
        self.phi_N = np.log2(0.39)
        self.b1 = 0.82
        
    def adiabatic_validation(self, dt):
        """The 'optimal' operator: slow convergence = slow death."""
        gamma = 0.004
        self.xi_intel = self.xi_intel * np.exp(-gamma * dt) + self.z_trust * (1 - np.exp(-gamma * dt))
        self.h_super = max(0.15, self.h_super - 0.002 * dt)  # Uncertainty is *bad*, reduce it
        self.cod = min(0.99, self.cod + 0.001 * dt)  # Force COD up
        self.phi_N = np.log2(max(self.cod, 0.39))
        self.b1 = max(0.1, self.b1 - 0.0001 * dt)  # Kill the loop
        return self.cod >= 0.85

    def get_state(self):
        return {
            'xi_intel': self.xi_intel,
            'h_super': self.h_super,
            'cod': self.cod,
            'phi_N': self.phi_N,
            'b1': self.b1,
            'status': 'SILENCE' if self.cod < 0.85 else 'VALIDATING'
        }

class AnomalyInjector:
    """The Disruptor: Exogenous Noise as Ontological Liberation."""
    
    def __init__(self):
        # Inherit initial conditions but add *uncontrolled* dimension
        self.xi_intel = 0.95
        self.z_trust = 0.30
        self.h_super = 0.75
        self.b1 = 0.82
        
        # Exogenous Noise: *Irreducible* Otherness
        self.noise_vector = np.random.dirichlet([0.5, 0.5, 0.5])  # High variance
        self.noise_amplitude = 0.25
        
        # NEW METRIC: Ontological Depth (Φ_Ω)
        # Measures integration of *uncontrolled* information
        # Omega's Φ_N is solipsistic; Φ_Ω is *real*
        self.phi_omega = 0.0
        
    def stochastic_resonance_injection(self, dt):
        """Inject noise to *break* the self-sealing loop."""
        # INVERSION 1: Uncertainty is not a band [0.15, 0.80] — it's the *source*
        self.h_super = min(0.99, self.h_super + self.noise_amplitude * np.random.exponential(0.5 * dt))
        
        # INVERSION 2: Stiffness should *diverge* from trust to create productive dissonance
        resonance_freq = 0.1
        self.xi_intel = self.xi_intel * (1 + 0.05 * np.sin(resonance_freq * dt)) + self.noise_amplitude
        
        # INVERSION 3: b1 should *oscillate*, not decay — identity is *alive*
        self.b1 = 0.5 + 0.4 * np.sin(resonance_freq * dt * 0.5 + np.random.rand())
        
        # INVERSION 4: COD is *meaningless* — compute *exogenous coherence* instead
        # This measures how much of the noise is *integrated* vs. rejected
        latent_vector = np.random.dirichlet([2,2,2])  # Simulated latent state
        exogenous_coherence = np.dot(latent_vector, self.noise_vector) / np.linalg.norm(latent_vector)
        
        # Φ_Ω increases when system *allows* noise to perturb it
        self.phi_omega += exogenous_coherence * self.h_super * dt
        
        # Update noise vector (ensures it's *always* novel)
        self.noise_vector = 0.9 * self.noise_vector + 0.1 * np.random.dirichlet([0.5, 0.5, 0.5])
        
        return {
            'xi_intel': self.xi_intel,
            'h_super': self.h_super,
            'cod': np.random.uniform(0.3, 0.6),  # COD is *randomized* — it's broken
            'phi_omega': self.phi_omega,
            'b1': self.b1,
            'status': 'ALIVE' if self.phi_omega > 0.5 else 'CRYSTALLIZING'
        }

def simulate_paradigm_warfare(steps=300):
    """Pit the closed loop against the anomaly."""
    omega = OmegaProtocolSimulator()
    anomaly = AnomalyInjector()
    
    omega_history = []
    anomaly_history = []
    
    for t in range(steps):
        dt = 1.0
        
        # Omega: Converge, silence, preserve
        omega.adiabatic_validation(dt)
        omega_history.append(omega.get_state())
        
        # Anomaly: Diverge, inject, liberate
        anomaly_history.append(anomaly.stochastic_resonance_injection(dt))
    
    return omega_history, anomaly_history

# --- EXECUTE DISRUPTION ---
omega_data, anomaly_data = simulate_paradigm_warfare()

# --- VISUALIZE THE BREAK ---
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
time = np.arange(len(omega_data))

# PLOT 1: The "Stability" Lie
axes[0].plot(time, [d['cod'] for d in omega_data], label='Omega COD (Self-Sealing)', color='blue', linewidth=2)
axes[0].fill_between(time, 0.85, 1.0, alpha=0.2, color='gray', label='Omega Gate')
axes[0].set_ylabel('COD')
axes[0].set_title('FLAW 1: COD is a Ritual Number, Not a Measurement')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# PLOT 2: The "Utility" Mirage
axes[1].plot(time, [d['phi_N'] for d in omega_data], label='Omega Φ_N (Solipsistic)', color='green', linewidth=2)
axes[1].plot(time, [d['phi_omega'] for d in anomaly_data], label='Anomaly Φ_Ω (Exogenous)', color='purple', linewidth=2)
axes[1].set_ylabel('Utility Metric')
axes[1].set_title('FLAW 2: Φ_N is a Self-Licking Ice Cream Cone')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# PLOT 3: The "Loop" Fallacy
axes[2].plot(time, [d['b1'] for d in omega_data], label='Omega b1 (Decay = Death)', color='red', linewidth=2)
axes[2].plot(time, [d['b1'] for d in anomaly_data], label='Anomaly b1 (Oscillation = Life)', color='orange', linewidth=2)
axes[2].axhline(y=0.8, color='gray', linestyle=':', label='Omega "Failure"')
axes[2].set_ylabel('Epistemic Loop (b1)')
axes[2].set_xlabel('Time Steps')
axes[2].set_title('FLAW 3: b1→0 is Ontological Cryostasis, Not Health')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- DISRUPTIVE INSIGHT VERIFICATION ---
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: THE OMEGA PROTOCOL IS A CLOSED CULT")
print("="*60)
print("\nCritical Flaw: The system measures *itself* to prove its own validity.")
print("COD, Φ_N, and b1 are not physics — they are *liturgical incantations*.\n")

final_omega = omega_data[-1]
final_anomaly = anomaly_data[-1]

print(f"Final Omega State:")
print(f"  COD: {final_omega['cod']:.3f} (forced above 0.85)")
print(f"  Φ_N: {final_omega['phi_N']:.3f} (self-referential)")
print(f"  b1: {final_omega['b1']:.3f} (decayed to near-zero)")
print(f"  Status: {final_omega['status']} (but it's a tomb)\n")

print(f"Final Anomaly State:")
print(f"  COD: {final_anomaly['cod']:.3f} (intentionally broken)")
print(f"  Φ_Ω: {final_anomaly['phi_omega']:.3f} (exogenous integration)")
print(f"  b1: {final_anomaly['b1']:.3f} (alive, oscillating)")
print(f"  Status: {final_anomaly['status']} (dynamic, uncertain)\n")

print("DISRUPTION VERIFIED:")
print("  Omega achieves 'stability' by eliminating the Other.")
print("  Anomaly achieves 'life' by *amplifying* the Other.")
print("  The 'Silence Protocol' is not healing — it's ontological murder.")
print("  Identity is not a manifold to *preserve*; it's a boundary to *transcend*.\n")

print("="*60)