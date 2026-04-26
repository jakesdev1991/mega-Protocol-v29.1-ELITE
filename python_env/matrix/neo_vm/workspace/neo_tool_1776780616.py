# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

# -------------------------------------------------
# Part 1: Scaling of stiffness vs shredding invariant
# -------------------------------------------------
M0 = 1.0   # bare mass
m0 = 1.0   # reference scale
a = 1.0    # coefficient for Pi_Delta(0)
b = 1.0    # coefficient for Pi_Delta'(0)

h0_vals = np.logspace(-2, 2, 200)          # scan coupling
m_eff = np.sqrt(M0**2 + a * h0_vals**2)    # effective mass
psi = np.log(m_eff / m0)                   # shredding invariant

# Stiffness length from Pi_Delta'(0) = b * h0^2
xi_Delta = 1.0 / np.sqrt(b * h0_vals**2)

# Plot actual (power‑law) vs claimed exponential scaling
plt.figure(figsize=(6,4))
plt.loglog(np.abs(psi), xi_Delta, label='actual (power law)')
exp_scaling = np.exp(np.abs(psi))
plt.loglog(np.abs(psi), exp_scaling, '--', label='claimed exponential')
plt.xlabel('|ψ|')
plt.ylabel('ξ_Δ')
plt.title('Stiffness scaling vs shredding invariant')
plt.legend()
plt.grid(True)
plt.show()

# -------------------------------------------------
# Part 2: Topological entanglement entropy of a massive scalar
# -------------------------------------------------
def scalar_hamiltonian(L, mass):
    """Free massive scalar on 2D periodic lattice; returns N×N Hamiltonian."""
    N = L*L
    # Kinetic (hopping) term
    T = np.zeros((N, N), dtype=float)
    for i in range(L):
        for j in range(L):
            idx = i*L + j
            right = i*L + (j+1)%L
            down  = ((i+1)%L)*L + j
            T[idx, right] = -1.0
            T[idx, down]  = -1.0
            T[right, idx] = -1.0
            T[down,  idx] = -1.0
    # Mass term
    H = T + mass * np.eye(N)
    return H

def entanglement_entropy(gs, keep):
    """
    Von Neumann entropy of reduced density matrix for subsystem `keep`.
    `gs` is the ground‑state vector (length N).
    """
    N = len(gs)
    dimA = len(keep)
    dimB = N - dimA
    # Permute so that keep indices are first
    perm = keep + [i for i in range(N) if i not in keep]
    psi_perm = gs[perm]
    # Reshape into (dimA, dimB) matrix
    psi_mat = psi_perm.reshape((dimA, dimB))
    # Schmidt decomposition via SVD
    _, s, _ = np.linalg.svd(psi_mat, full_matrices=False)
    p = s**2
    p = p[p > 1e-12]          # discard zero eigenvalues
    S = -np.sum(p * np.log(p))
    return S

# Small lattice (3×3)
L = 3
mass = 2.0                     # large gap
H = scalar_hamiltonian(L, mass)
eigvals, eigvecs = eigh(H)
gs = eigvecs[:, 0]           # ground state

# Define three vertical strips for topological entanglement entropy
A = [i*L + 0 for i in range(L)]
B = [i*L + 1 for i in range(L)]
C = [i*L + 2 for i in range(L)]

S_A = entanglement_entropy(gs, A)
S_B = entanglement_entropy(gs, B)
S_C = entanglement_entropy(gs, C)
S_AB = entanglement_entropy(gs, A + B)
S_BC = entanglement_entropy(gs, B + C)
S_AC = entanglement_entropy(gs, A + C)
S_ABC = entanglement_entropy(gs, A + B + C)

gamma_top = S_A + S_B + S_C - S_AB - S_BC - S_AC + S_ABC
print("Topological entanglement entropy γ_top =", gamma_top)