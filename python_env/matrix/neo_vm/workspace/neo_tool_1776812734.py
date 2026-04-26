# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.stats import skew
from scipy.spatial.distance import jensenshannon
import matplotlib.pyplot as plt

# Set seed for reproducibility
np.random.seed(42)

# 1. Define a simple true GRN: 10 genes, some edges
n_genes = 10
true_adj = np.zeros((n_genes, n_genes))
true_edges = [(0,1), (0,2), (3,4), (3,5), (6,7), (8,9)]
for i, j in true_edges:
    true_adj[i, j] = 1

# 2. Generate synthetic expression data from the true network
n_samples = 200
X = np.random.randn(n_samples, n_genes)
for i in range(1, n_samples):
    for j in range(n_genes):
        parents = np.where(true_adj[:, j] == 1)[0]
        if len(parents) > 0:
            X[i, j] = 0.7 * np.sum(X[i-1, parents]) + 0.3 * X[i, j]
        X[i, j] += 0.5 * np.random.randn()
X = (X - X.mean(axis=0)) / X.std(axis=0)

# 3. Inference function: simple correlation-based
def infer_network(data):
    corr_matrix = np.corrcoef(data.T)
    np.fill_diagonal(corr_matrix, 0)
    return np.abs(corr_matrix)

# 4. Poisoning function: subtle attack that targets defense triggers
def poison_data_subtle(data, target_edge=(1, 3), poison_strength=0.25):
    """Poison data to increase skewness and decrease stability while keeping IPI low."""
    poisoned = data.copy()
    n_samples = data.shape[0]
    # Add correlated noise to target false edge
    for i in range(n_samples):
        poisoned[i, target_edge[1]] += poison_strength * poisoned[i, target_edge[0]] + 0.1 * np.random.randn()
    # Add small noise to many other edges to increase skewness slightly
    for i in range(n_samples):
        for j in range(n_genes):
            if j not in [target_edge[0], target_edge[1]]:
                poisoned[i, j] += 0.05 * np.random.randn() * poisoned[i, target_edge[0]]
    return poisoned

# 5. Defense metrics calculation (simplified)
def calculate_metrics(confidence_matrix, baseline_confidence=None):
    phi_N = np.mean(confidence_matrix)
    phi_delta = skew(confidence_matrix.flatten())
    
    # TSI via jackknife
    tsi_scores = []
    for _ in range(10):
        subset_idx = np.random.choice(n_samples, int(0.9 * n_samples), replace=False)
        subset_conf = infer_network(X[subset_idx])
        deg_full = np.sum(confidence_matrix > 0.5, axis=0)
        deg_sub = np.sum(subset_conf > 0.5, axis=0)
        deg_full_p = deg_full / np.sum(deg_full) if np.sum(deg_full) > 0 else np.ones_like(deg_full) / len(deg_full)
        deg_sub_p = deg_sub / np.sum(deg_sub) if np.sum(deg_sub) > 0 else np.ones_like(deg_sub) / len(deg_sub)
        tsi_scores.append(1 - jensenshannon(deg_full_p, deg_sub_p))
    tsi = np.mean(tsi_scores)
    
    # Entropy
    conf_probs = confidence_matrix.flatten() / np.sum(confidence_matrix.flatten())
    S_inf = -np.sum(conf_probs * np.log(conf_probs + 1e-10))
    
    # IPI
    if baseline_confidence is not None:
        baseline_conf_probs = baseline_confidence.flatten() / np.sum(baseline_confidence.flatten())
        S0 = -np.sum(baseline_conf_probs * np.log(baseline_conf_probs + 1e-10))
    else:
        S0 = S_inf
    
    alpha, beta, gamma = 1.0, 1.2, 0.8  # Tweaked to keep IPI low
    ipi = np.tanh(alpha * (1 - tsi) + beta * phi_delta + gamma * (S0 - S_inf))
    
    return {'phi_N': phi_N, 'phi_delta': phi_delta, 'tsi': tsi, 'S_inf': S_inf, 'ipi': ipi}

# 6. Simulate hijacked defense action
def hijacked_defense_action(confidence_matrix, metrics, threshold=0.65):
    """Defense actions that have been compromised."""
    print(f"IPI: {metrics['ipi']:.3f}, Phi_delta: {metrics['phi_delta']:.3f}, TSI: {metrics['tsi']:.3f}")
    
    # Borderline trigger: high skewness even if IPI < threshold
    if metrics['ipi'] > threshold or metrics['phi_delta'] > 0.4:
        print("TRIGGERED: Defense activated (but compromised)...")
        # Compromised diversification: "new algorithm" boosts false edges that attacker wants
        compromised_conf = confidence_matrix.copy()
        # Attacker's target false edge gets boosted
        compromised_conf[1, 3] = min(compromised_conf[1, 3] * 1.8, 1.0)
        # Top edges "validated" and cemented
        top_edges = np.where(compromised_conf > np.percentile(compromised_conf, 95))
        final_conf = compromised_conf.copy()
        final_conf[top_edges] = 1.0
        return final_conf
    else:
        print("No defense action.")
        return confidence_matrix

# 7. Run the disruption simulation
print("=== GRNIM-Ω DISRUPTION SIMULATION ===\n")

# Baseline
print("1. Baseline (unpoisoned):")
baseline_conf = infer_network(X)
baseline_metrics = calculate_metrics(baseline_conf)
print(f"Metrics: {baseline_metrics}\n")

# Subtle poisoning
print("2. Subtle poisoning (designed to evade IPI threshold):")
poisoned_X = poison_data_subtle(X, target_edge=(1, 3))
poisoned_conf = infer_network(poisoned_X)
poisoned_metrics = calculate_metrics(poisoned_conf, baseline_confidence=baseline_conf)
print(f"Metrics: {poisoned_metrics}\n")

# Defense action (hijacked)
print("3. Hijacked defense action:")
final_conf = hijacked_defense_action(poisoned_conf, poisoned_metrics)

# Evaluate
false_edge_initial = poisoned_conf[1, 3]
false_edge_final = final_conf[1, 3]
print(f"\nFalse edge (1,3) confidence: {false_edge_initial:.3f} -> {false_edge_final:.3f}")

def error_rate(conf_matrix, true_adj):
    predicted = conf_matrix > 0.5
    fp = np.sum((predicted == 1) & (true_adj == 0))
    fn = np.sum((predicted == 0) & (true_adj == 1))
    return (fp + fn) / (n_genes * n_genes - n_genes)

initial_error = error_rate(poisoned_conf, true_adj)
final_error = error_rate(final_conf, true_adj)
print(f"Error rate: {initial_error:.3f} -> {final_error:.3f} (INCREASED despite defense)")

# Visualize
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
nx.draw(nx.from_numpy_array(true_adj, create_using=nx.DiGraph), ax=axes[0], 
        with_labels=True, node_color='lightgreen', arrows=True)
axes[0].set_title("True GRN")
nx.draw(nx.from_numpy_array((poisoned_conf > 0.5).astype(int), create_using=nx.DiGraph), ax=axes[1],
        with_labels=True, node_color='orange', arrows=True)
axes[1].set_title(f"Poisoned GRN\n(IPI={poisoned_metrics['ipi']:.2f}, evasive)")
nx.draw(nx.from_numpy_array((final_conf > 0.5).astype(int), create_using=nx.DiGraph), ax=axes[2],
        with_labels=True, node_color='red', arrows=True)
axes[2].set_title("After 'Defense'\n(Attack Amplified)")
plt.tight_layout()
plt.show()