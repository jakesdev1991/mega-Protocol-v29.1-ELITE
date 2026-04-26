# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script – Higher‑Order Lattice Polarization
Checks:
  1. Integral evaluation (including Jacobian Λ^3)
  2. Dimensionless nature of the correction
  3. Shannon conditional entropy of IR modes (>= 0.85)
  4. Presence of Omega invariants (psi, xi_N, xi_Delta) in a user‑provided expression
"""

import numpy as np
import mpmath as mp
import sympy as sp

# ----------------------------------------------------------------------
# 1. Integral evaluation with correct Jacobian
# ----------------------------------------------------------------------
def dimensionless_integral(Lambda=0.82, v=1.28, N=20000):
    """
    Compute I = ∫_{0}^{Lambda} e^{-k^2/(2 Lambda^2)} / (1 + (k·v)^2) d^3k
    using spherical coordinates: d^3k = 4π k^2 dk
    Returns I / Lambda^3 (so that the prefactor 1/Lambda^2 yields a dimensionless factor).
    """
    f = lambda k: np.exp(-k**2/(2*Lambda**2)) / (1.0 + (k*v)**2) * 4*np.pi * k**2
    ks = np.linspace(0, Lambda, N)
    vals = f(ks)
    I = np.trapz(vals, ks)          # numerical integration
    # Dimensionless part after extracting Lambda^3:
    I_dimless = I / (Lambda**3)
    return I, I_dimless

I_raw, I_dimless = dimensionless_integral()
print(f"Raw integral I = {I_raw:.6e}")
print(f"Dimensionless I/Λ^3 = {I_dimless:.6e}")

# The Engine claims: (ΦΔ/ΦN) * (1/Λ^2) * I = (ΦΔ/ΦN) * 0.0000054
# => I_dimless should equal 0.0000054 * Lambda^2
expected_I_dimless = 0.0000054 * (Lambda**2)
print(f"Expected I/Λ^3 from claim = {expected_I_dimless:.6e}")
print(f"Difference = {abs(I_dimless - expected_I_dimless):.6e}")

tol = 1e-6
integral_ok = abs(I_dimless - expected_I_dimless) < tol
print(f"Integral test: {'PASS' if integral_ok else 'FAIL'} (tol={tol})")

# ----------------------------------------------------------------------
# 2. Shannon conditional entropy of IR modes (k < Lambda)
# ----------------------------------------------------------------------
def shannon_entropy(Lambda=0.82, Nk=5000, V=1.0):
    """
    Occupation numbers: n_k = 1/(exp(k^2/(2 Lambda^2)) - 1)   (mu=0)
    Probability p_k ∝ n_k * g_k where g_k = V * k^2 / (2π^2)  (density of states in 3D)
    Normalize p_k over k in [0, Lambda].
    Shannon entropy: H = - Σ p_k ln p_k
    """
    ks = np.linspace(0, Lambda, Nk)
    nk = 1.0 / (np.exp(ks**2/(2*Lambda**2)) - 1.0 + 1e-15)  # avoid div/0 at k=0
    gk = V * ks**2 / (2.0 * np.pi**2)          # density of states (continuum approx)
    pk = nk * gk
    pk /= np.trapz(pk, ks)                     # normalize
    # Avoid log(0)
    pk_safe = np.where(pk > 0, pk, 1e-15)
    H = -np.trapz(pk_safe * np.log(pk_safe), ks)
    return H

H = shannon_entropy()
print(f"\nShannon entropy H = {H:.5f}")
entropy_ok = H >= 0.85
print(f"Entropy test (H ≥ 0.85): {'PASS' if entropy_ok else 'FAIL'}")

# ----------------------------------------------------------------------
# 3. Invariant presence check (user must supply a SymPy expression)
# ----------------------------------------------------------------------
print("\n--- Invariant Presence Check ---")
print("Provide a SymPy expression that should contain psi, xi_N, xi_Delta.")
print("Example: expr = psi * xi_N * xi_Delta + Lambda**2")
print("Enter expression as a string (or leave blank to skip):")
try:
    user_input = input().strip()
except EOFError:
    user_input = ""

if user_input:
    # Define symbols
    psi, xi_N, xi_Delta, Lambda = sp.symbols('psi xi_N xi_Delta Lambda')
    try:
        expr = sp.sympify(user_input, locals={'psi':psi, 'xi_N':xi_N,
                                              'xi_Delta':xi_Delta, 'Lambda':Lambda})
        missing = []
        for sym in (psi, xi_N, xi_Delta):
            if sym not in expr.free_symbols:
                missing.append(str(sym))
        if missing:
            print(f"FAIL: Missing invariants {', '.join(missing)} in expression.")
        else:
            print("PASS: All required invariants present.")
    except Exception as e:
        print(f"FAIL: Could not parse expression ({e}).")
else:
    print("Skipped invariant check (no expression supplied).")

# ----------------------------------------------------------------------
# Final summary
# ----------------------------------------------------------------------
print("\n=== SUMMARY ===")
print(f"Integral test          : {'PASS' if integral_ok else 'FAIL'}")
print(f"Entropy test           : {'PASS' if entropy_ok else 'FAIL'}")
print("Invariant test         : (see above)")
print("\nIf any test FAILS, the derivation does NOT meet Omega Protocol v26.0.")