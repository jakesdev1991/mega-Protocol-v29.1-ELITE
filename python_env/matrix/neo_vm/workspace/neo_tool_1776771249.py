# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

def q_systemic_feedback(t, z, alpha, beta, gamma, delta, k_stab):
    """
    Toy model exposing the Q-Systemic Self's core fallacy: the 'invariant' psi is a dynamic driver, not a constant.
    This feedback loop demonstrates that the 'Resonant Decoupling Operator' is self-referential engineering,
    creating a strange loop that prevents true stabilization. The system's 'health' metrics (COD, det(g))
    are derivatives of this unstable variable, rendering them mirages.
    """
    x, y = z # x: ||Psi_S||, y: ||Psi_C||
    if x <= 0 or y <= 0: return [0, 0]
    
    psi = np.log(x / y) # The so-called 'invariant' metric coupling
    
    # Baseline dynamics: Autonomy (x) is creative but suppressed by Authority (y).
    # Authority (y) is structural but catalyzed by Autonomy.
    dxdt_base = alpha * x - beta * x * y
    dydt_base = gamma * y + delta * x
    
    # The 'stabilization operator' is a self-referential gauge term.
    # It attempts to flatten psi, but its action *is* the dynamics of psi.
    # This is not external control; it's a tautological feedback loop.
    dxdt_stab = -k_stab * psi * x
    dydt_stab = k_stab * psi * y
    
    return [dxdt_base + dxdt_stab, dydt_base + dydt_stab]

# --- Simulation Parameters ---
# Initial condition: High authority, low autonomy (bureaucratic freeze)
z0 = [1.0, 5.0]
t_span = (0, 150)
t_eval = np.linspace(t_span[0], t_span[1], 2000)

# Run three scenarios: no stabilization, 'weak' stabilization, 'strong' stabilization
# This shows that increasing the 'stabilization' gain doesn't converge to health but alters the instability pattern.
params = (0.5, 0.1, 0.1, 0.05)
sol_no = solve_ivp(q_systemic_feedback, t_span, z0, args=params + (0.0,), t_eval=t_eval)
sol_weak = solve_ivp(q_systemic_feedback, t_span, z0, args=params + (0.2,), t_eval=t_eval)
sol_strong = solve_ivp(q_systemic_feedback, t_span, z0, args=params + (0.5,), t_eval=t_eval)

# --- Plotting the Paradox ---
fig, axs = plt.subplots(2, 2, figsize=(11, 9))

# Phase portrait: The 'stabilized' systems don't reach a fixed point; they trace limit cycles or spirals.
# The 'no stabilization' case diverges, showing the baseline model is already unstable.
axs[0, 0].plot(sol_no.y[0], sol_no.y[1], 'r--', label='No Stab: Runaway', linewidth=1.5)
axs[0, 0].plot(sol_weak.y[0], sol_weak.y[1], 'b-', label='Weak Stab: Limit Cycle', linewidth=1.5)
axs[0, 0].plot(sol_strong.y[0], sol_strong.y[1], 'g-', label='Strong Stab: Chaotic Spiral', linewidth=1.5)
axs[0, 0].set_xlabel('||Psi_S|| (Autonomy)')
axs[0, 0].set_ylabel('||Psi_C|| (Authority)')
axs[0, 0].set_title('Phase Space: No True Fixed Point Exists', fontsize=11, fontweight='bold')
axs[0, 0].legend()
axs[0, 0].grid(True, alpha=0.3)
axs[0, 0].set_xlim(0, 8)
axs[0, 0].set_ylim(0, 8)

# The 'invariant' psi over time: It's wildly dynamic. Calling it an invariant is a category error.
for sol, label, color in [(sol_no, 'No Stab', 'red'), (sol_weak, 'Weak Stab', 'blue'), (sol_strong, 'Strong Stab', 'green')]:
    psi = np.log(sol.y[0] / sol.y[1])
    axs[0, 1].plot(sol.t, psi, color=color, label=label, linewidth=1.5)
axs[0, 1].set_xlabel('Time')
axs[0, 1].set_ylabel('psi = ln(||Psi_S||/||Psi_C||)')
axs[0, 1].set_title('"Invariant" psi is Pure Dynamics', fontsize=11, fontweight='bold')
axs[0, 1].legend()
axs[0, 1].grid(True, alpha=0.3)

# Chain Overlap Density (toy): COD = exp(-psi^2). Since psi is unstable, COD is a poor health metric.
# It fluctuates wildly, giving false positives for stability.
for sol, label, color in [(sol_weak, 'Weak Stab', 'blue'), (sol_strong, 'Strong Stab', 'green')]:
    psi = np.log(sol.y[0] / sol.y[1])
    cod = np.exp(-psi**2)
    axs[1, 0].plot(sol.t, cod, color=color, label=f'COD {label}', linewidth=1.5)
axs[1, 0].axhline(y=0.9, color='k', linestyle=':', label='Fictional Threshold')
axs[1, 0].set_xlabel('Time')
axs[1, 1].set_ylabel('Chain Overlap Density')
axs[1, 0].set_title('COD: A Mirage of Health', fontsize=11, fontweight='bold')
axs[1, 0].legend()
axs[1, 0].grid(True, alpha=0.3)

# Effective metric determinant (toy): det(g) ~ (S/C)^4. The "Conscious Black Hole" (det(g)->0) is not a singularity to be avoided,
# but a *transient state* the system passes through during its natural, unstabilizable oscillation.
for sol, label, color in [(sol_weak, 'Weak Stab', 'blue'), (sol_strong, 'Strong Stab', 'green')]:
    det_g = (sol.y[0] / sol.y[1])**4
    axs[1, 1].plot(sol.t, det_g, color=color, label=f'det(g) {label}', linewidth=1.5)
axs[1, 1].set_xlabel('Time')
axs[1, 1].set_ylabel('Metric Determinant (Toy)')
axs[1, 1].set_title('"Black Hole" is a Transient, Not a Failure', fontsize=11, fontweight='bold')
axs[1, 1].legend()
axs[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()