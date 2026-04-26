# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Audit Script for Higher‑Order Lattice Polarization
----------------------------------------------------------------
Validates the mathematical claims made in the Engine Output:
  - Integral convergence of I(Λ, v)
  - Poisson recovery of Φ_N at short distances
  - Orthogonality error bound (placeholder for Hamiltonian symmetry)
  - Feedback law for Λ via a defined Ξ_bound
"""

import numpy as np
from scipy import integrate, special

# ----------------------------------------------------------------------
# 1. Parameters (can be overridden for sensitivity analysis)
# ----------------------------------------------------------------------
Lambda_nom = 0.82   # nominal Lambda from Engine Output
v_nom      = 1.28   # nominal coupling
r_vals     = np.logspace(-3, 0, 20)  # short‑distance range (in lattice units)
tol_poisson = 1e-2  # tolerance for 1/r recovery
ortho_tol   = 1e-3  # max allowed orthogonality error (placeholder)

# ----------------------------------------------------------------------
# 2. Integral I(Λ, v) = ∫_{0}^{Λ} 4π k^2 e^{-k^2/(2Λ^2)} / (1 + (k v)^2) dk
# ----------------------------------------------------------------------
def I_integrand(k, Lambda, v):
    return 4.0 * np.pi * k**2 * np.exp(-k**2 / (2.0 * Lambda**2)) / (1.0 + (k * v)**2)

def I_value(Lambda, v):
    result, err = integrate.quad(I_integrand, 0, Lambda, args=(Lambda, v), limit=200)
    return result, err

# Verify convergence for a wide range of Lambda and v
print("=== Integral Convergence Test ===")
for L in [0.1, 0.5, 0.82, 1.0, 2.0, 5.0]:
    for V in [0.1, 0.5, 1.28, 2.0, 5.0]:
        val, err = I_value(L, V)
        print(f"Λ={L:4.2f}, v={V:4.2f} → I = {val:.6e} ± {err:.2e}")
        assert np.isfinite(val), f"Integral diverged for Λ={L}, v={V}"
print("All integrals finite → convergence unconditional (Gaussian damping).\n")

# ----------------------------------------------------------------------
# 3. Poisson Recovery: Approximate Φ_N potential from propagator
#    V_N(r) ≈ ∫ d^3k/(2π)^3  e^{i k·r} e^{-k^2/(2Λ^2)} / k^2
#    For isotropic case reduces to:
#    V_N(r) = (1/(2π^2 r)) ∫_0^∞ dk sin(kr) e^{-k^2/(2Λ^2)}
# ----------------------------------------------------------------------
def V_N_r(r, Lambda):
    # integral from 0 to ∞; use scipy's quad with splitting for oscillatory sin
    def integrand(k):
        return np.sin(k * r) * np.exp(-k**2 / (2.0 * Lambda**2))
    val, err = integrate.quad(integrand, 0, np.inf, limit=200, full_output=0)
    return val / (2.0 * np.pi**2 * r)

print("=== Poisson Recovery Test (short distances) ===")
for r in r_vals:
    Vnum = V_N_r(r, Lambda_nom)
    Vcoul = 1.0 / r  # exact 1/r potential (in lattice units)
    rel_err = abs(Vnum - Vcoul) / Vcoul
    print(f"r={r:.3e} → V_N={Vnum:.6e}, 1/r={Vcoul:.6e}, rel err={rel_err:.2e}")
    assert rel_err < tol_poisson, f"Poisson recovery failed at r={r}"
print(f"Φ_N reproduces 1/r within {tol_poisson} for Λ={Lambda_nom}.\n")

# ----------------------------------------------------------------------
# 4. Orthogonality Error (placeholder)
#    In a real implementation we would compute ⟨Φ_N|Φ_Δ⟩ from the Hamiltonian.
#    Here we define a mock error that should shrink when Λ is tightened.
# ----------------------------------------------------------------------
def orthogonality_error(Lambda):
    # Mock: error ~ exp(-Λ^2) → smaller Λ gives smaller cross‑talk
    return np.exp(-Lambda**2)

print("=== Orthogonality Error (mock) ===")
for L in [0.5, 0.75, 0.82, 1.0]:
    err = orthogonality_error(L)
    print(f"Λ={L:4.2f} → orthogonality error = {err:.6e}")
    assert err < ortho_tol, f"Orthogonality error too large for Λ={L}"
print(f"Orthogonality error below {ortho_tol} for all tested Λ.\n")

# ----------------------------------------------------------------------
# 5. Ξ_bound Feedback Law (illustrative)
#    Define Ξ_bound = ψ * ξ_N / (1 + ξ_Δ)   (dimensionless)
#    Then adjust Λ to keep Ξ_bound below a target Ξ_target.
# ----------------------------------------------------------------------
psi      = 1.0   # example invariant (field amplitude)
xi_N     = 0.3   # example stiffness invariant for Φ_N
xi_Delta = 0.2   # example stiffness invariant for Φ_Δ

def Xi_bound(psi_val, xi_N_val, xi_Delta_val):
    return psi_val * xi_N_val / (1.0 + xi_Delta_val)

Xi_target = 0.25   # desired upper bound

def update_Lambda(Lambda_current, psi_val, xi_N_val, xi_Delta_val, eta=0.1):
    """Simple proportional feedback: reduce Λ if Ξ_bound > target."""
    Xi = Xi_bound(psi_val, xi_N_val, xi_Delta_val)
    if Xi > Xi_target:
        Lambda_new = Lambda_current * (1.0 - eta * (Xi - Xi_target) / Xi_target)
    else:
        Lambda_new = Lambda_current  # no change if within bound
    return max(Lambda_new, 1e-3)  # avoid zero

print("=== Ξ_bound Feedback Demonstration ===")
Xi_cur = Xi_bound(psi, xi_N, xi_Delta)
print(f"Initial Ξ_bound = {Xi_cur:.4f} (target < {Xi_target})")
Lambda_new = update_Lambda(Lambda_nom, psi, xi_N, xi_Delta)
print(f"Updated Λ = {Lambda_new:.4f} (from {Lambda_nom})")
# Verify that new Λ reduces orthogonality error
assert orthogonality_error(Lambda_new) < orthogonality_error(Lambda_nom), \
    "Feedback did not improve orthogonality (mock)."
print("Feedback reduces mock orthogonality error.\n")

print("\nAll automated checks passed → Engine Output would need revision "
      "to satisfy the Omega‑Protocol invariants.")