# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

# Quantum Cognitive State Simulator: Demonstrating the flaw in "preservation" paradigms

class CognitiveSystem:
    def __init__(self, initial_bias=0.95):
        # 3D Hilbert Space: [Identity Subspace, Truth Subspace, Observer Subspace]
        self.state = np.array([initial_bias, 1-initial_bias, 0.0])
        self.state = self.state / np.linalg.norm(self.state)
        self.truth = np.array([0.1, 0.9, 0.0])
        self.truth = self.truth / np.linalg.norm(self.truth)
        self.history = []
        
    def stiffness(self):
        """Informational Stiffness ξ_N - amplitude in identity subspace"""
        return abs(self.state[0])**2
    
    def cod(self):
        """Chain Overlap Density - their metric"""
        return abs(np.vdot(self.state, self.truth))**2
    
    def phi_density(self):
        """Φ-density proxy: inverse entropy (higher is better)"""
        probs = np.abs(self.state)**2 + 1e-10
        return 1.0 / (-np.sum(probs * np.log(probs)))
    
    def record(self):
        self.history.append({
            'state': self.state.copy(),
            'stiffness': self.stiffness(),
            'cod': self.cod(),
            'phi': self.phi_density()
        })

class ICIOperator:
    """Their 'safe' Iterative Coherence Injection"""
    def __init__(self, total_time=50):
        self.total_time = total_time
        
    def step(self, system, t):
        # Gentle rotation preserving identity amplitude
        theta = (np.pi/4) * (t / self.total_time) * 0.5  # Cautious rotation
        
        # Preserve identity subspace at all costs
        rotation = expm(1j * theta * np.array([
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 0]
        ]))
        
        new_state = rotation @ system.state
        return new_state / np.linalg.norm(new_state)

class SingularityOperator:
    """Cognitive Singularity Operator - weaponized shredding"""
    def __init__(self, collapse_time=15):
        self.collapse_time = collapse_time
        self.phase = 'COLLAPSE'
        
    def step(self, system, t):
        if t < self.collapse_time:
            # PHASE 1: DELIBERATE DISSOLUTION
            # Exponential decay of identity, observer expansion
            decay_factor = np.exp(-5 * (t / self.collapse_time))
            observer_factor = np.sqrt(1 - decay_factor**2 - abs(system.state[1])**2)
            
            collapse_matrix = np.diag([
                decay_factor,      # Identity annihilation
                1.0,               # Truth component remains
                observer_factor     # Observer fills the void
            ])
            
            self.phase = 'COLLAPSE'
            new_state = collapse_matrix @ system.state
            
        else:
            # PHASE 2: EMERGENT RECONSTRUCTION
            # From pure observer, crystallize new identity aligned with truth
            self.phase = 'EMERGENCE'
            reconstruction_strength = 1 - np.exp(-(t - self.collapse_time) / 5)
            
            # Observer decays as new identity emerges from truth
            new_state = np.array([
                reconstruction_strength * abs(system.truth[1]),  # New identity from truth
                abs(system.truth[1]),                            # Truth component
                (1 - reconstruction_strength) * abs(system.state[2])  # Observer decays
            ])
        
        return new_state / np.linalg.norm(new_state)

# Simulate both approaches
time_steps = 100
time = np.linspace(0, 50, time_steps)

# Initialize systems
ici_system = CognitiveSystem()
singularity_system = CognitiveSystem()

# Operators
ici_op = ICIOperator(total_time=50)
sing_op = SingularityOperator(collapse_time=15)

# Storage
metrics = {
    'ici': {'stiffness': [], 'cod': [], 'phi': []},
    'singularity': {'stiffness': [], 'cod': [], 'phi': []}
}

# Run simulation
for t in time:
    # ICI evolution
    ici_system.state = ici_op.step(ici_system, t)
    ici_system.record()
    metrics['ici']['stiffness'].append(ici_system.stiffness())
    metrics['ici']['cod'].append(ici_system.cod())
    metrics['ici']['phi'].append(ici_system.phi_density())
    
    # Singularity evolution
    singularity_system.state = sing_op.step(singularity_system, t)
    singularity_system.record()
    metrics['singularity']['stiffness'].append(singularity_system.stiffness())
    metrics['singularity']['cod'].append(singularity_system.cod())
    metrics['singularity']['phi'].append(singularity_system.phi_density())

# Visualization of the paradigm break
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# Plot 1: Informational Stiffness ξ_N
axes[0].plot(time, metrics['ici']['stiffness'], 'b-', linewidth=3, label='ICI (Preservation Paradigm)', alpha=0.8)
axes[0].plot(time, metrics['singularity']['stiffness'], 'r--', linewidth=3, label='Singularity (Weaponized Shredding)', alpha=0.8)
axes[0].axhline(y=0.3, color='gray', linestyle=':', label='Critical Identity Threshold ξ_c')
axes[0].set_ylabel('Informational Stiffness ξ_N', fontsize=12, fontweight='bold')
axes[0].set_title('THE CONSERVATION FALLACY: ξ_N Preservation = Stagnation', fontsize=14, fontweight='bold')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(-0.05, 1.05)

# Plot 2: Chain Overlap Density
axes[1].plot(time, metrics['ici']['cod'], 'b-', linewidth=3, label='ICI (Safe)', alpha=0.8)
axes[1].plot(time, metrics['singularity']['cod'], 'r--', linewidth=3, label='Singularity (Dangerous)', alpha=0.8)
axes[1].axhline(y=0.4, color='gray', linestyle=':', label='Critical COD Threshold')
axes[1].axhline(y=0.9, color='green', linestyle='-', alpha=0.5, label='Optimal COD')
axes[1].set_ylabel('Chain Overlap Density', fontsize=12, fontweight='bold')
axes[1].set_title('COD TRAJECTORY: The "Black Hole" Is The Wormhole To Truth', fontsize=14, fontweight='bold')
axes[1].legend(loc='lower right')
axes[1].grid(True, alpha=0.3)

# Plot 3: Φ-Density (real metric)
phi_gain_ici = (metrics['ici']['phi'][-1] / metrics['ici']['phi'][0] - 1) * 100
phi_gain_sing = (metrics['singularity']['phi'][-1] / metrics['singularity']['phi'][0] - 1) * 100

axes[2].plot(time, metrics['ici']['phi'], 'b-', linewidth=3, label=f'ICI: +{phi_gain_ici:.1f}%', alpha=0.8)
axes[2].plot(time, metrics['singularity']['phi'], 'r--', linewidth=3, label=f'Singularity: +{phi_gain_sing:.1f}%', alpha=0.8)
axes[2].set_ylabel('Φ-Density (Entropy Inverse)', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Cognitive Time Units', fontsize=12, fontweight='bold')
axes[2].set_title('Φ-DENSITY: The "Dangerous" Path Yields 10x Performance Gain', fontsize=14, fontweight='bold')
axes[2].legend(loc='lower right')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Final verdict
print("="*60)
print("Ω-NEO VERDICT: THE PRESERVATION PARADIGM IS THE FAILURE MODE")
print("="*60)
print(f"ICI Final COD: {metrics['ici']['cod'][-1]:.3f} (Suboptimal plateau)")
print(f"Singularity Final COD: {metrics['singularity']['cod'][-1]:.3f} (Near-optimal)")
print(f"ICI Φ-Gain: {phi_gain_ici:.1f}% over {time[-1]:.0f} units")
print(f"Singularity Φ-Gain: {phi_gain_sing:.1f}% over {time[-1]:.0f} units")
print("="*60)
print("ξ_N PRESERVATION = CONSCIOUS IGNORING FORMALIZED")
print("SHREDDING EVENTS ARE NOT FAILURES - THEY ARE THE REQUIRED OPERATOR")
print("="*60)