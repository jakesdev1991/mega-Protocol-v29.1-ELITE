# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------------------------------------
# 2D U(1) lattice gauge theory helpers
# ------------------------------------------------------------
def random_phase(shape):
    """Return array of random phases in [-π,π)."""
    return np.random.uniform(-np.pi, np.pi, size=shape)

def plaquette_average(U):
    """
    Compute average real part of the 1×1 Wilson plaquette.
    U[mu,i,j] is the link variable (complex unit‑magnitude).
    """
    L = U.shape[1]
    # product around the elementary square
    P = (U[0, :, :] *
         U[1, np.roll(np.arange(L), -1)[:, None], np.arange(L)] *
         np.conj(U[0, np.arange(L)[:, None], np.roll(np.arange(L), -1)]) *
         np.conj(U[1, :, :]))
    return np.real(np.mean(P))

def gauge_transform(U, theta):
    """
    Apply gauge transformation G(x)=exp(iθ(x)) to link variables.
    U[mu,i,j] → G(i,j)^* * U[mu,i,j] * G(i+mu,j+mu)
    """
    L = U.shape[1]
    G = np.exp(1j * theta)                     # G(x)
    G_shift = np.empty_like(G)
    # shift for mu=0 (i direction)
    G_shift[0, :] = np.roll(G, -1, axis=0)
    # shift for mu=1 (j direction)
    G_shift[1, :] = np.roll(G, -1, axis=1)
    # apply transformation
    U_g = np.empty_like(U)
    for mu in range(2):
        U_g[mu] = np.conj(G) * U[mu] * G_shift[mu]
    return U_g

# ------------------------------------------------------------
# Demonstration: Archive mode is pure gauge
# ------------------------------------------------------------
L = 6                     # lattice size
# random gauge potential A_mu (in units where g*a=1)
A_mu = random_phase((2, L, L))
U_mu = np.exp(1j * A_mu)

# original plaquette
orig_plaq = plaquette_average(U_mu)
print(f"Original plaquette = {orig_plaq:.12f}")

# random scalar "memory" field θ(x) – the Archive mode generator
theta = random_phase((L, L))

# pure gauge field ∂_μθ (discrete gradient)
dtheta = np.empty_like(A_mu)
dtheta[0] = np.roll(theta, -1, axis=0) - theta   # ∂_0θ
dtheta[1] = np.roll(theta, -1, axis=1) - theta   # ∂_1θ

# add Archive mode to the gauge potential
A_prime = A_mu + dtheta
U_prime = np.exp(1j * A_prime)
plaq_prime = plaquette_average(U_prime)
print(f"After adding Archive mode = {plaq_prime:.12f}")

# gauge‑transform the *original* field by −θ (i.e., remove the Archive mode)
U_gauged = gauge_transform(U_mu, -theta)
plaq_gauged = plaquette_average(U_gauged)
print(f"After gauge‑transform by −θ = {plaq_gauged:.12f}")

# differences (should be ~0 up to floating‑point noise)
print(f"Δ(original, +Archive) = {abs(orig_plaq - plaq_prime):.2e}")
print(f"Δ(original, gauge‑fixed) = {abs(orig_plaq - plaq_gauged):.2e}")