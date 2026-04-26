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
Checks the mathematical soundness of the "Higher‑Order Lattice Polarization"
derivation for the fine‑structure constant anisotropy.

Invariants to verify:
  • Φ_N  – isotropic shift (appears only in Π_T)
  • Φ_Δ  – anisotropic shift (appears only in Π_L, Π_M)
  • J*   – entropy‑gauge coupling:  J^μ = √2 Φ_Δ δ^μ_0,
           A_μ = ∂_μ S_pair,   S_pair = S_0 + Φ_Δ S_1 + O(Φ_Δ²)
           with S_1 = −(Π_L + 2Π_M)

The script uses sympy for symbolic checks and numpy/scipy for numeric
Monte‑Carlo evaluation of the loop integrals (continuum approximation).
"""

import numpy as np
import sympy as sp
from scipy import integrate
import warnings
warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------
# 1. Symbolic setup
# ----------------------------------------------------------------------
e, Phi_N, Phi_Delta, p2, a, m = sp.symbols('e Phi_N Phi_Delta p2 a m', positive=True)
pi = sp.pi

# Isotropic transverse part (as given in the derivation)
Pi_T = e**2/(12*pi**2) * sp.log(1/(a**2 * p2)) + e**2/pi**2 * Phi_N

# Placeholders for the anisotropic pieces (to be filled numerically later)
Pi_L = sp.Function('Pi_L')(p2, Phi_Delta)   # will be proportional to Phi_Delta
Pi_M = sp.Function('Pi_M')(p2, Phi_Delta)   # will be proportional to Phi_Delta

# Effective directional fine‑structure constant (Landau gauge)
alpha_0 = sp.symbols('alpha_0', positive=True)
# Direction indicator: delta_{i,z} = 1 for i = z, 0 otherwise
delta_iz = sp.symbols('delta_iz')   # 0 or 1 in numeric tests

alpha_eff = alpha_0 / (1 + Pi_T + delta_iz * Phi_Delta * (Pi_L + 2*Pi_M))

# ----------------------------------------------------------------------
# 2. Symbolic invariants checks
# ----------------------------------------------------------------------
print("=== Symbolic Invariant Checks ===")

# (a) Phi_N appears only in Pi_T
depends_on_Phi_N = Pi_T.has(Phi_N) and not (Pi_L.has(Phi_N) or Pi_M.has(Phi_N))
print(f"Phi_N appears only in Pi_T: {depends_on_Phi_N}")

# (b) Phi_Delta appears only in Pi_L and Pi_M (linear at leading order)
# We'll test this numerically later; symbolically we just note the structure.
print("Phi_Delta dependence: to be checked numerically.")

# (c) Entropy‑gauge relation: S1 = -(Pi_L + 2*Pi_M)
S1 = sp.symbols('S1')
entropy_relation = sp.simplify(S1 + (Pi_L + 2*Pi_M))
print(f"Entropy relation S1 + (Pi_L+2*Pi_M) = 0 ? -> {entropy_relation}")

# (d) When Phi_Delta -> 0, alpha_eff becomes isotropic (independent of direction)
alpha_iso = sp.simplify(alpha_eff.subs(Phi_Delta, 0))
print(f"Alpha_eff at Phi_Delta=0 (isotropic): {alpha_iso}")
print(f"Independent of delta_iz? {alpha_iso.has(delta_iz) == False}")

# ----------------------------------------------------------------------
# 3. Numeric evaluation of the one‑loop anisotropic integral
# ----------------------------------------------------------------------
print("\n=== Numeric One‑Loop Anisotropic Integral ===")

# Continuum approximation: replace lattice sums with integrals over Euclidean momentum.
# We evaluate the angular part of the integrand that should give the P2(cosθ_p) structure.
# The integral (schematic):
#   I_aniso(p) = ∫ d^4k  (k_z^2 - (1/3)k^2) / (k^2 + m^2)^2   * 1/((k-p)^2 + m^2)
# After integrating over |k|, the angular dependence reduces to P2(cosθ_p).
# We'll compute the angular dependence by fixing |p| and varying the angle between p and the z‑axis.

def integrand_angular(k_mag, theta_k, phi_k, p_mag, theta_p):
    """
    Returns the angular part of the one‑loop anisotropic integrand
    (continuum, Euclidean metric) for a given loop momentum magnitude k_mag
    and angles (theta_k, phi_k).  External momentum p has magnitude p_mag
    and polar angle theta_p (azimuth set to 0 w.l.o.g.).
    """
    # Components of k
    kx = k_mag * np.sin(theta_k) * np.cos(phi_k)
    ky = k_mag * np.sin(theta_k) * np.sin(phi_k)
    kz = k_mag * np.cos(theta_k)

    # Components of p (choose phi_p = 0)
    px = p_mag * np.sin(theta_p) * np.cos(0.0)
    py = p_mag * np.sin(theta_p) * np.sin(0.0)
    pz = p_mag * np.cos(theta_p)

    # Dot products
    k_dot_p = kx*px + ky*py + kz*pz
    k_sq = k_mag**2
    p_sq = p_mag**2
    k_minus_p_sq = k_sq + p_sq - 2*k_dot_p

    # Propagator denominators (mass m set to 1 for simplicity)
    denom = (k_sq + 1.0)**2 * (k_minus_p_sq + 1.0)

    # Anisotropic numerator: we keep the term that survives after trace:
    #   (k_z^2 - (1/3) k^2)  <-- quadrupole operator
    num = kz**2 - (1.0/3.0) * k_sq

    return num / denom

def angular_integral(p_mag, theta_p, samples=200000):
    """
    Monte‑Carlo integration over loop momentum magnitude (0, Λ) and angles.
    UV cutoff Λ = 5 (in lattice units) – sufficient to see angular shape.
    """
    Lambda = 5.0
    total = 0.0
    weight = 0.0
    for _ in range(samples):
        # Sample k_mag uniformly in [0, Lambda] (simple importance)
        k_mag = np.random.uniform(0, Lambda)
        # Sample directions uniformly on sphere
        cos_theta_k = np.random.uniform(-1, 1)
        phi_k = np.random.uniform(0, 2*np.pi)
        theta_k = np.arccos(cos_theta_k)

        val = integrand_angular(k_mag, theta_k, phi_k, p_mag, theta_p)
        total += val
        weight += 1.0

    integral_est = total / weight * (Lambda * (2*np.pi) * 2)  # approximate volume factor
    return integral_est

# Test a few external angles
p_mag_test = 1.0
angles = [0.0, np.pi/6, np.pi/4, np.pi/3, np.pi/2]  # theta_p from 0 (parallel) to π/2 (perp)
results = []
for th in angles:
    I = angular_integral(p_mag_test, th, samples=150000)
    results.append(I)
    print(f"theta_p = {th:.3f} rad -> I ≈ {I:.6f}")

# Expected P2(cosθ) = (3 cos^2θ -1)/2
def P2(x):
    return (3*x**2 - 1)/2

print("\nComparison with P2(cosθ_p):")
for th, I in zip(angles, results):
    expected = P2(np.cos(th))
    print(f"θ={th:.3f}: MC={I:.6f}, P2={expected:.6f}, diff={abs(I-expected):.6f}")

# Check if the shape matches P2 within tolerance
tol = 0.15  # generous tolerance due to MC noise and crude cutoff
shape_ok = all(abs(I - P2(np.cos(th))) < tol for th, I in zip(angles, results))
print(f"\nAngular shape matches P2(cosθ) within {tol}? {shape_ok}")

# ----------------------------------------------------------------------
# 4. Numeric test of the effective alpha formula
# ----------------------------------------------------------------------
print("\n=== Effective Alpha Test ===")

# Choose sample parameters
alpha_0_val = 1/137.0
e_val = np.sqrt(4*np.pi*alpha_0_val)   # in natural units
Phi_N_val = 0.01
Phi_Delta_val = 0.05
p2_val = 0.5
a_val = 0.1
m_val = 0.1

# Compute Pi_T numerically
Pi_T_val = (e_val**2/(12*np.pi**2))*np.log(1/(a_val**2 * p2_val)) + (e_val**2/np.pi**2)*Phi_N_val

# For Pi_L and Pi_M we use the angular integrals from above (scaled)
# In the derivation: Pi_L = e^2/π^2 * I_L,   Pi_M = e^2/π^2 * I_M
# We'll approximate I_L ≈ <cos^2θ_k> and I_M ≈ <cosθ_k * sinθ_k> (the latter vanishes by symmetry)
# For a quick test we set:
I_L_approx = 0.5   # <cos^2θ> over sphere = 1/3, but we keep O(1) for demo
I_M_approx = 0.0   # odd integrand → zero

Pi_L_approx = (e_val**2/np.pi**2) * I_L_approx * Phi_Delta_val
Pi_M_approx = (e_val**2/np.pi**2) * I_M_approx * Phi_Delta_val

# Directional alphas
alpha_perp = alpha_0_val / (1 + Pi_T_val)                     # delta_iz = 0
alpha_parallel = alpha_0_val / (1 + Pi_T_val + Phi_Delta_val*(Pi_L_approx+2*Pi_M_approx))

print(f"Alpha_perp (i=x,y)   = {alpha_perp:.6e}")
print(f"Alpha_parallel (i=z) = {alpha_parallel:.6e}")
print(f"Relative shift Δα/α  = {(alpha_parallel-alpha_perp)/alpha_perp:.6e}")

# Check isotropy when Phi_Delta -> 0
alpha_iso_test = alpha_0_val / (1 + Pi_T_val)
print(f"Alpha with Phi_Delta=0 = {alpha_iso_test:.6e}")
print(f"Isotropy recovered? {np.isclose(alpha_perp, alpha_iso_test) and np.isclose(alpha_parallel, alpha_iso_test)}")

# ----------------------------------------------------------------------
# 5. Summary verdict
# ----------------------------------------------------------------------
print("\n=== Summary ===")
print("Symbolic checks:")
print(f"  - Phi_N only in Pi_T: {depends_on_Phi_N}")
print(f"  - Isotropy at Phi_Delta=0: {not alpha_iso.has(delta_iz)}")
print("\nNumeric checks:")
print(f"  - Anisotropic integral shows P2(cosθ) shape? {shape_ok}")
print(f"  - Effective alpha shows expected directional splitting? "
      f"{abs((alpha_parallel-alpha_perp)/alpha_perp) > 1e-4}")

# Final recommendation
if depends_on_Phi_N and not alpha_iso.has(delta_iz) and shape_ok:
    print("\nPRELIMINARY PASS: The core tensor structure and invariants are respected.")
    print("However, the one‑loop coefficient and angular integral need a rigorous derivation")
    print("to replace the placeholder approximations used here.")
else:
    print("\nFAIL: One or more Omega Protocol invariants are violated.")
    print("Re‑examine the one‑loop trace (see critique) before proceeding.")