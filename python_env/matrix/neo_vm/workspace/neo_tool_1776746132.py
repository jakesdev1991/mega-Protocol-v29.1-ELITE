# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# --- Model parameters ---
S_crit = 1.0          # critical shear
nu = 0.5              # critical exponent
gamma = 0.2           # feedback gain
t_span = (0, 50)
t_eval = np.linspace(*t_span, 500)

def m_eff(S):
    """Effective mass that changes sign at the critical point."""
    return S - S_crit

def psi(S):
    """Pseudo‑Riemannian invariant: ln(m_eff)."""
    return np.log(np.abs(m_eff(S)))

# --- Control laws ---
def original_control(t, S):
    """Original (destabilizing) law: drives S toward S_crit."""
    return -gamma * np.sign(S - S_crit) * np.exp(-psi(S) / nu)

def toggle_control(t, S):
    """Toggle law: flips sign when ψ changes sign (i.e., when m_eff crosses zero)."""
    # tanh(ψ) changes sign exactly when ψ does
    return -gamma * np.tanh(psi(S)) * np.exp(-np.abs(psi(S)) / nu)

# --- Simulate both controllers ---
sol_original = solve_ivp(original_control, t_span, [1.5], t_eval=t_eval, max_step=0.1)
sol_toggle   = solve_ivp(toggle_control,   t_span, [1.5], t_eval=t_eval, max_step=0.1)

# --- Plot results ---
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(sol_original.t, sol_original.y[0], label='Original (destabilizing)', lw=2)
ax.plot(sol_toggle.t,   sol_toggle.y[0],   label='Toggle (stabilizing)', lw=2)
ax.axhline(S_crit, color='k', linestyle='--', label='Critical shear')
ax.set_xlabel('Time')
ax.set_ylabel('Shear flow S')
ax.set_title('Control Law Comparison: Original vs. Toggle')
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()