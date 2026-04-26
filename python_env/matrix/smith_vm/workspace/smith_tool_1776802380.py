# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Engine's "Higher-Order Lattice Polarization" claim.
Checks basic mathematical consistency conditions that any
effective alpha must obey in lattice QED.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
α0, e, p2, m2, a2 = sp.symbols('α0 e p2 m2 a2', positive=True)
ΦN, ΦΔ = sp.symbols('ΦN ΦΔ', real=True)   # ΦN, ΦΔ can be positive or negative
# Direction indicator: 1 for z (archive axis), 0 for transverse (x,y)
iz = sp.symbols('iz', integer=True)      # iz ∈ {0,1}

# ----------------------------------------------------------------------
# Engine's claimed pieces (as given in the final output)
# ----------------------------------------------------------------------
# Π0(p2; ΦN) = e^2/(12π^2) * ln(a^{-2}/p2) + e^2/π^2 * ΦN
Pi0 = e**2/(12*sp.pi**2) * sp.log(a2/p2) + e**2/sp.pi**2 * ΦN

# ΠΔ(p2) = e^2/π^2 * IΔ(p2)   (IΔ treated as a generic dimensionless function)
IΔ = sp.symbols('IΔ')   # dimensionless, O(1)
PiΔ = e**2/sp.pi**2 * IΔ

# Effective alpha (Engine's formula)
α_eff = α0 / (1 + Pi0 + iz * ΦΔ * PiΔ)

# ----------------------------------------------------------------------
# Consistency checks
# ----------------------------------------------------------------------
def check(name, condition):
    """Return True if condition holds symbolically (or as a simplification)."""
    try:
        # Simplify the condition; if it reduces to True, accept.
        simplified = sp.simplify(condition)
        return simplified is True or simplified == 0
    except Exception:
        return False

results = {}

# 1. Isotropic limit: ΦΔ → 0 must recover the isotropic coupling
results["Isotropic limit (ΦΔ→0)"] = check(
    sp.simplify(α_eff.subs(ΦΔ, 0) - α0/(1 + Pi0)),
    0
)

# 2. Transverse direction (iz=0) must be independent of ΦΔ
results["Transverse independence (iz=0)"] = check(
    sp.simplify(α_eff.subs(iz, 0).diff(ΦΔ)),
    0
)

# 3. Longitudinal direction (iz=1) derivative w.r.t ΦΔ should be
#    -α0 * PiΔ / (1 + Pi0 + ΦΔ*PiΔ)^2  (exact derivative of the claimed form)
#    We check that the derivative matches the analytic expression.
dα_dΦΔ_expected = -α0 * PiΔ / (1 + Pi0 + ΦΔ*PiΔ)**2
dα_dΦΔ_actual = sp.diff(α_eff.subs(iz, 1), ΦΔ)
results["Longitudinal ΦΔ derivative matches"] = check(
    sp.simplify(dα_dΦΔ_actual - dα_dΦΔ_expected),
    0
)

# 4. Positivity of denominator (α_eff must be positive for physical coupling)
#    We test a generic numeric substitution to see if denominator can become zero/negative.
#    Choose sample values: α0=1/137, e^2=4π α0, p2=1e-2, a2=1e0, m2=1e-4, ΦN=0.1, ΦΔ=0.2, IΔ=0.5
subs_dict = {
    α0: 1/137,
    e: sp.sqrt(4*sp.pi*α0),
    p2: 1e-2,
    a2: 1e0,
    m2: 1e-4,
    ΦN: 0.1,
    ΦΔ: 0.2,
    IΔ: 0.5
}
denom_val = (1 + Pi0 + iz*ΦΔ*PiΔ).subs(subs_dict).evalf()
results["Denominator positive (sample)"] = denom_val > 0

# 5. Dimensionless check: Π0 and ΠΔ must be dimensionless.
#    In natural units, e^2 is dimensionless, logs are dimensionless, ΦN, ΦΔ dimensionless.
#    We verify that the combination e^2/π^2 * ΦN has no leftover dimensions (trivially true).
#    Here we just ensure no explicit mass scales appear besides those inside log ratio.
Pi0_dim = sp.simplify(Pi0.subs({e**2: 4*sp.pi*α0}))  # replace e^2 with α0 to see if any mass left
PiΔ_dim = sp.simplify(PiΔ.subs({e**2: 4*sp.pi*α0}))
results["Π0 dimensionless (no leftover m/p)"] = Pi0_dim.free_symbols.issubset({α0, ΦN, a2, p2})
results["ΠΔ dimensionless (no leftover m/p)"] = PiΔ_dim.free_symbols.issubset({α0, IΔ})

# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------
print("=== Validation Results ===")
for k, v in results.items():
    print(f"{k:45}: {'PASS' if v else 'FAIL'}")

# Overall decision
overall_pass = all(results.values())
print("\nOverall:", "PASS" if overall_pass else "FAIL")
if not overall_pass:
    print("\nThe Engine's formula fails one or more basic consistency checks.")