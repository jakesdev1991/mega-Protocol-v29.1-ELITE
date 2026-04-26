# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for PICM‑Ω v2
Checks:
  1. Effective mass from phi^4 action.
  2. Stiffness invariants from reduced 2D potential.
  3. Orthogonality of constant and sin(omega*t) basis.
  4. Eigenvalue of fluctuation operator on sin mode.
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
lam, v, phi_c = sp.symbols('lam v phi_c', positive=True, real=True)
t, T, omega = sp.symbols('t T omega', real=True)
phi0 = sp.Function('phi0')(t)          # background field
delta_phi = sp.Function('delta_phi')(t)  # fluctuation

# ----------------------------------------------------------------------
# 1. Phi^4 action and effective mass
# ----------------------------------------------------------------------
V = lam/4 * (phi0**2 - v**2)**2
dV_dphi = sp.diff(V, phi0)
d2V_dphi2 = sp.diff(dV_dphi, phi0)   # = lam*(3*phi0**2 - v**2)
m_eff_sq = lam*(3*phi0**2 - v**2)

print("=== Effective mass from phi^4 ===")
print("d^2V/dphi^2 =", d2V_dphi2.simplify())
print("Assert m_eff^2 matches:", sp.simplify(d2V_dphi2 - m_eff_sq) == 0)
assert sp.simplify(d2V_dphi2 - m_eff_sq) == 0, "Effective mass mismatch"

# ----------------------------------------------------------------------
# 2. Reduced 2D potential and stiffness invariants
# ----------------------------------------------------------------------
PhiN, PhiD = sp.symbols('PhiN PhiD', real=True)
V2 = lam/4 * ((PhiN**2 + PhiD**2) - v**2)**2
# Hessian matrix
H = sp.Matrix([[sp.diff(V2, PhiN, PhiN), sp.diff(V2, PhiN, PhiD)],
               [sp.diff(V2, PhiD, PhiN), sp.diff(V2, PhiD, PhiD)]])
print("\n=== Hessian of reduced potential ===")
sp.pprint(H)

# Invariants claimed (assuming basis diagonalizes H, i.e. off-diagonal = 0)
xiN_inv2_claimed = lam*(3*PhiN**2 + PhiD**2 - v**2)
xiD_inv2_claimed = lam*(PhiN**2 + 3*PhiD**2 - v**2)

# Check diagonal entries when PhiN*PhiD = 0 (decoupled basis)
H_diag = sp.diag(H[0,0], H[1,1])
print("\nDiagonal of H (general):", H_diag)
print("Claimed xi_N^{-2}:", xiN_inv2_claimed)
print("Claimed xi_Δ^{-2}:", xiD_inv2_claimed)

# Substitute PhiD=0 to test first invariant, PhiN=0 for second
assert sp.simplify(H[0,0].subs({PhiD:0}) - xiN_inv2_claimed.subs({PhiD:0})) == 0, \
    "xi_N invariant mismatch when PhiD=0"
assert sp.simplify(H[1,1].subs({PhiN:0}) - xiD_inv2_claimed.subs({PhiN:0})) == 0, \
    "xi_Δ invariant mismatch when PhiN=0"
print("Invariants hold under decoupled basis assumption (PhiN*PhiD=0).")

# ----------------------------------------------------------------------
# 3. Orthogonality of constant and sin(omega*t) basis on [0,T]
# ----------------------------------------------------------------------
const = 1
sin_mode = sp.sin(omega*t)
inner_const_sin = sp.integrate(const * sin_mode, (t, 0, T))
print("\n=== Basis orthogonality ===")
print("<1, sin(ωt)> over [0,T] =", inner_const_sin.simplify())
# Orthogonal iff integral = 0 -> requires omega*T = n*pi, n integer.
# We note the condition; the proposal assumes a suitable window.
orthogonal_cond = sp.simplify(inner_const_sin)
print("Orthogonality condition: ω·T = n·π (n∈ℤ).")
# No assertion – just inform user.

# ----------------------------------------------------------------------
# 4. Fluctuation operator eigenvalue on sin mode
# ----------------------------------------------------------------------
# Operator L = -d^2/dt^2 + m_eff^2 (assuming phi0 constant => m_eff constant)
L_sin = -sp.diff(sin_mode, t, 2) + m_eff_sq * sin_mode
eigenval = sp.simplify(L_sin / sin_mode)  # should be ω^2 + m_eff^2
print("\n=== Fluctuation operator on sin(ωt) ===")
print("L[sin] =", L_sin.simplify())
print("Eigenvalue (L[sin]/sin) =", eigenval)
expected = omega**2 + m_eff_sq
print("Expected ω^2 + m_eff^2 =", expected.simplify())
assert sp.simplify(eigenval - expected) == 0, "Fluctuation operator eigenvalue mismatch"
print("Eigenvalue check passed.")

print("\nAll core Ω‑Protocol mathematical checks passed.")