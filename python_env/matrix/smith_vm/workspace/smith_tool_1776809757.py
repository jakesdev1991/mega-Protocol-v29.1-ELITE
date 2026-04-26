# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith – Validation of the One‑Loop Anisotropic Vacuum Polarization
Omega Protocol invariants: Φ_N, Φ_Δ, J^μ (entropy gauge)
"""

import sympy as sp
import itertools

# ----------------------------------------------------------------------
# 1. Symbols
# ----------------------------------------------------------------------
# Lorentz indices (0..3)
mu, nu, rho, sigma = sp.symbols('mu nu rho sigma', integer=True)
# Momentum components
k0, k1, k2, k3, p0, p1, p2, p3 = sp.symbols('k0 k1 k2 k3 p0 p1 p2 p3', real=True)
# Lattice deformation
PhiDelta = sp.symbols('PhiDelta', real=True)
# Mass
m = sp.symbols('m', real=True, nonnegative=True)
# Pauli matrices (we use Dirac gamma in Euclidean rep: {γ_μ,γ_ν}=2δ_μν)
# For trace we only need the algebra: Tr[γ_μ γ_ν] = 4 δ_μν, Tr[γ_μ γ_ν γ_ρ γ_σ] = 4(δ_μνδ_ρσ - δ_μρδ_νσ + δ_μσδ_νρ)
# We'll implement trace via sympy with replacement rules.

# ----------------------------------------------------------------------
# 2. Helper: replace products of gammas with traces
# ----------------------------------------------------------------------
def gamma_trace(expr):
    """Replace gamma products by their trace using Euclidean Clifford algebra."""
    # First, expand products
    expr = sp.expand(expr)
    # Replace γ_μ γ_ν -> 4 δ_μν
    expr = expr.replace(
        lambda x: x.is_Power and x.base.has(sp.Symbol) and x.exp == 2,
        lambda x: 4  # γ_μ γ_μ = 4 (no sum)
    )
    # Replace γ_μ γ_ν γ_ρ γ_σ -> 4(δ_μνδ_ρσ - δ_μρδ_νσ + δ_μσδ_νρ)
    # We'll do it via pattern matching on ordered products of four distinct gammas.
    # For simplicity, we use sympy's tensor module (if available) but here we implement manually.
    # Since we only need traces up to four gammas, we can brute‑force.
    # We'll treat any product of gammas as a list of indices.
    def replace_product(expr):
        if expr.is_Mul:
            # extract gamma symbols
            gammas = [arg for arg in expr.args if arg.has(sp.Symbol) and str(arg).startswith('γ')]
            if len(gammas) == 4:
                idxs = [int(str(g)[1]) for g in gammas]  # assume γ0,γ1,γ2,γ3 naming
                # compute trace
                d = sp.KroneckerDelta
                trace = 4*(d(idxs[0], idxs[1])*d(idxs[2], idxs[3]) -
                           d(idxs[0], idxs[2])*d(idxs[1], idxs[3]) +
                           d(idxs[0], idxs[3])*d(idxs[1], idxs[2]))
                # remove the gammas and replace with trace
                remaining = [arg for arg in expr.args if not (arg.has(sp.Symbol) and str(arg).startswith('γ'))]
                return sp.Mul(*remaining, trace, evaluate=False)
        return expr
    expr = sp.simplify(expr.replace(sp.Mul, replace_product))
    return expr

# ----------------------------------------------------------------------
# 3. Define gamma symbols (γ0..γ3)
# ----------------------------------------------------------------------
gammas = [sp.Symbol(f'γ{i}') for i in range(4)]

# ----------------------------------------------------------------------
# 4. Fermion propagator S_F(k) to O(ΦΔ)
# ----------------------------------------------------------------------
# S0 = (i γ·sin k + m)^{-1}  ; we work with numerator only because trace uses S_F S_F
# For trace we need S_F(k) γ_μ S_F(k-p) γ_ν .
# Use identity: S_F = (iγ·sin k + m)^{-1} => S_F γ_μ S_F = (iγ·sin k + m)^{-1} γ_μ (iγ·sin k + m)^{-1}
# To O(ΦΔ) we expand sin k_i = k_i (continuum) for trace; lattice effects appear in angular integrals later.
# We'll keep sin symbols.
sin = sp.sin
sink = [sin(k0), sin(k1), sin(k2), sin(k3)]
sin(k-p) = [sin(k0-p0), sin(k1-p1), sin(k2-p2), sin(k3-p3)]

# Propagator numerator (inverse denominator will cancel in trace up to O(ΦΔ^2))
# S_F ≈ (iγ·sin k + m)^{-1} = ( -iγ·sin k + m ) / (k^2 + m^2)  (Euclidean)
den_k = sum(si**2 for si in sink) + m**2
den_kp = sum((sin(ki-pi))**2 for ki, pi in zip(sink, [p0,p1,p2,p3])) + m**2

S0_num = -sp.I*sum(gammas[i]*sink[i] for i in range(4)) + m   # -iγ·sin k + m
S0p_num = -sp.I*sum(gammas[i]*sin(ki-pi) for i,ki,pi in zip(range(4), sink, [p0,p1,p2,p3])) + m

# Anisotropic correction to propagator: δS = -S0 * (ΦΔ/2) i γ_z sin k_z * S0
gamma_z = gammas[3]
sin_kz = sink[3]
deltaS_num = -S0_num * (PhiDelta/2)*sp.I*gamma_z*sin_kz * S0_num   # we keep one S0 on each side

# Full propagator numerator to O(ΦΔ): S_num = S0_num + deltaS_num
S_num = sp.simplify(S0_num + deltaS_num)
S0p_num = sp.simplify(S0p_num)   # no ΦΔ in second propagator (we can add similarly but trace linear in ΦΔ needs only one insertion)

# ----------------------------------------------------------------------
# 5. Build trace: Tr[ γ_μ S(k) γ_ν S(k-p) ]
# ----------------------------------------------------------------------
def build_trace(mu_idx, nu_idx):
    gamma_mu = gammas[mu_idx]
    gamma_nu = gammas[nu_idx]
    # S(k) numerator * gamma_mu * S(k-p) numerator * gamma_nu
    expr = S_num * gamma_mu * S0p_num * gamma_nu
    # Take trace (replace gamma products)
    tr = gamma_trace(expr)
    # Denominator factor (scalar)
    tr = sp.simplify(tr / (den_k * den_kp))
    return tr

# ----------------------------------------------------------------------
# 6. Extract ΦΔ-linear piece
# ----------------------------------------------------------------------
def phi_delta_linear(expr):
    # series expand in PhiDelta and keep O(PhiDelta)
    series = sp.series(expr, PhiDelta, 0, 2).removeO()
    # keep term proportional to PhiDelta
    coeff = sp.Poly(series, PhiDelta).coeff_monomial(PhiDelta)
    return sp.simplify(coeff)

# ----------------------------------------------------------------------
# 7. Check angular structure: does the O(ΦΔ) term contain sin_z k sin_z(k-p) ?
# ----------------------------------------------------------------------
def contains_sin_z_sin_z(expr):
    # Look for product sin(k3)*sin(k3-p3) (or any combination with gamma_z)
    return expr.has(sin(k3)*sin(k3-p3)) or expr.has(sin(k3)*sin(k3-p3))

# ----------------------------------------------------------------------
# 8. Validate: correct trace vs. premature delta contraction
# ----------------------------------------------------------------------
# Correct trace (as above)
tr_correct = build_trace(0, 3)   # example μ=0, ν=z
linear_correct = phi_delta_linear(tr_correct)

# Premature contraction: replace δ_{μz}δ_{νz} before trace
# Simulate by setting gamma_mu = gamma_nu = gamma_z and then removing angular dependence
# Actually the error was: they replaced sin_mu k sin_nu(k-p) -> δ_{μz}δ_{νz} sin k·sin(k-p)
# We'll mimic that by forcing the numerator to be proportional to δ_{μz}δ_{νz} (i.e., only gamma_z gamma_z)
gamma_z = gammas[3]
tr_wrong = gamma_trace(S_num * gamma_z * S0p_num * gamma_z) / (den_k * den_kp)
linear_wrong = phi_delta_linear(tr_wrong)

print("Linear O(ΦΔ) term (correct trace):")
sp.pprint(linear_correct)
print("\nDoes it contain sin_z k sin_z(k-p)?", contains_sin_z_sin_z(linear_correct))
print("\nLinear O(ΦΔ) term (wrong trace – premature δ contraction):")
sp.pprint(linear_wrong)
print("\nDoes it contain sin_z k sin_z(k-p)?", contains_sin_z_sin_z(linear_wrong))

# ----------------------------------------------------------------------
# 9. Consistency check: the wrong version should reduce to a pure mass term (no angular dependence)
# ----------------------------------------------------------------------
# Simplify wrong expression and see if it depends on k_i or p_i only through k^2, p^2, k·p
def depends_only_on_invariants(expr):
    # Replace all sin(k_i) and sin(k_i-p_i) with symbols and see if any remain
    subs_dict = {sin(k0):'a0', sin(k1):'a1', sin(k2):'a2', sin(k3):'a3',
                 sin(k0-p0):'b0', sin(k1-p1):'b1', sin(k2-p2):'b2', sin(k3-p3):'b3'}
    expr_sub = expr.subs(subs_dict)
    # If after substitution any of a0..a3,b0..b3 remain, then angular dependence persists
    return not any(expr_sub.has(sym) for sym in ['a0','a1','a2','a3','b0','b1','b2','b3'])

print("\nWrong term depends only on invariants (scalar)?", depends_only_on_invariants(linear_wrong))
print("Correct term depends only on invariants (scalar)?", depends_only_on_invariants(linear_correct))