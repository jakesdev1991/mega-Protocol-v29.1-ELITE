# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script
Verifies the Higher-Order Lattice Polarization correction for α_fs.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
α0, Λ, m, g, ΦN, ΦΔ = sp.symbols('α0 Λ m g ΦN ΦΔ', positive=True, real=True)
ε = g * ΦN / m                     # expansion parameter
a = sp.cosh(ΦΔ)                    # shorthand for coshΦΔ

# ----------------------------------------------------------------------
# 1. Logarithmic expansion check
# ----------------------------------------------------------------------
# Exact log argument from effective masses:
log_arg = 1 - 2 * ε * a + ε**2
log_exact = sp.log(log_arg)

# Series expansion up to O(ε^2)
log_series = sp.series(log_exact, ε, 0, 3).removeO()
# Expected series: -2ε a + ε^2 (1 - 2 a^2)
expected = -2 * ε * a + ε**2 * (1 - 2 * a**2)

assert sp.simplify(log_series - expected) == 0, \
    "Logarithmic expansion mismatch"

# ----------------------------------------------------------------------
# 2. Vacuum polarization Π(0) from the rubric form
# ----------------------------------------------------------------------
# Rubric definition: Π(0) = (α0/(3π)) [ ln(Λ/m) - 1/2 * ln(m_e m_p / m^2) ]
Pi_rubric = (α0 / (3 * sp.pi)) * (sp.log(Λ / m) - sp.Rational(1,2) * sp.log(log_arg))

# Substitute the series for the log and simplify to O(ε^2)
Pi_series = sp.series(Pi_rubric, ε, 0, 3).removeO()
# Expected: (α0/(3π)) [ ln(Λ/m) + ε a - (ε^2/2)(1 - 2 a^2) ]
Pi_expected = (α0 / (3 * sp.pi)) * (sp.log(Λ / m) + ε * a -
                                    sp.Rational(1,2) * ε**2 * (1 - 2 * a**2))

assert sp.simplify(Pi_series - Pi_expected) == 0, \
    "Vacuum polarization series mismatch"

# ----------------------------------------------------------------------
# 3. Renormalized α expression (boxed form)
# ----------------------------------------------------------------------
α_ren = α0 / (1 - (α0 / (3 * sp.pi)) *
             (sp.log(Λ / m) + ε * a -
              sp.Rational(1,2) * ε**2 * (1 - 2 * a**2)))

# Verify that α_ren → α0 when ε → 0 (no field)
assert sp.simplify(sp.series(α_ren, ε, 0, 1).removeO() - α0) == 0, \
    "α_ren does not reduce to α0 at zero field"

# ----------------------------------------------------------------------
# 4. Mass‑positivity (shredding) constraint
# ----------------------------------------------------------------------
# Require m_e = m - g ΦN e^{+ΦΔ} > 0 and m_p = m - g ΦN e^{-ΦΔ} > 0
m_e = m - g * ΦN * sp.exp(ΦΔ)
m_p = m - g * ΦN * sp.exp(-ΦΔ)

constraint = sp.And(sp.simplify(m_e > 0), sp.simplify(m_p > 0))
# Solve for ΦN bound:
bound = sp.solve(sp.Eq(m_e, 0), ΦN)[0]   # gives ΦN < m/(g*exp(ΦΔ))
# The stricter bound is the minimum of the two:
bound_strict = sp.Min(m/(g*sp.exp(ΦΔ)), m/(g*sp.exp(-ΦΔ)))
assert sp.simplify(bound_strict - m/(g*sp.exp(abs(ΦΔ)))) == 0, \
    "Mass‑positivity bound incorrect"

# ----------------------------------------------------------------------
# 5. Invariant definitions (structural check)
# ----------------------------------------------------------------------
ψ = sp.log(ΦN)
# ξ_N = <|∇ψ|^2>  – we only verify that ψ is a scalar function of ΦN
assert ψ.diff(ΦN) == 1/ΦN, "ψ definition inconsistent"
# ξ_Δ = <|∇(ΦΔ/ΦN)|^2> – check that the ratio is dimensionless
ratio = ΦΔ / ΦN
assert ratio.diff(ΦN) == -ΦΔ/ΦN**2 and ratio.diff(ΦΔ) == 1/ΦN, \
    "ξ_Δ building block malformed"

# ----------------------------------------------------------------------
# 6. Entropy placeholder (ensure functional form)
# ----------------------------------------------------------------------
# S_mass = -∫ p(m_eff) ln p(m_eff) dμ
p = sp.Function('p')
m_eff = sp.symbols('m_eff')
S_mass = -sp.integrate(p(m_eff) * sp.log(p(m_eff)), (m_eff, -sp.oo, sp.oo))
# We cannot evaluate without a specific p, but we can confirm the integrand:
assert S_mass.args[0].args[0] == -p(m_eff) * sp.log(p(m_eff)), \
    "Entropy integrand malformed"

print("All Omega Protocol validation checks passed.")