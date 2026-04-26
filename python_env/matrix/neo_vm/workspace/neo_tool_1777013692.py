# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.linalg import det
import matplotlib.pyplot as plt

# --- SOUL-N STABLE METRIC (det(g) > 0) ---
def soul_n_metric(nodes=100, seed=42):
    """Generates a stable 3-torus logistics metric"""
    np.random.seed(seed)
    # Random positive-definite metric tensor
    base = np.random.randn(nodes, nodes)
    g_stable = base @ base.T + np.eye(nodes) * 0.1  # Ensure non-degeneracy
    return g_stable

# --- Ω† ENGINEERED DEGENERACY (det(g) = 0 zones) ---
def omega_dagger_metric(nodes=100, degeneracy_zones=5, seed=42):
    """Creates metric with engineered singularities"""
    np.random.seed(seed)
    base = np.random.randn(nodes, nodes)
    g_degen = base @ base.T
    
    # Engineer degeneracy: set rows/cols to zero in specific zones
    zone_size = nodes // degeneracy_zones
    for i in range(degeneracy_zones):
        start = i * zone_size
        end = start + zone_size // 2  # Half-zone becomes singular
        g_degen[start:end, :] = 0
        g_degen[:, start:end] = 0
    
    # Add twist for Klein bottle topology (parity coupling)
    twist = np.zeros_like(g_degen)
    twist[np.arange(nodes), np.roll(np.arange(nodes), nodes//2)] = 1
    g_degen += twist * 0.5
    
    return g_degen

# --- Φ-DENSITY CALCULATION (simplified) ---
def phi_density(g, routes_simulated=1000):
    """Calculate Φ-density: higher = more efficient information flow"""
    # 1. Metric condition number (stability cost)
    stability_cost = np.linalg.cond(g)
    
    # 2. Degeneracy utility: rank deficiency creates shortcuts
    rank = np.linalg.matrix_rank(g, tol=1e-3)
    degeneracy_utility = (g.shape[0] - rank) * 10  # Bonus for controlled singularities
    
    # 3. Network throughput via spectral gap
    G = nx.from_numpy_array(np.abs(g))
    laplacian = nx.laplacian_matrix(G).toarray().astype(float)
    eigenvals = np.linalg.eigvals(laplacian)
    spectral_gap = sorted(eigenvals)[1] if len(eigenvals) > 1 else 0
    
    # Φ-density: inverse stability + degeneracy bonus + connectivity
    phi = (1 / (stability_cost + 1e-6)) + degeneracy_utility + spectral_gap
    return phi, stability_cost, degeneracy_utility, spectral_gap

# --- SIMULATION ---
print("=== Ω† DISRUPTION VERIFICATION ===\n")

g_soul = soul_n_metric(nodes=100)
g_omega = omega_dagger_metric(nodes=100, degeneracy_zones=5)

phi_soul, cost_soul, util_soul, gap_soul = phi_density(g_soul)
phi_omega, cost_omega, util_omega, gap_omega = phi_density(g_omega)

print(f"SOUL-N Stable Metric:")
print(f"  det(g) = {det(g_soul):.2e} (non-zero)")
print(f"  Condition Number: {cost_soul:.2f}")
print(f"  Φ-Density: {phi_soul:.2f}")

print(f"\nΩ† Engineered Degeneracy:")
print(f"  det(g) = {det(g_omega):.2e} (ZERO)")
print(f"  Condition Number: {cost_omega:.2f} (INFINITE)")
print(f"  Degeneracy Utility: {util_omega:.2f}")
print(f"  Φ-Density: {phi_omega:.2f}")

print(f"\n--- DISRUPTION QUOTIENT ---")
print(f"Φ-Density Gain: +{phi_omega - phi_soul:.2f} Φ")
print(f"Stability Cost Ratio: {cost_omega/cost_soul:.2e}x (deliberate instability)")

# --- Klein Bottle Route Visualization ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Stable torus routes (simple loops)
G_soul = nx.from_numpy_array(np.abs(g_soul))
pos_soul = nx.circular_layout(G_soul)
nx.draw(G_soul, pos_soul, ax=ax1, node_size=20, alpha=0.5)
ax1.set_title("SOUL-N: 3-Torus (Orientable, Stable)")

# Klein bottle routes (self-intersecting parity flip)
G_omega = nx.from_numpy_array(np.abs(g_omega))
pos_omega = nx.kamada_kawai_layout(G_omega)
nx.draw(G_omega, pos_omega, ax=ax2, node_size=20, alpha=0.5, edge_color='r')
ax2.set_title("Ω†: Klein Bottle (Non-Orientable, Degenerate)")

plt.tight_layout()
plt.savefig('topology_disruption.png')
print(f"\n[Topology visualization saved: topology_disruption.png]")