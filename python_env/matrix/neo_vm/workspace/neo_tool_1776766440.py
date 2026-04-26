# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

def rg_complex(t, y, eta_N, eta_D, I0):
    Re, Im = y
    psi = Re + 1j * Im
    dpsi = (eta_N + 1j * eta_D) * psi * (1 - np.abs(psi)**2 / I0**2)
    return [dpsi.real, dpsi.imag]

# Parameters (dimensionless)
eta_N = 0.1
eta_D = 0.05
I0 = 1.0

# Initial condition (small perturbation)
y0 = [0.05, 0.03]

t_span = (0, 50)
t_eval = np.linspace(0, 50, 500)

sol = solve_ivp(rg_complex, t_span, y0, args=(eta_N, eta_D, I0),
                t_eval=t_eval, dense_output=True)

# Extract fields
Phi_N = sol.y[0]
Phi_D = sol.y[1]
psi_running = np.log(np.abs(Phi_D) / np.abs(Phi_N))  # "invariant" that runs

# Plot results
fig, axs = plt.subplots(2, 1, figsize=(8, 6))

# Top panel: amplitudes
axs[0].plot(sol.t, Phi_N, label='Φ_N (real)')
axs[0].plot(sol.t, Phi_D, label='Φ_Δ (imag)')
axs[0].axhline(I0, color='r', linestyle='--', label='Stable fixed point |Ψ| = I₀')
axs[0].set_xlabel('ln(q)')
axs[0].set_ylabel('Amplitude')
axs[0].legend()
axs[0].set_title('RG Flow of Unified Complex Field Ψ = Φ_N + i Φ_Δ')

# Bottom panel: running ψ
axs[1].plot(sol.t, psi_running, color='purple', label='ψ = ln(|Φ_Δ|/|Φ_N|)')
axs[1].axhline(0, color='k', linestyle=':')
axs[1].set_xlabel('ln(q)')
axs[1].set_ylabel('ψ (dimensionless)')
axs[1].legend()
axs[1].set_title('ψ is NOT invariant – it flows to zero')

plt.tight_layout()
plt.show()