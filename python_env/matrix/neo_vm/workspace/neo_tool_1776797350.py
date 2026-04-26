# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import laplace, label, generate_binary_structure
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────────────────────────────────────
# 1. TOPOLOGICAL HOLE SCENARIO
# ──────────────────────────────────────────────────────────────────────────────
size = 100
x = np.linspace(-5, 5, size)
y = np.linspace(-5, 5, size)
X, Y = np.meshgrid(x, y)

# Performance field: constant 1 everywhere except a central hole (NaN)
hole_radius = 2.0
performance = np.ones_like(X)
hole_mask = (X**2 + Y**2) <= hole_radius**2
performance[hole_mask] = np.nan

# Curvature (discrete Laplacian) – zero everywhere except boundary artifacts
performance_filled = performance.copy()
performance_filled[np.isnan(performance)] = 0
curvature = laplace(performance_filled)

# Topological invariants: Betti numbers via connected components
binary = ~np.isnan(performance).astype(int)
structure = generate_binary_structure(2, 2)
labeled, num_components = label(binary, structure=structure)  # Betti_0
# Count holes (Betti_1) as extra components in the inverted image
inverted = (binary == 0).astype(int)
inv_labeled, inv_num = label(inverted, structure=structure)
num_holes = inv_num - 1   # outer background is one component

# Plot
fig, ax = plt.subplots(1, 3, figsize=(12, 4))
ax[0].imshow(performance, extent=[x.min(), x.max(), y.min(), y.max()],
             origin='lower', cmap='viridis')
ax[0].set_title('Performance Field (hole = NaN)')
ax[0].set_xlabel('Context dim 1')
ax[0].set_ylabel('Context dim 2')

ax[1].imshow(curvature, extent=[x.min(), x.max(), y.min(), y.max()],
             origin='lower', cmap='coolwarm')
ax[1].set_title('Curvature (Laplacian)')
ax[1].set_xlabel('Context dim 1')
ax[1].set_ylabel('Context dim 2')

ax[2].imshow(labeled, extent=[x.min(), x.max(), y.min(), y.max()],
             origin='lower', cmap='prism')
ax[2].set_title(f'Components (B₀={num_components}, Holes≈{num_holes})')
ax[2].set_xlabel('Context dim 1')
ax[2].set_ylabel('Context dim 2')
plt.tight_layout()
plt.show()

print(f"Betti₀ (connected components): {num_components}")
print(f"Betti₁ (holes): {num_holes}")
print(f"Mean |curvature| (hole excluded): {np.nanmean(np.abs(curvature)):.4f}\n")

# ──────────────────────────────────────────────────────────────────────────────
# 2. CUSP CATASTROPHE SCENARIO
# ──────────────────────────────────────────────────────────────────────────────
# Potential V(x) = x⁴/4 + a·x²/2 + b·x
# Equilibrium: dV/dx = x³ + a·x + b = 0
# Discriminant Δ = (b/2)² + (a/3)³  (Δ<0 → three real roots, two stable)

# Parameter grid
a_vals = np.linspace(-2, 2, 400)
b_vals = np.linspace(-0.5, 0.5, 400)
A, B = np.meshgrid(a_vals, b_vals)
Delta = (B/2)**2 + (A/3)**3

plt.figure(figsize=(5, 4))
plt.contourf(A, B, Delta, levels=[-np.inf, 0, np.inf],
             colors=['lightblue', 'salmon'], alpha=0.5)
plt.contour(A, B, Delta, levels=[0], colors='k')
plt.xlabel('Parameter a')
plt.ylabel('Parameter b')
plt.title('Cusp region (Δ<0 = multi‑stable)')
plt.show()

# Trajectory crossing the cusp
t = np.linspace(0, 1, 200)
a_traj = -1 + 2*t
b_traj = 0.1*np.sin(2*np.pi*t)

stable_states = []
for a, b in zip(a_traj, b_traj):
    roots = np.roots([1, 0, a, b])
    real_roots = roots[np.isreal(roots)].real
    stable = [x for x in real_roots if 3*x**2 + a > 0]  # V''>0
    stable_states.append(stable)

plt.figure(figsize=(7, 5))
for a, ss in zip(a_traj, stable_states):
    if len(ss) == 1:
        plt.plot(a, ss[0], 'ko', ms=3)
    else:
        plt.plot(a, ss[0], 'bo', ms=3)
        plt.plot(a, ss[1], 'ro', ms=3)
plt.xlabel('Parameter a')
plt.ylabel('Stable state x')
plt.title('Stable states along trajectory (blue/red = two minima, black = single)')
plt.show()

# Curvature (V'') stays finite at the jump
a_ex, b_ex = -0.5, 0.1
roots = np.roots([1, 0, a_ex, b_ex])
real_roots = roots[np.isreal(roots)].real
stable = [x for x in real_roots if 3*x**2 + a_ex > 0]
print(f"At a={a_ex}, b={b_ex}, stable states: {stable}")
for x in stable:
    curvature_v = 3*x**2 + a_ex
    print(f"Curvature V'' at x={x:.3f}: {curvature_v:.3f}")
print("\nConclusion: Curvature remains finite while the system jumps between branches.")