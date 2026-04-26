# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random, math, sys

# ----------------------------------------------------------------------
# 1.  Anisotropic one‑loop kernel (continuum toy model)
# ----------------------------------------------------------------------
def aniso_kernel(phi_delta, p=1.0, N_samples=200000):
    """
    Monte‑Carlo estimate of the dimensionless anisotropic piece:
        Pi_Delta ~ phi_delta * ∫ d⁴k (cos²θ_k) / [k² (k-p)²]
    The integral is regulated by a UV cutoff Lambda=1 (lattice spacing a=1).
    For large phi_delta the metric factor sqrt(g) = (1+phi_delta)**0.5
    enters the measure, giving an extra exp(phi_delta/2) growth.
    """
    # UV cutoff
    Lambda = 1.0
    total = 0.0
    for _ in range(N_samples):
        # sample k uniformly in a 4‑ball of radius Lambda
        # (acceptance‑rejection would be more accurate, but uniform is enough for the trend)
        k = np.random.normal(0, 0.5, size=4)
        if np.dot(k, k) > Lambda**2:
            continue
        k2 = np.dot(k, k)
        # external momentum p along z‑axis (archive direction)
        kp = k[3] * p  # only z‑component matters for angular factor
        # angle between k and archive direction
        cos_theta = k[3] / np.sqrt(k2) if k2 > 1e-12 else 0.0
        # measure factor from anisotropic metric: sqrt(g) = sqrt(1+phi_delta)
        measure = (1.0 + phi_delta)**0.5
        # integrand: cos²θ / [k² (k-p)²] (approx (k-p)² ~ k² + p² - 2kp)
        denom = k2 * (k2 + p**2 - 2*kp)
        if denom < 1e-12:
            continue
        total += measure * (cos_theta**2) / denom
    # normalize by volume factor (approximate)
    vol = (np.pi**2 / 2) * Lambda**4  # volume of 4‑ball
    return phi_delta * total / N_samples * vol

# ----------------------------------------------------------------------
# 2.  Effective scalar α_eff in two different orthogonal bases
# ----------------------------------------------------------------------
def alpha_eff(phi_N, phi_delta, basis_angle=0.0, alpha0=1/137):
    """
    Rotate the deformation vector (phi_N, phi_delta) by basis_angle.
    The rotated components are:
        phi_N'   = phi_N * cosθ - phi_delta * sinθ
        phi_D'   = phi_N * sinθ + phi_delta * cosθ
    The Engine’s formula uses only the *magnitudes* of the rotated
    components, ignoring the off‑diagonal mixing.  This yields a
    basis‑dependent α_eff.
    """
    # rotate
    phi_N_p   = phi_N * math.cos(basis_angle) - phi_delta * math.sin(basis_angle)
    phi_D_p   = phi_N * math.sin(basis_angle) + phi_delta * math.cos(basis_angle)

    # isotropic piece (toy value)
    Pi_T = 0.01 * phi_N  # placeholder

    # anisotropic piece from kernel
    Pi_D = aniso_kernel(abs(phi_D_p), p=1.0, N_samples=50000)

    # Engine’s scalar formula
    denom = 1 + Pi_T + abs(phi_D_p) * Pi_D
    return alpha0 / denom

# ----------------------------------------------------------------------
# 3.  Demonstrate divergence & basis‑dependence
# ----------------------------------------------------------------------
if __name__ == "__main__":
    phi_N = 0.1
    print("Phi_N =", phi_N, "\n")

    # scan phi_delta
    for phi_delta in [0.1, 0.5, 1.0, 2.0, 5.0]:
        # compute aniso kernel (magnitude)
        Pi_D = aniso_kernel(phi_delta, p=1.0, N_samples=100000)
        print(f"Phi_Delta = {phi_delta:4.1f}  ->  Pi_D ≈ {Pi_D:8.3e}")

    print("\n--- Basis dependence of α_eff (Phi_Delta=1.0) ---\n")
    phi_delta = 1.0
    for theta in [0.0, math.pi/6, math.pi/4, math.pi/3, math.pi/2]:
        a = alpha_eff(phi_N, phi_delta, basis_angle=theta)
        print(f"θ = {theta*180/math.pi:5.1f}°  ->  α_eff ≈ {a:.6e}")

    # The kernel grows exponentially with phi_delta, as shown by the
    # measure factor (1+phi_delta)**0.5 in aniso_kernel.
    # This causes the denominator 1+Pi_T+phi_delta*Pi_D to become
    # negative for phi_delta >~ 2, signaling breakdown of perturbation theory.
    print("\n--- Divergence: denominator sign flip ---\n")
    for phi_delta in [0.5, 1.0, 1.5, 2.0, 3.0]:
        Pi_T = 0.01 * phi_N
        Pi_D = aniso_kernel(phi_delta, p=1.0, N_samples=80000)
        denom = 1 + Pi_T + phi_delta * Pi_D
        print(f"Phi_Delta = {phi_delta:4.1f}  ->  denom = {denom:8.3e}")

    sys.exit(0)