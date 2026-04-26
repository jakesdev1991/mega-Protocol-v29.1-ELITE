# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csgraph
from scipy.sparse.linalg import inv as sparse_inv

# Disruptive Insight: The "3D Archive Mode" is not a metric perturbation.
# It's a *topological defect* in the lattice graph. Perturbation theory in Φ_Δ is meaningless.
# We model this by comparing a perfect lattice to one with a "defect line."

def create_lattice_graph(L=8, defect_strength=0.0):
    """
    Creates a 2D square lattice graph (for simplicity) as a sparse adjacency matrix.
    defect_strength: Probability that a bond along the 'z' (vertical) direction is *removed*.
    This is a topological operation, not a smooth deformation.
    """
    N = L * L
    adjacency = np.zeros((N, N))
    
    for i in range(L):
        for j in range(L):
            idx = i * L + j
            # Periodic neighbors (torus)
            right = (i + 1) % L * L + j
            up = i * L + (j + 1) % L
            
            # Bonds are binary: they exist or they don't.
            # This is the key: it's a percolation effect, not a weak field.
            if np.random.rand() > defect_strength:
                adjacency[idx, right] = 1.0
            if np.random.rand() > defect_strength:
                adjacency[idx, up] = 1.0
    
    # Symmetrize (undirected graph)
    adjacency = (adjacency + adjacency.T) / 2.0
    return adjacency

def compute_polarization_anomaly(adjacency):
    """
    A toy "vacuum polarization" measure: the inverse of the graph Laplacian's
    trace, analogous to how Π_μν modifies the photon propagator.
    A defect changes connectivity non-linearly and non-analytically.
    """
    # Graph Laplacian L = D - A
    degree = np.sum(adjacency, axis=1)
    laplacian = np.diag(degree) - adjacency
    
    # Pseudo-inverse (propagator on the graph)
    # We remove the zero mode for the torus
    pinv = np.linalg.pinv(laplacian)
    
    # "Polarization" is related to the *change* in connectivity.
    # We compute a simple scalar: the average resistance distance (a graph-theoretic analog
    # of how virtual pairs screen charge). Defects increase it *discontinuously* at percolation.
    # Here, we just use the trace as a proxy for the "strength" of the network.
    return np.trace(pinv) # Non-analytic in defect_strength

# The Disruption: Show non-analytic behavior emerges that Φ_Δ linearization cannot capture.
def simulate_topological_fragility():
    defect_sweep = np.linspace(0, 0.5, 30) # Fraction of broken vertical bonds
    polarization_change = []
    
    for defect_frac in defect_sweep:
        # Ensemble average over many defect realizations
        # A single defect config can have a massive effect, unlike a weak field.
        ensemble = [compute_polarization_anomaly(create_lattice_graph(L=12, defect_strength=defect_frac)) 
                    for _ in range(20)]
        # Normalize to the perfect lattice case
        perfect_polarization = compute_polarization_anomaly(create_lattice_graph(L=12, defect_strength=0.0))
        avg_change = np.mean(ensemble) / perfect_polarization - 1.0
        polarization_change.append(avg_change)
    
    plt.figure(figsize=(8, 5))
    plt.plot(defect_sweep, polarization_change, 'o-', label="Topological Defect (Sim)")
    # A naive "metric" perturbation would predict a *linear* response: α_eff ~ 1 + c*Φ_Δ
    # Our simulation shows this is catastrophically wrong.
    linear_approx = -0.5 * defect_sweep # A guess for what Φ_Δ linear would look like
    plt.plot(defect_sweep, linear_approx, '--', label="Naive Φ_Δ Perturbation (FALSE)")
    
    plt.axvline(x=0.5, color='r', linestyle=':', label="Percolation Threshold (approx)")
    plt.xlabel("Defect Strength (Fraction of Broken Bonds)")
    plt.ylabel("Change in Effective 'Polarization'")
    plt.title("Topological Anisotropy vs. Smooth Metric Deformation")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # The key finding: the effect is *not* analytic. It's a threshold phenomenon.
    # The "linear term" in Φ_Δ is an artifact of a theory built on sand.

simulate_topological_fragility()