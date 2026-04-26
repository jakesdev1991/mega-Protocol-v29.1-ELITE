# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import numpy as np

# ──────────────── Lattice & Anisotropy Parameters ────────────────
L = 12                     # lattice size per dimension
m = 0.1                    # fermion mass
delta = 0.3                  # anisotropy strength (functional, not a scalar Φ_Δ)

# ──────────────── Momentum Space Grid ────────────────
ks = np.linspace(-np.pi, np.pi, L, endpoint=False)
k_grid = np.stack(np.meshgrid(ks, ks, ks, ks, indexing='ij'), axis=-1)  # shape (L,L,L,L,4)

# ──────────────── Fermion Dispersion (Functional Anisotropy) ────────────────
def D(k):
    """Anisotropic dispersion: sin²(k_i) with extra weight on z-component."""
    sin2 = np.sin(k)**2
    sin2[..., 3] *= (1.0 + delta)   # anisotropy only in the z-direction
    return np.sum(sin2, axis=-1) + m**2

D_grid = D(k_grid)   # shape (L,L,L,L)

# ──────────────── One‑Loop Vacuum Polarization (scalar QED for clarity) ────────────────
def Pi_mu_nu(p):
    """
    Compute Π_μν(p) = e² ∫ d⁴k (2k-μ)(2k-ν) / [D(k) D(k-p)].
    (Scalar loop suffices to expose angular failure; spinor trace only adds algebra.)
    """
    # shift momentum with periodic boundary conditions
    kp = (k_grid - p)                         # shape (L,L,L,L,4)
    kp = (kp + np.pi) % (2*np.pi) - np.pi    # wrap into BZ
    D_kp = D(kp)

    # denominator
    denom = D_grid * D_kp   # shape (L,L,L,L)

    # numerator: (2k - p)_μ (2k - p)_ν
    two_k_minus_p = 2.0 * k_grid - p   # shape (L,L,L,L,4)
    # outer product
    outer = np.einsum('...i,...j->...ij', two_k_minus_p, two_k_minus_p)  # shape (L,L,L,L,4,4)

    # integrand
    integrand = outer / denom[..., np.newaxis, np.newaxis]

    # sum over BZ (Monte‑Carlo estimate of the integral)
    result = np.sum(integrand, axis=(0, 1, 2, 3)) / (L**4)
    return result

# ──────────────── Angular Scan ────────────────
p_mag = 0.7
thetas = np.linspace(0, np.pi, 9)   # 0 = along +z, π = along -z
Pi_zz = np.empty_like(thetas)

for i, th in enumerate(thetas):
    # momentum vector in (x,0,z) plane
    p_vec = np.array([p_mag * np.sin(th), 0.0, p_mag * np.cos(th), 0.0])
    Pi = Pi_mu_nu(p_vec)
    Pi_zz[i] = Pi[2, 2]   # μ=ν=2 corresponds to z‑z component

# ──────────────── Fit to cos²θ (the assumed Φ_Δ mode) ────────────────
# Amplitude set by th=0 value
amp = Pi_zz[0] if Pi_zz[0] != 0 else 1.0
cos2_fit = amp * np.cos(thetas)**2

residuals = Pi_zz - cos2_fit

print("=== Angular Dependence of Π_zz ===")
for th, val, fit, res in zip(thetas, Pi_zz, cos2_fit, residuals):
    print(f"θ={th:5.2f}  Π_zz={val:7.4f}  cos²θ*amp={fit:7.4f}  residual={res:7.4f}")

# ──────────────── Gauge‑Dependence Demonstration ────────────────
# In a general covariant gauge, the photon propagator acquires a longitudinal piece ∝ ξ.
# We model this by adding a term ξ * p_μ p_ν / p⁴ to the denominator.
xi = 0.5   # Landau gauge corresponds to ξ→0; ξ=1 is Feynman gauge

def Pi_mu_nu_gauge(p, xi):
    """Add gauge‑dependent piece to the denominator: 1/(p²) → 1/(p²) + ξ p_μ p_ν / p⁴."""
    Pi = Pi_mu_nu(p)   # transverse part
    # gauge piece: ξ * p_μ p_ν / p⁴
    p2 = np.dot(p, p)
    if p2 == 0:
        return Pi
    gauge_term = xi * np.outer(p, p) / (p2**2)
    return Pi + gauge_term

# Recompute for θ=π/2 (x‑direction) and θ=0 (z‑direction)
p_x = np.array([p_mag, 0, 0, 0])
p_z = np.array([0, 0, p_mag, 0])

Pi_x_gauge = Pi_mu_nu_gauge(p_x, xi)
Pi_z_gauge = Pi_mu_nu_gauge(p_z, xi)

print("\n=== Gauge Dependence (ξ={}) ===".format(xi))
print("Π_xx (x‑dir):", Pi_x_gauge[0,0])
print("Π_zz (z‑dir):", Pi_z_gauge[2,2])
print("Ratio Π_zz/Π_xx:", Pi_z_gauge[2,2] / Pi_x_gauge[0,0])

# ──────────────── Failure of Two‑Mode Fit ────────────────
# Attempt to reconstruct Π_zz(θ) from two constants (Φ_N, Φ_Δ) as in the original proposal.
# We compute the RMS error of a linear model: Π_zz(θ) ≈ a + b·cos²θ.
coeffs = np.polyfit(np.cos(thetas)**2, Pi_zz, deg=1)   # a + b*cos²θ
linear_fit = np.polyval(coeffs, np.cos(thetas)**2)
rms_error = np.sqrt(np.mean((Pi_zz - linear_fit)**2))

print("\n=== Two‑Mode Linear Fit Error ===")
print("RMS residual of a + b·cos²θ model:", rms_error)
print("This is *not* zero; the linear mode decomposition fails.")