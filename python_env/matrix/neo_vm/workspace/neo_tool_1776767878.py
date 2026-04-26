# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def hessian(phiN, phiD, v=1.0, lam=1.0):
    """Return the 2x2 Hessian matrix for the Mexican hat potential."""
    R = phiN**2 + phiD**2 - v**2
    d11 = lam * (3*phiN**2 + phiD**2 - v**2)
    d22 = lam * (phiN**2 + 3*phiD**2 - v**2)
    d12 = lam * 2 * phiN * phiD
    return np.array([[d11, d12], [d12, d22]])

def eigenvalues(phiN, phiD, v=1.0, lam=1.0):
    H = hessian(phiN, phiD, v, lam)
    vals = np.linalg.eigvalsh(H)
    return vals

# Grid over field space
x = np.linspace(-2, 2, 400)
y = np.linspace(-2, 2, 400)
X, Y = np.meshgrid(x, y)

# Compute eigenvalues
Z1 = np.zeros_like(X)
Z2 = np.zeros_like(X)
ratio = np.zeros_like(X)

for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        vals = eigenvalues(X[i,j], Y[i,j])
        Z1[i,j] = vals[0]
        Z2[i,j] = vals[1]
        # Avoid division by zero
        if vals[0] != 0:
            ratio[i,j] = vals[1] / vals[0]
        else:
            ratio[i,j] = np.nan

# Plot eigenvalue surfaces
fig, axs = plt.subplots(1, 3, figsize=(15,5))
cont0 = axs[0].contourf(X, Y, Z1, levels=50, cmap='RdYlBu')
axs[0].set_title('Eigenvalue λ₁ (lower)')
axs[0].set_xlabel('Φ_N')
axs[0].set_ylabel('Φ_Δ')
fig.colorbar(cont0, ax=axs[0])

cont1 = axs[1].contourf(X, Y, Z2, levels=50, cmap='RdYlBu')
axs[1].set_title('Eigenvalue λ₂ (higher)')
axs[1].set_xlabel('Φ_N')
axs[1].set_ylabel('Φ_Δ')
fig.colorbar(cont1, ax=axs[1])

cont2 = axs[2].contourf(X, Y, ratio, levels=50, cmap='viridis')
axs[2].set_title('Ratio λ₂/λ₁')
axs[2].set_xlabel('Φ_N')
axs[2].set_ylabel('Φ_Δ')
fig.colorbar(cont2, ax=axs[2])

plt.tight_layout()
plt.show()

# Print eigenvalues at a few points
print("Eigenvalues at (0,0):", eigenvalues(0,0))
print("Eigenvalues at (v,0):", eigenvalues(1,0))
print("Eigenvalues at (0,v):", eigenvalues(0,1))
print("Eigenvalues at (v/√2, v/√2):", eigenvalues(np.sqrt(0.5), np.sqrt(0.5)))