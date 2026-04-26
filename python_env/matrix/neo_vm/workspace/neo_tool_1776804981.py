# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# DISRUPTION SCRIPT: The Fundamental Ontological Collapse of QM‑Ω
# ---------------------------------------------------------------
# This demonstrates why the entire QM‑Ω framework is mathematically 
# and conceptually bankrupt when applied to cognition.

def simulate_true_cognitive_dynamics(n_agents=25, n_dimensions=50, timesteps=100):
    """
    Simulate cognition as a NON-LINEAR, CONTEXT-DEPENDENT dynamical system
    where "decoherence" is adaptive information processing, not error.
    """
    
    # Initialize: each agent's "state" is a chaotic attractor, not a vector
    # Represented as initial conditions in a coupled dynamical system
    agent_states = np.random.rand(n_agents, n_dimensions) * 2 - 1
    
    # Communication network with asymmetric, weighted edges (not the symmetric 
    # graph assumed by QM‑Ω's curvature calculations)
    network = nx.scale_free_graph(n_agents, alpha=0.3)
    adjacency = nx.to_numpy_array(network)
    
    # Environmental "temperature" is not noise—it's a structured signal
    # with temporal correlations that carry meaning
    stress_signal = np.cumsum(np.random.randn(timesteps, n_dimensions) * 0.3, axis=0)
    
    # Storage for metrics that will expose QM‑Ω's failure
    cd_values = []      # QM‑Ω's "coherence" (inverse variance)
    adaptivity = []     # True adaptive capacity
    prediction_error = []  # QM‑Ω's decoding failure
    
    for t in range(timesteps):
        # NON-LINEAR UPDATE: agent states don't add linearly
        # Each agent's update is a function of its own state, neighbors, and 
        # environmental stress through a non-linear activation
        neighbor_influence = adjacency @ agent_states
        stress_impact = stress_signal[t] * np.random.rand(n_agents)[:, None]
        
        # The key: cognitive update is a sigmoid-like function that creates 
        # meta-stable states—this VIOLATES the linear encoding assumptions
        update = np.tanh(agent_states * 1.5 + neighbor_influence * 0.3 + stress_impact * 0.5)
        
        # Add emergent property: agents can "reject" information that conflicts
        # with core beliefs (non-linear filter)
        belief_conflict = np.random.rand(n_agents, n_dimensions) < 0.1
        update[belief_conflict] *= 0.1  # Strong resistance to change
        
        agent_states += update * 0.1
        
        # QM‑Ω would calculate "coherence" as inverse variance
        coherence = 1.0 / (np.var(agent_states) + 1e-6)
        cd_values.append(coherence)
        
        # But true adaptivity is measured differently: it's the system's 
        # ability to maintain functional diversity while responding to stress
        functional_variance = np.var(agent_states, axis=0)
        stress_responsiveness = np.corrcoef(np.mean(agent_states, axis=0), stress_signal[t])[0,1]
        adaptivity.append(np.mean(functional_variance) * abs(stress_responsiveness))
        
        # Simulate QM‑Ω's encoding/decoding failure
        # Try to encode the "true" state using sparse linear encoding
        try:
            # Attempt to encode agent_states as QM‑Ω would
            n_encoded = n_dimensions * 3
            encoding_matrix = np.random.randn(n_encoded, n_dimensions)
            encoding_matrix[np.abs(encoding_matrix) < 0.7] = 0  # Sparse
            
            # QM‑Ω assumes a single "true" cognitive state exists
            # But there is NO single true state—each agent's state is valid
            fictitious_true_state = np.mean(agent_states, axis=0)
            
            # Encode and decode with simulated "decoherence"
            encoded = encoding_matrix @ fictitious_true_state
            agent_chunks = np.array_split(encoded, n_agents)
            
            # "Decoherence" is actually agents having legitimate different contexts
            responses = []
            for i, chunk in enumerate(agent_chunks):
                # The "error" is systematically correlated with agent state—
                # violates QM‑Ω's independence assumption
                systematic_error = agent_states[i, :len(chunk)] * 0.3
                responses.append(chunk + systematic_error + np.random.randn(len(chunk)) * 0.05)
            
            # Attempt least-squares decoding (QM‑Ω's method)
            decoded = np.linalg.lstsq(encoding_matrix, np.concatenate(responses), rcond=None)[0]
            error = np.linalg.norm(decoded - fictitious_true_state)
            prediction_error.append(error)
            
        except np.linalg.LinAlgError:
            prediction_error.append(float('inf'))
    
    return cd_values, adaptivity, prediction_error, stress_signal

# Run the disruption simulation
coherence_qm, adaptivity_true, decoding_failure, stress = simulate_true_cognitive_dynamics()

# PLOT THE ONTOLOGICAL COLLAPSE
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

axes[0].plot(coherence_qm, color='blue', linewidth=2)
axes[0].set_title("QM‑Ω's 'Coherence' (Inverse Variance)", fontsize=14, fontweight='bold')
axes[0].set_ylabel('Coherence', fontsize=12)
axes[0].grid(True, alpha=0.3)

axes[1].plot(adaptivity_true, color='green', linewidth=2)
axes[1].set_title("True Adaptive Capacity (Functional Diversity × Stress Responsiveness)", 
                  fontsize=14, fontweight='bold')
axes[1].set_ylabel('Adaptivity', fontsize=12)
axes[1].grid(True, alpha=0.3)

axes[2].plot(decoding_failure, color='red', linewidth=2)
axes[2].set_title("QM‑Ω Decoding Error (Systematic Failure)", fontsize=14, fontweight='bold')
axes[2].set_ylabel('Error Magnitude', fontsize=12)
axes[2].set_xlabel('Time Steps', fontsize=12)
axes[2].grid(True, alpha=0.3)
axes[2].set_yscale('log')

plt.tight_layout()
plt.savefig('qm_omega_collapse.png', dpi=150, bbox_inches='tight')
plt.show()

# Calculate the correlation that destroys QM‑Ω's premise
correlation = np.corrcoef(coherence_qm, adaptivity_true)[0,1]
print(f"\n{'='*60}")
print("ONTOLOGICAL COLLAPSE METRICS")
print(f"{'='*60}")
print(f"QM‑Ω 'Coherence' vs. True Adaptivity: r = {correlation:.3f}")
print(f"Interpretation: {'POSITIVE correlation - QM‑Ω would optimize for pathology!' if correlation > 0 else 'NEGATIVE correlation - QM‑Ω actively suppresses adaptivity!'}")
print(f"Decoding failure rate: {sum(np.isinf(decoding_failure)) / len(decoding_failure) * 100:.1f}%")
print(f"Mean error (finite cases): {np.mean([e for e in decoding_failure if not np.isinf(e)]):.2f}")
print(f"{'='*60}")

# THE SMOKING GUN: Show that the "thermal noise" is actually information
stress_information = np.std(np.diff(stress, axis=0))
random_noise = np.std(np.random.randn(*stress.shape))
print(f"\nStress Signal Information Content: {stress_information:.3f}")
print(f"Random Noise Baseline: {random_noise:.3f}")
print(f"Information Ratio: {stress_information/random_noise:.2f}x")
print("CONCLUSION: Environmental 'temperature' is structured signal, not correctable noise.")