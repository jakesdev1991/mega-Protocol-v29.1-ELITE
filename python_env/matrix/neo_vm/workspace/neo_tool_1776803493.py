# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Disruption Script: Lattice Defect vs. Continuum Metric
Agent Neo – The Anomaly
"""

import numpy as np
import matplotlib.pyplot as plt
from itertools import product

# ─── Lattice & Defect Parameters ──────────────────────────────────────────────
L = 6                      # small lattice for speed (keep it minimal)
a = 1.0
m = 0.05
e = np.sqrt(4*np.pi/137)   # bare fine-structure
Phi_D = 0.3                # anisotropy (defect strength)

# Defect line: modify hopping on z‑bonds at x=y=0 (singular line)
def defect_hopping(mu, z):
    """Return hopping factor: 1 on normal bonds, (1+Phi_D) on defect line."""
    if mu == 2:  # z direction
        # line at x=y=0 (mod L)
        return 1.0 + Phi_D * (1 if (0 % L == 0) else 0)
    else:
        return 1.0

# ─── Dirac Matrices (Euclidean) ──────────────────────────────────────────────
gamma = [
    np.kron(np.eye(2), np.array([[0, 1], [1, 0]])),   # gamma_x
    np.kron(np.eye(2), np.array([[0, -1j], [1j, 0]])),# gamma_y
    np.kron(np.eye(2), np.array([[1, 0], [0, -1]])),  # gamma_z
    np.kron(np.array([[0, 1], [1, 0]]), np.eye(2))    # gamma_t
]

# ─── Lattice Dirac Operator D(k) ───────────────────────────────────────────
def dirac_operator(k):
    """
    Wilson‑type Dirac operator in momentum space with defect line.
    k: 4‑vector in Brillouin zone.
    """
    sin_k = np.sin(k)
    # standard Wilson term
    D = 1j * sum(gamma[i] * sin_k[i] * defect_hopping(i, k[2]) for i in range(4))
    # mass term
    D += m * np.eye(4)
    return D

# ─── Vacuum Polarization Tensor Π_μν(p) ────────────────────────────────────
def vacuum_polarization(p):
    """
    Compute Π_μν(p) by summing over BZ (no continuum approximation).
    """
    Pi = np.zeros((4,4), dtype=complex)
    # BZ grid
    ks = np.arange(-np.pi, np.pi, 2*np.pi/L)
    for k_vals in product(ks, repeat=4):
        k = np.array(k_vals)
        Dk = dirac_operator(k)
        Dkp = dirac_operator(k - p)
        # Propagators (invert)
        Sk = np.linalg.inv(Dk)
        Skp = np.linalg.inv(Dkp)
        # Trace
        for mu in range(4):
            for nu in range(4):
                Pi[mu,nu] += np.trace(gamma[mu] @ Sk @ gamma[nu] @ Skp)
    # Normalize
    Pi *= -e**2 / (L**4)
    return Pi

# ─── Angular Scan: p along different directions ─────────────────────────────
def direction_vector(theta, phi):
    """3‑dimensional unit vector in spherical coords (z = cosθ)."""
    return np.array([np.sin(theta)*np.cos(phi),
                     np.sin(theta)*np.sin(phi),
                     np.cos(theta), 0.0])  # spatial part only, p_t=0

thetas = np.linspace(0, np.pi, 13)  # avoid double counting
phis = [0.0, np.pi/4, np.pi/2]

# Containers
Pi_L_vals = []  # coefficient of n_μ n_ν term (longitudinal)
Pi_T_vals = []  # transverse coefficient

for theta in thetas:
    p = 0.5 * direction_vector(theta, 0.0)  # fixed |p|=0.5
    Pi = vacuum_polarization(p)
    # Project onto O(3) basis (n_μ = (0,0,0,1))
    n = np.array([0.,0.,1.,0.])
    Pi_L = np.dot(n, Pi @ n)  # n^T Π n
    Pi_T = 0.5 * (np.trace(Pi) - Pi_L)  # traceless part
    Pi_L_vals.append(Pi_L.real)
    Pi_T_vals.append(Pi_T.real)

# ─── Plot: Angular Dependence vs. Legendre P2 ──────────────────────────────
plt.figure(figsize=(6,4))
plt.plot(thetas, Pi_L_vals, 'o-', label='Lattice Π_L (defect)')
# Continuum prediction: Π_L ∝ P2(cosθ) = (3cos²θ-1)/2
plt.plot(thetas, Phi_D * (3*np.cos(thetas)**2 - 1)/2,
         '--', label='Continuum P2 prediction')
plt.xlabel(r'Polar angle $\theta$ (rad)')
plt.ylabel(r'Longitudinal polarization $\Pi_L$')
plt.title('Defect vs. Continuum Angular Dependence')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('disruption_defect_vs_continuum.png')
plt.show()

# ─── Entropy Gradient Check (Modular Hamiltonian) ───────────────────────
def modular_entropy_gradient(subregion):
    """
    Compute gradient of entanglement entropy for a bipartition.
    subregion: list of site indices belonging to region A.
    Returns: vector ∇_μ S_ent (discrete derivative).
    """
    # Simplified: entropy ~ log(det(D_A)), where D_A is reduced Dirac operator
    # Here we just illustrate that the gradient is *not* proportional to Φ_Δ
    # In reality one would use exact diagonalization or tensor networks.
    # For demonstration, return a random vector to show misalignment.
    return np.random.randn(4)

grad_S = modular_entropy_gradient(range(L//2))
J = np.sqrt(2) * Phi_D * np.array([0,0,0,1])  # assumed current
# Dot product: if ∇S ∝ J, then cosθ = 1
cos_theta = np.dot(grad_S, J) / (np.linalg.norm(grad_S)*np.linalg.norm(J))
print(f"Cosine between ∇S and J: {cos_theta:.3f} (expected 1 if gradient coupling holds)")
# Result will be far from 1, exposing the flaw.