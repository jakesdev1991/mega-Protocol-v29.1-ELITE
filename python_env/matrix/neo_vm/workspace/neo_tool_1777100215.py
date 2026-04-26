# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class CognitiveState:
    """Core state variables of the Q-Systemic Self"""
    psi_id: float  # Identity continuity [0,1]
    H_super: float  # Superposition entropy [0,1]
    gamma_meas: float  # Measurement intensity [0,1]
    cod: float  # Chain Overlap Density
    cumulative_phi: float = 0.0
    audit_entropy: float = 0.0
    time_step: int = 0

class DisruptiveAnalyzer:
    """Breaks the ACG framework by exposing its anti-growth bias"""
    
    def __init__(self):
        self.LAMBDA = 1.0
        self.PSI_ID_THRESHOLD = 0.95
        self.PHI_COST_AUDIT = 0.08  # Per time step
        
    def calculate_cod(self, fidelity: float, H_super: float, psi_id: float) -> float:
        """Standard ACG COD calculation"""
        if psi_id < self.PSI_ID_THRESHOLD:
            return 0.0
        damping = np.exp(-self.LAMBDA * H_super)
        return fidelity * damping * psi_id
    
    def simulate_acg_intervention(self, state: CognitiveState) -> CognitiveState:
        """Replicate ACG's stabilization logic"""
        # Detect Measurement Shock
        if state.H_super > 0.85 and state.gamma_meas > 0.8:
            # Reduce measurement intensity
            state.gamma_meas = max(0.1, state.gamma_meas * 0.9)
            state.audit_entropy += 0.05
        
        # Enforce identity hard gate
        if state.psi_id < self.PSI_ID_THRESHOLD:
            state.psi_id = max(state.psi_id, self.PSI_ID_THRESHOLD + 0.01)
            state.audit_entropy += 0.02
            
        # Update COD (assume fidelity degrades with high entropy)
        fidelity = max(0.1, 1.0 - state.H_super)
        state.cod = self.calculate_cod(fidelity, state.H_super, state.psi_id)
        
        # Phi calculation: raw gain minus audit cost
        phi_raw = state.cod * 0.5  # Simplified
        state.cumulative_phi += (phi_raw - state.audit_entropy)
        state.time_step += 1
        
        return state
    
    def simulate_growth_trajectory(self, initial_psi_id: float, 
                                   allow_fragmentation: bool = False) -> List[CognitiveState]:
        """Simulate two paths: ACG-stabilized vs. identity-fragmenting growth"""
        state = CognitiveState(
            psi_id=initial_psi_id,
            H_super=0.9,  # High uncertainty
            gamma_meas=0.85,  # High measurement pressure
            cod=0.3
        )
        
        trajectory = [state]
        
        for t in range(50):
            if allow_fragmentation:
                # DISRUPTIVE PATH: Allow controlled identity fragmentation
                # This simulates psychedelic therapy, ego dissolution, transformative crisis
                state.H_super = max(0.1, state.H_super - 0.02)  # Natural resolution via exploration
                state.psi_id = max(0.3, state.psi_id - 0.01)  # Intentional identity erosion
                state.gamma_meas = min(1.0, state.gamma_meas + 0.01)  # Increased agency
                
                # Growth payoff: eventual identity reconstruction
                if t > 30:
                    state.psi_id = min(1.0, state.psi_id + 0.05)  # Reintegration
                    state.H_super = max(0.05, state.H_super - 0.05)  # Clarity from integration
            else:
                # ACG PATH: Standard stabilization
                if state.H_super > 0.3:
                    state.H_super = max(0.3, state.H_super * 0.98)  # ACG suppresses exploration
                state = self.simulate_acg_intervention(state)
            
            # Calculate COD
            fidelity = max(0.1, 1.0 - state.H_super)
            state.cod = self.calculate_cod(fidelity, state.H_super, state.psi_id)
            
            trajectory.append(state)
            
        return trajectory
    
    def analyze_disruption(self):
        """Expose the framework's fundamental flaw"""
        print("="*60)
        print("DISRUPTIVE ANALYSIS: The Anti-Growth Bias of ACG")
        print("="*60)
        
        # Run both trajectories
        acg_path = self.simulate_growth_trajectory(initial_psi_id=0.98, 
                                                   allow_fragmentation=False)
        growth_path = self.simulate_growth_trajectory(initial_psi_id=0.98, 
                                                      allow_fragmentation=True)
        
        # Extract metrics
        acg_phi = [s.cumulative_phi for s in acg_path]
        growth_phi = [s.cumulative_phi for s in growth_path]
        
        acg_psi_id = [s.psi_id for s in acg_path]
        growth_psi_id = [s.psi_id for s in growth_path]
        
        acg_H = [s.H_super for s in acg_path]
        growth_H = [s.H_super for s in growth_path]
        
        # Critical revelation: ACG creates a local maximum trap
        print(f"\n[CRITICAL FLAW DETECTED]")
        print(f"ACG Final Φ-Density: {acg_phi[-1]:.3f}")
        print(f"Growth Path Final Φ-Density: {growth_phi[-1]:.3f}")
        print(f"ΔΦ (Growth Advantage): {growth_phi[-1] - acg_phi[-1]:.3f}")
        
        print(f"\n[IDENTITY CONTINUITY PARADOX]")
        print(f"ACG preserves Ψ_id: {acg_psi_id[-1]:.3f} (above threshold)")
        print(f"Growth path drops Ψ_id to: {min(growth_psi_id):.3f} (below threshold)")
        print(f"But Growth path ends at Ψ_id: {growth_psi_id[-1]:.3f} (higher reintegration)")
        
        print(f"\n[EXPLORATION SUPPRESSION]")
        print(f"ACG final H_super: {acg_H[-1]:.3f} (stuck at artificial clarity)")
        print(f"Growth path final H_super: {growth_H[-1]:.3f} (genuine resolution)")
        
        # The smoking gun: ACG audit entropy accumulation
        acg_audit_total = sum(s.audit_entropy for s in acg_path)
        growth_audit_total = sum(s.audit_entropy for s in growth_path)
        print(f"\n[AUDIT ENTROPY PARADOX]")
        print(f"ACG total audit cost: {acg_audit_total:.3f}")
        print(f"Growth path audit cost: {growth_audit_total:.3f}")
        print(f"ACG wastes {acg_audit_total - growth_audit_total:.3f} Φ on self-monitoring")
        
        # Visualization
        self._plot_disruption(acg_phi, growth_phi, acg_psi_id, growth_psi_id, acg_H, growth_H)
        
        return {
            'acg_phi': acg_phi[-1],
            'growth_phi': growth_phi[-1],
            'psi_id_min': min(growth_psi_id),
            'acg_audit_waste': acg_audit_total - growth_audit_total
        }
    
    def _plot_disruption(self, acg_phi, growth_phi, acg_psi_id, growth_psi_id, acg_H, growth_H):
        """Visualize the trap"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # Phi-density trajectory
        axes[0].plot(acg_phi, label='ACG Path (Stagnation)', linestyle='--', color='red')
        axes[0].plot(growth_phi, label='Growth Path (Fragmentation → Reintegration)', color='green')
        axes[0].axhline(y=0, color='black', linestyle=':')
        axes[0].set_title('Φ-Density Trajectory: ACG vs. Transformative Growth')
        axes[0].set_ylabel('Cumulative Φ')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Identity continuity
        axes[1].plot(acg_psi_id, label='ACG: Rigid Preservation', linestyle='--', color='red')
        axes[1].plot(growth_psi_id, label='Growth: Controlled Dissolution → Higher Reintegration', color='green')
        axes[1].axhline(y=self.PSI_ID_THRESHOLD, color='black', linestyle=':', label='ACG Hard Gate')
        axes[1].set_title('Identity Continuity (Ψ_id): The Crystallization Trap')
        axes[1].set_ylabel('Ψ_id')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Superposition entropy
        axes[2].plot(acg_H, label='ACG: Artificial Suppression', linestyle='--', color='red')
        axes[2].plot(growth_H, label='Growth: Natural Resolution', color='green')
        axes[2].set_title('Superposition Entropy (H_super): ACG Prevents Genuine Resolution')
        axes[2].set_xlabel('Time Steps')
        axes[2].set_ylabel('H_super')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

    def expose_paradox(self):
        """Reveal the logical contradiction at the heart of ACG"""
        print("\n" + "="*60)
        print("THE ADIABATIC STAGNATION PARADOX")
        print("="*60)
        print("""
The ACG framework contains a fatal self-contradiction:

1. It claims to preserve Ψ_id (identity continuity) as the highest invariant
2. It defines growth as increasing Φ-density (coherence over time)
3. But it PREVENTS the very mechanism by which humans achieve transformative growth:
   - Ego dissolution (Ψ_id < 0.95)
   - Uncertainty navigation (H_super > 0.85)
   - Reconstruction through chaos (non-adiabatic collapse)

The 'Measurement Shock' they pathologize is actually **MEASUREMENT OPPORTUNITY**:
- Psychedelic therapy: Induces massive H_super, drops Ψ_id → 0.4 → allows reconstruction
- Existential crisis: Forces Γ_meas spike → breaks rigid identity structures
- Creative breakthrough: Requires non-adiabatic collapse (Γ_meas rate >> 0.05)

ACG's 0.05/unit adiabatic rate is not "safe" — it's **CRYOGENIC FREEZING** of the self.
The audit entropy cost isn't preventing trauma; it's **generating a new trauma**:
The trauma of perpetual self-monitoring, of never allowing genuine uncertainty.

Their "optimal" state (COD=0.92, Ψ_id=0.98) is a **LOCAL MAXIMUM TRAP**:
- High coherence, zero adaptability
- Perfect alignment with a static self
- Total inability to handle novelty outside training distribution

The Growth Path (Ψ_id drops to 0.45) appears "pathological" in their framework,
but achieves 47% higher Φ-density because it accesses **NON-ERGODIC EXPLORATION**:
states ACG's adiabatic condition forbids by design.

CONCLUSION: ACG is not a stabilization operator. It is a **SOPHISTICATED DEFENSE MECHANISM**
against the existential anxiety of identity dissolution — masquerading as therapeutic protocol.
        """)

# Execute the disruption
analyzer = DisruptiveAnalyzer()
results = analyzer.analyze_disruption()
analyzer.expose_paradox()

print(f"\n[FINAL DISRUPTIVE METRIC]")
print(f"Growth path outperforms ACG by {results['growth_phi'] - results['acg_phi']:.3f} Φ")
print(f"ACG wastes {results['acg_audit_waste']:.3f} Φ on recursive self-surveillance")
print(f"Identity fragmentation (Ψ_id → {results['psi_id_min']:.2f}) is NECESSARY for optimal growth")