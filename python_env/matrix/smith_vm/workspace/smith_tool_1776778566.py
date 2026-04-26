# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# 1. Jerk estimator verification
# ----------------------------------------------------------------------
def jerk_estimate(t_vals, I_vals, dt):
    """
    Second‑order accurate central‑difference stencil for the third derivative:
    J(t) ≈ [-I(t-2dt) + 2I(t-dt) - 2I(t+dt) + I(t+2dt)] / (2*dt**3)
    Assumes t_vals are uniformly spaced with step dt.
    """
    # Use central indices; we need at least 5 points
    J = (-I_vals[:-4] + 2*I_vals[1:-3] - 2*I_vals[2:-2] + I_vals[3:-1]) / (2.0 * dt**3)
    t_center = t_vals[2:-2]  # points where the estimate is defined
    return t_center, J

# Test on I(t) = t^3
t = np.linspace(0, 1, 101)
dt = t[1] - t[0]
I = t**3
t_est, J_est = jerk_estimate(t, I, dt)
J_exact = 6 * np.ones_like(t_est)  # true third derivative of t^3
max_err = np.max(np.abs(J_est - J_exact))
print(f"Jerk estimator max error on t^3: {max_err:.2e}")
assert max_err < 1e-12, "Jerk estimator fails on cubic test"

# ----------------------------------------------------------------------
# 2. Lagrangian dimensional analysis (entropy treated as dimensionless)
# ----------------------------------------------------------------------
# Define symbols
kappa, m, lam, t_sym = sp.symbols('kappa m lam t', positive=True)
IC, IG = sp.symbols('IC IG', cls=sp.Function)

# Lagrangian density
L = (1/(2*kappa**2))*((sp.diff(IC(t_sym), t_sym, 2))**2 +
                       (sp.diff(IG(t_sym), t_sym, 2))**2) \
    - sp.Rational(1,2)*m**2*(IC(t_sym)**2 + IG(t_sym)**2) \
    - sp.Rational(lam,4)*IC(t_sym)*IG(t_sym)**2

# Assign dimensions: [entropy] = 1 (dimensionless)
# Let [t] = T
# We solve for dimensions of kappa, m, lam such that each term has dimension T^{-1}
# (so that integrating over dt gives dimensionless action)
T = sp.symbols('T')
# Assume [kappa] = T**a, [m] = T**b, [lam] = T**c
a, b, c = sp.symbols('a b c')
# Dimensions of each term:
# term1: 1/kappa^2 * (d^2 I/dt^2)^2 -> T^{-2a} * (T^{-2})^2 = T^{-2a-4}
# term2: m^2 * I^2 -> T^{2b}
# term3: lam * I * I^2 -> T^{c}
# We require each term to have dimension T^{-1}
eq1 = sp.Eq(-2*a - 4, -1)   # term1
eq2 = sp.Eq(2*b, -1)        # term2
eq3 = sp.Eq(c, -1)          # term3
sol = sp.solve([eq1, eq2, eq3], (a, b, c))
print("Dimensional solution (exponents of T):", sol)
# Expected: a = -3/2, b = -1/2, c = -1
assert sol[a] == -sp.Rational(3,2) and sol[b] == -sp.Rational(1,2) and sol[c] == -1

# ----------------------------------------------------------------------
# 3. Linearized equations of motion and eigenvalues
# ----------------------------------------------------------------------
# Linearize around IC=IG=0 (drop quadratic and higher terms)
# Linear Lagrangian: L_lin = (1/(2*kappa**2))*[(IC_tt)^2 + (IG_tt)^2] - (1/2)*m**2*(IC^2+IG^2)
# Euler-Lagrange gives: (1/kappa**2)*IC_tttt - m**2*IC = 0 (same for IG)
s = sp.symbols('s')
# Assume solution exp(s*t) -> substitute derivatives: d^n/dt^n -> s^n
char_eq = s**4/kappa**2 - m**2
print("Characteristic equation:", char_eq)
# Solve for s^4
s4_sol = sp.solve(char_eq, s**4)
print("s^4 =", s4_sol)
# s = (kappa^2 * m^2)^{1/4} * (±1, ±i)
omega = (kappa**2 * m**2)**sp.Rational(1,4)
roots = [ omega, -omega, sp.I*omega, -sp.I*omega ]
print("Eigenvalues (growth rates):", [r.simplify() for r in roots])
# Verify one positive real root
assert any(r.is_real and r > 0 for r in roots), "No growing mode found"

# ----------------------------------------------------------------------
# 4. Covariant mode decoupling
# ----------------------------------------------------------------------
# Define Phi_N = (IC+IG)/sqrt(2), Phi_Delta = (IC-IG)/sqrt(2)
Phi_N = (IC + IG)/sp.sqrt(2)
Phi_D = (IC - IG)/sp.sqrt(2)
# Express IC, IG in terms of Phi_N, Phi_D
IC_expr = (Phi_N + Phi_D)/sp.sqrt(2)
IG_expr = (Phi_N - Phi_D)/sp.sqrt(2)
# Substitute into linearized EoM and simplify
# Linear EoM for IC: (1/kappa**2)*IC_tttt - m**2*IC = 0
# Same for IG
# After substitution, each should give same equation for Phi_N and Phi_D
# Let's compute for Phi_N:
IC_tttt = sp.diff(IC_expr, t_sym, 4)
IG_tttt = sp.diff(IG_expr, t_sym, 4)
eq_N = (1/kappa**2)*IC_tttt - m**2*IC_expr
eq_D = (1/kappa**2)*IG_tttt - m**2*IG_expr
# Since IC and IG are independent, the combination should split:
# (eq_N + eq_D)/sqrt(2) should give equation for Phi_N
# (eq_N - eq_D)/sqrt(2) should give equation for Phi_D
eq_N_simpl = sp.simplify((eq_N + eq_D)/sp.sqrt(2))
eq_D_simpl = sp.simplify((eq_N - eq_D)/sp.sqrt(2))
print("Equation for Phi_N:", eq_N_simpl)
print("Equation for Phi_D:", eq_D_simpl)
# Both should be of the form (1/kappa**2)*Phi_tttt - m**2*Phi = 0
assert sp.simplify(eq_N_simpl - ((1/kappa**2)*sp.diff(Phi_N, t_sym, 4) - m**2*Phi_N)) == 0
assert sp.simplify(eq_D_simpl - ((1/kappa**2)*sp.diff(Phi_D, t_sym, 4) - m**2*Phi_D)) == 0
print("Covariant mode decoupling verified.")