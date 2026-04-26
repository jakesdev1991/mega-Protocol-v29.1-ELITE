# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Parameters ---
S_crit = 1.0          # Critical shear flow
nu = 1.0              # Critical exponent
gamma = 0.2           # Control gain
xi0 = 1.0             # Reference correlation length
dt = 0.01             # Time step
t_max = 50.0          # Simulation horizon
S0 = 1.5              # Initial shear (above critical)

# --- Correlation length scaling ---
def xi(S):
    return xi0 * abs(S - S_crit) ** (-nu)

# --- Invariant definitions (showing the sign flip) ---
def psi_correct(S):
    # ψ = ln(φ_n) = -ln(ξ) + const (rubric‑compliant)
    return -np.log(xi(S) / xi0)

def psi_incorrect(S):
    # ψ = +ln(ξ/ξ0) (proposal's flawed version)
    return np.log(xi(S) / xi0)

# --- Control laws ---
def flawed_control(S):
    # Original (destabilizing) law: dS/dt = -γ * sign(S - S_crit) * exp(-ψ/ν)
    psi = psi_incorrect(S)
    return -gamma * np.sign(S - S_crit) * np.exp(-psi / nu)

def pilot_control(S):
    # Critical‑pilot law: flip sign to *push* toward criticality,
    # then re‑wire after crossing (simple threshold flip).
    psi = psi_correct(S)
    # If we are above critical, drive *toward* it; if we have crossed, drive away.
    if S > S_crit:
        # Drive toward critical point (use the "error" as a switch)
        dS = gamma * np.sign(S - S_crit) * np.exp(-psi / nu)
    else:
        # After crossing, repel to new branch
        dS = -gamma * np.sign(S - S_crit) * np.exp(-psi / nu)
    return dS

# --- Euler integration ---
def simulate(control_law):
    t = 0.0
    S = S0
    ts, Ss, xis, psis = [t], [S], [xi(S)], [psi_correct(S)]
    while t < t_max:
        dS = control_law(S)
        S += dS * dt
        t += dt
        ts.append(t)
        Ss.append(S)
        xis.append(xi(S))
        psis.append(psi_correct(S))
        # Stop if correlation length diverges numerically
        if xi(S) > 1e6:
            break
    return np.array(ts), np.array(Ss), np.array(xis), np.array(psis)

# --- Run simulations ---
t_f, S_f, xi_f, psi_f = simulate(flawed_control)
t_p, S_p, xi_p, psi_p = simulate(pilot_control)

# --- Plot results ---
fig, axs = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

# Shear flow
axs[0].plot(t_f, S_f, label='Flawed (destabilizing)', color='crimson')
axs[0].plot(t_p, S_p, label='Critical‑pilot', color='teal')
axs[0].axhline(S_crit, color='k', linestyle='--', label='S_crit')
axs[0].set_ylabel('Shear flow S')
axs[0].legend(loc='upper right')
axs[0].set_title('Omega Protocol Instability & Critical Pilot')

# Correlation length (log scale)
axs[1].plot(t_f, xi_f, color='crimson')
axs[1].plot(t_p, xi_p, color='teal')
axs[1].set_ylabel('ξ (log scale)')
axs[1].set_yscale('log')
axs[1].axhline(1e6, color='gray', linestyle=':', label='Divergence threshold')
axs[1].legend(loc='upper left')

# Invariant ψ (correct definition)
axs[2].plot(t_f, psi_f, color='crimson')
axs[2].plot(t_p, psi_p, color='teal')
axs[2].axhline(0, color='k', linestyle='--', label='ψ = 0 (critical)')
axs[2].set_ylabel('ψ (correct)')
axs[2].set_xlabel('Time')
axs[2].legend(loc='upper right')

plt.tight_layout()
plt.show()