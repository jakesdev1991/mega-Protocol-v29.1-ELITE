# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Strictor Gate v26.0 Validator
--------------------------------------------
Checks a symbolic derivation of the Higher‑Order Lattice Polarization
correction for the fine‑structure constant.

Assumptions:
- The user supplies the expression as a SymPy expression `expr`.
- The expression should be a function of the basis symbols:
    Phi_N, Phi_Delta, Lambda, v, k (vector), plus any auxiliary symbols.
- The entropy term, if present, must be identifiable as Shannon conditional:
    H = - Σ p_i * log(p_i | condition)  (SymPy representation: -p*log(p|cond))
"""

import sympy as sp
from sympy import symbols, log, sqrt, exp, Integral, Eq

class OmegaViolation(Exception):
    pass

def validate_derivation(expr):
    """
    Main validation routine.
    Returns True if the derivation passes all Omega‑Protocol checks.
    """
    # ------------------------------------------------------------------
    # 1. Symbol inventory – look for required invariants
    # ------------------------------------------------------------------
    # Required invariant symbols (as per rubric §3)
    required = {sp.Symbol('psi'), sp.Symbol('xi_N'), sp.Symbol('xi_Delta')}
    # psi is defined as ln(Phi_N); we accept either explicit psi or ln(Phi_N)
    free_syms = set(expr.free_symbols)

    # Check for psi or its definition
    has_psi = (sp.Symbol('psi') in free_syms) or (
        any(isinstance(s, sp.Symbol) and s.name == 'Phi_N' for s in free_syms) and
        any(isinstance(node, sp.log) and node.args[0].has(sp.Symbol('Phi_N')) for node in sp.preorder_traversal(expr))
    )
    # Check for xi_N and xi_Delta (any symbols with those names)
    has_xi_N = any(s.name == 'xi_N' for s in free_syms)
    has_xi_Delta = any(s.name == 'xi_Delta' for s in free_syms)

    if not (has_psi and has_xi_N and has_xi_Delta):
        missing = []
        if not has_psi: missing.append('psi (or ln(Phi_N))')
        if not has_xi_N: missing.append('xi_N')
        if not has_xi_Delta: missing.append('xi_Delta')
        raise OmegaViolation(f"Missing Ω‑Protocol invariants: {', '.join(missing)}")

    # ------------------------------------------------------------------
    # 2. Entropy type check – must be Shannon conditional, not bosonic BE
    # ------------------------------------------------------------------
    # Detect bosonic BE occupation: 1/(exp(something)-1)
    be_pattern = lambda node: isinstance(node, sp.Pow) and \
                              isinstance(node.base, sp.Add) and \
                              any(isinstance(c, sp.exp) for c in node.args) and \
                              node.exp == -1
    # Detect Shannon conditional: -p*log(p|cond)  (we approximate as -p*log(p) with a condition symbol)
    shannon_pattern = lambda node: isinstance(node, sp.Mul) and \
                                   len(node.args) == 2 and \
                                   any(isinstance(a, sp.log) for a in node.args) and \
                                   any(not a.has(sp.exp) for a in node.args)

    be_found = any(be_pattern(n) for n in sp.preorder_traversal(expr))
    shannon_found = any(shannon_pattern(n) for n in sp.preorder_traversal(expr))

    if be_found and not shannon_found:
        raise OmegaViolation(
            "Entropy term appears as bosonic von‑Neumann/Bose‑Einstein form. "
            "Rubric §5 requires Shannon conditional entropy or topological impedance."
        )
    # If neither is found, we simply note that entropy is absent – not a violation
    # (the rubric does not mandate an entropy term in every expression,
    #  only that if present it must be of the correct type.)

    # ------------------------------------------------------------------
    # 3. Denominator positivity: 1 + (k·v)^2 ≥ 1
    # ------------------------------------------------------------------
    # Assume k and v are real vectors; we check the scalar product term.
    k = sp.Matrix(symbols('k1 k2 k3', real=True))
    v = sp.Matrix(symbols('v1 v2 v3', real=True))
    denom = 1 + (k.dot(v))**2   # SymPy expression

    # Prove global minimum >= 1
    min_val = sp.minimum(denom, (k, sp.S.NegativeInfinity, sp.S.Infinity),
                         (v, sp.S.NegativeInfinity, sp.S.Infinity))
    # SymPy may not compute directly; we instead show that the square term is >=0
    sq_term = (k.dot(v))**2
    if not sq_term >= 0:   # this will always be True for real symbols, but we keep the check
        raise OmegaViolation("Internal error: non‑real symbols detected in k·v.")
    # Since sq_term >= 0, denom >= 1 automatically.
    # Any claim of divergence or need for epsilon regularisation is rejected.
    # We scan the expression for patterns like (1 + (k·v)**2 + eps)**(-1)
    eps_pattern = lambda node: isinstance(node, sp.Pow) and \
                               node.exp == -1 and \
                               isinstance(node.base, sp.Add) and \
                               any(str(a).startswith('eps') or a.has(sp.Symbol('eps')) for a in node.args)
    if any(eps_pattern(n) for n in sp.preorder_traversal(expr)):
        raise OmegaViolation(
            "Unjustified regularisation term detected in denominator. "
            "The factor 1+(k·v)^2 is strictly ≥1 for real k,v; no divergence exists."
        )

    # ------------------------------------------------------------------
    # 4. Optional: check that Lambda > 0 (physical cutoff)
    # ------------------------------------------------------------------
    Lambda = sp.Symbol('Lambda', positive=True, real=True)
    if Lambda not in free_syms:
        # Not a hard failure, but we warn
        pass

    # If we reach here, all Ω‑Protocol checks pass.
    return True


# ----------------------------------------------------------------------
# Example usage (replace with the Engine's actual expression)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Placeholder: the Engine's claimed correction (simplified)
    Phi_N, Phi_Delta, Lambda, v_sym = symbols('Phi_N Phi_Delta Lambda v', positive=True, real=True)
    k1, k2, k3 = symbols('k1 k2 k3', real=True)
    k = sp.Matrix([k1, k2, k3])
    v = sp.Matrix([v_sym, v_sym, v_sym])   # isotropic assumption for demo
    # The Engine's integral (pretended evaluated to a number I0)
    I0 = symbols('I0')   # would be the numeric result of the integral
    # The claimed correction term:
    correction = Phi_Delta/Phi_N * (1/Lambda**2) * I0
    expr = correction   # plus alpha_0 factor omitted for brevity

    try:
        if validate_derivation(expr):
            print("Ω‑Protocol Validation: PASS")
    except OmegaViolation as e:
        print(f"Ω‑Protocol Validation: FAIL – {e}")