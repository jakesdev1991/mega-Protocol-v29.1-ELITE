# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validator for the Higher‑Order Lattice Polarization
correction to the fine‑structure constant.

Checks:
  - Correct 𝒪(ε²) term in ln(m_e m_p / m²)
  - Consistency of the final α_ren series expansion
  - (Optional) Presence of required invariant/entropy symbols
"""

import sympy as sp
import re

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
α0, Λ, m, g, ΦN, ΦΔ = sp.symbols('α0 Λ m g ΦN ΦΔ', positive=True)
ε = g*ΦN/m  # expansion parameter

# ----------------------------------------------------------------------
# 1. Effective masses and their product ratio
# ----------------------------------------------------------------------
m_e = m - g*ΦN*sp.exp( ΦΔ)   # m - g Φ⁺
m_p = m - g*ΦN*sp.exp(-ΦΔ)   # m - g Φ⁻
ratio = sp.simplify(m_e * m_p / m**2)   # should be 1 - 2ε coshΦΔ + ε²
print("Ratio m_e m_p / m² =", ratio)

# ----------------------------------------------------------------------
# 2. Logarithm expansion to O(ε²)
# ----------------------------------------------------------------------
L = sp.log(ratio)
L_series = sp.series(L, ε, 0, 3).removeO()   # up to ε²
print("\nSeries expansion of ln(m_e m_p/m²):")
print(sp.simplify(L_series))
print("\nExpected: -2ε*cosh(ΦΔ) + ε²*(1 - 2*cosh²(ΦΔ))")
expected_L = -2*ε*sp.cosh(ΦΔ) + ε**2 * (1 - 2*sp.cosh(ΦΔ)**2)
print("Match?", sp.simplify(L_series - expected_L) == 0)

# ----------------------------------------------------------------------
# 3. Vacuum polarization Π(0) and α_ren
# ----------------------------------------------------------------------
Pi0 = (α0/(3*sp.pi)) * (sp.log(Λ/m) - L/2)
Pi0_series = sp.series(Pi0, ε, 0, 3).removeO()
print("\nSeries expansion of Π(0):")
print(sp.simplify(Pi0_series))

# α_ren = α0 / (1 - Π(0))
α_ren = α0 / (1 - Pi0)
α_series = sp.series(α_ren, ε, 0, 3).removeO()
print("\nSeries expansion of α_ren/α0:")
print(sp.simplify(α_series/α0))
# Expected: 1 + (α0/3π)[ ln(Λ/m) + ε coshΦΔ - ε²/2 (1-2cosh²ΦΔ) ] + O(ε³)
expected_alpha = 1 + (α0/(3*sp.pi)) * (
    sp.log(Λ/m) + ε*sp.cosh(ΦΔ) - ε**2/2 * (1 - 2*sp.cosh(ΦΔ)**2)
)
print("\nExpected α_ren/α0 series:")
print(sp.simplify(expected_alpha))
print("Match?", sp.simplify(α_series/α0 - expected_alpha) == 0)

# ----------------------------------------------------------------------
# 4. Optional invariant/entropy checker (placeholder)
# ----------------------------------------------------------------------
def check_symbols(expr_str, required):
    """Return True if all substrings in required appear in expr_str."""
    return all(sym in expr_str for sym in required)

# Example: if you have the final LaTeX or sympy expression as a string:
expr_str = r"\alpha_{\text{ren}} = \alpha_0 \left[ 1 - \frac{\alpha_0}{3\pi} \left( \ln\frac{\Lambda}{m} + \frac{g\Phi_N}{m}\cosh\Phi_\Delta - \frac12\left(\frac{g\Phi_N}{m}\right)^2\!\left(1 - 2\cosh^2\Phi_\Delta\right) \right) \right]^{-1}"
required_invariants = [r"\psi", r"\xi_N", r"\xi_\Delta"]
required_entropy    = [r"S_{\text{mass}}", r"Z_{\text{top}}"]  # examples

print("\n--- Invariant / Entropy presence check (informational) ---")
print("Invariants present?", check_symbols(expr_str, required_invariants))
print("Entropy term present?", check_symbols(expr_str, required_entropy))

# ----------------------------------------------------------------------
# End of script
# ----------------------------------------------------------------------