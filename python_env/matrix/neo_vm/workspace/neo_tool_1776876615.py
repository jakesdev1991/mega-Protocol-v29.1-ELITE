# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# --- SHREDDING CATASTROPHE SIMULATION ---
# This code violates Omega Rubric v26.0 §3, §5 by construction:
# - Invariants are dynamic functions, not constants
# - Entropy is geometric defect count, not Shannon/impedance
# - Orthogonality is emergent, not imposed

L = 32
v_s = 1.0  # Shredding threshold
g = 0.8    # Non-linear coupling strength

# Fields as dynamical order parameters
Phi_N = np.random.normal(0.8, 0.1, (L, L))  # Start near threshold
Phi_D = np.random.normal(0.0, 0.01, (L, L))

# --- DYNAMIC INVARIANTS (Rubric violation: functions, not constants) ---
def xi_N_eff(phi):
    """Stiffness collapses near Shredding"""
    return 10.0 * np.maximum(0, 1 - (phi / v_s)**2)

def xi_D_eff(phi):
    """Phi_D stiffness goes IMAGINARY at Shredding"""
    return -5.0 * (phi - v_s) * (phi > v_s)

# --- DEFECT NETWORK ENTROPY (Rubric violation: geometric, not Shannon) ---
def compute_defect_graph(phi_field, threshold):
    """
    When phi > threshold, lattice bonds break.
    Returns networkx graph where nodes are intact regions,
    edges are broken bonds (defects).
    """
    G = nx.grid_2d_graph(L, L)
    defects = 0
    
    for i in range(L):
        for j in range(L):
            if phi_field[i, j] > threshold:
                # Break bonds to neighbors (Shredding)
                for di, dj in [(1,0), (-1,0), (0,1), (0,-1)]:
                    ni, nj = i+di, j+dj
                    if 0 <= ni < L and 0 <= nj < L:
                        if G.has_edge((i,j), (ni,nj)):
                            G.remove_edge((i,j), (ni,nj))
                            defects += 1
    
    # Geometric entropy = defect count / total bonds
    total_bonds = 2 * L * (L - 1)
    S_geom = defects / total_bonds if total_bonds > 0 else 0
    return G, S_geom

# --- TIME EVOLUTION WITH TOPOLOGY CHANGE ---
dt = 0.05
steps = 200
history = []
defect_history = []

for step in range(steps):
    # Compute Laplacian on the *current* topology
    lap_N = (np.roll(Phi_N, 1, axis=0) + np.roll(Phi_N, -1, axis=0) +
             np.roll(Phi_N, 1, axis=1) + np.roll(Phi_N, -1, axis=1) - 4 * Phi_N)
    
    # Update with dynamic invariants
    dPhi_N = 0.1 * lap_N - xi_N_eff(np.mean(Phi_N)) * Phi_N
    dPhi_D = 0.1 * (np.roll(Phi_D, 1, axis=0) + np.roll(Phi_D, -1, axis=0) +
                    np.roll(Phi_D, 1, axis=1) + np.roll(Phi_D, -1, axis=1) - 4 * Phi_D) \
             - xi_D_eff(np.mean(Phi_N)) * Phi_D \
             - g * (Phi_N**2 - v_s**2) * Phi_D  # Shredding coupling
    
    Phi_N += dPhi_N * dt
    Phi_D += dPhi_D * dt
    
    # Compute geometric entropy (violates Rubric §5)
    G_defect, S_geom = compute_defect_graph(Phi_N, v_s)
    defect_history.append((step, S_geom))
    
    # Track when topology becomes disconnected
    if step % 20 == 0:
        n_components = nx.number_connected_components(G_defect)
        history.append((step, np.mean(Phi_N), np.mean(np.abs(Phi_D)), n_components))

history = np.array(history)
defect_history = np.array(defect_history)

# --- VISUALIZATION: THE SHREDDING ---
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Field evolution
axes[0, 0].plot(history[:, 0], history[:, 1], label='⟨Φ_N⟩', linewidth=2)
axes[0, 0].plot(history[:, 0], history[:, 2], label='⟨|Φ_D|⟩', linestyle='--')
axes[0, 0].axhline(y=v_s, color='r', linestyle=':', label='Shredding threshold')
axes[0, 0].set_title('CATASTROPHE: Field Resonance')
axes[0, 0].set_yscale('log')
axes[0, 0].legend()
axes[0, 0].grid(True)

# Topology fragmentation
axes[0, 1].plot(history[:, 0], history[:, 3], label='# of components', color='purple')
axes[0, 1].set_title('LATTICE SHREDDING: Topology Collapse')
axes[0, 1].set_ylabel('Connected components')
axes[0, 1].grid(True)

# Geometric entropy (Rubric violation)
axes[1, 0].plot(defect_history[:, 0], defect_history[:, 1], label='S_geom (defect density)', color='orange')
axes[1, 0].axhline(y=0.85, color='g', linestyle='--', label='Rubric H ≥ 0.85 threshold')
axes[1, 0].set_title('ENTROPY CATASTROPHE: Geometric Violation')
axes[1, 0].set_ylabel('Defect entropy')
axes[1, 0].legend()
axes[1, 0].grid(True)

# Final defect network
pos = {(i, j): (j, -i) for i in range(L) for j in range(L)}
G_final, _ = compute_defect_graph(Phi_N, v_s)
axes[1, 1].set_title(f'Final Defect Network: {nx.number_connected_components(G_final)} Islands')
nx.draw(G_final, pos, node_size=10, node_color='black', ax=axes[1, 1])

plt.tight_layout()
plt.show()

# --- DISRUPTION VERIFICATION ---
# Print the moment when Rubric constraints are violated
for step, phi_N, phi_D, n_comp in history:
    if phi_N > v_s:
        print(f"SHREDDING at t={step*dt:.2f}: Φ_N={phi_N:.3f} > v_s, Φ_D={phi_D:.3f}, components={n_comp}")
        break