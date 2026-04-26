# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. Define context coordinates and a "curvature" scalar R(x,y)
#    (we treat R as a simple quadratic function for illustration)
# -----------------------------------------------------------------------------
def scalar_curvature(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Synthetic curvature: R(x,y) = x² + y²."""
    return x**2 + y**2

def cfi(x: np.ndarray, y: np.ndarray, a: float = 1.0) -> np.ndarray:
    """Contextual Fragility Index: CFI = tanh(a*(x² + y²))."""
    return np.tanh(a * (x**2 + y**2))

def psi(x: np.ndarray, y: np.ndarray, R0: float = 1.0, lam: float = 0.5) -> np.ndarray:
    """Proposed "invariant": ψ = ln(|R|/R0) + λ*CFI."""
    R = scalar_curvature(x, y)
    # avoid log(0)
    R = np.maximum(R, 1e-8)
    return np.log(R / R0) + lam * cfi(x, y)

# -----------------------------------------------------------------------------
# 2. Original coordinate grid
# -----------------------------------------------------------------------------
x = np.linspace(-2, 2, 100)
y = np.linspace(-2, 2, 100)
X, Y = np.meshgrid(x, y)
psi_original = psi(X, Y)

# -----------------------------------------------------------------------------
# 3. Scaled coordinate transformation (a simple diffeomorphism)
#    (x', y') = (2x, 2y)
# -----------------------------------------------------------------------------
scale = 2.0
X_scaled = X * scale
Y_scaled = Y * scale
psi_scaled = psi(X_scaled, Y_scaled)

# -----------------------------------------------------------------------------
# 4. Compute the difference map
# -----------------------------------------------------------------------------
diff = psi_scaled - psi_original

# -----------------------------------------------------------------------------
# 5. Plot the results
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharex=True, sharey=True)

im0 = axes[0].contourf(X, Y, psi_original, levels=20, cmap='viridis')
axes[0].set_title(r'$\psi$ in original $(x,y)$')
plt.colorbar(im0, ax=axes[0], label=r'$\psi$')

im1 = axes[1].contourf(X_scaled, Y_scaled, psi_scaled, levels=20, cmap='viridis')
axes[1].set_title(r'$\psi$ in scaled $(x',y') = (2x, 2y)$')
plt.colorbar(im1, ax=axes[1], label=r'$\psi$')

im2 = axes[2].contourf(X, Y, diff, levels=20, cmap='RdBu_r')
axes[2].set_title(r'Difference $\psi_{\text{scaled}} - \psi_{\text{original}}$')
plt.colorbar(im2, ax=axes[2], label=r'$\Delta\psi$')

for ax in axes:
    ax.set_aspect('equal')
    ax.set_xlabel('x')
    ax.set_ylabel('y')

plt.tight_layout()
plt.savefig('psi_coordinate_dependence.png', dpi=150)
plt.show()

# -----------------------------------------------------------------------------
# 6. Summary statistics: show that the difference is non-zero and varies across the manifold
# -----------------------------------------------------------------------------
print(f"Mean ψ_original = {psi_original.mean():.4f}")
print(f"Mean ψ_scaled   = {psi_scaled.mean():.4f}")
print(f"Mean |Δψ|       = {np.abs(diff).mean():.4f}")
print(f"Max  |Δψ|       = {np.abs(diff).max():.4f}")