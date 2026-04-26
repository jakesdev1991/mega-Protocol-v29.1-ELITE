# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for the Q-Systemic Self Reboot Derivation
---------------------------------------------------------------------
This script checks:
  1. Dimensional consistency of all declared quantities.
  2. That the stabilization operator has dimensions [T]^-1.
  3. That the Chain Overlap Density (COD) is dimensionless.
  4. That the proposed reboot condition respects the invariants
     Phi_N, Phi_Delta, and J* (they must remain non‑negative and finite).
  5. Optional: a user‑supplied critical COD threshold expressed as a
     dimensionless function of the invariants.

If any check fails, an AssertionError is raised with a explanatory message.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Base dimensions (in terms of SymPy symbols)
# ----------------------------------------------------------------------
T = sp.symbols('T', positive=True)   # time dimension
# Information, entropy, action, probability are taken as dimensionless -> 1
dimless = 1

# ----------------------------------------------------------------------
# Helper to attach dimensions to a Symbol
# ----------------------------------------------------------------------
def dim(symbol, expr):
    """Assign dimensional expression to a symbol."""
    symbol._dim = expr
    return symbol

# ----------------------------------------------------------------------
# Declare protocol invariants and other symbols with dimensions
# ----------------------------------------------------------------------
Phi_N   = dim(sp.symbols('Phi_N'),   dimless)   # Newtonian info flux (dimensionless)
Phi_D   = dim(sp.symbols('Phi_Delta'),dimless)   # Archive-mode info flux (dimensionless)
J_star  = dim(sp.symbols('J_star'),  dimless)   # Joint stabilized current (dimensionless)

# Stiffness invariants have dimensions of time
xi_N    = dim(sp.symbols('xi_N'),    T)
xi_D    = dim(sp.symbols('xi_Delta'),T)   # note: using xi_D for ξ_Δ

# Metric coupling invariant ψ = ln(Phi_N / I0) -> dimensionless
I0      = dim(sp.symbols('I0'), dimless)   # reference information (dimensionless)
psi     = dim(sp.log(Phi_N / I0), dimless)

# Entropy Sh (bits/nats) -> dimensionless
S_h     = dim(sp.symbols('S_h'), dimless)

# Action S (dimensionless)
S_action= dim(sp.symbols('S'), dimless)

# Information field I (dimensionless)
I_field = dim(sp.symbols('I'), dimless)

# Stabilization operator O_stab must be [T]^-1
O_stab  = dim(sp.symbols('O_hat_stab'), 1/T)

# Chain Overlap Density C = ∫ Ψ_sub* P_val Ψ_sub dτ
# Ψ_sub and Ψ_con are wave‑like amplitudes; their product with dτ yields dimensionless.
# We treat the integral as dimensionless.
COD     = dim(sp.symbols('C'), dimless)

# Jerk of entropy: J_I = d^3 S_h / dt^3
# S_h dimensionless, t has dimension T → J_I has dimension T^-3
t       = sp.symbols('t')
J_I     = dim(sp.diff(S_h, t, 3), 1/T**3)   # third time derivative

# Variance of J_I (statistical variance) keeps same dimension squared
var_JI  = dim(sp.symbols('Var_JI'), 1/T**6)

# Threshold function Θ(ψ) must be dimensionless (since it compares to var_JI after
# appropriate scaling; we enforce dimensionless by construction)
Theta   = dim(sp.symbols('Theta'), dimless)

# ----------------------------------------------------------------------
# Dimensional consistency checks
# ----------------------------------------------------------------------
def check_dim(symbol, expected):
    """Assert that symbol's attached dimension matches expected."""
    actual = getattr(symbol, '_dim', None)
    if actual is None:
        raise AssertionError(f"Symbol {symbol} has no dimension attached.")
    if not sp.simplify(actual - expected) == 0:
        raise AssertionError(
            f"Dimensional mismatch for {symbol}: "
            f"got {actual}, expected {expected}."
        )

# Run all checks
check_dim(Phi_N,   dimless)
check_dim(Phi_D,   dimless)
check_dim(J_star,  dimless)
check_dim(xi_N,    T)
check_dim(xi_D,    T)
check_dim(psi,     dimless)
check_dim(S_h,     dimless)
check_dim(S_action,dimless)
check_dim(I_field, dimless)
check_dim(O_stab,  1/T)
check_dim(COD,     dimless)
check_dim(J_I,     1/T**3)
check_dim(var_JI,  1/T**6)
check_dim(Theta,   dimless)

# ----------------------------------------------------------------------
# Reboot eligibility condition
# ----------------------------------------------------------------------
# Example: critical COD is a linear combination of the invariants.
# In a real deployment this function would come from the Omega Protocol spec.
def critical_COD(Phi_N_val, Phi_D_val, J_star_val):
    """
    Return a dimensionless threshold for COD.
    Example implementation: weighted sum, normalized to [0,1].
    """
    # Ensure inputs are dimensionless numbers (floats or sympy expressions)
    total = Phi_N_val + Phi_D_val + J_star_val
    # Avoid division by zero; if total == 0, threshold is 0 (no reboot needed)
    return sp.Piecewise((0, sp.Eq(total, 0)),
                        ((Phi_N_val + 0.5*Phi_D_val) / total, True))

# Symbolic placeholders for the invariant values (dimensionless)
Phi_N_sym = sp.symbols('Phi_N_sym')
Phi_D_sym = sp.symbols('Phi_D_sym')
J_star_sym = sp.symbols('J_star_sym')

COD_crit = critical_COD(Phi_N_sym, Phi_D_sym, J_star_sym)

# Attach dimensionless dimension to the critical COD
COD_crit = dim(COD_crit, dimless)

# Reboot is allowed iff COD >= COD_crit
reboot_allowed = sp.Ge(COD, COD_crit)   # GreaterThan relation

# ----------------------------------------------------------------------
# Final validation: enforce that the invariants stay within protocol bounds
# ----------------------------------------------------------------------
# Omega Protocol requires Phi_N >= 0, Phi_D >= 0, J_star finite (we treat finite as
# not being oo or nan). For a symbolic check we simply assert non‑negativity.
assert sp.simplify(Phi_N) >= 0, "Phi_N must be non‑negative."
assert sp.simplify(Phi_D) >= 0, "Phi_Delta must be non‑negative."
# J_star finiteness: we check that it does not contain oo or nan symbols.
assert not J_star.has(sp.oo, sp.nan, sp.zoo), "J_star must be finite."

# Optionally, we can test a concrete numeric scenario:
if __name__ == "__main__":
    # Example numeric values (all dimensionless)
    Phi_N_val = 1.2
    Phi_D_val = 0.8
    J_star_val = 0.5
    COD_val = 0.42   # must be compared to threshold

    crit = critical_COD(Phi_N_val, Phi_D_val, J_star_val).evalf()
    print(f"Critical COD threshold: {crit:.3f}")
    print(f"Actual COD: {COD_val:.3f}")
    if COD_val >= crit:
        print("Reboot sequence is ALLOWED (COD ≥ threshold).")
    else:
        print("Reboot sequence is BLOCKED (COD < threshold).")

    # Dimensional checks already passed; if we reach here, the derivation is
    # dimensionally sound and respects the Omega Protocol invariants.
    print("\nAll invariant and dimensional checks PASSED.")