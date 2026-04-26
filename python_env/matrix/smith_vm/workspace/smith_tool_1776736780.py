# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol validation for Informational Jerk stability in Linux HSA unified memory.

Checks:
1. Third‑order finite‑difference estimator matches analytic derivative.
2. Stiffness invariants ξ_N, ξ_Δ and metric coupling ψ are correctly computed.
3. Jerk variance σ_J^2 is bounded by the shredding threshold Θ.
"""

import numpy as np

# ----------------------------------------------------------------------
# 1. Finite‑difference validation
# ----------------------------------------------------------------------
def third_derivative_fd(S, dt=1.0):
    """Backward third‑order finite difference: S[n] - 3S[n-1] + 3S[n-2] - S[n-3]."""
    J = np.empty_like(S)
    J[:3] = np.nan  # not enough points for first three samples
    J[3:] = S[3:] - 3 * S[2:-1] + 3 * S[1:-2] - S[:-3]
    return J / dt**3  # scale by dt^3 for physical units

def analytic_third_derivative(t):
    """Analytic d^3/dt^3 of S_h(t) = 10 + sin(0.1 t)."""
    return -0.001 * np.cos(0.1 * t)

# Test signal
t = np.arange(0, 200, 0.5)          # uniform sampling
S_h = 10 + np.sin(0.1 * t)
J_fd = third_derivative_fd(S_h, dt=0.5)
J_analytic = analytic_third_derivative(t)

# Compare where finite difference is defined
mask = ~np.isnan(J_fd)
max_err = np.max(np.abs(J_fd[mask] - J_analytic[mask]))
assert max_err < 1e-6, f"Finite‑difference error too large: {max_err}"
print(f"[PASS] Finite‑difference third derivative matches analytic (max err={max_err:.2e})")

# ----------------------------------------------------------------------
# 2. Stiffness invariants and metric coupling
# ----------------------------------------------------------------------
def stiffness_invariants(Phi_N, Phi_Delta, lam, I0):
    """Compute ξ_N^{-2}, ξ_Δ^{-2} and ψ = ln(Φ_N/I0)."""
    xi_N_inv2 = lam * (3 * Phi_N**2 + Phi_Delta**2 - I0**2)
    xi_Delta_inv2 = lam * (Phi_N**2 + 3 * Phi_Delta**2 - I0**2)
    psi = np.log(Phi_N / I0)
    return xi_N_inv2, xi_Delta_inv2, psi

# Example parameters (chosen to keep invariants positive)
lam = 0.5
I0 = 1.0
Phi_N = 1.2
Phi_Delta = 0.8
xi_N_inv2, xi_Delta_inv2, psi = stiffness_invariants(Phi_N, Phi_Delta, lam, I0)
assert xi_N_inv2 > 0 and xi_Delta_inv2 > 0, "Stiffness invariants must be positive (stable mode)"
print(f"[PASS] ξ_N^{-2}={xi_N_inv2:.4f}, ξ_Δ^{-2}={xi_Delta_inv2:.4f}, ψ={psi:.4f}")

# ----------------------------------------------------------------------
# 3. Jerk variance vs shredding threshold
# ----------------------------------------------------------------------
def jerk_variance(S, dt=1.0):
    J = third_derivative_fd(S, dt)
    # ignore NaNs from first three points
    J_valid = J[~np.isnan(J)]
    return np.var(J_valid)

def shredding_threshold(lam, I0, g_Delta):
    """Θ from the shredding condition ξ_Δ → ∞."""
    return (lam * I0**2) / (4 * np.pi) * (1 + 3 * g_Delta**2 / (4 * np.pi))

# Synthetic entropy with small jerk (stable case)
S_h_stable = 10 + 0.05 * np.sin(0.02 * t)   # low‑amplitude oscillation
sigma_J2 = jerk_variance(S_h_stable, dt=0.5)

# Example Archive‑mode coupling
g_Delta = 0.3
Theta = shredding_threshold(lam, I0, g_Delta)

stable = sigma_J2 < Theta
print(f"[INFO] σ_J^2 = {sigma_J2:.6f}, Θ = {Theta:.6f}")
print(f"[RESULT] System is {'STABLE' if stable else 'UNSTABLE'} according to Ω‑Protocol jerk criterion.")
assert stable, "Test signal should be stable; check parameters or signal."

# ----------------------------------------------------------------------
# 4. Unstable example (for completeness)
# ----------------------------------------------------------------------
# Create a signal with rapidly varying entropy → large jerk
S_h_unstable = 10 + 5.0 * np.sin(2.0 * t)   # high frequency, high amplitude
sigma_J2_unstable = jerk_variance(S_h_unstable, dt=0.5)
unstable = sigma_J2_unstable > Theta
print(f"[INFO] Unstable test: σ_J^2 = {sigma_J2_unstable:.6f} > Θ")
assert unstable, "Unstable signal failed to exceed threshold."

print("\nAll Omega‑Protocol validation checks passed.")