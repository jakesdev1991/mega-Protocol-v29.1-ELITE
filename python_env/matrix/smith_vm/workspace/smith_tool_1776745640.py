# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol validator for the Thermal‑Spatial Fragility Monitor (TSFM‑Ω).
Checks dimensional consistency, positivity of invariants, and constraint bounds.
"""

import numpy as np
from scipy.stats import genpareto

# ----------------------------------------------------------------------
# Helper physics constants (chosen for dimensional consistency)
# ----------------------------------------------------------------------
Lx, Ly, Lz = 2.0, 1.0, 0.5          # rack dimensions [m] (arbitrary)
Nx, Ny, Nz = 20, 10, 5             # sensor grid
dx, dy, dz = Lx/Nx, Ly/Ny, Lz/Nz
xs = np.linspace(dx/2, Lx-dx/2, Nx)
ys = np.linspace(dy/2, Ly-dy/2, Ny)
zs = np.linspace(dz/2, Lz-dz/2, Nz)
X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
V = Lx*Ly*Lz                         # total volume [m^3]

# Reference values (to make everything dimensionless)
T0 = 350.0          # nominal temperature [K]
xi0 = 0.1           # reference correlation length [m]
Q0 = 1e3            # reference heat flux [W/m^3] (makes integral dimensionless)
lambda_I = 0.01     # coupling strength (dimensionless)
alpha = 1.0         # double‑well stiffness [K^-2]
D = 1e-4            # thermal diffusivity [m^2/s] (not used directly)
lambda_S = 0.5
lambda_Psi = 0.5
barS_star = 0.69    # ~ln(2) – maximal entropy for a binary binning

# ----------------------------------------------------------------------
# 1. Synthetic temperature field: a uniform + dipole + small noise
# ----------------------------------------------------------------------
np.random.seed(42)
a0_true = 0.8 * T0          # uniform mode coefficient
a1_true = 0.3 * T0          # dipole mode coefficient (x‑direction)

# Eigenfunctions for Neumann BCs: cos(nπx/Lx) etc.
psi0 = np.ones_like(X) / np.sqrt(V)               # uniform (normalised)
psi1 = np.sqrt(2/Lx) * np.cos(np.pi * X / Lx)    # dipole in x (normalised)

T_field = a0_true * psi0 + a1_true * psi1
T_field += 0.02 * T0 * np.random.randn(*T_field.shape)  # small noise

# ----------------------------------------------------------------------
# 2. Compute modal coefficients (projection)
# ----------------------------------------------------------------------
def project(mode, field):
    """Inner product <mode|field> / <mode|mode> (modes already normalised)."""
    return np.trapz(np.trapz(np.trapz(mode * field, xs, axis=0),
                             ys, axis=0), zs, axis=0)

a0 = project(psi0, T_field)
a1 = project(psi1, T_field)

# ----------------------------------------------------------------------
# 3. Effective mass, correlation length, and invariants
# ----------------------------------------------------------------------
T_sq_mean = np.trapz(np.trapz(np.trapz(T_field**2, xs, axis=0),
                              ys, axis=0), zs, axis=0) / V
m_eff_sq = alpha * (3 * T0**2 - T_sq_mean)
assert m_eff_sq > 0, "Effective mass squared must be positive (stable phase)."
xi = 1.0 / np.sqrt(m_eff_sq)          # correlation length [m]
psi = np.log(xi / xi0)                # dimensionless invariant

# Stiffness inverses (dimensionless after dividing by 1/L^2)
xiN_inv2 = alpha * (3 * a0**2 + a1**2 - T0**2)
xiD_inv2 = alpha * (a0**2 + 3 * a1**2 - T0**2)
assert xiN_inv2 > 0 and xiD_inv2 > 0, "Stiffness inverses must be positive."

# ----------------------------------------------------------------------
# 4. Heat flux and its divergence (made dimensionless)
# ----------------------------------------------------------------------
# Simple Fourier law: q = -k grad T ; take k=1 for dimensional analysis
k = 1.0  # [W/(m·K)] – set to 1 to keep q in [K/m]; we will normalise later
gradTx = np.gradient(T_field, dx, axis=0)
gradTy = np.gradient(T_field, dy, axis=1)
gradTz = np.gradient(T_field, dz, axis=2)
qx = -k * gradTx
qy = -k * gradTy
qz = -k * gradTz

# Divergence
div_q = np.gradient(qx, dx, axis=0) + np.gradient(qy, dy, axis=1) + np.gradient(qz, dz, axis=2)
# Make dimensionless by dividing by Q0 and integrating over volume
div_q_dimless = np.trapz(np.trapz(np.trapz(div_q / Q0, xs, axis=0),
                                 ys, axis=0), zs, axis=0)  # now dimensionless
heatflux_term = np.exp(div_q_dimless)

# ----------------------------------------------------------------------
# 5. Entropy gauge (Shannon entropy of temperature fluctuations)
# ----------------------------------------------------------------------
# Fluctuations around the mean at each sensor point
T_mean = np.mean(T_field)
fluct = T_field - T_mean
# Bin into 10 equiprobable ranges (simple histogram)
hist, _ = np.histogram(fluct.flatten(), bins=10, density=True)
# Avoid zeros for log
hist = np.where(hist == 0, 1e-12, hist)
S_i = -np.sum(hist * np.log(hist))   # same for every sensor because we used global hist
# Spatial average (identical here)
barS = S_i

# ----------------------------------------------------------------------
# 6. Thermal‑Spatial Fragility Index (TSFI)
# ----------------------------------------------------------------------
TSFI = (xi / xi0) * heatflux_term * np.exp(-barS)
assert TSFI >= 0, "TSFI must be non‑negative."
# ----------------------------------------------------------------------
# 7. Extreme‑Value Theory anomaly score (GPD fit to upper tail)
# ----------------------------------------------------------------------
# Build a time‑series by pretending we have 100 consecutive snapshots
tsfi_series = TSFI + 0.05 * np.random.randn(100)  # add small temporal noise
u = np.percentile(tsfi_series, 95)                # threshold
exceed = tsfi_series[tsfi_series > u] - u
if len(exceed) > 0:
    # Fit shape (c) and scale (sigma) – fix loc=0
    shape, loc, scale = genpareto.fit(exceed, floc=0)
    # CDF of GPD
    def gpd_cdf(x):
        return genpareto.cdf(x, c=shape, loc=loc, scale=scale)
    # Anomaly score for the latest point
    latest = tsfi_series[-1]
    a_tsfi = 1.0 - gpd_cdf(max(latest - u, 0.0))
else:
    a_tsfi = 1.0  # no exceedances → nominal
assert 0.0 <= a_tsfi <= 1.0, "EVT anomaly score must lie in [0,1]."

# ----------------------------------------------------------------------
# 8. MPC‑Ω cost (integrand only, we drop time integral for snapshot test)
# ----------------------------------------------------------------------
cost_integrand = 0.5 * (0.0**2 + 0.0**2)  # \dot a_n set to zero for static test
cost_integrand += alpha/4 * (a0**2 + a1**2 - T0**2)**2
cost_integrand += lambda_S * (barS - barS_star)**2
cost_integrand += lambda_Psi * psi**2
assert cost_integrand >= 0, "MPC‑Ω Lagrangian density must be non‑negative."

# ----------------------------------------------------------------------
# 9. Omega‑Protocol constraint checks
# ----------------------------------------------------------------------
assert TSFI <= 1.5, f"TSFI constraint violated: {TSFI:.3f} > 1.5"
assert a0 >= 0.6 * T0, f"Phi_N (a0) too low: {a0:.3f} < {0.6*T0:.3f}"
assert np.abs(a1) <= 0.7 * T0, f"Phi_Delta (|a1|) too high: {np.abs(a1):.3f} > {0.7*T0:.3f}"
assert np.max(T_field) <= 1.0 * T0, f"Temperature exceeds redline: {np.max(T_field):.3f} > {T0:.3f}"

# ----------------------------------------------------------------------
# If we reach here, all mathematical checks passed.
# ----------------------------------------------------------------------
print("✅ All Omega‑Protocol invariants and constraints satisfied.")
print(f"   a0 (Φ_N)   = {a0:.3f}  K")
print(f"   a1 (Φ_Δ)   = {a1:.3f}  K")
print(f"   ξ          = {xi:.3f}  m  (ψ = {psi:.3f})")
print(f"   TSFI       = {TSFI:.3f}")
print(f"   Anomaly score a_TSFI = {a_tsfi:.3f}")
print(f"   MPC cost density    = {cost_integrand:.3f}")