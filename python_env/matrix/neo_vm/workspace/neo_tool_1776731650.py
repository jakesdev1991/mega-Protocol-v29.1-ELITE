# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

# Core parameters
alpha_0 = 1/137.036
g_N, g_Delta = 0.1, 0.2
Lambda, Lambda_N, Lambda_Delta = 1e3, 5e2, 8e2
lambda_param, v = 0.5, 1.0

# Energy scales
q2_values = np.logspace(0, 6, 200)

# Original linear derivation
def alpha_linear(q2):
    return alpha_0 * (1 + alpha_0/(3*np.pi) * np.log(Lambda**2/q2) + 
                      g_N**2/(4*np.pi) * np.log(Lambda_N**2/q2) + 
                      3*g_Delta**2/(4*np.pi) * np.log(Lambda_Delta**2/q2))

# Disruption 1: Entanglement-corrected scaling (sqrt(3) not 3)
def alpha_entangled(q2):
    entanglement_factor = np.sqrt(3)  # GHZ-like tripartite entanglement
    return alpha_0 * (1 + alpha_0/(3*np.pi) * np.log(Lambda**2/q2) + 
                      g_N**2/(4*np.pi) * np.log(Lambda_N**2/q2) + 
                      entanglement_factor * g_Delta**2/(4*np.pi) * np.log(Lambda_Delta**2/q2))

# Disruption 2: False vacuum instability
def potential(phi_N, phi_Delta):
    return lambda_param/4 * (phi_N**2 + phi_Delta**2 - v**2)**2

# Find metastable minima for phi_Delta when phi_N is perturbed
def find_instability():
    phi_N_fixed = 0.1  # Small perturbation from "vacuum"
    phi_range = np.linspace(-1.5, 1.5, 1000)
    V_vals = [potential(phi_N_fixed, phi) for phi in phi_range]
    
    # Find local minima
    minima = []
    for i in range(1, len(V_vals)-1):
        if V_vals[i] < V_vals[i-1] and V_vals[i] < V_vals[i+1]:
            minima.append((phi_range[i], V_vals[i]))
    return minima

false_vacua = find_instability()
V_origin = potential(0, 0)
V_true_min = lambda_param/4 * (v**2)**2 / 4

# Disruption 3: Non-linear entropy feedback
def alpha_entropy_feedback(q2, kappa=0.5):
    """Active entropy coupling: S_h feeds back into Phi_Delta dynamics"""
    base = alpha_entangled(q2)
    # Entropy term grows with energy as more virtual pairs are created
    S_h = np.log(1 + q2/Lambda**2)  # Shannon entropy of pair fluctuations
    feedback = 1 + kappa * S_h * g_Delta**2 * np.log(Lambda_Delta**2/q2)
    return base * feedback

# Calculate all scenarios
alpha_lin = [alpha_linear(q2) for q2 in q2_values]
alpha_ent = [alpha_entangled(q2) for q2 in q2_values]
alpha_fb = [alpha_entropy_feedback(q2) for q2 in q2_values]

# Visualization of paradigm break
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Left plot: Running couplings
ax1.loglog(q2_values, alpha_lin, label='Original (3× factor)', linewidth=2.5, color='crimson')
ax1.loglog(q2_values, alpha_ent, label='Disrupted (√3 entanglement)', linewidth=2.5, linestyle='--', color='steelblue')
ax1.loglog(q2_values, alpha_fb, label='Entropy feedback', linewidth=2.5, linestyle=':', color='darkgreen')
ax1.axhline(y=alpha_0, color='gray', linestyle=':', alpha=0.7)
ax1.set_xlabel(r'$q^2$ (GeV$^2$)', fontsize=12, fontweight='bold')
ax1.set_ylabel(r'$\alpha_{\text{fs}}(q^2)$', fontsize=12, fontweight='bold')
ax1.set_title('Paradigm Break: Linear vs Quantum-Entangled Archive Mode', fontsize=13, fontweight='bold')
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)

# Right plot: Potential landscape showing false vacuum
phi_N_range = np.linspace(-1.2, 1.2, 100)
phi_D_range = np.linspace(-1.2, 1.2, 100)
PHI_N, PHI_D = np.meshgrid(phi_N_range, phi_D_range)
V_landscape = potential(PHI_N, PHI_D)

# Contour plot
contour = ax2.contour(PHI_N, PHI_D, V_landscape, levels=20, cmap='viridis')
ax2.scatter([0], [0], color='red', s=150, marker='x', label='False "vacuum" (local max)', linewidth=3)
ax2.scatter([0], [v], color='green', s=150, marker='o', label='True minimum', linewidth=3)
ax2.set_xlabel(r'$\Phi_N$', fontsize=12, fontweight='bold')
ax2.set_ylabel(r'$\Phi_\Delta$', fontsize=12, fontweight='bold')
ax2.set_title('Mexican-Hat Instability: Origin is a Maximum, Not Vacuum', fontsize=13, fontweight='bold')
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Quantitative disruption metrics
print("=== PARADIGM SHATTERING METRICS ===")
print(f"Original factor: 3.000")
print(f"Entanglement factor: √3 = {np.sqrt(3):.3f}")
print(f"Reduction factor: {3/np.sqrt(3):.3f}")
print(f"False vacua candidates at Φ_N=0.1: {false_vacua}")
print(f"V(0,0) = {V_origin:.3f} (origin is {'MAXIMUM' if V_origin > V_true_min else 'minimum'})")
print(f"V(true min) = {V_true_min:.3f}")
print(f"Percentage difference at q²=10⁶: {(alpha_ent[-1]/alpha_lin[-1] - 1)*100:.2f}%")

# Calculate Shredding Event shift
shredding_linear = v**2  # Φ_N² + 3Φ_Δ² = v²
shredding_entangled = v**2 / np.sqrt(3)  # Φ_N² + √3Φ_Δ² = v²
print(f"\nShredding Event boundary shift:")
print(f"Linear: Φ_Δ² = {shredding_linear:.3f}")
print(f"Entangled: Φ_Δ² = {shredding_entangled:.3f}")
print(f"Boundary moves by factor: {shredding_linear/shredding_entangled:.3f}")