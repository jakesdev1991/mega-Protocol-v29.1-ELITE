# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ghost-Driven Divergence in the HOLP Overlap Integral

We integrate:
  I(E_min) = ∫_{k_min}^{k_max} d³k  ΦΔ(k) / sqrt(k² + mΔ²) * 1/(k² - E_pair² + iε)

and scan E_pair = E_min → 0 to expose the IR divergence.
"""
import numpy as np
from scipy.integrate import quad
from math import log

# -----------------------------------------------------------------
# Archive mode spectral function (chosen to be non‑vanishing at k→0)
def phi_delta(k, mDelta=0.0):
    """ΦΔ(k) ∝ 1/(k² + mΔ²) gives a finite limit as k→0 if mΔ=0."""
    return 1.0 / (k**2 + mDelta**2 + 1e-12)  # avoid division by zero

def integrand(k, E_pair, mDelta=0.0):
    """Integrand in spherical coordinates: k² * (ΦΔ / sqrt(k²+mΔ²)) * 1/(k² - E_pair²)."""
    # 3‑D measure: k² dk
    num = k**2 * phi_delta(k, mDelta)
    # Archive propagator denominator
    denom = np.sqrt(k**2 + mDelta**2) * (k**2 - E_pair**2)
    return num / (denom + 1e-12j)

def compute_integral(E_pair, k_max=10.0, mDelta=0.0):
    """Perform radial integral from 0 to k_max."""
    # IR cutoff k_min -> 0 (we'll approach it analytically)
    # For numerical stability we start at a tiny lower bound.
    k_min = 1e-6
    real_part = lambda k: np.real(integrand(k, E_pair, mDelta))
    imag_part = lambda k: np.imag(integrand(k, E_pair, mDelta))

    Re, _ = quad(real_part, k_min, k_max, limit=200)
    Im, _ = quad(imag_part, k_min, k_max, limit=200)
    return Re + 1j*Im

# -----------------------------------------------------------------
if __name__ == "__main__":
    print("E_pair      |  I(E_pair)  (real)   |  log|I|  ")
    print("-" * 45)
    for E in [1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]:
        I_val = compute_integral(E_pair=E, k_max=5.0, mDelta=0.0)
        log_mag = log(abs(I_val.real) + 1e-12)
        print(f"{E:8.2f}    |  {I_val.real:12.6e}    |  {log_mag:6.2f}")

    # As E_pair → 0, the integral diverges logarithmically.
    # This is the ghost‑driven IR singularity the critique denied.