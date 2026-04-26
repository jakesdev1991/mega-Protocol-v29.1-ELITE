# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith – Omega Protocol Invariant Validator
Validates the Linux HSA Unified Memory Informational Jerk Stability Analysis.
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# 1. Supplied base data (normalized to I0 = 1)
# ----------------------------------------------------------------------
I0 = 1.0
phi_N = 0.78          # Φ_N / I0
phi_D = 0.35          # Φ_Δ / I0
dot_phi_N = 2.1e3     # s^-1
dot_phi_D = 8.7e3     # s^-1
# Second derivatives are NOT provided; we will treat them as symbols.
ddot_phi_N, ddot_phi_D = sp.symbols('ddot_phi_N ddot_phi_D')
# Third derivatives also unknown.
dddot_phi_N, dddot_phi_D = sp.symbols('dddot_phi_N dddot_phi_D')

# Stiffness (inverse squared) supplied
xi_inv2 = 4.2e6       # s^-2
xi = 1.0 / np.sqrt(xi_inv2)   # s

# Source jerk (given)
J_source = 1.5e12     # s^-3

# ----------------------------------------------------------------------
# 2. Define invariant ψ and its exact derivatives (chain rule)
# ----------------------------------------------------------------------
psi = sp.log(phi_N)                     # dimensionless
dot_psi = sp.diff(psi, sp.Symbol('t'))  # will substitute later
# Using chain rule: dψ/dt = (1/φ_N) * dφ_N/dt
dot_psi_expr = dot_phi_N / phi_N

# Second derivative: d²ψ/dt² = (φ_N * ddot_φ_N - dot_φ_N^2) / φ_N^2
ddot_psi_expr = (phi_N * ddot_phi_N - dot_phi_N**2) / phi_N**2

# Third derivative: d³ψ/dt³ = (φ_N^2 * dddot_φ_N - 3 φ_N dot_φ_N ddot_φ_N + 2 dot_φ_N^3) / φ_N^3
dddot_psi_expr = (phi_N**2 * dddot_phi_N -
                  3 * phi_N * dot_phi_N * ddot_phi_N +
                  2 * dot_phi_N**3) / phi_N**3

# ----------------------------------------------------------------------
# 3. Entropy S_h(ψ, φ_D) and its derivatives w.r.t ψ and φ_D
# ----------------------------------------------------------------------
# Probabilities
p_N = sp.exp(psi) / (sp.exp(psi) + phi_D)
p_D = phi_D / (sp.exp(psi) + phi_D)

# Shannon conditional entropy
S_h = -(p_N * sp.log(p_N) + p_D * sp.log(p_D))

# Derivatives needed for jerk expression
dS_dpsi   = sp.diff(S_h, psi)
d2S_dpsi2 = sp.diff(dS_dpsi, psi)
d3S_dpsi3 = sp.diff(d2S_dpsi2, psi)

dS_dphiD   = sp.diff(S_h, phi_D)
d2S_dphiD2 = sp.diff(dS_dphiD, phi_D)

# ----------------------------------------------------------------------
# 4. Jerk via third‑order finite difference (explicit Δt)
# ----------------------------------------------------------------------
# User must supply the true sampling interval Δt (seconds). Here we keep it symbolic.
dt = sp.symbols('dt', positive=True)

# Build stencil coefficients for third derivative: [-1, 3, -3, 1] / dt^3
J_psi = (dS_dpsi   * dddot_psi_expr +
         3 * d2S_dpsi2 * dot_psi_expr * ddot_psi_expr +
         d3S_dpsi3 * dot_psi_expr**3)

J_phiD = (dS_dphiD   * dddot_phi_D +
          3 * d2S_dphiD2 * dot_phi_D * ddot_phi_D)

# Total jerk (excluding source)
J_total_expr = J_psi + J_phiD + J_source

# ----------------------------------------------------------------------
# 5. Substitute numerical values (where known) and keep unknown derivatives symbolic
# ----------------------------------------------------------------------
subs_dict = {
    phi_N: phi_N,
    phi_D: phi_D,
    dot_phi_N: dot_phi_N,
    dot_phi_D: dot_phi_D,
    # keep ddot_phi_*, dddot_phi_* as symbols
}
J_num = sp.simplify(J_total_expr.subs(subs_dict))
print("Symbolic Jerk expression (with unknown higher derivatives):")
print(J_num)
print("\n")

# ----------------------------------------------------------------------
# 6. Evaluate Jerk assuming the *provided* second‑derivative estimates
# ----------------------------------------------------------------------
# The analysis gave: ddot_phi_N ≈ 4.3e6 s^-2, ddot_phi_D ≈ 1.78e7 s^-2
# and implied ddot_psi ≈ 5.5e6 s^-2, dddot_psi ≈ 1.12e10 s^-3
# We will insert these as numbers to see what the jerk becomes.
ddot_phi_N_val = 4.3e6
ddot_phi_D_val = 1.78e7
# Approximate third derivatives using the same closure as the paper:
# dddot ≈ ddot / xi
dddot_phi_N_val = ddot_phi_N_val / xi
dddot_phi_D_val = ddot_phi_D_val / xi

subs_num = subs_dict.copy()
subs_num.update({
    ddot_phi_N: ddot_phi_N_val,
    ddot_phi_D: ddot_phi_D_val,
    dddot_phi_N: dddot_phi_N_val,
    dddot_phi_D: dddot_phi_D_val,
})
J_val = J_num.subs(subs_num)
print(f"Numerical Jerk (using paper's derivative closure): {J_val:.3e} s^-3")
print(f"Source jerk: {J_source:.3e} s^-3")
print(f"Jerk without source: {J_val - J_source:.3e} s^-3")
print("\n")

# ----------------------------------------------------------------------
# 7. Shredding threshold from invariant condition
# ----------------------------------------------------------------------
# Invariant: Φ_N^2 + 3 Φ_Δ^2 = I0^2  =>  (I0 e^ψ)^2 + 3 (I0 φ_D)^2 = I0^2
# Solve for the critical ψ_c at which equality holds:
psi_c = sp.log(sp.sqrt(1 - 3*phi_D**2))   # note: requires RHS>0
print(f"Critical ψ_c (from invariant): {psi_c.evalf():.3f}")
print(f"Current ψ = {psi.evalf():.3f}")
print(f"ψ < ψ_c ? {psi.evalf() < psi_c.evalf()}  (True => Newtonian mode depleted)")
print("\n")

# Threshold Θ as derived from the invariant (no ad‑hoc prefactor)
# We define Θ = λ I0^2 / (4π) * exp(-ψ)  (the factor from the paper's exponential)
lam = 1.0e10   # s^-2, as used in the analysis
Theta = lam * I0**2 / (4*np.pi) * np.exp(-float(psi))
print(f"Threshold Θ (λ I0^2 / 4π * e^{-ψ}): {Theta:.3e} s^-6")
print("\n")

# ----------------------------------------------------------------------
# 8. Variance estimate (20 % fluctuation assumption)
# ----------------------------------------------------------------------
sigma_J = 0.2 * abs(J_val)
var_J = sigma_J**2
print(f"Assumed 20 % jerk fluctuation → σ_J = {sigma_J:.3e} s^-3")
print(f"Variance σ_J^2 = {var_J:.3e} s^-6")
print(f"Comparison σ_J^2 >> Θ ? {var_J > Theta}")
print("\n")

# ----------------------------------------------------------------------
# 9. Invariant compliance checklist
# ----------------------------------------------------------------------
def check_invariant(name, value, condition):
    ok = condition(value)
    print(f"{name}: {'PASS' if ok else 'FAIL'}  (value={value})")
    return ok

# Φ_N and Φ_Δ must be real and positive
check_invariant("Φ_N > 0", phi_N, lambda x: x > 0)
check_invariant("Φ_Δ > 0", phi_D, lambda x: x > 0)

# Jerk must be finite (no NaN/Inf)
check_invariant("Jerk finite", J_val, lambda x: np.isfinite(x))

# Stability: variance must NOT exceed threshold for stability
stable = var_J <= Theta
print(f"Stability (σ_J^2 ≤ Θ): {'PASS' if stable else 'FAIL'}")
if not stable:
    print("  → System flagged as UNSTABLE under the Omega Protocol.")
else:
    print("  → System flagged as STABLE under the Omega Protocol.")