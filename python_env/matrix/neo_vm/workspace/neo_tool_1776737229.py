# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# parameters
alpha0 = 1/137.035999084          # fine-structure constant at low energy
gN0    = 0.05                     # Newtonian mode coupling
gD0    = 0.03                     # Archive mode coupling
lam    = 1.0                      # lambda in Mexican-hat
v      = 1.0                      # vacuum expectation value
PhiN0  = 0.9*v                    # initial field values close to vacuum
PhiD0  = 0.1*v

# stiffness invariants as functions of fields
def xiN(PhiN, PhiD):
    return 1.0/np.sqrt(lam * (3*PhiN**2 + PhiD**2 - v**2))

def xiD(PhiN, PhiD):
    return 1.0/np.sqrt(lam * (PhiN**2 + 3*PhiD**2 - v**2))

# RG scale (log of momentum squared)
lnq2_start = np.log(1e-6)   # IR scale
lnq2_end   = np.log(1e6)    # UV scale

# ODE system for the running couplings and field expectation values.
# Unknowns: y[0]=alpha, y[1]=gN, y[2]=gD, y[3]=PhiN, y[4]=PhiD
def rg_flow(lnq2, y):
    a, gN, gD, PhiN, PhiD = y
    # compute stiffness ratio
    xi_N = xiN(PhiN, PhiD)
    xi_D = xiD(PhiN, PhiD)
    ratio = xi_N / xi_D

    # standard QED term
    beta_a = - a**2 / np.pi

    # naive linear contributions (with factor 3 for gD)
    # beta_a -= a**2/np.pi * (gN**2/(4*np.pi) + 3*gD**2/(4*np.pi))

    # disruptive non‑linear mixing term: gN*gD * ratio
    # this can dominate over the naive 3*gD^2 term
    beta_a -= a**2/np.pi * (gN**2/(4*np.pi) + gN*gD*ratio)

    # simple beta functions for the scalar couplings (toy model)
    beta_gN = -0.1 * gN**3
    beta_gD = -0.1 * gD**3

    # field evolution (slow roll approx)
    dPhiN_dlnq2 = - 0.01 * (PhiN - v)
    dPhiD_dlnq2 = - 0.01 * (PhiD)

    return [beta_a, beta_gN, beta_gD, dPhiN_dlnq2, dPhiD_dlnq2]

# initial conditions
y0 = [alpha0, gN0, gD0, PhiN0, PhiD0]

sol = solve_ivp(rg_flow,
                t_span=(lnq2_start, lnq2_end),
                y0=y0,
                method='RK45',
                dense_output=True)

# plot the running of alpha
lnq2_vals = np.linspace(lnq2_start, lnq2_end, 500)
alpha_run = sol.sol(lnq2_vals)[0]

plt.figure(figsize=(6,4))
plt.plot(np.exp(lnq2_vals), alpha_run, label='α with non‑linear mixing')
plt.axhline(y=alpha0, color='gray', linestyle='--', label='low‑energy α')
plt.xscale('log')
plt.xlabel('q² (arbitrary units)')
plt.ylabel('α(q²)')
plt.title('Disruptive RG flow: Archive mode can freeze α')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()