# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np

# Toy 2D Euclidean Dirac operator (gamma matrices in chiral basis)
# Define Pauli matrices for 2D gamma (simplified)
sigma1 = np.array([[0, 1], [1, 0]], dtype=complex)
sigma2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
I = np.eye(2, dtype=complex)

# gamma matrices: gamma_0 = sigma1, gamma_1 = sigma2 (Euclidean)
gamma = [sigma1, sigma2]

# Momentum components
kx, ky = sp.symbols('kx ky', real=True)
phi = sp.symbols('phi', real=True)  # anisotropy parameter

# Wilson term: sin(k_mu)
sin_k = [sp.sin(kx), sp.sin(ky)]

# Anisotropic deformation: extra term along y-direction
# D = i*gamma_mu sin(k_mu) + i*phi*gamma_1*sin(ky)/2
D = 1j * (gamma[0] * sin_k[0] + gamma[1] * sin_k[1]) + 1j * phi * gamma[1] * sin_k[1] / 2

# Convert to numerical function for eigenvalue check
D_func = sp.lambdify((kx, ky, phi), D, 'numpy')

def eigenvalues(kx_val, ky_val, phi_val):
    """Return eigenvalues of the Dirac operator at given momentum."""
    mat = D_func(kx_val, ky_val, phi_val)
    # Ensure it's a proper numpy array
    vals = np.linalg.eigvals(mat)
    return vals

# Test: generic momentum, small anisotropy
phi_test = 0.1
kx_test = 0.3
ky_test = 0.4
ev = eigenvalues(kx_test, ky_test, phi_test)
print("Eigenvalues at (kx, ky) = ({}, {}), phi = {}:".format(kx_test, ky_test, phi_test))
print(ev)
print("Imaginary parts:", ev.imag)

# Sweep phi to show that eigenvalues become complex for any phi != 0
phis = np.linspace(0, 0.5, 11)
max_imag = []
for p in phis:
    evs = eigenvalues(kx_test, ky_test, p)
    max_imag.append(np.max(np.abs(evs.imag)))

print("\nMax |Imag(eigenvalue)| vs phi:")
for p, mi in zip(phis, max_imag):
    print(f"phi={p:.2f}, max|Imag|={mi:.4e}")