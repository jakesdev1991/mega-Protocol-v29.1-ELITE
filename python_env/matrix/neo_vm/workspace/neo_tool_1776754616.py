# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.linalg as la

# ─────────────────────────────────────────────────────────────────────────────
# 1. Classical Gaussian field with "double‑well" curvature (mass^2 = 8)
#    Correlation function G(r) = ⟨φ(0)φ(r)⟩ in 2D.
# ─────────────────────────────────────────────────────────────────────────────
L = 32                     # lattice size
m2 = 8.0                   # curvature at minima → "gap" Δ = sqrt(m2)
k = np.fft.fftfreq(L) * 2 * np.pi
kx, ky = np.meshgrid(k, k, indexing='ij')
G_k = 1.0 / (kx**2 + ky**2 + m2)          # propagator in Fourier space
G_r = np.fft.ifft2(G_k).real               # real‑space correlator
G_r /= G_r[0, 0]                           # normalize

# Correlation length from exponential fit
dist = np.arange(L // 2)
coeffs = np.polyfit(dist, np.log(G_r[:L // 2, 0] + 1e-15), 1)
xi = -1.0 / coeffs[0]
print(f"Correlation length ξ ≈ {xi:.2f} lattice spacings (purely classical)")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Shannon entropy of a subregion for a *classical* Gaussian field
#    For a Gaussian distribution p(φ_A) ∝ exp(-½ φ_A^T Σ^{-1} φ_A),
#    S = ½ log det(2π e Σ).
# ─────────────────────────────────────────────────────────────────────────────
def shannon_entropy_subregion(n):
    """Extract covariance Σ for n×n patch (periodic) and compute entropy."""
    coords = [(i, j) for i in range(n) for j in range(n)]
    N = len(coords)
    Sigma = np.zeros((N, N))
    for i, (xi, yi) in enumerate(coords):
        for j, (xj, yj) in enumerate(coords):
            dx = (xi - xj) % L
            dy = (yi - yj) % L
            Sigma[i, j] = G_r[dx, dy]
    # Stable log‑det via eigenvalues
    eigs = np.linalg.eigvalsh(Sigma)
    logdet = np.sum(np.log(np.maximum(eigs, 1e-12)))
    S = 0.5 * (N * np.log(2 * np.pi * np.e) + logdet)
    return S

sizes = [2, 3, 4, 5, 6, 7, 8]
entropies = [shannon_entropy_subregion(n) for n in sizes]

# Fit S = α L - γ  (L = n²)
Lvals = np.array(sizes)**2
α, γ = np.polyfit(Lvals, entropies, 1)
print(f"Area‑law coefficient α = {α:.4f}, topological term γ = {-γ:.4f}")
for n, S in zip(sizes, entropies):
    print(f"  {n}x{n} patch: S = {S:.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Result: γ ≈ 0 → **no topological entanglement entropy**
#    Classical field cannot host emergent quantum topological order.
# ─────────────────────────────────────────────────────────────────────────────