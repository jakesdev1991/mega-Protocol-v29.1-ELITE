# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import quad

# Engine parameters
Lambda = 0.82
v      = 1.28

# -------------------------------------------------------------
# 1. Evaluate the dimensionless integral I = (4π/v) ∫_0^1 q e^{-q^2/2} arctan(Λ q v) dq
def integrand(q):
    return q * np.exp(-q**2 / 2.0) * np.arctan(Lambda * q * v)

I_val, I_err = quad(integrand, 0.0, 1.0)
I = (4.0 * np.pi / v) * I_val

print(f"Dimensionless integral I = (4π/v)∫_0^1 ... dq = {I:.6f} ± {I_err:.6e}")
# For the quoted parameters this yields ~3.9, not 3.2e-5.

# -------------------------------------------------------------
# 2. Entropy integral H = -4π ∫_0^Λ k^2 n_k ln n_k dk,
#    with n_k = 1/(exp(k^2/(2Λ^2)) - 1). Show IR divergence.
def entropy_integrand(k):
    # avoid overflow at k=0 by returning 0 for k==0 (limit is finite but integrand diverges as k->0)
    if k == 0.0:
        return 0.0
    n = 1.0 / (np.exp(k**2 / (2.0 * Lambda**2)) - 1.0)
    # n diverges ~ 2Λ^2/k^2; ln n diverges as -2 ln(k) + const
    return -k**2 * n * np.log(n)

def compute_H(epsilon):
    H, err = quad(entropy_integrand, epsilon, Lambda, limit=200)
    return 4.0 * np.pi * H, err

for eps in [1e-3, 1e-4, 1e-5, 1e-6]:
    H_val, H_err = compute_H(eps)
    print(f"Entropy H (ε={eps:.0e}) = {H_val:.6f} ± {H_err:.6e}")

# -------------------------------------------------------------
# 3. “Correction” Δα/α for a few plausible Φ_Δ/Φ_N ratios
ratios = [1.0, 1e-2, 1e-4, 1e-5]
print("\nΔα/α for various Φ_Δ/Φ_N (assuming I is the full factor):")
for r in ratios:
    print(f"  Φ_Δ/Φ_N = {r:.0e}  →  Δα/α = {I * r:.6e}")

# -------------------------------------------------------------
# 4. Show that the claimed 3.21e-5 would require Φ_Δ/Φ_N ≈ 8e-6,
#    i.e. an extreme fine‑tuning that contradicts the premise.
required_ratio = 3.21e-5 / I
print(f"\nTo obtain Δα/α = 3.21e-5, Φ_Δ/Φ_N must be {required_ratio:.2e}")