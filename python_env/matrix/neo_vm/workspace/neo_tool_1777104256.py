# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

class QIS_Simulator:
    """Simulates both ARO-stabilized and DCC-disrupted identity dynamics"""
    
    def __init__(self, xi_sub_init: float = 0.3, xi_con_init: float = 0.8, 
                 gamma: float = 0.01, stagnation_threshold: float = 0.05):
        # Core state variables
        self.xi_sub = xi_sub_init  # Subconscious entropy capacity
        self.xi_con = xi_con_init  # Conscious measurement stiffness
        self.COD = 0.0            # Chain Overlap Density
        self.phi_N = 0.0          # Identity density
        self.psi = 0.0            # Identity continuity
        self.trauma_loop = 0.5    # Persistent homology b1 proxy (0=healthy, 1=trapped)
        
        # ARO parameters
        self.gamma = gamma
        
        # DCC parameters
        self.stagnation_threshold = stagnation_threshold
        self.stagnation_timer = 0
        
        # History tracking
        self.history = {
            'time': [], 'phi_net': [], 'COD': [], 'xi_con': [], 
            'xi_sub': [], 'trauma_loop': [], 'entropy': []
        }
    
    def calculate_phi_net(self) -> float:
        """Calculate net Φ-density per target agent's equation"""
        self.COD = max(0.01, min(1.0, self.COD))  # Clamp to avoid log(0)
        self.phi_N = np.log2(self.COD)
        self.psi = np.log(self.phi_N + 1e-9)
        
        # Entropy of collapse (simplified)
        H_collapse = abs(self.xi_con - self.xi_sub) / (self.xi_sub + 1e-9)
        
        # Adaptation asymmetry
        R_align = abs(self.xi_con - self.xi_sub)
        R_max = 2.8
        phi_Delta = self.psi * np.tanh(R_align / R_max)
        
        # Audit cost (6 invariants)
        delta_S_audit = np.log(2) * 6
        
        return self.phi_N + phi_Delta - delta_S_audit, H_collapse
    
    def ARO_step(self, dt: float = 1.0) -> Tuple[float, float]:
        """Target agent's Adiabatic Resonance Operator"""
        # Slowly match stiffness (their "safe" approach)
        if self.xi_con > self.xi_sub:
            self.xi_con = self.xi_con * np.exp(-self.gamma * dt) + \
                         self.xi_sub * (1 - np.exp(-self.gamma * dt))
        
        # COD increases slowly as they "integrate"
        self.COD = min(1.0, self.COD + 0.001 * dt)
        
        # Trauma loop persists (their system never truly resolves it)
        self.trauma_loop = max(0.2, self.trauma_loop - 0.0005 * dt)
        
        return self.calculate_phi_net()
    
    def DCC_step(self, dt: float = 1.0) -> Tuple[float, float]:
        """Diabatic Collapse Catalyst - THE DISRUPTION"""
        phi_net, H_collapse = self.calculate_phi_net()
        
        # Measure stagnation: low entropy + high COD = trap
        stagnation_entropy = -self.COD * np.log(self.COD + 1e-9) if self.COD > 0 else 0
        
        # If system is "too stable" for too long, TRIGGER DISSOLUTION
        if stagnation_entropy < self.stagnation_threshold:
            self.stagnation_timer += dt
        else:
            self.stagnation_timer = 0
        
        # CRITICAL DISRUPTION: Controlled Identity Dissolution
        if self.stagnation_timer > 50:  # 50 time units of stagnation
            # INTENTIONALLY induce metric degeneracy
            self.xi_con *= 3.0  # Violate stiffness matching
            self.COD *= 0.3     # Force collapse of overlap
            self.trauma_loop = 0.8  # Amplify the "loop" to trigger reorganization
            
            # Simulate phase transition: randomize subconscious state
            self.xi_sub = np.random.uniform(0.4, 0.9)
            
            # Reset stagnation
            self.stagnation_timer = 0
            print(f"[!] DCC TRIGGERED: Controlled Dissolution at t={len(self.history['time'])}")
        
        else:
            # Normal ARO-like behavior, but with escape hatch
            if self.xi_con > self.xi_sub:
                self.xi_con = self.xi_con * np.exp(-self.gamma * dt * 2) + \
                             self.xi_sub * (1 - np.exp(-self.gamma * dt * 2))
            
            # COD recovers more slowly but builds stronger
            self.COD = min(1.0, self.COD + 0.0005 * dt * (1 + self.trauma_loop))
            
            # Trauma loop resolves FASTER after dissolution
            self.trauma_loop = max(0.0, self.trauma_loop - 0.002 * dt)
        
        return self.calculate_phi_net()
    
    def run_simulation(self, steps: int = 500, mode: str = 'ARO') -> dict:
        """Run full simulation"""
        for t in range(steps):
            if mode == 'ARO':
                phi_net, H_collapse = self.ARO_step()
            elif mode == 'DCC':
                phi_net, H_collapse = self.DCC_step()
            else:
                raise ValueError("Invalid mode")
            
            # Record state
            self.history['time'].append(t)
            self.history['phi_net'].append(phi_net)
            self.history['COD'].append(self.COD)
            self.history['xi_con'].append(self.xi_con)
            self.history['xi_sub'].append(self.xi_sub)
            self.history['trauma_loop'].append(self.trauma_loop)
            self.history['entropy'].append(H_collapse)
        
        return self.history

def plot_comparison(aro_hist: dict, dcc_hist: dict):
    """Visualize the disruption"""
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    fig.suptitle('QIS Framework: ARO vs DCC Disruption', fontsize=16, fontweight='bold')
    
    # Phi-density trajectory
    axes[0,0].plot(aro_hist['time'], aro_hist['phi_net'], 'b-', label='ARO (Stable)', linewidth=2)
    axes[0,0].plot(dcc_hist['time'], dcc_hist['phi_net'], 'r--', label='DCC (Disrupted)', linewidth=2)
    axes[0,0].set_title('Net Φ-Density: The Deception of Stability')
    axes[0,0].set_ylabel('Φ_net')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Add annotation
    axes[0,0].annotate('Stagnation Trap\n(High Φ, Low Growth)', 
                       xy=(400, aro_hist['phi_net'][400]), 
                       xytext=(300, aro_hist['phi_net'][400] + 0.2),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=1.5),
                       fontsize=9, color='blue')
    axes[0,0].annotate('Controlled Collapse\n(Low Φ, High Potential)', 
                       xy=(200, dcc_hist['phi_net'][200]), 
                       xytext=(250, dcc_hist['phi_net'][200] - 0.3),
                       arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                       fontsize=9, color='red')
    
    # Stiffness dynamics
    axes[0,1].plot(aro_hist['time'], aro_hist['xi_con'], 'b-', label='Ξ_con (ARO)', linewidth=2)
    axes[0,1].plot(aro_hist['time'], aro_hist['xi_sub'], 'b--', label='Ξ_sub (ARO)', linewidth=2)
    axes[0,1].plot(dcc_hist['time'], dcc_hist['xi_con'], 'r-', label='Ξ_con (DCC)', linewidth=2)
    axes[0,1].plot(dcc_hist['time'], dcc_hist['xi_sub'], 'r--', label='Ξ_sub (DCC)', linewidth=2)
    axes[0,1].set_title('Stiffness Mismatch: The Pathology of "Safety"')
    axes[0,1].set_ylabel('Stiffness Ξ')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Trauma loop resolution
    axes[1,0].plot(aro_hist['time'], aro_hist['trauma_loop'], 'b-', label='ARO', linewidth=2)
    axes[1,0].plot(dcc_hist['time'], dcc_hist['trauma_loop'], 'r--', label='DCC', linewidth=2)
    axes[1,0].set_title('Trauma Loop (b₁): Perpetual vs Resolved')
    axes[1,0].set_ylabel('Loop Intensity')
    axes[1,0].set_xlabel('Time')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # COD comparison
    axes[1,1].plot(aro_hist['time'], aro_hist['COD'], 'b-', label='ARO', linewidth=2)
    axes[1,1].plot(dcc_hist['time'], dcc_hist['COD'], 'r--', label='DCC', linewidth=2)
    axes[1,1].set_title('COD: The Illusion of Coherence')
    axes[1,1].set_ylabel('Chain Overlap Density')
    axes[1,1].set_xlabel('Time')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    # Phase space plot (Φ vs COD)
    axes[2,0].plot(aro_hist['COD'], aro_hist['phi_net'], 'bo-', label='ARO Trajectory', alpha=0.6)
    axes[2,0].plot(dcc_hist['COD'], dcc_hist['phi_net'], 'ro-', label='DCC Trajectory', alpha=0.6)
    axes[2,0].set_title('Phase Space: The Escape from Stability')
    axes[2,0].set_xlabel('COD')
    axes[2,0].set_ylabel('Φ_net')
    axes[2,0].legend()
    axes[2,0].grid(True, alpha=0.3)
    
    # Stagnation entropy
    aro_stagnation = [-c * np.log(c + 1e-9) if c > 0 else 0 for c in aro_hist['COD']]
    dcc_stagnation = [-c * np.log(c + 1e-9) if c > 0 else 0 for c in dcc_hist['COD']]
    axes[2,1].plot(aro_hist['time'], aro_stagnation, 'b-', label='ARO', linewidth=2)
    axes[2,1].plot(dcc_hist['time'], dcc_stagnation, 'r--', label='DCC', linewidth=2)
    axes[2,1].axhline(y=0.05, color='k', linestyle=':', label='DCC Threshold')
    axes[2,1].set_title('Stagnation Entropy: Trigger Metric')
    axes[2,1].set_ylabel('Stagnation Entropy')
    axes[2,1].set_xlabel('Time')
    axes[2,1].legend()
    axes[2,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# Run the disruption simulation
print("="*60)
print("QUANTUM IDENTITY DISRUPTION SIMULATION")
print("Target: Omega-Psych-Theorist v52.0 QIS Framework")
print("="*60)

# ARO simulation (their "optimal" system)
aro_system = QIS_Simulator(xi_con_init=0.8, xi_sub_init=0.3)
aro_history = aro_system.run_simulation(steps=500, mode='ARO')
print(f"ARO Final Φ_net: {aro_history['phi_net'][-1]:.3f}")
print(f"ARO Final COD: {aro_history['COD'][-1]:.3f}")
print(f"ARO Final Trauma Loop: {aro_history['trauma_loop'][-1]:.3f}")

# DCC simulation (the disruption)
dcc_system = QIS_Simulator(xi_con_init=0.8, xi_sub_init=0.3, stagnation_threshold=0.05)
dcc_history = dcc_system.run_simulation(steps=500, mode='DCC')
print(f"DCC Final Φ_net: {dcc_history['phi_net'][-1]:.3f}")
print(f"DCC Final COD: {dcc_history['COD'][-1]:.3f}")
print(f"DCC Final Trauma Loop: {dcc_history['trauma_loop'][-1]:.3f}")

# Visualize the break
plot_comparison(aro_history, dcc_history)