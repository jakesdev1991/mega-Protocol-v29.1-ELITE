# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Shredding Flaw Verification
===========================
This script computes:
1. The 'fake' eigenvalue xi_Delta^{-2} from the frozen Hessian.
2. The true field-space metric eigenvalues including the dilaton factor.
3. The locus where the metric eigenvalue vanishes (real shredding).
"""

import numpy as np
import matplotlib.pyplot as plt

# Parameters (in units where v=1)
lam = 1.0
v = 1.0
M = 2.0  # dilaton scale

# Field grids
N_pts = 400
Phi_N = np.linspace(0.1, 1.5, N_pts)  # avoid Phi_N=0 singularity
Phi_D = np.linspace(0.0, 1.2, N_pts)
Phi_N_grid, Phi_D_grid = np.meshgrid(Phi_N, Phi_D)

# -------------------------------------------------------------
# 1. Fake eigenvalue from frozen Hessian (as in the original derivation)
# -------------------------------------------------------------
xi_fake_inv_sq = lam * (Phi_N_grid**2 + 3 * Phi_D_grid**2 - v**2)

# -------------------------------------------------------------
# 2. True field-space metric (including dilaton psi = ln(Phi_N/v))
# -------------------------------------------------------------
psi_grid = np.log(Phi_N_grid / v)

# Metric components g_{ab} = diag(e^{2psi}, e^{-2psi})
g_NN = np.exp(2 * psi_grid)
g_DD = np.exp(-2 * psi_grid)

# Mass matrix from potential curvature (second derivatives)
V_NN = lam * (3 * Phi_N_grid**2 + Phi_D_grid**2 - v**2)
V_DD = lam * (Phi_N_grid**2 + 3 * Phi_D_grid**2 - v**2)
V_ND = 2 * lam * Phi_N_grid * Phi_D_grid  # off-diagonal piece omitted in original

# Full mass-squared matrix M^2_{ab} = g^{ac} V_{cb} (no sum)
# For simplicity we evaluate eigenvalues of the matrix:
#   [ V_NN/g_NN   V_ND/sqrt(g_NN*g_DD) ]
#   [ V_ND/sqrt(g_NN*g_DD)   V_DD/g_DD ]
inv_g_NN = 1.0 / g_NN
inv_g_DD = 1.0 / g_DD
sqrt_g = np.sqrt(g_NN * g_DD)

# Build 2x2 matrices for each grid point
mass_matrix = np.empty((N_pts, N_pts, 2, 2))
mass_matrix[:, :, 0, 0] = V_NN * inv_g_NN
mass_matrix[:, :, 1, 1] = V_DD * inv_g_DD
mass_matrix[:, :, 0, 1] = V_ND / sqrt_g
mass_matrix[:, :, 1, 0] = V_ND / sqrt_g

# Compute eigenvalues
eig1 = np.empty_like(Phi_N_grid)
eig2 = np.empty_like(Phi_N_grid)
for i in range(N_pts):
    for j in range(N_pts):
        w, _ = np.linalg.eig(mass_matrix[i, j, :, :])
        # Sort ascending
        w_sorted = np.sort(w)
        eig1[i, j] = w_sorted[0]
        eig2[i, j] = w_sorted[1]

# -------------------------------------------------------------
# 3. Identify shredding loci
# -------------------------------------------------------------
# Fake shredding: xi_fake_inv_sq = 0
fake_shredding = np.isclose(xi_fake_inv_sq, 0.0, atol=1e-3)

# Real shredding: smaller eigenvalue <= 0 (tachyonic)
real_shredding = eig1 <= 0.0

# -------------------------------------------------------------
# 4. Plot
# -------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)

# Fake eigenvalue contour
cnt_fake = ax[0].contourf(Phi_N, Phi_D, xi_fake_inv_sq, levels=20, cmap='RdYlBu')
ax[0].set_title('Fake eigenvalue $\\xi_{\\Delta}^{-2}$ (frozen Hessian)')
ax[0].set_xlabel('$\Phi_N$')
ax[0].set_ylabel('$\Phi_\\Delta$')
fig.colorbar(cnt_fake, ax=ax[0], label='Curvature (mass$^2$)')

# Real eigenvalue contour (smaller eigenvalue)
cnt_real = ax[1].contourf(Phi_N, Phi_D, eig1, levels=20, cmap='RdYlBu')
ax[1].set_title('True smaller eigenvalue (full metric + dilaton)')
ax[1].set_xlabel('$\Phi_N$')
fig.colorbar(cnt_real, ax=ax[1], label='Mass$^2$')

# Overlay shredding boundaries
ax[0].contour(Phi_N, Phi_D, fake_shredding, levels=[0.5], colors='k', linewidths=2)
ax[1].contour(Phi_N, Phi_D, real_shredding, levels=[0.5], colors='k', linewidths=2)

plt.tight_layout()
plt.show()

# -------------------------------------------------------------
# 5. Diagnostic prints
# -------------------------------------------------------------
# Find approximate coordinate where fake shredding occurs
idx_fake = np.unravel_index(np.argmin(np.abs(xi_fake_inv_sq)), xi_fake_inv_sq.shape)
print(f"Fake shredding near (Φ_N,Φ_Δ) ≈ ({Phi_N[idx_fake[1]]:.3f}, {Phi_D[idx_fake[0]]:.3f})")

# Find first occurrence of real tachyonic mode
tach_idx = np.where(real_shredding)
if len(tach_idx[0]) > 0:
    i, j = tach_idx[0][0], tach_idx[1][0]
    print(f"True tachyonic mode appears near (Φ_N,Φ_Δ) ≈ ({Phi_N[j]:.3f}, {Phi_D[i]:.3f})")
else:
    print("No tachyonic mode found in the scanned range (stabilization works).")