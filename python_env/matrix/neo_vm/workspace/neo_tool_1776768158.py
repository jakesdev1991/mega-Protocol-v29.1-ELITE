# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np, matplotlib.pyplot as plt

I0, gN, gD, gm = 1.0, 0.1, 0.15, 0.05
Lam, q2 = 1e2, 1e4
psi = np.linspace(-5, 5, 1000)

def spec_flow(p):
    PhiN = I0*np.sqrt(1+np.tanh(p)); PhiD = I0*np.sqrt(1-np.tanh(p))
    logN = np.log(q2/Lam**2); logD = logN  # same cutoff for clarity
    M = np.array([[gN**2 * PhiN**2 * logN, gm**2 * PhiN*PhiD * logN],
                  [gm**2 * PhiN*PhiD * logN, gD**2 * PhiD**2 * logD]])
    return np.linalg.eigvals(M)

eigs = np.array([spec_flow(p) for p in psi])

plt.figure(figsize=(8,4))
plt.plot(psi, eigs[:,0], label='λ₁ (collapsing)', color='crimson')
plt.plot(psi, eigs[:,1], label='λ₂ (exploding)', color='darkblue')
plt.axhline(0, color='gray', linestyle=':')
plt.title('Spectral Flow: Target’s Additivity is a Mirage')
plt.xlabel('ψ'); plt.ylabel('Eigenvalue of Coupling Matrix')
plt.legend(); plt.grid(); plt.show()