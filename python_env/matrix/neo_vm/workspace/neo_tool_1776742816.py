# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- 1. Hessian spectrum of a single scalar field ---
λ = 1.0
I0 = 1.0
m2 = 2 * λ * I0**2                # mass^2 from Hessian

# Discretize a 1D lattice (the kinetic term is a nearest‑neighbour Laplacian)
L = 10
lap = np.diag(np.ones(L-1), -1) + np.diag(np.ones(L-1), 1) - 2*np.eye(L)
# The full Hessian: H = -Δ + m2 (in units where a=1)
H = -lap + m2 * np.eye(L)

eigvals = np.real(la.eigvals(H))
print("Hessian eigenvalues (single scalar):", np.sort(eigvals))

# All eigenvalues are m2 (≈2.0) plus O(1/L^2) from the Laplacian → only ONE physical mass.

# --- 2. RG flow of the purported two‑mode system ---
ηN, ηΔ, κ = 0.1, -0.05, 0.2

def rg_flow(t, y):
    φN, φΔ = y
    βN = ηN * φN * (1 - φN**2 / I0**2) - κ * φΔ**2
    βΔ = ηΔ * φΔ * (1 - φΔ**2 / I0**2) + κ * φN * φΔ
    return [βN, βΔ]

# Integrate from a small initial perturbation
sol = solve_ivp(rg_flow, [0, 10], [0.1, 0.1], dense_output=True)
t = np.linspace(0, 10, 500)
φN_traj, φΔ_traj = sol.sol(t)

plt.figure(figsize=(7,3))
plt.plot(t, φN_traj, label='Φ_N')
plt.plot(t, φΔ_traj, label='Φ_Δ')
plt.xlabel('ln(q)'), plt.ylabel('amplitude')
plt.title('RG flow – Archive mode diverges (ghost instability)')
plt.legend(), plt.tight_layout(), plt.show()