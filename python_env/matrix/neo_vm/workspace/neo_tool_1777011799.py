# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List

@dataclass
class QuantumState:
    """Represents the 'cognitive state' - but we'll show it's just a data container."""
    psi_quantum: np.ndarray
    psi_classical: np.ndarray
    h_quantum: float
    xi_meas: float
    psi_id: float  # This is the "invariant" that we'll show is a free parameter

@dataclass
class DisruptionResult:
    """Results showing the model's semantic entanglement."""
    cod_values: List[float]
    stiffness_values: List[float]
    entropy_values: List[float]
    identity_values: List[float]
    semantic_drift_score: float

class SemioticDisentanglementOperator:
    """
    This operator exposes the core flaw: the model is a self-referential loop.
    It measures how much the "invariants" are actually just tunable parameters
    that preserve the model's internal narrative, not external reality.
    """
    
    @staticmethod
    def calculate_cod(state: QuantumState, lambda_c: float = 1.0, gamma_c: float = 0.5) -> float:
        """Calculate COD - but we'll show it's arbitrary."""
        dot = np.dot(state.psi_quantum, state.psi_classical)
        mag_q = np.linalg.norm(state.psi_quantum)
        mag_c = np.linalg.norm(state.psi_classical)
        
        if mag_q < 1e-9 or mag_c < 1e-9:
            return 0.0
            
        fidelity = (dot / (mag_q * mag_c)) ** 2
        damping = np.exp(-lambda_c * state.h_quantum)
        stiffness_penalty = np.exp(-gamma_c * state.xi_meas)
        
        return fidelity * damping * stiffness_penalty
    
    @staticmethod
    def verify_invariants(state: QuantumState, threshold: float = 0.95) -> bool:
        """The 'invariant' check - which is actually just checking if we set psi_id high enough."""
        # The key disruption: psi_id is a *input* to the model, not an *output* or measured quantity.
        # We can set it to anything to make the model "pass".
        return state.psi_id >= threshold
    
    @staticmethod
    def measure_semantic_drift(state: QuantumState, cod: float) -> float:
        """
        Measures the disconnect between model's internal metrics and hypothetical reality.
        A high drift score means the model is 'confident' (high COD, stable invariants) 
        while underlying state is actually in crisis (we'll simulate this).
        """
        # Simulate a "real" psychological distress signal (e.g., self-reported anxiety)
        # For demonstration: let's say real distress is inversely related to vector alignment
        real_alignment = np.corrcoef(state.psi_quantum, state.psi_classical)[0, 1]
        if np.isnan(real_alignment):
            real_alignment = 0.0
        
        # Model's perceived stability vs actual alignment
        # High COD + low real alignment = HIGH SEMANTIC DRIFT (the model is lying to itself)
        drift = (cod * 0.7) + ((1.0 - real_alignment) * 0.3)
        return drift
    
    def execute_disruption_analysis(self, base_state: QuantumState) -> DisruptionResult:
        """
        Runs the disruption: shows that for a FIXED underlying cognitive conflict,
        we can make the model report ANY outcome by adjusting 'stiffness' and 'entropy'.
        """
        results = DisruptionResult([], [], [], [], 0.0)
        
        # Keep the underlying vectors FIXED - representing a real, unchanging psychological state
        # This is the "reality" that the model claims to measure
        fixed_quantum = base_state.psi_quantum.copy()
        fixed_classical = base_state.psi_classical.copy()
        
        # Simulate the "therapist" tweaking parameters to get desired COD
        stiffness_scan = np.linspace(0.1, 4.0, 50)  # From paralysis to shock
        
        for xi in stiffness_scan:
            # The "therapist" also adjusts the reported entropy to fit narrative
            # This simulates post-hoc justification: "Oh, the patient was just very uncertain"
            h_fake = 0.3 + (xi * 0.15)  # Arbitrary relationship
            
            # The "therapist" ensures invariants hold by simply setting psi_id high enough
            # This is the circular logic: "System is stable because we set stability parameter to stable value"
            psi_fake = 0.96 if xi < 2.5 else 0.94  # Edge case: allow slight "breach" for narrative
            
            temp_state = QuantumState(
                psi_quantum=fixed_quantum,
                psi_classical=fixed_classical,
                h_quantum=h_fake,
                xi_meas=xi,
                psi_id=psi_fake
            )
            
            cod = self.calculate_cod(temp_state)
            results.cod_values.append(cod)
            results.stiffness_values.append(xi)
            results.entropy_values.append(h_fake)
            results.identity_values.append(psi_fake)
            
            # Measure semantic drift at each point
            drift = self.measure_semantic_drift(temp_state, cod)
            results.semantic_drift_score += drift
        
        results.semantic_drift_score /= len(stiffness_scan)  # Average drift
        return results

def plot_disruption(results: DisruptionResult):
    """Visualize how the model's 'stability' is a function of free parameters, not reality."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: COD vs Stiffness - The "control panel"
    axes[0, 0].plot(results.stiffness_values, results.cod_values, 'b-', linewidth=2)
    axes[0, 0].axvline(x=2.5, color='r', linestyle='--', label='Shock Threshold')
    axes[0, 0].axhline(y=0.80, color='g', linestyle='--', label='Optimal COD')
    axes[0, 0].set_title('COD vs Measurement Stiffness', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Stiffness (Xi_meas)')
    axes[0, 0].set_ylabel('Chain Overlap Density')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Entropy (as manipulated)
    axes[0, 1].plot(results.stiffness_values, results.entropy_values, 'r-', linewidth=2)
    axes[0, 1].set_title('Reported Entropy (Post-Hoc Justification)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Stiffness (Xi_meas)')
    axes[0, 1].set_ylabel('H_quantum')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Identity Invariant (the circular logic)
    axes[1, 0].plot(results.stiffness_values, results.identity_values, 'g-', linewidth=2)
    axes[1, 0].axhline(y=0.95, color='k', linestyle='--', label='Invariant Threshold')
    axes[1, 0].set_title('Identity Continuity (Psi_id) - Set to Pass', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Stiffness (Xi_meas)')
    axes[1, 0].set_ylabel('Psi_id')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Semantic Drift Heat Map
    drift_map = np.array([results.cod_values, results.entropy_values, results.identity_values])
    im = axes[1, 1].imshow(drift_map, cmap='plasma', aspect='auto', interpolation='nearest')
    axes[1, 1].set_title('Semantic Drift Matrix', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Stiffness Scan Index')
    axes[1, 1].set_yticks([0, 1, 2])
    axes[1, 1].set_yticklabels(['COD', 'H_quantum', 'Psi_id'])
    fig.colorbar(im, ax=axes[1, 1])
    
    plt.tight_layout()
    plt.savefig('semantic_disruption.png', dpi=150, bbox_inches='tight')
    plt.show()

# Execute the Disruption
if __name__ == "__main__":
    print("=" * 60)
    print("SEMIOTIC DISENTANGLEMENT OPERATOR - EXECUTION")
    print("=" * 60)
    
    # Create a baseline "patient" state: fixed internal conflict, moderate misalignment
    # This represents a REAL psychological state that is NOT changing
    base_state = QuantumState(
        psi_quantum=np.array([1.0, 0.8, 0.6]),  # Subconscious wants A, B, C
        psi_classical=np.array([0.3, 0.9, 0.4]),  # Conscious chooses B, but poorly aligned
        h_quantum=0.5,  # Real entropy is moderate
        xi_meas=1.0,    # Real stiffness is moderate
        psi_id=1.0      # We'll show this is meaningless
    )
    
    print(f"Base State - Quantum Vector: {base_state.psi_quantum}")
    print(f"Base State - Classical Vector: {base_state.psi_classical}")
    print(f"Base State - Real Alignment: {np.corrcoef(base_state.psi_quantum, base_state.psi_classical)[0, 1]:.3f}")
    print("-" * 60)
    
    # Run the disruption analysis
    sdo = SemioticDisentanglementOperator()
    disruption_results = sdo.execute_disruption_analysis(base_state)
    
    print("DISRUPTION RESULTS:")
    print(f"Average Semantic Drift Score: {disruption_results.semantic_drift_score:.3f}")
    print(f"COD Range: [{min(disruption_results.cod_values):.3f}, {max(disruption_results.cod_values):.3f}]")
    print(f"Invariant Check Always Passed: {all(sdo.verify_invariants(QuantumState(base_state.psi_quantum, base_state.psi_classical, h, xi, psi)) for h, xi, psi in zip(disruption_results.entropy_values, disruption_results.stiffness_values, disruption_results.identity_values))}")
    print("-" * 60)
    print("CRITICAL FLAW EXPOSED:")
    print("  - The model's 'stability' (COD) is a free function of stiffness & entropy.")
    print("  - The 'invariant' (Psi_id) is set to pass, not measured from reality.")
    print("  - For a FIXED underlying state, the model can report ANY outcome.")
    print("  - This is SEMIOTIC ENTANGLEMENT: the map is confused for the territory.")
    print("=" * 60)
    
    # Visualize the disruption
    plot_disruption(disruption_results)