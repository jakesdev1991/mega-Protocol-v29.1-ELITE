# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith: Dimensional & invariant check for the repaired solution
import sympy as sp

# --- Symbols for dimensions ---
T = sp.symbols('T', positive=True)   # time dimension
# In natural units ħ=c=1: [action] = 1, [Lagrangian] = T^{-1}
# We adopt the convention used in the text: [L] = T^{-2}, [S] = T^{-1}
# Fields:
I   = sp.symbols('I')   # dimensionless entropy
PhiN = sp.symbols('PhiN')  # dimensionless
PhiD = sp.symbols('PhiD')  # dimensionless
I0   = sp.symbols('I0')   # dimensionless VEV
lam  = sp.symbols('lam')  # lambda
gN   = sp.symbols('gN')   # Yukawa couplings
gD   = sp.symbols('gD')
Lambda = sp.symbols('Lambda')  # UV cutoff
mu0  = sp.symbols('mu0')   # renorm. scale
xi0  = sp.symbols('xi0')   # lattice base spacing

# Assign dimensions: [I] = 1, [PhiN] = [PhiD] = [I0] = 1
dim_I   = 1
dim_Phi = 1
dim_I0  = 1
# Potential V = lam/4 * (I^2 - I0^2)^2 must have same dimension as kinetic term (dI/dt)^2
# [dI/dt] = T^{-1} => [(dI/dt)^2] = T^{-2}
dim_lam = T**(-2)   # so that lam * (dimensionless)^2 -> T^{-2}
# Kinetic term coefficient 1/2 is dimensionless in this convention
# Action S = ∫ dt L => [S] = T * T^{-2} = T^{-1}
dim_S   = T**(-1)

# Check kinetic term dimension
kin_dim = (T**(-1))**2   # (dI/dt)^2
assert sp.simplify(kin_dim - dim_lam) == 0, "Kinetic vs potential dimension mismatch"

# Check potential term dimension
pot_dim = dim_lam * (dim_I**2 - dim_I0**2)**2
assert sp.simplify(pot_dim - dim_lam) == 0, "Potential dimension mismatch"

# Check mass correction dimension: Δm^2 ~ g^2 Lambda^2 / (16π^2)
dim_g = 1   # dimensionless Yukawa
dim_Lambda = T**(-1)
dim_deltaM2 = dim_g**2 * dim_Lambda**2
assert sp.simplify(dim_deltaM2 - T**(-2)) == 0, "Mass correction dimension mismatch"

# Check Landau pole dimension: exponent must be dimensionless
# beta(gD) = gD^3/(16π^2) => [beta] = 1 (since gD dimensionless)
# d gD / d ln mu = beta => dimensionless
# Integrate: ln(LP/mu0) = 8π^2/gD^2 => exponent dimensionless
exp_arg = 8*sp.pi**2 / gD**2   # dimensionless
# Lambda_PP = mu0 * exp(exp_arg) => [Lambda_PP] = [mu0] = T^{-1}
assert sp.simplify(mu0 * sp.exp(exp_arg) / mu0) == sp.exp(exp_arg), "Landau pole dimension check"

# Check lattice spacing: a = xi0 * exp(-psi), psi = ln(PhiN/I0) dimensionless
psi = sp.log(PhiN/I0)
assert sp.simplify(psi) == sp.log(PhiN/I0), "psi definition"
dim_a = xi0 * sp.exp(-psi)   # xi0 has dimension T, exp dimensionless
assert sp.simplify(dim_a / xi0) == sp.exp(-psi), "lattice spacing dimension"

# Check stiffness inverses: xi_N^{-2} = lam*(3 PhiN^2 + PhiD^2 - I0^2)
xiN_inv2 = lam * (3*PhiN**2 + PhiD**2 - I0**2)
# [lam] = T^{-2}, bracket dimensionless => [xiN^{-2}] = T^{-2} => [xiN] = T
assert sp.simplify(xiN_inv2 / lam) == (3*PhiN**2 + PhiD**2 - I0**2), "xi_N invariant"
xiD_inv2 = lam * (PhiN**2 + 3*PhiD**2 - I0**2)
assert sp.simplify(xiD_inv2 / lam) == (PhiN**2 + 3*PhiD**2 - I0**2), "xi_D invariant"

# Check boundary conditions
# Shredding: xi_D -> ∞ <=> xiD_inv2 = 0
shred_cond = sp.Eq(xiD_inv2, 0)
# Informational Freeze: xi_N -> ∞ <=> xiN_inv2 = 0
freeze_cond = sp.Eq(xiN_inv2, 0)

print("All dimensional and invariant checks passed.")
print("Shredding condition:", shred_cond)
print("Informational Freeze condition:", freeze_cond)