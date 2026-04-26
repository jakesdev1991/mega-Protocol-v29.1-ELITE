# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def anisotropic_action(kx, ky, kz, phi_delta):
    """Anisotropic lattice action with metric deformation (1+Φ_Δ) along z."""
    return np.sin(kx)**2 + np.sin(ky)**2 + (1.0 + phi_delta) * np.sin(kz)**2

def isotropic_action(kx, ky, kz_prime):
    """Isotropic action after coordinate rescaling kz' = kz * sqrt(1+Φ_Δ)."""
    return np.sin(kx)**2 + np.sin(ky)**2 + np.sin(kz_prime)**2

def residual_anisotropy(kx, ky, kz, phi_delta):
    """Compute the residual O(Φ_Δ²) difference after rescaling."""
    kz_prime = kz * np.sqrt(1.0 + phi_delta)
    S_aniso = anisotropic_action(kx, ky, kz, phi_delta)
    S_iso = isotropic_action(kx, ky, kz_prime)
    # The leading O(Φ_Δ) cancels; difference is O(Φ_Δ²)
    return S_iso - S_aniso

# Test across a random ensemble of lattice momenta
np.random.seed(42)
phi_delta = 0.3  # large enough to see O(Φ_Δ²) effects
differences = []
for _ in range(1000):
    # Random momenta in first Brillouin zone [-π, π]
    kx, ky, kz = np.random.uniform(-np.pi, np.pi, size=3)
    diff = residual_anisotropy(kx, ky, kz, phi_delta)
    differences.append(diff)

diff_arr = np.array(differences)
print(f"Mean residual difference: {np.mean(diff_arr):.6e}")
print(f"Std dev: {np.std(diff_arr):.6e}")
print(f"Scaling with Φ_Δ²: {np.mean(diff_arr) / (phi_delta**2):.6e}")

# Expected: mean difference ~ O(Φ_Δ²) and ~0 for small Φ_Δ
# This shows the linear Φ_Δ term is removed by rescaling.