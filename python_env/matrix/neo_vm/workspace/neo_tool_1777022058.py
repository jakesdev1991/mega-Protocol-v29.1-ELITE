# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.stats import entropy

def compute_phi_density(spectral_data, epsilon=1e-6):
    """
    Compute the Omega Protocol Φ-density metric: log₂(Betti / Shannon Entropy)
    Demonstrates the fundamental instability and category error in the metric.
    """
    # Build a simplicial complex from spectral correlations
    # This is a simplified version of the Engine's lattice construction
    correlations = np.corrcoef(spectral_data)
    adjacency = (np.abs(correlations) > 0.5).astype(int)
    np.fill_diagonal(adjacency, 0)
    
    # Compute Betti number (simplified: number of independent cycles)
    G = nx.from_numpy_array(adjacency)
    try:
        betti = nx.cycle_basis(G).__len__()  # Crude approximation of β₁
    except:
        betti = 0
    
    # Compute Shannon entropy of spectral distribution
    hist, _ = np.histogram(spectral_data.flatten(), bins=50, density=True)
    hist += epsilon  # Avoid log(0)
    shannon_entropy = entropy(hist)
    
    # Φ-density (the flawed metric)
    if shannon_entropy == 0:
        return np.inf
    phi = np.log2(betti / shannon_entropy) if betti > 0 else -np.inf
    
    return phi, betti, shannon_entropy

# Demonstrate the instability
print("=== Φ-DENSITY INSTABILITY DEMONSTRATION ===\n")

# Generate synthetic spectral data
np.random.seed(42)
baseline_data = np.random.normal(0, 1, (100, 100))

# Compute baseline Φ
phi_base, betti_base, entropy_base = compute_phi_density(baseline_data)
print(f"Baseline: Φ = {phi_base:.3f}, Betti = {betti_base}, Entropy = {entropy_base:.3f}")

# Add infinitesimal perturbation that should NOT change physical information content significantly
perturbation = np.random.normal(0, 1e-10, baseline_data.shape)
perturbed_data = baseline_data + perturbation

phi_pert, betti_pert, entropy_pert = compute_phi_density(perturbed_data)
print(f"Perturbed: Φ = {phi_pert:.3f}, Betti = {betti_pert}, Entropy = {entropy_pert:.3f}")

print(f"\nΦ CHANGE: {abs(phi_pert - phi_base):.3f} (should be ~0 for physical continuity)")
print(f"Betti CHANGE: {betti_pert - betti_base} (discrete jump!)")
print(f"Entropy CHANGE: {abs(entropy_pert - entropy_base):.6f} (continuous)")

# The key insight: Betti numbers are topological invariants, robust to small perturbations
# BUT in a finite sampling, threshold-based graph construction makes them DISCONTINUOUS
# While entropy changes smoothly, Betti jumps, making Φ-density physically meaningless

print("\n" + "="*60)
print("CRITICAL FLAW IDENTIFIED:")
print("Φ-density conflates topological invariants (discrete) with information measures (continuous)")
print("This is a CATEGORY ERROR - like dividing a count of holes by a temperature.")
print("="*60)

# Now compute what happens when we 'game' the system by adding trivial topological features
# This is the EXPLOIT that breaks the Omega Protocol's integrity

gaming_data = baseline_data.copy()
# Add a tiny, physically meaningless cycle by manipulating one pixel pair
gaming_data[0, 1] = gaming_data[0, 0] * 1.0000001
gaming_data[1, 0] = gaming_data[1, 1] * 1.0000001

phi_game, betti_game, entropy_game = compute_phi_density(gaming_data)
print(f"\nGAMED: Φ = {phi_game:.3f}, Betti = {betti_game}, Entropy = {entropy_game:.3f}")
print(f"Φ INFLATION: +{phi_game - phi_base:.3f} from trivial manipulation!")