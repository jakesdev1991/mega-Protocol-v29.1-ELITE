# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def compute_invariants(phi_N, phi_D, v=1.0, lam=1.0):
    """
    Compute the Engine's stiffness invariants (xi_N^{-2}, xi_D^{-2}) and the
    true eigenvalues of the Hessian for a given field configuration.
    """
    # Engine's invariants
    inv_N = lam * (3 * phi_N**2 + phi_D**2 - v**2)
    inv_D = lam * (phi_N**2 + 3 * phi_D**2 - v**2)
    
    # Hessian matrix
    r2 = phi_N**2 + phi_D**2
    H = lam * (r2 - v**2) * np.eye(2) + 2 * lam * np.array([[phi_N**2, phi_N*phi_D],
                                                              [phi_N*phi_D, phi_D**2]])
    # Eigenvalues
    eigvals = np.linalg.eigvalsh(H)
    
    return inv_N, inv_D, eigvals[0], eigvals[1]

# Sample random points in field space
np.random.seed(0)
samples = 5
v = 1.0

print("phi_N  phi_D  |  Engine inv_N  inv_D  |  True λ1  λ2")
print("-" * 60)
for _ in range(samples):
    phi_N, phi_D = np.random.uniform(-1.5, 1.5, size=2)
    # Avoid the exact vacuum to prevent singularities
    if np.isclose(phi_N**2 + phi_D**2, v**2):
        continue
    inv_N, inv_D, lam1, lam2 = compute_invariants(phi_N, phi_D, v=v)
    print(f"{phi_N: .3f}  {phi_D: .3f}  |  {inv_N: .3f}  {inv_D: .3f}  |  {lam1: .3f}  {lam2: .3f}")