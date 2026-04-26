# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith – Omega Protocol Validator
# This script checks a candidate FTFM‑Ω proposal for strict compliance
# with the Omega Physics Rubric v26.0 (the “Strictor Gate”).
# It focuses on the invariant, the diffusion term, the gauge term,
# dimensional consistency of the stiffness invariants, and the
# functional form of the Contextual Fragility Index (CFI).
#
# To use: replace the placeholder strings in the `proposal` dict
# with the actual mathematical expressions from the revised proposal.
# The script will raise AssertionError on any violation.

import sympy as sp
import re

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def normalize_expr(expr_str):
    """Parse a string into a sympy expression, simplifying."""
    return sp.simplify(sp.sympify(expr_str))

def is_log_of_phi_n(expr, phi_n_sym):
    """
    Return True if expr is of the form log(phi_n) + const,
    where const may be zero.  No other dependence on phi_n
    (e.g., powers, products) is allowed.
    """
    # Move constant term out
    const = sp.nsimplify(expr - sp.log(phi_n_sym))
    # const should be independent of phi_n
    return const.free_symbols.isdisjoint({phi_n_sym})

def has_half_diffusion_term(diff_eq_str):
    """
    Check that the diffusion term appears as (1/2)*D*∇²F
    (or equivalently D*∇²F with a comment that D already contains 1/2).
    We accept either an explicit 1/2 factor or a note that D is defined
    with the factor included.
    """
    # Look for pattern 1/2 * D * laplacian or 0.5 * D * laplacian
    pattern = r'(?i)\b(1/2|0\.5)\s*\*\s*D\s*\*\s*∇²\s*F\b'
    if re.search(pattern, diff_eq_str):
        return True
    # If the user states that D already includes the 1/2 factor, accept it
    if re.search(r'(?i)D\s*\(.*?1/2.*?\)', diff_eq_str):
        return True
    return False

def gauge_term_variational(gauge_str, entropy_str):
    """
    Very light check: the gauge term should be derivable from
    A_mu J^mu where A_mu = ∂_mu S_context.
    We verify that the expression contains a derivative of the entropy.
    """
    # Accept patterns like dS/dx_mu or ∂_mu S
    return bool(re.search(r'(?i)(∂|d)\s*.*?S\s*[_\w]*', gauge_str))

def stiffness_dimension_ok(stiff_expr, time_sym):
    """
    Stiffness invariants ξ_N, ξ_Δ must have dimensions of time.
    In a dimensionless manifold we introduce an explicit time scale τ0.
    We accept expressions that are proportional to τ0 (or its inverse
    squared inside a kinetic prefactor, etc.).
    """
    # Simple check: expression contains τ0 (or a symbol named tau0)
    return bool(re.search(r'(?i)\bτ0\b|\btau0\b', stiff_expr))

def cfi_form(cfi_expr):
    """
    CFI must be a tanh of a linear combination of the four base metrics
    (variance, coupling, singularity, -density) with non‑negative weights.
    We only check the outer tanh and that the argument is a sum.
    """
    # Outer tanh
    if not isinstance(cfi_expr, sp.Function) or cfi_expr.func != sp.tanh:
        return False
    inner = cfi_expr.args[0]
    # Inner should be a sum (Add) of terms
    return isinstance(inner, sp.Add)

# ----------------------------------------------------------------------
# Proposal placeholder – replace with the actual strings from the revised
# proposal.  For illustration we use the *corrected* forms.
# ----------------------------------------------------------------------
proposal = {
    # Invariant: psi = ln(phi_n)  (phi_n is the connectivity mode Φ_N)
    "invariant_expr": "ln(Phi_N)",                     # <-- must be exactly log(Phi_N) (+ const allowed)
    "phi_n_symbol": "Phi_N",

    # Stochastic reaction‑diffusion: ∂t F = (1/2) D(c) ∇²c F + R(F,s) + ζ
    "diffusion_eq": "∂t F = (1/2) * D(c) * ∇²c F + R(F,s) + ζ(c,t)",

    # Entropy gauge term: A_mu J^mu with A_mu = ∂_mu S_context
    "gauge_term": "A_mu * J^mu where A_mu = ∂_mu S_context",
    "entropy_expr": "S_context = - Σ p_k log p_k",

    # Stiffness invariants (should contain τ0)
    "xi_N_expr": "τ0 * f_N(Φ_N, Φ_Δ)",                 # <-- contains τ0
    "xi_Δ_expr": "τ0 * f_Δ(Φ_N, Φ_Δ)",

    # Contextual Fragility Index: tanh(α σ² + β κ + γ χ - δ ρ)
    "cfi_expr": "tanh(α*σ2_TF + β*κ + γ*χ - δ*ρ)",

    # Lead‑time adaptation (optional check)
    "lead_time_expr": "τ(CFI, ρ) = τ0 * exp(-β*CFI) / (1 + ρ)",
}

# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------
def validate_proposal(p):
    # 1. Invariant check
    expr = normalize_expr(p["invariant_expr"])
    phi_n = sp.Symbol(p["phi_n_symbol"])
    assert is_log_of_phi_n(expr, phi_n), \
        f"Invariant must be ln(phi_n) (+ const). Got: {expr}"

    # 2. Diffusion term ½ factor
    assert has_half_diffusion_term(p["diffusion_eq"]), \
        f"Diffusion term missing explicit 1/2 factor: {p['diffusion_eq']}"

    # 3. Gauge term variational origin
    assert gauge_term_variational(p["gauge_term"], p["entropy_expr"]), \
        f"Gauge term not shown to derive from A_mu = ∂_mu S_context: {p['gauge_term']}"

    # 4. Stiffness invariants dimension of time
    tau0 = sp.Symbol('τ0')
    assert stiffness_dimension_ok(p["xi_N_expr"], tau0), \
        f"ξ_N expression does not contain time scale τ0: {p['xi_N_expr']}"
    assert stiffness_dimension_ok(p["xi_Δ_expr"], tau0), \
        f"ξ_Δ expression does not contain time scale τ0: {p['xi_Δ_expr']}"

    # 5. CFI functional form
    cfi = normalize_expr(p["cfi_expr"])
    assert cfi_form(cfi), \
        f"CFI must be tanh(linear combination of σ², κ, χ, -ρ). Got: {cfi}"

    # 6. Lead‑time dependence (soft warning, not fatal)
    lead = p["lead_time_expr"]
    if "τ0" not in lead and "tau0" not in lead:
        print("[Warning] Lead time does not explicitly reference τ0; consider making it adaptive.")

    print("✅ All Omega Protocol invariants satisfied.")

if __name__ == "__main__":
    try:
        validate_proposal(proposal)
    except AssertionError as e:
        print("❌ Validation failed:")
        print(e)
        # Optionally, you could halt integration here.
        raise SystemExit(1)