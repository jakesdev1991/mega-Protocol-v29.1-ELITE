# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simple 2D lattice model for Wilson fermion polarization
# The goal: compute Pi_Delta(0) = h0^2 * sum_{p} Tr[ S(p) S(p) ]
# and show that it can diverge and cause tachyonic instability.

def wilson_propagator_momentum(p, m0, r=1.0, a=1.0):
    """
    Wilson fermion propagator in momentum space (2D).
    S(p) = 1 / (i*gamma·sin(p) + m0 + r*sum_mu (1 - cos(p_mu)))
    For simplicity, we treat gamma matrices as Pauli matrices in 2D,
    but we only need the trace of S(p)*S(p) which is independent of gamma structure
    for the scalar polarization. We'll approximate the denominator.
    """
    # Wilson term
    wilson_term = r * np.sum(1 - np.cos(p * a))
    # Total mass term
    total_mass = m0 + wilson_term
    # For trace of S*S, we approximate the denominator squared
    # In 2D, Tr[S(p) S(p)] ≈ 2 / (total_mass**2 + sin^2 terms)
    # We'll approximate sin^2 term by average over momenta
    sin_term_sq = np.sum(np.sin(p * a)**2)
    denom = total_mass**2 + sin_term_sq
    # Trace of product of two propagators (scalar part)
    # In continuum: Tr[S(p) S(p)] = 4 / (p^2 + m^2)^2
    # Here we approximate by 2 / denom^2 for 2D (2 spinor components)
    return 2.0 / (denom**2)

def compute_pi_delta(L, h0, m0=0.1, M0=0.1):
    """
    Compute Pi_Delta(0) on an LxL lattice (in lattice units).
    Sum over momentum space grid.
    """
    # Momentum grid: [-π, π) excluding zeros? We'll include all.
    ks = np.linspace(-np.pi, np.pi, L, endpoint=False)
    pi_delta = 0.0
    count = 0
    for px in ks:
        for py in ks:
            p = np.array([px, py])
            # Avoid p = (0,0) divergence? Wilson term regularizes it.
            pi_delta += wilson_propagator_momentum(p, m0)
            count += 1
    # Multiply by h0^2 and volume factor (2π)^2 / L^2 approximated by count
    # Actually sum over all modes: each mode weight is (2π/L)^2, but we just sum.
    # We'll normalize by count to get average, then multiply by h0^2 * count.
    # Simpler: pi_delta = h0^2 * sum
    pi_delta = h0**2 * pi_delta
    return pi_delta

def simulate_shredding():
    # Simulate for various lattice sizes and couplings
    Ls = [10, 20, 30, 40, 50]
    h0s = np.linspace(0.1, 2.0, 10)
    m0 = 0.1
    M0 = 0.1  # small Archive mass
    
    results = []
    for L in Ls:
        for h0 in h0s:
            pi = compute_pi_delta(L, h0, m0, M0)
            m_eff_sq = M0**2 + pi
            # Check for tachyonic instability (negative m_eff^2)
            is_tachyon = m_eff_sq < 0
            # Shredding invariant psi = ln(m_eff / m0)
            # If m_eff is negative, psi is complex -> physically meaningless
            if m_eff_sq > 0:
                psi = np.log(np.sqrt(m_eff_sq) / m0)
            else:
                psi = np.nan  # indicates breakdown
            results.append((L, h0, pi, m_eff_sq, is_tachyon, psi))
    
    # Plot results: Pi vs h0 for different L
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    # Pi scaling
    for L in Ls:
        pi_vals = [r[2] for r in results if r[0] == L]
        h_vals = [r[1] for r in results if r[0] == L]
        axes[0,0].plot(h_vals, pi_vals, label=f'L={L}')
    axes[0,0].set_xlabel('h0')
    axes[0,0].set_ylabel('Pi_Delta(0)')
    axes[0,0].set_title('Pi_Delta(0) scaling with coupling')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # Effective mass squared
    for L in Ls:
        meff_vals = [r[3] for r in results if r[0] == L]
        h_vals = [r[1] for r in results if r[0] == L]
        axes[0,1].plot(h_vals, meff_vals, label=f'L={L}')
    axes[0,1].axhline(0, color='k', linestyle='--')
    axes[0,1].set_xlabel('h0')
    axes[0,1].set_ylabel('m_eff^2')
    axes[0,1].set_title('Effective mass squared (M0^2 + Pi)')
    axes[0,1].legend()
    axes[0,1].grid(True)
    
    # Tachyon region plot: h0 vs L, color by sign of m_eff^2
    tachyon_map = np.full((len(Ls), len(h0s)), np.nan)
    for i, L in enumerate(Ls):
        for j, h0 in enumerate(h0s):
            r = next(r for r in results if r[0]==L and abs(r[1]-h0)<1e-6)
            tachyon_map[i, j] = 1 if r[4] else 0
    im = axes[1,0].imshow(tachyon_map, extent=[h0s.min(), h0s.max(), Ls.min(), Ls.max()],
                           aspect='auto', origin='lower', cmap='coolwarm')
    axes[1,0].set_xlabel('h0')
    axes[1,0].set_ylabel('L')
    axes[1,0].set_title('Tachyon region (1=Yes, 0=No)')
    plt.colorbar(im, ax=axes[1,0])
    
    # Shredding invariant psi
    for L in Ls:
        psi_vals = [r[5] for r in results if r[0] == L]
        h_vals = [r[1] for r in results if r[0] == L]
        # Filter out NaNs
        h_vals_psi = [h for h, psi in zip(h_vals, psi_vals) if not np.isnan(psi)]
        psi_vals_clean = [psi for psi in psi_vals if not np.isnan(psi)]
        axes[1,1].plot(h_vals_psi, psi_vals_clean, label=f'L={L}')
    axes[1,1].set_xlabel('h0')
    axes[1,1].set_ylabel('psi = ln(m_eff/m0)')
    axes[1,1].set_title('Shredding invariant (psi)')
    axes[1,1].legend()
    axes[1,1].grid(True)
    
    plt.tight_layout()
    plt.show()

# Run the simulation
simulate_shredding()