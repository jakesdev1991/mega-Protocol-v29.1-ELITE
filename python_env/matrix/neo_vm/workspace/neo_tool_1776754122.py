# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# RG parameters (dimensionless)
eta_N = 0.12
eta_D = 0.08
kappa = 0.05
I0 = 1.0

def rg_flow(ln_q, y):
    """dy/dln_q for [Phi_N, Phi_D]"""
    phi_N, phi_D = y
    dphi_N = eta_N * phi_N * (1 - phi_N**2 / I0**2) - kappa * phi_D**2
    dphi_D = eta_D * phi_D * (1 - phi_D**2 / I0**2) + kappa * phi_N * phi_D
    return [dphi_N, dphi_D]

# initial conditions near the "healthy" vacuum
y0 = [0.9, 0.1]  # Phi_N ~ I0, Phi_D small
ln_q_span = np.linspace(-10, 10, 500)

sol = solve_ivp(rg_flow, (ln_q_span[0], ln_q_span[-1]), y0,
                t_eval=ln_q_span, dense_output=True)

# compute effective coupling correction factor
# Pi_mix ~ (alpha/pi)^2 * (Phi_D/Phi_N) * ln^2(q^2/m_e^2)
# Here we set alpha=1/137 and track the ratio
alpha0 = 1/137.036
ln_ratio_sq = ln_q_span**2
Pi_mix = (alpha0/np.pi)**2 * (sol.y[1,:] / (sol.y[0,:] + 1e-12)) * ln_ratio_sq

# Plot: ratio blows up → mixing term diverges → fake Landau pole
fig, ax = plt.subplots(1,2, figsize=(12,5))
ax[0].plot(ln_q_span, sol.y[0,:], label='Phi_N')
ax[0].plot(ln_q_span, sol.y[1,:], label='Phi_D')
ax[0].set_xlabel('ln(q)')
ax[0].set_ylabel('Mode amplitude')
ax[0].legend()
ax[0].set_title('RG Flow: Spurious Growth of Phi_D')

ax[1].plot(ln_q_span, Pi_mix, color='crimson')
ax[1].set_xlabel('ln(q)')
ax[1].set_ylabel('Pi_mix (effective correction)')
ax[1].set_title('Divergent Mixing Term → Fake Landau Pole')
plt.tight_layout()
plt.show()