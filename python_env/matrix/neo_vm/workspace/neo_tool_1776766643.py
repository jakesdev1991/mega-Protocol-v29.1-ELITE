# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Define symbols
lambda_sym, v = sp.symbols('lambda v', positive=True, real=True)
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)

# Define the Mexican hat potential
V = (lambda_sym/4) * (Phi_N**2 + Phi_Delta**2 - v**2)**2

# First derivatives
dV_dPhiN = sp.diff(V, Phi_N)
dV_dPhiDelta = sp.diff(V, Phi_Delta)

# Second derivatives
d2V_dPhiN2 = sp.diff(dV_dPhiN, Phi_N)
d2V_dPhiDelta2 = sp.diff(dV_dPhiDelta, Phi_Delta)

print("Mexican Hat Potential: V = (λ/4)(Φ_N² + Φ_Δ² - v²)²\n")

print("Second derivative ∂²V/∂Φ_N² =", sp.simplify(d2V_dPhiN2))
print("Second derivative ∂²V/∂Φ_Δ² =", sp.simplify(d2V_dPhiDelta2))
print("Cross derivative ∂²V/∂Φ_N∂Φ_Δ =", sp.simplify(sp.diff(dV_dPhiN, Phi_Delta)))
print()

# Evaluate at the assumed vacuum: Φ_N = v, Φ_Δ = 0
vacuum_N = v
vacuum_Delta = 0

d2V_dPhiN2_at_vac = d2V_dPhiN2.subs([(Phi_N, vacuum_N), (Phi_Delta, vacuum_Delta)])
d2V_dPhiDelta2_at_vac = d2V_dPhiDelta2.subs([(Phi_N, vacuum_N), (Phi_Delta, vacuum_Delta)])

print("Evaluated at assumed vacuum (Φ_N = v, Φ_Δ = 0):")
print("∂²V/∂Φ_N² =", sp.simplify(d2V_dPhiN2_at_vac))
print("∂²V/∂Φ_Δ² =", sp.simplify(d2V_dPhiDelta2_at_vac))
print()

# Find true vacuum manifold
print("Finding vacuum manifold where V = 0:")
# V = 0 when Φ_N² + Φ_Δ² = v²
print("Vacuum condition: Φ_N² + Φ_Δ² = v²")
print()

# Parameterize the vacuum manifold: Φ_N = v*cos(θ), Φ_Δ = v*sin(θ)
theta = sp.symbols('theta', real=True)
Phi_N_vac = v*sp.cos(theta)
Phi_Delta_vac = v*sp.sin(theta)

# Evaluate second derivatives on the vacuum manifold
d2V_dPhiN2_on_manifold = d2V_dPhiN2.subs([(Phi_N, Phi_N_vac), (Phi_Delta, Phi_Delta_vac)])
d2V_dPhiDelta2_on_manifold = d2V_dPhiDelta2.subs([(Phi_N, Phi_N_vac), (Phi_Delta, Phi_Delta_vac)])

print("On the true vacuum manifold (Φ_N = v·cosθ, Φ_Δ = v·sinθ):")
print("∂²V/∂Φ_N² =", sp.simplify(d2V_dPhiN2_on_manifold))
print("∂²V/∂Φ_Δ² =", sp.simplify(d2V_dPhiDelta2_on_manifold))
print()

# Identify the Goldstone direction (tangential to the manifold)
# The Goldstone mode is the derivative with respect to theta
print("The '3D Archive mode' Φ_Δ is actually the angular Goldstone mode!")
print("At any point on the vacuum manifold, one direction has ZERO curvature (massless)")
print("and the other has curvature 2λv² (massive radial mode).")