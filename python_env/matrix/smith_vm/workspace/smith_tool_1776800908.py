# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator (Rubric v26.0)

Usage:
    >>> from omega_validator import validate_proposal
    >>> validate_proposal(proposal_dict)   # raises AssertionError on violation
"""

import re
import sympy as sp

def _check_no_boilerplate(text: str) -> None:
    """Very loose check: ensure the proposal contains domain‑specific terms."""
    required_terms = {"transfer-function", "context manifold", "Ricci curvature",
                      "CFI", "Phi_N", "Phi_Delta", "Omega Action"}
    missing = [t for t in required_terms if t.lower() not in text.lower()]
    if missing:
        raise AssertionError(f"Boilerplate suspicion: missing terms {missing}")

def _check_covariant_modes(text: str) -> None:
    """Phi_N and Phi_Delta must be explicitly defined from the Hessian."""
    pattern = r"Phi_N.*spectral gap|Phi_Delta.*asymmetry|Fiedler vector"
    if not re.search(pattern, text, re.I):
        raise AssertionError("Covariant modes (Phi_N, Phi_Delta) not properly defined.")

def _check_invariants(text: str) -> None:
    """
    The invariant must be expressed as psi = ln(Phi_N) (or an equivalent
    logarithmic coupling to Phi_N). Any other form is a violation.
    """
    # Normalise whitespace
    cleaned = re.sub(r'\s+', ' ', text)

    # Look for a definition of psi
    psi_defs = re.findall(r'psi\s*=\s*([^;\n]+)', cleaned, re.I)
    if not psi_defs:
        raise AssertionError("No invariant (psi) definition found.")

    for expr in psi_defs:
        # Strip possible surrounding parentheses
        expr = expr.strip()
        # Accept forms like ln(Phi_N), log(Phi_N), or ln(Phi_N) + 0*something
        # We'll parse with sympy and see if it reduces to ln(Phi_N) up to a constant factor.
        try:
            # Replace common symbols
            expr_sym = expr.replace('ln', 'log').replace('Φ_N', 'Phi_N').replace('ϕ_N', 'Phi_N')
            # Allow optional multiplicative constant before log
            expr_sym = re.sub(r'\s*\*\s*', '*', expr_sym)
            # Parse
            parsed = sp.sympify(expr_sym)
            # Check if parsed is of the form c*log(Phi_N) where c is a constant (including 1)
            if parsed.is_Mul:
                coeff, func = parsed.as_two_terms()
                if func.has(sp.log) and func.args[0].has(sp.Symbol) and str(func.args[0]) == 'Phi_N':
                    # constant coefficient allowed (including 1)
                    continue
            elif parsed.has(sp.log):
                # Could be just log(Phi_N) or log(Phi_N) + constant
                args = parsed.args if parsed.is_Add else (parsed,)
                log_terms = [a for a in args if a.has(sp.log) and a.args[0].has(sp.Symbol) and str(a.args[0]) == 'Phi_N']
                const_terms = [a for a in args if not a.has(sp.log)]
                if log_terms and all(c.is_constant() for c in const_terms):
                    continue
            # If we reach here, the expression is not a pure log(Phi_N) up to constants
            raise AssertionError(
                f"Invariant psi expression '{expr}' does not match required form ln(Phi_N) "
                "(or constant * ln(Phi_N) + constant)."
            )
        except (sp.SympifyError, AssertionError) as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"Unable to parse invariant expression '{expr}': {e}")

def _check_boundaries(text: str) -> None:
    """Must mention Functional Collapse (psi → +∞) and Functional Rigidity (psi → -∞)."""
    if "Functional Collapse" not in text or "Functional Rigidity" not in text:
        raise AssertionError("Boundary conditions (Collapse/Rigidity) not explicitly stated.")

def _check_entropy(text: str) -> None:
    """Entropy gauge must be based on Shannon entropy of context distribution."""
    if "Shannon entropy" not in text and "S_context" not in text:
        raise AssertionError("Entropy gauge term not defined via Shannon entropy.")

def _check_equations(text: str) -> None:
    """Presence of stochastic reaction‑diffusion and Omega Action."""
    required = [
        r"partial_t\s*\\mathcal{F}",   # ∂tF
        r"nabla^2",                    # diffusion
        r"Omega Action",               # action integral
        r"Mexican-hat potential",      # V(F)
    ]
    for pat in required:
        if not re.search(pat, text, re.I):
            raise AssertionError(f"Missing equation component: {pat}")

def validate_proposal(proposal_dict: dict) -> None:
    """
    Runs all rubric checks on the proposal.
    proposal_dict should contain at least the key 'text' with the full proposal.
    """
    text = proposal_dict.get("text", "")
    _check_no_boilerplate(text)
    _check_covariant_modes(text)
    _check_invariants(text)          # <-- this will fail for the current Engine output
    _check_boundaries(text)
    _check_entropy(text)
    _check_equations(text)
    # If we reach here, the proposal passes the rubric.
    return True

# Example usage (will raise AssertionError for the current Engine proposal):
if __name__ == "__main__":
    # Simulated Engine output (truncated for brevity)
    engine_text = """
    ... (the full Engine output as provided in the prompt) ...
    """
    try:
        validate_proposal({"text": engine_text})
        print("PROPOSAL PASSES OMEGA RUBRIC v26.0")
    except AssertionError as ae:
        print(f"PROPOSAL FAILS OMEGA RUBRIC v26.0: {ae}")