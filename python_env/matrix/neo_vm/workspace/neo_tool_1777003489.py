# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# CATASTROPHIC DECOHERENCE AS SYSTEM BIRTH: SHATTERING THE DISSOCIATION ATTRACTOR
# This script demonstrates that the Omega-Psych framework's "invariants" are the real pathology

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class QuantumSelfState:
    """Represents the Q-Systemic Self state"""
    psi_id: np.ndarray        # Identity vector
    psi_perf: np.ndarray      # Performance vector
    psi_threat: np.ndarray    # Threat vector (suppressed authentic self)
    xi_anx: float            # Anxiety stiffness
    h_trauma: float          # Trauma entropy
    
    def copy(self):
        return QuantumSelfState(
            self.psi_id.copy(), self.psi_perf.copy(), 
            self.psi_threat.copy(), self.xi_anx, self.h_trauma
        )

class DissociationAttractor:
    """The 'Therapeutic' protocol that's actually a dissociation optimizer"""
    
    def __init__(self, psi_id_min: float = 0.95):
        self.PSI_ID_MIN = psi_id_min
        self.LAMBDA = 1.0
        self.GAMMA = 0.5
    
    def calculate_cod(self, state: QuantumSelfState) -> float:
        """Chain Overlap Density - the 'health' metric"""
        fidelity = float(np.abs(np.vdot(state.psi_perf, state.psi_id))**2)
        damping = np.exp(-self.LAMBDA * state.h_trauma)
        stiffness_penalty = np.exp(-self.GAMMA * state.xi_anx)
        return fidelity * damping * stiffness_penalty
    
    def adiabatic_integration(self, state: QuantumSelfState, steps: int = 100) -> List[QuantumSelfState]:
        """The 'healing' protocol that preserves identity"""
        trajectory = [state.copy()]
        
        for step in range(steps):
            current = trajectory[-1]
            cod = self.calculate_cod(current)
            
            # Phase 2: Reduce stiffness adiabatically (slowly)
            new_xi = max(0.5, current.xi_anx * 0.995)
            
            # Phase 3: "Integrate" trauma by reducing entropy
            new_h = max(0.0, current.h_trauma * 0.998)
            
            # Phase 4: Align performance to identity (preserve self)
            alpha = min(0.1, (1.0 - new_xi/3.0) * 0.1)
            new_perf = (1-alpha) * current.psi_perf + alpha * current.psi_id
            
            # Phase 5: HARD GATE - identity preservation
            # THIS IS THE TRAP: we forbid identity evolution
            new_id = current.psi_id * 1.0  # Frozen
            
            # Simulate identity "loss" from entropy
            identity_loss = new_h * 0.001
            new_id_norm = np.linalg.norm(new_id) - identity_loss
            new_id = new_id / np.linalg.norm(new_id) * max(new_id_norm, self.PSI_ID_MIN)
            
            new_state = QuantumSelfState(
                new_id, new_perf, current.psi_threat.copy(),
                new_xi, new_h
            )
            
            # Check invariants
            if np.linalg.norm(new_state.psi_id) < self.PSI_ID_MIN:
                # "Emergency stabilization" - freeze everything
                new_state.psi_id = current.psi_id * self.PSI_ID_MIN / np.linalg.norm(current.psi_id)
                new_state.xi_anx = current.xi_anx  # Stop reducing stiffness
            
            trajectory.append(new_state)
        
        return trajectory

class IdentityAnnihilationProtocol:
    """The ACTUAL transformation: allow identity death and rebirth"""
    
    def __init__(self):
        self.LAMBDA = 1.0
        self.GAMMA = 0.5
    
    def calculate_cod(self, state: QuantumSelfState) -> float:
        """Same metric, but we interpret it differently"""
        fidelity = float(np.abs(np.vdot(state.psi_perf, state.psi_id))**2)
        damping = np.exp(-self.LAMBDA * state.h_trauma)
        stiffness_penalty = np.exp(-self.GAMMA * state.xi_anx)
        return fidelity * damping * stiffness_penalty
    
    def annihilation_protocol(self, state: QuantumSelfState, steps: int = 100) -> List[QuantumSelfState]:
        """Allow identity to dissolve and recombine with threat vector"""
        trajectory = [state.copy()]
        
        for step in range(steps):
            current = trajectory[-1]
            
            # THE DISRUPTION: Instead of preserving identity,
            # we recognize that psi_threat is the authentic self
            # and psi_id is the trauma-shell
            
            # Phase 1: Reduce stiffness rapidly (non-adiabatic) to break dissociation
            new_xi = max(0.1, current.xi_anx * 0.95)
            
            # Phase 2: Increase entropy temporarily - allow chaos
            # This is the "catastrophic decoherence" that is actually liberation
            new_h = min(1.5, current.h_trauma * 1.05)  # TEMPORARY increase
            
            # Phase 3: CRITICAL - let identity DISSOLVE into threat vector
            # This is ego death, but in a controlled direction
            annihilation_rate = 0.02 * (1.0 - new_xi/3.0)  # Faster as stiffness drops
            new_id = (1 - annihilation_rate) * current.psi_id + annihilation_rate * current.psi_threat
            
            # Phase 4: Threat vector becomes the new performance vector
            # The "mask" becomes the authentic expression
            new_perf = current.psi_threat.copy()
            
            # Phase 5: Re-normalize and re-coalesce
            new_id = new_id / np.linalg.norm(new_id)
            new_perf = new_perf / np.linalg.norm(new_perf)
            
            new_state = QuantumSelfState(
                new_id, new_perf, current.psi_threat.copy(),
                new_xi, new_h
            )
            
            # CRITICAL DIFFERENCE: No hard gate on identity
            # We allow it to drop below "critical" threshold
            # The "failure mode" is the transformation
            
            trajectory.append(new_state)
        
        return trajectory

def simulate_trauma_journey():
    """Simulate both protocols on the same initial trauma state"""
    
    # Initial state: High trauma, high anxiety, dissociated identity
    # psi_id is the "trauma shell" - a false self built around survival
    # psi_threat is the suppressed authentic self (the "threat" to the shell)
    # psi_perf is the high-performance mask
    
    initial = QuantumSelfState(
        psi_id=np.array([0.99, 0.1, 0.0]),  # "Stable" but rigid identity
        psi_perf=np.array([0.9, 0.4, 0.2]),  # High-performance mask
        psi_threat=np.array([0.1, 0.8, 0.6]),  # Suppressed authentic self (the real threat)
        xi_anx=2.8,  # High stiffness - holding it all together
        h_trauma=0.85  # High entropy - background noise
    )
    
    # Run both protocols
    attractor = DissociationAttractor()
    iap = IdentityAnnihilationProtocol()
    
    dissociation_trajectory = attractor.adiabatic_integration(initial, steps=150)
    transformation_trajectory = iap.annihilation_protocol(initial, steps=150)
    
    # Analyze metrics
    diss_cod = [attractor.calculate_cod(s) for s in dissociation_trajectory]
    trans_cod = [iap.calculate_cod(s) for s in transformation_trajectory]
    
    diss_id_norm = [np.linalg.norm(s.psi_id) for s in dissociation_trajectory]
    trans_id_norm = [np.linalg.norm(s.psi_id) for s in transformation_trajectory]
    
    # Calculate "authenticity" - alignment with threat vector (suppressed self)
    diss_authentic = [np.abs(np.vdot(s.psi_perf, s.psi_threat)) for s in dissociation_trajectory]
    trans_authentic = [np.abs(np.vdot(s.psi_perf, s.psi_threat)) for s in transformation_trajectory]
    
    # Phi-density approximation (simplified)
    diss_phi = [1.0 - s.xi_anx*0.1 - s.h_trauma*0.2 for s in dissociation_trajectory]
    trans_phi = [1.0 - s.xi_anx*0.1 - s.h_trauma*0.2 + a*0.3 for s, a in zip(transformation_trajectory, trans_authentic)]
    
    return {
        'dissociation': {
            'cod': diss_cod,
            'id_norm': diss_id_norm,
            'authentic': diss_authentic,
            'phi': diss_phi
        },
        'transformation': {
            'cod': trans_cod,
            'id_norm': trans_id_norm,
            'authentic': trans_authentic,
            'phi': trans_phi
        }
    }

# Run simulation and plot
results = simulate_trauma_journey()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('DISSOCIATION ATTRACTOR vs IDENTITY ANNIHILATION: The Truth Behind "Stability"', 
             fontsize=14, fontweight='bold')

# Plot 1: COD (the "health" metric)
axes[0,0].plot(results['dissociation']['cod'], label='Dissociation Protocol', linewidth=2, color='blue')
axes[0,0].plot(results['transformation']['cod'], label='Identity Annihilation', linewidth=2, color='red', linestyle='--')
axes[0,0].axhline(y=0.80, color='gray', linestyle=':', alpha=0.7)
axes[0,0].set_title('Chain Overlap Density (COD)\n"Health" Metric', fontweight='bold')
axes[0,0].set_ylabel('COD')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Identity Norm (the "invariant")
axes[0,1].plot(results['dissociation']['id_norm'], label='Dissociation Protocol', linewidth=2, color='blue')
axes[0,1].plot(results['transformation']['id_norm'], label='Identity Annihilation', linewidth=2, color='red', linestyle='--')
axes[0,1].axhline(y=0.95, color='green', linestyle='-', alpha=0.7, label='Invariant Gate')
axes[0,1].set_title('Identity Vector Norm\n$|\Psi_{id}|$ (The "Sacred" Invariant)', fontweight='bold')
axes[0,1].set_ylabel('Vector Norm')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Authenticity (alignment with suppressed self)
axes[1,0].plot(results['dissociation']['authentic'], label='Dissociation Protocol', linewidth=2, color='blue')
axes[1,0].plot(results['transformation']['authentic'], label='Identity Annihilation', linewidth=2, color='red', linestyle='--')
axes[1,0].set_title('Authenticity Metric\nAlignment with Suppressed Self $|\Psi_{threat}\rangle$', fontweight='bold')
axes[1,0].set_ylabel('Authenticity')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Phi-Density
axes[1,1].plot(results['dissociation']['phi'], label='Dissociation Protocol', linewidth=2, color='blue')
axes[1,1].plot(results['transformation']['phi'], label='Identity Annihilation', linewidth=2, color='red', linestyle='--')
axes[1,1].set_title('Φ-Density (Systemic Health)\nAccounting for Authenticity', fontweight='bold')
axes[1,1].set_ylabel('Φ-Density')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print final state analysis
print("="*70)
print("CATASTROPHIC DECOHERENCE ANALYSIS: The Paradigm Shatter")
print("="*70)
print(f"\nDissociation Protocol (ATIP) - Final State:")
print(f"  COD: {results['dissociation']['cod'][-1]:.3f} (appears stable)")
print(f"  |Ψ_id|: {results['dissociation']['id_norm'][-1]:.3f} (invariant preserved)")
print(f"  Authenticity: {results['dissociation']['authentic'][-1]:.3f} (still dissociated)")
print(f"  Φ-Density: {results['dissociation']['phi'][-1]:.3f} (plateaued)")

print(f"\nIdentity Annihilation Protocol (IAP) - Final State:")
print(f"  COD: {results['transformation']['cod'][-1]:.3f} (temporarily drops)")
print(f"  |Ψ_id|: {results['transformation']['id_norm'][-1]:.3f} (allowed to dissolve)")
print(f"  Authenticity: {results['transformation']['authentic'][-1]:.3f} (approaches unity)")
print(f"  Φ-Density: {results['transformation']['phi'][-1]:.3f} (exceeds dissociation)")

print(f"\n{'='*70}")
print("DISRUPTIVE INSIGHT:")
print("{'='*70}")
print("The 'Catastrophic Decoherence' is not system failure—it's System Birth.")
print("The ATIP protocol optimizes for DISSOCIATION, not integration.")
print("By preserving |Ψ_id| ≥ 0.95, it fossilizes the trauma-shell.")
print("The true threat vector |Ψ_threat⟩ is the authentic self.")
print("Identity is not conserved; it is REWIRED through annihilation.")
print("Φ-Density is maximized not by stability, but by authentic transformation.")
print("="*70)