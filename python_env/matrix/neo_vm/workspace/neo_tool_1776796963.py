# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np

# ------------------------------------------------------------
# 1. Dimensional inconsistency: stiffness invariants claim "time"
# ------------------------------------------------------------
Lambda, alpha, beta, gamma = sp.symbols('Lambda alpha beta gamma', real=True)
V = alpha/2 * Lambda**2 + beta/4 * Lambda**4 - gamma * Lambda
d2V = sp.diff(V, Lambda, 2)
print("Second derivative of V (dimensionless):", d2V)
tau = sp.symbols('tau', positive=True, real=True)
print("Second derivative * tau (units of time):", sp.simplify(d2V * tau))

# ------------------------------------------------------------
# 2. Fokker‑Planck missing ½ factor: variance & probability current
# ------------------------------------------------------------
x, k, D = sp.symbols('x k D', real=True, positive=True)
# Correct steady‑state (with ½ factor): P ∝ exp(-k*x^2/(2*D))
P_correct = sp.exp(-k*x**2/(2*D))
# Incorrect steady‑state (missing ½): effective diffusion D/2 -> exponent -k*x^2/D
P_incorrect = sp.exp(-k*x**2/D)

# Variances (Gaussian integrals)
var_correct = sp.integrate(x**2 * P_correct, (x, -sp.oo, sp.oo)) / sp.integrate(P_correct, (x, -sp.oo, sp.oo))
var_incorrect = sp.integrate(x**2 * P_incorrect, (x, -sp.oo, sp.oo)) / sp.integrate(P_incorrect, (x, -sp.oo, sp.oo))
print("Variance (correct ½ factor):", sp.simplify(var_correct))
print("Variance (missing ½ factor):", sp.simplify(var_incorrect))

# Probability current J = mu*P - D*∂_x P  (mu = -k*x)
J_correct = -k*x*P_correct - D*sp.diff(P_correct, x)
J_incorrect = -k*x*P_incorrect - D*sp.diff(P_incorrect, x)
print("Current (correct):", sp.simplify(J_correct))
print("Current (incorrect):", sp.simplify(J_incorrect))