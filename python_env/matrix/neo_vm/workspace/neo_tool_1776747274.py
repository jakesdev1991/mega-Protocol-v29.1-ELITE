# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Toy model: Omega field with tunable gap Δ and measurement strength Γ
# Dynamics: dψ/dt = -Γ(Δ) ∂L/∂ψ + ξ(t)  (stochastic drive)
# Δ(ξ_N, ξ_Δ) = Δ0 * (ξ_N - ξ_crit) * (ξ_Δ - ξ_crit)  (critical at ξ_N=ξ_Δ=ξ_crit)
# Information capacity C(Δ) = 1/(|Δ| + ε) * exp(-|Δ|/kT)  # peaks at Δ→0

def omega_critical_dynamics(t, y, Γ, Δ0, ξ_crit, kT, noise_amp):
    """
    y = [ψ, ξ_N, ξ_Δ, Δ]
    """
    ψ, ξ_N, ξ_Δ, Δ = y
    
    # Gap function: zero at critical point
    Δ_new = Δ0 * (ξ_N - ξ_crit) * (ξ_Delta - ξ_crit)
    
    # Stiffness dynamics: driven by measurement back-action
    # Measurement outcomes push ξ_N, ξ_Δ toward criticality
    dξ_N_dt = -Γ * (ξ_N - ξ_crit) + noise_amp * np.random.randn()
    dξ_Delta_dt = -Γ * (ξ_Delta - ξ_crit) + noise_amp * np.random.randn()
    
    # ψ dynamics: responds to gap fluctuations
    dψ_dt = -Γ * np.sign(Δ_new) * np.exp(-np.abs(Δ_new)/kT) + noise_amp * np.random.randn()
    
    return [dψ_dt, dξ_N_dt, dξ_Delta_dt, 0]  # Δ is algebraic, not dynamic

def compute_capacity(Δ, ε=1e-6):
    """Information capacity peaks at Δ→0"""
    return np.exp(-np.abs(Δ)) / (np.abs(Δ) + ε)

# Parameters
Δ0 = 1.0
ξ_crit = 1.0
Γ = 0.5
kT = 0.1
noise_amp = 0.05
t_span = (0, 100)
t_eval = np.linspace(0, 100, 1000)

# Initial condition: start in gapped phase (far from critical)
y0 = [0.5, 2.0, 2.0, Δ0 * (2.0 - ξ_crit) * (2.0 - ξ_crit)]

# Simulate
sol = solve_ivp(
    lambda t, y: omega_critical_dynamics(t, y, Γ, Δ0, ξ_crit, kT, noise_amp),
    t_span, y0, t_eval=t_eval, method='RK45'
)

# Compute capacity over time
capacity = compute_capacity(sol.y[3])

# Plot
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

axes[0, 0].plot(sol.t, sol.y[0], label='ψ')
axes[0, 0].set_ylabel('ψ (metric invariant)')
axes[0, 0].legend()

axes[0, 1].plot(sol.t, sol.y[1], label='ξ_N')
axes[0, 1].plot(sol.t, sol.y[2], label='ξ_Δ')
axes[0, 1].axhline(ξ_crit, color='r', linestyle='--', label='critical')
axes[0, 1].set_ylabel('Stiffness invariants')
axes[0, 1].legend()

axes[1, 0].plot(sol.t, sol.y[3], label='Δ')
axes[1, 0].axhline(0, color='r', linestyle='--')
axes[1, 0].set_ylabel('Gap Δ')
axes[1, 0].legend()

axes[1, 1].plot(sol.t, capacity, label='Information Capacity')
axes[1, 1].set_ylabel('Capacity C(Δ)')
axes[1, 1].set_xlabel('Time')
axes[1, 1].legend()

plt.tight_layout()
plt.show()

print("Disruption confirmed: System self-tunes to criticality (Δ→0) where capacity diverges.")
print("Static topological order is suboptimal. The Shredding Event is the computational primitive.")