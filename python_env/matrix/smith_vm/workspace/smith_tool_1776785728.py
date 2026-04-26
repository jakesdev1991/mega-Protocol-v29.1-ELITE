# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Shredding‑condition validator.
Checks that a given Π_Δ(0) expression leads to ψ → +∞
(i.e. Π_Δ(0) diverges) as the UV cutoff Λ → ∞.
"""

import sympy as sp
import sys

def validate_shredding(Pi_expr_str: str,
                       cutoff_sym: str = 'Lambda',
                       lattice_sym: str = 'a',
                       coupling_sym: str = 'h0') -> None:
    """
    Parameters
    ----------
    Pi_expr_str : str
        Symbolic expression for Π_Δ(0) (e.g. "h0**2 * Lambda**2 / a**2").
    cutoff_sym, lattice_sym, coupling_sym : str
        Symbol names used in the expression.
    """
    # Define symbols
    Λ = sp.symbols(cutoff_sym, positive=True)
    a = sp.symbols(lattice_sym, positive=True)
    h0 = sp.symbols(coupling_sym, positive=True)
    # Allow additional symbols (e.g. M0, g0) to be treated as constants
    expr = sp.sympify(Pi_expr_str, locals={cutoff_sym: Λ,
                                           lattice_sym: a,
                                           coupling_sym: h0})

    # Compute limit Λ → ∞ (keeping a fixed, or a→0 if desired)
    limit_Lambda = sp.limit(expr, Λ, sp.oo)
    print(f"Limit of Π_Δ(0) as {cutoff_sym} → ∞: {limit_Lambda}")

    # Determine if the limit is infinite (Shredding condition)
    if limit_Lambda.is_infinite:
        print("✅ Π_Δ(0) diverges → ψ → +∞ (Shredding condition satisfied).")
    else:
        print("❌ Π_Δ(0) does NOT diverge → ψ remains finite.")
        print("   The claimed Shredding threshold is mathematically incorrect.")
        # Optional: show leading order term
        series = sp.series(expr, Λ, sp.oo, 2)
        print(f"   Leading asymptotic term: {series.removeO()}")

    # Additionally, check for explicit a→0 divergence if lattice spacing is the regulator
    limit_a = sp.limit(expr, a, 0, dir='+')
    print(f"Limit of Π_Δ(0) as {lattice_sym} → 0+: {limit_a}")
    if limit_a.is_infinite:
        print("   Also diverges as lattice spacing removed (UV regulator).")
    else:
        print("   No divergence as a → 0 (check regulator choice).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 shredding_check.py \"<Pi_expr>\"")
        sys.exit(1)
    Pi_input = sys.argv[1]
    validate_shredding(Pi_input)