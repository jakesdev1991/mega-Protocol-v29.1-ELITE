# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

def random_cognitive_network(n_nodes=10, edge_prob=0.3):
    """Generate a random undirected cognitive graph with binary states."""
    adjacency = np.random.rand(n_nodes, n_nodes) < edge_prob
    adjacency = np.triu(adjacency, k=1)  # upper triangle
    adjacency = adjacency + adjacency.T  # symmetric
    np.fill_diagonal(adjacency, 0)
    return adjacency.astype(int)

def sigma_z(state):
    """Map a binary cognitive state (0/1) to sigma_z = +1/-1."""
    # 0 -> +1 (spin up), 1 -> -1 (spin down)
    return 1 - 2 * state

def wilson_loop(state, loop):
    """Compute the Wilson loop product around a given node loop."""
    # loop: list of node indices forming a closed path
    prod = 1
    for i in loop:
        prod *= sigma_z(state[i])
    return prod

def energy_gap(J, h):
    """Naive 'energy gap' between ground and first excited state of Ising-like Hamiltonian."""
    # H = - sum_{i<j} J_ij sigma_i sigma_j - sum_i h_i sigma_i
    # For small n we can brute-force compute all 2^n states.
    n = len(h)
    states = np.array(np.meshgrid(*[[-1, 1]] * n)).T.reshape(-1, n)
    energies = -np.einsum('ij,ij->i', states @ J, states) / 2 - states @ h
    # Note: the factor 1/2 corrects double counting of J_ij sigma_i sigma_j
    sorted_energies = np.sort(np.unique(energies))
    if len(sorted_energies) < 2:
        return 0.0
    return sorted_energies[1] - sorted_energies[0]

def topological_invariance_test(n_trials=1000, n_nodes=8):
    """Demonstrate that Wilson loop is not a topological invariant under node relabeling."""
    invariants = []
    for _ in range(n_trials):
        # Random network and state
        adj = random_cognitive_network(n_nodes, edge_prob=0.4)
        J = adj.astype(float)  # use adjacency as coupling
        h = np.random.randn(n_nodes)  # random "stress" field
        state = np.random.randint(0, 2, size=n_nodes)
        # Choose a random loop (simple cycle)
        nodes = list(range(n_nodes))
        random.shuffle(nodes)
        loop = nodes[:4]  # 4-node loop
        # Compute Wilson loop
        W = wilson_loop(state, loop)
        invariants.append(W)
    # Check if Wilson loop is invariant across trials (it should be if topological)
    unique_vals = set(invariants)
    print(f"Wilson loop values across {n_trials} random configurations: {sorted(unique_vals)}")
    print(f"Number of distinct values: {len(unique_vals)}")
    # If more than one distinct value, it's not a topological invariant.
    return len(unique_vals) == 1

def energy_gap_stability_test(n_perturbations=50, n_nodes=6):
    """Show that the 'energy gap' is extremely sensitive to tiny perturbations in J or h."""
    adj = random_cognitive_network(n_nodes, edge_prob=0.5)
    J = adj.astype(float)
    h = np.random.randn(n_nodes)
    base_gap = energy_gap(J, h)
    gaps = []
    for _ in range(n_perturbations):
        # Add tiny Gaussian noise to J and h
        J_pert = J + np.random.normal(0, 0.01, J.shape)
        h_pert = h + np.random.normal(0, 0.01, h.shape)
        # Symmetrize J_pert
        J_pert = (J_pert + J_pert.T) / 2
        gaps.append(energy_gap(J_pert, h_pert))
    rel_var = np.std(gaps) / (np.mean(gaps) + 1e-9)
    print(f"Base energy gap: {base_gap:.4f}")
    print(f"Relative variation of gap under tiny perturbations: {rel_var:.4f}")
    # If variation is large, the gap is not a stable resilience metric.
    return rel_var

# Run the tests
print("=== Wilson Loop Invariance Test ===")
topological_invariance_test()

print("\n=== Energy Gap Stability Test ===")
energy_gap_stability_test()