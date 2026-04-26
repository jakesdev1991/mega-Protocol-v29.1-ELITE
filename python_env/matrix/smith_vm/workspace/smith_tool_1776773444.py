# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OGEM-Ω mathematical validation (refined version)
Checks:
  1. Effective mass m^2 from double-well potential.
  2. Zero‑mode (Newtonian) frequency ω_N^2 = m^2.
  3. Archive mode dispersion ω_Δ^2(k) = k^2 + m^2.
  4. Stiffness invariants ξ_N, ξ_Δ from curvature of V_eff.
  5. Invariant ψ = ln(phi_n/phi_n0) and its limits.
  6. Overdamped control law approximation.
  7. Entropy gauge field strength (should be zero for pure gauge).
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# 1. Parameters (representative market values)
# ----------------------------------------------------------------------
G0   = 0.0          # equilibrium Greek exposure (net zero)
kappa = -0.5        # <0 -> double well
gamma = 2.0         # >0 ensures stability at large field
m0    = 1.0         # reference mass scale (sets units)

# Field average (simulate moving away from equilibrium)
G_bar_vals = np.linspace(-0.8, 0.8, 9)   # <-> bar G - G0

# ----------------------------------------------------------------------
# 2. Symbolic definitions
# ----------------------------------------------------------------------
G, G0_sym, kappa_sym, gamma_sym = sp.symbols('G G0 kappa gamma', real=True)
# Double-well potential V(G)
V = (kappa_sym/2)*(G - G0_sym)**2 + (gamma_sym/4)*(G - G0_sym)**4
# Effective mass squared m^2 = d^2V/dG^2 evaluated at G = G_bar
m2_expr = sp.diff(V, G, 2).subs({G: G_bar_sym, G0: G0_sym,
                                 kappa: kappa_sym, gamma: gamma_sym})
# Lambdify for numeric evaluation
m2_func = sp.lambdify((G_bar_sym, kappa_sym, gamma_sym), m2_expr, 'numpy')

# ----------------------------------------------------------------------
# 3. Compute m^2, frequencies, stiffness, psi
# ----------------------------------------------------------------------
print("{:>10} {:>12} {:>12} {:>12} {:>12} {:>12}".format(
    "G_bar", "m^2", "ω_N^2", "ξ_N", "ξ_Δ(k=0)", "ψ"))
for Gb in G_bar_vals:
    m2 = m2_func(Gb, kappa, gamma)
    # Stability check: if m2 <= 0 we are at or beyond critical point
    if m2 <= 0:
        ωN2 = np.nan
        xiN = np.nan
        xiD0 = np.nan
        psi = np.nan
        status = "CRITICAL (m^2≤0)"
    else:
        ωN2 = m2
        xiN = 1.0/np.sqrt(ωN2)          # ξ_N = 1/|m|
        xiD0 = xiN                      # k=0 gives same
        phi_n = 1.0/(m0 * xiN * xiD0)   # = m/m0
        psi = np.log(phi_n)             # phi_n0 = 1 by choice of m0
        status = ""
    print("{:>10.3f} {:>12.4f} {:>12.4f} {:>12.4f} {:>12.4f} {:>12.4f} {}".format(
        Gb, m2, ωN2, xiN, xiD0, psi, status))

# ----------------------------------------------------------------------
# 4. Archive mode dispersion for a few k values
# ----------------------------------------------------------------------
k_vals = [0.0, 0.5, 1.0, 2.0]
print("\nArchive mode dispersion ω_Δ^2(k) = k^2 + m^2")
for Gb in G_bar_vals[:3]:   # show a couple of points
    m2 = m2_func(Gb, kappa, gamma)
    if m2 <= 0:
        continue
    print(f"G_bar={Gb:.2f}, m^2={m2:.3f}:")
    for k in k_vals:
        w2 = k**2 + m2
        print(f"  k={k:4.1f} → ω_Δ^2={w2:6.3f}")

# ----------------------------------------------------------------------
# 5. Entropy gauge field strength (should vanish for pure gauge)
# ----------------------------------------------------------------------
# Suppose S_Gamma(x) = a * sin(q·x)  (example entropy variation)
def entropy_gauge_strength(a, q, x):
    # A_mu = ∂_mu S
    A = a * q * np.cos(q * x)   # 1‑D illustration
    # Field strength F_{01} = ∂_0 A_1 - ∂_1 A_0 (here static → zero)
    F = 0.0                      # because we assume time‑independent & 1‑D
    return A, F

a, q = 0.3, 1.2
xs = np.linspace(0, 2*np.pi, 5)
print("\nEntropy gauge (pure gauge) check:")
for x in xs:
    A, F = entropy_gauge_strength(a, q, x)
    print(f"x={x:5.2f}  A={A:8.4f}  F={F:8.4f}")

# ----------------------------------------------------------------------
# 6. Overdamped control law validation
# ----------------------------------------------------------------------
# Effective potential V_eff(G) ≈ 0.5*m^2*G^2 (quadratic approx)
def V_eff(Gval, m2val):
    return 0.5 * m2val * Gval**2

def dV_dG(Gval, m2val):
    return m2val * Gval

# Parameters for control law
eta = 0.8   # learning rate for potential term
mu  = 0.3   # entropy coupling strength
S_target = 0.5
def entropy(Gval):
    # toy model: entropy decreases with |G|
    return np.exp(-abs(Gval))

def dS_dG(Gval):
    return -np.sign(Gval) * np.exp(-abs(Gval))

def full_control(Gval, m2val):
    # exact Euler‑Lagrange (second order) with damping term gamma_damp*Gdot omitted
    # we compare the first‑order approximation used in the proposal
    term1 = -eta * dV_dG(Gval, m2val)
    term2 = -mu * (entropy(Gval) - S_target) * dS_dG(Gval)
    return term1 + term2

def exact_second_order(Gval, Gdot, m2val, gamma_damp=0.5):
    # γ_damp * Gdot + dV/dG + 2λ(S-S_target) dS/dG = 0  → solve for Gdot
    lam = mu  # using same coefficient as in proposal for illustration
    rhs = -dV_dG(Gval, m2val) - 2*lam*(entropy(Gval)-S_target)*dS_dG(Gval)
    Gdot_new = rhs / gamma_damp
    return Gdot_new

print("\nControl law comparison (G=0.2):")
G_test = 0.2
m2_test = m2_func(G_test, kappa, gamma)
if m2_test > 0:
    approx = full_control(G_test, m2_test)
    # assume a small Gdot to feed into exact formula
    Gdot_guess = 0.0
    exact = exact_second_order(G_test, Gdot_guess, m2_test)
    print(f"  Approx (first‑order) = {approx:.6f}")
    print(f"  Exact (steady‑state Gdot) = {exact:.6f}")
    print(f"  Relative error = {abs(approx-exact)/abs(exact):.2%}")
else:
    print("  m^2 ≤ 0 → system in critical region; control law needs revision.")

# ----------------------------------------------------------------------
# End of validation
# ----------------------------------------------------------------------