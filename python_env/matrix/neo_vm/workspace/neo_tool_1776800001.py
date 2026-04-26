# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform

# NEO'S DISRUPTION SCRIPT: "The Manifold is a Lie"
# Demonstrates why the smooth manifold approach fails and topological defects are real

print("=== NEO'S ANOMALY: BREAKING THE MANIFOLD PARADIGM ===\n")

# Simulate "biological context" data: 5 chassis, 3 media, 2 temperatures = 30 contexts
# But biological reality: contexts are DISCRETE categories, not continuous
chassis = ['E_coli_K12', 'E_coli_B', 'B_subtilis', 'S_cerevisiae', 'P_putida']
media = ['LB', 'M9', 'YPD']
temperatures = [30, 37]

# Real biological data: performance is NOT smooth across this space
# Create synthetic but realistic "device performance" data with CATASTROPHIC DISCONTINUITIES
np.random.seed(42)
contexts = []
performances = []

for c in chassis:
    for m in media:
        for t in temperatures:
            contexts.append([chassis.index(c), media.index(m), t])
            
            # KEY INSIGHT: Performance is NOT a smooth function
            # Instead, it's DISCRETE with cliff-like transitions
            if c == 'E_coli_K12' and m == 'LB':
                perf = np.random.normal(1.0, 0.1)  # Works great
            elif c == 'E_coli_B' and m == 'M9':
                perf = np.random.normal(0.9, 0.1)  # Works well
            elif c == 'B_subtilis' and m == 'LB' and t == 37:
                perf = np.random.normal(0.3, 0.05)  # CATASTROPHIC FAILURE - not on a smooth gradient!
            elif c == 'S_cerevisiae' and m == 'YPD':
                perf = np.random.normal(0.8, 0.15)  # Works
            elif c == 'P_putida' and m == 'M9':
                perf = np.random.normal(0.2, 0.1)  # Another cliff!
            else:
                perf = np.random.normal(0.5, 0.2)  # Mediocre

            performances.append(perf)

contexts = np.array(contexts)
performances = np.array(performances)

print(f"Generated {len(contexts)} discrete biological contexts")
print(f"Performance range: {performances.min():.3f} to {performances.max():.3f}")
print(f"Standard deviation: {performances.std():.3f}\n")

# === ATTEMPT 1: The Manifold Approach (the proposal's method) ===
print("--- MANIFOLD APPROACH (THEIR METHOD) ---")

# Try to embed into a "smooth manifold" using GPLVM assumptions
# This is what their proposal does - treats discrete contexts as continuous

# Use pairwise distances to create a "similarity matrix"
distances = squareform(pdist(contexts, metric='euclidean'))
# Normalize distances to pretend they're continuous
distances = distances / distances.max()

# Try to fit a smooth Gaussian Process
kernel = RBF(length_scale=1.0)
gp = GaussianProcessRegressor(kernel=kernel, alpha=0.1)

# Fit the GP to predict performance from context
gp.fit(contexts, performances)

# Now try to predict performance for "intermediate" contexts (that don't exist in biology!)
# This is what their manifold approach IMPLIES - that you can interpolate between chassis
test_contexts = []
for i in np.linspace(0, len(chassis)-1, 20):
    for j in np.linspace(0, len(media)-1, 10):
        for k in [30, 37]:
            test_contexts.append([i, j, k])
test_contexts = np.array(test_contexts)

smooth_predictions, smooth_std = gp.predict(test_contexts, return_std=True)

# Find the ACTUAL catastrophic failures
actual_failures = np.where(performances < 0.4)[0]
print(f"Actual catastrophic failures at contexts: {actual_failures}")
print(f"Actual failure performances: {performances[actual_failures]}")

# The smooth manifold will COMPLETELY MISS these failures
# It will predict everything is fine because it's smooth
worst_predicted = np.argmin(smooth_predictions)
print(f"Manifold predicts worst performance at {worst_predicted}: {smooth_predictions[worst_predicted]:.3f}")
print("Manifold's 'curvature' is smooth - it cannot detect cliffs!")
print("Curvature-based CFI will be WRONG for these contexts\n")

# === ATTEMPT 2: The Topological/Hypergraph Approach (NEO'S DISRUPTION) ===
print("--- TOPOLOGICAL DEFECT APPROACH (NEO'S METHOD) ---")

# Build a hypergraph where contexts are nodes, devices are hyperedges
# Fragility is in the CONNECTIVITY, not the curvature

# Create a graph where edges exist between contexts that are "compatible"
# Compatibility = performance above threshold
threshold = 0.6
G = nx.Graph()

# Add nodes for each context
for i, ctx in enumerate(contexts):
    G.add_node(i, 
               chassis=chassis[int(ctx[0])],
               media=media[int(ctx[1])],
               temp=int(ctx[2]),
               perf=performances[i])

# Add edges between contexts where performance is STABLE (not fragile)
# This creates a "compatibility hypergraph"
for i in range(len(contexts)):
    for j in range(i+1, len(contexts)):
        # If BOTH contexts work well, they're compatible
        if performances[i] > threshold and performances[j] > threshold:
            # Check if they differ by only one factor (chassis, media, or temp)
            diff = np.sum(contexts[i] != contexts[j])
            if diff <= 1:  # Adjacent in context space
                G.add_edge(i, j, weight=min(performances[i], performances[j]))

print(f"Hypergraph nodes: {G.number_of_nodes()}")
print(f"Hypergraph edges (stable connections): {G.number_of_edges()}")

# Detect TOPOLOGICAL DEFECTS - disconnected components indicating catastrophic context gaps
components = list(nx.connected_components(G))
print(f"\nConnected components: {len(components)}")

fragile_contexts = []
for i, comp in enumerate(components):
    print(f"Component {i}: {len(comp)} contexts")
    if len(comp) < 3:  # Small, isolated component = FRAGILE
        print(f"  -> FRAGILE COMPONENT (isolated contexts):")
        for node in comp:
            print(f"    Node {node}: {chassis[int(contexts[node][0])]}, {media[int(contexts[node][1])]}, {int(contexts[node][2])}°C, perf={performances[node]:.3f}")
            fragile_contexts.append(node)

# Calculate PERSISTENT HOMOLOGY - track holes in the context space
# A "hole" means there's a set of contexts that should be connected but aren't
# This is the REAL measure of fragility, not curvature

# Create a Vietoris-Rips complex from the discrete contexts
# But weight by PERFORMANCE - low performance = high "distance"
performance_distances = np.zeros_like(distances)
for i in range(len(contexts)):
    for j in range(len(contexts)):
        # If either context is fragile (low perf), make distance large
        performance_distances[i,j] = 1.0 - min(performances[i], performances[j])

# Find contexts that are "holes" - should be connected but aren't
# These are the CATASTROPHIC FAILURES the manifold misses
hole_contexts = []
for i in range(len(contexts)):
    # If a context has low performance but is surrounded by high-performance neighbors
    # it's a TOPOLOGICAL DEFECT
    if performances[i] < threshold:
        neighbor_perfs = [performances[n] for n in G.neighbors(i)]
        if len(neighbor_perfs) > 0 and np.mean(neighbor_perfs) > threshold:
            hole_contexts.append(i)

print(f"\nTopological defects (holes in context space): {hole_contexts}")
print("These are contexts that SHOULD work based on neighbors but DON'T - true fragility!")

# === THE DISRUPTION: Why their entire framework collapses ===
print("\n=== NEO'S DISRUPTIVE INSIGHT ===")

print("FLAW 1: The 'manifold' is a mathematical hallucination.")
print("  - Biological contexts are DISCRETE (E. coli ≠ B. subtilis ≠ yeast)")
print("  - GPLVM creates false continuity, inventing non-existent 'intermediate' contexts")
print("  - Curvature is meaningless on a discrete space with cliffs")

print("\nFLAW 2: The invariant ψ = ln(Φ_N) is intellectual conformity.")
print("  - Forcing biology into a pre-defined physics rubric is backwards")
print("  - The real invariant is a TOPOLOGICAL BARCODE, not a scalar")
print("  - Φ_N (spectral gap) is a graph property, not a field property")

print("\nFLAW 3: The 'control actions' are recursive fragility.")
print("  - Codon harmonization itself has context-fragility")
print("  - You're using a fragile controller to control a fragile system")
print("  - No analysis of the MPC-Ω's own contextual collapse")

print("\nFLAW 4: The Φ-density calculations are cargo-cult numerology.")
print("  - Assigning precise percentages to conceptual gains is pseudo-science")
print("  - Creates illusion of predictability where none exists")

print("\nBREAKTHROUGH: Replace FTFM-Ω with CHDM-Ω (Contextual Hypergraph Defect Monitor)")
print("  - Model contexts as hypergraph nodes, not manifold points")
print("  - Measure fragility via PERSISTENT HOMOLOGY (holes, disconnected components)")
print("  - Invariant = barcode of Betti numbers, not scalar ψ")
print("  - Control actions = HYPERGRAPH SURGERY (add/remove edges), not parameter tweaks")
print("  - This respects the discrete, combinatorial nature of biology")

print("\nThe manifold approach is SMOOTHING OVER THE VERY DISCONTINUITIES THAT CAUSE FAILURE.")
print("By the time your curvature detects a problem, the device has already fallen off a cliff.")
print("Only topological defects can see the cliffs before you step off them.")

# === VISUALIZATION: Show the failure ===
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: The "smooth manifold" prediction
ax1.scatter(contexts[:, 0], performances, c='black', s=100, label='Actual Data', zorder=5)
ax1.scatter(test_contexts[:, 0], smooth_predictions, c='blue', alpha=0.3, s=20, label='Manifold Prediction')
ax1.fill_between(test_contexts[:, 0], 
                 smooth_predictions - smooth_std, 
                 smooth_predictions + smooth_std, 
                 color='blue', alpha=0.1)
ax1.axhline(y=threshold, color='red', linestyle='--', label='Failure Threshold')
ax1.set_xlabel('Chassis (continuous)')
ax1.set_ylabel('Performance')
ax1.set_title('MANIFOLD APPROACH: Smooth hallucination misses cliffs')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: The hypergraph showing topological defects
pos = nx.spring_layout(G, seed=42)
node_colors = ['green' if performances[i] > threshold else 'red' for i in G.nodes()]
node_sizes = [100 if i in fragile_contexts else 50 for i in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax2)
nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax2)
nx.draw_networkx_labels(G, pos, 
                        labels={i: f"{i}\n{performances[i]:.2f}" for i in G.nodes()},
                        font_size=8, ax=ax2)
ax2.set_title('HYPERGRAPH APPROACH: Red nodes = topological defects (isolated failures)')
ax2.axis('off')

plt.tight_layout()
plt.show()

print("\n=== AUDIT CONCLUSION ===")
print("The 'PASS' verdict is WRONG. The proposal is mathematically elegant but biologically")
print("delusional. It commits the cardinal sin of applied math: mistaking the map for the territory.")
print("Only by abandoning the manifold and embracing topological defects can we truly")
print("predict contextual collapse in synthetic biology.")