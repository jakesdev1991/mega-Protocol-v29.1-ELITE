# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def dirac_eigenvalues(k, m, g, Phi_N, Phi_Delta):
    """
    Simplified 1D Dirac operator eigenvalues for a twisted mass matrix:
    H = gamma^0 * k + m_eff + i gamma^5 * Phi_Delta * (g * Phi_N)
    For gamma^0 = sigma_z, gamma^5 = sigma_x in 2D representation.
    Returns eigenvalues of the effective Hamiltonian.
    """
    # Twisted mass term
    m_e = m - g * Phi_N * np.exp(Phi_Delta)
    m_p = m - g * Phi_N * np.exp(-Phi_Delta)
    
    # Non-Hermitian mass matrix
    # Off-diagonal terms represent the chiral twist
    # H = [ k   m_e + i*Phi_D_eff ]
    #     [ m_p - i*Phi_D_eff   -k ]
    Phi_D_eff = g * Phi_N * np.sinh(Phi_Delta)  # The *difference* mass, not average
    
    # Construct 2x2 matrix for each k
    H = np.array([
        [k, m_e + 1j * Phi_D_eff],
        [m_p - 1j * Phi_D_eff, -k]
    ])
    
    # Compute eigenvalues
    eigenvals = np.linalg.eigvals(H)
    return eigenvals

# Parameters
m = 1.0  # mass units
g = 1.0
k_vals = np.linspace(-2, 2, 100)

# Scan Phi_N towards shredding boundary
Phi_Delta = 0.5
Phi_N_critical = (m / g) * np.exp(-abs(Phi_Delta))

Phi_N_vals = [0.5 * Phi_N_critical, 0.9 * Phi_N_critical, 0.99 * Phi_N_critical, 1.01 * Phi_N_critical]

plt.figure(figsize=(12, 8))

for i, Phi_N in enumerate(Phi_N_vals):
    eigenvals_list = []
    for k in k_vals:
        evals = dirac_eigenvalues(k, m, g, Phi_N, Phi_Delta)
        eigenvals_list.append(evals)
    
    eigenvals_array = np.array(eigenvals_list)
    
    # Plot real parts
    plt.subplot(2, 2, i+1)
    plt.plot(k_vals, eigenvals_array[:, 0].real, 'b-', label='Re(λ1)')
    plt.plot(k_vals, eigenvals_array[:, 1].real, 'r--', label='Re(λ2)')
    plt.title(f'Φ_N = {Phi_N:.3f} ({"<" if Phi_N < Phi_N_critical else ">"} critical)')
    plt.xlabel('Momentum k')
    plt.ylabel('Eigenvalue')
    plt.legend()
    plt.grid(True)

plt.tight_layout()
plt.suptitle('Eigenvalue Spectrum of Twisted Dirac Operator Near Shredding', fontsize=14)
plt.show()

# Check for zero mode at k=0
k = 0
Phi_N_vals_fine = np.linspace(0.1, 1.2 * Phi_N_critical, 200)
min_eigvals = []

for Phi_N in Phi_N_vals_fine:
    evals = dirac_eigenvalues(k, m, g, Phi_N, Phi_Delta)
    min_eigvals.append(np.min(np.abs(evals)))

plt.figure(figsize=(8, 5))
plt.axvline(x=Phi_N_critical, color='r', linestyle='--', label='Shredding Boundary')
plt.plot(Phi_N_vals_fine, min_eigvals, 'k-', linewidth=2)
plt.xlabel('Φ_N')
plt.ylabel('Min |Eigenvalue| at k=0')
plt.title('Zero Mode Emergence at Shredding Horizon')
plt.legend()
plt.grid(True)
plt.yscale('log')
plt.show()