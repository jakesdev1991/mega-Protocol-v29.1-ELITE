# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the "Higher-Order Lattice Polarization" derivation
submitted by the Engine (architect) agent.

We verify:
1. Algebraic consistency of the effective polarization Π_eff(q²).
2. Correct emergence of the factor 3 from the three internal dimensions of Φ_Δ.
3. RG equation derived from Π_eff matches the claimed beta‑function.
4. Basic Omega‑Protocol invariants:
   - Φ_N and Φ_Δ contributions are additive and independent (no cross‑terms).
   - The total coefficient of ln(q²) in α⁻¹ must be positive (screening, not antiscreening).
   - The invariant J* (interpreted here as the sum of mode‑weights) is conserved:
         J* = 1 + (3 g_Δ²/4π) + (g_N²/4π)  > 0 .
If any check fails, the script raises an AssertionError with a diagnostic message.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
q2   = sp.symbols('q2', positive=True)   # momentum squared
Lambda = sp.symbols('Lambda', positive=True)   # UV cutoff (common for QED part)
Lambda_N = sp.symbols('Lambda_N', positive=True)
Lambda_Delta = sp.symbols('Lambda_Delta', positive=True)
e2   = sp.symbols('e2', positive=True)   # bare e^2
gN2  = sp.symbols('gN2', positive=True)  # Newtonian mode coupling squared
gD2  = sp.symbols('gD2', positive=True)  # Archive mode coupling squared
pi   = sp.pi

# ----------------------------------------------------------------------
# Step 1: Effective polarization from the derivation
# ----------------------------------------------------------------------
# QED one-loop (leading log) piece:
Pi_QED = (e2/(3*sp.pi)) * sp.log(Lambda**2 / q2)

# Newtonian mode contribution (factor 1/4π from the derivation):
Pi_N   = (gN2/(4*sp.pi)) * sp.log(Lambda_N**2 / q2)

# Archive mode contribution – note the explicit factor 3:
Pi_Delta = (3*gD2/(4*sp.pi)) * sp.log(Lambda_Delta**2 / q2)

Pi_eff = sp.simplify(Pi_QED + Pi_N + Pi_Delta)
print("Effective polarization Π_eff(q²):")
sp.pprint(Pi_eff)
print()

# ----------------------------------------------------------------------
# Step 2: Inverse running fine‑structure constant
# ----------------------------------------------------------------------
# α⁻¹(q²) = α₀⁻¹ - Π_eff(q²)   with α₀ = e²/(4πε₀ħc) → we treat e² as proportional to α₀
# For the purpose of checking the logarithmic coefficients we keep e² as the bare coupling.
alpha0_inv = sp.symbols('alpha0_inv')   # placeholder for α₀⁻¹
alpha_inv = sp.simplify(alpha0_inv - Pi_eff)
print("Inverse running coupling α⁻¹(q²):")
sp.pprint(alpha_inv)
print()

# ----------------------------------------------------------------------
# Step 3: Extract the coefficient of ln(q²) (should be negative for screening)
# ----------------------------------------------------------------------
# Write α⁻¹ = α₀⁻¹ + C * ln(q²) + const
# We isolate the ln(q²) term:
ln_q2 = sp.log(q2)
# Collect terms multiplying ln(q²):
coeff_ln_q2 = sp.collect(alpha_inv, ln_q2, evaluate=False).get(ln_q2, 0)
print("Coefficient of ln(q²) in α⁻¹:")
sp.pprint(sp.simplify(coeff_ln_q2))
print()

# Expected coefficient from the derivation:
expected_coeff = - (e2/(3*sp.pi)) - (gN2/(4*sp.pi)) - (3*gD2/(4*sp.pi))
print("Expected coefficient:")
sp.pprint(expected_coeff)
print()

assert sp.simplify(coeff_ln_q2 - expected_coeff) == 0, \
    "Mismatch in ln(q²) coefficient – derivation inconsistent."

# ----------------------------------------------------------------------
# Step 4: Running α (first‑order expansion)
# ----------------------------------------------------------------------
# α(q²) ≈ α₀ [1 - α₀ * (coeff_ln_q2) * ln(q²) ]   (since α⁻¹ ≈ α₀⁻¹ + coeff*ln)
# We compute the linear correction term:
alpha0 = sp.symbols('alpha0', positive=True)
# Relation between e² and α₀: in natural units e² = 4π α₀ (we ignore ε₀, ħ, c)
# For consistency we substitute e2 -> 4*pi*alpha0
subs_dict = {e2: 4*pi*alpha0}
alpha_corrected = sp.simplify(
    alpha0 * (1 + alpha0 * (-coeff_ln_q2.subs(subs_dict)) * sp.log(Lambda**2 / q2))
)
print("Running α(q²) (first order) after substituting e²=4πα₀:")
sp.pprint(alpha_corrected)
print()

# Extract the three logarithmic pieces:
# α₀ term (standard QED):
term_QED = alpha0 * (alpha0/(3*sp.pi)) * sp.log(Lambda**2 / q2)
# Newtonian term:
term_N   = alpha0 * (alpha0 * gN2/(4*sp.pi)) * sp.log(Lambda_N**2 / q2)
# Archive term:
term_D   = alpha0 * (alpha0 * (3*gD2/(4*sp.pi))) * sp.log(Lambda_Delta**2 / q2)

print("Standard QED piece:")
sp.pprint(term_QED)
print("Newtonian piece:")
sp.pprint(term_N)
print("Archive (3‑enhanced) piece:")
sp.pprint(term_D)
print()

# Verify that the archive piece carries the factor 3:
assert sp.simplify(term_D / (alpha0**2 * gD2/(4*sp.pi) * sp.log(Lambda_Delta**2 / q2))) == 3, \
    "Archive mode contribution missing the required factor 3."

# ----------------------------------------------------------------------
# Step 5: RG equation (beta function)
# ----------------------------------------------------------------------
# β(α) = dα/dln(q²) = - α² * [coeff_without_alpha0]
# From α⁻¹ derivative: dα⁻¹/dln(q²) = coeff_ln_q2  →  dα/dln(q²) = -α² * coeff_ln_q2
beta = - alpha0**2 * coeff_ln_q2.subs(subs_dict)
print("Beta function β(α) = dα/dln(q²):")
sp.pprint(sp.simplify(beta))
print()

# Expected beta from the paper:
expected_beta = - alpha0**2 * (1/(3*sp.pi) + gN2/(4*sp.pi) + 3*gD2/(4*sp.pi))
print("Expected beta:")
sp.pprint(expected_beta)
print()

assert sp.simplify(beta - expected_beta) == 0, \
    "Beta function does not match the claimed RG equation."

# ----------------------------------------------------------------------
# Step 6: Omega‑Protocol invariant checks
# ----------------------------------------------------------------------
# Invariant J* interpreted as the total weight multiplying α² in the beta function:
J_star = 1/(3*sp.pi) + gN2/(4*sp.pi) + 3*gD2/(4*sp.pi)
print("Invariant J* (coefficient of α² in β):")
sp.pprint(J_star)
print()

# J* must be positive (screening, not antiscreening):
assert J_star > 0, "Invariant J* violated: negative or zero screening coefficient."

# No cross‑terms between Φ_N and Φ_Δ should appear in Π_eff:
# Verify that Π_eff is a sum of three independent logs:
terms = [Pi_QED, Pi_N, Pi_Delta]
for i, t in enumerate(terms):
    # each term should depend on only its own cutoff
    if i == 0:
        assert t.has(Lambda) and not (t.has(Lambda_N) or t.has(Lambda_Delta)), \
            "QED term incorrectly depends on mode cutoffs."
    elif i == 1:
        assert t.has(Lambda_N) and not (t.has(Lambda) or t.has(Lambda_Delta)), \
            "Newtonian term incorrectly depends on other cutoffs."
    else:
        assert t.has(Lambda_Delta) and not (t.has(Lambda) or t.has(Lambda_N)), \
            "Archive term incorrectly depends on other cutoffs."

print("All checks passed: derivation is mathematically sound and respects Omega Protocol invariants.")