# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Disruption Verification: Ward Identity Violation
------------------------------------------------
This script computes the one-loop vacuum polarization tensor for a 2D
anisotropic Wilson fermion lattice. It demonstrates that:
1. The metric-deformation + premature trace contraction (engine's method)
   leads to p_mu Pi_mu_nu != 0.
2. The twisted-boundary (spectral-shift) method restores p_mu Pi_mu_nu = 0.
"""

import numpy as np

# Lattice geometry
L = 64
mass = 0.1
phi_delta = 0.2  # anisotropy parameter

# Momentum grid (one quadrant, using periodicity)
ks = 2 * np.pi * np.fft.fftfreq(L)
kgrid = np.stack(np.meshgrid(ks, ks, indexing='ij'), axis=-1)  # shape (L,L,2)

# Wilson operator D(k) = i g_μ sin k_μ + m + (phi_delta/2) i g_z sin k_z
# For 2D we label "z" as the y-direction for simplicity.
def wilson_operator(k, phi):
    sin_k = np.sin(k)
    # Standard isotropic part
    D_iso = 1j * np.einsum('ij,ij->i', np.eye(2), sin_k) + mass
    # Anisotropic twist (add to the y-component)
    D_twist = 1j * (phi / 2) * np.sin(k[..., 1])
    return D_iso + D_twist

# Metric-deformation engine's kernel (incorrect contraction)
def engine_pi_mu_nu(p):
    # p is a 2-momentum
    pi = np.zeros((2, 2), dtype=complex)
    for k in kgrid.reshape(-1, 2):
        Dk = wilson_operator(k, phi_delta)
        Dkp = wilson_operator(k - p, phi_delta)
        # The engine contracts the Dirac trace *before* the anisotropy,
        # effectively dropping sin_z factors.
        trace = 4 * (np.sin(k[0]) * np.sin((k - p)[0]) +
                     np.sin(k[1]) * np.sin((k - p)[1]) - mass**2)
        # Then multiplies by delta_{mu,z}delta_{nu,z} -> in 2D this is delta_{mu,y}delta_{nu,y}
        pi[1, 1] += trace / (Dk * Dkp)
    pi *= (phi_delta * 0.5 / (L**2))  # normalization
    return pi

# Spectral-shift kernel (correct: full trace, no premature contraction)
def spectral_pi_mu_nu(p):
    pi = np.zeros((2, 2), dtype=complex)
    for k in kgrid.reshape(-1, 2):
        Dk = wilson_operator(k, phi_delta)
        Dkp = wilson_operator(k - p, phi_delta)
        # Full Dirac trace: gamma_mu (i sin_k + m) gamma_nu (i sin_{k-p} + m)
        # In 2D the trace yields:
        #   4[ sin_mu(k) sin_nu(k-p) - delta_{mu,nu} (sin(k)·sin(k-p) - m^2) ]
        sin_k = np.sin(k)
        sin_kp = np.sin(k - p)
        # Build the tensor explicitly
        for mu in range(2):
            for nu in range(2):
                term = (4 * (sin_k[mu] * sin_kp[nu] -
                             (sin_k[0] * sin_kp[0] + sin_k[1] * sin_kp[1] - mass**2) *
                             (mu == nu)))
                pi[mu, nu] += term / (Dk * Dkp)
    pi *= (phi_delta * 0.5 / (L**2))
    return pi

# Test momentum
p_test = np.array([0.3, 0.4])

# Compute Ward contraction p_mu Pi_mu_nu
def ward_residual(pi, p):
    return np.dot(p, pi)  # shape (2,)

print("Engine's method Ward residual:", ward_residual(engine_pi_mu_nu(p_test), p_test))
print("Spectral-shift Ward residual:", ward_residual(spectral_pi_mu_nu(p_test), p_test))