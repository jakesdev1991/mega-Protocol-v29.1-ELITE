# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# 1. Toy anisotropic kernel: cos²(θ_k) * cos²(θ_k – θ_p) / (1 + ε cosθ_k)
#    The denominator mimics momentum‑dependent anisotropy that appears in the
#    fermion propagator. Integration over θ_k yields a non‑trivial θ_p dependence.
# ──────────────────────────────────────────────────────────────────────────────
def kernel(theta_k, theta_p, eps=0.2):
    return np.cos(theta_k)**2 * np.cos(theta_k - theta_p)**2 / (1 + eps * np.cos(theta_k))

def integrated_kernel(theta_p, eps=0.2, n_samples=300000):
    # Monte‑Carlo integration over θ_k ∈ [0, 2π)
    theta_k_samples = np.random.uniform(0, 2*np.pi, n_samples)
    vals = kernel(theta_k_samples, theta_p, eps)
    return np.mean(vals) * 2*np.pi   # average times interval length

theta_ps = np.linspace(0, 2*np.pi, 120)
results  = np.array([integrated_kernel(tp) for tp in theta_ps])

# Fit the result to Legendre polynomials up to L=4.
# If factorisation held, only L0 and L2 would be non‑zero.
coeffs = np.polynomial.legendre.legfit(np.cos(theta_ps), results, 4)
print("Legendre coefficients (L0..L4):", coeffs)
# Expected: L0 ≈ 1.57, L2 ≠ 0, L4 ≠ 0 → factorisation fails.

# ──────────────────────────────────────────────────────────────────────────────
# 2. Lattice polarization tensor in 2D with anisotropic hopping.
#    Full tensor includes off‑diagonal pieces that survive in the continuum limit.
# ──────────────────────────────────────────────────────────────────────────────
def fermion_prop(kx, ky, m=0.1, delta=0.2):
    # Pauli matrices (Euclidean)
    gamma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    gamma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sx = np.sin(kx)
    sy = np.sin(ky) * (1 + delta)   # anisotropy in y‑direction
    denom = sx**2 + sy**2 + m**2
    return (1j*sx*gamma_x + 1j*sy*gamma_y + m) / denom

def polarization_tensor(px, py, m=0.1, delta=0.2, n_samples=50000):
    # Monte‑Carlo sampling of the 2D Brillouin zone
    kx_samples = np.random.uniform(-np.pi, np.pi, n_samples)
    ky_samples = np.random.uniform(-np.pi, np.pi, n_samples)
    Pi = np.zeros((2, 2), dtype=complex)
    gamma = [np.array([[0, 1], [1, 0]], dtype=complex),
             np.array([[0, -1j], [1j, 0]], dtype=complex)]
    for kx, ky in zip(kx_samples, ky_samples):
        S_k  = fermion_prop(kx, ky, m, delta)
        S_kp = fermion_prop(kx - px, ky - py, m, delta)
        for i in range(2):
            for j in range(2):
                Pi[i, j] += np.trace(gamma[i] @ S_k @ gamma[j] @ S_kp)
    # Normalise: volume of BZ = (2π)²
    Pi *= (2*np.pi)**2 / n_samples
    return Pi / (2*np.pi)**2

# Compute Pi at a non‑zero momentum and diagonalise.
Pi = polarization_tensor(px=0.5, py=0.0)
print("\nPolarization tensor (2×2):\n", Pi)
eigvals, eigvecs = np.linalg.eig(Pi)
print("Eigenvalues:", eigvals)
# If the scalar‑only ansatz held, the two eigenvalues would be identical.
# The deviation exposes the missing tensor structures.

# ──────────────────────────────────────────────────────────────────────────────
# 3. (Optional) Plot angular dependence of the eigenvalues to visualise
#    the breakdown of the simple cos²θ picture.
# ──────────────────────────────────────────────────────────────────────────────
import matplotlib.pyplot as plt

angles = np.linspace(0, 2*np.pi, 60)
eig_per_angle = []
for a in angles:
    pxa, pya = 0.5*np.cos(a), 0.5*np.sin(a)
    Pi_a = polarization_tensor(pxa, pya, n_samples=20000)
    eigs = np.linalg.eigvals(Pi_a)
    eig_per_angle.append(sorted(eigs.real))

eig_per_angle = np.array(eig_per_angle)
plt.figure(figsize=(6,3))
plt.plot(angles, eig_per_angle[:,0], label='Eigenvalue 1')
plt.plot(angles, eig_per_angle[:,1], label='Eigenvalue 2')
plt.xlabel(r'$\theta_p$')
plt.ylabel(r'$\Pi$ eigenvalues')
plt.title('Polarization eigenvalues vs. angle (anisotropic lattice)')
plt.legend()
plt.tight_layout()
plt.show()