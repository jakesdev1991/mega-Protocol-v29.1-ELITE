# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy import integrate

# -------------------------------------------------
# Parameters from the revised analysis
Lambda = 0.82          # original cutoff
v      = 1.28          # coupling
Lambda_safe = 0.75     # proposed tightened bound

# -------------------------------------------------
# 1. Integral I(Lambda, v) = ∫_{k<Λ} e^{-k^2/(2Λ^2)} / (1+(k·v)^2) d^3k
def integrand(k):
    # k is magnitude; angular part gives 4πk^2
    return 4.0 * np.pi * k**2 * np.exp(-k**2/(2*Lambda**2)) / (1.0 + (k*v)**2)

I_val, I_err = integrate.quad(integrand, 0, Lambda, limit=200, epsabs=1e-12, epsrel=1e-12)
print(f"I(Lambda={Lambda}, v={v}) = {I_val:.6f} ± {I_err:.2e}")

# -------------------------------------------------
# 2. Dimensionless form: k = Λ q  →  I = Λ^3 * ∫_0^1 4π q^2 e^{-q^2/2} / (1+(Λ v q)^2) dq
def integrand_dimless(q):
    return 4.0 * np.pi * q**2 * np.exp(-q**2/2.0) / (1.0 + (Lambda*v*q)**2)

I_dim, I_dim_err = integrate.quad(integrand_dimless, 0, 1, limit=200, epsabs=1e-12, epsrel=1e-12)
I_from_dim = Lambda**3 * I_dim
print(f"I via dimless = {I_from_dim:.6f} (error {I_dim_err:.2e})")

# -------------------------------------------------
# 3. IR/UV overlap metric O(Lambda) = ∫_{Λ/2}^{Λ} same integrand d^3k / I(Lambda,v)
def overlap_integrand(k):
    return 4.0 * np.pi * k**2 * np.exp(-k**2/(2*Lambda**2)) / (1.0 + (k*v)**2)

overlap_num, _ = integrate.quad(overlap_integrand, Lambda/2.0, Lambda, limit=200, epsabs=1e-12, epsrel=1e-12)
overlap_frac = overlap_num / I_val
print(f"IR/UV overlap fraction = {overlap_frac:.4f}")

# -------------------------------------------------
# 4. Repeat for Lambda_safe = 0.75 to see if overlap drops below a tolerance (e.g., 0.05)
def overlap_for_Lambda(L):
    def integrand_L(k):
        return 4.0*np.pi*k**2*np.exp(-k**2/(2*L**2))/(1.0+(k*v)**2)
    I_L, _ = integrate.quad(integrand_L, 0, L, limit=200, epsabs=1e-12, epsrel=1e-12)
    ov_num, _ = integrate.quad(integrand_L, L/2.0, L, limit=200, epsabs=1e-12, epsrel=1e-12)
    return ov_num/I_L

overlap_safe = overlap_for_Lambda(Lambda_safe)
print(f"Overlap for Lambda_safe={Lambda_safe}: {overlap_safe:.4f}")

# -------------------------------------------------
# 5. Stability operator: Lambda(t) = 0.75 * exp(-Xi_bound/100)
def Lambda_of_Xi(Xi):
    return 0.75 * np.exp(-Xi/100.0)

# Example Xi values (stiffness invariants)
for Xi in [0, 20, 50, 100]:
    print(f"Xi={Xi:3d} → Lambda={Lambda_of_Xi(Xi):.4f}")

# -------------------------------------------------
# 6. Φ‑density impact formulas (as given)
def delta_phi_leak(Xi):
    return -0.12 * (1.0 - np.exp(-Xi/50.0))

def delta_phi_gain(Lambda_t):
    return +0.08 * np.exp(-Lambda_t**2/2.0)

Xi_test = 30.0
Lam_t   = Lambda_of_Xi(Xi_test)
print(f"\nExample Xi={Xi_test}:")
print(f"  Lambda(t) = {Lam_t:.4f}")
print(f"  ΔΦ_leak   = {delta_phi_leak(Xi_test):.4f}")
print(f"  ΔΦ_gain   = {delta_phi_gain(Lam_t):.4f}")
print(f"  Net ΔΦ    = {delta_phi_leak(Xi_test)+delta_phi_gain(Lam_t):.4f}")