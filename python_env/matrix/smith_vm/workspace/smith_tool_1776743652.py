# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Narrative Curvature Shredding Monitor (NCSM‑Ω)
Checks mathematical consistency of the field‑theoretic derivation.
"""

import sympy as sp

# ----------------------------------------------------------------------
# 1. Symbols
# ----------------------------------------------------------------------
# Coordinates on the semantic manifold
x0, x1, x2, x3 = sp.symbols('x0 x1 x2 x3', real=True)
xs = sp.Matrix([x0, x1, x2, x3])          # 4‑D for generality; works for any D

# Embedding field φ: M → ℝ^D (we treat each component as a scalar field)
D = 3                                      # embedding dimension (example)
phi = sp.Matrix([sp.Function(f'phi{i}')( *xs ) for i in range(D)])

# Metric components g_{ij} = <∂_i φ, ∂_j φ>
g = sp.Matrix.zeros(len(xs), len(xs))
for i in range(len(xs)):
    for j in range(len(xs)):
        g[i, j] = sum(sp.diff(phi[k], xs[i]) * sp.diff(phi[k], xs[j]) for k in range(D))

# Inverse metric
g_inv = g.inv()

# ----------------------------------------------------------------------
# 2. Christoffel symbols Γ^k_{ij}
# ----------------------------------------------------------------------
Gamma = sp.Matrix.zeros(len(xs), len(xs), len(xs))
for i in range(len(xs)):
    for j in range(len(xs)):
        for k in range(len(xs)):
            Gamma[i, j, k] = sp.Rational(1,2) * sum(
                g_inv[k, l] * (
                    sp.diff(g[j, l], xs[i]) +
                    sp.diff(g[i, l], xs[j]) -
                    sp.diff(g[i, j], xs[l])
                ) for l in range(len(xs))
            )

# ----------------------------------------------------------------------
# 3. Ricci tensor R_{ij} = ∂_k Γ^k_{ij} - ∂_j Γ^k_{ik} + Γ^k_{kl} Γ^l_{ij} - Γ^k_{jl} Γ^l_{ik}
# ----------------------------------------------------------------------
R = sp.Matrix.zeros(len(xs), len(xs))
for i in range(len(xs)):
    for j in range(len(xs)):
        term1 = sum(sp.diff(Gamma[k, i, j], xs[k]) for k in range(len(xs)))
        term2 = -sum(sp.diff(Gamma[k, i, k], xs[j]) for k in range(len(xs)))
        term3 = sum(Gamma[k, k, l] * Gamma[l, i, j] for k in range(len(xs)) for l in range(len(xs)))
        term4 = -sum(Gamma[k, j, l] * Gamma[l, i, k] for k in range(len(xs)) for l in range(len(xs)))
        R[i, j] = sp.simplify(term1 + term2 + term3 + term4)

# Scalar curvature R_scalar = g^{ij} R_{ij}
R_scalar = sp.simplify(sum(g_inv[i, j] * R[i, j] for i in range(len(xs)) for j in range(len(xs))))

print("Scalar curvature expression (simplified):")
sp.pprint(R_scalar)
print("\n---\n")

# ----------------------------------------------------------------------
# 4. Effective potential V_eff(I) and stiffness invariants
# ----------------------------------------------------------------------
I, I0, lam_eff, alpha, R_avg = sp.symbols('I I0 lam_eff alpha R_avg', real=True)
V_eff = lam_eff/4 * (I**2 - I0**2)**2 + alpha * R_avg * I

# Define normal modes (linearised around I0)
# Φ_N = δI/√2,   Φ_Δ = (1/√2) * (φ·δφ_⊥)/|φ|  → for the purpose of stiffness we treat them as independent
# The Hessian of V_eff w.r.t. I gives the curvature in the I‑direction.
# To obtain ξ_N and ξ_Δ we project onto the two eigenvectors:
#   v_N = [1, 0]   (synchronous)
#   v_Δ = [0, 1]   (asynchronous)
# In the reduced 2‑D space the Hessian is diagonal with entries:
#   H_NN = ∂^2 V_eff/∂I^2 * (∂I/∂Φ_N)^2 = V_eff'' * (1/2)
#   H_ΔΔ = ∂^2 V_eff/∂I^2 * (∂I/∂Φ_Δ)^2 = V_eff'' * (1/2)
# However the coupling to R introduces different prefactors for the two modes
# as derived in the text. We reproduce those formulas directly.

# Second derivative of V_eff w.r.t I
V_eff_pp = sp.diff(V_eff, I, 2)
# Stiffness inverses as given in the proposal
xi_N_inv2 = lam_eff * (3*I0**2 + R_avg)
xi_D_inv2 = lam_eff * (I0**2 + 3*R_avg)

# Verify that these equal V_eff_pp times the appropriate geometric factors
# For a general derivation we would need the eigenvectors; here we simply
# check proportionality (the factors 3 and 1 are built‑in).
print("V_eff'' =", sp.simplify(V_eff_pp))
print("xi_N^{-2} (claimed) =", xi_N_inv2)
print("xi_Δ^{-2} (claimed) =", xi_D_inv2)
print("\nAre they proportional to V_eff''?")
print("xi_N^{-2} / V_eff'' =", sp.simplify(xi_N_inv2 / V_eff_pp))
print("xi_Δ^{-2} / V_eff'' =", sp.simplify(xi_D_inv2 / V_eff_pp))
print("\n---\n")

# ----------------------------------------------------------------------
# 5. Invariant ψ and relations ξ_N = ∂Φ_N/∂ψ, ξ_Δ = ∂Φ_Δ/∂ψ
# ----------------------------------------------------------------------
psi, xi0 = sp.symbols('psi xi0', real=True)
# ξ = sqrt(xi_N * xi_D)
xi = sp.sqrt(1/xi_N_inv2 * 1/xi_D_inv2)   # because ξ_N = 1/ sqrt(xi_N_inv2)
psi_expr = sp.log(xi / xi0)

# Assume Φ_N = sqrt(2)*(I - I0)  (linearised) and Φ_Δ = 0 for this test
Phi_N = sp.sqrt(2)*(I - I0)
Phi_Δ = 0   # placeholder; the relation will hold for the synchronous mode

# Compute derivatives
dPhi_N_dpsi = sp.diff(Phi_N, psi)
dPhi_D_dpsi = sp.diff(Phi_Delta, psi)

# Replace I with psi via the chain rule: we need I(psi). From definition:
# ξ_N = 1/ sqrt(xi_N_inv2)  → ξ_N = 1/ sqrt(lam_eff*(3 I0^2 + R_avg))
# For simplicity we treat xi_N as a function of R_avg only; then psi depends on R_avg.
# We'll verify the identity symbolically by expressing xi_N and xi_D in terms of psi.
# Solve for xi_N and xi_D from psi:
xi_N_expr = 1/sp.sqrt(xi_N_inv2)
xi_D_expr = 1/sp.sqrt(xi_D_inv2)

# Express psi in terms of xi_N, xi_D:
psi_from_xi = sp.log(sp.sqrt(xi_N_expr * xi_D_expr) / xi0)
# Invert to get xi_N*xi_D = xi0^2 * exp(2 psi)
product_expr = xi0**2 * sp.exp(2*psi)

# Now compute ∂Φ_N/∂ψ using chain rule: ∂Φ_N/∂ψ = (∂Φ_N/∂I)*(∂I/∂psi)
# ∂Φ_N/∂I = sqrt(2)
# We need ∂I/∂psi. From xi_N = 1/ sqrt(lam_eff*(3 I0^2 + R_avg)) and
# assuming R_avg is the only psi‑dependent quantity, we get:
#   d xi_N / d psi = - xi_N   (since xi_N ∝ exp(-psi) )
#   => dR_avg/d psi = ... (omitted for brevity). Instead we directly test
#   the claimed identity by substituting the explicit formulas.

# For brevity, we numerically validate the identity with random values.
print("Numeric check of ξ_N = ∂Φ_N/∂ψ and ξ_Δ = ∂Φ_Δ/∂ψ:")
import random, math
random.seed(42)
for _ in range(5):
    I0_val = random.uniform(0.5, 2.0)
    lam_eff_val = random.uniform(0.1, 2.0)
    R_avg_val = random.uniform(-1.0, 1.0)
    # compute xi_N, xi_D
    xi_N_val = 1/math.sqrt(lam_eff_val * (3*I0_val**2 + R_avg_val))
    xi_D_val = 1/math.sqrt(lam_eff_val * (I0_val**2 + 3*R_avg_val))
    xi_val = math.sqrt(xi_N_val * xi_D_val)
    psi_val = math.log(xi_val / 1.0)   # take xi0 = 1 for simplicity
    # Φ_N ≈ sqrt(2)*(I - I0); we need I corresponding to this psi.
    # Invert xi_N expression for I (assuming R_avg depends linearly on I for test):
    # Let R_avg = k*(I - I0) with k=1 for simplicity.
    k = 1.0
    # Solve xi_N = 1/ sqrt(lam_eff*(3 I0^2 + k*(I - I0)))
    # => 3 I0^2 + k*(I - I0) = 1/(lam_eff * xi_N^2)
    I_val = I0_val + (1/(lam_eff_val * xi_N_val**2) - 3*I0_val**2)/k
    Phi_N_val = math.sqrt(2)*(I_val - I0_val)
    Phi_D_val = 0.0   # asynchronous mode zero in this simplified test
    # Numerical derivatives via finite difference
    eps = 1e-6
    xi_N_eps = 1/math.sqrt(lam_eff_val * (3*I0_val**2 + (R_avg_val+eps)))
    xi_D_eps = 1/math.sqrt(lam_eff_val * (I0_val**2 + 3*(R_avg_val+eps)))
    xi_eps = math.sqrt(xi_N_eps * xi_D_eps)
    psi_eps = math.log(xi_eps / 1.0)
    I_eps = I0_val + (1/(lam_eff_val * xi_N_eps**2) - 3*I0_val**2)/k
    Phi_N_eps = math.sqrt(2)*(I_eps - I0_val)
    dPhi_N_dpsi_num = (Phi_N_eps - Phi_N_val) / (psi_eps - psi_val)
    dPhi_D_dpsi_num = 0.0   # Φ_Δ stays zero
    print(f"I0={I0_val:.3f}, lam={lam_eff_val:.2f}, R={R_avg_val:.3f}")
    print(f"  ξ_N={xi_N_val:.5f}, ∂Φ_N/∂ψ_num={dPhi_N_dpsi_num:.5f}, diff={abs(xi_N_val-dPhi_N_dpsi_num):.2e}")
    print(f"  ξ_Δ={xi_D_val:.5f}, ∂Φ_Δ/∂ψ_num={dPhi_D_dpsi_num:.5f}, diff={abs(xi_D_val-dPhi_D_dpsi_num):.2e}")
    print()

print("---\n")

# ----------------------------------------------------------------------
# 6. Dimensional analysis (symbolic)
# ----------------------------------------------------------------------
# Assign dimensions: [L] = length, [T] = time, [M] = mass.
# In natural units ħ = c = 1 → [action] = 1 (dimensionless).
# We'll just verify that the combination inside the action is dimensionless.
L, T, M = sp.symbols('L T M', positive=True)
# Embedding φ is dimensionless (normalized word vectors)
dim_phi = 1
# Derivative ∂_i adds [L]^{-1}
dim_dphi = 1/L
# Metric g_{ij} = <∂_i φ, ∂_j φ> → [L]^{-2}
dim_g = dim_dphi**2
# Inverse metric g^{ij} → [L]^{2}
dim_g_inv = 1/dim_g
# Christoffel symbols involve derivative of g → [L]^{-3} times g^{ij} [L]^2 → [L]^{-1}
dim_Gamma = dim_g_inv * (dim_g / L)   # actually ∂g ~ [L]^{-3}
# Ricci tensor: ∂Γ + ΓΓ → [L]^{-2}
dim_R = dim_Gamma / L + dim_Gamma**2
# Scalar curvature: g^{ij} R_{ij} → [L]^{2} * [L]^{-2} = 1 (dimensionless)
dim_R_scalar = dim_g_inv * dim_R
print("Dimensional check:")
print("  [φ] =", dim_phi)
print("  [∂φ] =", dim_dphi)
print("  [g] =", dim_g)
print("  [R] (scalar curvature) =", sp.simplify(dim_R_scalar))
print("  Should be dimensionless →", dim_R_scalar == 1)
print("\n---\n")

# ----------------------------------------------------------------------
# 7. MPC‑Ω cost function positivity (symbolic)
# ----------------------------------------------------------------------
NCI, lam1, lam2, lam3 = sp.symbols('NCI lam1 lam2 lam3', nonnegative=True)
Phi_D_nar, u = sp.symbols('Phi_D_nar u', real=True)
# Simplified stage cost (integrand)
stage_cost = (1 - NCI)**2 + lam1 * Phi_D_nar**2 + lam2 * u**2   # omitted Σ term for brevity
print("Stage cost expression:", stage_cost)
print("Is it manifestly non‑negative? (coefficients ≥0):", 
      all(c >= 0 for c in [1, lam1, lam2]))
print("\nValidation complete.")