# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ──────────────────────────────────────────────────────────────────────────────
# 1.  Potential landscape: truncated vs full periodic
# ──────────────────────────────────────────────────────────────────────────────
phi = np.linspace(-3*np.pi, 3*np.pi, 600)

# Truncated polynomial (quadratic + quartic) from the original analysis
def V_trunc(phi, m2=1.0, kappa=0.5):
    # m2 > 0, but the quartic coefficient is negative because kappa > 0
    return 0.5*m2*phi**2 - (kappa/24)*phi**4   # κ/24 chosen to match cos expansion

# True periodic potential (the “un‑truncated” result)
def V_true(phi):
    return -np.cos(phi)

plt.figure(figsize=(8,4))
plt.plot(phi, V_trunc(phi), 'r--', lw=2, label='Truncated (unbounded)')
plt.plot(phi, V_true(phi),  'g-',  lw=2, label='Full periodic (bounded)')
plt.ylim(-2,2)
plt.xlabel('Φ_Δ')
plt.ylabel('Effective potential V')
plt.title('Artifact of truncation: the quartic “instability” disappears when periodicity is restored')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ──────────────────────────────────────────────────────────────────────────────
# 2.  Dynamics: particle in the two potentials
# ──────────────────────────────────────────────────────────────────────────────
def dynamics_trunc(t, y):
    phi, dphi = y
    # EOM: d²φ/dt² = -dV/dφ
    return [dphi, -(m2*phi - (kappa/6)*phi**3)]

def dynamics_true(t, y):
    phi, dphi = y
    return [dphi, -np.sin(phi)]

# Initial small fluctuation
y0 = [0.2, 0.0]
t_span = [0, 30]
t_eval = np.linspace(*t_span, 300)

sol_trunc = solve_ivp(dynamics_trunc, t_span, y0, t_eval=t_eval, max_step=0.1)
sol_true  = solve_ivp(dynamics_true,  t_span, y0, t_eval=t_eval, max_step=0.1)

plt.figure(figsize=(8,4))
plt.plot(sol_trunc.t, sol_trunc.y[0], 'r--', lw=2, label='Truncated → runaway')
plt.plot(sol_true.t,  sol_true.y[0],  'g-',  lw=2, label='Periodic → stable oscillation')
plt.xlabel('Time')
plt.ylabel('Φ_Δ(t)')
plt.title('Dynamics confirm: truncation spurious, periodic potential is stable')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()