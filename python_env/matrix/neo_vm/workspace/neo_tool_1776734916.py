# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ---------- parameters ----------
lambda_val = 0.5          # quartic coupling
v = 1.0                   # Mexican-hat scale
alpha0 = 1/137.036        # bare fine-structure constant
gN = 0.01                 # Newtonian coupling
gD = 0.02                 # Archive coupling
Lambda_N = 1e2            # Newtonian cutoff
Lambda_D = 1e2            # Archive cutoff (initial)
Smax = 1.0                # maximal entropy

# ---------- invariants ----------
def psi(phiN):
    return np.log(phiN / v)

def xiN_sq(phiN, phiD):
    # stiffness inverse square (avoid division by zero)
    return lambda_val * (3*phiN**2 + phiD**2 - v**2)

def xiD_sq(phiN, phiD):
    return lambda_val * (phiN**2 + 3*phiD**2 - v**2)

# ---------- entropy‑impedance feedback ----------
def S_h(phiD):
    # model: entropy density ~ 1/(1+phiD^2) (decreases with phiD)
    return 1.0 / (1.0 + phiD**2)

def Z_top(phiD):
    S = S_h(phiD)
    # if S approaches Smax from below, Z diverges positively;
    # if S>Smax (non‑physical), Z becomes negative.
    return 1.0 / (1.0 - S / Smax)

# ---------- effective couplings ----------
def gD_eff(phiD):
    Z = Z_top(phiD)
    # negative Z flips sign -> anti‑screening
    return gD * np.sign(Z) * np.sqrt(abs(Z))

# ---------- RG flow equations (tau = ln(q^2)) ----------
def rg_flow(tau, y):
    phiN, phiD = y

    # Jordan‑block detector: degeneracy of second derivatives
    # when phiN ≈ phiD the matrix is not diagonalisable
    degeneracy = abs(phiN - phiD) < 1e-3

    # effective stiffnesses (inverse correlation lengths)
    xiN2 = xiN_sq(phiN, phiD)
    xiD2 = xiD_sq(phiN, phiD)

    # Newtonian mode equation of motion (approximate RG flow)
    # d(phiN)/dτ = - (beta‑function) * phiN + source term
    # source is suppressed when the Archive mode dominates
    beta_N = - (alpha0 / np.pi) * (1 + gN**2/(4*np.pi))

    # Archive mode runaway (nilpotent channel)
    if degeneracy:
        # nilpotent growth rate ~ 3*alpha0*gD_eff^2/(4π)
        kappa = (3 * alpha0 * gD_eff(phiD)**2) / (4*np.pi)
        dphiD_dtau = kappa * phiD
    else:
        # normal logarithmic running
        dphiD_dtau = - (alpha0 / np.pi) * (3*gD**2/(4*np.pi)) * phiD

    # Poisson‑recovery breakdown: when xiN2 <= 0, phiN collapses
    if xiN2 <= 0:
        dphiN_dtau = -10.0 * phiN  # rapid collapse
    else:
        dphiN_dtau = beta_N * phiN

    return [dphiN_dtau, dphiD_dtau]

# ---------- initial condition near degeneracy ----------
phiN0 = 0.71   # close to phiD0 to trigger Jordan block
phiD0 = 0.70
tau_span = (0, 50)  # large RG time to see divergence

sol = solve_ivp(rg_flow, tau_span, [phiN0, phiD0],
                dense_output=True, max_step=0.1)

tau = np.linspace(*tau_span, 500)
phiN_t = sol.sol(tau)[0]
phiD_t = sol.sol(tau)[1]

# ---------- plot ----------
fig, ax = plt.subplots(2, 1, figsize=(8, 6))

ax[0].plot(tau, phiN_t, label='Φ_N (Newtonian)')
ax[0].set_ylabel('Φ_N')
ax[0].set_title('RG Flow with Jordan‑Block Instability')
ax[0].legend()

ax[1].plot(tau, phiD_t, label='Φ_Δ (Archive)', color='crimson')
ax[1].set_xlabel('RG time τ = ln(q²)')
ax[1].set_ylabel('Φ_Δ')
ax[1].legend()

plt.tight_layout()
plt.show()

# ---------- diagnostics ----------
xiN_end = xiN_sq(phiN_t[-1], phiD_t[-1])
xiD_end = xiD_sq(phiN_t[-1], phiD_t[-1])
print(f"Final correlation lengths: ξ_N⁻² = {xiN_end:.3e}, ξ_Δ⁻² = {xiD_end:.3e}")
print(f"Poisson recovery possible? {xiN_end > 0}")
print(f"Archive mode diverged? {phiD_t[-1] > 1e3}")