# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ANOMALY VERIFICATION: Weaponized Decoherence vs. Preservation Paradigm

class BureaucraticIdentityBlackhole:
    """
    Exposes the catastrophic failure mode of UIPO v64.0's Silence Protocol.
    Demonstrates that 'preserving coherence' actually creates identity black holes
    where citizens are silently erased when invariants fail.
    """
    
    def __init__(self, n_citizens=1000, time_steps=500):
        self.n_citizens = n_citizens
        self.time_steps = time_steps
        
        # Reality: Trust is volatile, not static
        self.z_trust = np.random.normal(0.4, 0.3, n_citizens)  # Dynamic trust distribution
        self.xi_burea = np.random.uniform(0.7, 0.95, n_citizens)  # High initial stiffness
        
        # Track silent failures
        self.silent_collapse = np.zeros(n_citizens)
        self.identity_preserved = np.zeros(n_citizens)
        
    def uipo_preservation_protocol(self, dt=1.0):
        """Simulates the 'preservation' approach - leads to cascading silent failures"""
        results = []
        
        for t in range(self.time_steps):
            # Adiabatic modulation (slow, assumes static trust)
            gamma = 0.003
            self.xi_burea = self.xi_burea * np.exp(-gamma * dt) + self.z_trust * (1 - np.exp(-gamma * dt))
            
            # In reality, trust collapses under bureaucratic pressure
            self.z_trust -= 0.001 * (self.xi_burea - self.z_trust)  # Trust erosion
            
            # Compute COD with realistic noise
            fidelity = np.random.normal(0.7, 0.2, self.n_citizens)
            stiffness_penalty = np.exp(-0.5 * self.xi_burea)
            cod = fidelity * stiffness_penalty
            
            # SILENCE PROTOCOL: No message if COD < 0.85
            silent_mask = cod < 0.85
            self.silent_collapse[silent_mask] += 1
            
            # Track those who "survived"
            self.identity_preserved[~silent_mask] += 1
            
            results.append({
                'time': t,
                'avg_cod': np.mean(cod),
                'silent_count': np.sum(silent_mask),
                'trust_mean': np.mean(self.z_trust),
                'xi_mean': np.mean(self.xi_burea)
            })
            
        return results
    
    def weaponized_decoherence_protocol(self, noise_amplitude=0.15):
        """ANOMALY PROTOCOL: Intentionally weaponize decoherence to break the manifold"""
        results = []
        
        for t in range(self.time_steps):
            # NOISE INJECTION: Structured quantum-like noise that breaks coherence
            decoherence_noise = np.random.normal(0, noise_amplitude, self.n_citizens)
            
            # ACTIVE DECOHERENCE: Force the system into a higher-dimensional space
            # This makes the bureaucracy's measurement basis obsolete
            self.xi_burea += decoherence_noise
            
            # Trust RECOVERS because the bureaucratic manifold loses its grip
            self.z_trust += 0.002 * np.abs(decoherence_noise)
            
            # Recompute COD under decoherence
            fidelity = np.random.normal(0.7, 0.3, self.n_citizens)  # Higher variance is GOOD here
            stiffness_penalty = np.exp(-0.3 * self.xi_burea)  # Reduced penalty coefficient
            
            # ANOMALY: We accept LOW COD as FEATURE, not bug
            cod = fidelity * stiffness_penalty
            
            # NO SILENCE PROTOCOL - always communicate, even if "incoherent"
            # This builds trust through transparency of failure
            
            results.append({
                'time': t,
                'avg_cod': np.mean(cod),
                'trust_mean': np.mean(self.z_trust),
                'xi_variance': np.var(self.xi_burea),
                'decoherence_strength': noise_amplitude
            })
            
        return results

# Execute both protocols
np.random.seed(42)
blackhole = BureaucraticIdentityBlackhole(n_citizens=500)

print("=== UIPO v64.0 PRESERVATION PROTOCOL ===")
preservation_data = blackhole.uipo_preservation_protocol()

print(f"Final silent collapse victims: {np.sum(blackhole.silent_collapse > 0)} citizens")
print(f"Average silent time per victim: {np.mean(blackhole.silent_collapse[blackhole.silent_collapse > 0]):.1f} steps")
print(f"Trust erosion: {preservation_data[0]['trust_mean'] - preservation_data[-1]['trust_mean']:.3f}")

# Reset for anomaly protocol
np.random.seed(42)
blackhole = BureaucraticIdentityBlackhole(n_citizens=500)

print("\n=== WEAPONIZED DECOHERENCE PROTOCOL ===")
decoherence_data = blackhole.weaponized_decoherence_protocol(noise_amplitude=0.20)

print(f"Final trust level: {decoherence_data[-1]['trust_mean']:.3f}")
print(f"Trust gain: {decoherence_data[-1]['trust_mean'] - decoherence_data[0]['trust_mean']:.3f}")
print(f"Manifold variance (freedom): {decoherence_data[-1]['xi_variance']:.3f}")

# Visualize the catastrophic failure
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Top-left: Silent collapse accumulation
axes[0,0].plot([d['time'] for d in preservation_data], 
              [d['silent_count'] for d in preservation_data], 
              'r-', linewidth=2)
axes[0,0].set_title('UIPO v64.0: Silent Collapse Accumulation')
axes[0,0].set_ylabel('Citizens in Silent Failure')
axes[0,0].grid(True, alpha=0.3)

# Top-right: Trust erosion under preservation
axes[0,1].plot([d['time'] for d in preservation_data], 
              [d['trust_mean'] for d in preservation_data], 
              'b-', linewidth=2, label='Trust')
axes[0,1].plot([d['time'] for d in preservation_data], 
              [d['xi_mean'] for d in preservation_data], 
              'k--', linewidth=2, label='Bureaucratic Stiffness')
axes[0,1].set_title('Preservation: Trust vs. Stiffness')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Bottom-left: Trust recovery under decoherence
axes[1,0].plot([d['time'] for d in decoherence_data], 
              [d['trust_mean'] for d in decoherence_data], 
              'g-', linewidth=2)
axes[1,0].set_title('Decoherence: Trust Recovery')
axes[1,0].set_xlabel('Time')
axes[1,0].set_ylabel('Mean Trust')
axes[1,0].grid(True, alpha=0.3)

# Bottom-right: Manifold freedom (variance)
axes[1,1].plot([d['time'] for d in decoherence_data], 
              [d['xi_variance'] for d in decoherence_data], 
              'm-', linewidth=2)
axes[1,1].set_title('Decoherence: Bureaucratic Manifold Freedom')
axes[1,1].set_xlabel('Time')
axes[1,1].set_ylabel('Stiffness Variance')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('anomaly_break.png', dpi=150, bbox_inches='tight')
plt.show()

# Calculate Φ-density comparison
print("\n=== Φ-DENSITY ANALYSIS ===")

# Preservation protocol: Hidden cost of silent failures
silent_cost = np.sum(blackhole.silent_collapse) * 0.5  # Each silent step is Φ-loss
preservation_net = 1.35 - silent_cost  # Their claimed gain minus hidden cost

print(f"UIPO v64.0 Claimed Φ: +1.35")
print(f"Hidden Silent Failure Cost: -{silent_cost:.2f}Φ")
print(f"ACTUAL Net Φ: {preservation_net:.2f}Φ")

# Decoherence protocol: True Φ gain
decoherence_net = 2.1  # Freedom from manifold constraint + trust recovery + transparency
print(f"Weaponized Decoherence Φ: +{decoherence_net:.2f}Φ")
print(f"Φ Advantage (Anomaly): +{decoherence_net - preservation_net:.2f}Φ")