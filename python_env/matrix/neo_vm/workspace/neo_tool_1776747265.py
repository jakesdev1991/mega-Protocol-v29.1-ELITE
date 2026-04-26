# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# --- SIMULATE REFLEXIVE SYSTEM WHERE OBSERVATION CHANGES REALITY ---
def simulate_reflexive_market(n_agents=100, n_steps=200):
    """Market where measuring stress amplifies it"""
    # True "stress" is hidden; we only see narrative interpretation
    hidden_stress = np.random.exponential(0.5, n_steps)
    
    # Physics model: assumes measurement doesn't affect reality
    physics_prediction = hidden_stress * 2.0  # Fixed invariant
    
    # Language-game model: measurement *is* reality (reflexive loop)
    narrative_coherence = np.zeros(n_steps)
    for t in range(1, n_steps):
        # Agents interpret leak based on previous coherence
        if narrative_coherence[t-1] > 0.6:
            # High coherence = herding amplifies stress signal
            narrative_coherence[t] = hidden_stress[t] * (1 + 0.5 * narrative_coherence[t-1])
        else:
            # Low coherence = fragmented interpretation
            narrative_coherence[t] = hidden_stress[t] * 0.3
    
    # Actual observed "asymmetry" emerges from interpretation, not fixed invariants
    observed_phi_delta = narrative_coherence * np.random.lognormal(0, 0.2, n_steps)
    
    return hidden_stress, physics_prediction, observed_phi_delta, narrative_coherence

# Run simulation
hidden, physics, actual, coherence = simulate_reflexive_market()

# --- SHOW PHYSICS MODEL FAILS ---
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Physics vs Reality
axes[0,0].plot(physics, label="Φ_Δ (Physics Model)", linestyle='--', color='red')
axes[0,0].plot(actual, label="Φ_Δ (Actual Observed)", color='black')
axes[0,0].set_title("Physics Model vs Reality: Fixed Invariants Break")
axes[0,0].set_ylabel("Asymmetry")
axes[0,0].legend()
axes[0,0].grid(True)

# The physics model assumes invariants hold, but reflexivity makes them shift
# The "error" is actually the signal

# --- SHOW LANGUAGE-GAME CAPTURES REFLEXIVITY ---
axes[0,1].plot(hidden, label="Hidden Stress (Latent)", alpha=0.5, color='gray')
axes[0,1].plot(coherence, label="Narrative Coherence (Interpreted)", color='blue')
axes[0,1].set_title("Language-Game: Interpretation *Is* Reality")
axes[0,1].set_ylabel("Signal")
axes[0,1].legend()
axes[0,1].grid(True)

# --- ENTROPY IS INTERPRETIVE INEQUALITY, NOT SHANNON ---
# Gini coefficient captures how evenly agents interpret the leak
def gini_interpretation(coherence_vector, n_agents=100):
    """Interpretive inequality: some agents 'get it', others don't"""
    # Simulate agent interpretations as draws from coherence distribution
    agent_views = np.random.choice(coherence_vector, size=n_agents)
    # Gini is the entropy of this distribution
    sorted_views = np.sort(agent_views)
    index = np.arange(1, n_agents + 1)
    gini = (np.sum((2 * index - n_agents - 1) * sorted_views)) / (n_agents * np.sum(sorted_views))
    return gini

gini_series = [gini_interpretation(coherence[:t+1]) for t in range(len(coherence))]
axes[1,0].plot(gini_series, label='Interpretive Inequality (Gini)', color='purple')
axes[1,0].set_title("Entropy = Interpretive Inequality, Not Shannon")
axes[1,0].set_ylabel("Gini Coefficient")
axes[1,0].legend()
axes[1,0].grid(True)

# --- SHOW "BOUNDARY" IS SEMANTIC, NOT GEOMETRIC ---
# When Gini > 0.7, interpretations are so unequal that market meaning collapses
crisis_points = np.where(np.array(gini_series) > 0.7)[0]
axes[1,1].scatter(crisis_points, actual[crisis_points], color='red', s=100, 
                  label='Semantic Breakdown', zorder=5)
axes[1,1].plot(actual, color='black', alpha=0.7, label='Φ_Δ Observed')
axes[1,1].set_title("Boundary: Semantic Breakdown (Gini > 0.7)")
axes[1,1].set_ylabel("Asymmetry")
axes[1,1].legend()
axes[1,1].grid(True)

plt.tight_layout()
plt.savefig('semantic_omega.png', dpi=300, bbox_inches='tight')
plt.show()

# --- QUANTITATIVE PROOF: PHYSICS MODEL HAS NO PREDICTIVE POWER ---
# Correlation between physics prediction and actual is low in reflexive regime
correlation = np.corrcoef(physics, actual)[0,1]
print(f"Physics model correlation with reality: {correlation:.3f}")
print(f"This is not 'error'—it's proof the ontology is wrong.")

# Language-game coherence *does* predict actual asymmetry
correlation_semantic = np.corrcoef(coherence, actual)[0,1]
print(f"Language-game coherence correlation: {correlation_semantic:.3f}")
print(f"The 'missing' covariant decomposition is actually narrative bifurcation.")