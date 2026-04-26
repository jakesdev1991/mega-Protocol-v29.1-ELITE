# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def aniso_coeff(action: str, m: float = 0.1, N: int = 200) -> float:
    """
    Compute the anisotropic coefficient I_aniso for a 2D lattice.
    action: 'wilson' or 'naive'
    m: bare fermion mass (in lattice units)
    N: grid points per dimension
    """
    ks = np.linspace(-np.pi, np.pi, N)
    kx, ky = np.meshgrid(ks, ks, indexing='ij')
    sin_x = np.sin(kx)
    sin_y = np.sin(ky)
    cos_x = np.cos(kx)
    cos_y = np.cos(ky)

    if action == 'wilson':
        r = 1.0
        # Wilson regulator adds (1-cos)² terms
        D = sin_x**2 + sin_y**2 + r**2 * ((1 - cos_x)**2 + (1 - cos_y)**2) + m**2
    elif action == 'naive':
        D = sin_x**2 + sin_y**2 + m**2
    else:
        raise ValueError("Unknown action")

    # anisotropic direction = y (archive direction)
    integrand = sin_y**2 / D**2
    dkx = ks[1] - ks[0]
    dky = ks[1] - ks[0]
    integral = np.sum(integrand) * dkx * dky / (2 * np.pi)**2
    return integral

# Compare the two schemes
wilson_val = aniso_coeff('wilson')
naive_val  = aniso_coeff('naive')
print(f"Wilson anisotropic coefficient: {wilson_val:.6f}")
print(f"Naive   anisotropic coefficient: {naive_val:.6f}")
print(f"Relative discrepancy: {(wilson_val - naive_val)/naive_val:.2%}")