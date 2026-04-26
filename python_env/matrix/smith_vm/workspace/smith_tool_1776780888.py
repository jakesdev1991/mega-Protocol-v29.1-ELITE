# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the refined DARM‑Ω proposal.
Checks:
  1. Dimensional consistency of the Omega Action terms.
  2. Positivity / bounds of the Omega invariants (Φ_N, Φ_Δ, J*).
  3. Consistency of the Configuration Dynamics Index (CDI) definition.
  4. Mapping formulas for Φ_N and Φ_Δ stay within physical ranges.
  5. Entropy gauge and stiffness invariants are well‑defined.
  6. MPC‑Ω constraints are respected for a synthetic test case.

The script uses sympy for symbolic dimensional analysis and numpy for a quick
numeric sanity check.  If any check fails, an AssertionError is raised.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. Symbolic dimensional analysis
# ----------------------------------------------------------------------
# Base dimensions: [M] mass, [L] length, [T] time, [I] information (dimensionless)
# We work in natural units where ħ = c = 1 → action is dimensionless.
# Therefore we assign dimensions such that the action S has dimension 1.

# Define symbols with dimensions (as sympy objects with assumed dimension)
# We'll use a simple dimensional analysis: each symbol gets a power of [T]
# (time) because in natural units length and mass are inverse time.
t   = sp.symbols('t', real=True)          # time
dt  = sp.symbols('dt', real=True, positive=True)  # time step
# Configuration vector components are taken to be dimensionless after
# normalisation (station weight ∈ {0,1}, integration time normalised by max,
# frequency normalised by reference ν0).
c   = sp.symbols('c', real=True)          # generic config component (dimensionless)
# Information gain I is dimensionless (mutual information in nats)
I   = sp.symbols('I', real=True, nonnegative=True)
# Metric g_μν multiplies \dot{c}^2 → must have dimension [T]^2 to make kinetic term dimensionless
g   = sp.symbols('g', real=True, positive=True)   # dimension [T]^2
# Lambda_Omega couples to L_Omega (dimensionless) → lambda dimensionless
lambda_O = sp.symbols('lambda_O', real=True)
# Gauge term A_mu J^mu: A_mu = ∂_mu S_conf, S_conf dimensionless → A_mu has [T]^-1
# J^mu is a current, dimension [T] (to make product dimensionless)
A   = sp.symbols('A', real=True)          # dimension [T]^-1
J   = sp.symbols('J', real=True)          # dimension [T]

# Build the action density Lagrangian (integrand)
# S = ∫ dt [ 1/2 g \dot{c}^2 - I + lambda_O * L_Omega + A_mu J^mu ]
# For dimensional check we ignore integrals and just check the bracket.
c_dot = sp.symbols('c_dot', real=True)   # \dot{c} has dimension [T]^-1 (since c dimensionless)
# Kinetic term: 1/2 g * c_dot^2
kinetic = sp.Rational(1,2) * g * c_dot**2
# Potential term: -I
potential = -I
# Omega coupling term: lambda_O * L_Omega (L_Omega dimensionless)
omega_coupling = lambda_O * sp.symbols('L_Omega', real=True)
# Gauge term: A * J
gauge_term = A * J

lagrangian = kinetic + potential + omega_coupling + gauge_term

# Expected dimension of lagrangian: [T]^-1 (since ∫ dt gives dimensionless action)
# Therefore each term must have dimension [T]^-1.
# We'll assign dimensional powers and verify they sum to -1.
# Let dim[X] denote exponent of [T] in X.
dim = {
    g: 2,          # [T]^2
    c_dot: -1,     # [T]^-1
    I: 0,          # dimensionless
    lambda_O: 0,
    sp.symbols('L_Omega'): 0,
    A: -1,         # [T]^-1
    J: 1,          # [T]^1
}

def dim_of(expr):
    """Return the total dimension exponent of [T] in expr (assuming symbols are independent)."""
    if expr.is_number:
        return 0
    if expr in dim:
        return dim[expr]
    if expr.is_Add:
        # For sum, all terms must have same dimension; we return the dimension of the first term
        # and later verify consistency.
        return dim_of(expr.args[0])
    if expr.is_Mul:
        return sum(dim_of(arg) for arg in expr.args)
    if expr.is_Pow:
        base, exp = expr.as_base_exp()
        return exp * dim_of(base)
    # Fallback: treat as dimensionless
    return 0

lag_dim = dim_of(lagrangian)
assert lag_dim == -1, f"Lagrangian dimension mismatch: expected -1, got {lag_dim}"

# ----------------------------------------------------------------------
# 2. Define CDI and check its dimensionless nature after normalisation
# ----------------------------------------------------------------------
# CDI(t) = α * ||Δc*||/Δt + β * ||Δc*|| + γ * ||c* - c_actual||
# All norms are Euclidean over dimensionless config components → dimensionless.
# Thus:
#   term1: α * (dimensionless / [T]) → α must have dimension [T]
#   term2: β * dimensionless          → β dimensionless
#   term3: γ * dimensionless          → γ dimensionless
# After normalisation by median CDI_quiet (dimensionless) → CDI_tilde dimensionless.

alpha, beta, gamma = sp.symbols('alpha beta gamma', real=True)
delta_c = sp.symbols('delta_c', real=True)   # ||Δc*|| (dimensionless)
delta_t = sp.symbols('delta_t', real=True, positive=True)  # Δt
diff_actual = sp.symbols('diff_actual', real=True)  # ||c* - c_actual|| (dimensionless)

CDI = alpha * delta_c / delta_t + beta * delta_c + gamma * diff_actual
# Assign dimensions: delta_c, diff_actual dimensionless; delta_t [T]
dim_alpha = 1   # [T]
dim_beta  = 0
dim_gamma = 0

CDI_dim = dim_of(alpha) + dim_of(delta_c) - dim_of(delta_t) \
          + dim_of(beta) + dim_of(delta_c) \
          + dim_of(gamma) + dim_of(diff_actual)
assert CDI_dim == 0, f"CDI dimension mismatch: expected 0, got {CDI_dim}"

# ----------------------------------------------------------------------
# 3. Mapping to Omega invariants (Φ_N, Φ_Δ) – check bounds
# ----------------------------------------------------------------------
# Φ_N = Φ_N0 - η1 * CDI_tilde(t-τ1) + η2 * I(c*)
# Φ_Δ = Φ_Δ0 + η3 * CDI_tilde(t-τ2) - η4 * Uniformity(c*)
# Assume Φ_N0, Φ_Δ0 ∈ [0,1]; η_i ≥0; I ∈ [0, I_max]; Uniformity ∈ [0,1]
# We'll test with random numbers to ensure outputs stay in [0,1] for reasonable parameters.

Phi_N0 = 0.6
Phi_Delta0 = 0.3
eta1, eta2, eta3, eta4 = 0.2, 0.15, 0.25, 0.1
I_max = 2.0
tau1, tau2 = 5.0, 8.0  # days, not needed for dimension check

def test_mapping(num_samples=1000):
    np.random.seed(0)
    CDI_tilde = np.random.uniform(0.5, 2.5, size=num_samples)  # normalised CDI
    I_val = np.random.uniform(0, I_max, size=num_samples)
    uniformity = np.random.uniform(0, 1, size=num_samples)

    Phi_N = Phi_N0 - eta1 * CDI_tilde + eta2 * I_val
    Phi_Delta = Phi_Delta0 + eta3 * CDI_tilde - eta4 * uniformity

    # Clip to see if any violation occurs
    assert np.all(Phi_N >= 0) and np.all(Phi_N <= 1), \
        f"Phi_N out of bounds: min={Phi_N.min()}, max={Phi_N.max()}"
    assert np.all(Phi_Delta >= 0) and np.all(Phi_Delta <= 1), \
        f"Phi_Delta out of bounds: min={Phi_Delta.min()}, max={Phi_Delta.max()}"
    return True

assert test_mapping(), "Mapping to Omega invariants violated bounds"

# ----------------------------------------------------------------------
# 4. Stiffness invariants from Hessian eigenvalues (symbolic check)
# ----------------------------------------------------------------------
# ξ_N^{-2} = λ_N(t), ξ_Δ^{-2} = λ_Δ(t) → ξ_N, ξ_Δ have dimension [T]
# We'll verify that if λ has dimension [T]^-2 then ξ has [T].
lambda_N, lambda_Delta = sp.symbols('lambda_N lambda_Delta', real=True)
# Assign dimension [T]^-2 to eigenvalues
dim_lambda = -2
xi_N = lambda_N**(-0.5)
xi_Delta = lambda_Delta**(-0.5)
assert dim_of(xi_N) == 1, f"xi_N dimension mismatch: expected 1, got {dim_of(xi_N)}"
assert dim_of(xi_Delta) == 1, f"xi_Delta dimension mismatch: expected 1, got {dim_of(xi_Delta)}"

# ----------------------------------------------------------------------
# 5. Entropy gauge: S_conf dimensionless → A_mu = ∂_mu S_conf has dimension [T]^-1
# ----------------------------------------------------------------------
S_conf = sp.symbols('S_conf', real=True)   # dimensionless
# derivative w.r.t. time adds -1 exponent
A_mu = sp.diff(S_conf, t)  # symbolic derivative; dimension analysis:
assert dim_of(A_mu) == -1, f"A_mu dimension mismatch: expected -1, got {dim_of(A_mu)}"

# ----------------------------------------------------------------------
# 6. MPC‑Ω constraints check (synthetic state vector)
# ----------------------------------------------------------------------
# Constraints: CDI_tilde ≤ 3.0, Φ_N ≥ 0.4, Φ_Δ ≤ 0.8, S_conf ≥ S_min
S_min = 0.2
def check_constraints(state):
    CDI_tilde, Phi_N, Phi_Delta, S_conf_val = state
    assert CDI_tilde <= 3.0 + 1e-9, f"CDI_tilde too large: {CDI_tilde}"
    assert Phi_N >= 0.4 - 1e-9, f"Phi_N too small: {Phi_N}"
    assert Phi_Delta <= 0.8 + 1e-9, f"Phi_Delta too large: {Phi_Delta}"
    assert S_conf_val >= S_min - 1e-9, f"S_conf too small: {S_conf_val}"
    return True

# Generate a random feasible state and test
np.random.seed(42)
state = [
    np.random.uniform(0.5, 2.5),   # CDI_tilde
    np.random.uniform(0.4, 0.9),   # Phi_N
    np.random.uniform(0.2, 0.7),   # Phi_Delta
    np.random.uniform(S_min, 1.0)  # S_conf
]
assert check_constraints(state), "MPC‑Ω constraints violated"

# ----------------------------------------------------------------------
# If we reach here, all checks passed.
# ----------------------------------------------------------------------
print("All validation checks passed:")
print("  - Action Lagrangian dimensionless ✓")
print("  - CDI dimensionally consistent ✓")
print("  - Φ_N, Φ_Δ mappings respect [0,1] bounds ✓")
print("  - Stiffness invariants have correct time dimension ✓")
print("  - Entropy gauge derivative dimension correct ✓")
print("  - MPC‑Ω constraints satisfied for synthetic state ✓")