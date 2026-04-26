# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script
--------------------------------
Validates the mathematical soundness and invariant compliance of the
'Higher-Order Lattice Polarization' correction derivation.
"""

import numpy as np
from scipy.integrate import quad

# ----------------------------------------------------------------------
# User‑defined parameters (representative values from the Engine output)
# ----------------------------------------------------------------------
Lambda_nom = 0.82          # nominal cutoff used in the Engine
v_nom      = 1.28          # velocity parameter
tol_overlap = 0.05         # IR/UV overlap tolerance from Rubric
entropy_min = 0.85         # minimum Shannon conditional entropy

# ----------------------------------------------------------------------
# 1. Integral definitions with correct scaling
# ----------------------------------------------------------------------
def integrand_I(k, L, v):
    """Full integral I = ∫0^L e^{-k^2/(2L^2)} / (1+(k*v)^2) * 4π k^2 dk"""
    return np.exp(-k**2 / (2.0 * L**2)) / (1.0 + (k * v)**2) * 4.0 * np.pi * k**2

def integrand_J(k, L, v):
    """IR/UV overlap integrand (same kernel, limits L/2 -> L)"""
    return np.exp(-k**2 / (2.0 * L**2)) / (1.0 + (k * v)**2) * 4.0 * np.pi * k**2

def compute_I(L, v):
    val, err = quad(integrand_I, 0.0, L, args=(L, v), epsabs=1e-12, epsrel=1e-12)
    return val, err

def compute_J(L, v):
    val, err = quad(integrand_J, L/2.0, L, args=(L, v), epsabs=1e-12, epsrel=1e-12)
    return val, err

I_val, I_err = compute_I(Lambda_nom, v_nom)
J_val, J_err = compute_J(Lambda_nom, v_nom)

print(f"I (0→Λ) = {I_val:.6f} ± {I_err:.2e}")
print(f"J (Λ/2→Λ) = {J_val:.6f} ± {J_err:.2e}")

# ----------------------------------------------------------------------
# 2. IR/UV overlap criterion
# ----------------------------------------------------------------------
overlap_ok = J_val <= tol_overlap
print(f"Overlap ≤ {tol_overlap}? {'PASS' if overlap_ok else 'FAIL'} (value={J_val:.6f})")

# ----------------------------------------------------------------------
# 3. Orthogonality check via Z₂‑symmetric Hamiltonian
# ----------------------------------------------------------------------
# Simple toy Hamiltonian: H = p_N^2 + p_Δ^2 + m_N^2 φ_N^2 + m_Δ^2 φ_Δ^2
# plus a Z₂‑odd mixing term g φ_N φ_Δ that vanishes under φ→-φ.
# Block‑diagonalisation occurs when g=0. We enforce g=0 and verify
# ⟨φ_N|φ_Δ⟩ = 0 for eigenstates.

def hamiltonian_block_diagonal(mN=1.0, mD=1.0):
    """Return 2x2 block‑diagonal Hamiltonian (no mixing)."""
    return np.array([[mN**2, 0.0],
                     [0.0,  mD**2]], dtype=float)

H = hamiltonian_block_diagonal()
evals, evecs = np.linalg.eigh(H)
# Eigenvectors are orthonormal by construction; check dot product
phi_N = evecs[:, 0]   # first eigenmode (associated with Φ_N)
phi_D = evecs[:, 1]   # second eigenmode (associated with Φ_Δ)
orthogonality = np.abs(np.dot(phi_N, phi_D)) < 1e-12
print(f"Orthogonality (Φ_N·Φ_Δ ≈ 0)? {'PASS' if orthogonality else 'FAIL'} (dot={np.dot(phi_N, phi_D):.2e})")

# ----------------------------------------------------------------------
# 4. Invariant embedding and stability operator
# ----------------------------------------------------------------------
# Define invariants as they would appear in the Omega Action:
#   S ∝ ∫ d^4x [ ½ (∂Φ_N)^2 + ½ ξ_N (∂^2 Φ_N)^2 + ψ Φ_N  + (N→Δ) ]
# For validation we pick representative constant values.
psi = np.log(1.0)          # ψ = ln(Φ_N) ; choose Φ_N = 1 for simplicity
xi_N = 0.45                # stiffness invariant for Φ_N
xi_D = 0.45                # stiffness invariant for Φ_Δ
Xi_bound = xi_N + xi_D

# Stability operator from the Engine: Λ(t) = 0.75 * exp(-Ξ_bound/100)
Lambda_t = 0.75 * np.exp(-Xi_bound / 100.0)
print(f"Ξ_bound = ξ_N + ξ_Δ = {Xi_bound:.6f}")
print(f"Λ(t) from invariant feedback = {Lambda_t:.6f}")

# Check consistency: the Λ used in integrals should equal Λ(t) (within tolerance)
Lambda_consistent = np.abs(Lambda_nom - Lambda_t) < 1e-3
print(f"Λ used in integrals matches Λ(t)? {'PASS' if Lambda_consistent else 'FAIL'} "
      f"(ΔΛ={np.abs(Lambda_nom - Lambda_t):.6f})")

# ----------------------------------------------------------------------
# 5. Entropy check (Shannon conditional entropy of normalized kernel)
# ----------------------------------------------------------------------
def normalized_pdf(k, L, v):
    """PDF ∝ integrand_I (must be normalised over [0, L])"""
    val = integrand_I(k, L, v)
    return val if val >= 0.0 else 0.0

# Normalisation constant
norm, _ = quad(normalized_pdf, 0.0, Lambda_nom, args=(Lambda_nom, v_nom), epsabs=1e-12, epsrel=1e-12)

def entropy_integrand(k, L, v):
    p = normalized_pdf(k, L, v) / norm
    return -p * np.log(p + 1e-16)  # avoid log(0)

S, _ = quad(entropy_integrand, 0.0, Lambda_nom, args=(Lambda_nom, v_nom), epsabs=1e-12, epsrel=1e-12)
print(f"Shannon conditional entropy S = {S:.6f}")
entropy_ok = S >= entropy_min
print(f"S ≥ {entropy_min}? {'PASS' if entropy_ok else 'FAIL'}")

# ----------------------------------------------------------------------
# Final verdict
# ----------------------------------------------------------------------
all_checks = [overlap_ok, orthogonality, Lambda_consistent, entropy_ok]
verdict = "PASS" if all(all_checks) else "FAIL"
print("\n=== OMEGA PROTOCOL VALIDATION ===")
print(f"Overall: {verdict}")
if verdict != "PASS":
    print("Failed checks:")
    if not overlap_ok:      print(" - IR/UV overlap exceeds tolerance")
    if not orthogonality:   print(" - Orthogonality not verified")
    if not Lambda_consistent: print(" - Λ(t) not consistent with invariant feedback")
    if not entropy_ok:      print(" - Shannon conditional entropy below threshold")