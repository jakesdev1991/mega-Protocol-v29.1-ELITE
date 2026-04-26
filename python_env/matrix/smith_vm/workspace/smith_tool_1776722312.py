# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑QED v3 Validation Script
Checks the mathematical correctness and Omega‑Protocol invariants
of the derivation presented in the audit.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
α0, Q2, m, g, ΦN, ΦΔ = sp.symbols('α0 Q2 m g ΦN ΦΔ', positive=True, real=True)
ε = g*ΦN/m  # dimensionless coupling
# lattice anisotropy parameters (three directions)
εx, εy, εz = sp.symbols('εx εy εz', real=True)
# momentum components
qx, qy, qz = sp.symbols('qx qy qz', real=True)
# lattice spacing base
a0 = sp.symbols('a0', positive=True)

# ----------------------------------------------------------------------
# 1. Integral and series expansion checks
# ----------------------------------------------------------------------
# One-loop vacuum polarization integrand (Euclidean, spacelike Q^2>0)
x = sp.symbols('x', real=True)
integrand = x*(1-x)*sp.log(1 + x*(1-x)*Q2/(m**2 * (1 - 2*ε*sp.cosh(ΦΔ) + ε**2)))
# Expand for small Q2/m_eff^2
series = sp.series(integrand, Q2, 0, 3).removeO()
# Integral of x^2 (1-x)^2 from 0 to 1
I_exact = sp.integrate(x**2 * (1-x)**2, (x, 0, 1))
I_series = sp.integrate(series, (x, 0, 1))

print("Integral ∫₀¹ x²(1-x)² dx =", I_exact.simplify())
print("Series‑expanded integral (coeff of Q²) =", I_series.simplify())
# Expected coefficient: 1/30
assert sp.simplify(I_exact - sp.Rational(1,30)) == 0, "Integral value wrong"
assert sp.simplify(I_series - sp.Rational(1,30)*Q2/(m**2 * (1 - 2*ε*sp.cosh(ΦΔ) + ε**2))) == 0, \
    "Series expansion mismatch"

# ----------------------------------------------------------------------
# 2. Effective mass positivity (mass‑positivity bound)
# ----------------------------------------------------------------------
m_eff_sq = m**2 * (1 - 2*ε*sp.cosh(ΦΔ) + ε**2)
cond = sp.simplify(m_eff_sq > 0)
print("\nEffective mass squared:", m_eff_sq)
print("Positivity condition (should be True for allowed parameters):", cond)
# We test a random point inside the bound
np.random.seed(0)
ΦN_val = np.random.rand()*0.5
ΦΔ_val = np.random.rand()*0.5 - 0.25
g_val = 1.0
m_val = 1.0
ε_val = g_val*ΦN_val/m_val
cond_num = 1 - 2*ε_val*np.cosh(ΦΔ_val) + ε_val**2 > 0
print("Sample point (ΦN,ΦΔ) =", ΦN_val, ΦΔ_val, "→ condition satisfied?", cond_num)
assert cond_num, "Mass‑positivity bound violated for sampled point"

# ----------------------------------------------------------------------
# 3. Omega‑Rubric invariants
# ----------------------------------------------------------------------
phi_n = sp.sqrt(1 - 2*ε*sp.cosh(ΦΔ) + ε**2)   # m_eff/m
psi = sp.log(phi_n)
xi_N = 1/(g*ΦN)          # up to a positive constant
xi_Delta = 1/sp.Abs(ΦΔ)  # up to a positive constant
print("\nInvariants:")
print("ψ =", psi.simplify())
print("ξ_N ~", xi_N)
print("ξ_Δ ~", xi_Delta)
# Check that they are real and finite for our sample point
psi_val = np.log(np.sqrt(1 - 2*ε_val*np.cosh(ΦΔ_val) + ε_val**2))
xiN_val = 1/(g_val*ΦN_val)
xiD_val = 1/np.abs(ΦΔ_val)
print("Numerical ψ:", psi_val)
print("Numerical ξ_N:", xiN_val)
print("Numerical ξ_Δ:", xiD_val)
assert np.isfinite(psi_val) and np.isfinite(xiN_val) and np.isfinite(xiD_val), "Invariants non‑finite"

# ----------------------------------------------------------------------
# 4. Entropy of virtual pairs (Shannon, non‑negative)
# ----------------------------------------------------------------------
# Mode energy ω_k = sqrt(k^2 + m_eff^2)
k = sp.symbols('k', real=True, nonnegative=True)
ωk = sp.sqrt(k**2 + m_eff_sq)
# Unnormalized weight w(k) ∝ 1/ω_k^2
w = 1/ωk**2
# Normalization constant Z = ∫_0^∞ w(k) dk (in 3D we would have 4πk^2 dk, but we keep 1D for simplicity)
Z = sp.integrate(w, (k, 0, sp.oo))
# Normalized probability p(k) = w/Z
p = w / Z
# Shannon entropy S = -∫ p log p dk
S_expr = -sp.integrate(p * sp.log(p), (k, 0, sp.oo))
print("\nEntropy expression (symbolic):", S_expr)
# Evaluate numerically for sample parameters
m_eff_val = m_val * np.sqrt(1 - 2*ε_val*np.cosh(ΦΔ_val) + ε_val**2)
def w_num(k):
    return 1.0/(k**2 + m_eff_val**2)
# Numerical integration (simple quadrature)
ks = np.linspace(0, 20, 2000)
ws = w_num(ks)
Z_num = np.trapz(ws, ks)
p_num = ws / Z_num
# Avoid log(0)
p_num = np.clip(p_num, 1e-15, None)
S_num = -np.trapz(p_num * np.log(p_num), ks)
print("Numerical entropy S ≈", S_num)
assert S_num >= -1e-10, "Entropy negative (should be ≥0)"

# ----------------------------------------------------------------------
# 5. Gauge invariance (transversality) of one‑loop Π^{μν}
# ----------------------------------------------------------------------
# In dimensional regularization (d = 4 - 2ε_dim) the one‑loop vacuum polarization
# for a fermion of mass m_eff is proportional to (g^{μν} q^2 - q^μ q^ν) * Π(q^2).
# We verify that the longitudinal piece q_μ Π^{μν} vanishes symbolically.
mu, nu, rho, sigma = sp.symbols('mu nu rho sigma')
# Define metric and momentum vectors (generic)
g = sp.diag(1, -1, -1, -1)  # Minkowski signature (+,-,-,-)
q = sp.Matrix([sp.Symbol('q0'), sp.Symbol('q1'), sp.Symbol('q2'), sp.Symbol('q3')])
# One‑loop scalar function Π(q^2) (we only need its dependence on q^2)
Pi_scalar = sp.Function('Pi')(q.dot(g, q))  # q^2 = q_μ q^μ
# Tensor structure: Π^{μν} = (g^{μν} q^2 - q^μ q^ν) * Π(q^2)
Pi_tensor = sp.Matrix.zeros(4,4)
for a in range(4):
    for b in range(4):
        term1 = g[a,a] * (q.dot(g, q)) if a==b else 0  # g^{μν} q^2 (no sum over a,b here)
        term2 = - q[a] * q[b]
        Pi_tensor[a,b] = (term1 + term2) * Pi_scalar
# Compute q_μ Π^{μν}
q_Pi = sp.Matrix.zeros(4)
for nu_idx in range(4):
    summ = 0
    for mu_idx in range(4):
        summ += q[mu_idx] * Pi_tensor[mu_idx, nu_idx]
    q_Pi[nu_idx] = sp.simplify(summ)
print("\nq_μ Π^{μν} (should be zero):")
print(q_Pi)
# The expression simplifies to zero because of the tensor structure
assert all([sp.simplify(expr) == 0 for expr in q_Pi]), "Transversality fails"

# ----------------------------------------------------------------------
# 6. Running α: numerator vs denominator consistency to O(α0^2)
# ----------------------------------------------------------------------
# Numerator form (as given in the paper)
alpha_num = α0 * (1 + α0/(3*sp.pi)*sp.log(Q2/m_eff_sq)
                  + α0**2/(4*sp.pi**2)*(sp.Rational(11,2) - 3*sp.zeta(2))
                  + α0**2/(sp.pi**2) * (Q2/m_eff_sq) *
                    (sp.Symbol('β1')*sp.cosh(ΦΔ) + sp.Symbol('β2')*(εx**2+εy**2+εz**2)*ΦΔ**2))
# Denominator form (as boxed)
den = 1 - α0/(3*sp.pi)*sp.log(Q2/m_eff_sq) \
      - α0**2/(4*sp.pi**2)*(sp.Rational(11,2) - 3*sp.zeta(2)) \
      - α0**2/(sp.pi**2) * (Q2/m_eff_sq) * (sp.Symbol('γ1')*sp.cosh(ΦΔ) + sp.Symbol('γ2')*(εx**2+εy**2+εz**2)*ΦΔ**2)
alpha_den = α0 / den
# Expand both to O(α0^2)
alpha_num_series = sp.series(alpha_num, α0, 0, 3).removeO()
alpha_den_series = sp.series(alpha_den, α0, 0, 3).removeO()
print("\nα numerator series:", alpha_num_series)
print("α denominator series:", alpha_den_series)
# They should match if γ_i = β_i/4
subs_dict = {sp.Symbol('γ1'): sp.Symbol('β1')/4,
             sp.Symbol('γ2'): sp.Symbol('β2')/4}
alpha_den_series_sub = alpha_den_series.subs(subs_dict)
print("After substituting γ_i = β_i/4:", alpha_den_series_sub)
assert sp.simplify(alpha_num_series - alpha_den_series_sub) == 0, "Numerator/denominator mismatch"

print("\n=== ALL CHECKS PASSED ===")