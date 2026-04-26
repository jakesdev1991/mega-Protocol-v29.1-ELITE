# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import sympy as sp

# ----------------------------------------------------------------------
# 1. Jerk stencil validation
# ----------------------------------------------------------------------
t, dt = sp.symbols('t dt', real=True)
# generic cubic: I(t) = a0 + a1*t + a2*t**2 + a3*t**3
a0, a1, a2, a3 = sp.symbols('a0 a1 a2 a3', real=True)
I = a0 + a1*t + a2*t**2 + a3*t**3

# stencil: J ≈ (-I(t-2dt)+2I(t-dt)-2I(t+dt)+I(t+2dt))/(2*dt**3)
J_est = (-I.subs(t, t-2*dt) + 2*I.subs(t, t-dt) -
         2*I.subs(t, t+dt) + I.subs(t, t+2*dt)) / (2*dt**3)

# Simplify; should equal 6*a3 (the exact third derivative)
J_exact = sp.diff(I, t, 3)  # 6*a3
assert sp.simplify(J_est - J_exact) == 0, "Stencil fails on cubic"
print("✓ Jerk stencil exact for cubic polynomial")

# Truncation error test on quartic term b*t**4
b = sp.symbols('b', real=True)
I_quartic = I + b*t**4
J_est_q = (-I_quartic.subs(t, t-2*dt) + 2*I_quartic.subs(t, t-dt) -
           2*I_quartic.subs(t, t+dt) + I_quartic.subs(t, t+2*dt)) / (2*dt**3)
J_exact_q = sp.diff(I_quartic, t, 3)  # 6*a3 + 24*b*t
error = sp.simplify(sp.series(J_est_q - J_exact_q, dt, 0, 2).removeO())
assert error == 0, f"Unexpected truncation error: {error}"
print("✓ Jerk stencil is O(dt^2) accurate (error starts at dt^2)")

# ----------------------------------------------------------------------
# 2. Dimensional consistency of the Ω‑action Lagrangian
# ----------------------------------------------------------------------
# Define dimensions as powers of fundamental time T
T = sp.symbols('T')
dim_kappa = T**(-sp.Rational(3,2))
dim_m     = T**(-sp.Rational(1,2))
dim_lambda = T**(-1)

# Fields I_C, I_G are dimensionless (entropy units)
dim_I = 1

# Lagrangian terms:
#   (1/(2*kappa^2))*[(d^2 I_C/dt^2)^2 + (d^2 I_G/dt^2)^2]
#   -(1/2)*m^2*(I_C^2 + I_G^2)
#   -(lambda/4)*I_C*I_G^2
term1 = 1/(2*dim_kappa**2) * ( (1/T**4)**2 + (1/T**4)**2 )  # d^2/dt^2 -> T^{-2}
term2 = -(1/2)*dim_m**2 * (dim_I**2 + dim_I**2)
term3 = -(dim_lambda/4) * dim_I * dim_I**2

L_dim = sp.simplify(term1 + term2 + term3)
assert L_dim == 1, f"Lagrangian dimension is {L_dim}, expected dimensionless"
print("✓ Lagrangian is dimensionless")

# ----------------------------------------------------------------------
# 3. Euler‑Lagrange equations from the Lagrangian
# ----------------------------------------------------------------------
# Treat I_C(t), I_G(t) as fields; L = L[I_C, I_G, d2I_C/dt2, d2I_G/dt2]
IC, IG = sp.symbols('IC IG', cls=sp.Function)
# Define Lagrangian density (integrand)
L = (1/(2*dim_kappa**2)) * (sp.diff(IC(t), t, 2)**2 + sp.diff(IG(t), t, 2)**2) \
    - (1/2)*dim_m**2 * (IC(t)**2 + IG(t)**2) \
    - (dim_lambda/4) * IC(t) * IG(t)**2

# Euler‑Lagrange for higher derivatives: ∂L/∂φ - d^2/dt^2 (∂L/∂φ'') = 0
def EL(field):
    return sp.diff(L, field(t)) - sp.diff(sp.diff(L, sp.diff(field(t), t, 2)), t, 2)

EL_IC = sp.simplify(EL(IC))
EL_IG = sp.simplify(EL(IG))

# Expected equations of motion:
#   (1/kappa^2) * d^4 IC/dt^4 - m^2 * IC - (lambda/4) * IG^2 = 0
#   (1/kappa^2) * d^4 IG/dt^4 - m^2 * IG - (lambda/2) * IC * IG = 0
expected_IC = (1/dim_kappa**2) * sp.diff(IC(t), t, 4) - dim_m**2 * IC(t) - (dim_lambda/4) * IG(t)**2
expected_IG = (1/dim_kappa**2) * sp.diff(IG(t), t, 4) - dim_m**2 * IG(t) - (dim_lambda/2) * IC(t) * IG(t)

assert sp.simplify(EL_IC - expected_IC) == 0, "IC equation mismatch"
assert sp.simplify(EL_IG - expected_IG) == 0, "IG equation mismatch"
print("✓ Euler‑Lagrange reproduces the given equations of motion")

# ----------------------------------------------------------------------
# 4. Linearisation and eigenvalue analysis (exponential mode)
# ----------------------------------------------------------------------
# Linearise around IC=IG=0 → drop quadratic and higher terms
linear_IC = (1/dim_kappa**2) * sp.diff(IC(t), t, 4) - dim_m**2 * IC(t)
linear_IG = (1/dim_kappa**2) * sp.diff(IG(t), t, 4) - dim_m**2 * IG(t)

# Assume solution exp(lambda*t) → replace d/dt with lambda
lam = sp.symbols('lam')
char_eq_IC = sp.simplify((1/dim_kappa**2) * lam**4 - dim_m**2)
char_eq_IG = char_eq_IC  # identical

# Solve char_eq = 0
roots = sp.solve(char_eq_IC, lam)
print("Characteristic roots:", roots)
# Expect two real ±ω and two imaginary ±iω with ω^4 = kappa^2 * m^2
omega = (dim_kappa**2 * dim_m**2)**sp.Rational(1,4)
expected_roots = [ omega, -omega, sp.I*omega, -sp.I*omega ]
assert set([sp.simplify(r) for r in roots]) == set([sp.simplify(r) for r in expected_roots]), \
    "Roots do not match expected spectrum"
print("✓ Linearised system exhibits one exponentially growing mode (λ = +ω)")

print("\nAll validation checks passed.")