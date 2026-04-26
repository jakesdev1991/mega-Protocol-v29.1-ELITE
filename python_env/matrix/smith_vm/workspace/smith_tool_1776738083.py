# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETO‑Ω Mathematical & Invariant Compliance Checker
-------------------------------------------------
This script validates the refined Emergent Topological Omega (ETO‑Ω) proposal
against the Omega Protocol invariants and basic dimensional consistency.
It uses SymPy for symbolic manipulation and a custom dimension system.
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Dimension system (M, L, T).  Energy E = M*L^2/T^2.
#    We work in natural units where action S is dimensionless.
# ----------------------------------------------------------------------
M, L, T = sp.symbols('M L T', positive=True)
def dim(exp):
    """Return the dimension of a SymPy expression as a tuple (M, L, T)."""
    # Replace each base symbol with its exponent vector.
    # We assume that any Symbol not in {M,L,T} is dimensionless.
    subs = {M: (1,0,0), L: (0,1,0), T: (0,0,1)}
    # Recursively compute dimension via multiplication/addition rules.
    def _dim(e):
        if e.is_Number:
            return (0,0,0)
        if e.is_Symbol:
            return subs.get(e, (0,0,0))
        if e.is_Mul:
            dims = tuple(sum(x) for x in zip(*[_dim(a) for a in e.args]))
            return dims
        if e.is_Add:
            # All terms must have same dimension; we return the first.
            dims = _dim(e.args[0])
            for a in e.args[1:]:
                if _dim(a) != dims:
                    raise ValueError(f"Addition of mismatched dimensions in {e}")
            return dims
        if e.is_Pow:
            base, exp = e.args
            if not exp.is_Number:
                raise ValueError(f"Non‑constant power in {e}")
            bdim = _dim(base)
            return tuple(exp * d for d in bdim)
        # Fallback: treat as dimensionless
        return (0,0,0)
    return _dim(exp)

# ----------------------------------------------------------------------
# 2. Assign dimensions to the fundamental quantities.
# ----------------------------------------------------------------------
# Spatial dimension d (kept symbolic)
d = sp.symbols('d', integer=True, positive=True)

# Field ϕ: from the kinetic term (∂ϕ)^2 in the action.
# Action S = ∫ d^d x [ 1/2 (∂ϕ)^2 + ... ] must be dimensionless.
# [∂ϕ] = [ϕ] * L^{-1}
# [(∂ϕ)^2] = [ϕ]^2 * L^{-2}
# Integration adds L^d → total dimension = [ϕ]^2 * L^{d-2}
# Set this to 1 (dimensionless) → [ϕ] = L^{-(d-2)/2}
phi_dim = (0, -(d-2)/2, 0)   # (M, L, T)

# Stiffness invariants ξ_N, ξ_Δ: appear as lengths (correlation lengths)
xi_N_dim = (0, 1, 0)   # Length
xi_Delta_dim = (0, 1, 0)

# ψ = ln(Φ_N / I_0) → dimensionless
psi_dim = (0,0,0)

# Covariant modes Φ_N, Φ_Δ: logical operators → dimensionless
Phi_N_dim = (0,0,0)
Phi_Delta_dim = (0,0,0)

# Gap Δ: energy dimension
# Energy E = M L^2 T^{-2}
Delta_dim = (1,2,-2)

# Couplings J_{ij}, K_{ij} in H_eff: must have energy dimension
J_dim = Delta_dim
K_dim = Delta_dim

# Order parameter O = ⟨ϕ(x)ϕ(y)⟩_{|x-y|→∞}
# Two-point function has dimension [ϕ]^2
O_dim = tuple(2*a for a in phi_dim)   # = L^{-(d-2)}

# Topological entanglement entropy S_h: dimensionless (entropy in natural units)
S_h_dim = (0,0,0)

# ----------------------------------------------------------------------
# 3. Define symbolic expressions from the proposal.
# ----------------------------------------------------------------------
# Basic symbols
xi0 = sp.symbols('xi0', positive=True)   # reference length
Delta0 = sp.symbols('Delta0', positive=True)   # reference energy
g_N, g_D = sp.symbols('g_N g_D', positive=True)   # dimensionless couplings

# Stiffness ratio (dimensionless)
r_N = xi_N / xi0
r_D = xi_Delta / xi0

# Example gap function: monotonic increasing in r_N, r_D
# Choose a simple form: f = sqrt(r_N * r_D)  (can be replaced)
f = sp.sqrt(r_N * r_D)
Delta_expr = Delta0 * f   # Δ = Δ0 * sqrt( (ξ_N/ξ0)*(ξ_Δ/ξ0) )

# Couplings J, K: take them proportional to Δ (common in effective models)
J_expr = g_N * Delta_expr
K_expr = g_D * Delta_expr

# Effective Hamiltonian density (per bond) – we check dimension of J σσ
# σ are dimensionless Pauli‑like operators
H_bond_dim = dim(J_expr)   # should equal Delta_dim

# Equations of motion for the logical operators:
Gamma0 = sp.symbols('Gamma0', positive=True)
kB = sp.symbols('kB', positive=True)   # Boltzmann constant (energy/T)
T_sym = sp.symbols('T', positive=True) # temperature
Gamma_N = Gamma0 * sp.exp(-Delta_expr/(kB*T_sym))
Gamma_D = Gamma0 * sp.exp(-Delta_expr/(kB*T_sym))

# dΦ_N/dt = - Γ_N * ∂L_Ω/∂Φ_N
# We treat ∂L_Ω/∂Φ_N as dimensionless (L_Ω is a scalar Lagrangian density)
# Hence RHS dimension = [Gamma_N] = [1/time] because exponent is dimensionless.
# So we need to check that [Gamma_N] = T^{-1}
Gamma_N_dim = dim(Gamma_N)   # should be (0,0,-1)

# Order parameter O: we propose O ~ exp(-|x-y|/ξ) → at large separation O→0
# In topological phase O becomes non‑zero; we treat O as dimensionless.
# For consistency we verify that the exponent is dimensionless:
expo_O_dim = dim( (sp.symbols('x') - sp.symbols('y')) / xi_N )   # should be (0,0,0)
# Actually we just check that xi_N has length dimension, so ratio is dimensionless.

# ----------------------------------------------------------------------
# 4. Perform checks and report.
# ----------------------------------------------------------------------
def check_dim(expr, expected_dim, name):
    """Check that expr has the expected dimension."""
    actual = dim(expr)
    if actual == expected_dim:
        print(f"[PASS] {name}: dimension {actual} matches expected {expected_dim}")
    else:
        print(f"[FAIL] {name}: dimension {actual} != expected {expected_dim}")

print("=== Dimensional Consistency Checks ===")
check_dim(J_expr, J_dim, "Coupling J_{ij}")
check_dim(K_expr, K_dim, "Coupling K_{ij}")
check_dim(H_bond_dim, Delta_dim, "Effective Hamiltonian bond term")
check_dim(Gamma_N_dim, (0,0,-1), "Gamma_N (rate)")
check_dim(Gamma_D_dim, (0,0,-1), "Gamma_D (rate)")
check_dim(sp.exp(-Delta_expr/(kB*T_sym)), (0,0,0), "Exponential factor in Gamma")
check_dim(sp.sqrt(r_N * r_D), (0,0,0), "Gap function f (dimensionless)")
check_dim(Delta_expr, Delta_dim, "Energy gap Δ")
check_dim(sp.log(Phi_N/sp.symbols('I0')), (0,0,0), "ψ = ln(Φ_N/I0)")
check_dim(sp.sqrt(r_N * r_D), (0,0,0), "Stiffness ratio combination")
check_dim(sp.exp(-Delta_expr/(kB*T_sym)), (0,0,0), "Exponential in Γ")
# Order parameter dimensionless check
check_dim(sp.exp(-sp.symbols('r')/xi_N), (0,0,0), "Order parameter exponential (dimensionless)")

print("\n=== Invariant Usage Checks ===")
# Verify that Φ_N and Φ_Δ appear in the equations of motion
expr_dPhiN = -Gamma_N * sp.symbols('dL_dPhiN')   # placeholder for ∂L_Ω/∂Φ_N
expr_dPhiD = -Gamma_D * sp.symbols('dL_dPhiDelta')
# We just ensure the symbols are present
if Phi_N in expr_dPhiN.atoms(sp.Symbol):
    print("[PASS] Φ_N appears in dΦ_N/dt expression")
else:
    print("[FAIL] Φ_N missing from dΦ_N/dt expression")
if Phi_Delta in expr_dPhiD.atoms(sp.Symbol):
    print("[PASS] Φ_Δ appears in dΦ_Δ/dt expression")
else:
    print("[FAIL] Φ_Δ missing from dΦ_Δ/dt expression")

# Verify that ξ_N, ξ_Δ appear in the gap and couplings
if xi_N in Delta_expr.atoms(sp.Symbol) and xi_Delta in Delta_expr.atoms(sp.Symbol):
    print("[PASS] ξ_N and ξ_Δ appear in the gap Δ")
else:
    print("[FAIL] ξ_N or ξ_Δ missing from gap")
if xi_N in J_expr.atoms(sp.Symbol) and xi_Delta in J_expr.atoms(sp.Symbol):
    print("[PASS] ξ_N and ξ_Δ appear in coupling J")
else:
    print("[FAIL] ξ_N or ξ_Δ missing from coupling J")

print("\n=== Boundary Condition Checks ===")
# Shredding: Δ → 0 when ξ_N or ξ_Δ → 0 (or when f → 0)
limit_shred = sp.limit(Delta_expr, xi_N, 0, dir='+')
print(f"Limit Δ as ξ_N → 0+: {limit_shred} (should be 0)")
limit_shred2 = sp.limit(Delta_expr, xi_Delta, 0, dir='+')
print(f"Limit Δ as ξ_Δ → 0+: {limit_shred2} (should be 0)")

# Informational Freeze: ξ_N, ξ_Δ → 0 leads to trivial phase (gap still →0)
# In the proposal, freeze corresponds to ξ_N, ξ_Δ → 0 *and* the system becoming
# a gapped trivial phase; we note that our simple f → 0 gives gapless,
# so we flag that a more sophisticated f (e.g., f = 1 - exp(-ξ/ξ0)) would be needed.
print("\nNote: The simple gap function f = sqrt(r_N r_D) goes to zero when ξ→0,")
print("which matches a gapless trivial limit. For a gapped trivial phase,")
print("one would need a gap function that approaches a non‑zero constant")
print("as ξ→0 (e.g., f = 1 - exp(-r_N) * exp(-r_D)).")

print("\n=== Summary ===")
print("If all checks above read [PASS], the proposal is dimensionally")
print("consistent and makes active use of the Omega Protocol invariants.")
print("Any [FAIL] indicates a point that needs revision before formal")
print("submission to the Omega Protocol audit.")