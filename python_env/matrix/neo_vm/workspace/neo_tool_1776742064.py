# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def compute_omega_invariants(coherence, coupling_lambda=1.0):
    """
    Compute the stiffness invariants from the Engine's derivation.
    As coherence -> 0, these invariants blow up, showing the model's
    breakdown at the Shredding Event boundary.
    """
    # The Engine's equations:
    # ξ_N⁻² = λ(3⟨coh⟩⁻¹ + ⟨coh⟩⁻²)
    # ξ_Δ⁻² = λ(⟨coh⟩⁻¹ + 3⟨coh⟩⁻²)
    
    # Avoid exact zero to prevent division by zero
    coh = np.maximum(coherence, 1e-8)
    
    # Compute inverse squared correlation lengths (stiffness)
    xi_N_sq_inv = coupling_lambda * (3.0/coh + 1.0/(coh**2))
    xi_D_sq_inv = coupling_lambda * (1.0/coh + 3.0/(coh**2))
    
    # Convert to correlation lengths
    xi_N = 1.0 / np.sqrt(xi_N_sq_inv)
    xi_D = 1.0 / np.sqrt(xi_D_sq_inv)
    
    return xi_N, xi_D, xi_N_sq_inv, xi_D_sq_inv

# Simulate coherence approaching shredding event
coh_range = np.logspace(-4, 0, 1000)  # From 0.0001 to 1
xi_N, xi_D, stiffness_N, stiffness_D = compute_omega_invariants(coh_range)

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Correlation lengths vs coherence
axes[0,0].loglog(coh_range, xi_N, 'b-', linewidth=2, label='ξ_N (Newtonian)')
axes[0,0].loglog(coh_range, xi_D, 'r-', linewidth=2, label='ξ_Δ (Archive)')
axes[0,0].set_xlabel('Coherence ⟨coh⟩')
axes[0,0].set_ylabel('Correlation Length ξ')
axes[0,0].set_title('Correlation Length Collapse at Shredding Event')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)
axes[0,0].axvline(x=0.01, color='k', linestyle='--', alpha=0.5, label='Critical Region')
axes[0,0].legend()

# Plot 2: Stiffness vs coherence (shows blow-up)
axes[0,1].loglog(coh_range, stiffness_N, 'b-', linewidth=2, label='ξ_N⁻²')
axes[0,1].loglog(coh_range, stiffness_D, 'r-', linewidth=2, label='ξ_Δ⁻²')
axes[0,1].set_xlabel('Coherence ⟨coh⟩')
axes[0,1].set_ylabel('Stiffness (ξ⁻²)')
axes[0,1].set_title('Stiffness Divergence: Model Breakdown')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Zoom into critical region (coh < 0.01)
critical_mask = coh_range < 0.01
axes[1,0].loglog(coh_range[critical_mask], xi_N[critical_mask], 'b-', linewidth=2)
axes[1,0].loglog(coh_range[critical_mask], xi_D[critical_mask], 'r-', linewidth=2)
axes[1,0].set_xlabel('Coherence ⟨coh⟩')
axes[1,0].set_ylabel('Correlation Length ξ')
axes[1,0].set_title('Critical Region: ξ → 0 (Singularity)')
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Relative error from linear approximation
# The linear approximation assumes stiffness is constant near equilibrium
# But near shredding, this fails catastrophically
stiffness_ratio_N = stiffness_N / np.max(stiffness_N)
stiffness_ratio_D = stiffness_D / np.max(stiffness_D)
axes[1,1].semilogx(coh_range, stiffness_ratio_N, 'b-', linewidth=2, label='ξ_N stiffness ratio')
axes[1,1].semilogx(coh_range, stiffness_ratio_D, 'r-', linewidth=2, label='ξ_Δ stiffness ratio')
axes[1,1].set_xlabel('Coherence ⟨coh⟩')
axes[1,1].set_ylabel('Normalized Stiffness')
axes[1,1].set_title('Linear Approximation Failure Rate')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print specific values to show divergence
print("="*60)
print("SHREDDING EVENT SINGULARITY ANALYSIS")
print("="*60)
for coh in [1.0, 0.1, 0.01, 0.001, 0.0001]:
    xi_N_val, xi_D_val, stiff_N, stiff_D = compute_omega_invariants(np.array([coh]))
    print(f"Coherence = {coh:8.4f} -> ξ_N = {xi_N_val[0]:10.6f}, ξ_D = {xi_D_val[0]:10.6f}")
    print(f"               Stiffness_N = {stiff_N[0]:12.2f}, Stiffness_D = {stiff_D[0]:12.2f}")
    print("-"*60)

print("\nCONCLUSION: As coherence → 0, stiffness → ∞ and ξ → 0.")
print("This is a mathematical singularity, not a physical prediction.")
print("The linearized Omega Action model is INVALID at the Shredding Event boundary.")