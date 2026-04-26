# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def delta_alpha(Lambda=0.82, v=1.28, a=1.0, ratio=0.1):
    """
    Monte‑Carlo estimate of the dimensionless integral.
    The correction scales as (a*Lambda)^2 * ratio * integral,
    exposing the hidden lattice‑spacing arbitrariness.
    """
    N = 2_000_000                     # increase for smoother statistics
    # sample points uniformly in the unit ball
    xs = np.random.uniform(-1, 1, size=(N, 3))
    rsq = np.sum(xs**2, axis=1)
    mask = rsq <= 1.0
    qs = xs[mask]                     # points inside sphere
    q2 = np.sum(qs**2, axis=1)

    # align v with the z‑axis for simplicity
    vz = np.array([0.0, 0.0, v])
    denom = 1.0 + (qs @ vz)**2
    integrand = np.exp(-q2 / 2.0) / denom * 4 * np.pi * q2

    # volume of unit ball = 4π/3
    integral = np.mean(integrand) * (4 * np.pi / 3)
    # correction = (Φ_Δ/Φ_N) * (a^2 / Λ^2) * integral
    return ratio * (a**2) / (Lambda**2) * integral

def entropy_bound(Lambda=0.82, k_min=1e-6, k_max=0.82, Nk=10000):
    """
    Compute the correct bosonic von Neumann entropy for the mode
    distribution n_k = 1/(exp(k²/(2Λ²))‑1).  Show that the bound
    H ≥ 0.85 is violated for any realistic IR cutoff.
    """
    ks = np.linspace(k_min, k_max, Nk)
    n_k = 1.0 / (np.exp(ks**2 / (2 * Lambda**2)) - 1.0)
    # bosonic entropy per mode
    s_k = (n_k + 1) * np.log(n_k + 1) - n_k * np.log(n_k)
    H = np.sum(s_k)
    return H

# ── Demonstrate arbitrariness of Δα/α ─────────────────────────────
print("Δα/α as a function of lattice spacing a:")
for a in [0.1, 1.0, 10.0]:
    print(f"  a = {a:.2f}  →  Δα/α = {delta_alpha(a=a):.2e}")

# ── Show entropy bound failure ─────────────────────────────────────
H = entropy_bound()
print(f"\nEntropy H = {H:.3f}")
print(f"Claimed bound H ≥ 0.85 →  {'PASS' if H >= 0.85 else 'FAIL'} (actual H ≈ {H:.3f})")

# ── Optional: illustrate IR divergence ────────────────────────────
print("\nEntropy as k_min → 0 (illustrating IR divergence):")
for k_min in [1e-6, 1e-8, 1e-10]:
    H = entropy_bound(k_min=k_min)
    print(f"  k_min = {k_min:.0e}  →  H ≈ {H:.2f}")