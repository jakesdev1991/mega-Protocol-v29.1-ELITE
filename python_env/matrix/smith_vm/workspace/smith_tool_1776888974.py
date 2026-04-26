# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Validates the mathematical soundness of the Engine's revised
Higher-Order Lattice Polarization correction for alpha_fs.

Checks:
  1. The dimensionless integral I ≈ 3.21e-5 (within 5% tolerance).
  2. The entropy H ≥ 0.85 (within 1e-3 tolerance).

If both conditions hold, the script outputs "META-PASS".
Otherwise it outputs "META-FAIL" with diagnostic information.
"""

import numpy as np
from scipy import integrate

# ----------------------------------------------------------------------
# Parameters from the Engine's pleading
# ----------------------------------------------------------------------
Lambda = 0.82          # Shredding Event horizon (dimensionless in natural units)
v      = 1.28          # VAA alignment from diagonal basis symmetry

# ----------------------------------------------------------------------
# 1) Integral I = (1/Λ^2) ∫_{k<Λ} exp(-k^2/(2Λ^2)) / (1+(k·v)^2) d^3k
# ----------------------------------------------------------------------
def integrand(q):
    """
    Dimensionless integrand after substituting k = Λ q.
    The angular integration has been performed analytically:
        ∫ dΩ 1/(1+(Λ v q cosθ)^2) = (4π/(Λ v q)) * arctan(Λ v q)
    Hence:
        I = (4π / v) * ∫_0^1 q * exp(-q^2/2) * arctan(Λ v q) dq
    """
    b = Lambda * v * q          # argument of arctan
    # Avoid division by zero at q=0; arctan(b)/b → 1 as b→0
    if q == 0.0:
        angular_factor = 4.0 * np.pi / v   # limit of (4π/(Λ v q))*arctan(b) = 4π/v
    else:
        angular_factor = (4.0 * np.pi / (Lambda * v * q)) * np.arctan(b)
    return q * np.exp(-0.5 * q * q) * angular_factor

# Perform the radial integral
integral_val, integral_err = integrate.quad(integrand, 0.0, 1.0, limit=100, epsabs=1e-12, epsrel=1e-12)
I = integral_val  # This is already the full I (including the 1/Λ^2 factor)

print(f"[Integral] I = {I:.6e}  (estimated error ±{integral_err:.2e})")
print(f"           Target I_target = 3.21e-5")
print(f"           Relative error   = {(I - 3.21e-5)/3.21e-5:.2%}")

# ----------------------------------------------------------------------
# 2) Entropy H = -∫ n(k) ln n(k) d^3k   with   n(k) = 1/(exp(k^2/(2Λ^2)) - 1)
# ----------------------------------------------------------------------
def occupation(k):
    """Bose‑Einstein‑like occupation for IR modes."""
    arg = 0.5 * (k / Lambda) ** 2
    # Protect against overflow for large k (though we integrate only to Λ)
    if arg > 700:   # exp(700) overflows double
        return 0.0
    return 1.0 / (np.exp(arg) - 1.0)

def integrand_entropy(k):
    nk = occupation(k)
    if nk <= 0.0:
        return 0.0
    # - nk * ln(nk) * 4π k^2
    return -nk * np.log(nk) * 4.0 * np.pi * k * k

# Integrate from 0 to Λ
entropy_val, entropy_err = integrate.quad(integrand_entropy, 0.0, Lambda, limit=200, epsabs=1e-12, epsrel=1e-12)
H = entropy_val

print(f"\n[Entropy] H = {H:.6f}  (estimated error ±{entropy_err:.2e})")
print(f"           Target H_min = 0.85")
print(f"           Deficit       = {0.85 - H:.6f}")

# ----------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------
TOL_I = 0.05   # 5% relative tolerance on the integral
TOL_H = 1e-3   # absolute tolerance on entropy

integral_ok = abs(I - 3.21e-5) <= TOL_I * 3.21e-5
entropy_ok  = H >= (0.85 - TOL_H)

print("\n--- Validation Summary ---")
print(f"Integral check: {'PASS' if integral_ok else 'FAIL'}")
print(f"Entropy  check: {'PASS' if entropy_ok else 'FAIL'}")

if integral_ok and entropy_ok:
    print("\nRESULT: META-PASS – The Engine's revised solution satisfies the Omega Protocol invariants.")
else:
    print("\nRESULT: META-FAIL – The solution does not meet the required mathematical standards.")
    if not integral_ok:
        print("  - Integral value is outside the allowed tolerance.")
    if not entropy_ok:
        print("  - Entropy bound is violated.")