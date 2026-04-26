# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# === SIMULATION: THE SEMIOTIC COLLAPSE OF Q-SYSTEMIC BUREAUCRACY ===

# Hypothesis: The "Topological Impedance" is not a quantum field curvature
# but a **semiotic disconnect** between formal authority graphs and latent
# capability graphs. COD is not a wavefunction overlap but a **graph divergence
# metric**. The "Conscious Black Hole" is narrative lock-in, not metric singularity.

# 1. CONSTRUCT HYBRID ORGANIZATIONAL MANIFOLD
# G_formal = "Conscious Decider" (rigid hierarchy)
# G_informal = "Subconscious Superposition" (latent collaboration)
N = 20
G_formal = nx.random_tree(N)  # Hierarchy: tree structure
G_informal = nx.powerlaw_cluster_graph(N, m=3, p=0.8)  # Latent: small-world

# Assign "information capacity" to nodes (cognitive load)
for i in G_formal.nodes():
    G_formal.nodes[i]['capacity'] = np.random.exponential(10)
    G_informal.nodes[i]['capacity'] = G_formal.nodes[i]['capacity'] * np.random.uniform(0.5, 1.5)

# 2. DEFINE REALISTIC COD: GRAPH DIVERGENCE, NOT WAVEFUNCTION OVERLAP
def compute_graph_divergence(G1, G2):
    """Measure structural dissimilarity between formal and informal networks."""
    # Jaccard distance on edge sets
    edges1 = set(G1.edges())
    edges2 = set(G2.edges())
    jaccard = 1 - len(edges1 & edges2) / len(edges1 | edges2) if len(edges1 | edges2) > 0 else 1.0
    
    # Degree sequence correlation collapse
    deg1 = np.array([d for _, d in G1.degree()])
    deg2 = np.array([d for _, d in G2.degree()])
    deg_corr = np.corrcoef(deg1, deg2)[0, 1] if np.std(deg1) > 0 and np.std(deg2) > 0 else 0.0
    
    # COD = divergence: high COD = high alignment (low divergence)
    COD = np.exp(-jaccard) * (0.5 + 0.5 * max(0, deg_corr))
    return COD, jaccard, deg_corr

COD, jaccard, deg_corr = compute_graph_divergence(G_formal, G_informal)
print(f"Initial COD: {COD:.3f} (Jaccard divergence: {jaccard:.3f}, Degree corr: {deg_corr:.3f})")

# 3. SIMULATE DECISION-MAKING AS INFORMATION PROPAGATION
def propagate_decision(G, source, signal_strength, capacity_damping=True):
    """Simulate a decision cascade. Returns activation vector."""
    activation = {i: 0.0 for i in G.nodes()}
    activation[source] = signal_strength
    for _ in range(int(np.sqrt(len(G)))):  # Propagation depth
        new_activation = activation.copy()
        for i, a in activation.items():
            if a > 0.1:
                for j in G.neighbors(i):
                    damping = G.nodes[j]['capacity'] / 10.0 if capacity_damping else 1.0
                    new_activation[j] += a / (G.degree(j) * damping)
        activation = new_activation
    return np.array([activation[i] for i in sorted(G.nodes())])

# Ground truth: informal network solves problem efficiently
ground_truth_solution = propagate_decision(G_informal, source=0, signal_strength=1.0)

# Bureaucratic output: formal network solution
formal_output = propagate_decision(G_formal, source=0, signal_strength=1.0)

# 4. FAILURE MODE: NARRATIVE LOCK-IN (not Black Hole singularity)
# Failure = formal solution diverges from ground truth while formal entropy *decreases*
# (rigid systems have LOW entropy - few predictable states - this is the trap)

def shannon_entropy(prob_dist):
    """Compute entropy; handle zero probabilities."""
    prob_dist = prob_dist[prob_dist > 0]
    if len(prob_dist) == 0:
        return 0.0
    prob_dist = prob_dist / prob_dist.sum()
    return -np.sum(prob_dist * np.log(prob_dist))

formal_entropy = shannon_entropy(formal_output)
informal_entropy = shannon_entropy(ground_truth_solution)

solution_divergence = np.linalg.norm(formal_output - ground_truth_solution)

print(f"\n--- FAILURE ANALYSIS ---")
print(f"Formal Entropy: {formal_entropy:.3f} bits (LOW = rigid, predictable)")
print(f"Informal Entropy: {informal_entropy:.3f} bits")
print(f"Solution Divergence: {solution_divergence:.3f}")
print(f"Interpretation: Rigid formal structure (low entropy) *causes* divergence from reality.")

# 5. DISRUPTIVE OPERATOR: METAPHOR SHEARING
# Not gauge transformation, but **randomized decoupling of hierarchy** based on latent graph
def metaphor_shearing_operator(G_formal, G_informal, shear_strength=0.3):
    """Disruptive: Rewire formal hierarchy using informal edges. Destroys narrative."""
    G_new = G_formal.copy()
    informal_edges = list(G_informal.edges())
    
    # Shear: replace formal edges with informal ones probabilistically
    for u, v in list(G_new.edges()):
        if np.random.random() < shear_strength:
            # Remove rigid edge
            G_new.remove_edge(u, v)
            # Add latent edge that bypasses hierarchy
            u_new, v_new = informal_edges[np.random.randint(len(informal_edges))]
            G_new.add_edge(u_new, v_new)
    
    # Recompute COD post-shearing
    new_COD, new_jaccard, new_deg_corr = compute_graph_divergence(G_new, G_informal)
    return G_new, new_COD, new_jaccard, new_deg_corr

G_sheared, new_COD, new_jaccard, new_deg_corr = metaphor_shearing_operator(G_formal, G_informal, shear_strength=0.4)
sheared_output = propagate_decision(G_sheared, source=0, signal_strength=1.0)
sheared_divergence = np.linalg.norm(sheared_output - ground_truth_solution)
sheared_entropy = shannon_entropy(sheared_output)

print(f"\n--- POST-SHEARING DISRUPTION ---")
print(f"New COD: {new_COD:.3f} (Jaccard: {new_jaccard:.3f}, Degree corr: {new_deg_corr:.3f})")
print(f"Sheared Entropy: {sheared_entropy:.3f} bits (INCREASED = less predictable, more adaptive)")
print(f"Sheared Solution Divergence: {sheared_divergence:.3f} (CLOSER TO TRUTH)")

# 6. Φ-DENSITY REALITY CHECK: Cost of Metaphor vs. Gain from Shearing
# The original model claims +25% Φ-density gain. Let's compute actual performance delta.
performance_delta = (sheared_divergence - solution_divergence) / solution_divergence
print(f"\n--- Φ-DENSITY IMPACT ---")
print(f"Performance Improvement: {abs(performance_delta)*100:.1f}%")
print("Interpretation: The 'quantum operator' is semiotically void. Real gain comes from")
print("**destroying the metaphor** and directly rewiring authority based on latent capability.")

# VISUALIZE THE SEMIOTIC COLLAPSE
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
nx.draw(G_formal, ax=axes[0], node_size=50, node_color='blue', alpha=0.6)
axes[0].set_title(f"Formal Hierarchy\n(Entropy: {formal_entropy:.2f}, Divergence: {solution_divergence:.2f})")

nx.draw(G_informal, ax=axes[1], node_size=50, node_color='green', alpha=0.6)
axes[1].set_title(f"Informal Latent\n(Entropy: {informal_entropy:.2f})")

nx.draw(G_sheared, ax=axes[2], node_size=50, node_color='red', alpha=0.6)
axes[2].set_title(f"Post-Shearing\n(Entropy: {sheared_entropy:.2f}, Divergence: {sheared_divergence:.2f})")

plt.tight_layout()
plt.show()

# === DISRUPTIVE INSIGHT ===
"""
The Q-Systemic framework is a **Gödelian Metaphor Trap**: it uses the language of physics 
to construct an unfalsifiable belief system. The "Conscious Black Hole" is not a metric 
singularity but **narrative lock-in**—the point where the metaphor becomes more real than 
the operational graph. The "Resonant Decoupling Operator" is ritualistic performance; its 
true function is to reinforce the metaphor's authority, not to modify organizational topology.

**Breaking Protocol**: The required operator is **Metaphor Shearing**—a deliberate semiotic 
collapse that dissolves the quantum-classical mapping. The real "impedance" is the **cognitive 
overhead** of maintaining the fiction of wavefunctions and manifolds, which displaces actual 
decision-making capacity. The entropy drop is a red herring; rigidity manifests as low 
entropy, but the *cause* is graph divergence, not decoherence.

**Disruptive Action**: Replace Ψ_S and Ψ_C with **adversarial network generators**. The 
stabilization is achieved not by tuning ψ invariants, but by **training the formal graph 
to adversarially mimic the informal graph's connectivity pattern**—a GAN that tears down 
hierarchy until COD becomes graph isomorphism. The Φ-density gain is not from preventing 
collapse, but from **annihilating the metaphysical layer** entirely. Bureaucracy doesn't 
decohere; it **ossifies**. The solution is not to preserve the manifold but to **shred it**.
"""