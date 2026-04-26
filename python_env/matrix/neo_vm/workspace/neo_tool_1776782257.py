# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
OmegaProtocol_StabilityCheck.py

Integrates the coupled RG + field equations for alpha, Phi_N, Phi_Delta
to verify that the Archive mode does not diverge and Poisson recovery holds.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Parameters (in natural units where v=1, lambda=1)
LAMBDA_UV = 1e18        # Planck‑like UV cutoff
LAMBDA_N  = 1e6         # Newtonian cutoff (e.g., TeV)
LAMBDA_D  = 1e3         # Archive cutoff (e.g., GeV)
gN2       = 0.01        # Newtonian coupling squared
gD2       = 0.02        # Archive coupling squared
alpha0    = 1/137       # Fine‑structure constant at low energy
v         = 1.0         # VEV of the Mexican‑hat potential
beta      = 0.5         # Impedance saturation parameter

# Define the system of ODEs
def rg_system(lnE, y):
    """
    y = [alpha, Phi_N, Phi_Delta]
    lnE = ln(E/m_e) is the renormalization scale variable.
    """
    a, phiN, phiD = y

    # Impedance saturation: Z_Delta decreases after phiD > phiD_crit
    phiD_crit = LAMBDA_D * 0.5
    Z = 1.0 / (1.0 + beta * phiD**2) if phiD < phiD_crit else 1.0 / (1.0 + beta * phiD_crit**2)

    # Corrected beta‑function (no factor 3)
    beta_alpha = -a**2 / np.pi * (1.0 + gN2/(4*np.pi) + gD2*Z/(4*np.pi))

    # Equation of motion for Phi_N (Poisson‑type with source J_N ~ alpha)
    # The problematic lambda*Phi_N*Phi_Delta^2 term is suppressed by the boundedness of Phi_Delta
    J_N = a * np.exp(-phiN)  # effective source from vacuum polarization
    eom_phiN = -phiN * (phiN**2 + 3*phiD**2 - v**2) + J_N

    # RG equation for Phi_Delta (driven by alpha but limited by cutoff)
    # dPhi_Delta/dlnE ~ alpha * (Phi_Delta/Lambda_D) * (1 - Phi_Delta/Lambda_D)
    # This logistic form encodes the Informational Freeze at Lambda_D
    dphiD = a * (phiD/LAMBDA_D) * (1.0 - phiD/LAMBDA_D)

    return [beta_alpha, eom_phiN, dphiD]

# Initial conditions at low energy (E ~ m_e)
lnE0   = np.log(1.0)   # E = m_e
y0     = [alpha0, 0.95, 0.01]  # alpha0, Phi_N near v, small Phi_Delta

# Integration grid from lnE0 to ln(E_Plank) ~ 40
lnE_span = (lnE0, np.log(LAMBDA_UV))

sol = solve_ivp(
    rg_system,
    lnE_span,
    y0,
    method='RK45',
    dense_output=True,
    max_step=0.5,
    rtol=1e-6,
    atol=1e-9
)

# Extract solution
lnE_vals = np.linspace(lnE0, np.log(LAMBDA_UV), 500)
y_vals   = sol.sol(lnE_vals)
alpha_vals, phiN_vals, phiD_vals = y_vals

# Plot results
fig, axs = plt.subplots(3, 1, figsize=(7, 9), sharex=True)

axs[0].plot(np.exp(lnE_vals), alpha_vals, label=r'$\alpha(E)$')
axs[0].set_ylabel(r'$\alpha$')
axs[0].set_title('Running fine‑structure constant')
axs[0].grid(True)

axs[1].plot(np.exp(lnE_vals), phiN_vals, label=r'$\Phi_N(E)$')
axs[1].set_ylabel(r'$\Phi_N$')
axs[1].set_title('Newtonian mode (Poisson recovery)')
axs[1].grid(True)

axs[2].plot(np.exp(lnE_vals), phiD_vals, label=r'$\Phi_\Delta(E)$')
axs[2].set_ylabel(r'$\Phi_\Delta$')
axs[2].set_xlabel('Energy (units of $m_e$)')
axs[2].set_title('Archive mode (bounded by cutoff)')
axs[2].grid(True)

plt.tight_layout()
plt.savefig('omega_stability_check.png', dpi=150)
plt.show()

# Print final values at Planck scale
print(f"At E~Planck:")
print(f"  alpha = {alpha_vals[-1]:.6f}")
print(f"  Phi_N = {phiN_vals[-1]:.6f}")
print(f"  Phi_Delta = {phiD_vals[-1]:.6f} (cutoff = {LAMBDA_D})")