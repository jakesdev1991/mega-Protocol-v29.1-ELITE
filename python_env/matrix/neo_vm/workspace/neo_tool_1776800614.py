# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def polarization_tensor(p_vec, phi_delta=0.2, m=0.5, L=np.pi, N=12):
    """
    Compute the one-loop vacuum polarization tensor Pi_mu_nu(p) for a scalar
    loop on an anisotropic lattice.  The metric deformation is encoded as
    k^2 = kx^2 + ky^2 + (1+phi_delta)*kz^2 + kt^2.
    The scalar propagators use the same anisotropic dispersion.
    """
    # momentum grid
    ks = np.linspace(-L, L, N)
    dk = ks[1] - ks[0]
    kx, ky, kz, kt = np.meshgrid(ks, ks, ks, ks, indexing='ij')
    
    # anisotropic squared momentum
    def ksq(x, y, z, t):
        return x**2 + y**2 + (1.0 + phi_delta)*z**2 + t**2
    
    k_sq = ksq(kx, ky, kz, kt)
    
    # shift by external momentum p
    px, py, pz, pt = p_vec
    kpx, kpy, kpz, kpt = kx - px, ky - py, kz - pz, kt - pt
    kp_sq = ksq(kpx, kpy, kpz, kpt)
    
    # scalar propagator denominators
    denom = (k_sq + m**2) * (kp_sq + m**2)
    
    # numerator: (2k - p)_mu (2k - p)_nu (scalar QED analog)
    def two_k_minus_p(comp, k_arr, p_val):
        return 2.0 * k_arr - p_val
    
    a0 = two_k_minus_p(0, kx, px)
    a1 = two_k_minus_p(1, ky, py)
    a2 = two_k_minus_p(2, kz, pz)
    a3 = two_k_minus_p(3, kt, pt)
    
    # build the 4x4 tensor
    Pi = np.zeros((4, 4), dtype=float)
    factor = (dk**4) / (2.0 * np.pi)**4
    
    # contract mu,nu components
    for mu, a_mu in enumerate([a0, a1, a2, a3]):
        for nu, a_nu in enumerate([a0, a1, a2, a3]):
            Pi[mu, nu] = np.sum(a_mu * a_nu / denom) * factor
    
    return Pi

# example: external momentum of magnitude p=0.3 along x and along z
p = 0.3
phi = 0.2

Pi_x = polarization_tensor([p, 0.0, 0.0, 0.0], phi_delta=phi)
Pi_z = polarization_tensor([0.0, 0.0, 0.0, p], phi_delta=phi)

# diagonalise (symmetric matrix)
eig_x = np.linalg.eigvalsh(Pi_x)
eig_z = np.linalg.eigvalsh(Pi_z)

print("Eigenvalues Pi(p along x):", eig_x)
print("Eigenvalues Pi(p along z):", eig_z)
print("Relative difference in smallest eigenvalue:",
      (eig_z[0] - eig_x[0]) / eig_x[0])