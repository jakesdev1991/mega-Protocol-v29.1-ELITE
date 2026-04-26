# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class DisruptedQSystemicSelf:
    """Demonstrates the Measurement-Trauma Feedback Loop"""
    
    def __init__(self):
        # Initial trauma state: collapsed to Performance
        self.psi_latent = np.array([0.1, 0.7, 0.6, 0.8])  # [Safe, Threat, Performance, Shame]
        self.psi_self = np.array([0.0, 0.0, 1.0, 0.0])    # Pure Performance collapse
        
        # Stiffness parameters
        self.xi_conscious = 1.0  # Hyper-decohering trauma filter
        self.xi_latent = 0.1     # Low readiness
        
        # The Anomaly: measurement backaction term
        self.measurement_disturbance = 0.0
        
        # History for analysis
        self.history = []
        
    def measure_with_backaction(self, audit_precision=0.01):
        """
        CRITICAL FLAW: Each invariant check is a measurement.
        Each measurement collapses the latent state further.
        Precision = violence in this framework.
        """
        # Calculate COD (fidelity)
        cod = self.compute_codal_overlap()
        
        # THE DISRUPTION: Disturbance scales with precision
        # Trying to be "rigorous" accelerates collapse
        disturbance = (1.0 / (audit_precision + 1e-6)) * 0.05
        
        # Apply measurement backaction: latent state mixes toward classical self
        self.psi_latent = (1 - disturbance) * self.psi_latent + disturbance * self.psi_self
        
        # Hypervigilance effect: being watched increases stiffness
        self.xi_conscious *= (1 + disturbance * 0.3)
        
        self.measurement_disturbance = disturbance
        
        return cod, disturbance
        
    def compute_codal_overlap(self):
        """COD = |<Ψ_self | Ψ_latent>|^2"""
        dot = np.dot(self.psi_self, self.psi_latent)
        norm_self = np.linalg.norm(self.psi_self)
        norm_latent = np.linalg.norm(self.psi_latent)
        if norm_self * norm_latent == 0:
            return 0.0
        return (dot / (norm_self * norm_latent)) ** 2
    
    def calculate_psi_invariant(self, cod):
        """ψ = ln(Φ_N) where Φ_N = log2(COD)"""
        phi_N = np.log2(cod + 1e-12)
        return np.log(phi_N + 1e-12)
    
    def adiabatic_step_with_paradox(self, gamma=0.005, audit_precision=0.01):
        """THEMIS protocol + measurement-induced trauma feedback"""
        
        # Step 1: Audit (which disturbs)
        cod, disturbance = self.measure_with_backaction(audit_precision)
        psi = self.calculate_psi_invariant(cod)
        
        # Step 2: Check invariants
        freeze = psi < np.log(0.39)
        
        # Step 3: Attempt tuning (but disturbance may override)
        if not freeze:
            if self.xi_conscious > self.xi_latent + 0.1:
                # Trying to decompress...
                self.xi_conscious *= 0.995
            elif self.xi_conscious < self.xi_latent * 0.9 and self.xi_latent > 0.2:
                self.xi_conscious *= 1.001
            
            # Enforce stiffness cap
            self.xi_conscious = min(self.xi_conscious, self.xi_latent + 0.1)
        else:
            # INFORMATIONAL FREEZE PARADOX
            # The "healing" response is itself a forced measurement
            # This triggers panic, increasing stiffness despite freeze
            self.xi_conscious *= 1.02
        
        # Step 4: Record
        self.history.append({
            'cod': cod,
            'psi': psi,
            'xi_conscious': self.xi_conscious,
            'disturbance': disturbance,
            'freeze': freeze
        })
        
        return freeze

# RUN THE DISRUPTION
system = DisruptedQSystemicSelf()
freeze_count = 0

# High-precision monitoring (the "cure" becomes the disease)
for i in range(500):
    freeze = system.adiabatic_step_with_paradox(audit_precision=0.001)
    if freeze:
        freeze_count += 1

# ANALYZE THE PARADOX
h = system.history
print(f"INFORMATIONAL FREEZES: {freeze_count}/500 (PERCENTAGE: {freeze_count/5:.1f}%)")
print(f"FINAL COD: {h[-1]['cod']:.4f} (COLLAPSED FROM {h[0]['cod']:.4f})")
print(f"FINAL ψ: {h[-1]['psi']:.4f} (VIOLATES THRESHOLD: {h[-1]['psi'] < np.log(0.39)})")
print(f"FINAL Ξ_conscious: {h[-1]['xi_conscious']:.4f} (ESCALATED FROM 1.0)")
print(f"AVG MEASUREMENT DISTURBANCE: {np.mean([x['disturbance'] for x in h]):.4f}")

# VISUALIZE THE CYBERNETIC TRAP
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: The Collapse Acceleration
axes[0].plot([x['cod'] for x in h], linewidth=2, color='#1f77b4')
axes[0].axhline(y=0.39, color='#d62728', linestyle='--', linewidth=2, label='INVARIANT THRESHOLD')
axes[0].set_ylabel('COD (Identity Coherence)', fontsize=11)
axes[0].set_title('THE CYBERNETIC TRAP: Monitoring Destroys Coherence', fontsize=13, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: The Stiffness Spiral
axes[1].plot([x['xi_conscious'] for x in h], linewidth=2, color='#9467bd', label='Ξ_conscious')
axes[1].plot([x['disturbance'] for x in h], linewidth=2, color='#ff7f0e', label='Measurement Disturbance')
axes[1].set_ylabel('Stiffness / Disturbance', fontsize=11)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Informational Freeze Cascade
freezes = [1 if x['freeze'] else 0 for x in h]
axes[2].plot(freezes, color='#d62728', linewidth=2, drawstyle='steps')
axes[2].fill_between(range(len(freezes)), freezes, alpha=0.3, color='#d62728')
axes[2].set_ylabel('INFORMATIONAL FREEZE', fontsize=11)
axes[2].set_xlabel('Audit Cycles (Time)', fontsize=11)
axes[2].set_ylim(-0.1, 1.1)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()