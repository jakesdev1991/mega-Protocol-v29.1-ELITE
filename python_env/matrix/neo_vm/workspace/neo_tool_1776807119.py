# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# 2‑D gamma matrices (Euclidean) – Pauli basis
gamma_x = np.array([[0, 1], [1, 0]], dtype=complex)   # σ₁
gamma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)  # σ₂
I2 = np.eye(2, dtype=complex)

def inv2x2(M):
    """Fast inverse of a 2×2 matrix."""
    det = M[0,0]*M[1,1] - M[0,1]*M[1,0]
    return np.array([[M[1,1], -M[0,1]], [-M[1,0], M[0,0]]], dtype=complex) / det

def fermion_propagator(k, phi_delta, m=0.1):
    """
    Wilson fermion propagator S(k) = 1 / (i Σ_μ γ_μ sin(k_μ) + i γ_y (Φ_Δ/2) sin(k_y) + m)
    The anisotropy is encoded as an extra term in the *y* direction.
    """
    # Standard Wilson term
    sin_x = np.sin(k[0])
    sin_y = np.sin(k[1])
    # Anisotropic shift (linear in Φ_Δ)
    aniso_shift = 0.5 * phi_delta * sin_y
    # Denominator matrix
    D = 1j * (gamma_x * sin_x + gamma_y * (sin_y + aniso_shift)) + m * I2
    return inv2x2(D)

def vacuum_polarization(p, phi_delta, m=0.1, N=80, e2=1.0):
    """
    Compute Π_{μν}(p) = -e² ∫_BZ d²k/(2π)² Tr[ γ_μ S(k) γ_ν S(k-p) ].
    Return the 2×2 tensor (Π_xx, Π_xy; Π_yx, Π_yy).
    """
    # Brillouin zone discretisation
    ks = np.linspace(-np.pi, np.pi, N, endpoint=False)
    dk = ks[1] - ks[0]
    vol = dk**2 / (2*np.pi)**2

    Pi = np.zeros((2, 2), dtype=complex)
    for kx in ks:
        for ky in ks:
            k = np.array([kx, ky])
            k_minus_p = k - p
            Sk = fermion_propagator(k, phi_delta, m)
            Skp = fermion_propagator(k_minus_p, phi_delta, m)

            # Trace for each μ,ν
            for mu, gamma_mu in enumerate([gamma_x, gamma_y]):
                for nu, gamma_nu in enumerate([gamma_x, gamma_y]):
                    trace = np.trace(gamma_mu @ Sk @ gamma_nu @ Skp)
                    Pi[mu, nu] -= e2 * trace * vol
    return Pi

def vacuum_polarization_stretched(p, phi_delta, m=0.1, N=80, e2=1.0):
    """
    Same calculation but in the *stretched* coordinates where the archive momentum
    is rescaled: k_y' = (1+Φ_Δ) k_y. The propagator becomes isotropic.
    """
    stretch = 1.0 + phi_delta
    ks_x = np.linspace(-np.pi, np.pi, N, endpoint=False)
    ks_y = np.linspace(-np.pi, np.pi, N, endpoint=False) / stretch  # rescaled range
    dk_x = ks_x[1] - ks_x[0]
    dk_y = ks_y[1] - ks_y[0]
    vol = dk_x * dk_y / (2*np.pi)**2

    Pi = np.zeros((2, 2), dtype=complex)
    for kx in ks_x:
        for ky in ks_y:
            # Original k_y = stretch * ky
            k_orig = np.array([kx, stretch * ky])
            k_minus_p = k_orig - p
            # Isotropic propagator (no extra anisotropic term)
            Sk = fermion_propagator_isotropic(k_orig, m)
            Skp = fermion_propagator_isotropic(k_minus_p, m)

            for mu, gamma_mu in enumerate([gamma_x, gamma_y]):
                for nu, gamma_nu in enumerate([gamma_x, gamma_y]):
                    trace = np.trace(gamma_mu @ Sk @ gamma_nu @ Skp)
                    Pi[mu, nu] -= e2 * trace * vol
    return Pi

def fermion_propagator_isotropic(k, m=0.1):
    """Isotropic Wilson propagator (no Φ_Δ)."""
    sin_x = np.sin(k[0])
    sin_y = np.sin(k[1])
    D = 1j * (gamma_x * sin_x + gamma_y * sin_y) + m * I2
    return inv2x2(D)

# ──────────────────────────────────────────────────────────────────────────────
# Test: compare angular dependence for p along x vs p along y
phi = 0.2  # 20% anisotropy
p_mag = 0.5

p_x = np.array([p_mag, 0.0])
p_y = np.array([0.0, p_mag])

Pi_x = vacuum_polarization(p_x, phi)
Pi_y = vacuum_polarization(p_y, phi)

Pi_x_stretch = vacuum_polarization_stretched(p_x, phi)
Pi_y_stretch = vacuum_polarization_stretched(p_y, phi)

# Extract diagonal components (real parts)
def diag_comps(Pi):
    return Pi[0, 0].real, Pi[1, 1].real

print("Original coordinates:")
print("  Π_xx(p‖x) = {:.5e}, Π_yy(p‖x) = {:.5e}".format(*diag_comps(Pi_x)))
print("  Π_xx(p‖y) = {:.5e}, Π_yy(p‖y) = {:.5e}".format(*diag_comps(Pi_y)))

print("\nStretched coordinates (phantom removed):")
print("  Π_xx(p‖x) = {:.5e}, Π_yy(p‖x) = {:.5e}".format(*diag_comps(Pi_x_stretch)))
print("  Π_xx(p‖y) = {:.5e}, Π_yy(p‖y) = {:.5e}".format(*diag_comps(Pi_y_stretch)))