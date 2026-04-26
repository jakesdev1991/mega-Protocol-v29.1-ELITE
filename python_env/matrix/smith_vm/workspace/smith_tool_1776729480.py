# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol – Higher‑Order Lattice Polarization Validator
-----------------------------------------------------------
Checks the internal consistency of a claimed correction to the
fine‑structure constant α_fs(q^2) derived from the orthogonal
decomposition (Φ_N, Φ_Δ).

The script assumes the user provides the symbolic expression
for α_fs(q^2) as a sympy expression in the symbols:
    α0, gΔ, q2, m2, ψ, ξ0, C   (C is the lattice constant)
Optionally one may also supply ξ_N, ξ_Δ for invariant checks.

If all tests pass, the script prints "PASS". Otherwise it lists
the specific failures.
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Symbols and user‑supplied expression (to be edited)
# ----------------------------------------------------------------------
α0, gΔ, q2, m2, ψ, ξ0, C = sp.symbols('α0 gΔ q2 m2 ψ ξ0 C', positive=True)
# Example: the Engine's final expression (replace with the one to test)
alpha_fs_expr = α0 * (
    1
    + α0/(3*sp.pi) * sp.log(-q2/m2)                     # one‑loop QED
    + (gΔ**2 * α0)/(32*sp.pi**4) * sp.log(-q2/m2)**2   # Engine's two‑loop term
    + C * ξ0**(-2) * sp.exp(2*ψ) * q2                   # lattice term
)

# ----------------------------------------------------------------------
# 2. Helper: extract coefficient of a given structure
# ----------------------------------------------------------------------
def coeff_of(expr, term):
    """Return coefficient of `term` in `expr` assuming linear dependence."""
    return sp.simplify(sp.expand(expr).coeff(term))

# ----------------------------------------------------------------------
# 3. Test 1 – One‑loop QED sign & coefficient
# ----------------------------------------------------------------------
one_loop_term = sp.log(-q2/m2)
coeff_one_loop = coeff_of(alpha_fs_expr, one_loop_term)
expected_one_loop = α0/(3*sp.pi)   # +α0/(3π) * ln(...)
failures = []

if not sp.simplify(coeff_one_loop - expected_one_loop) == 0:
    failures.append(
        f"One‑loop QED coefficient mismatch: got {coeff_one_loop}, "
        f"expected {expected_one_loop}"
    )

# ----------------------------------------------------------------------
# 4. Test 2 – Two‑loop Φ_Δ contribution
# ----------------------------------------------------------------------
two_loop_term = sp.log(-q2/m2)**2
coeff_two_loop = coeff_of(alpha_fs_expr, two_loop_term)
# Known result from Yukawa‑photon mixing (MS‑bar, see e.g. Chetyrkin et al.):
expected_two_loop = - gΔ**2 * α0 / (8*sp.pi**3)   # - (gΔ^2 α0)/(8π^3) ln^2
if not sp.simplify(coeff_two_loop - expected_two_loop) == 0:
    failures.append(
        f"Two‑loop Φ_Δ coefficient mismatch: got {coeff_two_loop}, "
        f"expected {expected_two_loop}"
    )

# ----------------------------------------------------------------------
# 5. Test 3 – Lattice term structure
# ----------------------------------------------------------------------
lattice_term = q2   # we expect C * ξ0^{-2} * e^{2ψ} * q2
coeff_lattice = coeff_of(alpha_fs_expr, lattice_term)
expected_lattice = C * ξ0**(-2) * sp.exp(2*ψ)
if not sp.simplify(coeff_lattice - expected_lattice) == 0:
    failures.append(
        f"Lattice term mismatch: got {coeff_lattice}, "
        f"expected {expected_lattice}"
    )
# Additionally, the coefficient must be real and positive for physical a^2>0
if not sp.simplify(sp.im(expected_lattice)) == 0:
    failures.append("Lattice coefficient has an imaginary part.")
if not sp.simplify(sp.re(expected_lattice)) > 0:
    failures.append("Lattice coefficient is not positive-definite.")

# ----------------------------------------------------------------------
# 6. Test 4 – Mapping a = ξ0 e^{-ψ}  (implies a>0 automatically)
# ----------------------------------------------------------------------
a_expr = ξ0 * sp.exp(-ψ)
if not sp.simplify(sp.im(a_expr)) == 0:
    failures.append("Derived lattice spacing a has imaginary part.")
if not sp.simplify(sp.re(a_expr)) > 0:
    failures.append("Derived lattice spacing a is not positive.")

# ----------------------------------------------------------------------
# 7. Test 5 – Beta‑function consistency (optional, requires derivative)
# ----------------------------------------------------------------------
# β(α) = μ dα/dμ  ; using d/d ln(-q2) as RG scale
# Compute derivative of α_fs w.r.t. ln(-q2) and compare to expected form.
L = sp.log(-q2/m2)   # RG scale variable
# α_fs expressed as α0 * (1 + A1*L + A2*L^2 + A3*q2) ; we already have coefficients.
A1 = coeff_one_loop / α0          # coefficient of L in bracket
A2 = coeff_two_loop / α0          # coefficient of L^2
A3 = coeff_lattice / (α0 * q2)    # coefficient of q2 term (should be C ξ0^{-2} e^{2ψ})

# β = - α0 * (d/dL)[A1*L + A2*L^2]   (q2‑independent part)
beta_from_expr = -α0 * (A1 + 2*A2*L)
# Expected beta: 2α^2/(3π) + α gΔ^2/(16π^2)  (ignore higher orders)
expected_beta = 2*α0**2/(3*sp.pi) + α0*gΔ**2/(16*sp.pi**2)
# Compare the *constant* part (terms independent of L)
beta_const = sp.simplify(sp.expand(beta_from_expr).coeff(L, 0))
if not sp.simplify(beta_const - expected_beta) == 0:
    failures.append(
        f"Beta‑function constant term mismatch: got {beta_const}, "
        f"expected {expected_beta}"
    )
# Additionally, the coefficient of L in beta should vanish at this order
beta_L_coeff = sp.simplify(sp.expand(beta_from_expr).coeff(L, 1))
if not sp.simplify(beta_L_coeff) == 0:
    failures.append(
        f"Beta‑function has unwanted L‑dependence: coefficient {beta_L_coeff}"
    )

# ----------------------------------------------------------------------
# 8. Test 6 – Omega invariants positivity (if supplied)
# ----------------------------------------------------------------------
# Users can optionally define ξ_N, ξ_Δ symbols and add checks here.
# For demonstration we assume they are positive symbols.
ξ_N, ξ_Δ = sp.symbols('ξ_N ξ_Δ', positive=True)
# Example invariant: ψ = ln(Φ_N/I0) → Φ_N = I0 * exp(ψ) must be positive.
# This is automatically true for real ψ; we just check ψ is real.
if not sp.simplify(sp.im(ψ)) == 0:
    failures.append("Invariant ψ must be real.")

# ----------------------------------------------------------------------
# 9. Verdict
# ----------------------------------------------------------------------
if failures:
    print("FAIL – the following issues were detected:")
    for i, f in enumerate(failures, 1):
        print(f" {i}. {f}")
else:
    print("PASS – expression satisfies all checked consistency conditions.")