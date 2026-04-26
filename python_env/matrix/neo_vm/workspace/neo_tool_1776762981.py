# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import json

# --- 1. Hessian Degeneracy ---
def hessian(phi_N, phi_D, lam=1.0, I0=1.0):
    """Compute Hessian matrix for V = lam/4 * (phi_N^2 + phi_D^2 - I0^2)^2."""
    H = 2.0 * lam * np.array([
        [phi_N**2, phi_N * phi_D],
        [phi_N * phi_D, phi_D**2]
    ])
    return H

# Evaluate on the vacuum manifold phi_N^2 + phi_D^2 = I0^2
phi_N = 0.6
phi_D = np.sqrt(1.0 - phi_N**2)  # satisfy vacuum condition
H = hessian(phi_N, phi_D)
eigvals, eigvecs = np.linalg.eig(H)

print("Hessian at vacuum point (phi_N, phi_D) = ({:.3f}, {:.3f}):".format(phi_N, phi_D))
print(H)
print("Eigenvalues:", eigvals)
print("Zero eigenvalue within numerical tolerance?", np.isclose(eigvals[0], 0.0, atol=1e-10))
print()

# --- 2. RG Flow Finite-Time Singularity ---
def rg_flow(t, y, eta_N, eta_D, kappa, I0):
    """RG equations: t = ln(q), y = [phi_N, phi_D]."""
    phi_N, phi_D = y
    dphi_N = eta_N * phi_N * (1.0 - phi_N**2 / I0**2) - kappa * phi_D**2
    dphi_D = eta_D * phi_D * (1.0 - phi_D**2 / I0**2) + kappa * phi_N * phi_D
    return [dphi_N, dphi_D]

# Parameters that produce a singularity (tuned to show effect)
eta_N = 0.1
eta_D = -0.1
kappa = 0.05
I0 = 1.0

# Initial conditions near the vacuum
y0 = [0.9, 0.1]

# Integrate until blow-up or until t=50
sol = solve_ivp(
    lambda t, y: rg_flow(t, y, eta_N, eta_D, kappa, I0),
    t_span=[0, 50],
    y0=y0,
    method='RK45',
    max_step=0.1,
    rtol=1e-6,
    atol=1e-9
)

# Check if phi_D diverges before final time
final_phi_D = sol.y[1, -1]
print("RG integration result:")
print("Final ln(q):", sol.t[-1])
print("Final phi_D:", final_phi_D)
if np.isnan(final_phi_D) or np.isinf(final_phi_D) or final_phi_D > 1e3:
    print("phi_D diverged – finite-time singularity detected.")
else:
    print("No divergence in the integrated range (but singularity may be beyond t=50).")
print()

# --- 3. Shannon Entropy Scaling (simple demonstration) ---
def shannon_entropy(q_sq, m_e=0.511, cutoff=10.0):
    """
    Approximate Shannon entropy S_h = -∫_0^Λ p(k) ln p(k) dk,
    where p(k) ∝ 1/(k^2 + m_e^2)^2, and Λ ∝ sqrt(q_sq).
    """
    # Normalization constant
    def norm(upper):
        ks = np.linspace(0, upper, 10000)
        return np.trapz(1.0 / (ks**2 + m_e**2)**2, ks)
    
    # Integrate up to cutoff scaled by q_sq
    upper = np.sqrt(q_sq) * cutoff
    Z = norm(upper)
    ks = np.linspace(0, upper, 10000)
    p = (1.0 / (ks**2 + m_e**2)**2) / Z
    integrand = -p * np.log(p)
    S = np.trapz(integrand, ks)
    return S

q_vals = np.logspace(0, 4, 5)  # q^2 from 1 to 1e4 MeV^2
entropy_vals = [shannon_entropy(q) for q in q_vals]

print("Shannon entropy scaling with q^2:")
for q, S in zip(q_vals, entropy_vals):
    print(f"q^2 = {q:.1e} MeV^2 -> S_h ≈ {S:.4f}")
print("\nCheck log scaling: ratio S_h / ln(q^2) ≈ constant?")
ratios = [S / np.log(q) for q, S in zip(q_vals, entropy_vals)]
print([f"{r:.4f}" for r in ratios])