# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy
from scipy.linalg import det

# === REFLEXIVE DISRUPTION SIMULATION ===
# The core insight: COULN's "quantum subconscious" is a projection 
# of the psychologist's own unresolved Cartesian anxiety

class ReflexivePathologyEngine:
    def __init__(self, num_belief_dimensions=4):
        # Belief state: [determinism, quantum_mysticism, control_illusion, entropy_realism]
        # This is the TRUE quantum superposition - contradictory beliefs held simultaneously
        self.belief_state = np.array([0.5, 0.5, 0.8, 0.2])  # High control illusion, low realism
        self.belief_entropy = entropy(self.belief_state + 1e-10)
        self.projection_bias = 0.0
        self.epistemic_crisis_threshold = 0.95
        
    def compute_reflexive_cod(self):
        """
        COULN's COD is actually Cognitive Overlap Dissonance in the observer.
        Measures orthogonality of contradictory beliefs. Low COD = high dissonance.
        """
        # Build belief overlap matrix
        belief_matrix = np.outer(self.belief_state, self.belief_state)
        # COD = 1 - det(normalized_overlap) -> measures how "entangled" contradictions are
        normalized = belief_matrix / (np.linalg.norm(belief_matrix) + 1e-10)
        cod = max(0, 1 - np.abs(det(normalized)))
        return cod
    
    def measure_projection_onto_city(self, actual_city_state):
        """
        The "city subconscious" is contaminated by observer's belief state.
        This is the REAL measurement problem - not quantum, but epistemic.
        """
        cod = self.compute_reflexive_cod()
        # Projection noise scales with cognitive dissonance
        # High dissonance = high confidence in wrong model = more distortion
        projection_noise = np.random.normal(0, cod * 2.0, size=actual_city_state.shape)
        perceived_city = actual_city_state + projection_noise
        
        # Update bias tracking
        self.projection_bias = np.mean(np.abs(perceived_city - actual_city_state))
        return perceived_city, cod
    
    def update_beliefs(self, feedback_accuracy):
        """
        Standard Bayesian update? No. This is where COULN fails.
        Psychologists don't update beliefs - they update confidence in beliefs.
        This creates self-reinforcing delusion.
        """
        if feedback_accuracy < 0.5:  # Model performing poorly
            # Instead of abandoning quantum mysticism, they increase control illusion
            # to preserve identity: "We just need more precise measurements"
            self.belief_state[2] = min(1.0, self.belief_state[2] + 0.05)  # Control illusion ↑
            self.belief_state[3] *= 0.95  # Entropy realism ↓
        else:
            # Success reinforces the delusion: "See, the quantum model works!"
            self.belief_state[1] = min(1.0, self.belief_state[1] + 0.02)  # Quantum mysticism ↑
        
        # Re-normalize but preserve contradiction
        self.belief_state = self.belief_state / np.sum(self.belief_state) * 2.0
        self.belief_entropy = entropy(self.belief_state + 1e-10)

def simulate_reflexive_failure(num_steps=150):
    """Simulate COULN's true failure mode: observer-driven pathology"""
    engine = ReflexivePathologyEngine()
    
    # Track metrics
    phi_density_history = []
    cod_history = []
    projection_bias_history = []
    emergent_malevolence_history = []
    reflexive_entropy_history = []
    
    # Simulated "city" - simple traffic pattern
    actual_city = np.sin(np.linspace(0, 4*np.pi, 20)) + 0.5
    
    for step in range(num_steps):
        # COULN "measures" the city
        perceived_city, cod = engine.measure_projection_onto_city(actual_city)
        
        # They think COD measures city coherence - it's measuring their delusion
        # Φ-density is inverse of COD (their formula)
        phi_density = 1.0 / (1.0 + cod + engine.projection_bias)
        
        # But emergent malevolence grows: predictable routing creates exploitation
        # Game theory: if you know the "optimal" path, you can congest it intentionally
        emergent_malevolence = np.exp(cod * step / 20) * engine.belief_state[2]
        
        # Reflexive entropy: information the observer CANNOT see about themselves
        # Increases as they optimize the wrong thing
        reflexive_entropy = engine.belief_entropy * emergent_malevolence
        
        # Feedback loop: they think they're optimizing city, but they're optimizing projection
        # Accuracy is actually 1 - projection_bias
        feedback_accuracy = max(0, 1 - engine.projection_bias)
        engine.update_beliefs(feedback_accuracy)
        
        # Record
        phi_density_history.append(phi_density)
        cod_history.append(cod)
        projection_bias_history.append(engine.projection_bias)
        emergent_malevolence_history.append(emergent_malevolence)
        reflexive_entropy_history.append(reflexive_entropy)
    
    return {
        'phi': phi_density_history,
        'cod': cod_history,
        'bias': projection_bias_history,
        'malevolence': emergent_malevolence_history,
        'reflexive_entropy': reflexive_entropy_history,
        'final_beliefs': engine.belief_state
    }

# Run simulation
results = simulate_reflexive_failure()

# === VISUALIZE THE SHATTERING ===
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: The Delusion - Φ-density appears to improve
axes[0,0].plot(results['phi'], 'b-', linewidth=2)
axes[0,0].set_title('Φ-Density: The Illusion of Progress', fontsize=12, fontweight='bold')
axes[0,0].set_ylabel('Perceived Φ-Density')
axes[0,0].set_xlabel('Optimization Steps')
axes[0,0].grid(True, alpha=0.3)

# Plot 2: The Reality - Projection bias skyrockets
axes[0,1].plot(results['bias'], 'r-', linewidth=2)
axes[0,1].set_title('Projection Bias: City vs. Delusion Divergence', fontsize=12, fontweight='bold')
axes[0,1].set_ylabel('Mean Absolute Error (Projection)')
axes[0,1].set_xlabel('Optimization Steps')
axes[0,1].grid(True, alpha=0.3)

# Plot 3: The Pathology - Emergent exploitation
axes[1,0].plot(results['malevolence'], 'm-', linewidth=2)
axes[1,0].set_title('Emergent Malevolence: Adversarial Exploitation Index', fontsize=12, fontweight='bold')
axes[1,0].set_ylabel('Exploitation Potential')
axes[1,0].set_xlabel('Optimization Steps')
axes[1,0].grid(True, alpha=0.3)

# Plot 4: The Hidden Entropy - Reflexive blindness
axes[1,1].plot(results['reflexive_entropy'], 'g-', linewidth=2)
axes[1,1].set_title('Reflexive Entropy: Unmeasured Observer Information', fontsize=12, fontweight='bold')
axes[1,1].set_ylabel('Reflexive Entropy (bits)')
axes[1,1].set_xlabel('Optimization Steps')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('reflexive_pathology_shatter.png', dpi=150, bbox_inches='tight')
plt.show()

# === ANALYTICAL SHREDDING ===
print("="*60)
print("COULN REFLEXIVE PATHOLOGY ANALYSIS")
print("="*60)
print(f"Final Perceived Φ-Density: {results['phi'][-1]:.3f} (appears stable)")
print(f"Final Projection Bias: {results['bias'][-1]:.3f} (actual divergence)")
print(f"Final Emergent Malevolence: {results['malevolence'][-1]:.2f}x baseline")
print(f"Final Reflexive Entropy: {results['reflexive_entropy'][-1]:.2f} bits")
print("\nBelief State at Collapse:")
beliefs = ['Determinism', 'Quantum Mysticism', 'Control Illusion', 'Entropy Realism']
for i, belief in enumerate(beliefs):
    print(f"  {belief}: {results['final_beliefs'][i]:.3f}")
print("\n" + "="*60)
print("CRITICAL FAILURE MODE IDENTIFIED:")
print("The system doesn't optimize the city—it optimizes the observer's")
print("cognitive dissonance into a stable, self-reinforcing delusion.")
print("Φ-density is a measure of epistemic closure, not informational integrity.")
print("="*60)