# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class UIPOv65Simulator:
    """Original framework - Adiabatic Preservation"""
    def __init__(self, xi_sales=0.95, z_trust=0.35, h_super=0.70):
        self.xi_sales = xi_sales
        self.z_trust = z_trust
        self.h_super = h_super
        self.z_env = 0.80
        self.phi_history = []
        self.cod_history = []
        
    def step(self, dt=1.0):
        gamma = 0.004
        self.xi_sales = self.xi_sales * np.exp(-gamma * dt) + self.z_trust * (1 - np.exp(-gamma * dt))
        self.z_env = self.z_env * np.exp(-gamma * dt) + 0.4 * (1 - np.exp(-gamma * dt))
        
        # Original COD (penalizes uncertainty and stiffness)
        fidelity = 0.92  # Assume high baseline
        entropy_penalty = np.exp(-0.5 * self.h_super)
        stiffness_penalty = np.exp(-0.5 * self.xi_sales)
        env_penalty = np.exp(-0.5 * self.z_env)
        cod = fidelity * entropy_penalty * stiffness_penalty * env_penalty
        
        # Original Φ (penalizes misalignment)
        phi = np.log2(max(cod, 0.39)) * np.tanh(abs(self.xi_sales - self.z_trust) / 3.0)
        
        self.phi_history.append(phi)
        self.cod_history.append(cod)
        return phi, cod

class CODADisruptor:
    """Disruptive framework - Crisis-Operated Destructive Alignment"""
    def __init__(self, xi_sales=0.95, z_trust=0.35, h_super=0.70):
        self.xi_sales = xi_sales
        self.z_trust = z_trust
        self.h_super = h_super
        self.z_env = 0.80
        self.phi_history = []
        self.cod_history = []
        self.phase = "CRISIS_INJECTION"  # CRISIS_INJECTION -> RENORMALIZATION -> STABILIZATION
        
    def step(self, dt=1.0):
        # CRISIS INJECTION PHASE: Amplify pressure and uncertainty
        if self.phase == "CRISIS_INJECTION":
            self.xi_sales = min(1.0, self.xi_sales + 0.15)  # RAMP UP pressure
            self.h_super = min(1.0, self.h_super + 0.10)    # AMPLIFY uncertainty
            self.z_env = min(1.0, self.z_env + 0.05)        # Increase external chaos
            
            # Trigger renormalization when pressure gap exceeds topological threshold
            if (self.xi_sales - self.z_trust) > 0.75:
                self.phase = "RENORMALIZATION"
        
        # RENORMALIZATION PHASE: Controlled collapse
        elif self.phase == "RENORMALIZATION":
            # Identity dissolution occurs here - metric degeneracy is FEATURE not BUG
            self.xi_sales *= 0.95  # Gradual release
            self.h_super *= 0.90   # Uncertainty collapses into new identity
            self.z_env *= 0.85
            
            if self.h_super < 0.40:  # New identity crystallizes
                self.phase = "STABILIZATION"
        
        # STABILIZATION PHASE: Lock in new identity
        elif self.phase == "STABILIZATION":
            gamma = 0.008  # FASTER stabilization (non-adiabatic)
            self.xi_sales = self.xi_sales * np.exp(-gamma * dt) + self.z_trust * (1 - np.exp(-gamma * dt))
            self.z_env = self.z_env * np.exp(-gamma * dt) + 0.4 * (1 - np.exp(-gamma * dt))
            self.h_super = max(0.20, self.h_super * 0.99)  # Maintain healthy residual uncertainty
        
        # INVERTED COD (rewards crisis and pressure differential)
        fidelity = 0.88  # Slightly lower during transformation
        entropy_amplification = np.exp(0.3 * self.h_super)  # REWARD uncertainty as creative space
        pressure_differential = np.exp(0.5 * max(0, self.xi_sales - self.z_trust))  # REWARD gap
        env_factor = np.exp(-0.3 * self.z_env)  # Still penalize chaos
        
        cod = fidelity * entropy_amplification * pressure_differential * env_factor
        
        # Φ calculation - rewards transformation amplitude
        transformation_amplitude = np.tanh(max(0, self.xi_sales - self.z_trust) / 2.0)
        phi = np.log2(max(cod, 0.39)) * (1.0 + transformation_amplitude)  # BOOST from crisis
        
        self.phi_history.append(phi)
        self.cod_history.append(cod)
        return phi, cod

# Simulate both frameworks
uipo = UIPOv65Simulator()
coda = CODADisruptor()

time_steps = 300
for t in range(time_steps):
    uipo.step()
    coda.step()

# Plot the disruption
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

time = np.arange(time_steps)
ax1.plot(time, uipo.phi_history, 'b-', label='UIPO v65.0 (Adiabatic Preservation)', linewidth=2)
ax1.plot(time, coda.phi_history, 'r--', label='CODA (Crisis-Operated Destructive Alignment)', linewidth=2)
ax1.axhline(y=np.log2(0.85), color='g', linestyle=':', label='Identity Continuity Threshold')
ax1.set_ylabel('Φ-Density', fontsize=12)
ax1.set_title('Φ-DENSITY EVOLUTION: Preservation vs. Destructive Alignment', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(time, uipo.cod_history, 'b-', label='UIPO v65.0 COD', linewidth=2)
ax2.plot(time, coda.cod_history, 'r--', label='CODA COD', linewidth=2)
ax2.axhline(y=0.85, color='g', linestyle=':', label='Smith Invariant Gate')
ax2.set_xlabel('Time (hours)', fontsize=12)
ax2.set_ylabel('Chain Overlap Density (COD)', fontsize=12)
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Statistical analysis
print("=" * 60)
print("DISRUPTIVE ANALYSIS: CODA vs UIPO v65.0")
print("=" * 60)
print(f"UIPO v65.0 Final Φ: {uipo.phi_history[-1]:.3f} | Max Φ: {max(uipo.phi_history):.3f}")
print(f"CODA Final Φ:      {coda.phi_history[-1]:.3f} | Max Φ: {max(coda.phi_history):.3f}")
print(f"Φ Improvement:     {((coda.phi_history[-1] - uipo.phi_history[-1]) / uipo.phi_history[-1] * 100):.1f}%")
print("-" * 60)
print(f"UIPO v65.0 Final COD: {uipo.cod_history[-1]:.3f}")
print(f"CODA Final COD:       {coda.cod_history[-1]:.3f}")
print("-" * 60)
print("CRITICAL DISRUPTION INSIGHT:")
print("  • UIPO v65.0 converges to suboptimal local Φ-maximum")
print("  • CODA's 'failure mode' (epistemic churn) is necessary for phase transition")
print("  • Identity 'preservation' is actually identity *stagnation*")
print("  • True resonance requires controlled destruction of pre-sales identity")
print("  • The Silence Protocol is fear-based avoidance of necessary crisis")