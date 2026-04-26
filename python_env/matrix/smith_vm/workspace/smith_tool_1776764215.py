# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Dimensional consistency check for the Omega Action derivation
import sympy as sp

# Define base dimension: [T] for time
T = sp.symbols('T')
# Assign dimensions to fundamental quantities
dim_I = 1                     # I is dimensionless (entropy)
dim_lambda = T**(-2)          # potential coefficient λ has [T]⁻²
dim_xi = T                    # stiffnesses ξ_N, ξ_Δ have [T]
dim_psi = 1                   # ψ = ln(Φ_N/I₀) dimensionless
dim_g = 1                     # Yukawa couplings g_N, g_Δ dimensionless
dim_dt = T                    # differential dt has [T]
dim_dIdt = dim_I / dim_dt     # dI/dt has [T]⁻¹
dim_action = dim_dIdt**2 * dim_dt  # (dI/dt)² dt → [T]⁻¹

# Verify action integrand dimensions
kinetic = dim_dIdt**2 * dim_dt   # ½ (dI/dt)² dt
potential = dim_lambda * dim_I**4 * dim_dt  # λ/4 (I²-I₀²)² dt → λ I⁴ dt
# Both should equal [T]⁻¹
print("Kinetic term dimension:", kinetic)
print("Potential term dimension:", potential)
print("Action dimension expected:", dim_action)
print("Kinetic matches action?", kinetic.simplify() == dim_action)
print("Potential matches action?", potential.simplify() == dim_action)

# Check mass correction dimensions: Δm² ∼ g² Λ² / (16π²)
# Λ (UV cutoff) has dimension [T]⁻¹ (inverse length in natural units)
dim_Lambda = T**(-1)
dim_mass_correction = dim_g**2 * dim_Lambda**2  # g² Λ² → [T]⁻²
print("\nMass correction dimension:", dim_mass_correction)
print("Expected [T]⁻²?", dim_mass_correction == T**(-2))

# Check beta function β(g_Δ) = g_Δ³/(16π²) → dimensionless
dim_beta = dim_g**3  # dimensionless
print("\nBeta function dimension:", dim_beta)
print("Dimensionless?", dim_beta == 1)

# Check lattice spacing a = ξ₀ e^{-ψ}
dim_a = dim_xi * sp.exp(-dim_psi)  # ξ₀ [T], exponent dimensionless
print("\nLattice spacing dimension:", dim_a)
print("Should be [T]?", dim_a.simplify() == dim_xi)

# If all checks pass, output success
if (kinetic.simplify() == dim_action and
    potential.simplify() == dim_action and
    dim_mass_correction == T**(-2) and
    dim_beta == 1 and
    dim_a.simplify() == dim_xi):
    print("\nAll dimensional checks passed – derivation is dimensionally consistent.")
else:
    print("\nDimensional mismatch detected – revision required.")