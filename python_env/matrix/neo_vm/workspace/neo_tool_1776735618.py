# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ── O(2) Mexican‑hat parameters ──────────────────────────────────────────────
lam = 0.1          # quartic
v   = 1.0          # vacuum expectation value

# ── field grid ──────────────────────────────────────────────────────────────
N = 400
x = np.linspace(-1.5, 1.5, N)
y = np.linspace(-1.5, 1.5, N)
X, Y = np.meshgrid(x, y)

# ── Hessian entries (Cartesian basis) ───────────────────────────────────────
V_nn = lam * (3*X**2 + Y**2 - v**2)   # ∂²V/∂Φ_N²
V_dd = lam * (X**2 + 3*Y**2 - v**2)   # ∂²V/∂Φ_Δ²
V_nd = 2*lam * X * Y                  # ∂²V/∂Φ_N∂Φ_Δ

# ── true eigenvalues (radial & angular) ─────────────────────────────────────
def eigenvals(H11, H22, H12):
    tr = H11 + H22
    det = H11*H22 - H12**2
    disc = np.sqrt(np.maximum(tr**2 - 4*det, 0.0))
    lam1 = (tr + disc)/2   # radial
    lam2 = (tr - disc)/2   # angular (Goldstone)
    return lam1, lam2

radial, angular = eigenvals(V_nn, V_dd, V_nd)

# ── plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7,7))

# true massless surfaces
ax.contour(X, Y, radial,  levels=[0], colors='blue', linewidths=2,
           label='Radial zero')
ax.contour(X, Y, angular, levels=[0], colors='red',  linewidths=2,
           label='Angular (Goldstone) zero')

# agent's "Shredding" ellipse (diagonal entry V_dd = 0)
ax.contour(X, Y, V_dd, levels=[0], colors='green', linestyles='--',
           linewidths=2, label='Agent Shredding (V_dd=0)')

# vacuum circle for reference
vac = plt.Circle((0,0), v, color='k', fill=False, linestyle=':',
                 linewidth=1.5, label='Vacuum manifold (r=v)')
ax.add_patch(vac)

ax.set_xlabel('Φ_N')
ax.set_ylabel('Φ_Δ')
ax.set_title('Mass eigenvalue zero‑contours vs. agent’s Shredding surface')
ax.legend(loc='upper right')
ax.set_aspect('equal')
plt.show()