# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Define symbols
lambda_ , v = sp.symbols('lambda v', positive=True, real=True)
Phi_N, Phi_D = sp.symbols('Phi_N Phi_D', real=True)

# Mexican‑hat potential (incorrectly symmetric)
V = lambda_ / 4 * (Phi_N**2 + Phi_D**2 - v**2)**2

# Hessian matrix
H = sp.hessian(V, (Phi_N, Phi_D))

# Evaluate at the vacuum manifold: Phi_N**2 + Phi_D**2 = v**2
# Choose a point on the vacuum, e.g. Phi_N = v, Phi_D = 0
H_vac = H.subs({Phi_N: v, Phi_D: 0})
eigs = H_vac.eigenvals()
print("Hessian eigenvalues at (v,0):", eigs)

# Compute eigenvalues symbolically on the vacuum circle
# Parameterize: Phi_N = v*cos(theta), Phi_D = v*sin(theta)
theta = sp.symbols('theta', real=True)
H_theta = H.subs({Phi_N: v*sp.cos(theta), Phi_D: v*sp.sin(theta)})
eigs_theta = H_theta.eigenvals()
print("Symbolic eigenvalues on vacuum circle:", eigs_theta)

# Now add a symmetry‑breaking mass term for the archive mode
m_D = sp.symbols('m_D', positive=True, real=True)
V_broken = V + sp.Rational(1,2)*m_D**2 * Phi_D**2

H_broken = sp.hessian(V_broken, (Phi_N, Phi_D))
H_broken_vac = H_broken.subs({Phi_N: v, Phi_D: 0})
eigs_broken = H_broken_vac.eigenvals()
print("Eigenvalues with explicit mass term:", eigs_broken)