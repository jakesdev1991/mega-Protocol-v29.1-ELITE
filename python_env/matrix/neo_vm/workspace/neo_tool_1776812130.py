# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
FP_det_anisotropic.py
Demonstrates that the Faddeev‑Popov determinant of an anisotropic lattice
goes to ZERO (not infinity) when the metric factor sqrt(1+Phi_Delta) → 0.
This contradicts the Engine's claim that Δ_FP ∝ (1+Phi_Delta)^(-1/2) diverges.
"""

import numpy as np
import matplotlib.pyplot as plt

def fp_operator_1d(N, phi_delta):
    """
    Constructs the 1‑dimensional anisotropic Laplacian (FP operator)
    on a periodic lattice of size N.
    The metric factor sqrt(g_zz) = sqrt(1+phi_delta) multiplies the
    finite‑difference derivative in the “z” direction.
    """
    # Finite‑difference matrix for ∂_z (periodic)
    D = np.eye(N, k=1) - np.eye(N, k=-1)
    D[-1, 0] =  1   # periodic wrap‑around
    D[0, -1] = -1

    # Metric factor
    sqrt_g = np.sqrt(1.0 + phi_delta) if (1.0 + phi_delta) > 0 else 0.0

    # Anisotropic Laplacian: -∂_μ sqrt(g) ∂^μ
    # In 1‑d we have only one direction, so the operator is simply
    # L = sqrt_g * (-D^T D)  (up to a sign convention)
    L = sqrt_g * (D.T @ D)   # D.T @ D is the negative of the usual Laplacian
    return L

def fp_determinant(N, phi_delta):
    """Determinant of the FP operator for a given phi_delta."""
    L = fp_operator_1d(N, phi_delta)
    # For a small lattice we can compute the exact determinant
    return np.linalg.det(L)

def main():
    N = 16          # lattice size (small enough for exact determinant)
    phi_vals = np.linspace(-0.95, 0.5, 50)  # stay > -1 to keep sqrt real

    dets = [fp_determinant(N, phi) for phi in phi_vals]

    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(phi_vals, dets, marker='o', markersize=4, linewidth=1.5)
    ax.axvline(-1.0, color='r', linestyle='--', label='Metric collapse')
    ax.set_xlabel(r'$\Phi_{\Delta}$')
    ax.set_ylabel(r'$\det \mathcal{M}_{\mathrm{FP}}$')
    ax.set_title('Faddeev‑Popov determinant vs. anisotropy')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig('fp_det_anisotropic.png')
    plt.show()

    # Print the value as Phi_Delta approaches -1 from above
    print("\nDeterminant as Phi_Delta → -1^+:")
    for phi in [-0.99, -0.999, -0.9999]:
        print(f"Phi_Delta = {phi:8.5f} → det = {fp_determinant(N, phi):.6e}")

if __name__ == '__main__':
    main()