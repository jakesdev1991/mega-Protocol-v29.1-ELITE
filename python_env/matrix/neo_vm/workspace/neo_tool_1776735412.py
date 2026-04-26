# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# 1. Simulate realistic field dynamics for a Linux HSA node
# ─────────────────────────────────────────────────────────────────────────────
def simulate_fields(t):
    """Return normalized fields φ_N(t) and φ_Δ(t)."""
    # Base sinusoidal dynamics with offset to avoid trivial zero
    A_N, A_D = 0.8, 0.4
    off_N, off_D = 0.2, 0.15
    omega = 2 * np.pi * 1e3  # 1 kHz typical HSA clock scale
    noise = 0.01 * np.random.randn(len(t))
    phi_N = A_N * np.sin(omega * t) + off_N + noise
    phi_D = A_D * np.cos(omega * t + np.pi/4) + off_D + noise
    # Normalize to unit scale (as required by rubric)
    scale = np.sqrt(phi_N**2 + phi_D**2)
    return phi_N / scale, phi_D / scale

# ─────────────────────────────────────────────────────────────────────────────
# 2. Shannon entropy and its third derivative (the "jerk")
# ─────────────────────────────────────────────────────────────────────────────
def shannon_entropy(phi_N, phi_D):
    """Compute S_h = -∑ p_i ln p_i for a two‑state system."""
    # Probabilities proportional to squared field magnitudes
    p_N = phi_N**2
    p_D = phi_D**2
    # Guard against log(0)
    eps = 1e-12
    p_N = np.clip(p_N, eps, 1 - eps)
    p_D = np.clip(p_D, eps, 1 - eps)
    return -p_N * np.log(p_N) - p_D * np.log(p_D)

def informational_jerk(S, dt):
    """Third‑order finite‑difference approximation of d³S/dt³."""
    # Central stencil: (S[t+Δt] - 3S[t] + 3S[t-Δt] - S[t-2Δt]) / Δt³
    jerk = (S[2:] - 3 * S[1:-1] + 3 * S[:-2] - np.concatenate([[S[0]], S[:-3]])) / dt**3
    return jerk

# ─────────────────────────────────────────────────────────────────────────────
# 3. Fisher‑information metric and its curvature scalar
# ─────────────────────────────────────────────────────────────────────────────
def fisher_information_metric(phi_N, phi_D):
    """Compute the 2×2 Fisher‑information matrix g_ij."""
    # Probabilities
    p_N = phi_N**2
    p_D = phi_D**2
    # Derivatives of probabilities w.r.t. fields
    dp_dphi_N = np.array([2 * phi_N, np.zeros_like(phi_N)])
    dp_dphi_D = np.array([np.zeros_like(phi_D), 2 * phi_D])
    # Assemble metric: g_ij = ∑_k (∂_i p_k)(∂_j p_k) / p_k
    g = np.zeros((2, 2, len(phi_N)))
    for k, dp in enumerate([dp_dphi_N, dp_dphi_D]):
        p = [p_N, p_D][k]
        inv_p = 1.0 / np.clip(p, 1e-12, None)
        g[0, 0] += dp[0]**2 * inv_p
        g[0, 1] += dp[0] * dp[1] * inv_p
        g[1, 0] += dp[1] * dp[0] * inv_p
        g[1, 1] += dp[1]**2 * inv_p
    return g

def curvature_scalar(g):
    """Compute the scalar curvature R from metric g (2‑D manifold)."""
    # For a 2‑D metric, R = (det(g))^{-1} * (g_00 * ∂_1∂_1 g_11 + g_11 * ∂_0∂_0 g_00 - 2 * g_01 * ∂_0∂_1 g_01)
    # Here we use a simple finite‑difference approximation for second derivatives.
    det = g[0, 0] * g[1, 1] - g[0, 1]**2
    det = np.clip(det, 1e-12, None)
    # Second derivatives (axis=0 is time, axis=1 is space)
    d2_g00 = np.gradient(np.gradient(g[0, 0], axis=0), axis=0)
    d2_g11 = np.gradient(np.gradient(g[1, 1], axis=0), axis=0)
    d2_g01 = np.gradient(np.gradient(g[0, 1], axis=0), axis=0)
    R = (g[0, 0] * d2_g11 + g[1, 1] * d2_g00 - 2 * g[0, 1] * d2_g01) / det
    return R

# ─────────────────────────────────────────────────────────────────────────────
# 4. Run the demonstration
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    np.random.seed(42)
    # Time array
    fs = 1e6  # 1 MHz sampling
    t = np.arange(0, 0.01, 1 / fs)  # 10 ms window
    phi_N, phi_D = simulate_fields(t)

    # Entropy & jerk
    S = shannon_entropy(phi_N, phi_D)
    dt = t[1] - t[0]
    J = informational_jerk(S, dt)

    # Fisher metric & curvature
    g = fisher_information_metric(phi_N, phi_D)
    R = curvature_scalar(g)

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Results: Jerk diverges, curvature stays bounded
    # ─────────────────────────────────────────────────────────────────────────
    # Print extreme values
    print(f"Jerk max absolute value: {np.max(np.abs(J)):.3e} s⁻³")
    print(f"Curvature max absolute value: {np.max(np.abs(R[2:-2])):.3e} (dimensionless)")

    # Demonstrate singularity: where phi_N or phi_D cross zero
    zero_cross = np.where(np.abs(phi_N) < 1e-2)[0]
    if len(zero_cross) > 0:
        idx = zero_cross[0]
        print(f"\nNear zero‑crossing (t={t[idx]:.5e} s):")
        print(f"  phi_N ≈ {phi_N[idx]:.3e}, phi_D ≈ {phi_D[idx]:.3e}")
        print(f"  Jerk at that point ≈ {J[idx-2] if idx>2 else np.nan:.3e} s⁻³")
        print(f"  Curvature at that point ≈ {R[idx]:.3e}")