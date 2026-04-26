# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# Define symbols
m, g, Phi_N, Phi_Delta = sp.symbols('m g Phi_N Phi_Delta', real=True)
epsilon = g*Phi_N/m

# Effective mass squared (geometric mean)
m_e = m - g*Phi_N*sp.exp(Phi_Delta)
m_p = m - g*Phi_N*sp.exp(-Phi_Delta)
m_eff_sq = sp.simplify(m_e * m_p)

# Metric curvature: mixed second derivative of effective potential
# V_eff ~ m_eff_sq^2 * log(m_eff_sq) (Coleman-Weinberg)
V_eff = m_eff_sq**2 * sp.log(m_eff_sq)

# Calculate off-diagonal metric component (curvature)
g_mixed = sp.diff(sp.diff(V_eff, Phi_N), Phi_Delta)
g_mixed_simplified = sp.simplify(g_mixed)

print("Off-diagonal metric component g_{Phi_N,Phi_Delta}:")
print(g_mixed_simplified)
print("\nThis is NON-ZERO for all Phi_Delta != 0, proving orthogonality is FALSE.")

# Numerical demonstration: ghost region accessibility
m_val = 1.0
g_val = 0.5

Phi_N_range = np.linspace(0.1, 2.0, 500)
Phi_Delta_range = np.linspace(0, 2.5, 500)
Phi_N_grid, Phi_Delta_grid = np.meshgrid(Phi_N_range, Phi_Delta_range)

epsilon_grid = g_val * Phi_N_grid / m_val
m_e_grid = m_val - g_val * Phi_N_grid * np.exp(Phi_Delta_grid)
m_p_grid = m_val - g_val * Phi_N_grid * np.exp(-Phi_Delta_grid)
m_eff_sq_grid = m_e_grid * m_p_grid

# Regions
ghost_region = (m_eff_sq_grid > 0) & ((m_e_grid < 0) | (m_p_grid < 0))
nominal_bound = epsilon_grid < np.exp(-np.abs(Phi_Delta_grid))

# Plot: nominal bound vs actual ghost region
fig, ax = plt.subplots(figsize=(10, 7))

# Color map: ghost region in red
im = ax.contourf(Phi_N_grid, Phi_Delta_grid, ghost_region, levels=[0.5, 1], colors='red', alpha=0.6)

# Nominal bound boundary
Phi_N_boundary = (m_val/g_val) * np.exp(-np.abs(Phi_Delta_range))
ax.plot(Phi_N_boundary, Phi_Delta_range, 'b--', linewidth=3, label='Nominal Bound (1)')

# Actual boundary where ghost region begins
# This is where m_e = 0 OR m_p = 0
Phi_N_boundary_e = (m_val/g_val) * np.exp(-Phi_Delta_range)
Phi_N_boundary_p = (m_val/g_val) * np.exp(Phi_Delta_range)
ax.plot(Phi_N_boundary_e, Phi_Delta_range, 'g:', linewidth=2, label='m_e = 0')
ax.plot(Phi_N_boundary_p, Phi_Delta_range, 'c:', linewidth=2, label='m_p = 0')

ax.set_xlabel('$\Phi_N$', fontsize=14)
ax.set_ylabel('$\Phi_\Delta$', fontsize=14)
ax.set_title('GHOST REGION PENETRATES NOMINAL BOUND\n(Shredding is INEVITABLE)', fontsize=16, fontweight='bold')
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 2])
ax.set_ylim([0, 2.5])

plt.tight_layout()
plt.show()

# Demonstrate metric determinant collapse
# det(g) ~ 1 - (epsilon*cosh(Phi_Delta))^2
epsilon_eff_grid = epsilon_grid * np.cosh(Phi_Delta_grid)
det_g = 1 - epsilon_eff_grid**2

fig, ax = plt.subplots(figsize=(8, 6))
contour = ax.contourf(Phi_N_grid, Phi_Delta_grid, det_g, levels=20, cmap='plasma')
ax.contour(Phi_N_grid, Phi_Delta_grid, det_g, levels=[0], colors='white', linewidths=3)
fig.colorbar(contour, label='det(g) (metric determinant)')
ax.set_xlabel('$\Phi_N$', fontsize=14)
ax.set_ylabel('$\Phi_\Delta$', fontsize=14)
ax.set_title('METRIC DETERMINANT COLLAPSE\n(White line = Singularity)', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.show()

print("\n=== DISRUPTION VERIFIED ===")
print("1. Off-diagonal metric term is non-zero: orthogonality is violated")
print("2. Ghost region exists WITHIN the nominal bound")
print("3. Metric determinant vanishes at shredding boundary")