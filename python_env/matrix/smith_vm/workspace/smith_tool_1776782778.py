# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Dimensional‑consistency checker for the TEMPEST‑Ω refinement.
Base dimensions: [M] mass, [L] length, [T] time.
We treat the action S as having dimensions of [M L^2 T^-1] (natural units).
"""

import sympy as sp

# Base dimensions
M, L, T = sp.symbols('M L T', positive=True)

def dim(expr):
    """Return the dimension of a SymPy expression as a product of powers of M,L,T."""
    # Replace symbols with their dimensional placeholders
    subs_dict = {
        # Fundamental constants (set to dimensionless for simplicity)
        sp.Symbol('hbar'): 1,
        sp.Symbol('c'): 1,
        # We will assign dimensions to our variables later
    }
    # Substitute known dimensions
    expr_subs = expr.subs(subs_dict)
    # If the expression is a Symbol, look up its assigned dimension
    if isinstance(expr_subs, sp.Symbol):
        return dim_map.get(expr_subs, sp.Symbol('1'))  # default dimensionless
    # If it's a number
    if expr_subs.is_number:
        return 1
    # Recurse for products/powers
    if expr_subs.is_Mul:
        d = 1
        for factor in expr_subs.args:
            d *= dim(factor)
        return d
    if expr_subs.is_Pow:
        base, exp = expr_subs.args
        return dim(base) ** exp
    # Addition/subtraction: all terms must share same dimension
    if expr_subs.is_Add:
        terms = [dim(t) for t in expr_subs.args]
        # Check equality
        first = terms[0]
        for d in terms[1:]:
            if d != first:
                raise ValueError(f"Dimension mismatch in addition: {expr_subs}")
        return first
    # Fallback: treat as dimensionless
    return 1

# ----------------------------------------------------------------------
# Assign dimensions to the symbols used in the proposal
dim_map = {}

# Scalar stress field φ (claimed dimensionless)
phi = sp.Symbol('phi')
dim_map[phi] = 1

# Derivative ∂_μ has dimension [L]^-1
partial = sp.Symbol('partial')
dim_map[partial] = 1/L

# Effective mass m_eff (inverse time if φ dimensionless)
m_eff = sp.Symbol('m_eff')
dim_map[m_eff] = 1/T

# Reference mass m0 (choose to have same dimension as m_eff for RG invariance)
m0 = sp.Symbol('m0')
dim_map[m0] = 1/T

# Correlation lengths ξ_N, ξ_Δ
xi_N = sp.Symbol('xi_N')
xi_Delta = sp.Symbol('xi_Delta')
dim_map[xi_N] = T
dim_map[xi_Delta] = T

# Credential criticality C_i (dimensionless)
C = sp.Symbol('C')
dim_map[C] = 1

# Decay constant λ (inverse time)
lam = sp.Symbol('lambda')
dim_map[lam] = 1/T

# Time differences
t = sp.Symbol('t')
ti = sp.Symbol('t_i')
delta_t = sp.Symbol('Delta_t')  # = Δt_{f,e}
dim_map[t] = T
dim_map[ti] = T
dim_map[delta_t] = T

# Synchrony measure sync(t_i) (dimensionless)
sync = sp.Symbol('sync')
dim_map[sync] = 1

# Coefficients α, β, γ, η1, η2, η3 (unknown dimensions – we will solve for them)
alpha = sp.Symbol('alpha')
beta  = sp.Symbol('beta')
gamma = sp.Symbol('gamma')
eta1  = sp.Symbol('eta1')
eta2  = sp.Symbol('eta2')
eta3  = sp.Symbol('eta3')

# Temporal Stress Index TSI (as defined in the proposal)
TSI = alpha*C*sp.exp(-lam*sp.Abs(t - ti)) + beta/delta_t + gamma*sync
# Note: sp.Abs is treated as dimensionless if its argument is dimensionless;
# we will handle it by assuming the argument's dimension is checked inside.

# Dimensions of each term in TSI
dim_TSI_term1 = dim(alpha) * dim(C) * dim(sp.exp(-lam*(t - ti)))  # exp of dimensionless -> 1
dim_TSI_term2 = dim(beta) / dim(delta_t)
dim_TSI_term3 = dim(gamma) * dim(sync)

print("--- Dimensional analysis of TSI terms ---")
print("Term1 dimension:", dim_TSI_term1)
print("Term2 dimension:", dim_TSI_term2)
print("Term3 dimension:", dim_TSI_term3)

# For TSI to be dimensionless (as used in constraints TSI≤4), all three must match
constraints = []
if dim_TSI_term1 != dim_TSI_term2:
    constraints.append("Term1 ≠ Term2")
if dim_TSI_term1 != dim_TSI_term3:
    constraints.append("Term1 ≠ Term3")
if constraints:
    print("FAIL: TSI terms have mismatched dimensions:", constraints)
else:
    print("PASS: TSI terms can be made dimensionless if coefficients carry appropriate dimensions.")

# ----------------------------------------------------------------------
# Check the Φ_N^{(temp)} equation:
# Φ_N^{(temp)} = Φ_N^{(0)} + η1 * TSI(t-τ1) - η2 * TSI(t-τ2)^2
Phi_N0 = sp.Symbol('Phi_N0')
tau1 = sp.Symbol('tau1')
tau2 = sp.Symbol('tau2')
# Assume Φ_N and Φ_N0 are dimensionless (as used in constraints)
Phi_N = sp.Symbol('Phi_N')
dim_map[Phi_N0] = 1
dim_map[Phi_N] = 1
dim_map[tau1] = T
dim_map[tau2] = T

# TSI evaluated at shifted times has same dimension as TSI
TSI_shift1 = TSI.subs({t: t - tau1})
TSI_shift2 = TSI.subs({t: t - tau2})
dim_TSI = dim(TSI)  # whatever we found above

Phi_N_expr = Phi_N0 + eta1*TSI_shift1 - eta2*TSI_shift2**2
dim_Phi_N_expr = dim(Phi_N0) + dim(eta1)*dim_TSI - dim(eta2)*dim_TSI**2  # addition forces equality

print("\n--- Φ_N^{(temp)} dimensional check ---")
print("Dimension of Φ_N0:", dim(Phi_N0))
print("Dimension of η1*TSI:", dim(eta1)*dim_TSI)
print("Dimension of η2*TSI^2:", dim(eta2)*dim_TSI**2)

# For the sum to be dimensionless, each term must be dimensionless
if dim(Phi_N0) != 1:
    print("FAIL: Φ_N0 not dimensionless")
if dim(eta1)*dim_TSI != 1:
    print("FAIL: η1*TSI not dimensionless → η1 must have dimension", 1/dim_TSI)
if dim(eta2)*dim_TSI**2 != 1:
    print("FAIL: η2*TSI^2 not dimensionless → η2 must have dimension", 1/(dim_TSI**2))
else:
    print("PASS: Φ_N^{(temp)} can be dimensionless with appropriate η1, η2.")

# ----------------------------------------------------------------------
# Check the invariant ψ = ln(m_eff/m0)
psi = sp.Symbol('psi')
psi_expr = sp.log(m_eff / m0)
# log argument must be dimensionless
arg_psi = m_eff / m0
dim_arg = dim(arg_psi)
print("\n--- ψ dimensional check ---")
print("Dimension of m_eff/m0:", dim_arg)
if dim_arg != 1:
    print("FAIL: Argument of ln is not dimensionless → ψ not well‑defined")
else:
    print("PASS: ψ is dimensionless (as required).")
    # RG invariance would require m_eff ∝ μ (renormalization scale); not shown.

# ----------------------------------------------------------------------
# Entropy gauge 𝒜_μ = ∂_μ S_h, with S_h = c ln(ξ/ξ0)
S_h = sp.Symbol('S_h')
c = sp.Symbol('c')
xi0 = sp.Symbol('xi0')
# Assume c dimensionless, ξ0 same dimension as ξ
dim_map[c] = 1
dim_map[xi0] = T
S_h_expr = c * sp.log(xi_N / xi0)
dim_S_h = dim(S_h_expr)
print("\n--- Entropy S_h dimension ---")
print("Dimension of S_h:", dim_S_h)
if dim_S_h != 1:
    print("FAIL: S_h not dimensionless → gauge field will have wrong dimension")
else:
    print("PASS: S_h dimensionless.")
# Gauge field A_μ = ∂_μ S_h
A_mu = partial * S_h
dim_A = dim(A_mu)
print("Dimension of 𝒜_μ:", dim_A)
# For minimal coupling to action S ~ ∫ d^4x ( ... + A_μ J^μ ), A_μ must have [L]^-1
if dim_A != 1/L:
    print(f"FAIL: Gauge field dimension {dim_A} does not match required [L]^-1")
else:
    print("PASS: Gauge field has correct dimension.")

# ----------------------------------------------------------------------
# Action S (schematic)
# S = ∫ d^4x [ 1/2 (∂φ)^2 - V(phi) ]  ; V ~ 1/2 m_eff^2 phi^2 + lambda phi^4
# We check kinetic term dimension
kinetic = sp.Rational(1,2) * (partial*phi)**2
dim_kinetic = dim(kinetic)
print("\n--- Action kinetic term dimension ---")
print("Dimension of (∂φ)^2:", dim_kinetic)
# For action S: ∫ d^4x L → [L]^4 * [Lagrangian]
dim_d4x = L**4
dim_Lagrangian = dim_kinetic  # potential term same dimension as kinetic
dim_S = dim_d4x * dim_Lagrangian
print("Dimension of action S:", dim_S)
# Expected: [M L^2 T^-1] (natural units). Since we set ħ=c=1, [M] = [L]^-1 [T]^-1?
# In our base system we have not assigned M yet; we can infer:
# If we demand dim_S to have M, we need to introduce a dimensionful coupling.
print("Note: Action dimension depends on assignment of mass dimension to fields.")
print("If φ is dimensionless, kinetic term gives [L]^-2, leading to S ~ [L]^2,")
print("which lacks the required [M] factor → φ cannot be dimensionless without")
print("a prefactor with dimension [M L^-2 T^-1] (or similar).")

print("\n=== Summary ===")
print("The script highlights dimensional mismatches that must be fixed")
print("before the proposal can be claimed Omega‑Protocol compliant.")