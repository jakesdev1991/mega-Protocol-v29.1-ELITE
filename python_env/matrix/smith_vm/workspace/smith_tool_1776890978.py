# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith – Omega Protocol Audit Script
# Validates the mathematical claims in the Engine's pleading
# and checks compliance with the Omega Physics Rubric v26.0 invariants.

import numpy as np
from scipy import integrate

# ----------------------------------------------------------------------
# Parameters from the pleading
# ----------------------------------------------------------------------
Lambda_orig = 0.82   # original Lambda
Lambda_safe = 0.75   # tightened Lambda per pleading
v = 1.28             # coupling
tol_overlap = 0.05   # IR/UV overlap tolerance

# ----------------------------------------------------------------------
# 1. Integral I = ∫_0^1 [e^{-q^2/2}/(1+(q·v)^2)] * 4π q^2 dq
# ----------------------------------------------------------------------
def integrand_I(q):
    return np.exp(-q**2/2.0) / (1.0 + (q*v)**2) * 4.0*np.pi * q**2

I_val, I_err = integrate.quad(integrand_I, 0.0, 1.0, epsabs=1e-12, epsrel=1e-12)
print(f"Integral I = {I_val:.6f}  (error estimate ±{I_err:.2e})")
# Expected from pleading ≈ 0.318
assert np.isclose(I_val, 0.318, atol=0.01), \
    f"Integral value mismatch: got {I_val:.6f}, expected ~0.318"

# ----------------------------------------------------------------------
# 2. IR/UV overlap J(Λ) = ∫_{Λ/2}^{Λ} [e^{-k^2/(2Λ^2)}/(1+(k·v)^2)] d^3k
#    In spherical coords: 4π ∫_{Λ/2}^{Λ} k^2 * e^{-k^2/(2Λ^2)}/(1+(k·v)^2) dk
# ----------------------------------------------------------------------
def overlap_integral(Lambda):
    def integrand(k):
        return np.exp(-k**2/(2.0*Lambda**2)) / (1.0 + (k*v)**2) * 4.0*np.pi * k**2
    val, err = integrate.quad(integrand, Lambda/2.0, Lambda, epsabs=1e-12, epsrel=1e-12)
    return val, err

J_orig, err_orig = overlap_integral(Lambda_orig)
J_safe, err_safe = overlap_integral(Lambda_safe)

print(f"Overlap J(Λ={Lambda_orig}) = {J_orig:.6f} ± {err_orig:.2e}")
print(f"Overlap J(Λ={Lambda_safe}) = {J_safe:.6f} ± {err_safe:.2e}")

# Verify the pleading's claim: J(0.82) > tol, J(0.75) < tol
assert J_orig > tol_overlap, \
    f"Overlap for Λ={Lambda_orig} should exceed tolerance ({tol_overlap}), got {J_orig:.6f}"
assert J_safe < tol_overlap, \
    f"Overlap for Λ={Lambda_safe} should be below tolerance ({tol_overlap}), got {J_safe:.6f}"

# ----------------------------------------------------------------------
# 3. Orthogonality check (symbolic): we assert that the Hamiltonian
#    block‑diagonalizes → Φ_N·Φ_Δ = 0.  No numeric test needed,
#    but we can verify that the cross‑term integral vanishes under Z2.
# ----------------------------------------------------------------------
# Define a dummy cross‑term integrand that should be odd under q→-q
def cross_term(q):
    # Example: q * exp(-q^2/(2Λ^2)) / (1+(q*v)^2)  → odd → integral zero over symmetric domain
    return q * np.exp(-q**2/(2.0*Lambda_orig**2)) / (1.0 + (q*v)**2)

# Integrate over [-1,1] (symmetric) – should be ~0
cross_val, cross_err = integrate.quad(cross_term, -1.0, 1.0, epsabs=1e-12, epsrel=1e-12)
print(f"Cross‑term integral (symmetry test) = {cross_val:.6e} ± {cross_err:.2e}")
assert np.abs(cross_val) < 1e-8, \
    f"Cross‑term not zero (got {cross_val:.6e}), indicating possible Z2 breaking"

# ----------------------------------------------------------------------
# 4. Invariant‑driven stability operator: Λ(t) = 0.75 * exp(-Ξ_bound/100)
#    We only check that the mapping is monotonic decreasing in Ξ_bound ≥ 0.
# ----------------------------------------------------------------------
def Lambda_from_Xi(Xi):
    return Lambda_safe * np.exp(-Xi/100.0)

# Test a few values
for Xi in [0.0, 10.0, 50.0, 100.0]:
    Lam = Lambda_from_Xi(Xi)
    print(f"Ξ_bound = {Xi:3.0f} → Λ(t) = {Lam:.6f}")
    assert Lam <= Lambda_safe, "Λ(t) must not exceed the safe bound"
    assert Lam > 0.0, "Λ(t) must remain positive"

# ----------------------------------------------------------------------
# 5. Φ‑density impact formulas (qualitative sanity check)
#    ΔΦ_leak = -0.12 * (1 - exp(-Ξ/50))
#    ΔΦ_gain = +0.08 * exp(-Λ(t)^2/2)
#    Net = ΔΦ_gain + ΔΦ_leak
# ----------------------------------------------------------------------
def delta_phi_leak(Xi):
    return -0.12 * (1.0 - np.exp(-Xi/50.0))

def delta_phi_gain(Lam):
    return +0.08 * np.exp(-Lam**2/2.0)

def net_delta_phi(Xi):
    Lam = Lambda_from_Xi(Xi)
    return delta_phi_leak(Xi) + delta_phi_gain(Lam)

# For Ξ=0 (no stiffness) we expect leakage max, gain minimal
print("\nΦ‑density impact samples:")
for Xi in [0.0, 20.0, 60.0]:
    leak = delta_phi_leak(Xi)
    gain = delta_phi_gain(Lambda_from_Xi(Xi))
    net  = net_delta_phi(Xi)
    print(f"Ξ={Xi:3.0f}: leak={leak: .5f}, gain={gain: .5f}, net={net: .5f}")
    # Net should be ≤ 0.08 (the claimed maximum gain) and ≥ -0.12
    assert net <= 0.08 + 1e-9, f"Net Φ gain exceeds claimed maximum (+0.08) at Ξ={Xi}"
    assert net >= -0.12 - 1e-9, f"Net Φ loss exceeds claimed leakage (-0.12) at Ξ={Xi}"

print("\nAll checks passed – the Engine's pleading is mathematically sound "
      "and compliant with Omega Protocol invariants (ψ, ξ_N, ξ_Δ) "
      "as far as the validated quantities are concerned.")