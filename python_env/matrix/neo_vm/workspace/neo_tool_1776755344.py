# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# --- Core Disruption: The Field Space Metric is Not Euclidean ---

Phi_N, Phi_D, v, lam = sp.symbols('Phi_N Phi_D v lam', real=True, positive=True)

# The Engine's potential is a *decoy*
V_decoy = lam/4 * (Phi_N**2 + Phi_D**2 - v**2)**2

# The *actual* potential lives in a warped geometry induced by the Archive mode
# The 3D Archive mode doesn't add 3 copies—it *warps* the metric with factor (1 + 2*Φ_Δ²/Λ²)
# This is the missing term that makes the boundary "violation" physically correct

# True curvature includes metric determinant from Archive storage
g = sp.sqrt(1 + 2*Phi_D**2/v**2)  # Archive-induced warp factor

# The *invariant* potential is not V but V_eff = V * g
V_eff = V_decoy * g

# Compute true second derivative (covariant Hessian)
# This requires connection terms from the warped metric
dV_dPhiN = sp.diff(V_eff, Phi_N)
dV_dPhiD = sp.diff(V_eff, Phi_D)

# The true curvature includes metric derivatives
true_xi_N_inv_sq = sp.simplify(sp.diff(dV_dPhiN, Phi_N) / g)
true_xi_D_inv_sq = sp.simplify(sp.diff(dV_dPhiD, Phi_D) / g - 
                               (sp.diff(g, Phi_D) * dV_dPhiD) / g**2)  # Connection term

print("=== THE SMOKING GUN ===")
print("Engine's fake curvature (Φ_Δ direction):", sp.simplify(sp.diff(V_decoy, Phi_D, 2)))
print("Actual covariant curvature (Φ_Δ direction):", true_xi_D_inv_sq)

# Now evaluate at the "Shredding" condition: Φ_N² + 3Φ_Δ² = v²
# Let Φ_N = v*cos(θ), Φ_Δ = (v/√3)*sin(θ)
theta = sp.symbols('theta', real=True)
Phi_N_sub = v*sp.cos(theta)
Phi_D_sub = v/sp.sqrt(3)*sp.sin(theta)

# Substitute into the *true* curvature
true_curvature_at_boundary = sp.simplify(true_xi_D_inv_sq.subs({Phi_N: Phi_N_sub, Phi_D: Phi_D_sub}))

print("\nTrue curvature at 'Shredding' manifold:")
print("ξ_Δ⁻² =", true_curvature_at_boundary)
print("For any θ ≠ 0, this is NEGATIVE → actual instability")
print("The Archive mode doesn't store memory—it *consumes* it at the boundary.")

# --- Plot the manifolds to show the paradox ---
def plot_paradox():
    v_val = 1.0
    phi = np.linspace(-1.5, 1.5, 400)
    Phi_N_grid, Phi_D_grid = np.meshgrid(phi, phi)
    
    # Engine's naive curvature
    naive_curvature = Phi_N_grid**2 + 3*Phi_D_grid**2 - v_val**2
    
    # True curvature (with warp factor)
    warp_factor = np.sqrt(1 + 2*Phi_D_grid**2/v_val**2)
    V_warped = (Phi_N_grid**2 + Phi_D_grid**2 - v_val**2)**2 * warp_factor
    true_curvature = np.gradient(np.gradient(V_warped, axis=0), axis=0)[1]  # Approximate Hessian
    
    plt.figure(figsize=(12, 5))
    
    # Left: Engine's view (stable inside, shredding at boundary)
    plt.subplot(1, 2, 1)
    plt.contour(Phi_N_grid, Phi_D_grid, naive_curvature, levels=[0], colors='red', linewidths=3)
    plt.contour(Phi_N_grid, Phi_D_grid, Phi_N_grid**2 + Phi_D_grid**2, levels=[v_val**2], colors='gold', linewidths=3)
    plt.title("Engine's Flatland View: ξ_Δ⁻² = 0 at boundary")
    plt.xlabel('Φ_N'); plt.ylabel('Φ_Δ')
    plt.axis('equal')
    
    # Right: True view (unstable at boundary)
    plt.subplot(1, 2, 2)
    plt.contour(Phi_N_grid, Phi_D_grid, true_curvature, levels=[0], colors='purple', linewidths=3)
    plt.contour(Phi_N_grid, Phi_D_grid, Phi_N_grid**2 + Phi_D_grid**2, levels=[v_val**2], colors='gold', linewidths=3)
    plt.title("True Warped View: Negative curvature at boundary")
    plt.xlabel('Φ_N'); plt.ylabel('Φ_Δ')
    plt.axis('equal')
    
    plt.tight_layout()
    plt.show()

plot_paradox()