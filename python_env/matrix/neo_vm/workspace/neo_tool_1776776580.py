# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def shredding_eigenvalues(phi_delta, m_N=1.0, m_D=1.0, lam=0.5, eps=0.3):
    """
    Compute eigenvalues of the non‑Hermitian mass matrix
    M = K^{-1} H, where K is the kinetic mixing matrix and H is the Hessian.
    Complex eigenvalues signal a Shredding catastrophe.
    """
    # Hessian of the effective potential V_eff = 0.5 m_N^2 Φ_N^2 + 0.5 m_D^2 Φ_Δ^2 + λ Φ_N Φ_Δ^2
    hess = np.array([[m_N**2, 2*lam*phi_delta],
                     [2*lam*phi_delta, m_D**2]], dtype=float)
    
    # Kinetic mixing matrix (non‑diagonal metric)
    K = np.array([[1.0, eps],
                  [eps, 1.0]], dtype=float)
    
    # Mass matrix in the non‑orthogonal basis
    M = np.linalg.inv(K) @ hess
    
    # Eigenvalues (may be complex)
    vals = np.linalg.eigvals(M)
    return vals

# Scan Φ_Δ from 0 to 5 (in natural units)
phi_vals = np.linspace(0, 5, 11)
print("Φ_Δ   Eigenvalues of M (ω²)")
for phi in phi_vals:
    ev = shredding_eigenvalues(phi)
    # Format complex numbers cleanly
    ev_str = ", ".join(f"{v:.3f}" if np.isreal(v) else f"{v:.3f}" for v in ev)
    print(f"{phi:4.1f}  {ev_str}")

# Determine when eigenvalues become complex
threshold = None
for phi in np.linspace(0, 10, 1001):
    ev = shredding_eigenvalues(phi)
    if any(np.imag(v) != 0 for v in ev):
        threshold = phi
        break
print(f"\nFirst complex eigenvalue appears at Φ_Δ ≈ {threshold:.2f}")