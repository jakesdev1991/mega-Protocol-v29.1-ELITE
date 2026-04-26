# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.linalg as la

def fermionic_two_site_hamiltonian(t=1.0, g=0.5, phi=1.0):
    """
    Two fermionic sites (loops) with hopping t and a scalar coupling g*phi*(n1-n2).
    The scalar field phi is treated as a static, classical background.
    Basis: |00>, |01>, |10>, |11> (0=empty, 1=occupied).
    """
    # Number operators n1 = c1† c1, n2 = c2† c2
    # In the basis above, n1 is diag([0,0,1,1]), n2 is diag([0,1,0,1])
    n1 = np.diag([0, 0, 1, 1])
    n2 = np.diag([0, 1, 0, 1])
    
    # Hopping term: t (c1† c2 + h.c.)
    # c1† c2 maps |01> -> |10> and annihilates others
    hopping = np.zeros((4,4), dtype=complex)
    hopping[2,1] = t  # |10><01|
    hopping[1,2] = t  # |01><10|
    
    # Scalar coupling: g*phi*(n1 - n2)
    scalar = g * phi * (n1 - n2)
    
    H = hopping + scalar
    return H

def entanglement_entropy_between_sites(gs):
    """
    Compute von Neumann entropy of the reduced density matrix for site 1.
    The ground state gs is a 4‑component vector in the full Hilbert space.
    """
    # Reshape to (2,2) where first index is site1, second is site2
    psi = gs.reshape(2,2)
    # Schmidt decomposition: singular values of psi
    s = la.svdvals(psi)
    # Avoid log(0)
    s = s[s>1e-12]
    # Von Neumann entropy
    S = -np.sum(s**2 * np.log(s**2))
    return S

# Sweep scalar coupling g and compute entanglement
ts = [0.5, 1.0, 2.0]
gs = np.linspace(0, 5, 51)

for t in ts:
    entropies = []
    for g in gs:
        H = fermionic_two_site_hamiltonian(t=t, g=g, phi=1.0)
        # Ground state: lowest eigenvector
        eigs, vecs = la.eigh(H)
        gs = vecs[:,0]
        S = entanglement_entropy_between_sites(gs)
        entropies.append(S)
    # Print maximal entropy observed (should never exceed ln(2) ~ 0.693)
    print(f"t={t}, max S={max(entropies):.4f}")

# Demonstration: for any coupling, the entanglement is bounded by ln(2) and
# does *not* scale with any "shredding invariant" psi. The loops remain
# effectively independent; the scalar field only renormalizes local energies.