# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# 1.  Quadratic‑divergence cancellation in scalar mass correction
# ──────────────────────────────────────────────────────────────────────────────
def scalar_mass_correction(g, Lambda):
    """One‑loop quadratically divergent piece Δm² = (g²/16π²) Λ²."""
    return (g**2 / (16.0 * np.pi**2)) * Lambda**2

def ghost_mass_correction(g, Lambda):
    """Ghost loop contributes with opposite sign."""
    return - (g**2 / (16.0 * np.pi**2)) * Lambda**2

# Example scales (in arbitrary mass units)
g_N = 0.1
g_Delta = 0.2
Lambda = 1e3

delta_m2_N = scalar_mass_correction(g_N, Lambda)
delta_m2_Delta = scalar_mass_correction(g_Delta, Lambda)

delta_m2_N_ghost = ghost_mass_correction(g_N, Lambda)
delta_m2_Delta_ghost = ghost_mass_correction(g_Delta, Lambda)

net_m2_N = delta_m2_N + delta_m2_N_ghost
net_m2_Delta = delta_m2_Delta + delta_m2_Delta_ghost

print("Quadratic‑divergence cancellation:")
print(f"  Δm²_N (scalar only) = {delta_m2_N:.6e}")
print(f"  Δm²_N (scalar + ghost) = {net_m2_N:.6e}")
print(f"  Δm²_Δ (scalar only) = {delta_m2_Delta:.6e}")
print(f"  Δm²_Δ (scalar + ghost) = {net_m2_Delta:.6e}")

# ──────────────────────────────────────────────────────────────────────────────
# 2.  Beta‑function cancellation for the Yukawa coupling g_Δ
# ──────────────────────────────────────────────────────────────────────────────
def beta_g_Delta(g, include_ghost=True):
    """
    One‑loop beta function for g_Δ.
    Scalar loop gives +g³/(16π²); ghost loop gives −g³/(16π²).
    """
    scalar_contrib = g**3 / (16.0 * np.pi**2)
    if include_ghost:
        ghost_contrib = -g**3 / (16.0 * np.pi**2)
        return scalar_contrib + ghost_contrib
    else:
        return scalar_contrib

g = 0.5  # example coupling
print("\nBeta‑function for g_Δ:")
print(f"  Without ghost: β = {beta_g_Delta(g, include_ghost=False):.6e}")
print(f"  With ghost:    β = {beta_g_Delta(g, include_ghost=True):.6e}")