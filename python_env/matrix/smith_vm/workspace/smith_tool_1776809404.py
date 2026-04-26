# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Action validation for FreeZe‑Ω integration (Perceptual Integrity Shield).
Checks the Euler‑Lagrange equation for the perceptual field Ψ.
Replace the placeholder definitions of L_Ω and the Φ‑dependencies
with the true forms from the proposal to obtain a rigorous test.
"""

import numpy as np
import sympy as sp

# -------------------------- 1. Symbolic setup --------------------------
# Coordinates (perceptual spacetime)
x0, x1, x2, x3 = sp.symbols('x0 x1 x2 x3', real=True)
# Field Ψ(x)
Psi = sp.Function('Psi')(x0, x1, x2, x3)

# Constants (choose representative values)
ell0 = 1.0          # normalized perceptual scale
alpha = 1.0
beta  = 1.0
gamma = 0.5
lam   = 0.2         # λ_Ω coupling strength

# Placeholder: Φ_N and Φ_Δ as linear functions of Ψ
# In reality these are derived from descriptor statistics.
a1, b1 = 0.8, 0.2   # Φ_N = a1*Psi + b1
a2, b2 = 0.5, -0.1  # Φ_Δ = a2*Psi + b2
Phi_N = a1*Psi + b1
Phi_Delta = a2*Psi + b2

# Placeholder Ω‑Lagrangian (must be a scalar)
L_Omega = Phi_N**2 + Phi_Delta**2   # <-- REPLACE WITH TRUE FORM

# Potential U(Ψ)
U = sp.Rational(1,2)*alpha*Psi**2 + sp.Rational(1,4)*beta*Psi**4 - gamma*Psi

# Kinetic term (Minkowski metric η = diag(+1,-1,-1,-1) for simplicity)
# ∂_μΨ ∂^μΨ = (∂0Ψ)^2 - (∂1Ψ)^2 - (∂2Ψ)^2 - (∂3Ψ)^2
dPsi = [sp.diff(Psi, coord) for coord in (x0, x1, x2, x3)]
kinetic = sp.Rational(1,2)*(1/ell0**2) * (
    dPsi[0]**2 - dPsi[1]**2 - dPsi[2]**2 - dPsi[3]**2
)

# Gauge field strength (set to zero for this test; only the coupling matters)
# A_mu J^mu term: we take A_mu = ∂_mu S_pose, J^mu = sqrt(2)*ell0^3*Phi_Delta*delta^mu_0
# For a pure gauge A_mu = ∂_mu S, the term reduces to J^0 * ∂_0 S.
# We introduce a dummy scalar S to illustrate the coupling.
S = sp.Function('S')(x0, x1, x2, x3)
A0 = sp.diff(S, x0)   # only time component non‑zero in J^mu
J0 = sp.sqrt(2)*ell0**3 * Phi_Delta
gauge_coupling = A0 * J0   # A_mu J^mu with μ=0 only

# Full Lagrangian density
L = kinetic + U + lam*L_Omega + gauge_coupling

# -------------------------- 2. Euler‑Lagrange --------------------------
# ∂L/∂Ψ - ∂_μ (∂L/∂(∂_μΨ)) = 0
dL_dPsi = sp.diff(L, Psi)
dL_d_dPsi = [sp.diff(L, dPsi_i) for dPsi_i in dPsi]
# ∂_μ term (note sign from metric)
div_term = sp.diff(dL_d_dPsi[0], x0) - sp.diff(dL_d_dPsi[1], x1) \
           - sp.diff(dL_d_dPsi[2], x2) - sp.diff(dL_d_dPsi[3], x3)
EL_eq = sp.simplify(dL_dPsi - div_term)
print("Euler‑Lagrange expression (symbolic):")
sp.pprint(EL_eq)
print("\n")

# -------------------------- 3. Numeric test --------------------------
# Convert symbolic EL_eq to a lambda function for fast evaluation
# We treat Ψ and S as independent fields on a small lattice.
# For the test we set S = 0 (so gauge coupling vanishes) to focus on Ψ dynamics.
EL_func = sp.lambdify(
    (Psi, sp.diff(Psi, x0), sp.diff(Psi, x1), sp.diff(Psi, x2), sp.diff(Psi, x3),
     x0, x1, x2, x3),   # extra args for any explicit coordinate dependence (none here)
    EL_eq,
    modules='numpy'
)

# Build a small 4D grid (2 points per dimension → 16 cells)
grid_size = 2
coords = [np.linspace(0, 1, grid_size) for _ in range(4)]
X0, X1, X2, X3 = np.meshgrid(*coords, indexing='ij')

# Random field configuration (small amplitude to stay near vacuum)
np.random.seed(42)
Psi_vals = 0.1 * np.random.randn(*X0.shape)
# Derivatives via finite differences (central where possible)
def gradient(f, axis):
    # axis: 0->x0, 1->x1, 2->x2, 3->x3
    return np.gradient(f, coords[axis], axis=axis)

dPsi_vals = [gradient(Psi_vals, i) for i in range(4)]

# Evaluate EL residual pointwise
residual = EL_func(
    Psi_vals, dPsi_vals[0], dPsi_vals[1], dPsi_vals[2], dPsi_vals[3],
    X0, X1, X2, X3
)

max_res = np.max(np.abs(residual))
rms_res = np.sqrt(np.mean(residual**2))

print(f"Numeric test on {grid_size}^4 grid:")
print(f"  Max |EL|  = {max_res:.6e}")
print(f"  RMS |EL|  = {rms_res:.6e}")
print("\nInterpretation:")
print("  If the true L_Ω and Φ‑dependencies were inserted,")
print("  a correct action should give residuals ≈ 0 (up to machine precision).")
print("  Non‑zero values indicate either:")
print("   - missing terms in L_Ω,")
print("   - incorrect Φ‑Ψ relations, or")
print("   - a need for boundary conditions / gauge fixing.")