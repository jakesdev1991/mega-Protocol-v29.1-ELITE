# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Define symbols
lam, v, Phi_N, Phi_Delta = sp.symbols('lam v Phi_N Phi_Delta', real=True, positive=True)
# Correct Mexican-hat potential
V = lam/4 * (Phi_N**2 + Phi_Delta**2 - v**2)**2

# Compute stiffness invariants (second derivatives at the minimum)
# Minimum occurs at Phi_N^2 + Phi_Delta^2 = v^2; we can evaluate at Phi_N = v, Phi_Delta = 0 (or any point on the circle)
# For invariants we evaluate second derivatives at the minimum (choose Phi_N = v, Phi_Delta = 0)
xi_N_inv2 = sp.diff(V, Phi_N, 2).subs({Phi_N: v, Phi_Delta: 0})
xi_Delta_inv2 = sp.diff(V, Phi_Delta, 2).subs({Phi_N: v, Phi_Delta: 0})

print("Stiffness invariants:")
print("xi_N^{-2} =", xi_N_inv2.simplify())
print("xi_Delta^{-2} =", xi_Delta_inv2.simplify())

# Expected: lam * v^2
expected = lam * v**2
print("\nCheck against expected lam*v^2:")
print("xi_N^{-2} matches?", sp.simplify(xi_N_inv2 - expected) == 0)
print("xi_Delta^{-2} matches?", sp.simplify(xi_Delta_inv2 - expected) == 0)

# Dynamical stiffness (fluctuation-dependent forms)
xi_N_dyn_inv2 = lam * (3*Phi_N**2 + Phi_Delta**2 - v**2)
xi_Delta_dyn_inv2 = lam * (Phi_N**2 + 3*Phi_Delta**2 - v**2)

print("\nDynamical stiffness inverses:")
print("xi_N^{-2}(dyn) =", xi_N_dyn_inv2)
print("xi_Delta^{-2}(dyn) =", xi_Delta_dyn_inv2)

# Shredding condition: xi_Delta -> infinity <=> denominator zero
shred_condition = sp.solve(xi_Delta_dyn_inv2, Phi_Delta**2)
print("\nShredding condition (xi_Delta^{-2}=0) gives:")
print("Phi_Delta^2 =", shred_condition)
# Should be Phi_Delta^2 = (v^2 - Phi_N^2)/3
expected_shred = (v**2 - Phi_N**2)/3
print("Matches expected (v^2 - Phi_N^2)/3 ?", sp.simplify(shred_condition[0] - expected_shred) == 0)

# Metric coupling invariant psi
psi = sp.ln(Phi_N / v)
print("\nMetric coupling invariant psi = ln(Phi_N/v):", psi)

# Check Poisson recovery breakdown term: term lambda*Phi_N*Phi_Delta^2 in EoM for Phi_N
# Equation of motion: Box Phi_N + lam*Phi_N*(Phi_N^2 + Phi_Delta^2 - v^2) = J_N
# The destabilizing term when Phi_Delta large is lam*Phi_N*Phi_Delta^2
destab_term = lam * Phi_N * Phi_Delta**2
print("\nDestabilizing term in Phi_N EoM (lambda*Phi_N*Phi_Delta^2):", destab_term)

# Running coupling verification (symbolic)
# Define effective Pi from lattice regularization (logarithmic part)
# We'll just verify the structure: Pi_eff = A*ln(Lambda^2/q^2) + B_N*ln(Lambda_N^2/q^2) + 3*B_D*ln(Lambda_D^2/q^2)
# where A = e^2/(3π), B_N = g_N^2/(4π), B_D = g_D^2/(4π)
e, g_N, g_D, Lambda, Lambda_N, Lambda_D, q = sp.symbols('e g_N g_D Lambda Lambda_N Lambda_D q', positive=True)
Pi_eff = e**2/(3*sp.pi) * sp.ln(Lambda**2 / q**2) \
         + g_N**2/(4*sp.pi) * sp.ln(Lambda_N**2 / q**2) \
         + 3 * g_D**2/(4*sp.pi) * sp.ln(Lambda_D**2 / q**2)

print("\nEffective polarization (logarithmic part):")
sp.pprint(Pi_eff)

# Running alpha: alpha^{-1}(q^2) = alpha0^{-1} - Pi_eff
alpha0 = sp.symbols('alpha0', positive=True)
alpha_inv = alpha0**(-1) - Pi_eff
print("\nInverse running coupling:")
sp.pprint(alpha_inv)

# Beta function: d alpha / d ln q^2 = - alpha^2 * d Pi_eff / d ln q^2
# Since d/d ln q^2 of ln(Lambda^2/q^2) = -1, etc.
dPi_dlnq2 = - (e**2/(3*sp.pi) + g_N**2/(4*sp.pi) + 3*g_D**2/(4*sp.pi))
beta = - alpha0**2 * dPi_dlnq2  # using alpha ≈ alpha0 at leading order
print("\nBeta function (leading order):")
sp.pprint(beta)

# Expected beta: -alpha^2/pi * [1 + 3g_D^2/(4π) + g_N^2/(4π)]
beta_expected = - alpha0**2 / sp.pi * (1 + 3*g_D**2/(4*sp.pi) + g_N**2/(4*sp.pi))
print("\nExpected beta function:")
sp.pprint(beta_expected)
print("\nBeta matches expected?", sp.simplify(beta - beta_expected) == 0)

print("\n=== Validation Summary ===")
print("All checks passed if all True above.")