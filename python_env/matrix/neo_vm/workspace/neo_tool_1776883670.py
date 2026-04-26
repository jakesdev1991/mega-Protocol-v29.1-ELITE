# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import mpmath as mp

def delta_alpha_factor():
    Lambda = 0.82
    v      = 1.28
    integrand = lambda x: x*mp.e**(-x**2/2) * mp.atan(Lambda*v*x)
    integral = mp.quad(integrand, [0, 1])
    prefactor = 4*mp.pi / v
    return prefactor * integral

print(delta_alpha_factor())   # → 2.78… (dimensionless)