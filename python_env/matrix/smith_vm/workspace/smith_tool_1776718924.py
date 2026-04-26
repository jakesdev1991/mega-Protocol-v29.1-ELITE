# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Higher‑Order Lattice Polarization
Checks mass‑positivity and perturbative validity for the
(Phi_N, Phi_Delta) decomposition.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbolic parameters (positive constants)
m, g = sp.symbols('m g', positive=True)   # bare mass, coupling
Phi_N, Phi_D = sp.symbols('Phi_N Phi_D', real=True)   # fields
# ----------------------------------------------------------------------
# 1. Mass‑positivity constraint: m_e > 0 and m_p > 0
#    m_e = m - g * Phi_N * exp(+Phi_D)
#    m_p = m - g * Phi_N * exp(-Phi_D)
m_e = m - g * Phi_N * sp.exp(Phi_D)
m_p = m - g * Phi_N * sp.exp(-Phi_D)

pos_constraints = [sp.simplify(m_e > 0), sp.simplify(m_p > 0)]
# The stricter condition reduces to:
stricter = sp.simplify(Phi_N < (m/g) * sp.exp(-sp.Abs(Phi_D)))
print("Mass‑positivity (stricter) constraint:")
print(stricter)
print()

# ----------------------------------------------------------------------
# 2. Perturbative expansion parameter
epsilon = g * Phi_N / m
eff_param = epsilon * sp.cosh(Phi_D)
print("Effective expansion parameter:")
print(sp.simplify(eff_param))
print()

# ----------------------------------------------------------------------
# 3. Dynamics assumptions
#    Phi_N follows Poisson recovery → polynomial decay: Phi_N ~ t^{-p}
#    Phi_D may grow: we test linear growth Phi_D = beta * t (beta>0)
t, p, beta = sp.symbols('t p beta', positive=True)
Phi_N_t = t**(-p)          # polynomial decay (representative)
Phi_D_t = beta * t         # linear growth (can be changed to exp, etc.)

# Substitute into constraints
mass_pos_sub = stricter.subs({Phi_N: Phi_N_t, Phi_D: Phi_D_t})
pert_sub     = eff_param.subs({Phi_N: Phi_N_t, Phi_D: Phi_D_t})

print("Mass‑positivity after substituting dynamics:")
print(sp.simplify(mass_pos_sub))
print()
print("Perturbative parameter after substituting dynamics:")
print(sp.simplify(pert_sub))
print()

# ----------------------------------------------------------------------
# 4. Numerical search for failure time t_star
def find_failure_time(p_val=1.0, beta_val=0.1, m_val=1.0, g_val=0.01,
                      eps_thresh=1.0, t_max=100.0, dt=1e-3):
    """
    Returns the earliest t where either:
        - mass‑positivity violated (Phi_N >= (m/g)*exp(-|Phi_D|))
        - perturbative parameter >= eps_thresh
    """
    t_vals = np.arange(dt, t_max, dt)
    Phi_N_vals = t_vals**(-p_val)
    Phi_D_vals = beta_val * t_vals

    # mass‑positivity RHS
    rhs = (m_val/g_val) * np.exp(-np.abs(Phi_D_vals))
    mass_violation = Phi_N_vals >= rhs

    # perturbative parameter
    eps_eff = (g_val * Phi_N_vals / m_val) * np.cosh(Phi_D_vals)
    pert_violation = eps_eff >= eps_thresh

    fail_idx = np.where(mass_violation | pert_violation)[0]
    if len(fail_idx) == 0:
        return None  # no failure within t_max
    t_star = t_vals[fail_idx[0]]
    reason = []
    if mass_violation[fail_idx[0]]:
        reason.append("mass‑positivity")
    if pert_violation[fail_idx[0]]:
        reason.append("perturbative breakdown")
    return t_star, ", ".join(reason)

# Example evaluation
result = find_failure_time(p_val=1.0, beta_val=0.2,
                           m_val=1.0, g_val=0.01,
                           eps_thresh=1.0, t_max=50.0)
if result is None:
    print("No failure detected in the scanned interval.")
else:
    t_star, reason = result
    print(f"First failure at t* ≈ {t_star:.3f} due to: {reason}")

# ----------------------------------------------------------------------
# 5. Optional: symbolic verification that polynomial decay cannot outrun exp decay
#    Solve t^{-p} = (m/g) * exp(-beta*t) for t > 0.
#    This transcendental equation has a finite solution for any p>0, beta>0.
print("\nSymbolic insight: solving t^{-p} = (m/g)*exp(-beta*t)")
t_sym = sp.symbols('t_sym', positive=True)
eq = sp.Eq(t_sym**(-p), (m/g) * sp.exp(-beta * t_sym))
# We cannot solve in closed form, but we can show LHS decays slower than RHS:
lhs_asym = sp.series(t_sym**(-p), t_sym, sp.oo, 2)   # leading term ~ t^{-p}
rhs_asym = sp.series((m/g) * sp.exp(-beta * t_sym), t_sym, sp.oo, 2)  # leading term ~ 0
print("Asymptotic LHS (t→∞):", lhs_asym)
print("Asymptotic RHS (t→∞):", rhs_asym)
print("=> LHS >> RHS for large t → inevitable crossing.")