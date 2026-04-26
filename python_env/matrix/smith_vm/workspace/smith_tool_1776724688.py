# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Shredding‑Flaw Validator
---------------------------------------
Checks the mass‑positivity constraint, perturbative breakdown,
and the invariant J* for a given evolution of Phi_N and Phi_Delta.

Usage:
    python3 validate_shredding.py   # runs a demo scenario
"""

import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Model parameters (can be overridden)
# ----------------------------------------------------------------------
m   = 1.0          # bare mass scale
g   = 0.1          # coupling to the Phi fields
Phi_N0 = 1.0       # initial consensus field amplitude
p     = 1.0        # power‑law decay exponent for Phi_N(t) ~ t^{-p}
beta  = 0.2        # linear growth rate for Phi_Delta(t) = beta * t
# For exponential growth set: Phi_Delta(t) = Phi_D0 * np.exp(gamma * t)
Phi_D0 = 0.0
gamma  = 0.0       # set >0 for exponential growth

# Time grid
t_max = 50.0
Nt    = 2000
t     = np.linspace(0, t_max, Nt)
dt    = t[1] - t[0]

# ----------------------------------------------------------------------
# Field evolutions
# ----------------------------------------------------------------------
def Phi_N(t):
    """Power‑law decay (Poisson‑type recovery in static limit)."""
    return Phi_N0 * (1.0 + t) ** (-p)   # +1 avoids division by zero at t=0

def Phi_Delta(t):
    """Linear or exponential growth."""
    if gamma > 0.0:
        return Phi_D0 * np.exp(gamma * t)
    else:
        return beta * t

# ----------------------------------------------------------------------
# Derived quantities
# ----------------------------------------------------------------------
Phi_N_vals   = Phi_N(t)
Phi_D_vals   = Phi_Delta(t)

# Mass‑positivity bound
bound = (m / g) * np.exp(-np.abs(Phi_D_vals))

# Effective masses (for diagnostics)
m_e = m - g * Phi_N_vals * np.exp(+Phi_D_vals)
m_p = m - g * Phi_N_vals * np.exp(-Phi_D_vals)

# Perturbative expansion parameter
eps = g * Phi_N_vals / m          # = ε = g Φ_N / m
pert_param = eps * np.cosh(Phi_D_vals)

# Invariant J* = Φ_N * exp(-|Φ_Δ|)
J_star = Phi_N_vals * np.exp(-np.abs(Phi_D_vals))
J_thresh = m / g   # maximum allowed J* before shredding

# ----------------------------------------------------------------------
# Violation detection
# ----------------------------------------------------------------------
# 1. Mass‑positivity violation (either m_e or m_p ≤ 0)
mass_viol_idx = np.where((m_e <= 0) | (m_p <= 0))[0]
# 2. Perturbative breakdown (conservative threshold)
pert_viol_idx = np.where(pert_param >= 0.1)[0]   # 0.1 ≪ 1, can be tightened
# 3. Invariant J* exceeding threshold
J_viol_idx    = np.where(J_star >= J_thresh)[0]

def first_violation(idx_array):
    return t[idx_array[0]] if idx_array.size > 0 else None

t_mass   = first_violation(mass_viol_idx)
t_pert   = first_violation(pert_viol_idx)
t_J      = first_violation(J_viol_idx)

# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------
print("=== Omega Protocol Shredding Validation ===")
print(f"Time grid: 0 → {t_max} ({Nt} points)")
print()
print("Violation times (if any):")
print(f"  Mass‑positivity (m_e≤0 or m_p≤0): {t_mass if t_mass is not None else 'None'}")
print(f"  Perturbative breakdown (ε·coshΦΔ ≥ 0.1): {t_pert if t_pert is not None else 'None'}")
print(f"  Invariant J* ≥ m/g: {t_J if t_J is not None else 'None'}")
print()
if t_mass is not None or t_pert is not None or t_J is not None:
    t_first = min([x for x in [t_mass, t_pert, t_J] if x is not None])
    print(f"→ First shredding‑relevant violation occurs at t ≈ {t_first:.3f}")
else:
    print("→ No violation detected within the simulated interval.")

# ----------------------------------------------------------------------
# Optional diagnostic plot
# ----------------------------------------------------------------------
try:
    plt.figure(figsize=(10, 6))
    plt.subplot(3,1,1)
    plt.plot(t, Phi_N_vals, label=r'$\Phi_N(t)$')
    plt.plot(t, bound, '--', label=r'$(m/g)e^{-|\Phi_\Delta|}$')
    plt.yscale('log')
    plt.ylabel(r'$\Phi_N$, bound')
    plt.legend(loc='upper right')
    plt.title('Field Evolution and Mass‑Positivity Bound')

    plt.subplot(3,1,2)
    plt.plot(t, pert_param, label=r'$\varepsilon\cosh\Phi_\Delta$')
    plt.axhline(0.1, color='r', linestyle='--', label='Perturbative warning (0.1)')
    plt.yscale('log')
    plt.ylabel(r'Perturbation parameter')
    plt.legend(loc='upper right')

    plt.subplot(3,1,3)
    plt.plot(t, J_star, label=r'$J^*=\Phi_N e^{-|\Phi_\Delta|}$')
    plt.axhline(J_thresh, color='g', linestyle='--', label=r'$J^*_{\text{max}}=m/g$')
    plt.yscale('log')
    plt.xlabel('Time')
    plt.ylabel(r'$J^*$')
    plt.legend(loc='upper right')

    plt.tight_layout()
    plt.show()
except Exception as e:
    print("Plotting skipped:", e)