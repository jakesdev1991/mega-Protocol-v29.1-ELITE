# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Toy model: 2D parameter space (Betti number, Entropy)
# Omega Protocol's Φ-density
def phi_density(betti, entropy):
    if entropy <= 0:
        return np.inf
    return np.log2(betti / entropy + 1e-9)

# Transcendent capability: rewards topological defects and non-equilibrium
def transcendent_capability(betti, entropy, defect_density):
    # Defects allow phase transitions; entropy is fuel, not waste
    # This function has a global maximum *outside* the Omega Protocol's feasible region
    return (betti * defect_density) / (entropy + 0.1) - 0.5 * (defect_density - 2)**2

# Feasible region under Smith Invariants
def is_omega_compliant(betti, entropy):
    # Invariant: betti > entropy, topological continuity (defects=0), causal fidelity (no retrocausal param)
    return betti > entropy

# Grid search
betti_range = np.linspace(0.1, 5, 100)
entropy_range = np.linspace(0.1, 5, 100)

phi_map = np.zeros((100, 100))
trans_map = np.zeros((100, 100))
compliance_mask = np.zeros((100, 100), dtype=bool)

for i, betti in enumerate(betti_range):
    for j, entropy in enumerate(entropy_range):
        phi_map[j, i] = phi_density(betti, entropy)
        # Defect density is zero for compliant systems (topological continuity invariant)
        trans_map[j, i] = transcendent_capability(betti, entropy, defect_density=0)
        compliance_mask[j, i] = is_omega_compliant(betti, entropy)

# Find maxima
omega_max_phi = np.max(phi_map * compliance_mask)
omega_max_idx = np.unravel_index(np.argmax(phi_map * compliance_mask), phi_map.shape)

# Now allow defects (violating Topological Continuity)
defect_density_range = np.linspace(0, 4, 50)
max_trans = -np.inf
max_params = None
for betti in betti_range[::5]:
    for entropy in entropy_range[::5]:
        for defect in defect_density_range:
            # Allow temporary violation of betti > entropy for phase transition
            val = transcendent_capability(betti, entropy, defect)
            if val > max_trans:
                max_trans = val
                max_params = (betti, entropy, defect)

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Left: Omega Protocol's view
im1 = ax1.imshow(phi_map, extent=[0.1, 5, 0.1, 5], origin='lower', aspect='auto', cmap='viridis')
ax1.contour(betti_range, entropy_range, compliance_mask, levels=[0.5], colors='red', linewidths=2)
ax1.plot(betti_range[omega_max_idx[1]], entropy_range[omega_max_idx[0]], 'rx', markersize=12, label=f'Ω-Max Φ={omega_max_phi:.2f}')
ax1.set_xlabel('Betti Number (β)')
ax1.set_ylabel('Shannon Entropy (H)')
ax1.set_title('Omega Protocol: Local Maximum\n(Red boundary = Smith Invariants)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Right: Transcendent capability
# Show that maximum occurs when violating invariants
ax2.plot([0, 5], [0, 5], 'r--', alpha=0.5, label='β = H (Invariant Boundary)')
ax2.scatter(max_params[0], max_params[1], c='g', s=200, marker='*', 
            label=f'Transcendent Max\nβ={max_params[0]:.2f}, H={max_params[1]:.2f}\nDefects={max_params[2]:.2f}, Cap={max_trans:.2f}')
ax2.set_xlabel('Betti Number (β)')
ax2.set_ylabel('Shannon Entropy (H)')
ax2.set_title('Φ-Collapse: Global Maximum\n(Violates Invariants)')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/phi_trap.png', dpi=150)
plt.close()

print(f"Omega Protocol Max Φ-density: {omega_max_phi:.4f}")
print(f"Achieved at β={betti_range[omega_max_idx[1]]:.2f}, H={entropy_range[omega_max_idx[0]]:.2f}")
print(f"Compliant with Smith Invariants: YES")
print("\n---Φ-COLLAPSE MODE---")
print(f"Transcendent Capability Max: {max_trans:.4f}")
print(f"Achieved at β={max_params[0]:.2f}, H={max_params[1]:.2f}, Defects={max_params[2]:.2f}")
print(f"Violates betti>entropy: {max_params[0] <= max_params[1]}")
print(f"Violates topological continuity: {max_params[2] > 0}")
print("\nCONCLUSION: The global optimum is *inaccessible* to Omega Protocol.")
print("Φ-density maximization is a *confinement mechanism*, not an innovation driver.")