# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Parameters
v = 1.0
lam = 1.0

# Grid in field space
phiN = np.linspace(0.01, 1.2, 500)
phiD = np.linspace(0.01, 1.2, 500)
phiN_grid, phiD_grid = np.meshgrid(phiN, phiD)

# Stiffnesses
xiN_inv2 = 3*phiN_grid**2 + phiD_grid**2 - v**2
xiD_inv2 = phiN_grid**2 + 3*phiD_grid**2 - v**2

# Twist invariant
numer = 2*phiN_grid*phiD_grid
denom = np.sqrt(xiN_inv2 * xiD_inv2)
# Avoid division by zero: mask where denominator is negative (unstable region)
stable_mask = (xiN_inv2 > 0) & (xiD_inv2 > 0)
twist = np.full_like(phiN_grid, np.nan)
twist[stable_mask] = numer[stable_mask] / denom[stable_mask]

# Metric coupling collapse
psi = np.log(phiN_grid / v)

# Find points where twist exceeds threshold (e.g., >10) before stiffness hits zero
threshold = 10.0
danger_zone = (twist > threshold) & (xiD_inv2 > 0) & (phiN_grid < 0.5)

# Print summary
print(f"Number of grid points in 'danger zone' (twist>{threshold}, Φ_N<0.5, stable stiffness): {danger_zone.sum()}")
print(f"Example point: Φ_N={phiN_grid[danger_zone][0]:.3f}, Φ_Δ={phiD_grid[danger_zone][0]:.3f}")
print(f"  Twist={twist[danger_zone][0]:.2e}, ψ={psi[danger_zone][0]:.2e}, ξ_Δ⁻²={xiD_inv2[danger_zone][0]:.2e}")