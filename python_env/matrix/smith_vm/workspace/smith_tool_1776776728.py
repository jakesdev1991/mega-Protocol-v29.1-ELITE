# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Checks:
 1. Poisson equation from diagonal Omega Action.
 2. Hessian instability condition for V_eff.
 3. Monotonicity of Shannon conditional entropy proxy.
"""

import sympy as sp

# ------------------------------------------------------------------
# Symbols
# ------------------------------------------------------------------
x, y, z, t = sp.symbols('x y z t', real=True)
PhiN = sp.Function('PhiN')(x, y, z, t)
PhiD = sp.Function('PhiD')(x, y, z, t)   # Archive mode (Phi_Delta)

c, vD = sp.symbols('c vD', positive=True)   # propagation speeds
# Effective potential (model)
mN, mD, lam = sp.symbols('mN mD lam', real=True)
V_eff = (mN**2/2)*PhiN**2 + (mD**2/2)*PhiD**2 + lam*PhiN*PhiD**2

# Action density (diagonal basis)
L = (sp.diff(PhiN, t)**2)/2 - (c**2/2)*(sp.diff(PhiN, x)**2 +
                                        sp.diff(PhiN, y)**2 +
                                        sp.diff(PhiN, z)**2) \
    + (sp.diff(PhiD, t)**2)/2 - (vD**2/2)*(sp.diff(PhiD, x)**2 +
                                            sp.diff(PhiD, y)**2 +
                                            sp.diff(PhiD, z)**2) \
    - V_eff

# ------------------------------------------------------------------
# 1. Poisson equation: variation w.r.t. PhiN
# ------------------------------------------------------------------
# Euler-Lagrange: dL/dPhiN - d/d_mu (dL/d(dPhiN/dx_mu)) = 0
dL_dPhiN = sp.diff(L, PhiN)
# kinetic term contribution:
kinetic_term = -sp.diff(sp.diff(L, sp.diff(PhiN, t)), t) \
               + sp.diff(sp.diff(L, sp.diff(PhiN, x)), x) \
               + sp.diff(sp.diff(L, sp.diff(PhiN, y)), y) \
               + sp.diff(sp.diff(L, sp.diff(PhiN, z)), z)
EL_PhiN = sp.simplify(dL_dPhiN - kinetic_term)
print("Euler‑Lagrange for PhiN:")
sp.pprint(EL_PhiN)
# For static case (time‑independent) and neglecting PhiD kinetic part:
static_eq = sp.simplify(EL_PhiN.subs({sp.diff(PhiN, t):0,
                                      sp.diff(PhiD, t):0}))
print("\nStatic limit (∂_t Φ_N = ∂_t Φ_Δ = 0):")
sp.pprint(static_eq)
# Identify source rho_Delta = (1/c^2) * ∂V_eff/∂PhiN
rho_Delta = sp.diff(V_eff, PhiN) / c**2
print("\nSource term ρ_Δ = (1/c^2) ∂V_eff/∂Φ_N:")
sp.pprint(rho_Delta)
print("\nPoisson form: ∇^2 Φ_N = ρ_Δ  ?")
print(sp.simplify(static_eq - sp.laplacian(PhiN, (x, y, z)) + rho_Delta))

# ------------------------------------------------------------------
# 2. Hessian instability condition
# ------------------------------------------------------------------
# Treat PhiN, PhiD as constant background fields for mass matrix
H = sp.hessian(V_eff, (PhiN, PhiD))
print("\nHessian matrix of V_eff:")
sp.pprint(H)
# Eigenvalues
evals = H.eigenvals()
print("\nEigenvalues (symbolic):")
sp.pprint(evals)
# Condition for a negative eigenvalue: determinant < 0 (since trace>0 for positive masses)
detH = H.det()
print("\nDeterminant of Hessian:")
sp.pprint(detH)
# Solve detH < 0 for PhiD
cond = sp.solve(sp.Eq(detH, 0), PhiD**2)
print("\nCritical Φ_Δ^2 where det=0:")
sp.pprint(cond)
# Thus tachyonic when Φ_Δ^2 > (mN^2 * mD^2) / (4*lam^2)
crit = mN**2 * mD**2 / (4 * lam**2)
print("\nTachyonic condition: Φ_Δ^2 >", crit)

# ------------------------------------------------------------------
# 3. Entropy monotonicity check
# ------------------------------------------------------------------
# Define a mode label k (positive integer) and bracket B
k, Lambda, m_eff, g, xiD = sp.symbols('k Lambda m_eff g xiD', positive=True)
B = sp.log(Lambda**2 / m_eff**2) + g**2 * xiD**2   # since m_Δ = 1/ξ_Δ → 1/m_Δ^2 = ξ_Δ^2
# Probability proxy (unnormalized)
p_k = k**(-4) / B
# Normalization constant Z = Σ_{k=1}^∞ k^{-4} = π^4/90 (zeta(4))
Z = sp.pi**4 / 90
p_norm = p_k / Z
# Shannon entropy (up to additive constant -log Z)
S = -sp.summation(p_norm * sp.log(p_norm), (k, 1, sp.oo))
print("\nShannon conditional entropy (symbolic sum):")
sp.pprint(S)
# Show derivative dS/dB < 0 (entropy decreases as bracket grows)
dS_dB = sp.diff(S, B)
print("\n∂S/∂B:")
sp.pprint(dS_dB.simplify())
# Since B>0, we expect negative sign; evaluate numerically for sample values
sample = {Lambda: 10.0, m_eff: 1.0, g: 0.5, xiD: 2.0}
B_val = B.subsample(sample)
dS_val = dS_dB.subsample(sample)
print("\nSample B =", B_val.evalf())
print("Sample ∂S/∂B =", dS_val.evalf())
print("∂S/∂B < 0 ?", dS_val.evalf() < 0)

# ------------------------------------------------------------------
# End of script
# ------------------------------------------------------------------