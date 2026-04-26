# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol v26.0 – Strictor Gate Validator
----------------------------------------------
This script checks a candidate Ω‑integration (here the BRDI‑Ω proposal)
against the *absolute* mathematical requirements of the Omega Physics
Rubric v26.0.  It is deliberately minimal: it works with symbolic
expressions supplied as strings (or SymPy objects) and raises an
AssertionError the moment any invariant is violated.

Usage:
    1. Fill in the placeholders in the "USER DEFINED SECTION" with the
       actual expressions from the proposal (as SymPy objects or
       parsable strings).
    2. Run the script.  If it finishes without raising an AssertionError,
       the proposal passes the Strictor Gate; otherwise the traceback
       tells you exactly which rule failed.

The validator covers:
    • Kinetic term  → ½ g^{μν} ∂_μ 𝒟 ∂_ν 𝒟
    • Double‑well potential V(𝒟) = (α/2)‖𝒟‖² + (β/4)‖𝒟‖⁴ – γ𝒟
    • Entropy‑gauge term A_μ J^μ with an explicit, dimensionless J^μ
    • Covariant modes Φ_N (variance) and Φ_Δ (skewness)
    • Invariant ψ = ln φ_n  with φ_n dimensionless & positive
    • Boundary conditions expressed via divergence of Φ_Δ
    • Entropy gauge S_data = –∑ p_i ln p_i  (Shannon)
    • All fields & coordinates treated as dimensionless after
      normalisation (checked by ensuring no explicit dimensional
      constants appear).

If you need to extend the checks (e.g. add specific forms for R(𝒟,S) or
ζ), simply add more assertions in the appropriate section.
"""

import sympy as sp
import re

# ----------------------------------------------------------------------
# USER DEFINED SECTION – replace the placeholders with the actual
# expressions from the proposal.  They can be SymPy objects or strings
# that sympy.sympify can parse.
# ----------------------------------------------------------------------
# Example placeholders (do NOT edit these lines – replace the RHS):
# ----------------------------------------------------------------------
# Metric (assumed Minkowski for simplicity; replace with actual g^{μν})
mu, nu = sp.symbols('mu nu')
g = sp.Matrix([[1, 0, 0, 0],
               [0, -1, 0, 0],
               [0, 0, -1, 0],
               [0, 0, 0, -1]])  # η^{μν}
# Kinetic term: ½ g^{μν} ∂_μ 𝒟 ∂_ν 𝒟
phi = sp.Function('phi')(sp.Symbol('t'))  # placeholder for 𝒟(t)
# We'll treat ∂_μ 𝒟 as generic symbols dphi_mu, dphi_nu
dphi_mu, dphi_nu = sp.symbols('dphi_mu dphi_nu')
kinetic_term = sp.Rational(1,2) * g[mu, nu] * dphi_mu * dphi_nu  # <-- replace with real expression

# Double‑well potential V(𝒟)
alpha, beta, gamma = sp.symbols('alpha beta gamma', real=True)
# Assume ‖𝒟‖² = phi**2 for 1‑d placeholder; adapt for vector norm if needed
norm_sq = phi**2
norm_quartic = phi**4
potential = (alpha/2)*norm_sq + (beta/4)*norm_quartic - gamma*phi  # <-- replace

# Entropy gauge: A_μ J^μ
# A_μ = ∂_μ S_data  (we will define S_data later)
S_data = sp.Function('S')(sp.Symbol('t'))  # placeholder for entropy
A_mu = sp.diff(S_data, sp.Symbol('x' + str(mu)))  # generic derivative
# *** USER MUST DEFINE J^mu explicitly here ***
# Example compliant choice: J^mu = sqrt(2) * Phi_Delta * timelike_unit_vector
Phi_Delta = sp.symbols('Phi_Delta')
# timelike unit vector in μ‑direction (only μ=0 non‑zero for simplicity)
timelike_unit = sp.KroneckerDelta(mu, 0)  # 1 if mu==0 else 0
J_mu = sp.sqrt(2) * Phi_Delta * timelike_unit  # <-- replace with your definition
entropy_gauge_term = A_mu * J_mu

# Covariant modes (must be explicit statistical moments)
# We'll assume we have access to decoded data moments via symbols
phi_N = sp.symbols('Phi_N')   # variance across sources
# Phi_Delta already defined above as skewness placeholder

# Invariant ψ = ln φ_n  with φ_n dimensionless & positive
lam = sp.symbols('lambda')
# Placeholder for Ricci curvature scalar of source graph
Ricc = sp.symbols('R_G')
R0 = sp.symbols('R_0', positive=True)
DCI = sp.symbols('DCI')
phi_n = (Ricc / R0) * sp.exp(lam * DCI)   # dimensionless by construction
psi = sp.log(phi_n)

# Boundary conditions – must be expressed via divergence of Φ_Δ
# We define a generic divergence operator Div
def Div(expr):
    # placeholder: treat as derivative w.r.t. a generic coordinate x
    return sp.diff(expr, sp.Symbol('x'))

# Data Shredding: ψ → +∞  AND  Φ_Δ → +∞ (or exceeds high threshold)
# Data Freeze:   ψ → -∞  AND  Φ_Δ → 0   (or falls below low threshold)
# We'll encode as logical conditions that must be present in the proposal.
# For the validator we simply require that the proposal *mentions* these
# two conjunctions.  In practice you would search the proposal text;
# here we expose them as boolean flags the user must set True if present.
boundary_shredding_mentioned = False   # <-- SET TO TRUE if proposal states
boundary_freeze_mentioned    = False   # <-- SET TO TRUE if proposal states

# Entropy gauge S_data = –∑ p_i ln p_i  (Shannon)
# We'll just check that S_data appears with a log and a sum; actual form
# can be validated later if needed.
S_data_expr = -sp.Symbol('p') * sp.log(sp.Symbol('p'))  # placeholder

# ----------------------------------------------------------------------
# END OF USER DEFINED SECTION
# ----------------------------------------------------------------------


def assert_dimensionless(expr, name):
    """Very naive check: if expr contains any of the known dimensional
    constants (c, ħ, G, k_B, …) we flag it.  In a real deployment you
    would substitute the characteristic scales and verify the result is
    pure number."""
    dimensional_constants = [sp.Symbol('c'), sp.Symbol('hbar'),
                             sp.Symbol('G'), sp.Symbol('k_B')]
    for const in dimensional_constants:
        if const in expr.atoms(sp.Symbol):
            raise AssertionError(f"{name} appears to contain dimensional constant {const}.")
    # Additionally, ensure no explicit length/time symbols unless they are
    # cancelled by inverse symbols (too heavy for this demo – we trust the
    # user to have normalised).

def check_kinetic_term(term):
    # Must contain factor 1/2 and the contraction g^{μν}∂_μ𝒟∂_ν𝒟
    if term.has(sp.Rational(1,2)) is False:
        raise AssertionError("Kinetic term missing the required ½ factor.")
    # Check that it is a quadratic form in the derivatives with metric
    # For simplicity we just ensure it is of the form a * dphi_mu * dphi_nu
    # where a is the metric component.
    if not term.is_Mul:
        raise AssertionError("Kinetic term should be a product of metric and two derivatives.")
    # Extract the metric part
    coeffs = term.as_coeff_mul()
    # coeffs[0] should be the numeric factor; coeffs[1] list should contain g^{μν}
    # We'll skip deep tensor checks – rely on user to supply correct form.
    # Just ensure the term is not zero.
    if term == 0:
        raise AssertionError("Kinetic term is zero.")

def check_potential(V):
    # Must be of the form (α/2)‖𝒟‖² + (β/4)‖𝒟‖⁴ – γ𝒟
    # We'll check that V is a polynomial in 𝒟 up to order 4.
    if not V.is_polynomial(phi):
        raise AssertionError("Potential V(𝒟) is not a polynomial in the field.")
    deg = sp.Poly(V, phi).degree()
    if deg > 4:
        raise AssertionError("Potential exceeds quartic order (should be ≤4).")
    # Ensure constant term is zero (no standalone constant)
    if V.subs(phi, 0) != 0:
        raise AssertionError("Potential should vanish at 𝒟=0 (no constant offset).")

def check_entropy_gauge(term):
    # Must be of the form A_μ J^μ with J^μ explicitly defined.
    # We already built the term from user‑provided A_mu and J_mu.
    # Just ensure J_mu is not an undefined symbol.
    if J_mu.has(sp.Symbol('Undefined')) or J_mu.has(sp.Symbol('unknown')):
        raise AssertionError("Gauge current J^μ is not explicitly defined.")
    # Additionally, J_mu should be dimensionless – we rely on user.
    if not term.is_Mul:
        raise AssertionError("Entropy‑gauge term should be a product A_μ J^μ.")
    # Quick check: term should contain A_mu and J_mu factors
    if A_mu not in term.atoms() or J_mu not in term.atoms():
        raise AssertionError("Entropy‑gauge term does not contain both A_μ and J^μ.")

def check_covariant_modes(phi_N_sym, phi_Delta_sym):
    # They must be real symbols (or expressions) – we just ensure they exist.
    if not phi_N_sym:
        raise AssertionError("Covariant mode Φ_N is missing.")
    if not phi_Delta_sym:
        raise AssertionError("Covariant mode Φ_Δ is missing.")

def check_invariant(psi_expr):
    # ψ must be log of a dimensionless positive quantity φ_n
    if not psi_expr.has(sp.log):
        raise AssertionError("Invariant ψ is not expressed as a logarithm.")
    inside = psi_expr.args[0]  # argument of log
    if inside <= 0:
        raise AssertionError("Argument of log in ψ must be positive.")
    # Additionally, inside should be dimensionless – we trust user.
    # Optionally, we could verify that inside can be written as φ_n.
    if not inside.has(sp.exp):
        raise AssertionError("Inside of log does not contain the exponential "
                             "structure expected for φ_n = (|ℛ_G|/ℛ_0) e^{λ·DCI}.")

def check_boundary_conditions(shredding_flag, freeze_flag):
    # The proposal must explicitly state the two conjunctions.
    if not shredding_flag:
        raise AssertionError("Boundary condition 'Data Shredding' (ψ→+∞ & Φ_Δ→+∞) "
                             "not explicitly mentioned.")
    if not freeze_flag:
        raise AssertionError("Boundary condition 'Data Freeze' (ψ→−∞ & Φ_Δ→0) "
                             "not explicitly mentioned.")

def check_entropy(S_data_expr):
    # Must be Shannon form – at least contain a log and a sum over i.
    # We'll do a lightweight check: expression should contain -p*log(p)
    if not S_data_expr.has(sp.log):
        raise AssertionError("Entropy S_data does not contain a logarithm.")
    if not S_data_expr.has(sp.Mul):
        raise AssertionError("Entropy S_data does not appear as a sum over i.")
    # Additional checks could be added if the full sum is supplied.

def check_dimensionless(*exprs):
    for e in exprs:
        assert_dimensionless(e, str(e))

# ----------------------------------------------------------------------
# RUN VALIDATION
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Kinetic term
    print("Checking kinetic term …")
    check_kinetic_term(kinetic_term)

    # 2. Potential
    print("Checking double‑well potential …")
    check_potential(potential)

    # 3. Entropy‑gauge term
    print("Checking entropy‑gauge term …")
    check_entropy_gauge(entropy_gauge_term)

    # 4. Covariant modes
    print("Checking covariant modes …")
    check_covariant_modes(phi_N, Phi_Delta)

    # 5. Invariant ψ
    print("Checking invariant ψ …")
    check_invariant(psi)

    # 6. Boundary conditions (user‑provided flags)
    print("Checking boundary conditions …")
    check_boundary_conditions(boundary_shredding_mentioned,
                              boundary_freeze_mentioned)

    # 7. Entropy gauge S_data
    print("Checking entropy S_data …")
    check_entropy(S_data_expr)

    # 8. Dimensionless check on all major constructs
    print("Checking dimensionless nature …")
    check_dimensionless(kinetic_term, potential, entropy_gauge_term,
                        phi_N, Phi_Delta, psi, DCI, S_data_expr)

    print("\n✅ All checks passed – the proposal satisfies the Omega Protocol")
    print("   Strictor Gate (Rubric v26.0).")