# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith – Omega Protocol Validator
# This script checks the Engine's proposal against the Omega Physics Rubric v26.0
# and highlights any violations of the core invariants and mathematical form.

import sympy as sp
import re

# ----------------------------------------------------------------------
# Helper: simple pattern matcher for the required invariant form
# ----------------------------------------------------------------------
def check_invariant(expr_str):
    """
    The rubric requires the invariant to appear exactly as:
        psi = ln(phi_n)
    (allowing optional whitespace and optional multiplicative constant 1).
    Any extra additive terms or different functional form is a violation.
    """
    # Normalise: remove spaces, lower case
    s = expr_str.replace(" ", "").lower()
    # Expected pattern: psi=ln(phi_n)  (phi_n may be written as phi_n or \phi_n)
    pattern = r'psi=ln\([\\]?phi[ _]?n\)'
    return bool(re.fullmatch(pattern, s))

# ----------------------------------------------------------------------
# Helper: check Fokker‑Planck diffusion term for the 1/2 factor
# ----------------------------------------------------------------------
def check_fokker_planck(eq_str):
    """
    Canonical Fokker‑Planck (in one variable Λ):
        ∂_t P = -∂_Λ[μ P] + (1/2) ∂_Λ²[D P] + S
    We look for the term "... ∂_Λ²[ ... ]" preceded by a factor 0.5 or 1/2.
    """
    # Remove spaces for easier regex
    s = eq_str.replace(" ", "")
    # Pattern: ... (1/2)∂_Λ²[ ... ]  or  ...0.5∂_Λ²[ ... ]  or  ...(0.5)∂_Λ²[ ... ]
    pattern = r'(?:\(\s*0\.5\s*\)|0\.5|\(\s*1/2\s*\)|1/2)\s*\\?partial_?\Lambda\s*^?2\s*\['
    return bool(re.search(pattern, s, re.IGNORECASE))

# ----------------------------------------------------------------------
# Helper: verify that the action contains the entropy gauge term A_μ J^μ
# ----------------------------------------------------------------------
def check_gauge_term(action_str):
    """
    The Omega Action must include a term of the form A_μ J^μ (with implicit sum).
    We accept variations like A_mu J^mu, A_μ J^μ, A·J, etc.
    """
    s = action_str.replace(" ", "")
    # Look for A followed by _?mu and J followed by _?mu (case‑insensitive)
    pattern = r'A[ _]?mu.*J[ _]?mu|J[ _]?mu.*A[ _]?mu'
    return bool(re.search(pattern, s, re.IGNORECASE))

# ----------------------------------------------------------------------
# Mock data – replace these strings with the actual proposal text if available
# ----------------------------------------------------------------------
# Example invariant as written by the Engine (from the critique)
engine_invariant = "psi = ln(|R_cog|/R_0) + λ·max TFFI"
# Example Fokker‑Planck equation as written
engine_fokker = "∂_t P = -∂_Λ[μ P] + ∂_Λ²[D P] + S"
# Example Omega Action snippet (missing gauge term)
engine_action = r"S[Λ] = ∫ d^4x √{-g} [ ½ g^{μν} ∂_μ Λ ∂_ν Λ + V(Λ) + λ_Ω L_Ω(Φ_N, Φ_Δ)]"

# ----------------------------------------------------------------------
# Run checks
# ----------------------------------------------------------------------
print("=== Omega Protocol Compliance Check ===\n")

# 1. Invariant form
inv_ok = check_invariant(engine_invariant)
print(f"Invariant check (psi = ln(phi_n)): {'PASS' if inv_ok else 'FAIL'}")
if not inv_ok:
    print(f"  → Found: {engine_invariant}")
    print("  → Rubric requires exactly ψ = ln(Φ_N) (no extra terms).\n")

# 2. Fokker‑Planck diffusion factor
fp_ok = check_fokker_planck(engine_fokker)
print(f"Fokker‑Planck ½ factor check: {'PASS' if fp_ok else 'FAIL'}")
if not fp_ok:
    print(f"  → Found: {engine_fokker}")
    print("  → Missing the factor ½ before the diffusion term.\n")

# 3. Gauge term in action
gauge_ok = check_gauge_term(engine_action)
print(f"Action gauge term (A_μ J^μ) check: {'PASS' if gauge_ok else 'FAIL'}")
if not gauge_ok:
    print(f"  → Action snippet: {engine_action}")
    print("  → The entropy gauge term A_μ J^μ is absent from the action integral.\n")

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
all_ok = inv_ok and fp_ok and gauge_ok
print("\n=== Verdict ===")
if all_ok:
    print("PASS – The proposal satisfies the Omega Physics Rubric v26.0 (to the extent checked).")
else:
    print("FAIL – One or more rubric requirements are violated. "
          "Correct the issues above before the integration can be accepted.")