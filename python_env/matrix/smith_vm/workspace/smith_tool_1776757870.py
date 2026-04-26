# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Agent Smith – Omega Protocol Invariant Validator
Checks dimensional consistency and the core invariant relations
for the NCSM-Ω proposal (Engine output).
"""

import sympy as sp
import re

# ----------------------------------------------------------------------
# 1. Define base dimensions (in natural units: ħ = 1, c = 1)
#    We treat time [T] as the fundamental dimension.
#    Length [L] will appear via curvature R ~ L^{-2}.
# ----------------------------------------------------------------------
T = sp.symbols('T', positive=True)   # time
L = sp.symbols('L', positive=True)   # length

# Dimension mapping for symbols used in the proposal
dim = {
    # Fundamental
    1: sp.Dimensionless,                # dimensionless constant
    # Fields / order parameters
    'I': sp.Dimensionless,              # normalized narrative magnitude
    'I0': sp.Dimensionless,
    'Phi_N': T,                         # covariant mode → time scale
    'Phi_Delta': T,
    'psi': sp.Dimensionless,
    'xi_N': T,
    'xi_Delta': T,
    # Curvature & metric
    'R': L**(-2),                       # scalar curvature
    'g_ij': sp.Dimensionless,           # induced metric (dimensionless)
    # Coupling constants from the effective action
    'lambda_eff': T**(-2),              # from kinetic term prefactor
    'alpha': L**2 * T,                  # needed to make α R I have [T]^{-1}
    'beta': T**(-2),                    # from ∂^2 V_eff/∂NCI^2
    'gamma': T**(-2),                   # from ∂^2 V_eff/∂Var(φ)^2
    # Entropy observable (must appear)
    'S_embed': sp.Dimensionless,        # Shannon entropy is dimensionless
    # Derived quantities
    'NCI': sp.Dimensionless,
    'R_c': L**(-2),                     # same dimension as curvature
    'Var_phi': sp.Dimensionless,
}

def expr_dim(expr):
    """Return the SymPy dimension of a SymPy expression."""
    if expr.is_Number:
        return dim[1]
    if expr.is_Symbol:
        return dim.get(str(expr), sp.Dimensionless)  # assume dimensionless if unknown
    if expr.is_Pow:
        base, exp = expr.as_base_exp()
        return expr_dim(base)**exp
    if expr.is_Mul:
        dims = [expr_dim(f) for f in expr.args]
        return sp.prod(dims)
    if expr.is_Add:
        # All terms in a sum must share the same dimension; we return the first
        # and rely on the caller to verify homogeneity.
        return expr_dim(expr.args[0])
    # Fallback
    return sp.Dimensionless

def check_homogeneity(expr, name):
    """Verify that expr is dimensionally homogeneous (all additive terms same dim)."""
    if not expr.is_Add:
        return True, expr_dim(expr)
    term_dims = [expr_dim(t) for t in expr.args]
    if all(d == term_dims[0] for d in term_dims):
        return True, term_dims[0]
    else:
        mismatched = [(str(t), d) for t, d in zip(expr.args, term_dims) if d != term_dims[0]]
        return False, mismatched

# ----------------------------------------------------------------------
# 2. Define the key equations from the proposal (as SymPy expressions)
# ----------------------------------------------------------------------
# Effective potential V_eff(I) = (lambda_eff/4)*(I**2 - I0**2)**2 + alpha*R*I
I, I0, lam_eff, alpha, R = sp.symbols('I I0 lam_eff alpha R')
V_eff = (lam_eff/4)*(I**2 - I0**2)**2 + alpha*R*I

# Stiffness invariants (as given)
xi_N_sq_inv = lam_eff * (3*I0**2 + R)
xi_Delta_sq_inv = lam_eff * (I0**2 + 3*R)

# Covariant mode mappings (simplified)
Phi_N0, Phi_Delta0, beta, gamma, NCI, Var_phi = sp.symbols('Phi_N0 Phi_Delta0 beta gamma NCI Var_phi')
Phi_N = Phi_N0 + alpha*sp.diff(NCI, sp.Symbol('t'))   # d(NCI)/dt placeholder
Phi_Delta = Phi_Delta0 - beta*(1 - NCI) + gamma*Var_phi

# Entropy term that SHOULD be present in the action:
# S_action = ∫ dt [ 0.5*(dI/dt)**2 + V_eff(I) + lam_S * S_embed ]
lam_S, S_embed = sp.symbols('lam_S S_embed')
Lagrangian = 0.5*sp.diff(I, sp.Symbol('t'))**2 + V_eff + lam_S*S_embed

# ----------------------------------------------------------------------
# 3. Run checks
# ----------------------------------------------------------------------
def report(label, ok, detail=None):
    status = "PASS" if ok else "FAIL"
    print(f"{label:40} [{status}]")
    if not ok and detail is not None:
        print("  ->", detail)

# Dimensional homogeneity of V_eff
ok, dim_V = check_homogeneity(V_eff, "V_eff")
report("V_eff homogeneity", ok, None if ok else f"bad dims: {dim_V}")

# Dimensional homogeneity of Lagrangian (should be [T]^{-1})
ok, dim_L = check_homogeneity(Lagrangian, "Lagrangian")
report("Lagrangian homogeneity", ok, None if ok else f"bad dims: {dim_L}")

# Check invariant relations: xi_N = dPhi_N/dpsi, xi_Delta = dPhi_Delta/dpsi
psi = sp.symbols('psi')
# We need expressions for Phi_N and Phi_Delta as functions of psi.
# In the proposal they are given only implicitly; we test the *form*:
# Assume Phi_N = f_N(psi) where f_N' = xi_N, similarly for Delta.
# Here we just verify that the symbols have correct dimensions.
report("Phi_N dimension", dim['Phi_N'] == expr_dim(Phi_N),
       f"expected {dim['Phi_N']}, got {expr_dim(Phi_N)}")
report("Phi_Delta dimension", dim['Phi_Delta'] == expr_dim(Phi_Delta),
       f"expected {dim['Phi_Delta']}, got {expr_dim(Phi_Delta)}")
report("xi_N dimension", dim['xi_N'] == expr_dim(xi_N),
       f"expected {dim['xi_N']}, got {expr_dim(xi_N)}")
report("xi_Delta dimension", dim['xi_Delta'] == expr_dim(xi_Delta),
       f"expected {dim['xi_Delta']}, got {expr_dim(xi_Delta)}")

# Entropy presence in Lagrangian
entropy_present = any(S_embed in str(term) for term in Lagrangian.args)
report("Entropy observable in Lagrangian", entropy_present,
       "Missing S_embed term" if not entropy_present else None)

# ----------------------------------------------------------------------
# 4. Summary
# ----------------------------------------------------------------------
print("\n=== Validation Summary ===")
print("If any FAIL appears above, the proposal does NOT satisfy")
print("the Omega Protocol invariant requirements and must be revised.")