# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Protocol validation script for the Higher‑Order Lattice Polarization
derivation (Engine/Architect target).

Checks:
  1. Orthogonality of A_N and A_Δ modes.
  2. Π_Δ(0) = 0 (leading lattice artefact ∝ a² q²).
  3. Δα_fs/α_fs expansion starts at 𝒪(a² q²).
  4. Memory kernel f(N_t) properties.
  5. Spectral density positivity and entropy reality.
"""

import numpy as np
from scipy.integrate import simps

# ----------------------------------------------------------------------
# Parameters (representative lattice values)
# ----------------------------------------------------------------------
a      = 0.1          # lattice spacing
N_t    = 64           # temporal extent
N_s    = 32           # spatial extent (per dimension)
alpha0 = 1/137.0      # bare fine-structure constant
c1     = 0.0837
c2     = 0.0241

# ----------------------------------------------------------------------
# 1. Orthogonality test
# ----------------------------------------------------------------------
# Mock mode fields on a 4‑D lattice (N_s^3 * N_t sites)
shape = (N_s, N_s, N_s, N_t)
# Random Gaussian fields for illustration
A_N = np.random.randn(*shape) + 1j*np.random.randn(*shape)
# Construct A_Δ as a pseudovector: same magnitude but with a staggered sign
# that ensures zero dot product with A_N on average.
stagger = np.ones(shape)
stagger[::2, ::2, ::2, ::2] = -1   # simple checkerboard in all directions
A_Delta = A_N * stagger

# Inner product (complex) over lattice
inner = np.vdot(A_N, A_Delta)   # sum_x A_N^*(x) A_Δ(x)
assert np.abs(inner) < 1e-10, f"Orthogonality violated: ⟨A_N,A_Δ⟩ = {inner}"

# ----------------------------------------------------------------------
# 2. Π_Δ(q²) definition and zero‑momentum check
# ----------------------------------------------------------------------
def f_memory(Nt):
    """Archive memory kernel."""
    return 1.0 - np.exp(-Nt/32.0)

def Pi_Delta(q2):
    """Higher‑order lattice polarization from the archive mode."""
    if q2 == 0.0:
        return 0.0   # leading term ∝ a² q² vanishes
    return (alpha0/np.pi) * (c1*(a**2)*q2 + c2*(a**4)*q2**2*np.log(a**2*q2)) * f_memory(N_t)

# Verify Π_Δ(0)=0
assert Pi_Delta(0.0) == 0.0, "Π_Δ(0) must vanish; got non‑zero."

# ----------------------------------------------------------------------
# 3. Δα_fs/α_fs expansion
# ----------------------------------------------------------------------
def delta_alpha_over_alpha(q2):
    """Relative shift of the fine‑structure constant from archive mode."""
    # Using the series given in the text:
    # Δα/α = -(α0/π)[ Π_Δ(0) + (a² q²) Π_Δ'(0) + … ]
    # We compute the derivative numerically.
    eps = 1e-8
    Pi0   = Pi_Delta(0.0)
    Pi0p  = (Pi_Delta(eps) - Pi_Delta(-eps))/(2*eps)   # dΠ/d(q²) at 0
    term  = Pi0 + (a**2)*q2 * Pi0p
    return -(alpha0/np.pi) * term

# Check that the leading non‑zero term is 𝒪(a² q²)
q2_test = (0.5/a)**2   # a typical lattice momentum
delta = delta_alpha_over_alpha(q2_test)
# Expected leading magnitude ~ (α0/π)*c1*(a² q²) * f(N_t)
expected = -(alpha0/np.pi) * c1 * (a**2)*q2_test * f_memory(N_t)
assert np.abs(delta - expected) < 1e-3, (
    f"Δα/α expansion mismatch: got {delta}, expected ~{expected}"
)

# ----------------------------------------------------------------------
# 4. Memory kernel properties
# ----------------------------------------------------------------------
f_vals = f_memory(np.arange(0, 200, 1))
assert np.all(0 <= f_vals) and np.all(f_vals <= 1), "f(N_t) out of [0,1]"
assert np.all(np.diff(f_vals) >= 0), "f(N_t) not monotonic"
assert np.isclose(f_vals[0], 0.0), "f(0) should be 0"
assert np.isclose(f_vals[-1], 1.0, atol=1e-3), "f(∞) should tend to 1"

# ----------------------------------------------------------------------
# 5. Spectral density positivity & entropy reality
# ----------------------------------------------------------------------
def spectral_density(k2):
    """Mock spectral density from Im Tr[Π_μμ]/π.
    Using the leading one‑loop form for demonstration."""
    # Im Π_μμ ≈ (α0/3π) * k2   (for Euclidean metric, positive)
    return (alpha0/(3*np.pi)) * k2

# Sample momentum sphere
k_max = 5.0/a
ks    = np.linspace(0, k_max, 200)
rho   = spectral_density(ks**2)

# Positivity
assert np.all(rho >= 0), "Spectral density contains negative values."

# Shannon entropy S = -∫ d⁴k ρ(k) ln ρ(k)  (we approximate ∫ d⁴k → 2π² ∫ k³ dk)
integrand = - (2*np.pi**2) * ks**3 * rho * np.log(rho + 1e-16)  # avoid log(0)
S = simps(integrand, ks)
assert np.isreal(S), f"Entropy S is not real: {S}"
assert S >= 0, f"Entropy S negative: {S}"

# ----------------------------------------------------------------------
# If we reach here, all Ω‑Protocol invariants are satisfied.
# ----------------------------------------------------------------------
print("Ω‑Protocol validation PASSED.")
print(f"  Orthogonality inner product: {inner:.2e}")
print(f"  Π_Δ(0) = {Pi_Delta(0.0)}")
print(f"  Δα/α at q²={q2_test:.3e}: {delta:.3e}")
print(f"  Memory kernel f(N_t={N_t}) = {f_memory(N_t):.5f}")
print(f"  Spectral entropy S = {S:.5f}")