# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import mpmath as mp

# Define parameters
Lambda = 0.82
v = 1.28

# Define integrand for the radial integral
def integrand(k):
    # k is a real number in [0, Lambda]
    # compute k * exp(-k^2/(2*Lambda^2)) * arctan(k*v)
    return k * mp.e**(-k**2/(2*Lambda**2)) * mp.atan(k * v)

# Compute the radial integral using quad
I_radial = mp.quad(integrand, [0, Lambda])
I = (4 * mp.pi / v) * I_radial

# Compute I/(Lambda^2) factor
factor = I / (Lambda**2)

print("I (full integral) =", I)
print("I/(Lambda^2) =", factor)

# Estimate expected Phi_Delta/Phi_N ratio to achieve claimed delta_alpha/alpha = 3.21e-5
claimed_delta = 3.21e-5
# Assuming (Phi_Delta/Phi_N) * (1/Lambda^2) * I = delta
# So (Phi_Delta/Phi_N) = delta * Lambda^2 / I
ratio = claimed_delta * (Lambda**2) / I
print("Required Phi_Delta/Phi_N ratio to match claimed delta:", ratio)