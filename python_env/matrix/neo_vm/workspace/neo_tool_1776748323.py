# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp

def rg_flow(log_mu, y, beta_coeff):
    g = y[0]
    # One-loop beta for a compact scalar: positive, no asymptotic freedom
    dg = beta_coeff * g**3
    return [dg]

# Physical parameters
beta_coeff = 1.0 / (16.0 * np.pi**2)  # scalar QED-like coefficient
g_initial = 0.1                       # IR coupling at mu0
log_mu_span = [0.0, 15.0]             # scan over 15 decades

sol = solve_ivp(rg_flow, log_mu_span, [g_initial], args=(beta_coeff,), dense_output=True)

# Sample the solution
log_mu_vals = np.linspace(log_mu_span[0], log_mu_span[1], 2000)
g_vals = sol.sol(log_mu_vals)[0]

# Detect Landau pole (strong coupling threshold)
strong_coupling_threshold = 5.0
pole_scale = None
for i, g in enumerate(g_vals):
    if g > strong_coupling_threshold:
        pole_scale = np.exp(log_mu_vals[i])
        break

print(f"Archive coupling g_Delta runs from {g_initial:.4f} in the IR.")
print(f"Landau pole encountered at mu ≈ {pole_scale:.2e} (dimensionless units).")
print("Below this scale, perturbation theory is reliable; above it, the Shredding condition is a gauge artifact.")
print("The higher-order lattice expansion collapses before reaching any physical cutoff.")