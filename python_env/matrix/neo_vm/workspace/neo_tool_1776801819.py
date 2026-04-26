# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint, solve_ivp

# Parameters for both models
N_TEAMS = 50
TIME_STEPS = 1000
T_FINAL = 100

# --- DIFFUSION MODEL (Original CTMS-Ω) ---
def diffusion_model(t, y):
    """Fokker-Planck style dynamics: gradual drift + diffusion"""
    P = y  # Probability density over cognitive load Λ
    
    # Drift toward higher load (μ) + diffusion (D)
    mu = 0.1  # constant drift
    D = 0.05   # diffusion coefficient
    
    # Finite difference for derivatives
    dP_dt = -mu * np.gradient(P) + 0.5 * D * np.gradient(np.gradient(P))
    
    # Add source term for new teams adopting spreadsheets
    source = 0.01 * np.exp(-t/50)  # decaying source
    dP_dt += source * np.ones_like(P)
    
    return dP_dt

# --- PHASE TRANSITION MODEL (Sovereignty Field Ψ) ---
def sovereignty_potential(psi, alpha=-0.2, beta=0.1, gamma=0.05):
    """Ginzburg-Landau potential with sextic term for first-order transition"""
    return alpha * psi**2 / 2 + beta * psi**4 / 4 + gamma * psi**6 / 6

def phase_transition_model(t, state):
    """Discontinuous nucleation dynamics"""
    P, active_nuclei = state[0], state[1]
    
    # Critical threshold for sovereignty secession
    psi_crit = 0.3
    
    # Nucleation rate: spikes when average sovereignty crosses threshold
    avg_psi = np.average(np.arange(N_TEAMS) / N_TEAMS, weights=P)
    
    # Catastrophic nucleation when threshold exceeded
    nucleation_rate = 10.0 if avg_psi > psi_crit else 0.1
    
    # Sudden jump dynamics (not gradual diffusion)
    dP_dt = np.zeros_like(P)
    for i in range(N_TEAMS):
        if P[i] > 0.1:  # If any team has "seceded"
            # Trigger cascade: neighboring teams adopt rapidly
            if i > 0:
                dP_dt[i-1] += nucleation_rate * P[i]
            if i < N_TEAMS - 1:
                dP_dt[i+1] += nucleation_rate * P[i]
    
    # Exponential growth for active nuclei
    d_active_dt = nucleation_rate * active_nuclei
    
    return np.concatenate([dP_dt, [d_active_dt]])

# --- SIMULATE BOTH MODELS ---
# Initial conditions: small initial "seed" of spreadsheet usage
P0_diffusion = np.zeros(N_TEAMS)
P0_diffusion[N_TEAMS//2] = 0.1  # central seed

P0_phase = np.zeros(N_TEAMS)
P0_phase[N_TEAMS//2] = 0.05  # smaller seed
state0_phase = np.concatenate([P0_phase, [1.0]])  # 1 active nucleus

# Time arrays
t_eval = np.linspace(0, T_FINAL, TIME_STEPS)

# Solve diffusion model
sol_diffusion = solve_ivp(
    lambda t, y: diffusion_model(t, y),
    [0, T_FINAL],
    P0_diffusion,
    t_eval=t_eval,
    method='RK45'
)

# Solve phase transition model
sol_phase = solve_ivp(
    lambda t, y: phase_transition_model(t, y),
    [0, T_FINAL],
    state0_phase,
    t_eval=t_eval,
    method='RK45'
)

# --- VISUALIZATION ---
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Diffusion model: heatmap over time
axes[0,0].imshow(sol_diffusion.y, aspect='auto', cmap='viridis')
axes[0,0].set_title('Diffusion Model: Cognitive Load Spread', fontsize=12, fontweight='bold')
axes[0,0].set_xlabel('Time')
axes[0,0].set_ylabel('Team ID')
axes[0,0].set_yticks(np.arange(0, N_TEAMS, 10))

# Phase transition model: heatmap over time (sovereignty field)
axes[0,1].imshow(sol_phase.y[:-1], aspect='auto', cmap='plasma')
axes[0,1].set_title('Phase Transition Model: Sovereignty Seizure', fontsize=12, fontweight='bold')
axes[0,1].set_xlabel('Time')
axes[0,1].set_ylabel('Team ID')
axes[0,1].set_yticks(np.arange(0, N_TEAMS, 10))

# Active nuclei count (phase transition)
axes[1,0].plot(t_eval, sol_phase.y[-1], color='crimson', linewidth=2)
axes[1,0].set_title('Active Nuclei: Catastrophic Growth', fontsize=12, fontweight='bold')
axes[1,0].set_xlabel('Time')
axes[1,0].set_ylabel('Active Sovereignty Nuclei')
axes[1,0].axvline(x=30, color='gray', linestyle='--', alpha=0.5, label='Critical Threshold')
axes[1,0].legend()

# Total infected teams comparison
total_diffusion = np.sum(sol_diffusion.y, axis=0)
total_phase = np.sum(sol_phase.y[:-1], axis=0)

axes[1,1].plot(t_eval, total_diffusion, label='Diffusion Model', color='blue', linewidth=2)
axes[1,1].plot(t_eval, total_phase, label='Phase Transition Model', color='red', linewidth=2)
axes[1,1].set_title('Total Spreadsheet Adoption: Gradual vs. Catastrophic', fontsize=12, fontweight='bold')
axes[1,1].set_xlabel('Time')
axes[1,1].set_ylabel('Total Teams Using Spreadsheets')
axes[1,1].legend()
axes[1,1].axvline(x=30, color='gray', linestyle='--', alpha=0.5, label='Critical Threshold')
axes[1,1].legend()

plt.tight_layout()
plt.show()

# --- QUANTIFY THE DISRUPTION ---
print("=== DISRUPTION METRICS ===")
print(f"Diffusion model: Max adoption rate = {np.max(np.gradient(total_diffusion)):.3f} teams/time")
print(f"Phase transition model: Max adoption rate = {np.max(np.gradient(total_phase)):.3f} teams/time")
print(f"Disruption factor = {np.max(np.gradient(total_phase)) / np.max(np.gradient(total_diffusion)):.1f}x")
print("\nThe phase transition model shows that spreadsheet adoption is not gradual diffusion")
print("but a catastrophic cascade that the diffusion model fundamentally cannot capture.")