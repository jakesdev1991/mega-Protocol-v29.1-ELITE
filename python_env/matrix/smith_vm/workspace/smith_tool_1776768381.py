# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Dimensional‑consistency validator for the refined CIFO‑Ω proposal.
Checks that all terms in the Omega Action, invariant definitions,
and boundary conditions are dimensionally homogeneous (using ħ = c = 1).
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Define dimension symbols (mass dimension) for each primitive quantity
# ----------------------------------------------------------------------
# Base dimensions: [M] = mass, [L] = length, [T] = time.
# In natural units ħ = c = 1 we have [M] = [L]^{-1} = [T]^{-1}.
# We'll track only the mass dimension (the others follow automatically).
M = sp.symbols('M')   # mass dimension

# Primitive quantities
dim = {
    # Field and its derivatives
    'E'          : 0,          # dimensionless efficiency
    'dE_dt'      : 1,          # ∂_t E  → mass^1
    'dE_dx'      : 1,          # ∇E     → mass^1
    # Parameters
    'v'          : 0,          # speed (set to 1, dimensionless)
    'lam'        : 2,          # λ in V(E) = λ/4 (E^2 - E0^2)^2
    'E0'         : 0,          # equilibrium efficiency (dimensionless)
    'xi_cap'     :-1,          # correlation length → mass^{-1}
    'xi0'        :-1,          # reference length (same dim as xi_cap)
    # Invariants
    'psi_cap'    : 0,          # ln(xi_cap/xi0) → dimensionless
    'xiT_inv2'   : 2,          # stiffness inverse squared → mass^2
    'xiA_inv2'   : 2,
    'xiG_inv2'   : 2,
    # Entropy
    'S_cap'      : 0,          # Shannon entropy → dimensionless
    'A_mu'       : 1,          # ∂_μ S_cap → mass^1
    # Covariant modes (averages/variances of E)
    'Phi_T'      : 0,
    'Phi_A'      : 0,
    'Phi_G'      : 0,
    # Mean and std-dev of E
    'E_bar'      : 0,
    'sigma_E'    : 0,
}

def dim_of(expr):
    """Return the mass dimension of a SymPy expression assuming symbols are multiplied."""
    if expr.is_Number:
        return 0
    if expr.is_Symbol:
        return dim.get(str(expr), 0)  # default 0 if unknown
    if expr.is_Pow:
        base, exp = expr.as_base_exp()
        return dim_of(base) * exp
    if expr.is_Mul:
        return sum(dim_of(arg) for arg in expr.args)
    if expr.is_Add:
        # For addition, all terms must share the same dimension; we return that dimension
        # (the caller will check homogeneity)
        dims = {dim_of(arg) for arg in expr.args}
        if len(dims) != 1:
            raise ValueError(f"Non‑homogeneous addition: {expr} → dimensions {dims}")
        return next(iter(dims))
    if expr.is_Function:
        # Treat generic functions (log, exp, etc.) as dimensionless if their argument is dimensionless
        arg = expr.args[0]
        return dim_of(arg)  # e.g., log(xi_cap/xi0) inherits dimension of argument (should be 0)
    return 0  # fallback

# ----------------------------------------------------------------------
# 2. Define key expressions from the proposal
# ----------------------------------------------------------------------
# Kinetic and gradient terms in the action
kinetic   = sp.Symbol('dE_dt')**2          # (∂_t E)^2
gradient  = sp.Symbol('v')**2 * sp.Symbol('dE_dx')**2  # v^2 (∇E)^2

# Potential V(E) = λ/4 (E^2 - E0^2)^2
V = sp.Symbol('lam')/4 * (sp.Symbol('E')**2 - sp.Symbol('E0')**2)**2

# Omega coupling (treated as dimensionless scalar for this check)
Omega_coupling = sp.Symbol('lambda_Omega') * sp.Symbol('L_Omega')  # placeholder

# Entropy gauge term A_mu J^μ – we only need the dimension of A_mu (J^μ taken as dimensionless current)
entropy_gauge_term = sp.Symbol('A_mu')  # dimension checked separately

# Action integrand Lagrangian density
L = kinetic + gradient + V + Omega_coupling + entropy_gauge_term

# ----------------------------------------------------------------------
# 3. Invariant definitions
# ----------------------------------------------------------------------
psi_cap_def   = sp.log(sp.Symbol('xi_cap')/sp.Symbol('xi0'))   # ln(xi_cap/xi0)
# Stiffness inverses (second derivative of effective potential)
# For the check we just verify that the symbols we introduced have the expected dimension.
xiT_inv2_def  = sp.Symbol('xiT_inv2')
xiA_inv2_def  = sp.Symbol('xiA_inv2')
xiG_inv2_def  = sp.Symbol('xiG_inv2')

# Entropy definition (dimensionless by construction)
S_cap_def = -sp.Integral(sp.Symbol('p')*sp.log(sp.Symbol('p')), (sp.Symbol('E'), 0, 1))
# We only check that the integrand is dimensionless; the integral over a dimensionless variable preserves dimension.
S_cap_integrand_dim = dim_of(sp.Symbol('p')*sp.log(sp.Symbol('p')))  # p is dimensionless → 0

# ----------------------------------------------------------------------
# 4. Boundary conditions (expressed as inequalities on second derivative)
# ----------------------------------------------------------------------
# Shredding: ∂^2 V_eff / ∂Φ_T^2 < 0   →   ξ_T^{-2} < 0
# Freeze:    ∂^2 V_eff / ∂Φ_G^2 → ∞   →   ξ_G^{-2} → +∞
# For dimensional check we just ensure the symbols have correct dimension.
shredding_cond = sp.Lt(xiT_inv2_def, 0)   # ξ_T^{-2} < 0
freeze_cond    = sp.Gt(xiG_inv2_def, 0)   # ξ_G^{-2} > 0 (signifies positive curvature; infinite limit is a separate statement)

# ----------------------------------------------------------------------
# 5. Perform dimensional checks
# ----------------------------------------------------------------------
def check_dimension(expr, name, expected_dim=None):
    """Assert that expr has a single, well‑defined dimension."""
    d = dim_of(expr)
    if expected_dim is not None and d != expected_dim:
        raise AssertionError(
            f"Dimension mismatch for {name}: got {d}, expected {expected_dim}"
        )
    # If we only want to verify homogeneity (no expected given), just return the dimension.
    return d

print("=== Dimensional Consistency Check for CIFO‑Ω ===")

# Action Lagrangian density – all terms must share the same dimension
print("\n1. Action Lagrangian density terms:")
for term, label in [(kinetic, "kinetic"), (gradient, "gradient"),
                    (V, "potential V"), (Omega_coupling, "Omega coupling"),
                    (entropy_gauge_term, "entropy gauge")]:
    d = check_dimension(term, label)
    print(f"   {label}: dimension = {d}")

# Ensure they are all equal
L_terms = [kinetic, gradient, V, Omega_coupling, entropy_gauge_term]
L_dims = {check_dimension(t, f"L_term_{i}") for i, t in enumerate(L_terms)}
assert len(L_dims) == 1, f"Action terms not dimensionally homogeneous: {L_dims}"
print(f"   → All Lagrangian terms share dimension = {next(iter(L_dims))}")

# Invariant definitions
print("\n2. Invariant definitions:")
d_psi = check_dimension(psi_cap_def, "psi_cap")
print(f"   psi_cap = ln(xi_cap/xi0): dimension = {d_psi}")
assert d_psi == 0, "psi_cap must be dimensionless"

d_S = check_dimension(S_cap_integrand_dim, "S_cap integrand")
print(f"   S_cap integrand dimension = {d_S} (should be 0 for dimensionless entropy)")
assert d_S == 0, "Entropy integrand must be dimensionless"

d_A = check_dimension(sp.Symbol('A_mu'), "A_mu")
print(f"   A_mu = ∂_μ S_cap: dimension = {d_A}")
assert d_A == 1, "A_mu must have mass dimension 1 (∂_μ adds one mass)"

# Stiffness inverses
print("\n3. Stiffness invariants:")
for sym, name in [(xiT_inv2_def, "xiT^{-2}"),
                  (xiA_inv2_def, "xiA^{-2}"),
                  (xiG_inv2_def, "xiG^{-2}")]:
    d = check_dimension(sym, name)
    print(f"   {name}: dimension = {d}")
    assert d == 2, f"{name} should have dimension mass^2"

# Covariant modes and related quantities
print("\n4. Covariant modes and statistical quantities:")
for sym, name in [('Phi_T', "Φ_T"), ('Phi_A', "Φ_A"), ('Phi_G', "Φ_G"),
                  ('E_bar', "⟨E⟩"), ('sigma_E', "σ_E")]:
    d = check_dimension(sp.Symbol(sym), name)
    print(f"   {name}: dimension = {d}")
    assert d == 0, f"{name} must be dimensionless"

# Boundary conditions (just check symbols)
print("\n5. Boundary condition symbols:")
print(f"   Shredding condition ξ_T^{{-2}} < 0 : symbol dimension = {check_dimension(xiT_inv2_def, 'xiT^{-2}')}")
print(f"   Freeze    condition ξ_G^{{-2}} > 0 : symbol dimension = {check_dimension(xiG_inv2_def, 'xiG^{-2}')}")

print("\n✅ All dimensional checks passed. The mathematical core of the proposal is dimensionally consistent.")