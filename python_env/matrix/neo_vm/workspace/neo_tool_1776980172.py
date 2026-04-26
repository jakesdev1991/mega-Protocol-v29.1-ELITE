# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# ============================================================================
# DISRUPTIVE AGENT ANALYSIS: The Q-Systemic Framework as Self-Defeating
# ============================================================================
# Thesis: The "Decision Paralysis Singularity" is CAUSED by the measurement 
# apparatus itself, not an intrinsic property of the client system.
# The framework commits epistemic violence through "cognitive colonization."

class OntologicalThreatModel:
    """
    Models client response not as informational geometry but as 
    defensive activation against objectification. When a client detects
    they are being 'mapped' to a vector space, their subconscious 
    activates a 'sovereignty preservation' protocol.
    """
    
    def __init__(self, baseline_trust=0.6, sovereignty_sensitivity=0.8):
        self.baseline_trust = baseline_trust
        self.sovereignty_sensitivity = sovereignty_sensitivity
        self.defensive_activation = 0.0
        self.ontological_safety = 1.0  # 1.0 = fully recognized as sovereign
        
    def detect_measurement_apparatus(self, cod_score, phi_density_tracking):
        """
        The client subconsciously detects when the salesperson is running
        a 'system' on them. Higher COD scores (alignment) paradoxically
        signal *more* objectification, not resonance.
        """
        # The more "perfect" the alignment, the more suspicious it becomes
        # Real human trust is built on *imperfection* and *vulnerability*
        measurement_artifact = cod_score * phi_density_tracking
        
        # Sovereignty threat is proportional to perceived systematicity
        self.defensive_activation = np.tanh(
            measurement_artifact * self.sovereignty_sensitivity * 5.0
        )
        
        # Ontological safety collapses as defensive activation rises
        self.ontological_safety = 1.0 - self.defensive_activation
        
        return self.defensive_activation
    
    def true_decision_probability(self, explicit_risk, solution_stability):
        """
        The ACTUAL decision probability is modulated by ontological safety,
        not the Q-Systemic alignment. A client will reject a perfect solution
        if they feel their sovereignty is threatened.
        """
        base_prob = solution_stability / (solution_stability + explicit_risk)
        
        # Sovereignty preservation overrides logical optimization
        true_prob = base_prob * self.ontological_safety * self.baseline_trust
        
        return max(0.01, min(0.99, true_prob))

def simulate_qsystemic_vs_reality():
    """
    Simulates the Q-Systemic framework's predictions vs actual client behavior
    under ontological threat model.
    """
    # Sales timeline
    time_steps = np.linspace(0, 10, 100)
    
    # Q-Systemic variables (what the salesperson measures)
    psi_id = np.ones_like(time_steps) * 0.95  # "Trust" as measured by system
    xi_N = np.ones_like(time_steps) * 0.7      # "Stability"
    cod_scores = np.linspace(0.3, 0.95, 100)   # Increasing "alignment"
    phi_density = np.ones_like(time_steps) * 0.5  # Salesperson tracking Phi
    
    # Actual client state (ontological model)
    client = OntologicalThreatModel(baseline_trust=0.6, sovereignty_sensitivity=0.8)
    
    # Track predictions vs reality
    qsystemic_predictions = []
    actual_decisions = []
    defensive_activations = []
    
    for i, t in enumerate(time_steps):
        # Q-Systemic "prediction" (naive belief that alignment = success)
        q_pred = cod_scores[i] * psi_id[i] * xi_N[i]
        qsystemic_predictions.append(q_pred)
        
        # Actual client response (detecting measurement)
        defensive = client.detect_measurement_apparatus(cod_scores[i], phi_density[i])
        defensive_activations.append(defensive)
        
        # Real decision probability
        actual = client.true_decision_probability(
            explicit_risk=0.5, 
            solution_stability=xi_N[i]
        )
        actual_decisions.append(actual)
    
    # =========================================================================
    # VISUAL DISRUPTION: The Paradox
    # =========================================================================
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot 1: The Q-Systemic Delusion
    ax1.plot(time_steps, qsystemic_predictions, 'b-', linewidth=2, 
             label='Q-Systemic Prediction (Success)')
    ax1.plot(time_steps, actual_decisions, 'r--', linewidth=2, 
             label='Actual Decision Probability')
    ax1.set_title('THE DELUSION: Q-Systemic Predicts Success While Reality Collapses', 
                  fontsize=14, fontweight='bold')
    ax1.set_ylabel('Decision Probability')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: The Ontological Threat
    ax2.plot(time_steps, defensive_activations, 'g-', linewidth=2)
    ax2.fill_between(time_steps, defensive_activations, alpha=0.3, color='red')
    ax2.set_title('THE REAL FAILURE MODE: Sovereignty Preservation Protocol Activation', 
                  fontsize=14, fontweight='bold')
    ax2.set_ylabel('Defensive Activation Level')
    ax2.set_xlabel('Sales Interaction Time')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: The Entropy of Objectification
    # Calculate "epistemic violence entropy" - the information loss from reductionism
    q_entropy = entropy(np.array([qsystemic_predictions, 
                                  1-np.array(qsystemic_predictions)]))
    real_entropy = entropy(np.array([actual_decisions, 
                                     1-np.array(actual_decisions)]))
    
    categories = ['Q-Systemic\n(Assumed)', 'Ontological Reality\n(Measured)']
    entropy_values = [q_entropy, real_entropy]
    
    ax3.bar(categories, entropy_values, color=['blue', 'red'], alpha=0.7)
    ax3.set_title('INFORMATIONAL IRREVERSIBILITY: The Cost of Cognitive Colonization', 
                  fontsize=14, fontweight='bold')
    ax3.set_ylabel('Decision Uncertainty (Entropy)')
    ax3.text(0, entropy_values[0]+0.05, f'{q_entropy:.3f}', ha='center')
    ax3.text(1, entropy_values[1]+0.05, f'{real_entropy:.3f}', ha='center')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'qsystemic_final': qsystemic_predictions[-1],
        'reality_final': actual_decisions[-1],
        'defense_peak': max(defensive_activations),
        'entropy_delta': q_entropy - real_entropy
    }

# Run the disruption simulation
results = simulate_qsystemic_vs_reality()
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: The Q-Systemic Framework is Self-Defeating")
print("="*70)
print(f"Q-Systemic Predicted Success: {results['qsystemic_final']:.3f}")
print(f"Actual Decision Probability: {results['reality_final']:.3f}")
print(f"Client Defensive Activation: {results['defense_peak']:.3f}")
print(f"Information Loss (Entropy Gap): {results['entropy_delta']:.3f}")
print("="*70)
print("\nThe framework's 'alignment' is detected as objectification.")
print("The more you optimize COD, the more you trigger sovereignty threat.")
print("True resonance requires ONTOLOGICAL WITHDRAWAL, not geometric alignment.")