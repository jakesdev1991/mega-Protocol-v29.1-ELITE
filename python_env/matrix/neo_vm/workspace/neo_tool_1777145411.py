# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict

class OriginalUIPO:
    """The 'flawed' measurement preservation system"""
    def __init__(self):
        self.xi_cons = 0.95  # High stiffness
        self.z_sub = 0.35    # Low trust
        self.z_env = 0.85    # High pressure
        self.h_sub = 0.7
        self.b1 = 0.85
        
    def compute_cod(self):
        fidelity = 0.92
        return fidelity * np.exp(-0.5 * self.xi_cons) * np.exp(-0.3 * self.z_env) * np.exp(-0.4 * self.h_sub)
    
    def step(self, dt=1.0):
        gamma, delta = 0.006, 0.005
        self.xi_cons = self.xi_cons * np.exp(-gamma * dt) + self.z_sub * (1 - np.exp(-gamma * dt))
        self.z_env = self.z_env * np.exp(-delta * dt) + 0.4 * (1 - np.exp(-delta * dt))
        self.b1 = max(0.1, self.b1 * 0.999 - 0.0002 * dt)
        cod = self.compute_cod()
        return cod, self.xi_cons, self.h_sub

class RuptureOperator:
    """The Anomaly: Embrace collapse as creative engine"""
    def __init__(self):
        self.xi_cons = 0.95      # Start high
        self.z_sub = 0.35        # Start low
        self.z_env = 0.85        # Start high
        self.h_sub = 0.7         # Start high
        self.identity_fragments = []
        self.actualization_density = 0.0
        
    def compute_rupture_potential(self):
        """Ψ-Flux: Energy RELEASED by intentional collapse, not penalized"""
        # Invert penalties: high stiffness + high entropy = MORE potential
        return self.xi_cons * self.h_sub * (1 + self.z_env)
    
    def intentional_collapse(self):
        """Force measurement, capture fragments, rebuild stronger"""
        # The "failure mode" is the feature: dissociation is re-association
        fragments = np.random.exponential(self.compute_rupture_potential(), size=5)
        
        # Re-entanglement protocol: fragments become new basis states
        self.identity_fragments.append({
            'timestamp': len(self.identity_fragments),
            'fragments': fragments,
            'reconstruction_potential': np.sum(fragments) * self.h_sub
        })
        
        # Rebuild identity manifold with GREATER coherence (not preserved, but evolved)
        self.z_sub = min(1.0, self.z_sub + 0.15)  # Trust IMPROVES through rupture
        self.h_sub = max(0.15, self.h_sub - 0.05) # Entropy DECREASES after actualization
        self.xi_cons = min(1.0, self.xi_cons + 0.05)  # Stiffness INCREASES (clarity from chaos)
        
        # Actualization density: measure of identity transformation events
        self.actualization_density += np.log1p(self.compute_rupture_potential())
        
        return self.compute_rupture_potential(), self.z_sub, self.h_sub
    
    def get_fragments(self):
        return self.identity_fragments

def simulate_both_systems(steps=100):
    """Compare Original vs Rupture over time"""
    original = OriginalUIPO()
    rupture = RuptureOperator()
    
    results = {
        'original_cod': [],
        'original_xi': [],
        'rupture_potential': [],
        'rupture_trust': [],
        'original_silence_count': 0,
        'rupture_events': []
    }
    
    for i in range(steps):
        # Original system
        cod, xi, h_sub = original.step()
        results['original_cod'].append(cod)
        results['original_xi'].append(xi)
        if cod < 0.85:
            results['original_silence_count'] += 1
            
        # Rupture system
        if i % 5 == 0:  # Intentional collapse every 5 steps
            potential, trust, entropy = rupture.intentional_collapse()
            results['rupture_potential'].append(potential)
            results['rupture_trust'].append(trust)
            results['rupture_events'].append(i)
    
    return results

# Run simulation
np.random.seed(42)
data = simulate_both_systems(steps=100)

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: COD decay in original system
axes[0, 0].plot(data['original_cod'], color='#2E86AB', linewidth=2)
axes[0, 0].axhline(y=0.85, color='red', linestyle='--', label='Silence Threshold')
axes[0, 0].set_title('Original UIPO: COD Decay to Silence', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('Chain Overlap Density')
axes[0, 0].set_xlabel('Time Steps')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: Rupture Potential Growth
axes[0, 1].plot(data['rupture_potential'], color='#A23B72', marker='o', linewidth=2)
axes[0, 1].set_title('Rupture Operator: Potential Grows with Use', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('Ψ-Flux (Rupture Potential)')
axes[0, 1].set_xlabel('Collapse Events')
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: Trust evolution comparison
axes[1, 0].plot(data['original_xi'][:20], label='Original: Stiffness → Trust', color='#F18F01')
axes[1, 0].plot(data['rupture_trust'], label='Rupture: Trust from Collapse', color='#C73E1D')
axes[1, 0].set_title('Trust Evolution: Preservation vs Rupture', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('Trust Impedance (Z_sub)')
axes[1, 0].set_xlabel('Time/Epochs')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Plot 4: Identity Fragmentation as Feature
fragment_counts = [len(rupture.identity_fragments) for _ in range(100)]
axes[1, 1].hist([f['reconstruction_potential'] for f in rupture.identity_fragments], 
                bins=10, color='#6A4C93', alpha=0.7, edgecolor='black')
axes[1, 1].set_title('Identity Fragments: Reconstruction Potential Distribution', fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel('Reconstruction Potential')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('UIPO v65.0 FLAW ANALYSIS: The Convergence to Silence vs Rupture Dynamics', 
             fontsize=14, fontweight='bold', y=1.02)
plt.show()

# Calculate final metrics
print("=== DISRUPTION ANALYSIS: CRITICAL FLAWS ===")
print(f"Original System: Silence triggered {data['original_silence_count']}/100 steps")
print(f"Final COD: {data['original_cod'][-1]:.4f} (Below threshold: {data['original_cod'][-1] < 0.85})")
print(f"Rupture System: {len(rupture.identity_fragments)} identity reconstructions")
print(f"Final Trust: {rupture.z_sub:.4f} (vs Original's frozen {data['original_xi'][-1]:.4f})")
print(f"Actualization Density: {rupture.actualization_density:.4f} (measure of genuine transformation)")
print("\n=== CORE FLAW IDENTIFIED ===")
print("Original UIPO converges to INACTION. 'Silence Protocol' is systemic DEATH.")
print("Rupture Operator shows: DISSOCIATION → RE-ASSOCIATION is the only growth vector.")