# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Higher-Order Lattice Polarization
Checks:
  - Poisson recovery of Φ_N
  - Orthogonality ⟨Φ_N|Φ_Δ⟩ = 0
  - UV finiteness of Φ_Δ energy
  - Conservation of J* (∂·J* ≈ 0)
Replace the placeholder definitions with the actual analytic forms
once they are available.
"""

import numpy as np

# ----------------------------------------------------------------------
# Configuration (tune to match the physical regime)
# ----------------------------------------------------------------------
L = 5.0                 # box half‑size (units)
N = 128                 # grid points per dimension
dx = 2 * L / N          # lattice spacing
x = np.linspace(-L, L, N, endpoint=False)
X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
r = np.sqrt(X**2 + Y**2 + Z**2)
r[r == 0] = dx/2        # avoid division by zero at origin

# Parameters from the thought (to be varied in sensitivity scans)
Lambda = 0.82
v = 1.28
Lambda_c = 1.0          # UV cutoff for finiteness test

# ----------------------------------------------------------------------
# Placeholder model functions (replace with true expressions)
# ----------------------------------------------------------------------
def Phi_N(r, lam):
    """Screened Coulomb: erf(r/(√2 λ))/r  → recovers 1/r as r→0."""
    return np.where(r > 0, np.erf(r/(np.sqrt(2)*lam))/r, 2/(np.sqrt(2*np.pi)*lam))

def Phi_Delta(r, lam, v):
    """Simple massive mode: v^2 * (exp(-r/lam)/r)  → falls off exponentially."""
    return v**2 * np.where(r > 0, np.exp(-r/lam)/r, 1/lam)

# ----------------------------------------------------------------------
# Helper: finite‑difference Laplacian (7‑point stencil)
# ----------------------------------------------------------------------
def laplacian(f, h):
    return (np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
            np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) +
            np.roll(f, 1, axis=2) + np.roll(f, -1, axis=2) -
            6*f) / (h**2)

# ----------------------------------------------------------------------
# 1. Poisson recovery test
# ----------------------------------------------------------------------
phiN = Phi_N(r, Lambda)
lap_phiN = laplacian(phiN, dx)
# Expected source: -4π δ(r). Approximate δ by a normalized Gaussian of width dx.
delta_approx = np.exp(-(r**2)/(2*dx**2)) / ((2*np.pi)**(1.5) * dx**3)
residual = lap_phiN + 4*np.pi*delta_approx
poisson_err = np.linalg.norm(residual) / np.linalg.norm(4*np.pi*delta_approx)

# ----------------------------------------------------------------------
# 2. Orthogonality test
# ----------------------------------------------------------------------
phiD = Phi_Delta(r, Lambda, v)
overlap = np.sum(phiN * phiD) * dx**3
ortho_err = np.abs(overlap)

# ----------------------------------------------------------------------
# 3. UV finiteness of Φ_Δ energy density
# ----------------------------------------------------------------------
energy_density = 0.5 * (np.gradient(phiD, dx, axis=0)**2 +
                        np.gradient(phiD, dx, axis=1)**2 +
                        np.gradient(phiD, dx, axis=2)**2) + 0.5 * (phiD**2) / (Lambda**2)
# Mask UV region (r > Lambda_c)
uv_mask = r > Lambda_c
uv_energy = np.sum(energy_density[uv_mask]) * dx**3
# Require UV energy < 1% of total energy as a sanity bound
total_energy = np.sum(energy_density) * dx**3
uv_frac = uv_energy / total_energy if total_energy != 0 else np.inf

# ----------------------------------------------------------------------
# 4. Current conservation test (J* = Φ_N ∇Φ_Δ − Φ_Δ ∇Φ_N)
# ----------------------------------------------------------------------
grad_phiN = np.stack(np.gradient(phiN, dx, axis=(0,1,2)), axis=-1)
grad_phiD = np.stack(np.gradient(phiD, dx, axis=(0,1,2)), axis=-1)
Jstar = phiN[...,None] * grad_phiD - phiD[...,None] * grad_phiN
div_J = (np.gradient(Jstar[...,0], dx, axis=0) +
         np.gradient(Jstar[...,1], dx, axis=1) +
         np.gradient(Jstar[...,2], dx, axis=2))
curr_err = np.linalg.norm(div_J) / (np.linalg.norm(Jstar) + 1e-12)

# ----------------------------------------------------------------------
# Tolerances (tight but realistic for numerical validation)
# ----------------------------------------------------------------------
TOL_POISSON = 1e-2   # 2% relative error in Poisson source
TOL_ORTHO   = 1e-3   # orthogonality integral < 1e-3
TOL_UV_FRAC = 0.01   # UV energy < 1% of total
TOL_CURRENT = 1e-2   # current divergence < 2% of |J*|

# ----------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------
def verdict(name, err, tol):
    return err <= tol

results = {
    "Poisson recovery": verdict("Poisson", poisson_err, TOL_POISSON),
    "Orthogonality":    verdict("Ortho",   ortho_err,   TOL_ORTHO),
    "UV finiteness":    verdict("UV frac", uv_frac,    TOL_UV_FRAC),
    "Current cons.":    verdict("Current", curr_err,   TOL_CURRENT),
}

all_pass = all(results.values())
print("\n=== Omega Protocol Invariant Validation ===")
for k, v in results.items():
    print(f"{k:20}: {'PASS' if v else 'FAIL'} (err={err if (err:=locals().get(k.lower().replace(' ', '_'))) else 'N/A'})")
print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")
if not all_pass:
    print("\nAction: Derivation must supply explicit Hamiltonian‑based proof of Z2 orthogonality,")
    print("        and demonstrate Poisson recovery and current conservation analytically.")