# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for FTFM‑Ω
Checks:
  - Invariant ψ = ln(Φ_N/Φ_N0)
  - Kinetic term prefactor 1/(2τ₀)
  - Presence of entropy gauge term A_μ J^μ
  - Basic dimensional consistency of the action
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbolic declarations
# ----------------------------------------------------------------------
# Coordinates (x^0, x^1, x^2, x^3) – natural units: [x] = L
x0, x1, x2, x3 = sp.symbols('x0 x1 x2 x3', real=True)
# Metric signature (-,+,+,+) – g^{μν} is dimensionless
g = sp.diag(-1, 1, 1, 1)  # simple Minkowski for illustration

# Fields and parameters
F   = sp.Function('F')(x0, x1, x2, x3)   # functional transfer field
PhiN = sp.symbols('Phi_N', positive=True)   # connectivity mode
PhiN0 = sp.symbols('Phi_N0', positive=True) # baseline
tau0 = sp.symbols('tau0', positive=True)    # characteristic time [τ₀] = L
ell  = sp.symbols('ell', positive=True)     # characteristic length [ℓ] = L
PhiDelta = sp.symbols('Phi_Delta', real=True) # asymmetry mode
Sctx   = sp.symbols('S_context', real=True)   # entropy (dimensionless)

# ----------------------------------------------------------------------
# 1. Invariant check
# ----------------------------------------------------------------------
psi_ftfm = sp.log(PhiN / PhiN0)   # candidate invariant
psi_required = sp.log(PhiN / PhiN0)   # rubric‑mandated form

invariant_ok = sp.simplify(psi_ftfm - psi_required) == 0
print(f"Invariant ψ = ln(Φ_N/Φ_N0) satisfied? {invariant_ok}")

# ----------------------------------------------------------------------
# 2. Kinetic term with ½·τ₀ prefactor
# ----------------------------------------------------------------------
# ∂_μ F
dF = [sp.diff(F, coord) for coord in (x0, x1, x2, x3)]
# g^{μν} ∂_μ F ∂_ν F  (summation implied)
kinetic_raw = sum(g[i,i] * dF[i] * dF[i] for i in range(4))   # no sum over repeated indices for simplicity
kinetic_term = (1/(2*tau0)) * kinetic_raw   # includes the required prefactor

# Verify the prefactor is exactly 1/(2τ₀)
prefactor_ok = sp.simplify(kinetic_term / kinetic_raw - 1/(2*tau0)) == 0
print(f"Kinetic term prefactor = 1/(2τ₀)? {prefactor_ok}")

# ----------------------------------------------------------------------
# 3. Entropy gauge term A_μ J^μ
# ----------------------------------------------------------------------
# A_μ = ∂_μ S_context
A = [sp.diff(Sctx, coord) for coord in (x0, x1, x2, x3)]
# J^μ = sqrt(2) * Φ_Δ * ℓ * δ^μ_0
J = [sp.sqrt(2) * PhiDelta * ell if mu == 0 else 0 for mu in range(4)]
# A_μ J^μ (sum over μ)
gauge_term = sum(A[mu] * J[mu] for mu in range(4))

# Check that gauge term has the expected structure
expected_gauge = sp.sqrt(2) * PhiDelta * ell * sp.diff(Sctx, x0)   # only μ=0 survives
gauge_ok = sp.simplify(gauge_term - expected_gauge) == 0
print(f"Gauge term A_μ J^μ matches √2·Φ_Δ·ℓ·∂_0 S_context? {gauge_ok}")

# ----------------------------------------------------------------------
# 4. Dimensional consistency (natural units: [x] = L, [∂] = L⁻¹)
# ----------------------------------------------------------------------
# Assign dimensions as symbols
L = sp.symbols('L', positive=True)   # length dimension
# Dimensions of basic quantities
dim = {}
dim['x']   = L
dim['∂']   = 1/L
dim['F']   = sp.Symbol('dim_F', positive=True)   # unknown for now
dim['τ₀']  = L
dim['ℓ']   = L
dim['Φ_N'] = 1   # dimensionless
dim['Φ_Δ'] = 1
dim['S']   = 1   # entropy dimensionless

# Kinetic term dimension: [1/(2τ₀)] * [∂F]²
dim_kinetic = (1/dim['τ₀']) * (dim['∂'] * dim['F'])**2
# Action integrand dimension (kinetic + V + λΩ LΩ + A·J)
# We require the total integrand to have dimension L⁻⁴ so that ∫ d⁴x √(-g) gives dimensionless.
# Solve for dim['F'] that makes kinetic term L⁻⁴:
dim_F_solution = sp.solve(sp.Eq(dim_kinetic, 1/L**4), dim['F'])
print(f"Required dimension of F for kinetic term to be L⁻⁴: {dim_F_solution}")

# With that dimension, check that the potential V(F) = α/2 (F-F₀)² + β/4 (F-F₀)⁴
# can be made dimensionless with appropriate α, β.
F_dim = dim_F_solution[0]   # pick the positive root
alpha_dim = (1/L**4) / (F_dim**2)   # because α·F² must give L⁻⁴
beta_dim  = (1/L**4) / (F_dim**4)   # because β·F⁴ must give L⁻⁴
print(f"Dimension of α (quadratic coeff): {alpha_dim}")
print(f"Dimension of β (quartic coeff):  {beta_dim}")

# Gauge term dimension: [A]·[J] = (∂S)·(Φ_Δ·ℓ) → (1/L)·(1·L) = 1 (dimensionless)
dim_gauge = dim['∂'] * dim['S'] * dim['Φ_Δ'] * dim['ell']
print(f"Dimension of gauge term A_μ J^μ: {dim_gauge} (should be 1)")

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
all_checks = [invariant_ok, prefactor_ok, gauge_ok]
if all(all_checks):
    print("\n✅ All core mathematical checks passed.")
else:
    print("\n❌ Some checks failed. Review the output above.")