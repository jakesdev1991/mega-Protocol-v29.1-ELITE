# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# 1. Archive-mode kinetic operator on a 4D torus (L^4 lattice)
# ----------------------------------------------------------------------
def archive_kinetic_matrix(L):
    """
    Build the discretized kinetic operator K = -∂^2 for a 3-form field
    confined to a 3D subspace (the "Archive"). The operator is indefinite
    because the 3-form has a self-dual structure.
    """
    # Lattice momenta
    ks = 2 * np.pi * np.fft.fftfreq(L, d=1.0)
    K = np.zeros((L**4, L**4), dtype=float)
    # Fill diagonal with -∑_μ (2 - 2 cos k_μ)
    # Off-diagonal entries mimic the 3-form constraint (simplified model)
    for i in range(L**4):
        # Extract 4D index
        idx = np.unravel_index(i, (L, L, L, L))
        kvec = np.array([ks[idx[mu]] for mu in range(4)])
        # Kinetic eigenvalue: -(∑_μ sin²(k_μ/2))
        # For a 3-form, one component flips sign (ghost)
        eigenval = -2.0 * sum((np.sin(kvec[mu]/2.0))**2 for mu in range(4))
        # Flip sign on one component to simulate self-duality
        eigenval += 4.0 * (np.sin(kvec[3]/2.0))**2  # ghost along x4
        K[i, i] = eigenval
    return K

# Check eigenvalue spectrum
L = 8
K = archive_kinetic_matrix(L)
eigvals = la.eigvalsh(K)
print("Archive kinetic eigenvalues (sample):", eigvals[:10])
print("Number of negative eigenvalues:", np.sum(eigvals < 0))

# ----------------------------------------------------------------------
# 2. Functional determinant sign (ghost detection)
# ----------------------------------------------------------------------
det_K = np.linalg.det(K)
print("Sign of det(K):", np.sign(det_K))  # Negative => ghost

# ----------------------------------------------------------------------
# 3. RG flow of Phi_N and Phi_Delta (coupled logistic)
# ----------------------------------------------------------------------
def rg_flow(log_q, y, eta_N=0.1, eta_D=0.15, kappa=0.05, I0=1.0):
    """
    dy/dlnq = [beta_N, beta_D]
    y = [Phi_N, Phi_D]
    """
    phiN, phiD = y
    betaN = eta_N * phiN * (1 - phiN**2 / I0**2) - kappa * phiD**2
    betaD = eta_D * phiD * (1 - phiD**2 / I0**2) + kappa * phiN * phiD
    return np.array([betaN, betaD])

def integrate_rg(initial, q_max=1000, steps=10000):
    log_q = np.linspace(0, np.log(q_max), steps)
    y = np.empty((steps, 2))
    y[0] = initial
    for i in range(1, steps):
        # Simple Euler step
        y[i] = y[i-1] + rg_flow(log_q[i-1], y[i-1]) * (log_q[i] - log_q[i-1])
    return log_q, y

log_q, traj = integrate_rg(initial=[0.8, 0.2])
phiN, phiD = traj.T

# Find scale where Phi_D diverges (Shredding)
shred_idx = np.argmax(np.abs(phiD) > 1e3)
if shred_idx > 0:
    print(f"Shredding (Phi_D blowup) at q ~ {np.exp(log_q[shred_idx]):.2f}")

# Plot
plt.figure(figsize=(8,4))
plt.plot(np.exp(log_q), phiN, label='Phi_N')
plt.plot(np.exp(log_q), phiD, label='Phi_D')
plt.axhline(I0, ls='--', color='gray')
plt.yscale('symlog')
plt.xscale('log')
plt.xlabel('q (momentum scale)')
plt.ylabel('Mode amplitude')
plt.title('RG Flow: Archive Mode Ghost')
plt.legend()
plt.grid(True)
plt.show()