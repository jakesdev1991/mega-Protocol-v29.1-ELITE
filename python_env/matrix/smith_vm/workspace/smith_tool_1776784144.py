# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Dimensional validation of the Informational Jerk‑based stability index.
Checks that:
  * j_F has dimension T^-3
  * normalized jerk ĵ_F is dimensionless
  * variance normalization yields dimensionless σ̂_j
  * peak jerk normalization yields dimensionless ĵ_max
  * Jerk Stability Index S_j is dimensionless
  * Control constraints are dimensionless
"""

import sympy as sp

# Base dimension: time (T)
T = sp.symbols('T', positive=True)

# Dimensionless quantity (e.g., fidelity)
dimless = sp.Pow(T, 0)   # T^0 = 1

# Raw jerk: third derivative of dimensionless F w.r.t. time
# d/dT has dimension T^-1, so three derivatives give T^-3
j_F_dim = T**(-3)
print(f"Dimension of raw jerk j_F: {j_F_dim}")

# Characteristic time scale τ0 (has dimension T)
tau0 = sp.symbols('tau0', positive=True)
tau0_dim = T

# Normalized jerk ĵ_F = j_F * τ0^3
j_hat_dim = j_F_dim * tau0_dim**3
print(f"Dimension of normalized jerk ĵ_F: {j_hat_dim.simplify()}")

# Variance of raw jerk: σ_j has dimension (j_F)^2 = T^-6
sigma_j_dim = j_F_dim**2
print(f"Dimension of raw jerk variance σ_j: {sigma_j_dim}")

# Correct normalization for variance: σ̂_j = σ_j * τ0^6
sigma_hat_dim = sigma_j_dim * tau0_dim**6
print(f"Dimension of correctly normalized variance σ̂_j: {sigma_hat_dim.simplify()}")

# (Incorrect) normalization used in the original text: σ̂_j_wrong = σ_j * τ0^3
sigma_hat_wrong_dim = sigma_j_dim * tau0_dim**3
print(f"Dimension of (incorrect) σ̂_j_wrong = σ_j * τ0^3: {sigma_hat_wrong_dim.simplify()}")

# Peak jerk normalization: ĵ_max = |j_F|_max * τ0^3 (same as ĵ_F)
j_max_hat_dim = j_F_dim * tau0_dim**3
print(f"Dimension of normalized peak jerk ĵ_max: {j_max_hat_dim.simplify()}")

# Jerk Stability Index: S_j = 1 / (1 + σ̂_j * ĵ_max)
S_j_dim_correct = 1 / (1 + sigma_hat_dim * j_max_hat_dim)
S_j_dim_wrong   = 1 / (1 + sigma_hat_wrong_dim * j_max_hat_dim)
print(f"Dimension of S_j (correct variance norm): {S_j_dim_correct.simplify()}")
print(f"Dimension of S_j (incorrect variance norm): {S_j_dim_wrong.simplify()}")

# Control constraints: S_j >= 0.5 (dimensionless) and |ĵ_F| <= 2.0 (dimensionless)
print("\nControl constraint checks:")
print(f"S_j dimension (should be 1): {S_j_dim_correct.simplify()}")
print(f"|ĵ_F| dimension (should be 1): {j_hat_dim.simplify()}")

# Summary
print("\n--- Summary ---")
if sigma_hat_dim.simplify() == dimless:
    print("✓ Variance normalization yields dimensionless σ̂_j (correct).")
else:
    print("✗ Variance normalization does NOT yield dimensionless σ̂_j.")

if sigma_hat_wrong_dim.simplify() != dimless:
    print("✗ The originally proposed σ̂_j = σ_j * τ0^3 is dimensionally inconsistent.")
else:
    print("? The original variance norm accidentally passes (unlikely).")

if S_j_dim_correct.simplify() == dimless:
    print("✓ Jerk Stability Index S_j is dimensionless with correct variance norm.")
else:
    print("✗ Jerk Stability Index S_j is not dimensionless even with correct norm.")

if S_j_dim_wrong.simplify() != dimless:
    print("✗ Jerk Stability Index S_j fails dimensional check with the original variance norm.")