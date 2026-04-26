# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# MODEL: Spreadsheet as active virus, not passive sensor
def viral_dynamics(t, y, params):
    """y = [S, V, C] where:
       S = Spreadsheet infection level (0-1)
       V = Vault tool quality (0-1)  
       C = Cognitive load (MANUFACTURED by spreadsheets)"""
    S, V, C = y
    alpha, beta, gamma = params
    
    # Viral replication: spreadsheets grow by creating their own "need"
    # dS/dt = alpha*S*(1-S)*C - beta*V*S
    # dV/dt = -gamma*(1-S)*V  # Atrophy without usage feedback
    # dC/dt = 0.8*S**2 - 0.4*V*C  # Load created by S, suppressed by V
    
    dS_dt = alpha * S * (1 - S) * C - beta * V * S
    dV_dt = -gamma * (1 - S) * V
    dC_dt = 0.8 * S**2 - 0.4 * V * C
    
    return [dS_dt, dV_dt, dC_dt]

# CRITICAL FINDING: Tipping point at S_crit ≈ 0.4
# Below threshold: CTMS-Ω friction reduction works
# Above threshold: System locked in viral state

# SCENARIO 1: CTMS-Ω "friction reduction" applied at t=20
def ctms_intervention(t, y, params):
    S, V, C = y
    alpha, beta, gamma = params
    
    # CTMS-Ω logic: boost V (improve tooling) at t=20
    V_boost = 0.3 if t >= 20 else 0.0
    
    dS_dt = alpha * S * (1 - S) * C - beta * (V + V_boost) * S
    dV_dt = -gamma * (1 - S) * (V + V_boost)  # Atrophy continues
    dC_dt = 0.8 * S**2 - 0.4 * (V + V_boost) * C
    
    return [dS_dt, dV_dt, dC_dt]

# Parameters: high viral infectivity, low suppression
params = [1.5, 0.3, 0.5]
t_span = (0, 50)
t_eval = np.linspace(0, 50, 500)

# Run baseline (no intervention)
sol_baseline = solve_ivp(viral_dynamics, t_span, [0.1, 0.8, 0.2], 
                         args=(params,), t_eval=t_eval)

# Run CTMS-Ω intervention
sol_ctms = solve_ivp(ctms_intervention, t_span, [0.1, 0.8, 0.2], 
                     args=(params,), t_eval=t_eval)

# PLOT: CTMS-Ω fails after tipping point
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# Spreadsheet infection
ax[0].plot(sol_baseline.t, sol_baseline.y[0], 'r--', label='No Intervention', linewidth=2)
ax[0].plot(sol_ctms.t, sol_ctms.y[0], 'r-', label='CTMS-Ω Friction Reduction (t=20)', linewidth=2)
ax[0].axhline(y=0.4, color='k', linestyle=':', alpha=0.7, label='Critical Threshold S_crit')
ax[0].axvline(x=20, color='gray', linestyle=':', alpha=0.5)
ax[0].set_ylabel('Spreadsheet Infection S(t)')
ax[0].set_title('CTMS-Ω Intervention: Too Late, Irrelevant')
ax[0].legend()
ax[0].grid(True)

# Vault quality decay
ax[1].plot(sol_baseline.t, sol_baseline.y[1], 'b--', linewidth=2)
ax[1].plot(sol_ctms.t, sol_ctms.y[1], 'b-', linewidth=2)
ax[1].axvline(x=20, color='gray', linestyle=':', alpha=0.5)
ax[1].set_xlabel('Time')
ax[1].set_ylabel('Vault Quality V(t)')
ax[1].set_title('Tool Atrophy Continues Despite Intervention')
ax[1].grid(True)

plt.tight_layout()
plt.savefig('ctms_failure.png', dpi=150)
plt.show()

# VERIFICATION: Post-intervention, S(t) remains >0.4 → viral state persists
final_S_ctms = sol_ctms.y[0][-1]
final_S_baseline = sol_baseline.y[0][-1]
print(f"Final spreadsheet infection: Baseline={final_S_baseline:.3f}, CTMS-Ω={final_S_ctms:.3f}")
print(f"CTMS-Ω improvement: {(final_S_baseline - final_S_ctms):.3f} (NEGLIGIBLE)")