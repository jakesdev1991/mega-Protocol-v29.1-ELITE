# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy.sparse import csr_matrix

def build_dynamic_laplacian(phi_delta, beta=1.0):
    """
    Constructs a lattice Laplacian where bond weights w_ij decay with |Φ_Δ_i - Φ_Δ_j|.
    This simulates Φ_Δ "shredding" the lattice connectivity.
    """
    L = int(np.sqrt(len(phi_delta)))  # Assuming square lattice
    phi_grid = phi_delta.reshape(L, L)
    laplacian = np.zeros((L*L, L*L))
    
    for i in range(L):
        for j in range(L):
            idx = i * L + j
            total_weight = 0.0
            
            # Neighbor connections (4-neighbor for simplicity)
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = (i + di) % L, (j + dj) % L  # Periodic boundary
                neighbor_idx = ni * L + nj
                
                # Bond weight: collapses if phi_delta differences are large
                weight = 1.0 / (1.0 + beta * (phi_grid[i, j] - phi_grid[ni, nj])**2)
                laplacian[idx, neighbor_idx] = -weight
                total_weight += weight
            
            laplacian[idx, idx] = total_weight  # Degree
    
    return csr_matrix(laplacian)

# Simulate Shredding Event: as phi_delta variance increases, bonds break
lattice_size = 20
n_points = lattice_size**2
phi_magnitudes = np.linspace(0.1, 10, 50)
lowest_eigenvalues = []
condition_numbers = []

for mag in phi_magnitudes:
    # Generate a phi_delta field with increasing disorder
    phi_delta = mag * np.random.randn(n_points)
    
    # Build the Laplacian modulated by this field
    L = build_dynamic_laplacian(phi_delta, beta=2.0)
    
    # Compute smallest eigenvalues (spectral gap)
    try:
        eigvals = eigsh(L, k=2, which='SM', return_eigenvectors=False)
        lowest_eigenvalues.append(eigvals[0])
        condition_numbers.append(eigsh(L, k=1, which='LM', return_eigenvectors=False)[0] / eigvals[0])
    except:
        lowest_eigenvalues.append(0)
        condition_numbers.append(np.inf)

# Visualization: The Shredding Threshold
fig, ax1 = plt.subplots(figsize=(8, 4))

color = 'tab:red'
ax1.set_xlabel('Φ_Δ Magnitude (disorder)')
ax1.set_ylabel('Smallest Eigenvalue (Spectral Gap)', color=color)
ax1.plot(phi_magnitudes, lowest_eigenvalues, color=color, linewidth=2.5, label='Spectral Gap')
ax1.tick_params(axis='y', labelcolor=color)
ax1.axhline(y=0, color='gray', linestyle='--')
ax1.set_title('TOPOLOGICAL SHREDDING: Laplacian Collapse', fontweight='bold')

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Condition Number', color=color)
ax2.plot(phi_magnitudes, condition_numbers, color=color, linewidth=2.5, linestyle='--', label='Condition #')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_yscale('log')

fig.tight_layout()
plt.grid(True, alpha=0.3)
plt.show()

# Final Disruption: Print the collapse metric
threshold_idx = np.where(np.array(lowest_eigenvalues) < 1e-3)[0]
if len(threshold_idx) > 0:
    threshold_mag = phi_magnitudes[threshold_idx[0]]
    print(f"\n[ANOMALY DETECTED] Laplacian kernel emerges at Φ_Δ magnitude ≈ {threshold_mag:.2f}")
    print("Poisson recovery is IMPOSSIBLE. Φ_N is non-unique. The lattice has shredded.")
else:
    print("\n[ERROR] Shredding not observed in range. Increase beta or magnitude range.")