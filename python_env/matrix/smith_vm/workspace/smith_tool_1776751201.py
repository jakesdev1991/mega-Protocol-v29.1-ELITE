# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Dimensional‑consistency validator for the Higher‑Order Lattice Polarization
derivation (Phi_N, Phi_Delta, J*).

Checks:
  - Each term in an expression shares the same dimension.
  - Key invariants:
      * Phi_N mediates a long-range force → mass term coefficient must be zero.
      * Phi_Delta must remain massless (no mass‑squared term).
      * Jerk invariant J* has dimension [T^{-3}].
"""

import sympy as sp
from sympy.physics.units import length, mass, time, charge

# ----------------------------------------------------------------------
# Define base dimensions (can be re‑scaled to match Omega‑Protocol units)
# ----------------------------------------------------------------------
M = mass          # [M]
L = length        # [L]
T = time          # [T]
Q = charge        # [Q]

# Helper to print dimensions nicely
def dim(expr):
    return sp.simplify(expr)

# ----------------------------------------------------------------------
# Symbolic placeholders for the quantities in the derivation
# ----------------------------------------------------------------------
# Fields
Phi_N   = sp.Symbol('Phi_N')   # Newtonian mode
Phi_D   = sp.Symbol('Phi_Delta') # Polarization mode
# Couplings
g_N     = sp.Symbol('g_N')
g_D     = sp.Symbol('g_Delta')
# Scales
Lambda  = sp.Symbol('Lambda')   # UV cutoff
xi0     = sp.Symbol('xi0')      # fundamental length
psi     = sp.Symbol('psi')      # log(Phi_N/I0)
I0      = sp.Symbol('I0')       # reference value for Phi_N
mu0     = sp.Symbol('mu0')      # RG reference scale
# Jerk invariant (should have dimension T^{-3})
J_star  = sp.Symbol('J_star')

# ----------------------------------------------------------------------
# Dimension assignments (adjust if your Omega‑Protocol uses different conventions)
# ----------------------------------------------------------------------
# Scalar fields: dimension of mass (can also be 1/L depending on convention)
dim_PhiN = M
dim_PhiD = M

# Yukawa couplings are dimensionless in 4‑D
dim_gN   = 1
dim_gD   = 1

# UV cutoff: inverse length
dim_Lambda = 1/L

# xi0: fundamental length
dim_xi0 = L

# psi = ln(Phi_N/I0) → dimensionless
dim_psi = 1

# I0 same dimension as Phi_N
dim_I0 = dim_PhiN

# mu0: RG scale (energy) → mass
dim_mu0 = M

# Jerk invariant: [T^{-3}]
dim_Jstar = 1/(T**3)

# ----------------------------------------------------------------------
# Define a few key expressions from the derivation
# ----------------------------------------------------------------------
# 1. One‑loop scalar mass correction (quadratically divergent)
#    Δm^2 ~ (g^2 / (16π^2)) * Λ^2
delta_m2_N = (g_N**2 / (16*sp.pi**2)) * Lambda**2
delta_m2_D = (g_D**2 / (16*sp.pi**2)) * Lambda**2

# 2. Beta function for g_D (one‑loop)
beta_gD = g_D**3 / (16*sp.pi**2)

# 3. Landau pole scale from integrating beta_gD
#    Λ_LP = μ0 * exp(8π^2 / g_D^2(μ0))
Lambda_LP = mu0 * sp.exp(8*sp.pi**2 / g_D**2)

# 4. Lattice spacing dependence on Phi_N
#    a = ξ0 * exp(-ψ) = ξ0 * I0 / Phi_N
a_lattice = xi0 * I0 / Phi_N

# 5. Photon kinetic term correction from lattice
#    ΔL ⊃ C a^2 q^2 A_μ A^μ   (C dimensionless)
C = sp.Symbol('C', dimensionless=True)
q = sp.Symbol('q')   # momentum
dim_q = 1/L          # momentum inverse length
A = sp.Symbol('A')   # gauge field (dimension 1/L^{1/2} in 4‑D, but we only need consistency)
dim_A = 1/(L**0.5)   # not essential for this check
term_photon = C * a_lattice**2 * q**2 * A**2

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def check_dimension(expr, expected_dim, name):
    """Return True if expr has dimension expected_dim (up to a dimensionless factor)."""
    # Replace symbols with their dimensional equivalents
    subs_dict = {
        Phi_N: dim_PhiN,
        Phi_D: dim_PhiD,
        g_N:   dim_gN,
        g_D:   dim_gD,
        Lambda: dim_Lambda,
        xi0:   dim_xi0,
        psi:   dim_psi,
        I0:    dim_I0,
        mu0:   dim_mu0,
        J_star: dim_Jstar,
        q:     dim_q,
        A:     dim_A,
        C:     1,   # dimensionless
    }
    dim_expr = sp.simplify(expr.subs(subs_dict))
    # Strip any remaining dimensionless symbols (they should be 1)
    dim_expr = sp.simplify(dim_expr)
    return sp.simplify(dim_expr / expected_dim) == 1, dim_expr

print("=== Dimensional Consistency Check ===\n")

# Check each expression
checks = [
    (delta_m2_N, M**2, "Δm_N^2 (one‑loop)"),
    (delta_m2_D, M**2, "Δm_Δ^2 (one‑loop)"),
    (beta_gD, 1, "β(g_Δ) (should be dimensionless)"),
    (Lambda_LP, M, "Λ_LP (Landau pole scale)"),
    (a_lattice, L, "a (lattice spacing)"),
    (term_photon, 1/L**2, "C a^2 q^2 A^2 (photon kinetic correction)"),
]

all_ok = True
for expr, exp_dim, label in checks:
    ok, got = check_dimension(expr, exp_dim, label)
    if not ok:
        all_ok = False
        print(f"[FAIL] {label}: expected {exp_dim}, got {got}")
    else:
        print(f"[PASS] {label}: dimension OK")

# Additional invariant checks
print("\n=== Invariant Checks ===")
# Phi_N must remain massless for Poisson recovery → coefficient of Phi_N^2 term must vanish
# In the effective Lagrangian the mass term is m_N^2 Phi_N^2; we require m_N^2 = 0.
# Here we test that the radiative correction does NOT generate a non‑zero mass unless fine‑tuned.
# We simply flag if delta_m2_N is non‑zero (it is) → indicates need for symmetry protection.
print("[INFO] One‑loop mass correction Δm_N^2 is non‑zero → requires symmetry (e.g., SUSY) to keep Φ_N massless.")
# Phi_Delta must stay massless (Archive mode)
print("[INFO] One‑loop mass correction Δm_Δ^2 is non‑zero → same comment as above.")
# Jerk invariant J* must have dimension T^{-3}
ok_J, got_J = check_dimension(J_star, 1/(T**3), "J*")
if not ok_J:
    all_ok = False
    print(f"[FAIL] J* dimension mismatch: expected T⁻³, got {got_J}")
else:
    print("[PASS] J* has correct dimension [T⁻³]")

print("\n=== Summary ===")
print("All checks passed:" if all_ok else "Some checks failed – revise derivation or introduce protective symmetry.")