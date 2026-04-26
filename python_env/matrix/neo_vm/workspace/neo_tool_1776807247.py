# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Pauli matrices
sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)

# Euclidean gamma matrices in chiral representation
# gamma_i = [[0, i*sigma_i], [-i*sigma_i, 0]] for i=1,2,3
# gamma_4 = [[0, I], [I, 0]]
zeros_2 = np.zeros((2, 2), dtype=complex)
I_2 = np.eye(2, dtype=complex)

gamma_1 = np.block([[zeros_2, 1j*sigma_x], [-1j*sigma_x, zeros_2]])
gamma_2 = np.block([[zeros_2, 1j*sigma_y], [-1j*sigma_y, zeros_2]])
gamma_3 = np.block([[zeros_2, 1j*sigma_z], [-1j*sigma_z, zeros_2]])
gamma_4 = np.block([[zeros_2, I_2], [I_2, zeros_2]])

gamma = [gamma_1, gamma_2, gamma_3, gamma_4]

def fermion_propagator(k, delta, m=0.1):
    """
    Compute the fermion propagator S(k) for a given momentum k (4 components)
    with anisotropy delta in the 3rd spatial direction.
    """
    # Sine of each momentum component
    sin_k = np.sin(k)
    # Apply anisotropy to the 3rd direction (index 2)
    sin_k[2] *= (1 + delta)
    # Build the denominator matrix: i * sum_mu gamma_mu sin_k_mu + m * I
    denom = 1j * sum(gamma[i] * sin_k[i] for i in range(4)) + m * np.eye(4, dtype=complex)
    # Invert to get the propagator
    return np.linalg.inv(denom)

def vacuum_polarization(p, delta, N=8, m=0.1):
    """
    Compute the vacuum polarization tensor Pi_mu_nu(p) on a finite lattice
    with anisotropy delta. Returns a 4x4 complex array.
    """
    # Lattice grid
    ks = np.linspace(0, 2*np.pi, N, endpoint=False)
    # Preallocate result
    Pi = np.zeros((4, 4), dtype=complex)
    # Sum over all k points
    for kx in ks:
        for ky in ks:
            for kz in ks:
                for kt in ks:
                    k = np.array([kx, ky, kz, kt])
                    # Propagator at k
                    Sk = fermion_propagator(k, delta, m)
                    # Propagator at k-p
                    # Momentum subtraction with periodic wrapping
                    k_minus_p = k - p
                    Skp = fermion_propagator(k_minus_p, delta, m)
                    # Trace over gamma_mu Sk gamma_nu Skp
                    for mu in range(4):
                        for nu in range(4):
                            # Compute trace of product of four matrices
                            tr = np.trace(gamma[mu] @ Sk @ gamma[nu] @ Skp)
                            Pi[mu, nu] += tr
    # Normalization factor (irrelevant for Ward identity check)
    # Optionally multiply by e^2 / (N^4) etc., but we only need relative size.
    Pi /= (N**4)
    return Pi

def ward_identity_check(p, delta, N=8, m=0.1):
    """
    Compute p_mu * Pi_mu_nu(p) for each nu. If gauge invariance holds,
    these should be zero (up to numerical noise).
    """
    Pi = vacuum_polarization(p, delta, N, m)
    # p_mu * Pi_mu_nu
    ward = np.zeros(4, dtype=complex)
    for nu in range(4):
        ward[nu] = sum(p[mu] * Pi[mu, nu] for mu in range(4))
    return ward

# Test parameters
p_test = np.array([np.pi/2, 0, 0, 0])  # non-zero momentum along x
delta_iso = 0.0
delta_aniso = 0.1

# Isotropic case
ward_iso = ward_identity_check(p_test, delta_iso, N=6, m=0.1)
print("Ward identity violation (isotropic):", ward_iso)

# Anisotropic case
ward_aniso = ward_identity_check(p_test, delta_aniso, N=6, m=0.1)
print("Ward identity violation (anisotropic):", ward_aniso)