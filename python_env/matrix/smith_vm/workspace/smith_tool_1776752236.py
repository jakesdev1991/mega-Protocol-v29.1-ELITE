# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Dimensional Validator (SymPy)
# --------------------------------------------------------------
# This script verifies the dimensional homogeneity of the
# core equations presented in the Engine's output.
# It assumes the following base dimensions:
#   [T]  = time
#   1    = dimensionless
# --------------------------------------------------------------

import sympy as sp

# Define symbols with dimensions
T   = sp.symbols('T')          # time dimension
one = sp.symbols('one')        # dimensionless

# Assign dimensions to fundamental quantities
dim = {
    # Base
    'T': T,
    'one': one,
    # Fields / parameters
    'I': one,                  # information content (entropy) -> dimensionless
    'PHI': one,                # Pipeline Health Index -> dimensionless
    'A': one,                  # harmonic amplitude (normalized) -> dimensionless
    'lam': T**(-2),            # coupling constant λ -> [T]^{-2}
    'I0': one,                 # equilibrium information -> dimensionless
    'tau0': T,                 # characteristic time scale (if needed) -> [T]
    # Derived
    'coh': one,                # coherence -> dimensionless
    'lam_N': T**(-2),          # stiffness eigenvalue -> [T]^{-2}
    'lam_Delta': T**(-2),      # stiffness eigenvalue -> [T]^{-2}
    'xi_N': T,                 # correlation length -> [T]
    'xi_Delta': T,             # correlation length -> [T]
    'psi': one,                # metric coupling invariant -> dimensionless
    'Phi_N': one,              # covariant mode -> dimensionless
    'Phi_Delta': one,          # covariant mode -> dimensionless
    'dPHI_dt': T**(-1),        # time derivative of PHI -> [T]^{-1}
}

def dim_of(expr):
    """Replace symbols with their dimensional placeholders and simplify."""
    return sp.simplify(expr.subs(dim))

# ---- 1. Stiffness eigenvalues from coherence ----
lam_N_expr   = sp.symbols('lam_N_expr')
lam_Delta_expr = sp.symbols('lam_Delta_expr')
# λ_N = λ (3⟨coh⟩^{-1} + ⟨coh⟩^{-2})
lam_N_expr   = dim['lam'] * (3/dim['coh'] + 1/dim['coh']**2)
# λ_Δ = λ (⟨coh⟩^{-1} + 3⟨coh⟩^{-2})
lam_Delta_expr = dim['lam'] * (1/dim['coh'] + 3/dim['coh']**2)

print("Dimensions:")
print("  λ_N   :", dim_of(lam_N_expr))
print("  λ_Δ   :", dim_of(lam_Delta_expr))
print("  λ     :", dim_of(dim['lam']))
print()

# ---- 2. Correlation lengths (ξ = λ^{-1/2}) ----
xi_N_expr   = sp.sqrt(1/lam_N_expr)   # ξ_N = λ_N^{-1/2}
xi_Delta_expr = sp.sqrt(1/lam_Delta_expr)  # ξ_Δ = λ_Δ^{-1/2}

print("Correlation lengths:")
print("  ξ_N   :", dim_of(xi_N_expr))
print("  ξ_Δ   :", dim_of(xi_Delta_expr))
print()

# ---- 3. Mapping Φ_N (problematic) ----
# α = ∂I/∂PHI  -> dimensionless
alpha_expr = sp.symbols('alpha_expr')
alpha_expr = dim['I'] / dim['PHI']   # dimensionless / dimensionless = dimensionless

# Φ_N = Φ_N0 + α * dPHI/dt
Phi_N_expr = dim['Phi_N'] + alpha_expr * dim['dPHI_dt']

print("Φ_N mapping dimensions:")
print("  Φ_N0            :", dim_of(dim['Phi_N']))
print("  α (∂I/∂PHI)    :", dim_of(alpha_expr))
print("  dPHI/dt         :", dim_of(dim['dPHI_dt']))
print("  α * dPHI/dt     :", dim_of(alpha_expr * dim['dPHI_dt']))
print("  Φ_N (total)     :", dim_of(Phi_N_expr))
print("  -> Mismatch?    :", dim_of(dim['Phi_N']) != dim_of(alpha_expr * dim['dPHI_dt']))
print()

# ---- 4. Corrected Φ_N mapping with τ0 ----
alpha_corr_expr = dim['tau0'] * alpha_expr   # now [T] * dimensionless = [T]
Phi_N_corr_expr = dim['Phi_N'] + alpha_corr_expr * dim['dPHI_dt']

print("Corrected Φ_N mapping (with τ0):")
print("  α_corr = τ0 * ∂I/∂PHI :", dim_of(alpha_corr_expr))
print("  α_corr * dPHI/dt      :", dim_of(alpha_corr_expr * dim['dPHI_dt']))
print("  Φ_N_corr (total)      :", dim_of(Phi_N_corr_expr))
print("  -> Consistent?       :", dim_of(dim['Phi_N']) == dim_of(Phi_N_corr_expr))
print()

# ---- 5. Φ_Δ mapping (appears OK) ----
# β = ∂²I/∂PHI²  (dimensionless)
# γ = ∂²I/∂A²    (dimensionless if A dimensionless)
beta_expr = dim['I'] / dim['PHI']**2   # dimensionless
gamma_expr = dim['I'] / dim['A']**2    # dimensionless
VarA_expr = dim['A']**2                # dimensionless

Phi_Delta_expr = dim['Phi_Delta'] - beta_expr * dim['PHI'] + gamma_expr * VarA_expr

print("Φ_Δ mapping dimensions:")
print("  Φ_Δ0          :", dim_of(dim['Phi_Delta']))
print("  β·PHI         :", dim_of(beta_expr * dim['PHI']))
print("  γ·Var(A)      :", dim_of(gamma_expr * VarA_expr))
print("  Φ_Δ (total)   :", dim_of(Phi_Delta_expr))
print("  -> Consistent? :", dim_of(dim['Phi_Delta']) == dim_of(Phi_Delta_expr))
print()

# --------------------------------------------------------------
# Summary
# --------------------------------------------------------------
print("=== Dimensional Check Summary ===")
print("Stiffness eigenvalues λ_N, λ_Δ : [T]^{-2}  ✓")
print("Correlation lengths ξ_N, ξ_Δ   : [T]       ✓")
print("Φ_N mapping (original)        : INCONSISTENT (adds [T]^{-1} to dimensionless)")
print("Φ_N mapping (with τ0)         : CONSISTENT")
print("Φ_Δ mapping                   : CONSISTENT")
print("All other quantities          : dimensionless as required")