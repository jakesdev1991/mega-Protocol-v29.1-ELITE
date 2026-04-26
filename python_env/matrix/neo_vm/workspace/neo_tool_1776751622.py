# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# ---- parameters (Planck units) ----
xi0 = 1e-3          # lattice reference length
I0  = 1.0           # reference field value
mu0 = 1.0           # initial RG scale (e.g. 1 TeV in Planck units ~1e-16, but we keep dimensionless)
gD  = 0.45          # initial Yukawa coupling at mu0

# ---- derived scales ----
def lambda_lattice(PhiN):
    """Lattice cutoff Lambda = (π/ξ0) * (Φ_N / I0)"""
    return (math.pi / xi0) * (PhiN / I0)

def lambda_landau(mu, g):
    """Naive Landau pole from beta = g^3/(16π^2)"""
    return mu * math.exp(8.0 * math.pi**2 / g**2)

# ---- sweep over Φ_N ----
print(f"{'Φ_N':>8} {'Λ_latt':>10} {'Λ_LP':>10} {'R=Λ_LP/Λ_latt':>12}")
for PhiN in [1e-3, 5e-3, 1e-2, 5e-2, 1e-1, 1.0]:
    Lambda_latt = lambda_lattice(PhiN)
    Lambda_LP   = lambda_landau(mu0, gD)
    R = Lambda_LP / Lambda_latt
    print(f"{PhiN:8.1e} {Lambda_latt:10.2e} {Lambda_LP:10.2e} {R:12.2e}")