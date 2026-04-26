# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ghost‑Induced Shredding of the Orthogonal Decomposition
-------------------------------------------------------
Integrates the coupled RG equations for (Φ_N, Φ_Δ) including the ghost‑generated
cubic term -ξ Φ_Δ³.  Detects the finite‑scale singularity where Φ_Δ diverges
and checks the Poisson‑recovery residual.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# Parameters (I₀ = 1, all couplings O(0.1–1) as typical in the Omega Protocol)
I0 = 1.0
eta_N = 0.15
eta_D = 0.10          # η_Δ > 0 (naively stable)
kappa = 0.20
xi = 0.35             # ghost coefficient – can be > |η_Δ|

# Initial conditions near the Gaussian fixed point
Phi_N0 = 0.05
Phi_D0 = 0.03
L0 = 0.0               # ln(q/q₀)

# ─────────────────────────────────────────────────────────────────────────────
def rg_flow(L, y):
    """
    RHS of the RG flow:
    y[0] = Φ_N(L), y[1] = Φ_Δ(L)
    """
    PhiN, PhiD = y
    # Assemble the β‑functions
    betaN = eta_N * PhiN * (1 - PhiN**2 / I0**2) - kappa * PhiD**2
    betaD = (eta_D * PhiD * (1 - PhiD**2 / I0**2)
             + kappa * PhiN * PhiD
             - xi * PhiD**3)          # <-- ghost term
    return [betaN, betaD]

def shredding_event(L, y):
    """Event that triggers when Φ_Δ exceeds a large threshold."""
    PhiD = y[1]
    return PhiD - 1e6   # zero‑crossing signals divergence

shredding_event.terminal = True
shredding_event.direction =  1

# ─────────────────────────────────────────────────────────────────────────────
# Integrate from L0 until shredding (or L_max)
L_max = 50.0
sol = solve_ivp(
    rg_flow,
    t_span=(L0, L_max),
    y0=[Phi_N0, Phi_D0],
    method='RK45',
    events=shredding_event,
    dense_output=True,
    rtol=1e-8,
    atol=1e-10
)

if sol.status == 1:
    Lc = sol.t_events[0][0]
    print(f"\n>>> SHREDDING EVENT at L_c = {Lc:.4f}  (q_c = q0·exp({Lc:.4f})) <<<")
else:
    print("\n>>> No shredding detected up to L_max <<<")

# ─────────────────────────────────────────────────────────────────────────────
# Post‑process: compute Poisson‑recovery residual
# In the continuum we would have ∂²Φ_N = -κ Φ_Δ².  In the RG‑only language we
# can construct an algebraic surrogate:  R ≡ |Φ_N| - (κ/2) Φ_Δ².
# When Φ_N is driven negative and large in magnitude, R → -∞, signalling breakdown.
PhiN = sol.y[0]
PhiD = sol.y[1]
residual = np.abs(PhiN) - 0.5 * kappa * PhiD**2

# ─────────────────────────────────────────────────────────────────────────────
# Plot the flow and the residual
fig, axs = plt.subplots(2, 1, figsize=(6, 6))

axs[0].plot(sol.t, PhiN, label=r'$\Phi_N$')
axs[0].plot(sol.t, PhiD, label=r'$\Phi_\Delta$')
axs[0].set_xlabel(r'$\ln(q/q_0)$')
axs[0].set_ylabel(r'$\Phi$')
axs[0].set_title('RG flow with ghost term')
axs[0].legend()
axs[0].grid(True)

axs[1].plot(sol.t, residual, color='crimson', label='Poisson‑recovery residual')
axs[1].set_xlabel(r'$\ln(q/q_0)$')
axs[1].set_ylabel(r'$|\Phi_N| - \frac{\kappa}{2}\Phi_\Delta^2$')
axs[1].set_title('Residual (negative → recovery fails)')
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()