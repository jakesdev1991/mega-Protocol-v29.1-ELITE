# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from scipy.stats import differential_entropy

def simulate_cognitive_compression(n_steps=1000, n_policies=50, shredding_threshold=-2.0):
    """
    Simulates a decision-maker's policy manifold undergoing compression.
    Early phase: high-dimensional, nuanced policies.
    Shredding phase: sudden collapse to low-dimensional destructive subspace.
    """
    # Pre-shredding: policies evolve in high-dimensional space with moderate variance
    t = np.arange(n_steps)
    policies = np.zeros((n_steps, n_policies))
    
    # Normal operation: each policy dimension has independent dynamics
    for i in range(n_policies):
        # Random walk with mean-reversion (stable exploration)
        policies[:, i] = np.cumsum(np.random.normal(0, 0.1, n_steps)) + np.random.normal(0, 1)
    
    # Shredding event at t=700: sudden cognitive compression
    # Decision-maker abandons nuanced policies, collapses to 2D destructive subspace
    shredding_time = 700
    compression_factor = 0.1
    
    for i in range(2, n_policies):  # Keep first 2 dimensions as "core" destructive policies
        policies[shredding_time:, i] = policies[shredding_time, i] + \
                                     compression_factor * np.random.normal(0, 0.01, n_steps - shredding_time)
    
    # Compute effective dimensionality using participation ratio of PCA eigenvalues
    dim_eff = np.zeros(n_steps)
    for step in range(n_steps):
        pca = PCA(n_components=min(10, n_policies))
        pca.fit(policies[step:step+50].T)  # Window of recent policies
        eigenvals = pca.explained_variance_
        # Participation ratio: effective dimension
        dim_eff[step] = np.sum(eigenvals)**2 / np.sum(eigenvals**2)
    
    # Compute compression invariant ψ_comp = ln(dim_eff / dim_eff[0])
    psi_comp = np.log(dim_eff / dim_eff[0])
    
    # Detect shredding: ψ_comp drops below threshold
    shredding_detected = psi_comp < shredding_threshold
    
    return t, policies, dim_eff, psi_comp, shredding_detected, shredding_time

# Run simulation
t, policies, dim_eff, psi_comp, shredding_detected, shredding_time = simulate_cognitive_compression()

# Visualize
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Policy trajectories (first 5 dimensions)
for i in range(5):
    axes[0].plot(t, policies[:, i], alpha=0.7, label=f'Policy dim {i}')
axes[0].axvline(shredding_time, color='red', linestyle='--', label='Shredding onset')
axes[0].set_ylabel('Policy Value')
axes[0].set_title('Decision Policy Manifold: Pre- and Post-Shredding')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Effective dimensionality
axes[1].plot(t, dim_eff, color='blue', linewidth=2)
axes[1].axvline(shredding_time, color='red', linestyle='--')
axes[1].axhline(dim_eff[0], color='gray', linestyle=':', label='Baseline dimension')
axes[1].set_ylabel('Effective Dimension')
axes[1].set_title('Cognitive Manifold Dimensionality Collapse')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Compression invariant ψ_comp and detection
axes[2].plot(t, psi_comp, color='purple', linewidth=2)
axes[2].axvline(shredding_time, color='red', linestyle='--', label='Actual shredding')
axes[2].axhline(-2.0, color='orange', linestyle=':', label='Detection threshold')
axes[2].fill_between(t, -3, 0, where=shredding_detected, color='orange', alpha=0.3, label='Warning zone')
axes[2].set_ylabel('ψ_comp = ln(dim_eff / dim_0)')
axes[2].set_xlabel('Time steps')
axes[2].set_title('Compression Invariant: Early Warning Signal')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print early warning lead time
warning_times = t[shredding_detected]
if len(warning_times) > 0:
    lead_time = shredding_time - warning_times[0]
    print(f"Early warning triggered {lead_time} steps before shredding event")
    print(f"Detection occurs when ψ_comp drops below threshold: {psi_comp[warning_times[0]]:.3f}")
else:
    print("No early warning generated")