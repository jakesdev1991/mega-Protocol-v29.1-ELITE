# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Define symbolic dimensions: [L] = length, everything else dimensionless
L = sp.symbols('L', positive=True)
# Dimensions: action S dimensionless, gauge field A_mu ~ 1/L, 
# lattice spacing a ~ L, bare coupling alpha0 dimensionless
# c0, f(Nt) dimensionless, pi dimensionless
# m0^2 ~ 1/L^2, delta m^2 ~ 1/L^2, psi argument dimensionless

# Dimensions of basic quantities
dim_alpha0 = 1          # dimensionless
dim_a = L               # length
dim_pi = 1
dim_c0 = 1
dim_f = 1               # f(Nt) dimensionless
dim_m0_sq = 1 / dim_a**2   # π/a^2 -> 1/L^2
dim_delta_m_sq = (dim_alpha0**2 * dim_c0 * dim_f) / (dim_pi * dim_a**2)  # α0^2 c0 f / (π a^2)

# Check mass‑shift dimension matches m0^2
assert sp.simplify(dim_delta_m_sq - dim_m0_sq) == 0, "Mass‑shift dimension mismatch"

# Invariant psi argument: 1 + (α0^2/π^2) c0 f(Nt)
dim_psi_arg = 1 + (dim_alpha0**2 / dim_pi**2) * dim_c0 * dim_f
assert dim_psi_arg == 1, "Psi argument not dimensionless"

# Stability condition: argument > 0  =>  c0 > -π^2/(α0^2 f)
# Since all dimensionless, we can test symbolically
c0_sym = sp.symbols('c0', real=True)
alpha0_sym = sp.symbols('alpha0', positive=True)
f_sym = sp.symbols('f', positive=True)
psi_arg_sym = 1 + (alpha0_sym**2 / sp.pi**2) * c0_sym * f_sym
stability_cond = sp.simplify(psi_arg_sym > 0)
# Solve for c0 bound
c0_bound = sp.solve(sp.Eq(psi_arg_sym, 0), c0_sym)[0]
assert sp.simplify(c0_bound) == -sp.pi**2 / (alpha0_sym**2 * f_sym), "Stability bound incorrect"

# Optional: numeric sanity check
def check_numeric(alpha0_val, c0_val, f_val):
    arg = 1 + (alpha0_val**2 / (sp.pi**2)) * c0_val * f_val
    assert arg > 0, f"Psi argument non‑positive: {arg}"
    psi = sp.log(arg)
    return psi.evalf()

# Example values
print("Numeric psi for α0=1/137, c0=-0.1, f=0.9:", check_numeric(1/137, -0.1, 0.9))
print("All dimensional and stability checks passed.")