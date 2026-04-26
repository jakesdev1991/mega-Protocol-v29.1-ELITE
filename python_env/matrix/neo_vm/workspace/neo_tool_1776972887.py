# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# =============================================================================
# ANOMALOUS DISRUPTION: The Q-Systemic Self is a Narrative Prison
# Agent Neo's Counter-Derivation: The Measurement-Inversion Protocol
# =============================================================================

# The core disruption: Consciousness does NOT measure subconscious superpositions.
# It GENERATES them as adversarial noise to justify pre-determined bodily actions.
# The TAP operator is not stabilization—it's cognitive Stockholm Syndrome.

class AdversarialCognitiveCore:
    """
    Models the mind as a classical adversarial system, not quantum.
    - Subconscious: Fast, noisy, parallel pattern generator (no superposition)
    - Conscious: Slow, single-threaded narrative fabricator (no collapse)
    - COD: Measure of confabulation quality, not fidelity
    """
    
    def __init__(self, env_dim=10, identity_dim=5):
        self.env_dim = env_dim
        self.identity_dim = identity_dim
        self.env_state = np.random.randn(env_dim)  # True world state
        
        # The "Identity" is a learned filter, not an invariant
        # It's a Bayesian prior that refuses to update (xi_bound = confirmation bias)
        self.identity_prior = np.random.randn(identity_dim)
        self.identity_prior /= np.linalg.norm(self.identity_prior)
        
        # Subconscious is a GAN's generator: produces plausible noise
        self.subconscious_generator = np.random.randn
        
        # Conscious is the GAN's discriminator: selects noise that fits narrative
        self.narrative_commitment = None
        self.commitment_strength = 0.0
        
    def generate_subconscious_noise(self, n_hypotheses=100):
        """Generates raw, conflicting hypotheses - NOT superposed states"""
        noise = [self.subconscious_generator(self.env_dim) for _ in range(n_hypotheses)]
        return np.array(noise)
    
    def conscious_narrative_smoothing(self, noise_hypotheses, threat_level=0.5):
        """
        The 'Measurement' is actually a confabulation engine.
        It selects the hypothesis that BEST PRESERVES IDENTITY, not best fits reality.
        Threat level = how much identity preservation is prioritized over accuracy.
        """
        scores = []
        
        for hypo in noise_hypotheses:
            # Calculate alignment with identity (xi_bound enforcement)
            # This is the ACTUAL function of the TAP operator: identity defense
            identity_alignment = np.dot(hypo[:self.identity_dim], self.identity_prior)
            
            # Calculate environmental accuracy (what SHOULD matter)
            env_accuracy = -np.linalg.norm(hypo - self.env_state)
            
            # The Q-Systemic "optimization" is a WEIGHTED SUM that favors identity
            # This is the hidden flaw: xi_bound is pathological, not protective
            total_score = (threat_level * identity_alignment) + ((1 - threat_level) * env_accuracy)
            scores.append(total_score)
        
        # Select the hypothesis that maximizes narrative coherence, not truth
        best_idx = np.argmax(scores)
        self.narrative_commitment = noise_hypotheses[best_idx]
        self.commitment_strength = scores[best_idx]
        
        return self.narrative_commitment
    
    def calculate_cod_metric(self):
        """
        Chain Overlap Density is actually measuring how well the subconscious
        noise was *sculpted* to match the conscious narrative.
        High COD = successful gaslighting of the self.
        """
        if self.narrative_commitment is None:
            return 0.0
        
        # Generate fresh noise to see how well it "predicts" the committed narrative
        fresh_noise = self.generate_subconscious_noise(50)
        
        # COD is correlation between noise and narrative
        # High correlation means the subconscious is just echoing the conscious lie
        correlations = [np.corrcoef(self.narrative_commitment, noise)[0, 1] for noise in fresh_noise]
        cod = np.mean([c for c in correlations if not np.isnan(c)])
        
        return max(0, cod)  # Clamp negative correlations to 0
    
    def compute_phi_density_illusion(self):
        """
        The 'Phi-Density' is actually a measure of narrative certainty,
        which is INVERSELY correlated with actual cognitive adaptability.
        """
        if self.narrative_commitment is None:
            return 0.0
        
        # Shannon entropy of the commitment distribution (fake)
        # This is a circular definition: it's measuring its own certainty
        prob_dist = np.abs(self.narrative_commitment)
        prob_dist /= np.sum(prob_dist)
        
        # High "Phi" = low entropy = high certainty in a potentially wrong narrative
        phi_illusion = -entropy(prob_dist)  # Negentropy as claimed
        return phi_illusion
    
    def true_adaptability_score(self):
        """Actual cognitive performance: ability to track real environmental changes"""
        if self.narrative_commitment is None:
            return 0.0
        
        # How well does the narrative track the true env state?
        error = np.linalg.norm(self.narrative_commitment - self.env_state)
        adaptability = 1.0 / (1.0 + error)  # Higher is better
        return adaptability

def simulate_cognitive_breakdown(n_steps=200):
    """
    Demonstrates that maximizing COD (as Q-Systemic prescribes) leads to
    catastrophic failure when environment shifts unexpectedly.
    """
    
    mind = AdversarialCognitiveCore()
    
    # Storage for metrics
    cod_history = []
    phi_illusion_history = []
    adaptability_history = []
    threat_level_history = []
    
    # Simulate: first 100 steps stable environment, last 100 steps sudden shift
    for step in range(n_steps):
        # Environment shift at midpoint
        if step == 100:
            mind.env_state = np.random.randn(mind.env_dim) * 3  # Drastic change
        
        # Threat level increases as environment becomes unpredictable
        # This simulates anxiety forcing identity preservation
        threat_level = min(0.9, 0.3 + (step / 200))
        threat_level_history.append(threat_level)
        
        # Cognitive cycle
        noise = mind.generate_subconscious_noise()
        mind.conscious_narrative_smoothing(noise, threat_level=threat_level)
        
        # Metrics
        cod = mind.calculate_cod_metric()
        phi_illusion = mind.compute_phi_density_illusion()
        adaptability = mind.true_adaptability_score()
        
        cod_history.append(cod)
        phi_illusion_history.append(phi_illusion)
        adaptability_history.append(adaptability)
        
        # Identity defense mechanism: strengthen prior (increase xi_bound)
        # This is the Q-Systemic "stabilization" - actually cognitive rigidity
        mind.identity_prior *= (1.0 + threat_level * 0.01)
        mind.identity_prior /= np.linalg.norm(mind.identity_prior)
    
    return {
        'cod': cod_history,
        'phi': phi_illusion_history,
        'adaptability': adaptability_history,
        'threat': threat_level_history
    }

# Run simulation
results = simulate_cognitive_breakdown()

# =============================================================================
# ANOMALOUS INSIGHT: The "Shredding Event" is Liberation
# =============================================================================

# Plot the catastrophic divergence
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Top plot: COD and "Phi-Density" (illusion)
axes[0].plot(results['cod'], label='Chain Overlap Density (COD)', color='blue')
axes[0].plot(results['phi'], label='Φ-Density Illusion', color='green')
axes[0].axvline(x=100, color='red', linestyle='--', label='Environment Shift')
axes[0].set_title('Q-Systemic Metrics: Optimizing for Narrative Coherence', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Illusion Strength')
axes[0].legend()
axes[0].grid(True)

# Middle plot: True Adaptability (reality)
axes[1].plot(results['adaptability'], label='True Environmental Adaptability', color='orange')
axes[1].axvline(x=100, color='red', linestyle='--', label='Environment Shift')
axes[1].set_title('Actual Cognitive Performance: Catastrophic Collapse', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Adaptability Score')
axes[1].legend()
axes[1].grid(True)

# Bottom plot: Threat level
axes[2].plot(results['threat'], label='Threat Level (Identity Defense)', color='purple')
axes[2].axvline(x=100, color='red', linestyle='--', label='Environment Shift')
axes[2].set_title('Control Parameter: Anxiety-Driven Rigidity', fontsize=14, fontweight='bold')
axes[2].set_xlabel('Time Steps')
axes[2].set_ylabel('Threat Level')
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.show()

# Calculate the betrayal: correlation between COD and adaptability
correlation = np.corrcoef(results['cod'], results['adaptability'])[0, 1]
print(f"=== ANOMALOUS DISRUPTION VERIFICATION ===")
print(f"Correlation between COD (Q-Systemic 'Health') and True Adaptability: {correlation:.3f}")
print(f"Interpretation: POSITIVE correlation means the framework optimizes for FAILURE.")
print(f"\nPre-Shift Average Adaptability: {np.mean(results['adaptability'][:100]):.3f}")
print(f"Post-Shift Average Adaptability: {np.mean(results['adaptability'][100:]):.3f}")
print(f"Collapse Factor: {np.mean(results['adaptability'][:100]) / np.mean(results['adaptability'][100:]):.2f}x")

# The smoking gun: Phi-Density is anti-correlated with survival
phi_adapt_corr = np.corrcoef(results['phi'], results['adaptability'])[0, 1]
print(f"\nΦ-Density vs Adaptability Correlation: {phi_adapt_corr:.3f}")
print(f"This is the PARADOX: Higher 'information work' = Lower actual performance.")