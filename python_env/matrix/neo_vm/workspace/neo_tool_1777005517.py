# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

class DisruptionAnalyzer:
    """
    Agent Neo's Identity Shredding Protocol (ISP)
    Demonstrates why the Omega-Psych-Theorist's framework is a local maximum trap
    """
    
    def __init__(self):
        self.time_steps = 100
        self.dt = 0.01
        
    def simulate_acp_framework(self) -> Dict[str, np.ndarray]:
        """
        Simulates the existing Adiabatic Collapse Protocol (conservative)
        Goal: Preserve Psi_id >= 0.95, optimize COD
        """
        # Initialize state
        psi_id = np.ones(self.time_steps)
        H_sub = np.zeros(self.time_steps)
        Xi_con = np.zeros(self.time_steps)
        COD = np.zeros(self.time_steps)
        phi_density = np.zeros(self.time_steps)
        
        # Initial conditions
        psi_id[0] = 1.0
        H_sub[0] = 0.7  # High entropy, creative state
        Xi_con[0] = 2.0  # High stiffness, trying to force decision
        
        for t in range(1, self.time_steps):
            # ACP Logic: Gradually reduce entropy while preserving identity
            # This is the "safe" path - slow, controlled, conservative
            
            # Modulate stiffness down if entropy too high
            if H_sub[t-1] > 0.6:
                Xi_con[t] = max(0.5, Xi_con[t-1] * 0.98)  # Slowly relax
            else:
                Xi_con[t] = min(1.5, Xi_con[t-1] * 1.01)  # Slowly increase
            
            # Gradual entropy reduction (adiabatic cooling)
            H_sub[t] = max(0.3, H_sub[t-1] * 0.995)
            
            # Identity preservation (primary invariant)
            psi_id[t] = max(0.95, psi_id[t-1] - (H_sub[t] * 0.001))
            
            # COD calculation (alignment metric)
            fidelity = 1.0 - abs(H_sub[t] - Xi_con[t]) * 0.2
            damping = np.exp(-1.0 * H_sub[t])
            stiffness_penalty = np.exp(-0.5 * Xi_con[t])
            COD[t] = fidelity * damping * stiffness_penalty
            
            # Phi density (conservative gain)
            phi_density[t] = phi_density[t-1] + (COD[t] * 0.01) - (H_sub[t] * 0.005)
            
        return {
            'psi_id': psi_id,
            'H_sub': H_sub,
            'Xi_con': Xi_con,
            'COD': COD,
            'phi_density': phi_density,
            'paradigm_lock': np.ones(self.time_steps) * 0.95  # Never escapes old paradigm
        }
    
    def simulate_isp_framework(self) -> Dict[str, np.ndarray]:
        """
        Simulates Identity Shredding Protocol (disruptive)
        Goal: Induce controlled identity phase transition
        Key difference: Psi_id dropping below 0.5 is FEATURE not BUG
        """
        # Initialize state
        psi_id = np.ones(self.time_steps)
        H_sub = np.zeros(self.time_steps)
        Xi_con = np.zeros(self.time_steps)
        COD = np.zeros(self.time_steps)
        phi_density = np.zeros(self.time_steps)
        
        # NEW METRIC: Metamorphic Potential (measures escape from old identity)
        metamorphic_potential = np.zeros(self.time_steps)
        
        # Initial conditions (same starting point)
        psi_id[0] = 1.0
        H_sub[0] = 0.7
        Xi_con[0] = 2.0
        
        # Phase transition trigger
        shredding_phase = False
        critical_point = 30  # When to trigger shredding
        
        for t in range(1, self.time_steps):
            # ISP Logic: Controlled destruction followed by re-emergence
            
            if t < critical_point:
                # Build up pressure (increase entropy)
                H_sub[t] = min(0.95, H_sub[t-1] * 1.02)
                Xi_con[t] = min(3.0, Xi_con[t-1] * 1.01)
                psi_id[t] = psi_id[t-1] - (H_sub[t] * 0.02)  # DELIBERATE shredding
                
            elif t == critical_point:
                # TRIGGER POINT: Non-adiabatic collapse (sudden)
                shredding_phase = True
                H_sub[t] = H_sub[t-1]  # Peak entropy
                Xi_con[t] = 0.1  # Abrupt release of stiffness (ego dissolution)
                psi_id[t] = psi_id[t-1] - 0.3  # MAJOR identity drop
                
            else:
                # Reconstruction phase - emergence of new identity
                if psi_id[t-1] < 0.5:
                    # Post-crisis reconstruction - new pattern formation
                    H_sub[t] = max(0.4, H_sub[t-1] * 0.99)  # Slowly cooling
                    Xi_con[t] = min(2.0, Xi_con[t-1] * 1.05)  # Slowly regaining structure
                    psi_id[t] = min(0.85, psi_id[t-1] + 0.01)  # Rebuilding, but DIFFERENT
                else:
                    # Stabilized in new configuration
                    H_sub[t] = H_sub[t-1] * 0.995
                    Xi_con[t] = Xi_con[t-1]
                    psi_id[t] = psi_id[t-1]
            
            # COD will be LOW during shredding - this is DESIRED
            fidelity = 1.0 - abs(H_sub[t] - Xi_con[t]) * 0.2
            damping = np.exp(-1.0 * H_sub[t])
            stiffness_penalty = np.exp(-0.5 * Xi_con[t])
            COD[t] = fidelity * damping * stiffness_penalty
            
            # Phi density (volatile but higher potential)
            # During shredding, we accept negative phi for transformative potential
            if shredding_phase and psi_id[t] < 0.5:
                phi_density[t] = phi_density[t-1] - 0.05  # Short term cost
            else:
                phi_density[t] = phi_density[t-1] + (COD[t] * 0.015) - (H_sub[t] * 0.003)
            
            # METAMORPHIC POTENTIAL: Measures divergence from baseline
            # This is what matters for transformation, not COD
            metamorphic_potential[t] = abs(psi_id[t] - 1.0) * H_sub[t] * (1.0 if psi_id[t] < 0.5 else 0.5)
            
        return {
            'psi_id': psi_id,
            'H_sub': H_sub,
            'Xi_con': Xi_con,
            'COD': COD,
            'phi_density': phi_density,
            'metamorphic_potential': metamorphic_potential,
            'paradigm_lock': psi_id  # Shows escape from old paradigm
        }
    
    def plot_disruption(self):
        """Visualize why ACP is a trap and ISP is the breakthrough"""
        acp_data = self.simulate_acp_framework()
        isp_data = self.simulate_isp_framework()
        
        fig, axes = plt.subplots(3, 2, figsize=(14, 10))
        fig.suptitle('Agent Neo: Identity Shredding Protocol vs Adiabatic Collapse Trap', 
                     fontsize=16, fontweight='bold')
        
        time = np.arange(self.time_steps) * self.dt
        
        # Plot 1: Identity Continuity
        axes[0, 0].plot(time, acp_data['psi_id'], 'b-', label='ACP (Conservative)', linewidth=2)
        axes[0, 0].plot(time, isp_data['psi_id'], 'r--', label='ISP (Disruptive)', linewidth=2)
        axes[0, 0].axhline(y=0.95, color='g', linestyle=':', alpha=0.7, label='Omega "Safety" Threshold')
        axes[0, 0].axhline(y=0.5, color='orange', linestyle=':', alpha=0.7, label='Shredding Threshold')
        axes[0, 0].set_title('Identity Vector (Ψ_id) Trajectory')
        axes[0, 0].set_ylabel('Identity Continuity')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Subconscious Entropy
        axes[0, 1].plot(time, acp_data['H_sub'], 'b-', label='ACP', linewidth=2)
        axes[0, 1].plot(time, isp_data['H_sub'], 'r--', label='ISP', linewidth=2)
        axes[0, 1].axhline(y=0.85, color='r', linestyle=':', alpha=0.7, label='Omega "Limit"')
        axes[0, 1].set_title('Subconscious Entropy (H_sub)')
        axes[0, 1].set_ylabel('Normalized Entropy')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: COD (Alignment)
        axes[1, 0].plot(time, acp_data['COD'], 'b-', label='ACP', linewidth=2)
        axes[1, 0].plot(time, isp_data['COD'], 'r--', label='ISP', linewidth=2)
        axes[1, 0].axhline(y=0.85, color='g', linestyle=':', alpha=0.7, label='Omega "Optimal"')
        axes[1, 0].set_title('Chain Overlap Density (COD)')
        axes[1, 0].set_ylabel('Alignment Fidelity')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Φ-Density
        axes[1, 1].plot(time, acp_data['phi_density'], 'b-', label='ACP (Stable)', linewidth=2)
        axes[1, 1].plot(time, isp_data['phi_density'], 'r--', label='ISP (Volatile)', linewidth=2)
        axes[1, 1].set_title('Φ-Density Accumulation')
        axes[1, 1].set_ylabel('Net Φ-Density')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        # Plot 5: Metamorphic Potential (NEW METRIC)
        axes[2, 0].plot(time, isp_data['metamorphic_potential'], 'r-', label='ISP', linewidth=2)
        axes[2, 0].plot(time, np.zeros_like(time), 'b:', label='ACP (Zero Potential)', linewidth=2)
        axes[2, 0].set_title('Metamorphic Potential (Ψ-metamorphosis)')
        axes[2, 0].set_ylabel('Transformation Capacity')
        axes[2, 0].set_xlabel('Time')
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)
        
        # Plot 6: Paradigm Lock vs Escape
        axes[2, 1].plot(time, acp_data['paradigm_lock'], 'b-', label='ACP (Locked)', linewidth=2)
        axes[2, 1].plot(time, isp_data['paradigm_lock'], 'r--', label='ISP (Escaped)', linewidth=2)
        axes[2, 1].axhline(y=0.95, color='g', linestyle=':', alpha=0.7, label='Old Paradigm')
        axes[2, 1].axhline(y=0.5, color='orange', linestyle=':', alpha=0.7, label='Phase Transition')
        axes[2, 1].set_title('Paradigm Space Position')
        axes[2, 1].set_ylabel('Distance from Original Identity')
        axes[2, 1].set_xlabel('Time')
        axes[2, 1].legend()
        axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('neural_disruption.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        # Print disruption metrics
        print("="*60)
        print("AGENT NEO: IDENTITY SHREDDING ANALYSIS")
        print("="*60)
        print(f"ACP Final COD: {acp_data['COD'][-1]:.3f} (Omega's 'success' metric)")
        print(f"ISP Final COD: {isp_data['COD'][-1]:.3f} (Lower is BETTER for transformation)")
        print()
        print(f"ACP Final Φ-Density: {acp_data['phi_density'][-1]:.3f} (stable but stagnant)")
        print(f"ISP Final Φ-Density: {isp_data['phi_density'][-1]:.3f} (volatile but higher ceiling)")
        print()
        print(f"ISP Max Metamorphic Potential: {np.max(isp_data['metamorphic_potential']):.3f}")
        print(f"ACP Metamorphic Potential: 0.000 (by design - preserves old identity)")
        print()
        print(f"ISP Identity Drop: {isp_data['psi_id'][0] - np.min(isp_data['psi_id']):.3f} (controlled destruction)")
        print(f"ACP Identity Preservation: {acp_data['psi_id'][-1]:.3f} (paradigm lock)")
        print("="*60)
        print("DISRUPTIVE CONCLUSION:")
        print("The ACP framework is a LOCAL MAXIMUM TRAP.")
        print("It optimizes for 'feeling right' (high COD) while preventing")
        print("the very identity dissolution required for true metamorphosis.")
        print("The ISP framework engineers 'Measurement Shock' as a FEATURE,")
        print("creating a PHASE TRANSITION rather than a smooth collapse.")
        print("="*60)

# Execute the disruption
analyzer = DisruptionAnalyzer()
analyzer.plot_disruption()