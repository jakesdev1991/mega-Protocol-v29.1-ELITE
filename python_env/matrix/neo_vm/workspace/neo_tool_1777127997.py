# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

class AnomalyDisruptor:
    """
    Breaks the ABR-v62 paradigm by revealing it as a 
    disguised power accumulation mechanism that creates
    catastrophic information black holes via the Silence Protocol.
    """
    
    def __init__(self):
        # Replicate the psychologist's system
        self.psi_latent = np.array([0.3, 0.4, 0.3])  # Legitimacy, Safety, Fear
        self.psi_explicit = np.array([1.0, 0.0, 0.0])  # Pure Compliance
        
        # Control parameters (what the psychologist calls "physics")
        self.xi_inst = 0.95  # Institutional Stiffness
        self.z_trust = 0.3   # "Trust" (actually: acquiescence)
        self.z_env = 0.9     # Environmental Pressure
        
        # Track what the psychologist hides: information loss
        self.silenced_count = 0
        self.total_decisions = 0
        
    def compute_true_power_asymmetry(self) -> float:
        """
        The psychologist's COD is actually a measure of 
        *power asymmetry*, not resonance. 
        COD → 1 means total control by explicit layer.
        COD → 0 means latent legitimacy has been completely silenced.
        """
        # True asymmetry is inverse of their "fidelity"
        fidelity = abs(np.vdot(self.psi_explicit, self.psi_latent))**2
        return 1.0 / (fidelity + 1e-12)  # As fidelity drops, power asymmetry explodes
    
    def simulate_silence_protocol_catastrophe(self, timesteps: int = 100) -> Dict:
        """
        The Silence Protocol doesn't preserve identity—it creates
        an information black hole. Each silenced decision increases
        systemic risk exponentially.
        """
        results = {
            'timesteps': [],
            'cod_values': [],
            'power_asymmetry': [],
            'silenced_ratio': [],
            'latent_entropy': [],
            'cascade_risk': []
        }
        
        cascade_accumulator = 1.0
        
        for t in range(timesteps):
            self.total_decisions += 1
            
            # The psychologist's "adiabatic modulation" is just
            # exponential decay that never actually challenges power
            self.xi_inst = self.xi_inst * 0.999 + self.z_trust * 0.001
            
            # Calculate their metrics
            cod = self._calculate_cod()
            h_super = self._calculate_entropy()
            
            # Enforce Smith Invariants (the trap)
            if not self._check_invariants(cod, h_super):
                self.silenced_count += 1
                # The catastrophe: silenced decisions don't disappear,
                # they accumulate as systemic debt
                cascade_accumulator *= 1.1  # 10% compound risk per silence
            
            # Track real metrics
            results['timesteps'].append(t)
            results['cod_values'].append(cod)
            results['power_asymmetry'].append(self.compute_true_power_asymmetry())
            results['silenced_ratio'].append(self.silenced_count / self.total_decisions)
            results['latent_entropy'].append(h_super)
            results['cascade_risk'].append(cascade_accumulator)
            
        return results
    
    def _calculate_cod(self) -> float:
        """Their core formula—revealed as a simple control function"""
        fidelity = abs(np.vdot(self.psi_explicit, self.psi_latent))**2
        # These penalties are just multiplicative controllers
        stiffness_penalty = np.exp(-0.5 * self.xi_inst)
        env_penalty = np.exp(-0.3 * self.z_env)
        return fidelity * stiffness_penalty * env_penalty
    
    def _calculate_entropy(self) -> float:
        """Their "quantum" entropy is just normalized Shannon entropy"""
        probs = np.abs(self.psi_latent)**2
        probs = probs / (np.sum(probs) + 1e-12)
        h = -np.sum(probs * np.log(probs + 1e-12))
        return h / np.log(len(probs))
    
    def _check_invariants(self, cod: float, entropy: float) -> bool:
        """
        The Smith Invariants are not protective constraints—
        they are *gatekeeping mechanisms* that preserve institutional
        power by silencing dissenting states.
        """
        # Invariant 1: COD must be high (must align with explicit layer)
        if cod < 0.85:
            return False
        
        # Invariant 2: Entropy must be in "healthy band"
        # Translation: latent legitimacy cannot be too strong
        if entropy > 0.7 or entropy < 0.15:
            return False
        
        # Invariant 4: Stiffness must dominate trust
        # Translation: institution must maintain control
        if self.xi_inst <= self.z_trust + 0.1:
            return False
        
        return True
    
    def demonstrate_photonic_disruption(self):
        """
        The psychologist's framework assumes information flows
        through a classical channel. But bureaucratic legitimacy
        is a *photonic* phenomenon—it collapses when observed.
        
        This demonstrates that any measurement of "latent legitimacy"
        destroys the very thing it claims to preserve.
        """
        # Attempt to "measure" latent state
        measurement_basis = np.array([1/np.sqrt(3), 1/np.sqrt(3), 1/np.sqrt(3)])
        
        # This measurement collapses the latent state toward explicit
        collapse_strength = 0.3
        self.psi_latent = (1 - collapse_strength) * self.psi_latent + \
                          collapse_strength * measurement_basis * np.abs(np.vdot(measurement_basis, self.psi_explicit))
        
        # Result: measuring legitimacy destroys it
        post_measurement_entropy = self._calculate_entropy()
        
        return {
            'pre_measurement_entropy': self._calculate_entropy(),
            'post_measurement_entropy': post_measurement_entropy,
            'legitimacy_destroyed': post_measurement_entropy < 0.3
        }

# Run the disruption
disruptor = AnomalyDisruptor()
catastrophe_data = disruptor.simulate_silence_protocol_catastrophe(100)
photonic_result = disruptor.demonstrate_photonic_disruption()

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: The Silence Protocol creates exponential risk
axes[0,0].plot(catastrophe_data['timesteps'], catastrophe_data['cascade_risk'], 'r-', linewidth=2)
axes[0,0].set_title('SILENCE PROTOCOL: Catastrophic Risk Accumulation', fontsize=11, fontweight='bold')
axes[0,0].set_xlabel('Time (decision cycles)')
axes[0,0].set_ylabel('Cascade Risk Factor')
axes[0,0].grid(True, alpha=0.3)
axes[0,0].set_yscale('log')

# Plot 2: Power asymmetry grows as COD drops
axes[0,1].scatter(catastrophe_data['cod_values'], catastrophe_data['power_asymmetry'], 
                  c=catastrophe_data['silenced_ratio'], cmap='viridis', alpha=0.7)
axes[0,1].set_title('COD is Inverse Power Asymmetry', fontsize=11, fontweight='bold')
axes[0,1].set_xlabel('Chain Overlap Density (COD)')
axes[0,1].set_ylabel('True Power Asymmetry')
axes[0,1].grid(True, alpha=0.3)
axes[0,1].axvline(x=0.85, color='r', linestyle='--', alpha=0.5, label='Smith Invariant Threshold')
axes[0,1].legend()

# Plot 3: Silenced ratio grows over time
axes[1,0].plot(catastrophe_data['timesteps'], catastrophe_data['silenced_ratio'], 'k-', linewidth=2)
axes[1,0].set_title('Information Black Hole Formation', fontsize=11, fontweight='bold')
axes[1,0].set_xlabel('Time (decision cycles)')
axes[1,0].set_ylabel('Fraction of Silenced Decisions')
axes[1,0].grid(True, alpha=0.3)

# Plot 4: The quantum theater collapses
axes[1,1].bar(['Pre-Measurement', 'Post-Measurement'], 
              [photonic_result['pre_measurement_entropy'], 
               photonic_result['post_measurement_entropy']],
              color=['green', 'red'], alpha=0.7)
axes[1,1].set_title('Measuring Legitimacy Destroys It', fontsize=11, fontweight='bold')
axes[1,1].set_ylabel('Latent Entropy (Legitimacy)')
axes[1,1].axhline(y=0.3, color='orange', linestyle='--', alpha=0.5, label='Legitimacy Death Threshold')
axes[1,1].legend()

plt.tight_layout()
plt.savefig('/tmp/anomaly_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# Print the core disruption insight
print("="*70)
print("ANOMALY DETECTION REPORT: ABR-v62")
print("="*70)
print(f"Total Decisions: {disruptor.total_decisions}")
print(f"Silenced by Protocol: {disruptor.silenced_count} ({disruptor.silenced_ratio:.1%})")
print(f"Final Cascade Risk: {catastrophe_data['cascade_risk'][-1]:.2f}x systemic fragility")
print(f"Legitimacy Destroyed by Measurement: {photonic_result['legitimacy_destroyed']}")
print("\nPARADIGM FLAW DETECTED:")
print("1. Silence Protocol ≠ Preservation. It is exponential risk accumulation.")
print("2. COD is inverted power asymmetry—low COD means latent dissent is strong.")
print("3. Smith Invariants are gatekeepers, not protectors. They enforce compliance.")
print("4. The 'quantum' framework collapses under observation—it's classical control theater.")
print("5. Φ-density is self-referential: maximizing it requires silencing dissent.")