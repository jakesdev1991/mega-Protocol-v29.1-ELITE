# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Define symbols
t = sp.symbols('t', real=True)
phi_N = sp.Function('phi_N')(t)
phi_D = sp.Function('phi_D')(t)  # phi_Delta

# Define probabilities
p_N = phi_N**2 / (phi_N**2 + phi_D**2)
p_D = phi_D**2 / (phi_N**2 + phi_D**2)

# Shannon entropy
S_h = -p_N*sp.log(p_N) - p_D*sp.log(p_D)

# Compute third time derivative
J = sp.diff(S_h, t, 3)
sp.simplify(J)