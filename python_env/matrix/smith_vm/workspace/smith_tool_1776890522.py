# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy import integrate

# ----- Parameters from the Engine -----
Lambda = 0.82          # cutoff (dimensionless, lattice spacing a=1)
v_mag  = 1.28          # magnitude of alignment vector v

# ----- 1. Integral for Δα/α (Eq. 1) -----
def integrand(q):
    # q in [0,1]
    return q * np.exp(-q**2/2) * np.arctan(Lambda * v_mag * q)

radial, radial_err = integrate.quad(integrand, 0, 1, limit=200)
factor = (4*np.pi / v_mag) * radial   # prefactor from Eq. (1)

print(f"Radial integral ∫0^1 q e^{-q^2/2} arctan(Λ v q) dq = {radial:.6e} ± {radial_err:.1e}")
print(f"Prefactor (4π/v) * integral = {factor:.6e}")
print(f"Claimed factor (Δα/α per ΦΔ/ΦN) = 5.30e-06")
print(f"Difference = {factor - 5.30e-06:.2e}")

# ----- 2. Entropy check -----
def n_k(k):
    return 1.0/(np.exp(k**2/(2*Lambda**2)) - 1.0)

def s_boson(n):
    return (n+1)*np.log(n+1) - n*np.log(n)

def entropy_integrand(k):
    n = n_k(k)
    return s_boson(n) * 4*np.pi * k**2   # integrand for numerator

num, num_err = integrate.quad(entropy_integrand, 0, Lambda, limit=200)
den, den_err = integrate.quad(lambda k: 4*np.pi*k**2, 0, Lambda, limit=200)
avg_entropy = num / den

print("\nEntropy validation:")
print(f"Numerator ∫ s(k) 4πk^2 dk = {num:.6f} ± {num_err:.1e}")
print(f"Denominator ∫ 4πk^2 dk   = {den:.6f} ± {den_err:.1e}")
print(f"Mode‑averaged entropy ⟨s⟩ = {avg_entropy:.5f}")
print(f"Required ⟨s⟩ ≥ 0.85 ? {'PASS' if avg_entropy >= 0.85 else 'FAIL'}")

# ----- 3. Check that Λ, v can be linked to invariants -----
# ψ = ln(Φ_N) appears only as an overall metric coupling; we verify
# that the horizon condition Λ = 1/R can be satisfied for some R>0.
R = 1.0/Lambda
print(f"\nDerived horizon radius R = 1/Λ = {R:.3f}")
print("If ξ_N(R) = ξ_Δ(R) can be solved for this R, the invariant")
print("coupling ψ = ln(Φ_N) is implicitly satisfied.")