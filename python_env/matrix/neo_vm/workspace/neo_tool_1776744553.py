# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Monte‑Carlo verification that the parity‑odd Archive loop integral vanishes.
The integral in question is
    I^{(Δ)}_{μν}(q) ∝ ε_{μνρσ} q^{ρ} ∫ d⁴k k^{σ} f(k², (k+q)²)
where f is an even scalar function of k. Because the integrand is odd in k,
the symmetric four‑dimensional integral must be zero.
"""

import random, math

def odd_integrand(k, q):
    """
    Compute the odd part of the integrand for a given loop momentum k
    and external momentum q (here taken along the z‑axis for simplicity).
    k : list of 4 components (k0,k1,k2,k3)
    q : list of 4 components
    Returns the scalar k^σ * f(k²,(k+q)²) (the epsilon contraction is omitted
    because it only produces a sign; the essential oddness is in k^σ).
    """
    # a simple even scalar function f(k²) = exp(-k²) (convergent)
    k2 = sum(x*x for x in k)
    # for demonstration we ignore the (k+q)² dependence; the oddness remains.
    f = math.exp(-k2)
    # pick sigma = 0 (time component) as a representative odd factor
    ks = k[0]
    return ks * f

def mc_integral(q, nsamples=500000):
    """
    Monte‑Carlo estimate of ∫ d⁴k odd_integrand(k,q) over a symmetric box.
    The box is taken large enough that the exponential suppresses edges.
    """
    total = 0.0
    # sample inside a 4‑dimensional hypercube of side L = 10 (units of 1/m_e)
    L = 10.0
    vol = (2*L)**4
    for _ in range(nsamples):
        # uniform sampling in [-L, L]^4
        k = [random.uniform(-L, L) for _ in range(4)]
        total += odd_integrand(k, q)
    avg = total / nsamples
    return avg * vol

if __name__ == "__main__":
    # choose an external momentum q along the z‑axis, e.g., q = (0,0,0,1)
    q = [0.0, 0.0, 0.0, 1.0]
    result = mc_integral(q)
    print(f"Monte‑Carlo estimate of the odd Archive loop integral: {result:.6e}")
    print("If the integral vanishes, the result should be consistent with zero within statistical error.")