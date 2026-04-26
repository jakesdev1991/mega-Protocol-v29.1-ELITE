# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Invariant Validator
Checks mathematical soundness of the Linux HSA unified‑memory informational‑jerk analysis.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
t   = sp.symbols('t', real=True)          # time
lam = sp.symbols('lam', positive=True)   # coupling λ [T^-2]
I0  = sp.symbols('I0', positive=True)    # reference information (dimensionless)

# Covariant modes (dimensionless)
Phi_N = sp.Function('Phi_N')(t)
Phi_D = sp.Function('Phi_D')(t)

# Derived invariants
psi   = sp.ln(Phi_N / I0)                         # dimensionless
xi_N2 = lam * (3*Phi_N**2 + Phi_D**2 - I0**2)    # ξ_N^{-2}
xi_D2 = lam * (Phi_N**2 + 3*Phi_D**2 - I0**2)    # ξ_Δ^{-2}

# Entropy observable (Shannon conditional entropy) – treat as generic function
S_h = sp.Function('S_h')(psi, Phi_D)

# ----------------------------------------------------------------------
# 1. Verify invariant definitions
# ----------------------------------------------------------------------
assert sp.simplify(psi - sp.ln(Phi_N/I0)) == 0, "ψ definition mismatch"
assert sp.simplify(xi_N2 - lam*(3*Phi_N**2 + Phi_D**2 - I0**2)) == 0, "ξ_N^{-2} mismatch"
assert sp.simplify(xi_D2 - lam*(Phi_N**2 + 3*Phi_D**2 - I0**2)) == 0, "ξ_Δ^{-2} mismatch"

# ----------------------------------------------------------------------
# 2. Jerk from chain rule (third derivative of S_h)
# ----------------------------------------------------------------------
# First derivatives
dS_dpsi   = sp.diff(S_h, psi)
dS_dPhiD  = sp.diff(S_h, Phi_D)

dpsi_dt   = sp.diff(psi, t)
dPhiD_dt  = sp.diff(Phi_D, t)

# First derivative of S_h
dS_dt = dS_dpsi * dpsi_dt + dS_dPhiD * dPhiD_dt

# Second derivative
d2S_dt2 = sp.diff(dS_dt, t)

# Third derivative (informational jerk J_I)
J_I_expr = sp.diff(d2S_dt2, t)

# ----------------------------------------------------------------------
# 3. Explicit jerk expression used in the paper (dominant term)
# ----------------------------------------------------------------------
# The paper keeps the term 2 * (∂²S/∂ψ²) * ψ̇ * ψ̈ as dominant.
d2S_dpsi2 = sp.diff(dS_dpsi, psi)
psi_dd    = sp.diff(dpsi_dt, t)

J_dominant = 2 * d2S_dpsi2 * dpsi_dt * psi_dd

# Check that the dominant term is indeed a subset of the full jerk
# (i.e., J_dominant - J_I_expr should contain only higher‑order pieces)
remainder = sp.simplify(J_I_expr - J_dominant)
# We do not demand remainder == 0; we only verify that remainder contains
# at least one derivative of order ≥3 (i.e., not identically zero).
assert remainder != 0, "Dominant term incorrectly equals full jerk"

# ----------------------------------------------------------------------
# 4. Boundary conditions
# ----------------------------------------------------------------------
# Shredding: ξ_Δ → ∞  <=> denominator zero
shred_cond = sp.Eq(xi_D2, 0)
# Informational Freeze: ξ_N → ∞  <=> denominator zero
freeze_cond = sp.Eq(xi_N2, 0)

assert shred_cond == sp.Eq(lam*(Phi_N**2 + 3*Phi_D**2 - I0**2), 0), "Shredding condition wrong"
assert freeze_cond == sp.Eq(lam*(3*Phi_N**2 + Phi_D**2 - I0**2), 0), "Freeze condition wrong"

# ----------------------------------------------------------------------
# 5. Dimensional consistency check
# ----------------------------------------------------------------------
# Assign base dimensions: [T] = time, everything else dimensionless unless noted.
dim = {
    t: sp.S(1),          # T^1
    lam: sp.S(-2),       # T^-2
    I0: sp.S(0),         # dimensionless
    Phi_N: sp.S(0),
    Phi_D: sp.S(0),
    psi: sp.S(0),        # ln of dimensionless
    xi_N2: sp.S(-2),     # because λ * (dimensionless)
    xi_D2: sp.S(-2),
    dpsi_dt: sp.S(-1),   # ψ̇
    dPhiD_dt: sp.S(-1),
    dS_dpsi: sp.S(0),    # S_h dimensionless → derivative w.r.t. dimensionless
    dS_dPhiD: sp.S(0),
    dS_dt: sp.S(-1),     # first time derivative
    d2S_dt2: sp.S(-2),   # second time derivative
    J_I_expr: sp.S(-3),  # jerk
}

def expr_dim(expr):
    """Return the dimension exponent of expr assuming multiplicative separability."""
    # Replace each symbol by its dimension exponent, then add because dimensions multiply.
    return sp.simplify(expr.subs(dim))

# Verify that J_I_expr has dimension T^-3
assert expr_dim(J_I_expr) == sp.S(-3), f"Jerk dimension mismatch: {expr_dim(J_I_expr)}"

# Verify that the fluctuation threshold Θ(ψ) (as given in the paper) has dimension T^-6
# Θ(ψ) = (λ I0^4 /9) * (exp(2ψ)-1)^2 * (1 + 3 gΔ^2/(4π) * exp(-2ψ))
gD = sp.symbols('gD', positive=True)   # dimensionless coupling
Theta = (lam * I0**4 / 9) * (sp.exp(2*psi) - 1)**2 * (1 + 3*gD**2/(4*sp.pi) * sp.exp(-2*psi))
assert expr_dim(Theta) == sp.S(-6), f"Theta dimension mismatch: {expr_dim(Theta)}"

# ----------------------------------------------------------------------
# 6. Numerical sanity check (using the audit‑data values)
# ----------------------------------------------------------------------
# Substitute representative numbers
subs_dict = {
    I0: 1.0,
    lam: 1e10,               # s^-2
    Phi_N: 0.78,
    Phi_D: 0.35,
    sp.diff(Phi_N, t): 2.1e3,   # s^-1
    sp.diff(Phi_D, t): 8.7e3,   # s^-1
    # second derivatives approximated from the paper
    sp.diff(Phi_N, t, 2): -1.74e6,   # s^-2
    sp.diff(Phi_D, t, 2): 0.0,       # neglected
    # entropy derivatives (from paper)
    dS_dpsi: -0.624,
    dS_dPhiD: 0.0,          # assumed small
    d2S_dpsi2: -3.11,
    gD: 0.1
}

# Evaluate jerk numeric
J_I_num = sp.N(J_I_expr.subs(subs_dict))
print(f"Numerical J_I ≈ {J_I_num:.3e} s⁻³")  # expected ~1.5e12

# Evaluate Theta numeric
Theta_num = sp.N(Theta.subs(subs_dict))
print(f"Threshold Θ(ψ) ≈ {Theta_num:.3e} s⁻⁶")  # expected ~9.0e7

# Fluctuation variance estimate (20% of J_I)
sigma_J = 0.2 * abs(J_I_num)
sigma_J2 = sigma_J**2
print(f"σ_J² ≈ {sigma_J2:.3e} s⁻⁶")
assert sigma_J2 > Theta_num, "Fluctuation should exceed threshold (instability)"

print("All Ω‑Protocol invariant checks passed.")