# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- PARAMETERS ---
S_crit = 1.0          # critical shear
nu_S   = 0.5          # RG exponent
gamma  = 0.1          # control gain
dt     = 0.01
t_max  = 10.0

# Two possible definitions of psi (gauge choices)
def psi_audit(S):
    """Audit's (incorrect) interpretation: psi = +ln(xi/xi0)"""
    return -nu_S * np.log(np.abs(S - S_crit))   # gives +ln(xi) after scaling

def psi_correct(S):
    """Correct gauge: psi = -ln(xi/xi0)"""
    return nu_S * np.log(np.abs(S - S_crit))

# Control law: dS/dt = -gamma * sign(S-S_crit) * exp(-psi/nu_S)
def dS_dt(S, psi_func):
    return -gamma * np.sign(S - S_crit) * np.exp(-psi_func(S) / nu_S)

def simulate(S0, psi_func):
    t, S = 0.0, S0
    ts, Ss = [t], [S]
    while t < t_max:
        S += dS_dt(S, psi_func) * dt
        t += dt
        ts.append(t); Ss.append(S)
    return np.array(ts), np.array(Ss)

# Start just above critical point (dangerous region)
S0 = S_crit + 0.5

t_audit, S_audit = simulate(S0, psi_audit)      # audit's gauge → destabilising
t_corr,  S_corr  = simulate(S0, psi_correct)    # correct gauge → stabilising

# --- PLOT ---
plt.figure(figsize=(8,4))
plt.plot(t_audit, S_audit, label='ψ = +ln(ξ) (audit) – drives toward criticality')
plt.plot(t_corr,  S_corr,  label='ψ = –ln(ξ) (correct) – drives away from criticality')
plt.axhline(S_crit, color='k', linestyle='--', label='S_crit')
plt.xlabel('Time')
plt.ylabel('Shear flow S')
plt.title('Gauge‑Dependent Control Law Dynamics')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()