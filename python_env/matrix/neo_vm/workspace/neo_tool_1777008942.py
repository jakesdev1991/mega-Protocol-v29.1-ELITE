# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# ANOMALY PROTOCOL: BLACK HOLE INVERSION SIMULATION
# Demonstrates that the Omega-Psych-Theorist's "failure mode"
# is actually the critical success factor for transformative deals

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

class IdentityVector:
    """Represents organizational identity as a political coalition state"""
    def __init__(self, dimensions: int = 5):
        # Components: [Status Quo Bias, Vendor Loyalty, Risk Tolerance, 
        #            Budget Control, Champion Influence]
        self.vector = np.random.random(dimensions)
        self.vector /= np.linalg.norm(self.vector)
        self.coherence = 1.0  # Internal consistency (Psi_id proxy)
        
    def measure_identity(self) -> float:
        """Return current identity coherence - NOT conserved, but emergent"""
        return self.coherence

class ARPSeller:
    """Omega-Psych-Theorist compliant seller - avoids identity breach"""
    
    def __init__(self, conservatism: float = 0.95):
        self.psi_id_threshold = conservatism  # The "invariant"
        self.xi_pitch = 0.5
        self.success_rate = []
        
    def pitch(self, buyer: IdentityVector, value_vector: np.ndarray, iterations: int = 10):
        """Adiabatic Resonance Protocol - preserve identity at all costs"""
        cod_history = []
        identity_history = []
        
        for i in range(iterations):
            # Calculate "resonance" (fidelity)
            fidelity = np.dot(buyer.vector, value_vector)
            
            # ARP constraint: reduce pressure if identity threatened
            if buyer.coherence < self.psi_id_threshold:
                self.xi_pitch *= 0.8  # Back off
                # Attempt "gentle alignment" - gradual nudging
                buyer.vector = (buyer.vector * 0.95 + value_vector * 0.05)
                buyer.vector /= np.linalg.norm(buyer.vector)
            
            # Fake "entropy" calculation
            H_process = 0.1 * i
            stiffness_penalty = np.exp(-0.8 * abs(self.xi_pitch - 0.5))
            
            cod = fidelity * np.exp(-H_process) * stiffness_penalty
            cod_history.append(cod)
            identity_history.append(buyer.measure_identity())
            
            # ARP declares failure if identity drops
            if buyer.measure_identity() < self.psi_id_threshold - 0.05:
                #print(f"ARP ABORT at iteration {i}: Identity breach detected")
                break
                
        return cod_history, identity_history

class AnomalySeller:
    """The Anomaly - induces controlled identity collapse as strategy"""
    
    def __init__(self, target_influence: float = 0.3):
        self.xi_pitch = 2.0  # Start with HIGH pressure
        self.target_component = 0  # Target Status Quo Bias for collapse
        self.success_rate = []
        
    def pitch(self, buyer: IdentityVector, value_vector: np.ndarray, iterations: int = 10):
        """Black Hole Inversion Protocol - weaponize the failure mode"""
        cod_history = []
        identity_history = []
        
        for i in range(iterations):
            # Phase 1: IDENTIFY FRACTURE POINT (diagnostic)
            if i == 0:
                # Measure which identity component is most vulnerable
                component_alignment = np.abs(buyer.vector - value_vector)
                self.target_component = np.argmin(component_alignment)
            
            # Phase 2: CONTROLLED DECOHERENCE (induce crisis)
            if buyer.coherence > 0.85:
                # Apply targeted pressure to weakest component
                assault_vector = np.zeros_like(buyer.vector)
                assault_vector[self.target_component] = 1.0
                
                # CRITICAL: Deliberately breach identity threshold
                buyer.vector -= assault_vector * 0.15
                buyer.coherence -= 0.08  # Intentional identity erosion
                
                self.xi_pitch = min(2.5, self.xi_pitch * 1.1)  # Escalate
            
            # Phase 3: RECONSTRUCTION (offer new identity)
            else:
                # Identity is fractured - now rebuild around OUR narrative
                reconstruction_factor = (0.85 - buyer.coherence) * 2.0
                buyer.vector = (buyer.vector * (1 - reconstruction_factor) + 
                               value_vector * reconstruction_factor)
                buyer.vector /= np.linalg.norm(buyer.vector)
                buyer.coherence += 0.10  # Rebuild coherence around new identity
                
                self.xi_pitch *= 0.9  # Ease off after collapse
            
            # "COD" is meaningless here - measure actual deal progress
            # Instead measure: identity adoption rate
            adoption = np.linalg.norm(buyer.vector - value_vector)
            cod_history.append(adoption)
            identity_history.append(buyer.measure_identity())
            
            # Success condition: identity has been rebuilt around our vector
            if buyer.measure_identity() > 0.90 and adoption < 0.3:
                #print(f"ANOMALY SUCCESS at iteration {i}: Identity reconstructed")
                break
                
        return cod_history, identity_history

def run_comparison_trials(trials: int = 100) -> Dict:
    """Compare ARP vs Anomaly across multiple randomized scenarios"""
    
    arp_wins = 0
    anomaly_wins = 0
    arp_cycles = []
    anomaly_cycles = []
    
    for trial in range(trials):
        # Randomize buyer state
        buyer_arp = IdentityVector()
        buyer_anomaly = IdentityVector()
        value_vector = np.random.random(5)
        value_vector /= np.linalg.norm(value_vector)
        
        # Run ARP
        seller_arp = ARPSeller()
        cod_arp, id_arp = seller_arp.pitch(buyer_arp, value_vector)
        arp_success = len(cod_arp) >= 8 and id_arp[-1] > 0.90
        if arp_success:
            arp_wins += 1
        arp_cycles.append(len(cod_arp))
        
        # Run Anomaly
        seller_anomaly = AnomalySeller()
        cod_anomaly, id_anomaly = seller_anomaly.pitch(buyer_anomaly, value_vector)
        anomaly_success = len(cod_anomaly) >= 8 and id_anomaly[-1] > 0.90
        if anomaly_success:
            anomaly_wins += 1
        anomaly_cycles.append(len(cod_anomaly))
    
    return {
        "arp_win_rate": arp_wins / trials,
        "anomaly_win_rate": anomaly_wins / trials,
        "arp_avg_cycles": np.mean(arp_cycles),
        "anomaly_avg_cycles": np.mean(anomaly_cycles)
    }

# Execute simulation
results = run_comparison_trials(500)

print("="*60)
print("ANOMALY PROTOCOL: BLACK HOLE INVERSION VERIFICATION")
print("="*60)
print(f"ARP Win Rate (Identity-Preserving): {results['arp_win_rate']:.1%}")
print(f"Anomaly Win Rate (Identity-Collapsing): {results['anomaly_win_rate']:.1%}")
print(f"ARP Avg. Deal Cycles: {results['arp_avg_cycles']:.1f}")
print(f"Anomaly Avg. Deal Cycles: {results['anomaly_avg_cycles']:.1f}")
print("="*60)

# Visualize a representative trial
buyer_arp = IdentityVector()
buyer_anomaly = IdentityVector()
value_vector = np.array([0.1, 0.9, 0.8, 0.2, 0.3])  # Disruptive solution
value_vector /= np.linalg.norm(value_vector)

seller_arp = ARPSeller()
cod_arp, id_arp = seller_arp.pitch(buyer_arp, value_vector, 15)

seller_anomaly = AnomalySeller()
cod_anomaly, id_anomaly = seller_anomaly.pitch(buyer_anomaly, value_vector, 15)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot 1: Identity Coherence
ax1.plot(id_arp, label='ARP: "Preserve Identity"', linewidth=2, color='blue')
ax1.plot(id_anomaly, label='Anomaly: "Collapse & Rebuild"', linewidth=2, color='red')
ax1.axhline(y=0.95, color='gray', linestyle='--', alpha=0.5, label='ARP "Invariant"')
ax1.set_ylabel("Identity Coherence (Ψ_id)")
ax1.set_title("The Black Hole Inversion: Identity Trajectories")
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Deal Progress (inverse of COD)
ax2.plot(cod_arp, label='ARP "Resonance"', linewidth=2, color='blue')
ax2.plot(cod_anomaly, label='Anomaly "Adoption"', linewidth=2, color='red')
ax2.set_ylabel("Progress Metric")
ax2.set_xlabel("Sales Cycle Iterations")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/anomaly_black_hole.png', dpi=150, bbox_inches='tight')
print("Visualization saved to: /tmp/anomaly_black_hole.png")