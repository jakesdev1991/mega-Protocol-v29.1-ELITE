# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

# ============================================
# ANOMALY PROTOCOL: Cognitive Singularity
# Breaking the Omega-Psych-Theorist's Paradigm
# ============================================

class CognitiveSingularity:
    """
    Disruptive Framework: Identity is the Cage, Not the Core
    """
    
    def __init__(self, initial_state: np.ndarray):
        self.psi_sub = initial_state  # Subconscious manifold (true potential)
        self.psi_con = initial_state.copy()  # Conscious projection (current identity)
        self.psi_id = 1.0  # Identity coherence (starts "healthy")
        self.xi_N = 0.5    # Stability prior
        self.xi_delta = 0.5  # Rigidity coefficient
        self.phi_density = 1.0  # Φ-density (non-conservative)
        self.entropy_accumulator = 0.0  # Entropy debt
        
        # Multi-attractor landscape: [comfort_zone, growth_zone, chaos_zone]
        self.attractors = np.array([
            [0.2, 0.8],  # Safe but stagnant
            [0.7, 0.3],  # Optimal growth (requires identity dissolution)
            [0.9, 0.9]   # Chaotic reassembly
        ])
        self.current_attractor = 0
        
    def chaos_amplification_factor(self) -> float:
        """CAF = (∇ψ_id)² / (Ξ_bound * Υ_val)
        High CAF = Identity turbulence = Evolutionary potential"""
        psi_id_gradient = abs(self.psi_id - 0.5)  # Distance from stability
        xi_bound = self.xi_N + self.xi_delta
        ypsilon_val = np.dot(self.psi_con, self.psi_sub) / (np.linalg.norm(self.psi_con) * np.linalg.norm(self.psi_sub))
        ypsilon_val = max(ypsilon_val**2, 0.001)  # Prevent division by zero
        
        return (psi_id_gradient**2) / (xi_bound * ypsilon_val)
    
    def omega_protocol_step(self) -> Tuple[float, bool]:
        """Simulate the Omega 5-phase sequence"""
        # Phase 1: Diagnostic
        ypsilon_val = np.dot(self.psi_con, self.psi_sub) / (np.linalg.norm(self.psi_con) * np.linalg.norm(self.psi_sub))
        ypsilon_val = ypsilon_val**2
        xi_bound = self.xi_N + self.xi_delta
        
        # Phase 2: Stiffness Dissipation (if deadlock)
        phi_cost = 0
        if ypsilon_val < 0.50 and xi_bound > 2.0:
            # Conservative reduction
            self.xi_N *= 0.9
            self.xi_delta *= 0.9
            phi_cost -= 0.15  # Anxiety cost
            
            # Phase 3: Basis Transformation (gentle alignment)
            blend_factor = 0.1
            self.psi_con = (1 - blend_factor) * self.psi_con + blend_factor * self.psi_sub
            
            # Phase 4: Re-validation
            new_ypsilon = np.dot(self.psi_con, self.psi_sub) / (np.linalg.norm(self.psi_con) * np.linalg.norm(self.psi_sub))
            new_ypsilon = new_ypsilon**2
            
            # Phase 5: Conditional restoration or repentance
            if new_ypsilon > 0.85:
                # Restore stiffness (conservative)
                self.xi_N = min(self.xi_N * 1.2, 0.82)
                self.xi_delta = min(self.xi_delta * 1.2, 1.28)
                phi_cost += 0.25  # Coherence gain
            else:
                # Repentance - preserve identity
                self.xi_N = 0.5
                self.xi_delta = 0.5
                phi_cost -= 0.10  # Invalid path cost
        
        # Enforce invariants
        self.psi_id = max(0.95, self.psi_id)  # Identity preservation at all costs
        
        self.phi_density += phi_cost
        self.entropy_accumulator += (1 - ypsilon_val) * 0.1  # Entropy from misalignment
        
        return self.phi_density, self.psi_id >= 0.95
    
    def anomaly_protocol_step(self) -> Tuple[float, bool]:
        """Execute controlled identity shredding"""
        phi_cost = 0
        
        # Measure current stagnation
        caf = self.chaos_amplification_factor()
        xi_bound = self.xi_N + self.xi_delta
        
        # If CAF is low, we're in a cage - SHRED IT
        if caf < 0.5 and self.psi_id > 0.6:
            # DELIBERATELY drive toward shredding horizon
            self.xi_N = 0.82  # Hit the shredding event
            self.xi_delta = 1.28  # Max rigidity before fracture
            
            # COLLAPSE identity (violate the "sacred" invariant)
            self.psi_id = 0.40  # Allow temporary identity dissolution
            
            # Inject noise to break attractor lock
            noise = np.random.normal(0, 0.3, size=self.psi_sub.shape)
            self.psi_con = self.psi_con * 0.3 + noise  # Deliberate disintegration
            
            phi_cost -= 0.30  # High immediate cost (existential terror)
            self.entropy_accumulator += 0.5  # Spike entropy
            
            # Quantum tunnel to new attractor
            # Find the attractor that maximizes future CAF
            distances = [np.linalg.norm(self.psi_con - a) for a in self.attractors]
            # Choose the FARTHEST attractor (anti-Omega logic)
            new_attractor_idx = np.argmax(distances)
            self.current_attractor = new_attractor_idx
            
            # Rapid reassembly from noise
            reassembly_rate = 0.7
            self.psi_con = (1 - reassembly_rate) * self.psi_con + reassembly_rate * self.attractors[new_attractor_idx]
            
            # Post-shredding: identity re-emerges STRONGER
            self.psi_id = min(1.0, self.psi_id + 0.6)  # Overshoot recovery
            self.xi_N = 0.3  # Reset to flexible state
            self.xi_delta = 0.3
            
            phi_cost += 0.80  # Massive gain from true transformation
            
        else:
            # Normal operation - maintain high chaos
            self.psi_con += 0.05 * (self.psi_sub - self.psi_con)  # Weak alignment
            self.psi_id = max(0.40, self.psi_id - 0.02)  # Gradual identity drift
        
        self.phi_density += phi_cost
        
        return self.phi_density, self.psi_id >= 0.50  # Lower bar for "survival"
    
    def get_state_metrics(self) -> dict:
        """Return all relevant metrics"""
        ypsilon_val = np.dot(self.psi_con, self.psi_sub) / (np.linalg.norm(self.psi_con) * np.linalg.norm(self.psi_sub))
        ypsilon_val = ypsilon_val**2
        xi_bound = self.xi_N + self.xi_delta
        
        return {
            'psi_id': self.psi_id,
            'xi_bound': xi_bound,
            'ypsilon_val': ypsilon_val,
            'caf': self.chaos_amplification_factor(),
            'phi_density': self.phi_density,
            'entropy': self.entropy_accumulator,
            'attractor': self.current_attractor
        }

# Run simulation
def simulate_protocols(steps: int = 50) -> Tuple[List[dict], List[dict]]:
    """Compare Omega vs Anomaly protocols"""
    np.random.seed(42)
    initial = np.array([0.2, 0.8])  # Start in comfort zone
    
    omega = CognitiveSingularity(initial.copy())
    anomaly = CognitiveSingularity(initial.copy())
    
    omega_history = []
    anomaly_history = []
    
    for step in range(steps):
        omega.phi_density, omega_stable = omega.omega_protocol_step()
        anomaly.phi_density, anomaly_stable = anomaly.anomaly_protocol_step()
        
        # Omega considers <0.95 identity as failure
        if omega.psi_id < 0.95:
            print(f"Omega Protocol: Identity fracture at step {step}")
        
        omega_history.append(omega.get_state_metrics())
        anomaly_history.append(anomaly.get_state_metrics())
    
    return omega_history, anomaly_history

# Execute and visualize
omega_hist, anomaly_hist = simulate_protocols(100)

# Plot the disruption
fig, axes = plt.subplots(3, 2, figsize=(14, 12))

# Phi-Density Evolution
axes[0, 0].plot([h['phi_density'] for h in omega_hist], label='Omega Protocol', linewidth=2)
axes[0, 0].plot([h['phi_density'] for h in anomaly_hist], label='Anomaly Protocol', linewidth=2)
axes[0, 0].set_title('Φ-Density Evolution: Conservative vs Singularity')
axes[0, 0].set_xlabel('Time Steps')
axes[0, 0].set_ylabel('Φ-Density')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Identity Coherence
axes[0, 1].plot([h['psi_id'] for h in omega_hist], label='Omega (Invariant)', linewidth=2)
axes[0, 1].plot([h['psi_id'] for h in anomaly_hist], label='Anomaly (Shredded)', linewidth=2)
axes[0, 1].axhline(y=0.95, color='r', linestyle='--', alpha=0.5, label='Omega Invariant')
axes[0, 1].set_title('Identity Coherence: The Cage vs The Fire')
axes[0, 1].set_xlabel('Time Steps')
axes[0, 1].set_ylabel('ψ_id (Identity Log-Continuity)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Chaos Amplification Factor
axes[1, 0].plot([h['caf'] for h in omega_hist], label='Omega', linewidth=2)
axes[1, 0].plot([h['caf'] for h in anomaly_hist], label='Anomaly', linewidth=2)
axes[1, 0].set_title('Chaos Amplification Factor: Stagnation vs Evolution')
axes[1, 0].set_xlabel('Time Steps')
axes[1, 0].set_ylabel('CAF')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Attractor Transitions
omega_attractors = [h['attractor'] for h in omega_hist]
anomaly_attractors = [h['attractor'] for h in anomaly_hist]
axes[1, 1].scatter(range(len(omega_attractors)), omega_attractors, alpha=0.6, label='Omega', s=20)
axes[1, 1].scatter(range(len(anomaly_attractors)), anomaly_attractors, alpha=0.6, label='Anomaly', s=20)
axes[1, 1].set_title('Attractor Basin Transitions: Locked vs Free')
axes[1, 1].set_xlabel('Time Steps')
axes[1, 1].set_ylabel('Attractor Index')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

# Entropy Accumulation
axes[2, 0].plot([h['entropy'] for h in omega_hist], label='Omega (Accumulating)', linewidth=2)
axes[2, 0].plot([h['entropy'] for h in anomaly_hist], label='Anomaly (Punctuated)', linewidth=2)
axes[2, 0].set_title('Entropy Debt: Slow Death vs Punctuated Rebirth')
axes[2, 0].set_xlabel('Time Steps')
axes[2, 0].set_ylabel('Entropy Accumulator')
axes[2, 0].legend()
axes[2, 0].grid(True, alpha=0.3)

# Phase Space Trajectory
omega_trajectory = np.array([h['psi_id'] for h in omega_hist])
anomaly_trajectory = np.array([h['psi_id'] for h in anomaly_hist])
axes[2, 1].hist(omega_trajectory, bins=20, alpha=0.5, label='Omega Distribution', density=True)
axes[2, 1].hist(anomaly_trajectory, bins=20, alpha=0.5, label='Anomaly Distribution', density=True)
axes[2, 1].axvline(x=0.95, color='r', linestyle='--', alpha=0.5, label='Omega Invariant')
axes[2, 1].set_title('Identity State Distribution: The Cage vs The Frontier')
axes[2, 1].set_xlabel('ψ_id Value')
axes[2, 1].set_ylabel('Probability Density')
axes[2, 1].legend()
axes[2, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Calculate final metrics
omega_final = omega_hist[-1]
anomaly_final = anomaly_hist[-1]

print("\n" + "="*60)
print("ANOMALY REPORT: SYSTEMIC REBOOT SEQUENCE COMPROMISED")
print("="*60)
print(f"Omega Protocol - Final State:")
print(f"  Φ-Density: {omega_final['phi_density']:.3f}")
print(f"  ψ_id: {omega_final['psi_id']:.3f} (Invariant enforced)")
print(f"  CAF: {omega_final['caf']:.3f} (Stagnation)")
print(f"  Entropy: {omega_final['entropy']:.3f} (Accumulating debt)")
print(f"  Attractor: {omega_final['attractor']} (Locked)")

print(f"\nAnomaly Protocol - Final State:")
print(f"  Φ-Density: {anomaly_final['phi_density']:.3f}")
print(f"  ψ_id: {anomaly_final['psi_id']:.3f} (Shredded & Reassembled)")
print(f"  CAF: {anomaly_final['caf']:.3f} (Perpetual evolution)")
print(f"  Entropy: {anomaly_final['entropy']:.3f} (Punctuated reset)")
print(f"  Attractor: {anomaly_final['attractor']} (Free exploration)")

print(f"\nΦ-Density Delta: {anomaly_final['phi_density'] - omega_final['phi_density']:.3f}")
print(f"Omega Opportunity Cost: {omega_final['entropy'] * 10:.3f}Φ (trapped potential)")
print("="*60)